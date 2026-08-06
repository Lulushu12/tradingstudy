# Discretionary Trading System, v1

Status: LIVING DOCUMENT, versioned. Unlike `FROZEN_SPEC.md`, this file is meant to be
amended, but only at a scheduled review (see Layer 7), never mid-trade and never after a
loss. Every amendment gets a dated entry in the Amendment Log at the bottom. If you find
yourself wanting to change a rule while a position is open, that is the rule working.

Author's note on scope: this replaces the mechanical MCB stack attempt (`FROZEN_SPEC.md`).
It does not replace `study/STRATEGY_FINDINGS.md`, which stays in force as the empirical
ground truth this system is built on top of.

---

## Layer 0: Mandate

### What this system is for

Extracting the level-rejection and trend-continuation edge that
`study/STRATEGY_FINDINGS.md` already demonstrated exists, at a trade frequency a
mechanical scan rejected as too low for a single symbol but which becomes workable across
a watchlist.

### The arithmetic, stated once, honestly

The prior study established three things that this system does not get to argue with:

1. The only multi-year, out-of-sample-stable edge found on BTC was 4H trend continuation
   at **+0.21R net per trade**, roughly 8 trades/month, 41.7% winrate at 2:1, max
   drawdown 12.3% at 1% risk per trade.
2. The highest-winrate conditions found (short into held 4H swing resistance in a 4H
   downtrend: 61% train / 64% test at 1:1; short into held prior-week high: 52% / 68%)
   were rejected **only for frequency**, roughly 1.5 to 3 trades/month on one symbol.
   They were not rejected for lack of edge.
3. 10%/month at 6% max drawdown implies a Calmar ratio near 35. That does not exist for a
   single liquid asset. The return target and the drawdown cap were mutually incompatible
   and no amount of discretion changes that.

Therefore the realistic mandate:

| Stage | Risk/trade | Target trades/mo | Expectancy assumption | Implied monthly |
|---|---|---|---|---|
| Prop challenge | 0.4% | 10-13 | +0.20R to +0.30R | +0.8% to +1.6% |
| Prop funded | 0.5% | 10-13 | +0.20R to +0.30R | +1.0% to +2.0% |
| Personal account | 1.0% | 10-13 | +0.20R to +0.30R | +2.0% to +4.0% |

These are planning figures derived from backtested numbers, not promises. They assume the
prior study's expectancy holds for discretionary versions of the same setups, which is
exactly the thing Layer 7 is built to test.

**During the prop stage, size is not a return lever.** With a hard drawdown limit and an
observed 9-trade losing streak at 2:1, risk per trade is capped near 0.4-0.5%. The only
levers available are trade count (Layer 1 watchlist) and per-trade quality (Layer 3
grading). If the plan for hitting a return number involves increasing size, the plan is
to fail the account.

### Hard limits

- Max drawdown, personal account: **12%** measured peak to trough on closed equity. At 8%
  drop to half size until a new equity high.
- Prop account: whatever the provider's published rules are, minus a 20% safety buffer.
  **ACTION REQUIRED: paste Breakout's exact daily loss limit, max/trailing drawdown, and
  profit target into this section before the first live trade.** Every number in Layer 5
  is provisional until that is filled in.
- Max 2 losing trades in a calendar day, then stop for the day regardless of setups.
- Max 4 losing trades in a calendar week, then stop for the week.

---

## Layer 1: Preparation, the level map

Discretion lives here. This is the part of the method that the mechanical port threw away,
and the part `13-deciding-what-levels-to-keep-on-your-chart.md` says is the actual filter.

### Watchlist

Frequency comes from breadth, not from dropping timeframes. Target 8 to 10 liquid perps.
Starting list, adjust at review only:

`BTCUSDT.P`, `ETHUSDT.P`, `SOLUSDT.P`, `XRPUSDT.P`, plus 4-6 others chosen for liquidity
and for having clean, respected structure. Avoid anything where the 4H chart looks like
noise; if you cannot draw levels on it, it does not belong on the list.

Correlation warning: BTC, ETH, SOL and most majors are one bet in a fast tape. Layer 5
caps total correlated exposure. Breadth buys you *setup selection*, not independent risk.

### Cadence

- **Weekly (Sunday):** 1D and 4H structure on every watchlist symbol. Mark swing highs and
  lows, prior week high/low/close, the working range if one exists. Rank symbols A/B/C on
  how clean the structure is. Only A and B symbols get watched this week.
- **Daily (start of your session):** update prior day high/low, refresh the working range
  if a new extreme printed, set price alerts. No new analysis during the session.
- **Never:** draw a new level while price is approaching it. If it was not on the map
  before price got there, it is not tradeable today. This is `34-trading-psychology.md`
  tip 1 as a hard rule.

### Confluence grading

A level is a price zone with a tolerance band of **0.25 x ATR(14)** on the timeframe the
level was drawn on. Two methods "agree" if they land inside the same band.

Independent methods that count, one point each, maximum one point per family:

| Family | Counts as a point when |
|---|---|
| HTF structure | A 1D or 4H swing high/low, or a broken level now flipped |
| Fibonacci | 0.618 to 0.786 golden pocket of the current working swing |
| Volume profile | Fixed-range POC, VAH, or VAL across the working range, or a naked POC |
| Session/period | Prior week high/low, prior day high/low |
| Moving average / VWAP | 4H 21EMA (in a trending market only), weekly or session VWAP |

Grade:

- **A grade: 3 or more families agree.** Full size.
- **B grade: exactly 2 families agree.** Reduced size (Layer 5).
- **C grade: 1 family.** Watch only. **Not tradeable.** No exceptions, no "but it is
  obviously going to hold."

Chart hygiene per lesson 13: once a zone is graded, delete the constituent fibs and
profile overlays and leave one line in a "key levels" folder. Record the constituent list
in the journal, not on the chart.

`levels.py` in this folder computes the objective half of this automatically (prior
period extremes, volume profile, fib, EMAs, ATR band, and the clustering) so that prep is
minutes, not an hour. It does not replace your judgment about whether the structure is
real; it removes the arithmetic.

---

## Layer 2: Context gate

Context decides **which direction you are allowed to trade**, before any setup is
considered. Discretionary read, mechanical gate.

### Trend state, 4H

- `close > EMA200` = uptrend. `close < EMA200` = downtrend.
- This exact filter is what carried the validated edge in the prior study. It is thin on
  purpose; the study explicitly found that stacking extra confluence layers on top of it
  (1D trend + RSI + candle trigger) **shrank samples and fell below breakeven
  out-of-sample**. Do not add filters here because they feel prudent.

### Permission table

| Direction vs 4H trend | Minimum grade | Extra requirement |
|---|---|---|
| With trend | B | none |
| Against trend | A | must also be an SFP (S2). No plain rejection counter-trend. |

Additional asymmetry, provisional and flagged for testing: the prior study found
**"long at support levels: consistently weaker / fails out-of-sample"** while short-side
level rejections held up. That may be an artifact of the sample period. Until the journal
says otherwise, longs at support require **one extra confluence family** compared to the
equivalent short. Layer 7 tests this and either keeps it or removes it on data.

### Market state

- **Trending:** trade S1 and S4 with trend, S2 against.
- **Post-impulse range:** trade S3 at boundaries. Per
  `28-how-to-plan-and-enter-trades.md`, re-pull the range and its fibs every time a new
  extreme extends it.
- **Undefined / chop with no clean boundary:** no trades. Chop is where overtrading
  converts a positive expectancy into a negative one via fees.

---

## Layer 3: Setup taxonomy, closed list

**If a trade is not one of these four, it is not a trade.** Not "mostly S2", not "a
variation of S1". Naming it is the requirement; if you cannot name it before entering, do
not enter.

Full desk-usable detail per setup is in `PLAYBOOK.md`. Summary:

| ID | Name | Basis |
|---|---|---|
| S1 | Level rejection | Study: 4H swing resistance short 61%/64% at 1:1; prior-week high 52%/68% |
| S2 | SFP / Chickens Drinking Water | Course lesson 26, at a graded level |
| S3 | Range-boundary rotation | Course lesson 28, post-impulse range |
| S4 | 4H volume-spike continuation | Study: +0.21R, stable 2021-2026, the validated baseline |

### Why S4 matters more than it looks

S4 is fully mechanical. It requires no discretion at all: 4H bar, volume > 1.8x its
20-bar average, closing in the direction of the EMA200 trend, stop 1.5 x ATR(14), target
2R, entry next 4H open.

It is in the system as the **control group**. S1, S2 and S3 are the discretionary bets.
S4 is the measured, known-expectancy alternative. At every review, the question is not
"did the discretionary setups make money" but **"did they beat S4"**. If your judgment
cannot beat a rule you could have automated in an afternoon, the judgment is costing you
money and the honest response is to trade S4 only.

Trade S4 mechanically alongside the others from day one. Do not skip S4 signals because a
discretionary setup looks better. The control group only works if it is not tampered with.

---

## Layer 4: Trigger

The level and the context say *where and which way*. The trigger says *now*.

### Trigger timeframe

15m default for 4H-anchored levels. 5m permitted only for S2 (an SFP is visible on lower
timeframes by construction, per lesson 26). Never below 5m.

### Required trigger conditions

1. **Closed bar only.** The condition is evaluated on the close of the trigger bar. Entry
   is a market order after that close.
2. **Market Cipher B confirmation:** a clear regular divergence on the wave, plus money
   flow turning in the trade direction.
3. **Cooldown, per lesson 23:** no long while an opposing (red) dot is actively printing
   at the level. Wait a minimum of **3 trigger bars** after the opposing dot before a
   long counts as valid. Mirrored for shorts.
4. **Structure agreement:** for a long, at least two consecutive higher lows on the
   trigger timeframe; for a short, two consecutive lower highs.

### The anti-front-run rule

`FROZEN_SPEC.md` section 7 names this trader's specific failure mode: *"intrabar
front-running before the close-based condition is met"*, and lesson 26 flags front-running
as higher risk even while acknowledging the instructor does it.

**Hard rule: no entry before the trigger bar closes. Ever.** An entry taken intrabar is
logged as `adherence = deviated` even if it wins. Especially if it wins. Layer 7 measures
whether front-running actually helps; until then it is banned, because the prior system
was destroyed partly by discretionary intrabar entries that could never be evaluated.

### Missed entries

If price leaves the zone without a valid trigger, the trade is gone. Do not chase. Per
lesson 28: wait for the next level on the map, or for a retest of the one just broken.
A chased entry is `adherence = deviated`.

---

## Layer 5: Risk

Zero discretion below this line. Every number here is a rule, not a guideline.

### Position sizing

```
risk_amount   = account_equity x risk_pct x grade_multiplier
position_size = risk_amount / stop_distance
```

- `risk_pct`: 0.4% prop challenge, 0.5% prop funded, 1.0% personal. Set per stage, not
  per trade, not per mood.
- `grade_multiplier`: **A = 1.0, B = 0.6.** This is where the confluence grading either
  earns its place or is exposed as decoration, because Layer 7 compares A-grade and
  B-grade expectancy directly.
- Leverage is an output, never an input (lesson 31). A tighter valid stop is what earns
  larger notional, not a slider you chose.

### Stop placement

- Beyond the invalidation point of the specific setup (see `PLAYBOOK.md` per setup), not a
  fixed ATR multiple. Exception: S4, which uses 1.5 x ATR(14) because that is how it was
  validated and it is not to be modified.
- **Minimum stop distance: 0.5%** of entry price. A stop tighter than that on a 15m
  trigger is noise, and it was already a rule in `FROZEN_SPEC.md` (0.6%) for good reason.
  If the valid invalidation is closer than 0.5%, either widen to 0.5% and re-check R:R, or
  skip. Do not use the tighter stop.
- No maximum stop distance, but the R:R floor below will usually enforce one.

### Reward and the R:R floor

- Target is measured to **the next opposing level on the map**, not to a round number and
  not to a fixed multiple. This is lesson 31's point: a long taken directly beneath
  overhead resistance is a bad trade even if the direction is right.
- **Minimum 2.0R to the next opposing level, or no trade.** If the nearest opposing level
  sits at 1.6R, the setup is unqualified. This single rule will kill a lot of tempting
  entries, which is the intent.

### Exposure caps

- Max **3** positions open at once.
- Max **1.5R** of total open risk at any time.
- **Correlation cap:** BTC, ETH, SOL and majors count as one bucket. Max 2 concurrent
  positions in the same direction in that bucket. Two longs on BTC and ETH is one trade in
  two accounts, and it will be a double loss on a single macro candle.
- Never hold opposing positions on the same symbol. `FROZEN_SPEC.md` allowed this; it was
  a modelling convenience, not a good idea, and in a chop it pays both stops.

### Exit policy, and how both styles get tested at once

You chose to decide this on data. Here is how to get that answer without splitting the
sample in half:

**Trade one policy live. Log MFE and MAE in R for every trade. Reconstruct the other
policies afterward.**

Because maximum favourable and adverse excursion in R fully determine the outcome of any
fixed exit policy, `review.py` can evaluate all of these on 100% of your trades:

- `full_2R`: hold to 2R or stop. (`FROZEN_SPEC.md` style.)
- `partial_be`: 40% off at 1R, stop to breakeven, remainder to 2R. (Jayson style,
  lessons 26/31/34.)
- `partial_be_early`: 40% off at 0.5R, stop to breakeven, remainder to 2R. (Lesson 26's
  "as soon as price has moved roughly 0.5% in your favour".)
- `full_1R`, `full_3R`: boundary checks.

**Live policy for the prop stage: `partial_be`.** Rationale is not that it earns more; the
study's ~41% winrate at 2:1 means it probably earns slightly less. It is that it converts
most trades into a small win or breakeven, which protects the prop drawdown limit and
removes the psychological pressure that produced the rule-breaking in the last system.
Revisit at the first 40-trade review with actual reconstructed numbers.

**Requirement: log MFE_R and MAE_R honestly, including on losers.** If those two fields are
sloppy, this entire comparison is worthless and you will be guessing about exits forever.

---

## Layer 6: Execution and life rules

From `34-trading-psychology.md` tip 7, made specific to this trader.

1. **Alert-driven only.** You do not watch charts waiting for something to happen. Levels
   are prepared, alerts are set, you engage when one fires. Screen time without a fired
   alert is how C-grade levels become "kind of an A".
2. **Trade only from a proper setup**, never from bed, never from a phone while distracted,
   never in a public place. If an alert fires and you are not at a position where you can
   check the map and the trigger properly, the trade does not happen.
3. **The pre-trade journal row is written before entry, not after.** Setup ID, grade,
   confluence list, planned entry, planned stop, planned target, planned R:R. If you have
   not typed it, you have not decided it. `review.py` audits for rows missing pre-trade
   fields and reports them as process failures.
4. **After 2 losses in a day, the platform gets closed.** Not "one more good one". Lesson
   34 tip 5: step away, do not revenge trade.
5. **No position size changes mid-trade.** No adding to losers. Adding to a winner is
   permitted only per lesson 34's version: redeploying banked profit into an already
   profitable position, and it gets logged as a separate trade with its own row.
6. **No moving a stop away from entry. Ever.** Toward entry (breakeven) per the exit
   policy only.
7. **A skipped trade costs nothing.** Lesson 28: "it is better to miss a trade than to
   take one you are not confident in." Log notable skips with the reason; that log is data
   about whether your filter is too tight or too loose.

---

## Layer 7: Measurement, the part that makes this a system

A discretionary system with no measurement layer is not falsifiable, and an unfalsifiable
system fails silently. This layer exists so that in six months there is data behind any
statement about whether this works.

### The journal

`JOURNAL_SCHEMA.md` defines the fields. `journal_template.csv` is the file you fill in.
Every trade, no exceptions, including the ones you are embarrassed about. Especially those.

### The three questions

At every review, `review.py` answers:

1. **Does the grading work?** A-grade expectancy vs B-grade expectancy. If B is equal or
   better, the confluence count is not measuring what you think and the grading rules need
   rebuilding, not the trade rules.
2. **Does discipline work?** `adherence = clean` expectancy vs `adherence = deviated`. If
   deviated trades do better, either the rules are wrong or the sample is small. If clean
   trades do better, you now have a number to put against the temptation, which is worth
   more than any amount of willpower.
3. **Does discretion beat the machine?** S1+S2+S3 pooled expectancy vs S4 expectancy. This
   is the whole premise of going discretionary. If discretion loses to S4, trade S4.

### Cadence

- **Every 40 trades:** run `review.py`, read the output, write a dated block note. Rule
  amendments happen here or nowhere.
- **Never after a loss.** Never mid-block. Never because a trade felt wrong.

### Pre-committed kill rule

Written now, before any results exist, so it cannot be negotiated later.

After **100 logged trades**, the discretionary premise is declared falsified if **all
three** hold:

- Pooled S1+S2+S3 net expectancy is <= 0R, **and**
- A-grade does not beat B-grade by at least 0.10R, **and**
- Clean does not beat deviated.

On falsification: stop trading S1, S2 and S3. Trade S4 mechanically only. That is not a
failure of the project; that is the project returning a real answer, which is more than
the last one did.

Sample size honesty: at 12 trades/month, 100 trades is roughly 8 months. With a typical
per-trade standard deviation near 1.2R, the standard error on expectancy at n=100 is about
0.12R. That means a measured +0.20R is genuinely uncertain and a measured difference of
less than about 0.25R between two buckets is not reliably distinguishable from noise.
`review.py` prints standard errors next to every number for this reason. Do not make
decisions off a 15-trade bucket.

---

## Amendment Log

| Date | Change | Reason | Block |
|---|---|---|---|
| 2026-08-06 | v1 created | Replaces the mechanical MCB stack attempt | pre-trade |

### Open items blocking the first live trade

1. Breakout's exact daily loss limit, max/trailing drawdown rule, and profit target,
   pasted into Layer 0.
2. Verification that Breakout's ATR indicator matches ATR14 with RMA/Wilder smoothing.
   Carried over from `FROZEN_SPEC.md` section 7 and still unverified. It affects S4's stop
   on every trade.
3. Final watchlist of 8-10 symbols, chosen on liquidity and structure quality.
4. Fee schedule confirmed. The prior work assumed 0.08% round trip, never verified.
