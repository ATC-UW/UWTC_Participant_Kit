# Before each round

The dashboard shows the current round's briefing during trading, and the **next
round's preview during a review break**. Its displayed costs, available products
and limits come from the configured rules. Use that card if an organizer changes
published rules before a start.

You do **not** have to write a new bot for every round or use every new feature.
Your latest saved Python file is used again. Your cash, holdings, waiting orders
and paid access reset each round; your overall score carries over.

All purchases below use virtual money and reduce your profit. Purchases and
bids are made by your code through the SDK, not by dashboard buttons. All SDK
amounts are **integer cents**: $5,000 is `500000`.

## Round 1 — Trade stocks

**Available:** stocks `A`, `B`, `C`, `D`, `E`. No paid extra features.

**New idea:** your bot receives imperfect forecasts called signals. It decides
whether to buy or sell, at what price, and how much to hold.

**Before the start:** upload the working starter. Confirm the selected file
version. Once the round starts, check that the bot is running and making trades.
Start with one change you can explain, rather than adding every feature.

## Round 2 — Add an index fund

**Available:** the five stocks plus `IDX`. No paid extra features.

**New idea:** `IDX` is a fund linked to the equal-weighted basket of the five
stocks. Its price has a relationship to those stocks.

**Before the start:** decide whether to add `IDX` trading logic. You can keep
using your stock strategy. The SDK supplies the fund's indicative value in
`ctx.inav`; see the [team guide](TEAM_GUIDE.md#instruments).

## Round 3 — Explore a leveraged fund

**Available:** stocks, `IDX`, and `E2X`. No paid extra features.

**New idea:** `E2X` targets twice stock `E`'s **daily** return. Its leverage
resets each simulated day. Over several days, that is different from simply
doubling the total return of `E`.

**Before the start:** account for the daily reset if you choose to trade it.
You can continue trading only stocks or `IDX`.

## Round 4 — Decide whether to unlock futures

**Available:** stocks, both funds, and futures after a paid unlock.

**Cost:** an optional **$5,000 per-round futures unlock**. No signal auction or
research purchases in this round.

**New idea:** a future is tied to a stock's value at a later date. It may offer
another trade or offset some risk from what you hold. Access has a cost.

**Before the start:** decide whether your strategy needs futures. Your bot
calls `ctx.unlock_futures()` to pay the fee and gain access. Check the SDK's
listed contracts, permissions and expiry dates; access does not carry into the
next round. You can leave futures locked and trade the other assets.

## Round 5 — Bid for better forecasts

**Available:** stocks, both funds, optional futures, and a signal auction.
Research purchases are not active.

**Auction:** the **top half of teams** can win access to better signals,
rounded down with a minimum of one winner. The exact count is based on that
round’s roster and shown in the dashboard before the start. Each winner pays
the highest losing bid, or the reserve if higher. The current reserve is $0
and maximum bid is $50,000. Bids close at the end of the **20-second opening
period**. Your last accepted bid counts.

**Before the start:** review `on_auction_open` in the starter. It automatically
submits a **$5,000 bid**. Change or remove that bid if it does not fit your
strategy. Submit through `ctx.submit_auction_bid(amount_in_cents)`. The price
you pay reduces profit; better forecasts do not guarantee profitable trades.

Futures still require their own $5,000 unlock in this round. Winning the signal
auction does not unlock futures.

## Round 6 — Decide what research is worth

**Available:** stocks, both funds, optional futures, and research purchases.
**The signal auction is not active in this round.**

**New idea:** signals weaken over the round. Research spending can improve
later signals, but it costs virtual money now.

**Before the start:** decide whether to buy research using
`ctx.allocate_research(amount_in_cents)`. Improvements begin the **next
simulated day**, rather than changing signals you already received. Research is
optional. Futures still require their own $5,000 unlock.

## Round 7 — Bring your strategy together

**Available:** stocks, both funds, optional futures, the signal auction, and
research purchases. The separate futures-signal shop is not enabled.

**Before the start:** use the features that fit your strategy. Recheck your
auction bid before the opening period ends, your futures-unlock decision,
and any research spending. Each purchase has its own cost. Paid access and
research from earlier rounds do not carry over.

A focused strategy is fine. You do not need a new bot or every available feature.

## What stays the same?

- Fresh **$100,000** virtual starting cash and no holdings each round.
- A **20-second opening period**, then **15 simulated days × 40 seconds** of
  trading. A **10-minute review break** separates rounds. Organizers control
  the next start; the timer is not an automatic start button.
- Your selected Python file carries over, unless you successfully upload a
  replacement. Replacing it during a round keeps your exchange account but
  restarts Python variables.
- Standard limits: **100 units per order**, **500 units held or short per asset**,
  **50 waiting orders**, **$300,000 combined absolute position value**, and
  **25 messages per simulated second**. See the dashboard for per-asset exceptions.
- A trade against an existing order costs **$0.01 per unit**. If someone trades
  with your waiting order, the standard fee is **$0**. Paid upgrades are extra.
- Overall scoring adds round-rank points: **N − rank + 1**, using the actual
  number of teams N in each round.
  All seven rounds count equally. Round ranks use final profit after costs;
  live profit is provisional. Read [scoring and tie rules](SCORING.md).

For exact SDK methods and order-rejection reasons, use the
[team guide](TEAM_GUIDE.md). For the first upload and common problems, use
[Your first trading bot](GETTING_STARTED.md).
