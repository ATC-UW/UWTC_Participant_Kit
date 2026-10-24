"""Transport-agnostic strategy driver.

Feeds protocol messages into a :class:`Context` and dispatches strategy
callbacks. The very same driver is used by the WebSocket runner (remote and
hosted teams) and by the server's headless simulator, so strategies behave
identically in local testing and in competition.
"""

from __future__ import annotations

import logging
import traceback
from typing import Callable

from . import protocol as P
from .base import BaseStrategy, Book, Context, OpenOrder

log = logging.getLogger("uwtc.sdk")


class StrategyDriver:
    def __init__(self, strategy: BaseStrategy, send: Callable[[dict], None],
                 on_exception: Callable[[str, BaseException], None] | None = None, cid_prefix: str = "c") -> None:
        self.strategy = strategy
        self.ctx = Context(send, cid_prefix)
        self.errors = 0
        self._on_exception = on_exception
        self._next_timer_ms: int | None = None

    # ------------------------------------------------------------- helpers

    def _call(self, name: str, *args) -> None:
        fn = getattr(self.strategy, name, None)
        if fn is None:
            return
        try:
            fn(self.ctx, *args)
        except Exception as exc:  # strategy bugs must never kill the driver
            self.errors += 1
            if self._on_exception:
                self._on_exception(name, exc)
            else:
                log.error("strategy %s raised:\n%s", name, traceback.format_exc())

    def _update_clock(self, msg: dict) -> None:
        if "day" in msg and isinstance(msg["day"], int):
            self.ctx.day = msg["day"]
        if "time_ms" in msg and isinstance(msg["time_ms"], int):
            self.ctx.time_ms = msg["time_ms"]

    # ------------------------------------------------------------- timer

    def tick(self, time_ms: int) -> None:
        """Call periodically with the current time-in-day (ms)."""
        if self.ctx.phase != "trading":
            self._next_timer_ms = None
            return
        interval = max(50, int(getattr(self.strategy, "timer_interval_ms", 1000) or 1000))
        if self._next_timer_ms is None:
            self._next_timer_ms = time_ms
        if time_ms >= self._next_timer_ms:
            self.ctx.time_ms = max(self.ctx.time_ms, time_ms)
            self._next_timer_ms = time_ms + interval
            self._call("on_timer")

    # ------------------------------------------------------------- dispatch

    def handle(self, msg: dict) -> None:
        t = msg.get("type")
        ctx = self.ctx
        self._update_clock(msg)
        if t == P.WELCOME:
            ctx.team = msg.get("team")
        elif t == P.ROUND_START:
            self._on_round_start(msg)
        elif t == P.AUCTION_OPEN:
            self._call("on_auction_open", msg)
        elif t == P.AUCTION_RESULT:
            ctx.premium = bool(msg.get("won"))
            self._call("on_auction_result", msg)
        elif t == P.DAY_START:
            ctx.phase = "trading"
            ctx.time_ms = 0
            ctx.signals = {s["symbol"]: s for s in msg.get("signals", [])}
            for s in msg.get("futures_signals", []):
                ctx.futures_signals[s["symbol"]] = s
            ctx.tradable = set(msg.get("tradable", []))
            ctx.offers = list(msg.get("offers", []))
            self._next_timer_ms = None
            self._call("on_day_start", ctx.day, ctx.signals)
            if ctx.offers:
                self._call("on_signal_offer", ctx.offers)
        elif t == P.MARKET_DATA:
            for sym, b in msg.get("books", {}).items():
                ctx.books[sym] = Book(sym, b.get("bids", []), b.get("asks", []))
            if "commodities" in msg:
                ctx.commodities = dict(msg["commodities"])
            if "inav" in msg:
                ctx.inav = dict(msg["inav"])
            for tr in msg.get("trades", []):
                ctx.last_trades[tr["symbol"]] = tr["price"]
            self._call("on_market_data", msg)
            for tr in msg.get("trades", []):
                self._call("on_trade", tr)
        elif t == P.ACCOUNT:
            ctx.cash = msg.get("cash", ctx.cash)
            ctx.positions = dict(msg.get("positions", {}))
            ctx.pnl = msg.get("pnl", ctx.pnl)
            if isinstance(msg.get("orders"), list):  # full snapshot after a reconnect
                ctx.open_orders = {}
                for o in msg["orders"]:
                    cid = o.get("client_id") or f"srv{o.get('order_id')}"
                    ctx.open_orders[cid] = OpenOrder(cid, o["symbol"], o["side"], o.get("price"), o["remaining"],
                                                     o["remaining"], "limit", o.get("order_id"))
        elif t == P.ORDER_ACK:
            o = ctx.open_orders.get(msg.get("client_id"))
            if o is not None:
                o.order_id = msg.get("order_id")
                o.price = msg.get("price", o.price)
            self._call("on_order_update", msg)
        elif t == P.ORDER_REJECT:
            ctx.open_orders.pop(msg.get("client_id"), None)
            self._call("on_order_update", msg)
        elif t == P.FILL:
            self._on_fill(msg)
        elif t == P.ORDER_CANCELLED:
            ctx.open_orders.pop(msg.get("client_id"), None)
            self._call("on_order_update", msg)
        elif t == P.CANCEL_REJECT:
            self._call("on_order_update", msg)
        elif t == P.SETTLEMENT:
            sym = msg.get("symbol")
            ctx.positions.pop(sym, None)
            ctx.cash += msg.get("cash", 0)
        elif t == P.CASH:
            ctx.cash += msg.get("amount", 0)
        elif t == P.FUTURES_UNLOCKED:
            ctx.futures_unlocked = True
        elif t == P.SIGNAL:
            for s in msg.get("signals", []):
                if s.get("kind") == "futures":
                    ctx.futures_signals[s["symbol"]] = s
                else:
                    ctx.signals[s["symbol"]] = s
                self._call("on_signal", s)
        elif t == P.DAY_END:
            ctx.phase = "eod"
            if "close_marks" in msg:
                ctx.close_marks[msg.get("day", ctx.day)] = dict(msg["close_marks"])
            for sym in msg.get("expired", []):
                ctx.futures_signals.pop(sym, None)
            ctx.open_orders = {k: v for k, v in ctx.open_orders.items() if v.order_id is not None}
            self._call("on_day_end", msg.get("day", ctx.day), msg)
        elif t == P.ROUND_END:
            ctx.phase = "closed"
            self._call("on_round_end", msg)
        elif t in (P.REQUEST_REJECT, P.ERROR):
            self._call("on_error", msg)

    def _on_round_start(self, msg: dict) -> None:
        ctx = self.ctx
        ctx.phase = "pre_open"
        ctx.round_number = msg.get("round")
        ctx.days = msg.get("days", 0)
        ctx.day_ms = msg.get("day_ms", 0)
        ctx.day = 0
        ctx.cash = ctx.starting_cash = msg.get("starting_cash", 0)
        ctx.pnl = 0
        ctx.positions = {}
        ctx.open_orders = {}
        ctx.books = {}
        ctx.signals = {}
        ctx.futures_signals = {}
        ctx.commodities = {}
        ctx.close_marks = {}
        ctx.futures_unlocked = False
        ctx.premium = False
        ctx.instruments = {i["symbol"]: i for i in msg.get("instruments", [])}
        ctx.rules = dict(msg.get("rules", {}))
        ctx.betas = dict(msg.get("betas", {}))
        self._call("on_round_start", msg)

    def _on_fill(self, msg: dict) -> None:
        ctx = self.ctx
        sym = msg["symbol"]
        sign = 1 if msg["side"] == "buy" else -1
        q = msg["qty"]
        ctx.positions[sym] = ctx.positions.get(sym, 0) + sign * q
        if ctx.positions[sym] == 0:
            del ctx.positions[sym]
        ctx.cash -= sign * msg["price"] * q + msg.get("fee", 0)
        o = ctx.open_orders.get(msg.get("client_id"))
        if o is not None:
            o.remaining = msg.get("remaining", o.remaining - q)
            if o.remaining <= 0:
                ctx.open_orders.pop(o.client_id, None)
        self._call("on_fill", msg)
