# UWTC Case 2 — Participant Starter Kit

Build a Python bot that buys and sells in a simulated market. All money is
virtual. We run your uploaded code on our server; you focus on its decisions.
Your goal is to earn profit after trading costs across seven rounds.

**New to trading? Start with [Your first trading bot](docs/GETTING_STARTED.md).**
It explains the game, dashboard, first upload and how to use AI to understand
the starter code. You can get started without installing Python or setting up
a server.

## Get your first bot running

1. Get your **team key** from the organizers, sent to your team's contact email.
2. Download this repository (**Code → Download ZIP**) and unzip it, or clone it.
   This repo is public; you do not need a GitHub invitation.
3. Open [your team dashboard](https://competition.atcuw.org/dashboard) and sign in.
4. Choose `competitor_strategy.py`, click **Upload bot**, and read the confirmation.
   The example works as-is; edit its `Strategy` class when you are ready.
5. When the organizer starts a round, check **Your bot: Running** and watch your
   profit and completed trades. If it stops, read **Bot output and errors**.

A saved file is ready for the next round; it is not trading until the round
starts. Your uploaded bot keeps running if you close the page or disconnect.
The server includes the SDK, NumPy and pandas, but no internet access. Only the
one Python file is uploaded, so keep your strategy self-contained.

**Read before competing:** the starter automatically submits a **$5,000
virtual-money bid** for better signals in auction rounds. You can change or
remove that bid. The starter is a working example, not a promise of profit.

## Choose how to upload

- **Browser:** use [the dashboard](https://competition.atcuw.org/dashboard).
  This is the easiest first step.
- **Terminal or script:** use the same [upload API](docs/TEAM_GUIDE.md#hosted-execution-optional).
  Set `UWTC_API_KEY` to the key from your team email, then run:

```bash
curl --fail-with-body \
  -H "X-API-Key: $UWTC_API_KEY" \
  -F "file=@competitor_strategy.py" \
  https://competition.atcuw.org/team/strategy
```

Treat the key like a password. Keep it within your team and out of Git and AI
prompts. Coordinate uploads: the last successful upload becomes your team's
selected version.

## Competition format

Read [the seven round briefs](docs/ROUND_BRIEFS.md) before the event. During a
break, the dashboard previews what is coming next, with available assets,
optional purchases and current costs.

- An organizer-controlled unscored practice round can run before round 1; your uploaded file carries over and your account resets.
- Seven rounds, each with 10 minutes of trading plus a 20-second pre-open.
- Fifteen simulated trading days of 40 seconds per round.
- Ten-minute review/update breaks between rounds.
- Fresh $100,000 simulated starting cash and no positions each round.
- Progression: stocks → index ETF → leveraged ETF → futures → premium-signal
  auction → research → combined final. The original scenario IDs are
  **1, 2, 3, 4, 6, 9, 12**.
- The number of contestant teams is determined by registrations. Premium
  auctions offer access to the top half of teams (rounded down, minimum one);
  the exact capacity and payment rule appear in the round preview. The final does not enable the
  separate futures-signal shop.
- Round profit includes fees and purchases. **Overall scoring uses round-rank
  points: N − rank + 1, where N is the number of teams in that round.**
  All seven rounds count equally.
  See [scoring and tie rules](docs/SCORING.md).
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
