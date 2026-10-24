"""WebSocket client that runs a :class:`BaseStrategy` against the exchange.

The same :class:`~uwtc.sdk.driver.StrategyDriver` as the offline simulator is
used, so a strategy behaves identically locally and in competition. The client
reconnects automatically (with backoff) and the server replays the current
round state on reconnect.
"""

from __future__ import annotations

import asyncio
import json
import logging
import random
import secrets
import time
from typing import Callable

from . import protocol as P
from .base import BaseStrategy
from .driver import StrategyDriver

log = logging.getLogger("uwtc.sdk.client")

# Close codes after which reconnecting is pointless.
FATAL_CLOSE_CODES = {4401: "unauthorized (check your API key)", 4409: "replaced by another connection"}
TIMER_RESOLUTION_S = 0.05


class StrategyClient:
    def __init__(self, strategy: BaseStrategy, url: str, api_key: str, reconnect: bool = True,
                 exit_when_finished: bool = True, max_backoff_s: float = 10.0,
                 on_message: Callable[[dict], None] | None = None) -> None:
        self.url = url
        self.api_key = api_key
        self.reconnect = reconnect
        self.exit_when_finished = exit_when_finished
        self.max_backoff_s = max_backoff_s
        self.on_message = on_message
        self._outbox: asyncio.Queue[dict] | None = None
        # Per-process client-id prefix: ids must not collide with resting orders
        # from a previous (crashed/restarted) run replayed in the reconnect snapshot.
        self.driver = StrategyDriver(strategy, self._send, cid_prefix=f"c{secrets.token_hex(3)}-")
        self._clock_ms = 0
        self._clock_wall = time.monotonic()
        self.finished = False
        self.stop_reason: str | None = None
        self.received = 0
        self.sent = 0

    # The driver calls this synchronously from strategy callbacks.
    def _send(self, msg: dict) -> None:
        if self._outbox is not None:
            self._outbox.put_nowait(msg)

    def _track_clock(self, msg: dict) -> None:
        t = msg.get("time_ms")
        if isinstance(t, int):
            self._clock_ms = t
            self._clock_wall = time.monotonic()

    def estimated_time_ms(self) -> int:
        ctx = self.driver.ctx
        est = self._clock_ms + int((time.monotonic() - self._clock_wall) * 1000)
        return min(est, ctx.day_ms) if ctx.day_ms else est

    async def run(self) -> None:
        import websockets  # imported lazily so offline users do not need it

        backoff = 0.5
        while True:
            try:
                async with websockets.connect(self.url, max_size=4 * 1024 * 1024, ping_interval=20,
                                              ping_timeout=20, open_timeout=10) as ws:
                    backoff = 0.5
                    await self._session(ws)
            except (OSError, asyncio.TimeoutError) as e:
                log.warning("connection failed: %s", e)
            except websockets.ConnectionClosed as e:
                code = e.rcvd.code if e.rcvd else None
                if code in FATAL_CLOSE_CODES:
                    self.stop_reason = FATAL_CLOSE_CODES[code]
                    log.error("server closed connection: %s", self.stop_reason)
                    return
                log.warning("connection closed (%s); reconnecting", code)
            except websockets.InvalidStatus as e:
                log.warning("handshake rejected: %s", e)
            if self.stop_reason or (self.finished and self.exit_when_finished) or not self.reconnect:
                return
            await asyncio.sleep(backoff + random.random() * 0.25)
            backoff = min(self.max_backoff_s, backoff * 2)

    async def _session(self, ws) -> None:
        await ws.send(json.dumps({"type": P.AUTH, "api_key": self.api_key}))
        self._outbox = asyncio.Queue()
        sender = asyncio.create_task(self._sender(ws))
        timer = asyncio.create_task(self._timer())
        try:
            async for raw in ws:
                msg = json.loads(raw)
                self.received += 1
                if self.on_message:
                    self.on_message(msg)
                t = msg.get("type")
                if t == P.ERROR and msg.get("reason") == "unauthorized":
                    self.stop_reason = FATAL_CLOSE_CODES[4401]
                if t == "session":
                    log.info("round %s %s; session %s", msg.get("completed_round"),
                             "aborted" if msg.get("aborted") else "finished", msg.get("state"))
                    if msg.get("state") == "finished":
                        self.finished = True
                if t == P.WELCOME:
                    sess = msg.get("session") or {}
                    log.info("connected as %s; session %s, round %s, next round %s", msg.get("team"),
                             sess.get("state"), sess.get("round"), sess.get("next_round"))
                    if sess.get("state") == "finished":
                        self.finished = True
                self._track_clock(msg)
                self.driver.handle(msg)
                if self.finished and self.exit_when_finished:
                    await self._flush()
                    await ws.close()
                    return
        finally:
            sender.cancel()
            timer.cancel()
            self._outbox = None

    async def _flush(self) -> None:
        if self._outbox is not None:
            for _ in range(100):
                if self._outbox.empty():
                    return
                await asyncio.sleep(0.01)

    async def _sender(self, ws) -> None:
        assert self._outbox is not None
        q = self._outbox
        while True:
            msg = await q.get()
            await ws.send(json.dumps(msg, separators=(",", ":")))
            self.sent += 1

    async def _timer(self) -> None:
        while True:
            await asyncio.sleep(TIMER_RESOLUTION_S)
            if self.driver.ctx.phase == "trading":
                self.driver.tick(self.estimated_time_ms())


def run_strategy(strategy: BaseStrategy, url: str, api_key: str, **kw) -> StrategyClient:
    """Blocking helper: run until the session finishes (or a fatal error)."""
    client = StrategyClient(strategy, url, api_key, **kw)
    asyncio.run(client.run())
    return client
