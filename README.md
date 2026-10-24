# UWTC Case 2 — Participant Starter Kit

Write a Python trading bot for the UW Algorithmic Trading Club competition.
This public repository contains the participant SDK, a working starter strategy,
and the team guide. Your organizer supplies the exchange URL and your team's API
key separately. No competition credentials belong in this repository.

## Start here: hosted competition

1. Clone this repository or download its ZIP from GitHub.
2. Open [the competition dashboard](https://competition.atcuw.org/dashboard) in your browser and sign in with your
   **team API key**. GitHub access and the competition key are separate.
3. Open `competitor_strategy.py` in your editor. It already defines a working
   `Strategy` class; customize it rather than writing exchange plumbing.
4. Upload that file using **Choose Python strategy → Upload strategy** on the
   dashboard. Confirm the selected version, then check the bot connection and
   runtime log when the organizer starts a round.
5. Monitor your private PnL, positions and orders. Review exports between rounds.

The bot runs on the organizer's server, so your laptop does not need to stay
connected for the uploaded bot to trade. The hosted environment includes the SDK,
NumPy and pandas and has no internet access. Keep the strategy self-contained:
only the uploaded Python file is transferred, not other files in your checkout.

**Starter behavior to review:** the template automatically bids **$5,000** in
premium-signal auctions. Change or remove that bid to match your own valuation.
The starter follows stock signals; futures, research and other mechanics require
additional strategy decisions.

## Competition format

- Seven rounds, each with 10 minutes of trading plus a 20-second pre-open.
- Fifteen simulated trading days of 40 seconds per round.
- Ten-minute review/update breaks between rounds.
- Fresh $100,000 simulated starting cash and no positions each round.
- Progression: stocks → index ETF → leveraged ETF → futures → premium-signal
  auction → research → combined final. The original scenario IDs are
  **1, 2, 3, 4, 6, 9, 12**.
- Five contestant teams; premium auctions have **two winners**, each paying the
  third-highest bid under the uniform-price rule. The final does not enable the
  separate futures-signal shop.
- Round PnL includes fees and purchases. Current overall scoring sums net PnL.
- During trading, the dashboard shows rivals' ranks delayed by at least 15
  seconds. Rival live PnL, positions, orders and logs stay private. Final settled
  PnL becomes visible after round close.

## Updating during a round

Upload a revised `competitor_strategy.py`. The old bot keeps running while the
replacement starts. An import error or startup timeout leaves the incumbent
active. A successful replacement preserves exchange cash, positions and resting
orders, but restarts Python variables. Rebuild local state from the SDK snapshot;
do not assume the account is empty.

Multiple teammates can view the same team's dashboard. Coordinate uploads so
one teammate does not unintentionally replace another's new version. A team key
provides access to that team's bot and private data; share it only within the team.
Refreshing or signing out clears the dashboard's in-memory key.

## Local development and remote execution

Python 3.11+ is recommended for local development. The browser upload flow does
not require a local trading connection. For SDK dependencies:

```bash
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell instead:
# .venv\Scripts\Activate.ps1
pip install -r requirements-sdk.txt
```

The SDK also supports running a bot on your own machine **when the organizer
registers your team for remote execution**:

```bash
python -m uwtc.sdk.run competitor_strategy.py --url wss://competition.atcuw.org/ws
```

Set `UWTC_API_KEY` in your local environment before using that command. Do not
commit it. Do not start a remote runner alongside a hosted bot: a second trading
connection replaces the first. Opening the dashboard is safe because it uses
read-only views rather than attaching a trading WebSocket.

The guide's hosted instructions apply to this event; its remote runner commands
are an alternative execution mode. This kit has no offline exchange simulator.

## SDK reference

Read [the team guide](docs/TEAM_GUIDE.md) for callbacks, signals, instruments,
order types, limits, fees and reconnect behavior. Prices and cash in the SDK are
**integer cents**: $101.25 is `10125`.

This public starter kit is shared by every contestant:
anyone can read its branches. Keep team-specific strategies in
your team's own private repository or local working copy. Do not push strategies
or API keys into a shared participant repository.
