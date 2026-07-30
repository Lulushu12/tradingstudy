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
