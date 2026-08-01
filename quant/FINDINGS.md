# BTCUSDT.P / majors — brute-force system search

Run 2026-07-30. Target set by you: **average >=10% per month, never breaching
Breakout 1-Step Classic limits** (10% profit target, 6% static drawdown anchored
to starting balance, 3% daily loss resetting 00:30 UTC), semi-automatic
execution, universe BTC + ETH + majors.

## Bottom line

The target is not reachable with this data. I did not conclude that from prior
belief; I measured it four independent ways and every one landed in the same
place. The best genuinely robust system I could construct returns about
**1.2-1.5% per month**, and it **failed its pre-registered holdout test**.

I am not going to dress that up. Below is what was tested, what was found, the
exact arithmetic that caps the result, and what would have to be true for 10%
to be possible.

---

## 1. Setup

**Data.** 1-minute Binance USD-M perpetual klines for BTC, ETH, SOL, XRP, BNB,
2021-01-01 to 2026-07-29, pulled fresh from `data.binance.vision`. 2.93M bars
per symbol. Zero duplicates, zero bad OHLC bars, zero missing minutes on
BTC/ETH/BNB (SOL and XRP each have one 3-day listing gap in early 2021). All
higher timeframes are resampled from that 1m series, so bar boundaries are
identical across timeframes by construction and stops/targets resolve on the
real intrabar path rather than a heuristic.

The repo's existing parquets stop at 2026-06-21, which is why the last five
weeks could serve as a true holdout.

**Blocks, declared before any search** (`HOLDOUT_DO_NOT_TOUCH.md`):
- TRAIN 2021-01-01 .. 2024-12-31 — search
- TEST 2025-01-01 .. 2026-06-21 — out-of-sample in time
- HOLDOUT 2026-06-22 .. 2026-07-29 — sealed, opened once at the end
- Cross-asset: all design done on **BTC only**; ETH/SOL/XRP/BNB held as a
  structural out-of-sample check.

**Execution model.** Signal on a closed bar; fill at the open of the next bar
plus one minute (alert fires, human clicks); 0.04% commission per side; 0.02%
slippage per fill charged against the trader both ways; stop wins every tie
where a single 1m bar spans both stop and target; 5x leverage cap on BTC/ETH,
2x elsewhere.

**Engine validation.** Random entries at 2:1 with zero costs produced a 33.49%
win rate and +0.005R expectancy against a theoretical fair-game null of 33.33%
and 0.000R. The engine is unbiased. Every number below rests on that check.

---

## 2. The arithmetic that governs everything

Cost drag per trade = `(2 x commission + 2 x slippage) / stop_distance_%`.
Measured across timeframes on 4,000 random trades each:

| Setup | Breakeven WR @2:1 | Edge needed over null | Avg hold | Trades/mo/slot |
|---|---|---|---|---|
| 5m, 1xATR | 58.0% | +25.1pp | 0.5h | — |
| 15m, 2xATR | 39.6% | +6.5pp | 6.4h | 114 |
| 30m, 2xATR | 37.5% | +3.7pp | 12.4h | 59 |
| 1h, 2xATR | 36.1% | +4.3pp | 23.4h | 31 |
| 4h, 2xATR | 34.6% | +1.1pp | 95h | 7.7 |
| 1D, 2xATR | 33.8% | +3.0pp | 495h | 1.5 |

Two facts follow, and they are in direct conflict:
1. Cheap costs require wide stops, which require long holds, which cap trade
   frequency.
2. High frequency requires tight stops, which makes costs enormous.

**Raw win rates sat on the martingale null at every single timeframe**
(0.49-0.51 at 1:1, 0.32-0.335 at 2:1). There is no free directional lunch
anywhere in this data.

### What 10%/month actually demands

Monte Carlo over the Breakout rules, sizing risk to the maximum that keeps
bust probability under 2%:

| Trades/month | Net expectancy required for 10%/mo | = win rate at 2:1 |
|---|---|---|
| 20 | 0.56R | 52.0% |
| 60 | 0.34R | 44.7% |
| 150 | 0.24R | 41.3% |
| 300 | 0.18R | 39.3% |
| 600 | 0.14R | 38.0% |

So the search had a hard target: **~0.20R net at ~250-300 trades/month**, which
means lifting the 2:1 hit rate from 33.7% to about 43.5%.

---

## 3. What was searched, and what it returned

### 3.1 Univariate conditional scan
71 causal features, deliberately avoiding the standard oscillator vocabulary
and built instead on things not recoverable from a close series: **aggressor
imbalance** (taker-buy volume vs total — who crossed the spread), trade-size
composition, liquidity texture (range delivered per trade, Kyle-style impact),
intrabar path shape measured from real 1m data, and clock/session structure.
A causality audit recomputed every feature with the future deleted and
confirmed no leakage.

Scanned across 13 (timeframe, ATR multiple, RR) configurations, each with a
**family-wise permutation null** — the same scan re-run on block-shuffled
labels to learn what "best of 1,320 tries" scores by luck alone.

Result: across every configuration, essentially nothing cleared the null and
then held out of sample. The single best cell anywhere (`tbi_ma96` long, 30m,
+0.110R train vs a +0.064R noise threshold) went to **-0.106R on TEST**.
Sustained buy-imbalance worked 2021-2024 and died in 2025-2026. A regime bet.

### 3.2 Template-free predictability (the most informative test)
Stripping away stops and targets to ask whether forward returns are predictable
at all:

- **Real predictability exists.** At 15m, 92 of 497 feature-horizon pairs had
  |IC| > 0.03 on TRAIN, and **95% of them held their sign out-of-sample**
  (coin flip = 50%). At 30m, 93%. That is emphatically not noise.
- **It is too small to trade.** Purged, embargoed walk-forward ridge gave
  **negative OOS R-squared at every timeframe and horizon** (-0.004 to -0.44).

The decile spreads convert directly into the killing arithmetic:

| TF / horizon | Top-decile drift | In R (2xATR stop) | Cost drag | Net |
|---|---|---|---|---|
| 15m / 24 bars | +0.125 ATR | 0.06R | 0.187R | **-0.13R** |
| 30m / 96 bars | +0.147 ATR | 0.07R | 0.124R | **-0.05R** |

**The predictable drift is real and roughly 2-3x smaller than the cost of
harvesting it.** That single sentence explains every dead result in this study.

### 3.3 Cross-sectional relative value
The most promising untested route, because trading assets against each other
cancels the dominant BTC beta where all the variance lives.

First attempt showed Sharpe -1 to -2, which was **my own bug**: equal-dollar
weighting is not risk-neutral, so ranking implicitly shorted the high-volatility
assets (SOL, XRP), and that tilt swamped the signal. Rebuilt with inverse-vol
risk-parity legs.

Corrected result: of 30 configurations, exactly one was positive in both blocks
(4h `atr_pct`, train Sharpe +0.20, test Sharpe **+0.07**). Sharpe 0.07 is
indistinguishable from zero. The target needs roughly Sharpe 7.

### 3.4 The one rule that survived
Six pre-registered rules, tested with no per-asset tuning:

| Rule | BTC TRAIN | BTC TEST | ETH | SOL | XRP | BNB |
|---|---|---|---|---|---|---|
| **vol_spike_cont** | **+0.115** | **+0.207** | +0.108 | +0.160 | +0.164 | +0.132 |
| flow_persist | -0.016 | +0.203 | -0.053 | +0.015 | +0.011 | -0.024 |
| range_pos | +0.070 | -0.230 | -0.033 | +0.082 | -0.071 | -0.120 |
| displacement | +0.027 | -0.039 | -0.034 | +0.066 | -0.036 | -0.016 |
| lowvol_cont | +0.061 | +0.075 | -0.065 | +0.038 | +0.074 | -0.023 |
| absorption_rev | -0.114 | +0.007 | +0.041 | +0.073 | -0.076 | -0.094 |

`vol_spike_cont` — a 4h bar with trade count >1.8x its 96-bar average, closing
in the direction of the 96-bar displacement — was positive everywhere:
in-sample, out-of-sample in time, and on all four assets never used to select
it. Pooled **+0.1426R, 95% CI [+0.040, +0.249]**, n=3391.

This independently reproduces the finding already in `study/STRATEGY_FINDINGS.md`
(+0.21R) with a stricter engine and a wider search.

But per-year it is fragile — **every individual year's CI contains zero**:

| 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|
| +0.233 | +0.222 | **+0.008** | +0.083 | +0.092 | +0.366 |

---

## 4. Account-level result

650 accounts per configuration, each started on a different historical date and
run until it passed +10% or busted:

| Risk / heat | P(pass +10%) | P(bust) | Mean monthly |
|---|---|---|---|
| 0.25% / 2% | 9.1% | 3.2% | **+1.24%** |
| 0.50% / 4% | 23.8% | 30.9% | +1.48% |
| 1.00% / 4% | 24.8% | 58.6% | +1.47% |
| 2.00% / 6% | 29.2% | 68.9% | +1.13% |
| 3.00% / 6% | 23.7% | 76.3% | +0.98% |

**Mean monthly return never exceeds ~1.5% at any risk setting.** This is the
central finding. Raising risk does not raise the mean — it stays pinned near
1.2-1.5% while bust probability climbs to 76%. That flatness is the 6% floor
truncating the left tail: extra leverage buys dead accounts, not returns.

Over 60-day windows the mean rises to ~2.3% and P(pass) to 35%.

---

## 5. Holdout: FAIL

The spec was frozen in `SYSTEM_FROZEN.md` with a pre-registered criterion
(pooled expectancy > 0) before the holdout was unsealed. Then it was opened
once.

| Metric | Expected | Holdout actual |
|---|---|---|
| Net expectancy | +0.143R | **-0.6135R** [-0.908, -0.332] |
| Win rate | 35.1% | **9.6%** |
| Account outcome | — | **static drawdown breached 2026-07-17** |

Per asset: BNB -0.97, ETH -0.96, BTC -0.73, XRP -0.52, SOL -0.05. Sum -31.9R
over 52 trades. **Verdict: FAIL**, by roughly 5 standard errors.

**Post-hoc diagnosis** (labelled as such — this is explanation, not rescue):
the holdout window was an extreme chop regime. BTC moved **+0.04% net across
5.5 weeks** with path-efficiency 0.000; SOL +0.24%, efficiency 0.001, against a
TRAIN median of 0.082 and a 10th percentile of 0.014. The **unconditional**
expectancy of any 4h 2:1 trade in that window was -0.286R at an 18.4% hit rate,
versus -0.015R/29.8% in TRAIN. Every 2:1 breakout trade lost there.

The system did worse than that unconditional baseline, which is exactly what a
trend-continuation rule with no regime filter does in a zero-trend market. The
holdout did not merely fail to confirm the edge; it confirmed the specific
weakness the per-year table already implied.

---

## 6. Why 10%/month is not reachable here

Three independent walls, any one of which is sufficient:

1. **Signal-to-cost.** Genuine predictability exists (95% of strong ICs hold
   sign out-of-sample) but the drift is 2-3x smaller than the round-trip cost of
   capturing it. This is not a matter of searching harder; it is a subtraction.

2. **Return-to-drawdown geometry.** 10%/month compounded against a 6% drawdown
   budget is a Calmar ratio near 20-35. The best sustained Calmar in liquid
   single-asset trading is low single digits. The account Monte Carlo shows the
   mechanism directly: return is flat in risk while bust probability is not, so
   there is no leverage setting that converts a 1.4% edge into a 10% one.

3. **Diversification is unavailable.** The five majors are one asset wearing
   five tickers. Cross-sectional relative value, the standard fix, produced
   Sharpe 0.07.

For 10%/month to be real, you would need net expectancy around 0.20R sustained
across ~300 trades/month. The best robust edge found was 0.14R at 51
trades/month — and it just failed its holdout.

## 7. What I would actually do with this

Stated plainly, since you asked for a system and I owe you the honest version of
one:

- **The `vol_spike_cont` edge is probably real but weak and regime-dependent.**
  It is positive on five assets and six years, and it dies in chop. Traded at
  0.25% risk it makes 1-1.5%/month with a 3% monthly bust risk. That is a real
  strategy. It is not your target.
- **The obvious next step is a regime filter**, since the failure mode is now
  precisely identified (trend-continuation in zero-efficiency chop). I did not
  build one, because doing so *after* seeing the holdout would be fitting to the
  holdout and would destroy the only clean test left. That work needs fresh
  quarantined data.
- **On the prop-firm economics specifically**: at 0.50% risk over 60-day
  windows, P(pass) was 35% against an $800 fee for a $100k Classic account.
  Whether that is a positive-expectancy business depends on the funded-account
  payout, and it is a genuinely different question from "10% per month". If you
  want, I can work that one properly — it is the question the structure is
  actually built to answer.

## 8. Reproduce

```
quant/src/fetch.py        1m data from data.binance.vision
quant/src/data.py         loading + holdout enforcement
quant/src/engine.py       1m-path resolution + Breakout account rules
quant/src/sanity.py       engine validation (run this first)
quant/src/costmap.py      cost drag by timeframe
quant/src/requirement.py  what 10%/month demands
quant/src/features.py     71 causal features + causality audit
quant/src/labels.py       per-bar outcome precomputation
quant/src/scan.py         univariate scan + permutation null
quant/src/ic.py           template-free predictability
quant/src/xsec.py         cross-sectional (equal dollar - has the bug)
quant/src/xsec2.py        cross-sectional (risk parity - corrected)
quant/src/candidate.py    pre-registered rule evaluation
quant/src/account.py      account-level Monte Carlo
quant/src/holdout.py      final holdout (run once)
```

---

# Part 2 — Prop-firm payout economics

Different question, different answer. "Can this make 10%/month" asks about the
return process. "Is buying an evaluation +EV" asks about an asymmetric option:
downside capped at the fee, upside an uncapped share of someone else's capital.

## Contract terms modelled (verified 2026-07-30)

- 1-Step Classic: +10% target, 6% static floor, 3% daily loss
- Passing yields a funded account starting fresh at the original size, floor
  again 6% below it, no profit target
- **The floor never trails.** Cushion = balance - floor, so withdrawing profit
  is precisely what re-exposes the account
- **Evaluation fee refunded in full with the first funded payout**
- 80% split (90% purchasable; 95% after 3 months and 2 payouts)
- Busted accounts are gone; no reset, only a new purchase

Monte Carlo over full lifecycles (evaluation to funded to payouts to bust),
20-30k paths per cell, 24-month horizon, empirical daily trade clustering
(1.24 trades/day, up to 10, 53% zero-days), R values drawn from the real
outcome classes with win probability tuned to a target expectancy.

## The result that needed checking

Raw breakeven came out at **-0.0012R**, i.e. apparently zero edge. If buying
evaluations were +EV with no skill, Breakout would be insolvent.

It resolves cleanly: **R is already net of fees and slippage.** "Zero net
expectancy" is not "no skill" — a no-skill trader has *negative* net
expectancy equal to the cost drag. The correct null is the unconditional
expectancy of the template: **-0.0148R** on TRAIN.

| True expR | P(funded) | P(paid) | Mean banked | EV | Interpretation |
|---|---|---|---|---|---|
| -0.286 | 0.0% | 0.0% | $0 | **-$800** | coin flipper, holdout regime |
| -0.050 | 7.2% | 3.5% | $152 | -$648 | no skill, poor conditions |
| **-0.015** | 21.2% | 12.9% | $674 | **-$126** | **no skill, TRAIN-average** |
| 0.000 | 29.9% | 20.1% | $1,155 | +$355 | exactly covers costs |
| +0.024 | 47.1% | 35.4% | $2,418 | +$1,618 | posterior estimate |
| +0.143 | 97.4% | 95.3% | $18,299 | +$17,499 | studied-data estimate |

The firm's model is intact. But note how *cheap* the no-skill ticket is: -$126
on an $800 fee, because the fee refund plus a 37.5% raw chance of drifting +10%
before -6% nearly pays for itself. The asymmetry is real; it just isn't free.

## The honest edge estimate

| Source | Estimate | n | SE |
|---|---|---|---|
| Studied data | +0.1426R | 3391 | 0.053 |
| Holdout | -0.6135R | 52 | 0.123 |
| **Inverse-variance posterior** | **+0.0238R** | — | 0.0488 |

**95% CI [-0.0717, +0.1194] — it straddles zero.** I do not know whether this
edge is positive. And the blend assumes one stationary edge, which the per-year
figures (+0.23, +0.22, +0.01, +0.08, +0.09, +0.37) contradict; the forward value
depends on the future regime mix, which this data cannot estimate.

## EV across that interval (0.25% risk, withdraw at +2%)

| True expR | P(funded) | Mean banked | EV | P(lose the fee) |
|---|---|---|---|---|
| -0.072 (CI low) | 3.3% | $55 | -$745 | 98.6% |
| 0.000 | 29.7% | $1,151 | +$351 | 80.2% |
| **+0.024 (posterior)** | **46.9%** | **$2,378** | **+$1,578** | **65.4%** |
| +0.119 (CI high) | 94.6% | $14,279 | +$13,479 | 9.2% |

At the posterior the purchase is **+EV at roughly 2x the fee, but you lose the
fee about two times in three.** The mean is carried entirely by the ~35% of
accounts that get funded and then pay repeatedly. Across the confidence interval
the answer swings from near-total loss to 17x. **The uncertainty dominates the
estimate.**

## Two operational findings that are robust across the whole range

**1. Undersize aggressively.** At the measured edge:

| Risk/trade | P(funded) | EV |
|---|---|---|
| **0.25%** | 97.4% | **$17,514** |
| 0.50% | 78.0% | $14,560 |
| 1.00% | 34.5% | $1,543 |
| 1.50% | 24.7% | $396 |

An 11x EV difference from sizing alone. Busts are absorbing, so survival
compounds and leverage does not.

**2. Bank early and often — the opposite of the usual instinct.** At the
posterior edge:

| Withdraw at | P(paid) | Payouts | EV |
|---|---|---|---|
| **+2%** | 34.6% | 1.08 | **+$1,529** |
| +5% | 23.9% | 0.39 | +$1,068 |
| +10% | 11.7% | 0.13 | +$391 |
| +20% | 1.8% | 0.02 | -$486 |

Because the floor is static, "letting profits run to build a cushion" is a bet
that the account survives long enough to build one. At a weak edge it usually
does not. Withdrawing at +2% was optimal at *both* the optimistic and the
posterior edge, so this conclusion does not depend on the edge estimate.

**Account size is close to ROI-neutral** ($5k: EV $75/$45 fee; $100k: EV
$1,574/$800), so size the purchase to what you can afford to lose, not for edge.

## Verdict on Part 2

Unlike 10%/month, this is not a no. At the posterior edge, buying a Classic
evaluation is positive expected value at roughly 2x the fee — but with a 65%
chance of losing the fee outright, and a confidence interval that includes
"you lose almost every time."

The single thing that would move this from a coin-flip-with-positive-drift to a
genuine business is resolving whether the edge is actually positive, which needs
the regime filter built and tested on fresh quarantined data, not more analysis
of this data.

---

# Part 3 — Regime filter, full ML, and the retrospective fit

Run overnight 2026-07-30/31. Brief: build a regime filter; if that falls short,
go full machine learning; fit everything on the data we have, hindsight allowed;
show retrospectively what would have produced 10%/month under Breakout rules, or
alternatively 100% every 2-4 months trading own capital.

## Headline

With **complete hindsight** — the model fitted on the whole 2021-2026 span,
knowing the future — the best system that still survives every Breakout rule
returns **6.63%/month**. It clears 10% in 32% of individual months and in
**56% of two-month windows**.

It does not reach 10%/month. Not because the fitted edge is too small, but
because **Breakout's 3% daily loss limit caps it**. The same signal sized more
aggressively returns +76%/month and dies on day 11.

The own-capital alternative fails outright: on the only signal that could
actually have been traded (walk-forward), every risk level from 1% to 15% ends
in **total ruin**.

## 1. Regime filter

Diagnosis from Part 1 was that the base signal is a trend-continuation bet that
dies in chop. Conditioning it on trend-worthiness does work in-sample and mostly
evaporates out of sample:

| Filter | IS expR | WF expR | base |
|---|---|---|---|
| `disp96 >= 7.84` | 0.329 | 0.142 | 0.143 |
| `absorb <= -0.028` | 0.294 | 0.211 | 0.143 |
| `tbi_ma96 <= -0.012` | 0.292 | 0.176 | 0.143 |

More important, it revealed the objective was wrong. Filters raise expectancy
but cut trade count, so monthly R **falls** (7.33 -> 2.73). The target reduces to
a ratio: monthly-R / worst-drawdown-R must exceed 10/6 = 1.67. The base signal
scores 0.19. This is a drawdown problem, not a return problem.

## 2. Machine learning

LightGBM predicting realised R per side from the 71 causal features, purged and
embargoed walk-forward versus full in-sample fit.

| Model | timeframe | IS | WF |
|---|---|---|---|
| Deep (31 leaves, 400 rounds) | 4h | +175%/mo, expR +1.86 | +0.29%/mo, expR +0.18 |
| Deep | 1h | +78%/mo | -0.13%/mo |
| Deep | 30m | +76%/mo | +0.15%/mo |
| **Shallow (8 leaves, depth 3)** | **30m** | **+16.7%/mo, expR +0.174** | **-3.1%/mo, expR -0.059** |

The shallow model is the informative one. With 8 leaves, depth 3, min_data 2000
and L2=50 it **cannot** memorise individual bars, yet the in-sample/walk-forward
gap is just as total. So the in-sample result is not bar-level recall; it is the
model encoding which regime ran in which year. Trained only on the past it
*anti-predicts* the future (negative expectancy, 94% drawdown).

That is the cleanest statement of the whole study: the in-sample performance is
real arithmetic on real data, and it is entirely a description of the past.

## 3. Compact rule systems (the executable deliverables)

A memorising model is not a system - there is nothing to write down. So I also
searched conjunctions of feature thresholds by beam search, which ARE systems:
you could have traded them mechanically had you known the constants.

All fitted with full hindsight, all validated through the real account simulator
(static floor, 3% daily limit on realised P&L, leverage caps, portfolio heat):

| System | Trades | Mean/mo | Positive months | >=10% months | CAGR | Notes |
|---|---|---|---|---|---|---|
| 4h, 4 rules | 1,485 | **3.11%** | 65% | 14% | 41.5% | risk 0.50%, heat 2% |
| 1h, 10 rules | 6,631 | **3.77%** | 70% | 18% | — | risk 0.23%, heat 2% |
| 30m, shallow-ML ranked | 31,962 | **6.63%** | 80% | 32% | — | risk 0.082%, heat 2% |

The 1h system's monthly returns, every month 2021-2026, are in
`reports/best_1h_v2.txt`; the rule set is in `reports/ruleset_1h.json`.

## 4. Why 10%/month is unreachable even with hindsight

The 3% daily loss limit, not the 6% static floor, is the binding constraint.
Evidence, same signal, same span, only risk changed:

| Risk | Mean/mo | Outcome |
|---|---|---|
| 0.082% | +6.63% | survives the full 5.5 years |
| 0.50% | **+76.77%** | **breaches `daily_loss` on 2021-01-11** |
| 1.00% (k=40) | +86.34% | breaches `daily_loss` on day 10 |

Signals cluster across five correlated assets, so a bad day closes several
losers at once. Any sizing large enough to compound at 10%/month produces a day
that loses more than 3%, and the account ends permanently. There is no risk
setting that delivers both.

I attempted to design around this by capping entries per day at k and sizing
3%/k, which appears to make a breach impossible. **That reasoning was wrong** and
I caught it in testing: trades entered on different days can exit on the same
day, and the limit applies to realised P&L, i.e. to exits. Capping entries does
not bound daily realised loss.

## 5. Own capital, no prop rules

No daily limit, no static floor, ruin only at wipeout.

| Signal | Risk 1% | Risk 5% | Risk 15% |
|---|---|---|---|
| In-sample (hindsight) | 99% maxDD | 100% maxDD | 97% maxDD |
| **Walk-forward (tradeable)** | **RUINED** | **RUINED** | **RUINED** |

The in-sample column reaches absurd terminal multiples but with 95-100% peak-to
-trough drawdowns, meaning the account was effectively wiped and rescued by
foreknowledge. It is not a strategy.

The walk-forward column is the answer to the question actually asked: with the
only signal that could have been traded without knowing the future, **every
leverage level from 1% to 15% ends in total loss.** 100% every 2-4 months is not
available from this data either.

## 6. Errors I found in my own work tonight

Reported because each one initially produced a spectacular and false result:

1. **Portfolio double-counting.** Unioning rules summed R over overlapping masks,
   so the same trade counted up to 8 times. Produced a fake "369%/month". Fixed
   by unioning as sets of (bar, side).
2. **Divide-by-zero ratio.** Rules with no drawdown scored 9.2e9. Fixed by
   rejecting degenerate curves.
3. **Coverage.** The best rule traded in 14 of 66 months. A system that sits out
   79% of the calendar cannot deliver a monthly return. Fixed with an 85%
   month-coverage constraint.
4. **The daily-loss proof was invalid** (section 4).
5. **Equal-dollar cross-sectional weighting** (Part 1) implicitly shorted the
   high-volatility assets and produced Sharpe -2 where the true answer was ~0.

## 7. What this means

You asked to see, in retrospect, what would have made 10% a month. The answer is
that under Breakout's rules **nothing in this data would have**, and the reason
is a rule rather than a lack of edge: the 3% daily cap and correlated multi-asset
signals are mutually exclusive with 10% monthly compounding.

The genuinely best retrospective system reaches 6.63%/month and hits your relaxed
"10% at worst every two months" bar in 56% of two-month windows. It is fitted to
this exact span and its walk-forward twin loses money, so it is a description of
2021-2026, not a prediction.

`quant/src/`: `regime.py`, `ml.py`, `ruleopt2.py`, `hifreq.py`, `hifreq2.py`,
`validate.py`, `findbest.py`, `frontier.py`, `dataset.py`.

---

# Part 4 — The two relaxed targets, measured on their own terms

Part 3 optimised mean monthly return, which is not the same objective as either
relaxed target. Re-run with the correct statistics.

## (a) 10% every one-to-two months, under Breakout rules

Config chosen to maximise P(rolling 2-month return >= 10%).

Best: 30m in-sample signal, risk 0.085%, heat 2%, mean +6.81%/mo.

| Window | Median | Worst | P(>=10%) |
|---|---|---|---|
| 1 month | +6.0% | -11.0% | 32% |
| **2 months** | **+12.7%** | **-8.6%** | **58%** |
| 3 months | +19.9% | -11.3% | 71% |

So the MEDIAN two-month return is 12.7% and clears the bar. But 42% of
two-month windows do not, and the worst loses 8.6%. "At worst every two months"
is not met; "typically every two months" is.

The 1h compact rule set is worse on this measure (2-month median +6.3%,
P(>=10%) 39%).

The walk-forward version of the same signal survived no risk level at all.

## (b) 100% every 2-4 months, no daily limit, no static floor

| Signal | Risk | Ruined | Final x | maxDD | Median 3mo | P(3mo >= 100%) |
|---|---|---|---|---|---|---|
| 30m IS | 5% | no | 1.36e9 | **84%** | +152% | 60% |
| 30m IS | 10% | no | 2.2e13 | **95%** | +225% | 54% |
| 1h rules IS | 2% | no | 3.0e6 | **79%** | +91% | 48% |
| 1h rules IS (heat 10%) | 2% | no | 8,041 | **67%** | +40% | 25% |
| **30m WF** | 2% | **RUINED** | 0.02 | 99% | -25% | 12% |
| **30m WF** | 5% | **RUINED** | 0.02 | 99% | -34% | 11% |

**No configuration reached 100% per 2-4 months without ruin and with a maximum
drawdown under 60%.** The in-sample configurations that do double every three
quarters of the time did so while at some point losing 67% to 95% of the
account. The walk-forward signal is wiped out at essentially every setting.

## Verdict

(a) is met on a median basis in-sample and fails 42% of two-month windows.
(b) is not met under any configuration, in-sample or otherwise.

Both (a) and (b) exist only in the hindsight fit. Their walk-forward twins
either fail to survive Breakout's rules at any risk level, or go to zero.

---

# Part 5 — Business model

The per-account return is unattractive. That is the wrong unit. Below is the
analysis of what actually scales.

## 1. Parallelism is unavailable; sequencing is not

Monthly-R correlation between per-asset streams running the same system:

|  | BNB | BTC | ETH | SOL | XRP |
|---|---|---|---|---|---|
| BTC | 0.324 | 1.000 | 0.665 | 0.267 | 0.299 |
| ETH | 0.424 | 0.665 | 1.000 | 0.229 | 0.336 |
| SOL | 0.118 | 0.267 | 0.229 | 1.000 | 0.196 |

Mean pairwise **rho = 0.30**. Five assets give only **2.27 effective independent
streams**.

| Accounts | Simultaneous (eff.) | Sequential (eff.) |
|---|---|---|
| 5 | 2.27 | 5.00 |
| 20 | **2.99** | **20.00** |

Twenty accounts run at once are worth three. Twenty run one after another are
worth twenty. **The scaling dimension is time, not account count.**

## 2. The right unit is return on FEE, not on notional

A prop fee is not capital deployed, it is the price of an option on someone
else's balance sheet. Downside is capped at $800; upside is a share of $100k.

| True expR | EV/account | ROI on fee | P(lose fee) | Annual EV @6 accts |
|---|---|---|---|---|
| -0.0148 (no skill) | -$133 | -0.17 | 87% | -$796 |
| 0.0000 | +$328 | +0.41 | 80% | +$1,965 |
| **+0.0240 (posterior)** | **+$1,546** | **+1.93** | 65% | **+$9,279** |
| +0.0500 | +$3,706 | +4.63 | 46% | +$22,236 |
| +0.1426 (studied) | +$17,443 | +21.80 | 4% | +$104,658 |

"1.5% per month" and "+193% on capital at risk" are the same system described in
two different units. The second is the one that matters for a business.

Bankroll survival, buying accounts sequentially, posterior edge:

| Bankroll | P(broke) | Median end | P(2x) |
|---|---|---|---|
| 5 fees ($4,000) | 12.9% | $38,576 | 87% |
| **10 fees ($8,000)** | **1.4%** | **$42,576** | **94%** |
| 20 fees ($16,000) | 0.0% | $50,576 | 89% |

Caveat that matters: this models 24 cycles as sequential draws. A funded account
pays out over up to 24 months, so the calendar time to run 24 cycles is years,
not months. The EV is right; the speed is optimistic.

## 3. Own money: growth-optimal sizing, and how fragile it is

Full Kelly on the real R distribution is f* = 8.0% per trade, implying 33%/month.
Half-Kelly 4% implies 24.4%/month, which would double capital every ~3.2 months
and meet the second target.

That is computed at the studied-data edge of +0.1426R. **Kelly is unforgiving
about that assumption.** Monthly growth when you size for one edge and the truth
is another (half-Kelly sizing):

| Sized for | f used | truth -0.015 | truth 0.000 | truth +0.024 | truth +0.050 | truth +0.143 |
|---|---|---|---|---|---|---|
| +0.024 | 0.6% | -0.6% | -0.3% | **+0.6%** | +1.3% | +4.3% |
| +0.050 | 1.4% | -1.8% | -1.0% | +1.1% | **+2.3%** | +10.2% |
| **+0.143** | **3.9%** | **-10.0%** | **-6.6%** | **-1.3%** | +2.4% | **+23.1%** |

Size for the optimistic edge and be wrong, and growth is negative **even though
the edge is still positive**. And the path is worse than the growth rate:

| f | true expR | median DD | P(DD>50%) | median 24mo | P(lose half) |
|---|---|---|---|---|---|
| 1.0% | +0.024 | 37% | 18% | 1.19x | 3% |
| 1.0% | +0.143 | 21% | 0% | 5.28x | 0% |
| 4.0% | +0.024 | 91% | 100% | **0.53x** | **49%** |
| 4.0% | +0.143 | 66% | 95% | 190x | 0% |
| 8.0% | +0.024 | 100% | 100% | 0.01x | 86% |

The 24%/month plan requires surviving a 66% drawdown in the *good* case and
loses half the account in the likely one. **f = 1% is the only sizing that is
positive in both worlds.**

## 4. The number that governs everything

Trades needed to distinguish a +0.1426R edge from a +0.024R one, 95%
confidence, 80% power: **1,074 trades = 21 months at 52 trades/month.**

You cannot know which world you are in for about two years, and the correct
action differs enormously between them. That, not the return figure, is the
central problem.

## 5. The business model this implies

Use the prop structure as **paid-for out-of-sample validation with capped
downside**, and let it resolve the edge question before own capital is scaled.

**Phase 1 (roughly 21 months).** Run prop evaluations sequentially, never in
parallel, at 0.25% risk and 2% heat. Bankroll 10 fees ($8,000), P(broke) 1.4%
at the pessimistic edge. Expected +$9,279/yr at the posterior edge, +$104,658 at
the studied one, and about -$800/yr if there is no edge at all. Own capital
either stays out or runs at f = 1%, the only sizing positive in both worlds.
The trade record accumulating across those accounts IS the experiment.

**Phase 2 (after ~1,074 trades).** The edge is now measured, not assumed. If it
confirms near +0.14R, scale own capital toward f = 2-4% knowing the drawdown
profile above. If it lands near +0.024R, stay on prop churn, which remains +EV
at roughly 2x on fees. If it is at or below zero, stop.

Why this is the right structure: it is the only configuration where the
downside is bounded ($800 a throw), the experiment pays for itself while
running, and the irreversible decision (levering own capital) is deferred until
the evidence exists to make it. Sizing own capital at 4% today is a coin flip on
an unresolved question with a 49% chance of losing half.

**What it is not.** It is not 10%/month, and it is not 100% per quarter with any
confidence. It is a capped-downside option on an unresolved edge, run at a scale
where variance cannot ruin you before the answer arrives.

---

# Part 6 — NASDAQ-100: cross-sectional equities and NQ futures

## Was volume used on crypto?

Yes, centrally. 21 of the 71 crypto features were volume or order-flow derived:
`volume`, `quote_volume`, `trades`, `taker_buy_base/quote`, `tbi` (aggressor
imbalance) and its 8/24/96-bar means and z-scores, `dq`, `dq_cum24`, `absorb`,
`flow_eff`, `avg_trade_usd`, `ats_z96`, `ats_rank480`, `trade_intensity`,
`vol_per_trade_z`, `range_per_trade`, `rpt_z`, `kyle` (impact per root notional),
`updn_ratio`.

The one rule that survived every crypto test, `vol_spike_cont`, IS a volume rule
(trade count above 1.8x its 96-bar average). `kyle`, `vol_per_trade_z` and
`range_per_trade` appear throughout the optimised rule sets. Crypto also supplied
something equities cannot: a true taker buy/sell split, i.e. real aggressor-side
flow rather than a proxy.

## Why NASDAQ was worth trying

Two structural advantages over crypto perps:
- **Cost.** NQ futures round-trip is about 0.005% (roughly $4 on ~$500k notional
  plus a 0.25pt spread) versus 0.12% on crypto. Cost drag killed every crypto edge.
- **Breadth.** Crypto gave 5 assets at rho=0.30, i.e. 2.27 effective independent
  streams. Ninety-plus names with market beta removed give far more, and breadth
  is what turns a small edge into a usable Sharpe.

## Data
97 Nasdaq-100 names, daily OHLCV + adjusted close, 1998-2026, 550,284 rows.
NQ=F hourly, 12,447 bars, 2024-04 to 2026-07 (Yahoo serves ~2 years of intraday).
47 cross-sectional features, 17 volume-derived.

## Result 1: cross-sectional long/short is the first positive walk-forward
### result in this entire study

Risk-parity long/short, top and bottom decile, net of 5bps round trip:

| Horizon | WF ann. | WF Sharpe | maxDD | Positive months |
|---|---|---|---|---|
| 1 day | +6.7% | **+0.65** | 42.9% | 58% |
| 5 day | +6.5% | **+0.68** | 35.6% | 53% |
| 21 day | +2.0% | +0.22 | 28.8% | 54% |

Crypto's walk-forward Sharpe was 0.07 or negative everywhere. This is genuinely
positive out-of-sample, market-neutral, over 28 years, and is consistent with the
published cross-sectional equity anomaly literature.

**Volume carries as much signal as price, with a smoother ride:**

| Feature set | WF Sharpe | maxDD |
|---|---|---|
| volume only (12 features) | **+0.55** | **24.4%** |
| price only (33 features) | +0.54 | 29.5% |
| both | +0.68 | 35.6% |

## Result 2: but it has decayed to nothing

Walk-forward annualised return by year:

```
2004 +14.6  2005 +13.6  2006  +3.7  2007  +7.2  2008 +31.4  2009 +24.1
2010 +11.0  2011  -3.6  2012  -9.6  2013 +10.3  2014 +15.0  2015 +13.0
2016  +6.9  2017  -5.2  2018 +19.3  2019  +3.1  2020 +31.1  2021  -3.5
2022  -6.6  2023 -12.4  2024  -9.6  2025  +8.4  2026  -6.5
```

First half **+10.7%/yr**, second half **+3.2%/yr**, and five of the last six
years negative. Two readings, and both are bad for trading it forward: either
survivorship bias inflates the early era (the universe is today's index
membership over 28 years), or the factor has been arbitraged away. The
literature supports the second; the data cannot separate them.

Threats tested:
- **Calendar artefact: CLEARED.** Removing `dow`/`dom` moves Sharpe 0.68 -> 0.63.
- **Cost: FAILS at realistic retail levels.** Edge crosses zero at ~22bps round
  trip. At 20bps, which is realistic for shorting 90 names daily, it is +1.3%/yr
  at Sharpe 0.14. Short borrow is not modelled at all.
- **Leverage to target: RUIN.** Unlevered Calmar is 0.18. 2%/month needs 4.1x,
  5%/month 12.3x, 10%/month 33x. All imply a 100% drawdown.

## Result 3: NQ futures intraday, and a bug worth reporting

First run showed unconditional expR of **+0.1942 long** vs -0.0017 short, which
looked like a large directional edge. It was not. I had resolved stops and
targets on hourly CLOSES, ignoring bar highs and lows, so stop-outs went
undetected and losers were scored as winners. For crypto I used the true 1-minute
path; Yahoo gives no sub-hourly futures data, so I re-ran on true bar high/low.

After the fix:

| | expR | monthly | implied |
|---|---|---|---|
| unconditional long | **-0.0010** | — | — |
| unconditional short | -0.0167 | — | — |
| WF thr=0.0 | +0.0024 | +0.53R | **+0.01%/mo** |
| WF thr=0.3 | -0.1081 | -5.15R | -0.16%/mo |
| IS thr=0.3 | +1.1394 | +79R | +26.07%/mo |

The entire apparent long edge was an artefact of undetected stop-outs. Corrected,
NQ sits on the same martingale null as BTC, and walk-forward is zero. In-sample
reaches 26%/month, the same hindsight premium seen everywhere in this study.

## Verdict on NASDAQ

Better than crypto, and for the predicted reason: cheap execution plus real
breadth produced the only positive out-of-sample Sharpe in the project (0.65-0.68
on the cross-sectional book). Volume features carried it as strongly as price
features, which answers the question directly.

It still does not reach the target, for the same arithmetic as everywhere else:
Calmar 0.18 means any leverage sufficient for 2%/month implies ruin. And the
edge has been flat-to-negative since 2021, so even the modest version is not
something I would trade forward without knowing whether survivorship or decay
explains it.

What this result IS: a legitimate institutional quant equity strategy. Sharpe
0.65 market-neutral at 5bps execution is roughly what systematic equity funds
run, unlevered, on prime-broker cost structures. It is not a retail path to
10%/month, and no amount of leverage converts it into one.

`quant/src/`: `eqfetch.py`, `eqml.py`, `eqstress.py`, `nqml.py`.

---

# Part 7 — Multi-timeframe cascade, MCB triggers, split entries

Tests three things the study had not: session-anchored confluence levels, HTF
regime gating, and lower-timeframe entry timing — the last using MCB Clone v1
(WaveTrend + MFI clone divergences and trigger-wave crosses) ported from
FROZEN_SPEC.md, and evaluated with a split-entry structure.

Setup: 4h `vol_spike_cont` decides direction (the one rule that survived every
earlier test, pooled +0.1448R over 3,391 signals on 5 assets). A lower timeframe
(15m or 5m) decides the moment. Three entry variants on identical signals:
A all at market, B all on confirmation else skip, C half at market and half on
confirmation.

## The main result: confirmation selects LOSERS

| LTF trigger | Confirm rate | expR on UNCONFIRMED | expR on CONFIRMED |
|---|---|---|---|
| 15m stacked div | 1% | +0.150 | **-0.430** |
| 15m either-osc div | 11% | +0.186 | -0.211 |
| 15m WT cross into OB/OS | 42% | **+0.421** | -0.235 |
| 5m stacked div | 7% | +0.180 | -0.309 |
| 5m either-osc div | 53% | **+0.404** | -0.090 |
| 5m WT cross into OB/OS | 93% | **+0.864** | +0.087 |

Every selective trigger shows the same sign. The mechanism is not mysterious: if
4h says long and 15m then prints a bullish divergence or an oversold cross,
price PULLED BACK — the move failed to run. Signals that never offer a pullback
entry are the ones that went straight up. For a momentum signal this is exactly
backwards, and "wait for lower-timeframe confirmation" is actively harmful here.

## The trap in that table

The +0.42 and +0.86 figures on unconfirmed signals look like a spectacular
filter. **They are not tradeable.** Whether a signal confirms is determined by
price action AFTER entry, inside the 8-hour window. Membership in the
"unconfirmed" set is unknowable at signal time, so filtering on it is
look-ahead. Recorded here because it is the most seductive number in this part.

## Split entry: validated, but it does not beat market entry

The split proposal fixes a real flaw in the pure-precision design — waiting
skips the runners — and it does what it was meant to:

| Config | A market | B precision | C split 50/50 |
|---|---|---|---|
| 15m div | +0.43%/mo | +0.13%/mo | **+0.41%/mo** |
| 15m cross_ext | +0.43%/mo | +0.29%/mo | **+0.41%/mo** |
| 5m div | +0.43%/mo | +0.36%/mo | **+0.44%/mo** |
| 5m cross_ext | +0.43%/mo | +0.38%/mo | **+0.41%/mo** |

C beats B in every single configuration, which is exactly the claim the split
was designed to make. But C does not beat A: taking everything at market is
already optimal for this signal, because the signal's edge lives in the moves
that never retrace.

## The one config that looked better, and did not survive a bootstrap

15m WaveTrend cross confirms 100% of the time, so it selects nothing — it is a
pure timing shift. It showed expR +0.1487 vs +0.1448 and maxDD 91.4R vs 105.9R,
i.e. +0.51%/mo vs +0.43%/mo. Block bootstrap, 4,000 resamples, paired:

- difference in expR **+0.0039, 95% CI [-0.022, +0.029]**, P(B>A) = 0.595
- difference in maxDD 95% CI **[-41.1, +19.0]R**, P(B lower) = 0.718

Both straddle zero. The improvement is noise.

## Verdict

For a momentum signal, entry timing on lower timeframes does not add edge, and
confirmation-based entry subtracts it. The split-entry structure is the correct
way to run a two-tranche entry if one is used at all — it dominated
precision-only everywhere — but for this system the best entry remains 100% at
market on the higher-timeframe signal.

`quant/src/`: `mcb.py` (MCB Clone v1 port), `mtf.py` (session levels, HTF
gating, pullback refinement), `splitentry.py`, `run_mtf.py`.

---

# Part 8 — Divergence-driven exits and stop management

Part 7 showed a same-direction divergence appearing AFTER entry marks the losing
cohort. That cannot be used to select entries (membership is only knowable after
the fact) but it CAN be used to manage risk, because you are already in the
trade when the divergence prints. Causal, and tradeable.

Variants against an identical entry (4h vol_spike_cont, market fill, 2xATR stop,
2R target, 3,391 signals, 5 assets):

- **TIGHTEN** on the first same-direction divergence after entry, move the stop
  to that divergence pivot's own extreme plus a buffer
- **REDDOT** exit at market on the first adverse trigger-wave cross
- **BOTH**

R is always measured against the ORIGINAL risk, since that is what the position
was sized on, so a tightened stop that is hit loses less than 1R.

## Results (15m divergences, 5% buffer)

| Variant | expR | avg win | avg loss | %stop | %moved | maxDD | %/mo |
|---|---|---|---|---|---|---|---|
| BASE | +0.1448 | +1.771 | -0.982 | 56% | 0% | 104.9R | 0.43% |
| **TIGHTEN** | +0.1197 | +1.365 | **-0.606** | 77% | 66% | **54.7R** | **0.68%** |
| REDDOT | -0.0158 | +0.263 | -0.299 | 7% | 0% | 84.1R | -0.06% |
| BOTH | -0.0131 | +0.264 | -0.288 | 11% | 11% | 75.1R | -0.05% |

Stable across the buffer sweep: 0.67% / 0.68% / 0.59% at buffers 0 / 5% / 15%.

**REDDOT fails even when defined correctly.** The first run used any WaveTrend
cross-down, which exited 98% of trades almost immediately. Restricting it to the
true Market Cipher red dot (cross while overbought) still exits 92% of trades,
because on a 15m chart that event occurs many times inside a multi-day hold.
It is not an exit rule at this timeframe pairing, it is churn.

## What survives a bootstrap, and what does not

Paired block bootstrap, 4,000 resamples, block 40:

| Statistic | Estimate | 95% CI | Verdict |
|---|---|---|---|
| maxDD difference | **-39.2R** | **[-98.8, -0.7]** | **REAL** (P=0.978) |
| monthly-return difference | +0.123pp | [-0.270, +0.580] | not established (P=0.761) |

The drawdown reduction is statistically solid. The return improvement is not.

Stability is mixed and argues for caution:

| Year | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|
| Better | BASE | TIGHTEN | TIGHTEN | BASE | BASE | BASE |

Per symbol, TIGHTEN reduces expR on BTC (+0.145 -> +0.094), SOL (+0.163 ->
+0.108) and BNB (+0.138 -> +0.104), is flat on ETH, and improves only XRP
(+0.159 -> +0.179).

## Verdict

The idea is mechanically sound and it does what it was designed to do: average
loss falls 38% and maximum drawdown roughly halves, both robustly. That matters
specifically under Breakout rules, where position size is set by the distance to
a static floor — halving drawdown roughly doubles the size that floor permits.

But raw per-trade edge falls, on four of five symbols and in four of six years,
and the headline monthly-return gain does not clear a bootstrap. The honest
statement is: **a real and reliable drawdown reduction, purchased with a real
reduction in expectancy, whose net effect on risk-adjusted return is positive at
about 76% confidence rather than established.**

It is the most promising structural idea tested in this study, and it is still
not enough to change the headline conclusion.

`quant/src/`: `exits.py`, `run_exits.py`, `mcb.py` (extended to return
divergence pivot levels).

## Part 8b — Sequential exits and the timeframe sweep

Correction to Part 8: REDDOT armed the red-dot exit from ENTRY. The intended
design is sequential - the divergence must confirm first, and only then does a
red dot become an exit trigger. Added as SEQ (arm on divergence, exit on red
dot) and SEQ_TIGHT (arm, tighten the stop, exit on red dot). Fractal detection
was numba-compiled so 1-minute timeframes are tractable.

### Loss reduction is monotone in timeframe, not constant

| LTF | avg loss | % stop moved |
|---|---|---|
| BASE | -0.982 | 0% |
| 1h | -0.844 | 30% |
| 30m | -0.747 | 46% |
| 15m | -0.606 | 66% |
| 5m | -0.406 | 88% |
| 1m | -0.220 | 98% |

Lower timeframes print more divergences, so the stop moves more often and lands
tighter. Perfectly ordered across all five.

### Best monthly return: 15m. Best R:R: 1m. They are not the same.

| LTF (TIGHTEN) | R:R | expR | maxDD | %/mo |
|---|---|---|---|---|
| BASE | 1.80 | +0.1448 | 104.9R | 0.43% |
| 1h | 2.03 | +0.1458 | 98.3R | 0.46% |
| 30m | 2.10 | +0.1419 | 68.3R | 0.65% |
| **15m** | 2.25 | +0.1197 | **54.7R** | **0.68%** |
| 5m | 2.67 | +0.0667 | 43.7R | 0.48% |
| 1m | **3.53** | +0.0156 | 56.6R | 0.09% |

An inverted-U in return with a monotone increase in R:R. At 1m the reward/risk
ratio nearly doubles versus baseline, and it is the worst configuration tested,
because the win rate collapses to 7% (93% of trades stop out). Optimising for
R:R alone would pick exactly the wrong timeframe.

### The sequential fix works

| 15m variant | expR | signal-exit rate | %/mo |
|---|---|---|---|
| REDDOT (armed from entry) | -0.0158 | 92% | -0.06% |
| **SEQ (armed by divergence)** | **+0.0913** | 64% | **+0.63%** |
| SEQ_TIGHT | +0.0939 | 60% | +0.63% |
| TIGHTEN only | +0.1197 | - | +0.68% |

Requiring the divergence first takes the red-dot exit from actively harmful to
competitive. It still does not beat tightening alone, but it is within noise.

### Best configuration found

4h vol_spike_cont entry, 15m divergence, stop moved to the divergence pivot with
a 5% buffer: **0.68%/month against a 0.43% baseline**, drawdown 54.7R against
104.9R. The Part 8 bootstrap caveat stands unchanged: the drawdown halving is
statistically real (P=0.978), the return improvement is not (P=0.761).

---

# Part 9 — Composition, sizing, partial exits, carry, and own capital

## Own capital, no prop rules: the headline answer

No 3% daily rule, no 6% floor. Sizing by growth rate on the real R distribution,
24-month Monte Carlo, 4,000 paths, 52 trades/month.

**At the studied edge (+0.12R, TIGHTEN system):**

| Sizing | f/trade | median monthly | median 24mo | median DD | P(DD>50%) | P(ruin) |
|---|---|---|---|---|---|---|
| quarter Kelly | 2.8% | **+16.0%** | 35x | 40% | 16% | 0% |
| half Kelly | 5.5% | **+28.6%** | 416x | 67% | 96% | 0% |
| full Kelly | 11.0% | +39.0% | 2,724x | 93% | 100% | 0% |

At quarter Kelly that is a double roughly every 4.6 months; at half Kelly, every
2.8 months. So the "100% every 2-4 months" target IS reachable on own
capital - **if the studied edge is the true edge.**

**At the holdout-adjusted posterior (+0.024R), same system, same sizing:**

| Sizing | f/trade | median monthly | median 24mo | median DD | P(ruin) |
|---|---|---|---|---|---|
| quarter Kelly | 2.8% | **+1.2%** | 1.32x | 64% | 1% |
| half Kelly | 5.5% | **-1.9%** | **0.63x** | 91% | 18% |

That is the entire question in two tables. The same system, sized identically,
returns 16%/month or 1.2%/month depending on which edge estimate is true - and
at half Kelly the posterior case LOSES money while drawing down 91%.

Removing the prop constraints does not remove the uncertainty. It converts it
from "you fail the evaluation" into "you lose your own capital".

## Composition of the two best findings: failed

Aux-model signal (walk-forward) combined with the 15m divergence stop:

| Variant | sizing | expR | maxDD | %/mo |
|---|---|---|---|---|
| TIGHTEN | FIXED | +0.0256 | 407R | **+0.16%** |
| TIGHTEN | CONVICTION | +0.0211 | 483R | +0.11% |
| PARTIAL_TIGHT | FIXED | +0.0025 | 501R | +0.01% |
| BASE | FIXED | -0.0131 | 1222R | -0.03% |

Far below the 0.68%/mo the same exit rule achieves on `vol_spike_cont`. The
aux-model signal at 4h with a 0.2 threshold produces 17,080 signals at negative
expectancy - it is barely selective. The gain reported earlier was at 1h.

## Conviction sizing: definitively fails

Decile mean R by model confidence:

```
+0.00  -0.03  -0.01  -0.01  +0.04  -0.03  +0.05  -0.02  -0.05  -0.07
```

Rank correlation between confidence decile and realised R: **-0.332**. The
highest-conviction decile is the worst. The model cannot rank trades, so sizing
by its confidence is actively harmful (0.16% -> 0.11%). This also explains why
raising the entry threshold never helped much.

## Partial exits: no help

Booking half at +1R and moving to breakeven returns +0.0025 expR against
+0.0256 for tightening alone. Cutting winners early costs more than the variance
reduction is worth for this R distribution.

## Funding carry: real, high Sharpe, low return

Long spot / short perp, gross of costs:

| Symbol | Ann. gross | % positive months | Sharpe |
|---|---|---|---|
| BTC | **10.90%** | 86% | **2.43** |
| ETH | 11.65% | 84% | 2.04 |
| XRP | 13.11% | 77% | 1.78 |
| SOL | 0.78% | 71% | 0.05 |
| BNB | -0.55% | 24% | -0.09 |

BTC and ETH are genuinely high-Sharpe. The equal-weight basket collapses to
Sharpe 0.74 (4.75-6.98%/yr net) because SOL had a -35.5% month during a funding
inversion and BNB funding is negative 76% of the time. Naive equal weighting is
the wrong construction; the trade should be conditional on funding being
positive, and concentrated in BTC/ETH.

Reaching 2%/month needs 5.6x leverage on the basket, which reintroduces
liquidation risk on the short-perp leg precisely when funding inverts. This is
not a path to the target, but it is the only stream in the study with a
mechanical reason to be reliably positive, and it composes with a directional
book rather than competing with it.

## Selection adjustment: the first null was wrong

A block-shuffle null over the 64-configuration exit search produced a
best-of-search of 1.58%/mo mean against an observed 0.685%, implying p = 1.000.
That null is **mis-specified**: shuffling destroys loss clustering, real markets
cluster losses, and the score depends on 1/maxDrawdown - so shuffled paths have
artificially small drawdowns and inflated scores.

What it does establish, and this matters: the "%/month at a 6% floor" statistic
is dominated by drawdown-path luck. Every such figure in this study carries far
more uncertainty than a point estimate suggests.

The correctly specified null (shift the MCB event timestamps by 7-90 days,
preserving market, trades and drawdown structure while breaking only the
divergence-to-outcome alignment) is in `selection2.py`.

---

# Part 10 — Is the edge clustered, and can bad clusters be filtered?

## Concentrated, but not autocorrelated

Null = the same trades with their time order shuffled, which preserves the
return distribution exactly and destroys only the sequencing.

| Statistic | Real | Null mean | Percentile |
|---|---|---|---|
| Monthly std | 18.07 | 8.16 | **100%** |
| **Top-10% of months' share of total profit** | **69.2%** | 32.3% | **100%** |
| Longest negative run (months) | 4 | 2.53 | 90% |
| Variance ratio, 2 months | 0.764 | 0.981 | 4% |
| Variance ratio, 6 months | 0.615 | 0.927 | 14% |

**Sixty-nine percent of all profit comes from seven months out of sixty-six.**
Monthly variance is more than double what the shuffled null produces.

But the variance ratios are BELOW one and month-to-month autocorrelation is
**-0.20 at lag 1**. So the returns are heavily CONCENTRATED and mildly
MEAN-REVERTING, not momentum-clustered. Those are different properties and only
the first is present. There is no hot-streak to ride.

This reframes the system. It is not a compounding machine that occasionally
stumbles; it is closer to an option on a handful of trending regimes, with the
rest of the calendar roughly flat. That is structurally incompatible with a
"consistent 10% every month" objective regardless of sizing.

## Filtering losing clusters from the equity curve: it fails

First attempt showed the trailing-10-trade filter lifting expectancy from
+0.1197 to +0.4069 and monthly return from 0.68% to **4.43%**. That was a
look-ahead bug of mine: the filter sorted trades by SIGNAL time and summed the
previous k rows, but trades hold for days, so many of those k were still OPEN at
the decision point and their outcomes were not yet knowable. The monotone
pattern across lookbacks (10-trade best, 100-trade weakest) is the signature of
exactly that overlap bias.

Rebuilt causally, counting only trades whose EXIT preceded the signal:

| Filter | kept | expR | maxDD | %/mo |
|---|---|---|---|---|
| none (baseline) | 100% | +0.1197 | 54.7R | **0.68%** |
| trailing 10-trade R > 0 | 43% | +0.1159 | 41.1R | 0.38% |
| trailing 25-trade R > 0 | 49% | +0.0808 | 89.1R | 0.14% |
| trailing 50-trade R > 0 | 56% | +0.0734 | 76.8R | 0.17% |
| trailing 100-trade R > 0 | 64% | +0.0655 | 78.6R | 0.17% |

**Every equity-curve filter makes it worse**, and the mechanism is visible in
the autocorrelation: at -0.20, periods following losses are slightly BETTER than
average, so standing aside after a drawdown removes precisely the trades that
recover. Equity-curve trading is actively harmful on this system.

## What this means

The two results together are decisive for the original objective. The edge is
concentrated in rare regimes, it is not predictable from its own history, and
the concentration cannot be filtered. A system whose profit is 69% delivered in
7 months out of 66 cannot be turned into a monthly income stream by better
sizing, better exits, or better filters - those change the distribution's scale,
not its shape.
