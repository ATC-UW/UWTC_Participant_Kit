# Your first trading bot

You know how to code. You do not need to know finance to get your first bot running.

In this competition, your team writes a Python program that buys and sells in a
simulated market. All money is virtual. We run your uploaded code on our server.
Your job is to improve its decisions, then learn from the results.

## First, get something working

1. **Get your team key.** Register your team with the organizers. They send one
   API key to your team's contact email. It works like a password for your team.
2. **Download this repo.** On GitHub, choose **Code → Download ZIP**, then unzip
   it. You can also clone it. Everyone can read the starter kit; no GitHub
   invitation is needed.
3. **Open the [competition dashboard](https://competition.atcuw.org/dashboard).**
   Paste the team key from your email and sign in.
4. **Upload `competitor_strategy.py`.** You can use the example unchanged for
   your first upload. Choose the file, click **Upload bot**, and read the
   confirmation. No local Python installation is needed just to upload it.
5. **Wait for the organizer to start a round.** A saved file is ready to run;
   it is not trading yet. During the round, **Your bot: Running** and completed
   trades show that your bot is active. Output and errors appear near the
   bottom of the page.

You do not need AWS, a server, or an open laptop for your uploaded bot to keep
trading. Refreshing the dashboard signs you out; it does not stop the bot.

The starter is a working example, not a promise of profit. It automatically
submits a **$5,000 virtual-money bid** for better signals in auction rounds.
Review, change or remove that behavior before competing.

## What is the bot deciding?

Suppose the highest offer to buy a stock is $99.90 (the **bid**), and the
cheapest seller asks $100.10 (the **ask**). Buying immediately costs $100.10;
selling immediately gets you $99.90. The gap is the **spread**.

Now your bot gets a forecast suggesting the price may rise. It can buy, wait,
place an order at a different price, or reduce an existing position.

A forecast is a clue, not a future price you can trust completely. A good bot
must decide **whether to trade, how much to trade, and what to do when it is
wrong**. Fees and paid upgrades reduce its profit.

Two common approaches are:

- **Take an available trade:** buy or sell at a price already offered in the
  market when your bot thinks it is worthwhile.
- **Offer a price:** leave a buy or sell order for someone else to trade with.
  Your bot needs to cancel or change that order if it becomes a bad deal.

You can focus on one approach. You do not need to trade every asset or implement
every feature to participate.

## Read the dashboard

| On the page | What it means |
| --- | --- |
| Profit / loss, also called PnL | What you have earned or lost since the round started, including the value of your holdings and trading costs. Positive is profit; negative is loss. |
| Cash available | Money in the account. Cash alone is not your score: you may also own or owe assets. |
| Completed trades, also called fills | Orders that actually matched and traded. An order that is still waiting is not a completed trade. |
| What you hold, also called positions | Positive quantities are assets you own. Negative quantities are short positions: you sold borrowed assets and benefit if their price falls. |
| Orders waiting to trade | Buy or sell requests that have not fully matched yet. They can remain on the market until matched or canceled. |
| Signal | A forecast sent to your bot. It can be inaccurate. |
| Spread | The gap between the best available buying and selling prices. |
| Team rankings | Other teams' ranks are delayed by at least 15 seconds during trading. Their live profit and holdings stay private. Final round profit becomes visible afterward. |

Live profit is an estimate. At the round's end, the exchange calculates the
final result using the official closing values. Your final profit determines
your rank that round. With N teams, you earn N − rank + 1 points: N for first,
N−1 for second, down to 1 for last. The team count comes from that round’s roster.
Your points across all seven rounds determine the overall ranking; every round
counts equally. Read [scoring and tie rules](SCORING.md).

## Practice before the competition

The organizer can run an **unscored practice round** using the stock market.
Upload the unchanged starter first, then check trades, positions, and bot output
while practice runs. You can edit and upload improvements during practice.
The dashboard labels practice clearly. Practice earns no competition points
and does not use up round 1. Your uploaded file carries over; cash, positions,
orders, and bot variables start fresh when scored round 1 begins.
The organizer starts the scored competition separately after everyone is ready.

## What happens in a round?

You start each round with **$100,000 in virtual cash and no holdings**. The
organizer starts the round. There is a 20-second opening period, followed by
10 minutes of trading. Fifteen simulated days fit into those 10 minutes.

Between rounds, you have a **10-minute review break**. Download your results,
change your bot, and upload the next version. A fresh round resets the account;
your results from previous rounds still count toward the overall ranking.
The organizer controls the next start, so the break timer is not an automatic
start button.

| Round | New idea |
| --- | --- |
| 1 | Five stocks and imperfect forecasts. Learn how your bot behaves. |
| 2 | An index fund, which is linked to a basket of stocks. |
| 3 | A leveraged fund, which targets twice one stock's daily return and resets each day. |
| 4 | Futures: contracts tied to a stock at a later date. Access has a fee. |
| 5 | An auction for better forecasts. Decide what that information is worth. |
| 6 | Research spending to improve future forecasts. Weigh the benefit against its cost. |
| 7 | A combined final. Use the parts that fit your strategy. |

Read [the round briefs](ROUND_BRIEFS.md) for what changes and what to prepare
before each start. The [team guide](TEAM_GUIDE.md) explains the exact assets, fees, limits and SDK
methods. The dashboard explains the current round as you go.

## Change one thing at a time

Open `competitor_strategy.py` in your editor. Start by understanding:

- `on_day_start`: reads the daily signals and chooses target holdings.
- `on_timer`: compares those targets with your current holdings and sends orders.
- `SIZE_PER_PCT` and `CHUNK`: affect how much the example tries to trade.

For a first experiment, change one sizing parameter and explain to yourself
what you expect it to do. Bigger positions can increase losses as well as gains.
Check your bot's trades and output before adding several new features.

Only one Python file is uploaded. Keep it self-contained. The server has the
SDK, NumPy and pandas, but your bot cannot use the internet or other files from
your laptop. SDK prices and cash are **integer cents**: $10.00 is `1000`.

You can upload an update during a round. The old bot keeps running while the
new one starts. If the update fails to start, the previous version stays
selected. A successful replacement keeps cash, holdings and waiting orders,
but starts fresh Python variables. Use the SDK's current state rather than
assuming your account is empty.

Coordinate uploads with teammates. The last successful upload becomes the
team's selected version.

## Use AI to help you understand your code

Give your AI the starter file and [team guide](TEAM_GUIDE.md), then try:

> Explain this starter strategy to a Python programmer who is new to trading.
> Show me where it receives signals, chooses order size and places trades.
> Suggest one small change and explain how it could help or lose money.
> Use only methods documented in this SDK. All prices and cash are integer cents.

After a round, you can ask it to analyze your own exported CSV files. Separate
what the data shows from a guess about why a strategy worked. One profitable
round does not prove that a change will keep working.

Keep your team key out of AI prompts, screenshots, Git commits and shared
notebooks. The starter repository is public; store your own strategy in a
private repo or your local files. Read and understand AI-generated code before
uploading it: AI can invent SDK methods or make incorrect assumptions.

## If something is confusing or broken

| Situation | What to do |
| --- | --- |
| I have no team key | Ask an organizer after registering your team. |
| My key is rejected | Copy the full key from your team email; make sure it is your team's current key. Ask an organizer if it still fails. |
| The file is saved, but the bot has not started | Before a round, this is normal. Wait for the organizer to start trading. |
| My bot stops during trading | Read **Bot output and errors**. Fix the Python error, upload again and check that the bot is running. Ask an organizer if you are stuck. |
| An update is rejected | Read the upload message. If you already had a working bot, its previous version remains selected. Fix the file and retry. |
| I refreshed and lost the chart or sign-in | Sign in again. The bot and exchange account continue. The on-page chart starts sampling again; the post-round export contains the recorded history. |
| The dashboard will not load | Check your connection, then ask an organizer whether the competition server is running. |

## Prefer the terminal?

Uploading through the [HTTP API](TEAM_GUIDE.md#hosted-execution-optional) is
optional and has the same effect as the upload button. You can script uploads
with `curl` and your team key.

The SDK also has a **remote runner** for teams explicitly registered to run
bots on their own computers. This is a different execution mode. For this
hosted event, upload your file; do not run a second trading connection alongside
it, because the second connection replaces the first.
