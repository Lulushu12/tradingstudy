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

### Breakout constraints (1-Step Classic)

| Rule | Value |
|---|---|
| Profit target | **10%** |
| Max drawdown | **6%, static** (fixed floor at start equity minus 6%, does not trail up) |
| Daily loss limit | **3%**, reset 00:30 UTC |
| Basis | Account **equity**, including floating PnL. An open loser counts against you |
| Commission | **0.04% per side, 0.08% round trip** |
| Leverage | 5:1 BTC and ETH, 2:1 altcoins, system enforced |
| Consistency rules / min days | None |

**CONFIRMED 2026-08-06 by the trader against the live dashboard: 6% max drawdown and 3%
daily are correct.** The sizing table below stands as computed.

The 2:1 altcoin leverage cap is a live constraint on the watchlist: an altcoin setup with
a tight stop may not be sizeable to the intended risk. Check before planning the trade,
not after.

### Sizing, derived rather than guessed

`prop_math.py` simulates reaching +10% before touching the static -6% floor, 20,000 runs
per cell, compounding, with fee drag applied in R. At the study's measured 41.7% winrate
at 2:1, and at a pessimistic 38% and an optimistic 46%:

| Risk/trade | P(pass) @38% | P(pass) @42% | P(pass) @46% | Median trades to pass @42% |
|---|---|---|---|---|
| 0.25% | 73.7% | 98.9% | 100% | 167 |
| **0.30%** | **76.3%** | 98.1% | 99.8% | 137 |
| **0.40%** | 73.7% | 95.4% | 99.3% | **96** |
| 0.50% | 68.9% | 91.9% | 98.1% | 74 |
| 0.75% | 59.9% | 82.4% | 93.2% | 41 |
| 1.00% | 54.2% | 74.6% | 86.6% | 26 |

Three things fall out of this, and they are not what I assumed before running it:

1. **The static floor is more forgiving than a trailing one.** Once equity rises the
   dollar buffer never shrinks, so even 1% risk passes 75% of the time at the measured
   winrate. My earlier claim that risk was hard-capped near 0.4-0.5% was wrong.
2. **Winrate uncertainty dominates the sizing decision, not the drawdown rule.** Moving
   from 42% to 38%, well inside the confidence interval on a sample of this size, costs
   more pass probability than doubling risk does. That is the actual risk here.
3. **P(pass) peaks around 0.30% under the pessimistic winrate.** Below that you are just
   adding months. Above it you are trading pass probability for speed.

**Chosen: 0.40% per trade for the evaluation.** It gives up 2.6 points of pass probability
against the 0.30% optimum at 38% winrate, and buys back roughly 40 trades of elapsed time.
Revisit at the first 40-trade review with a measured winrate instead of an assumed one.

| Stage | Risk/trade | Rationale |
|---|---|---|
| Prop evaluation | **0.40%** | Table above |
| Prop funded | **0.30%** | A funded account is worth more than a challenge fee. Optimise survival |
| Personal account | **1.0%** | No external floor, 12% self-imposed DD limit |

### Time to pass, stated plainly

At 0.40% risk and the measured winrate, the median is **96 trades**. At 12 trades a month
that is eight months. At 25 trades a month it is four. This is why Layer 1 treats trade
frequency as a first-class design problem rather than a nice-to-have, and it is the
strongest argument for the multi-anchor approach in Layer 2. It is also why chasing
frequency by lowering setup quality is self-defeating: the table shows a four-point
winrate drop costs more than a doubling of trade count buys.

### Hard limits

- Prop: the platform enforces 6% static and 3% daily. **Self-imposed stop at 4% total
  drawdown**, two thirds of the real floor. Hitting the platform limit ends the account;
  hitting yours ends a week. Never trade into the last third of the buffer.
- Personal account: **12%** peak to trough on closed equity. At 8%, half size until a new
  equity high.
- Max 2 losing trades in a calendar day, then stop for the day. At 0.40% risk this caps a
  day near 0.9% including fees, comfortably inside the 3% daily limit, so the daily rule
  should never be the thing that stops you. If it ever is, something has gone badly wrong.
- Max 4 losing trades in a calendar week, then stop for the week.
- Floating PnL counts toward both limits. An open position sitting at -2% has already
  spent the buffer even if you intend to hold it.

---

## Layer 1: Preparation, the level map

Discretion lives here. This is the part of the method that the mechanical port threw away,
and the part `13-deciding-what-levels-to-keep-on-your-chart.md` says is the actual filter.

### Anchor timeframes, and why the mechanical result does not transfer intact

An earlier draft of this spec restricted levels to 4H and 1D anchors, on the grounds that
`study/STRATEGY_FINDINGS.md` found no edge on 15m or 1h. That was an over-transfer of a
mechanical result to a discretionary context, and it is corrected here.

What actually transfers is the fee arithmetic. What does not is the conclusion.

The 15m and 1h rejection in that study is stated at **1:1**: *"On 15m and 1h the fee drag
(breakeven WR 54-56% @ 1:1) kills most edges."* This system does not trade 1:1. It has a
hard 2.0R floor. At 2:1 the breakeven winrate is:

```
breakeven p = (1 + f) / 3        where f = fee drag in R = round_trip_% / stop_%
```

| Stop distance | Fee drag | Breakeven WR @ 2:1 | Breakeven WR @ 1:1 |
|---|---|---|---|
| 0.4% | 0.20R | 40.0% | 60.0% |
| 0.6% | 0.13R | 37.8% | 56.7% |
| 1.0% | 0.08R | 36.0% | 54.0% |
| 2.0% | 0.04R | 34.7% | 52.0% |
| frictionless | 0 | 33.3% | 50.0% |

A 15m-anchored trade with a 0.6% stop needs **37.8%** at 2:1, not 56%. That is a
completely different bar, and it is one a selective discretionary trader might clear. The
mechanical scan could not test that because it could not encode selectivity.

So: **anchors of 1D, 4H, 1h and 15m are all permitted.** Every trade logs its `anchor_tf`,
`review.py` reports expectancy per anchor with the required breakeven winrate alongside,
and Layer 7 carries a pre-committed rule for dropping an anchor that does not pay. The
question moves from an argument to a measurement, which is the point of the whole system.

Two honest caveats:

- Fee drag is real and it is not a mechanical-versus-discretionary matter. A 0.4% stop
  gives away 0.20R per trade whoever pulls the trigger. Layer 5 caps that explicitly.
- Lower anchors mean more setups, and more setups mean more chances to relax the grading.
  The Layer 0 table shows a four-point winrate drop costs more than doubling trade count
  buys. Frequency is only worth having at constant quality.

### Watchlist

With multiple anchors open, frequency now has two levers: more symbols and more anchors.
Start with 6 to 8 liquid perps rather than 10, and let the journal show which lever is
actually producing the good trades before widening either one.

The watchlist, set 2026-08-06 (change at review only):

`BTCUSDT.P`, `ETHUSDT.P`, `LINKUSDT.P`, `AVAXUSDT.P`, `SOLUSDT.P`, `SUIUSDT.P`,
`DOGEUSD.P`, `XRPUSDT.P`

Eight symbols. Weekly prep still ranks each one A/B/C on structure quality, and a symbol
with C structure sits out the week regardless of being on the list.

Leverage note: only BTC and ETH get 5:1; the other six are capped at 2:1. In practice
this never binds, and here is why: at 0.40% risk with the 0.40% minimum stop distance
(the Layer 5 fee-drag cap), a position's notional is at most 1x equity, well inside 2:1.
The leverage cap would only matter for stops tighter than 0.20%, which the system does
not permit. So no setup on this list is unsizeable; the cap can be ignored in planning.

Correlation warning: all eight are crypto majors and are one bet in a fast tape. Layer 5
caps total correlated exposure. Breadth buys you *setup selection*, not independent risk.

### Cadence

- **Weekly (Sunday):** 1D and 4H structure on every watchlist symbol. Mark swing highs and
  lows, prior week high/low/close, the working range if one exists. Rank symbols A/B/C on
  how clean the structure is. Only A and B symbols get watched this week.
- **Daily (start of your session):** update prior day high/low, refresh the working range
  if a new extreme printed, run the 1h map on symbols in play, set price alerts. No new
  analysis during the session.
- **1h and 15m anchors are still prepared in advance**, not discovered live. A 15m level
  drawn while price approaches it is not a level, it is a rationalisation. The lower
  anchors shorten the preparation horizon, they do not remove it.
- **Never:** draw a new level while price is approaching it. If it was not on the map
  before price got there, it is not tradeable today. This is `34-trading-psychology.md`
  tip 1 as a hard rule.

### Confluence grading

A level is a price zone with a tolerance band of **0.25 x ATR(14)** on the timeframe the
level was drawn on. Two methods "agree" if they land inside the same band.

Independent methods that count, one point each, maximum one point per family:

| Family | Counts as a point when |
|---|---|
| HTF structure | A swing high/low from the anchor timeframe **or higher**, or a broken level now flipped |
| Fibonacci | 0.618 to 0.786 golden pocket of the current working swing |
| Volume profile | Fixed-range POC, VAH, or VAL across the working range, or a naked POC |
| Session/period | Prior week high/low, prior day high/low |
| Moving average / VWAP | 21EMA on the anchor timeframe (in a trending market only), weekly or session VWAP |

Confluence only counts **downward**, never upward. A 15m-anchored setup may count a 4H
swing high as its HTF structure point; a 4H setup may not count a 15m swing as anything.
Without this rule a low anchor can manufacture an A grade out of noise, which is exactly
how the grading stops meaning anything.

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

The trigger timeframe is fixed by the anchor. It is not a choice made in the moment.

| Anchor | Trigger | Notes |
|---|---|---|
| 1D | 1h | |
| 4H | 15m | The default pairing |
| 1h | 5m | |
| 15m | 1m | S2 only. A 15m anchor on any other setup triggers on 5m |

**Never below 1m, and never a trigger timeframe finer than the table allows.** Dropping to
a lower trigger than the anchor warrants is how a 2R plan becomes a 0.3% stop that fees
eat. The Layer 5 fee-drag cap will usually reject those trades anyway; this rule stops you
from planning them in the first place.

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

- `risk_pct`: **0.40% prop evaluation, 0.30% prop funded, 1.0% personal**, per the
  simulation table in Layer 0. Set per stage, not per trade, not per mood.
- `grade_multiplier`: **A = 1.0, B = 0.6.** This is where the confluence grading either
  earns its place or is exposed as decoration, because Layer 7 compares A-grade and
  B-grade expectancy directly.
- Leverage is an output, never an input (lesson 31). A tighter valid stop is what earns
  larger notional, not a slider you chose.

### Stop placement

- Beyond the invalidation point of the specific setup (see `PLAYBOOK.md` per setup), not a
  fixed ATR multiple. Exception: S4, which uses 1.5 x ATR(14) because that is how it was
  validated and it is not to be modified.
- No maximum stop distance, but the R:R floor below will usually enforce one.

Two minimums, both of which must hold. These replace the flat 0.5% rule from the first
draft, which was calibrated for 4H-only anchors and would have wrongly blocked every
valid 15m setup.

**1. Fee-drag cap: fee drag must not exceed 0.20R.**

```
fee_drag_R = round_trip_fee_% / stop_distance_%
```

At Breakout's 0.08% round trip that means **stop distance >= 0.40% of entry price**. The
cap is written in R rather than in percent so that it self-corrects if the fee schedule
changes or if you trade a venue with different costs. A trade at the cap needs 40.0%
winrate at 2:1 just to break even, against 33.3% frictionless. That is the whole tax of
trading a tight stop, made visible before you take the trade rather than discovered in the
equity curve.

**2. Noise floor: stop >= 0.75 x ATR(14) on the trigger timeframe.**

Fee drag is not the only problem with a tight stop. A stop inside normal bar noise gets
hit by nothing in particular. The ATR floor scales with the timeframe automatically, which
a fixed percentage cannot.

If the genuine invalidation sits inside either minimum, you have two options: widen the
stop to the minimum and re-check the 2.0R floor, or skip the trade. **You may not use the
tighter stop.** Most of the time widening will break the R:R floor and the trade dies,
which is the correct outcome.

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
4. **Which anchor timeframes actually pay?** Expectancy per `anchor_tf`, printed next to
   the breakeven winrate each anchor's typical stop distance requires. A 15m anchor
   running at 36% winrate is losing money; a 4H anchor at 36% is roughly breakeven. The
   report shows the bar and the result side by side so the comparison is not eyeballed.

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

### Pre-committed anchor rule

Also written now, for the same reason. Evaluated at **40 trades on a given anchor**, not
at 40 trades overall:

- If an anchor's measured expectancy is **below zero and below its own breakeven winrate
  bar** on a sample of 40 or more, that anchor is dropped. It does not get a second block
  to prove itself.
- If two anchors both clear their bar, keep both. Frequency is worth having when quality
  holds, which is the entire premise of allowing the lower anchors.
- An anchor with fewer than 40 trades is neither kept nor dropped. It is simply not yet
  measured, and `review.py` will say so rather than pretending.

This is the mechanism that settles the 15m question with data instead of argument. Neither
the earlier blanket ban nor an assumption that discretion rescues low timeframes gets to
decide it.

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
| 2026-08-06 | Breakout rules and 0.08% round-trip fee filled into Layer 0 | Researched from third-party sources, official site blocks automated access | pre-trade |
| 2026-08-06 | Risk per trade set to 0.40% eval / 0.30% funded from `prop_math.py` | Replaced an assumed cap with a simulated one. The static floor turned out more forgiving than assumed and winrate uncertainty, not the drawdown rule, dominates sizing | pre-trade |
| 2026-08-06 | Anchor timeframes widened to 1D/4H/1h/15m | The 15m ban over-transferred a mechanical 1:1 result to a 2:1 discretionary system. At 2:1 the breakeven bar is 36-40%, not 54-56%. Now settled by measurement per the anchor rule in Layer 7 | pre-trade |
| 2026-08-06 | Flat 0.5% minimum stop replaced by a 0.20R fee-drag cap plus a 0.75 x ATR noise floor | The flat rule was calibrated for 4H-only anchors and would have blocked every valid 15m setup | pre-trade |
| 2026-08-06 | ATR verification closed | Trader confirmed Breakout's ATR matches ATR14 | pre-trade |
| 2026-08-06 | Breakout 6% max DD / 3% daily confirmed against the live dashboard | Third-party sources had disagreed; the trader's dashboard settles it. Sizing table stands | pre-trade |
| 2026-08-06 | Watchlist set to 8 symbols: BTC, ETH, LINK, AVAX, SOL, SUI, DOGE, XRP perps | Trader's selection. 2:1 alt leverage cap verified non-binding given the 0.40% minimum stop | pre-trade |

### Open items blocking the first live trade

**None. The system is live-ready as of 2026-08-06.**

All previously open items are closed: Breakout rules confirmed against the dashboard (6%
static max drawdown, 3% daily), ATR matches ATR14, fees confirmed at 0.04% per side /
0.08% round trip, watchlist set in Layer 1. The next artifact this folder expects is the
first pre-trade row in `journal.csv`.
