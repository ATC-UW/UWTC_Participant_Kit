"""UWTC Case 2 - competitor strategy template.

Edit the ``Strategy`` class below. Run it against the exchange with::

    python -m uwtc.sdk.run competitor_strategy.py --url ws://HOST:8000/ws --key YOUR_API_KEY

or upload this file for hosted execution via the team API, including mid-round
replacement. Python variables restart; reconstruct state from the reconnect
snapshot and ``ctx`` rather than assuming a new account or empty order book.

Conventions
-----------
* All prices and cash are INTEGER CENTS (``$101.25 -> 10125``).
* ``ctx`` (a ``uwtc.sdk.Context``) holds the latest state: ``ctx.positions``,
  ``ctx.cash``, ``ctx.pnl``, ``ctx.books[symbol]``, ``ctx.signals[symbol]``,
  ``ctx.futures_signals``, ``ctx.commodities`` (premium only), ``ctx.rules``...
* Actions: ``ctx.buy / ctx.sell / ctx.place_order / ctx.cancel / ctx.cancel_all``,
  ``ctx.unlock_futures()``, ``ctx.submit_auction_bid(cents)``,
  ``ctx.buy_signal("futures_signals")``, ``ctx.allocate_research(cents)``.
* Callbacks must return quickly; exceptions are caught and logged, and your
  bot keeps running.
"""

from __future__ import annotations

from uwtc.sdk import BaseStrategy, Context

EQUITIES = ["A", "B", "C", "D", "E"]


class Strategy(BaseStrategy):
    timer_interval_ms = 500

    # Fraction of the position limit to hold per 1% of expected daily return.
    SIZE_PER_PCT = 1.0
    CHUNK = 50

    def on_round_start(self, ctx: Context, info: dict) -> None:
        self.targets: dict[str, int] = {}
        ctx.log("round", info.get("round"), "starting; instruments:", list(ctx.instruments))

    def on_auction_open(self, ctx: Context, info: dict) -> None:
        # Uniform-price (k+1) auction: bidding your true value is optimal.
        ctx.submit_auction_bid(5_000_00)

    def on_day_start(self, ctx: Context, day: int, signals: dict[str, dict]) -> None:
        self.targets = {}
        for sym, sig in signals.items():
            exp = sig.get("expected_return")
            if exp is None:  # strength not disclosed this round: use the raw score
                exp = 0.004 * sig["score"]
            limit = ctx.limit(sym)
            frac = max(-1.0, min(1.0, self.SIZE_PER_PCT * exp / 0.01))
            self.targets[sym] = int(frac * limit * 0.9)

    def on_timer(self, ctx: Context) -> None:
        for sym, target in self.targets.items():
            if sym not in ctx.tradable or ctx.orders_for(sym):
                continue
            book = ctx.book(sym)
            gap = target - ctx.position(sym)
            qty = min(abs(gap), self.CHUNK, ctx.rules.get("max_order_qty", self.CHUNK))
            if qty <= 0:
                continue
            if gap > 0 and book.best_ask is not None:
                ctx.buy(sym, qty, book.best_ask, order_type="ioc")
            elif gap < 0 and book.best_bid is not None:
                ctx.sell(sym, qty, book.best_bid, order_type="ioc")

    def on_order_update(self, ctx: Context, update: dict) -> None:
        if update.get("type") == "order_reject":
            ctx.log("reject", update.get("symbol"), update.get("reason"))

    def on_day_end(self, ctx: Context, day: int, summary: dict) -> None:
        ctx.log(f"day {day} pnl ${summary.get('pnl', 0) / 100:,.2f}")

    def on_round_end(self, ctx: Context, summary: dict) -> None:
        r = summary.get("result", {})
        ctx.log(f"round over: pnl ${r.get('pnl', 0) / 100:,.2f} rank {r.get('rank')}")
