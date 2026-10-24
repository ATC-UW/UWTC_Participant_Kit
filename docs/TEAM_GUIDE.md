# UWTC Case 2 - Team Guide

**First time here? Read [Your first trading bot](GETTING_STARTED.md) for a plain-language introduction and first-upload checklist.** This page is the detailed rules and SDK reference.

You write one Python class, `Strategy`, in `competitor_strategy.py`. The SDK
connects it to the exchange, keeps your view of the market up to date and calls
your methods when things happen. Everything below is what the exchange
guarantees; the house traders and the price process are deliberately not
documented.

## Quick start

For hosted competition teams, open `https://competition.atcuw.org/dashboard` and sign
in with your team API key. Upload `competitor_strategy.py`, check the selected
version and bot connection, and review your account and runtime log. Your key
stays only in the current tab's memory; sign in again after a refresh. Opening
the dashboard does not create a trading connection or replace your hosted bot.

The dashboard's live field shows **ranks only**, delayed by at least 15 wall-clock
seconds. Your own PnL and positions remain live and private. Live valuations
are provisional; final settled PnL and completed-round exports appear after
the round ends. A bot may exit after connecting, so check its runtime log.

The command below is for running a bot remotely, rather than using hosted
execution. Do not run it alongside your hosted bot.

```bash
pip install -r requirements-sdk.txt        # websockets only; numpy/pandas are optional
python -m uwtc.sdk.run competitor_strategy.py --url wss://competition.atcuw.org/ws --key YOUR_API_KEY
```

`--url` and `--key` can also come from the `UWTC_URL` and `UWTC_API_KEY`
environment variables. The runner reconnects automatically. After a
reconnect, the exchange re-sends the round state and your open orders, so
your bot can recover from a dropped connection. Run only one copy per team;
a second connection with the same key replaces the first one.

Treat your API key like a password. It identifies your team for trading and
for downloading your own round exports.

## Competition format

* Seven competition rounds, with a 10-minute review/update break between rounds.
  Each round has a 20 s pre-open (auction bids) followed by 15 trading "days"
  of 40 s: 10 minutes of trading, or 10 minutes 20 seconds including pre-open.
  Seven rounds and six breaks take 2 hours 12 minutes 20 seconds, leaving
  17 minutes 40 seconds within a 2.5-hour event for briefing and delays.
* The selected scenario IDs are 1, 2, 3, 4, 6, 9 and 12: equities, index ETF,
  leveraged ETF, futures, premium-signal auction, research, and the combined final.
* Each round starts with fresh cash (`starting_cash` in `round_start`) and no
  positions. Round results are independent.
* **Round ranking uses profit / loss (PnL)**: `cash + sum(position x close mark) - starting cash` at the end
  of the round. Mechanic purchases, fees and futures unlocks are all paid from
  cash, so they count against you.
* **Overall scoring uses round-rank points: N − rank + 1**, where N is the
  number of teams in that round. First earns N points; last earns 1 point. All seven rounds count equally. Equal round profits
  share rank and points; equal overall points use total profit, then share place
  if still tied. See [the full scoring rules](SCORING.md).
* Rounds introduce products and mechanics progressively. `round_start.mechanics`
  tells you what is active in the current round.

## Instruments

| Symbol | What it is |
| --- | --- |
| `A`..`E` | Equities. Betas vs the index are in `round_start.betas`. |
| `IDX` | ETF tracking the equal-weighted average of A-E, rebalanced daily. Live indicative NAV is in `ctx.inav["IDX"]`. |
| `E2X` | Leveraged ETF returning 2x the *daily* return of `E`. Its leverage resets every day at the close (`rules.letf_leverage`). |
| `X-F7-07`, `X-F7-14` | 7-day futures on every equity, expiring at the close of day 7 or 14. |
| `A-F14-14`, `B-F14-14`, `C-F14-14` | 14-day futures on A, B and C. |

Futures are listed from `list_day` to `expiry_day` (see `ctx.instruments`). At
expiry they are cash-settled at the official settlement price of the
underlying, and positions are closed by the exchange (`settlement` message). Trading
futures requires a one-off **unlock fee** per round (`rules.futures_unlock_fee_cents`):
call `ctx.unlock_futures()`.

## Signals and mechanics

* **Daily signals** (`on_day_start(ctx, day, signals)`): one per equity, with
  a `score` and, when disclosed, a `strength` (information coefficient) and an
  `expected_return` (the calibrated forecast of that day's return).
* **Premium signal auction** (`on_auction_open`): a sealed-bid auction during
  pre-open. The top `winners` bidders receive higher-strength signals for the
  whole round, plus a live commodity price feed (`ctx.commodities`). The
  payment rule, reserve price and maximum bid are given in the
  `auction_open` message:
  * `uniform_k_plus_1`: every winner pays the highest losing bid, or the
    reserve if it is higher. Bidding your true value is optimal.
  * `own_bid`: each winner pays their own bid.
  * `gsp`: each winner pays the bid ranked just below theirs.

  You can bid more than once, and the last bid counts. Bids are only accepted
  if you have the cash to cover them.
* **Futures signals** (`on_signal_offer`, `ctx.buy_signal("futures_signals")`):
  a purchasable forecast of each live future's settlement price, delivered
  every day after purchase (`ctx.futures_signals`). The offer lists the
  price.
* **Signal decay and research**: in some rounds signal strength decays day by
  day. `ctx.allocate_research(cents)` raises your strength from the *next* day
  onwards, with diminishing returns and a cap. Your current boost is reported
  in `day_start.research`.

Requests for mechanics you cannot use (disabled, already bought, not enough
cash) come back as `request_reject` with a `reason`.

## Trading rules

All prices and cash amounts are **integer cents** and quantities are
integer units. The exact limits for each round are in `ctx.rules`:

| Key | Meaning |
| --- | --- |
| `position_limit`, `position_limit_overrides` | Max absolute position per symbol (`ctx.limit(symbol)`). |
| `max_order_qty`, `max_open_orders` | Per-order size and resting-order caps. |
| `max_gross_notional_cents` | Cap on the total absolute value of all positions. |
| `maker_fee_cents`, `taker_fee_cents` | Fees per unit for adding and removing liquidity. |
| `msgs_per_second`, `msg_burst` | Token-bucket rate limit on everything you send. |
| `tick_cents`, `lot_size` | Price and quantity increments. |
| `cancel_on_eod` | Resting orders are cancelled at each day's close. |

* Order types: `limit` (rests), `ioc` (fills what it can immediately and
  cancels the rest), and `market` (an IOC protected by a price band).
* Self-trades are prevented: your incoming order cancels your own resting
  order instead of trading with it.
* A circuit breaker rejects orders priced far from the reference price.
* Some rounds add a small randomised delay (a "speed bump") before orders
  reach the book.
* Exceeding the rate limit gets messages rejected (`rate_limited`), and
  sustained abuse disconnects your bot (`rate_limit_violations`). Frames
  larger than 8 KB and non-JSON frames are rejected.
* Market data (`ctx.books`, top 5 levels, plus anonymised trades) is
  published every `rules.book_publish_ms`. If your bot falls behind, stale
  snapshots are dropped rather than queued. If it falls far behind, the
  exchange disconnects it so it can reconnect with fresh state.

## The `Strategy` API

```python
class Strategy(BaseStrategy):
    timer_interval_ms = 500                      # on_timer cadence (round time)
    def on_round_start(self, ctx, info): ...    # instruments, rules, betas, mechanics
    def on_auction_open(self, ctx, info): ...
    def on_auction_result(self, ctx, result): ...
    def on_day_start(self, ctx, day, signals): ...
    def on_signal_offer(self, ctx, offers): ...
    def on_signal(self, ctx, signal): ...
    def on_market_data(self, ctx, data): ...
    def on_trade(self, ctx, trade): ...
    def on_fill(self, ctx, fill): ...
    def on_order_update(self, ctx, update): ...  # ack / reject / cancelled
    def on_timer(self, ctx): ...
    def on_day_end(self, ctx, day, summary): ... # close_marks, pnl, positions, settlements
    def on_round_end(self, ctx, summary): ...
    def on_error(self, ctx, message): ...
```

**State on `ctx`:** `positions`, `cash`, `pnl`, `books[sym]` (with
`best_bid`, `best_ask`, `mid` and `spread`), `open_orders`, `signals`,
`futures_signals`, `commodities`, `inav`, `instruments`, `tradable`, `rules`,
`betas`, `close_marks`, `day`, `time_ms` and `ms_left_in_day`. `ctx.user` is a
free dict for your own state.

**Actions:** `ctx.buy(sym, qty, price, order_type="limit")`, `ctx.sell(...)`,
`ctx.place_order(...)`, `ctx.cancel(client_id)`, `ctx.cancel_all(sym=None)`,
`ctx.unlock_futures()`, `ctx.submit_auction_bid(cents)`,
`ctx.buy_signal(product)`, `ctx.allocate_research(cents)` and `ctx.log(...)`.
`buy` and `sell` return a `client_id`, which you can use to track or cancel
the order.

Callbacks run on one thread and should return quickly. Exceptions are caught
and logged, and your bot keeps running.

## Hosted execution (optional)

For this event, teams use hosted execution by default. Your Python code runs on the competition server. Set `UWTC_API_KEY` in your terminal to the key from your team email; keep it private.

If your team is registered as hosted, you can upload `competitor_strategy.py`
between rounds or to replace a running bot mid-round. The exchange runs it in an isolated container,
which has no internet access, a read-only filesystem, limited memory and CPU,
and only the SDK, numpy and pandas installed:

```bash
curl --fail-with-body -H "X-API-Key: $UWTC_API_KEY" -F file=@competitor_strategy.py https://competition.atcuw.org/team/strategy
curl --fail-with-body -H "X-API-Key: $UWTC_API_KEY" https://competition.atcuw.org/team/strategy      # what is installed
```

The file must be UTF-8, under 256 KB, and define `class Strategy`. During a
round, the old bot keeps running while the replacement boots. An import/startup
failure or 10-second connection timeout leaves the old bot and selected version
active. A successful response includes `activation: live`; an upload from a
remote team is saved as `activation: next_round` and does not replace its laptop
process. Do not run a remote copy alongside a hosted bot: a second connection
replaces the first.

Replacing a hosted bot restarts its Python variables. Cash, positions, resting
orders and permissions stay in the exchange and are replayed to the new client.
Use `ctx` and the reconnect callbacks to rebuild local state; do not assume a
fresh account, cancel everything automatically, or reuse old client-order IDs.

After an exchange server restart, the round recovers paused at its durable game
time. Organizers resume it after hosted bots reconnect. Strategy-process memory
restarts in this case too; exchange balances and open orders are restored.

## After each round

* `GET /leaderboard` shows the public standings.
* `GET /team/rounds/{n}/export` (with header `X-API-Key`) returns a zip of your
  fills, orders, PnL curve and event log, which you can use for post-mortems.
