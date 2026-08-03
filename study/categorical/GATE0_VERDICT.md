# Gate 0 verdict

> # RETRACTED IN PART - SEE CORRECTION.md
>
> **The fade-template results in this document are void.** The measurement counted untakeable
> entries (bar t+1 opened already past the take-profit) as automatic full-size wins. In the
> headline 4H set that was 404 of 902 signals, 44.8%. Corrected, the 4H fade goes from
> **+0.0991 R net to +0.0017 R**, and the 15m fade goes from +0.0165 to **-0.1478 R**. The
> section 3 cost-by-timeframe table and every fade conclusion drawn from it are wrong.
>
> Unaffected: sections 1, 2, 4, 5 and 6 below, which use symmetric barriers around the entry
> price where this defect cannot occur. They found no effect, and that finding stands.
>
> Phase 1 was never contaminated and its verdict is DEAD (PHASE1_RESULTS.md, 5 of 6 kill
> thresholds failed, negative expectancy even at zero cost).

> **UPDATE after the per-year split (GATE0_STABILITY.md).** Two corrections to this
> document. First, the **1h row in section 3 is void**: that parquet has a 520-day hole
> (2022-12-31 to 2024-06-04) swallowing all of 2023, found while running the split.
> 15m and 4H have complete coverage and their rows stand. Second, the section 4 concern
> that the surviving edge might be a 2021 artifact is **resolved and dismissed**: the 4H
> fade template is net positive in 6 of 6 years, worst year +0.0760 R. The result did not
> die. It also survives pessimistic fills, both-hit reassignment, and an overlap check.
> 15m does not survive pessimistic fills. See GATE0_STABILITY.md.

Pre-committed pass condition (SYSTEMIZATION.md s4, written before any result existed):

> monotone separation of continuation probability across the classifier spectrum, not merely one
> good bucket.

**Verdict: PASS on the mechanism, FAIL on the configuration the video teaches.**

The categorical framework's central claim is true and measurable. The way the video implements it
is not tradeable. Those are two separate findings and both are load-bearing.

---

## 1. The headline test failed, and it failed for an instructive reason

5m, ER(20), symmetric +/-1 x ATR14 barriers, 40-bar horizon, 522,550 decided samples:

| ER decile | continuation % | 95% block-bootstrap CI |
|---|---|---|
| 0 (most consolidative) | 50.07 | 49.67 to 50.50 |
| 9 (most directional) | 50.04 | 49.31 to 50.85 |

Spread bottom to top: **-0.03 points**. Non-monotone. Causal expanding-quantile bucketing gives
the same answer (-0.30 points). Whatever the label is doing, it is not moving a symmetric
1:1 barrier race on 5m BTC.

The classifier horse race says the same thing. ER -0.03, RangeEff +0.31, VR +0.99, ADX +1.20,
Hurst -0.42 points of spread. Nothing clears the noise floor.

Worse, the 36-cell parameter grid shows the effect **changes sign with the parameters**:

| lookback / barrier | spread |
|---|---|
| n=10, 0.5 x ATR | **-3.69 pts** |
| n=20, 1.0 x ATR | -0.03 pts |
| n=80, 2.0 x ATR | **+4.50 pts** |

Anyone who picks the bottom row confirms the framework. Anyone who picks the top row refutes it.
That is not a property of the market, it is the standard horizon-dependence of autocorrelation:
short lookbacks with tight barriers see microstructure mean reversion, long lookbacks with wide
barriers see momentum. A symmetric barrier race cannot separate the regime label from the
measurement horizon.

**So the headline test was the wrong instrument.** It conditions only on the sign of recent
displacement. The video's trades condition on position within the range. That distinction is the
whole ballgame, and it is why the trade-shaped tests below give a completely different answer.

## 2. The trade-shaped tests confirm the framework, monotonically, on both templates

Both templates use a 20-bar Donchian range on 5m, entry at bar t+1 open, ~39,400 samples per
decile after filtering out degenerate near-midpoint entries.

**Direction template** (target = range extreme plus buffer, stop = range midpoint):

| ER decile | win rate | mean R:R | gross expectancy (R) |
|---|---|---|---|
| 0 | 20.98% | 3.10 | **-0.4181** |
| 4 | 37.74% | 2.21 | -0.0345 |
| 9 | 58.32% | 0.93 | **+0.0429** |

**Consolidation template** (target = range midpoint, stop = beyond the extreme):

| ER decile | win rate | mean R:R | gross expectancy (R) |
|---|---|---|---|
| 0 | 79.02% | 0.47 | **+0.0978** |
| 4 | 62.26% | 0.74 | +0.0057 |
| 9 | 41.68% | 1.54 | **-0.0357** |

Monotone across ten buckets, both templates, opposite signs, in exactly the direction the video
predicts. Fading pays in consolidation and stops paying in direction. Breaking out pays in
direction and loses badly in consolidation. The -0.4181 R on breakout trades in the most
consolidative decile is the single largest effect in the study, and it is the video's own warning
made quantitative:

> "you will lose all your money if you're doing mean reversion in direction or targeting new
> areas in consolidation" [03:07]

That statement is correct. It is now measured.

Note what the win rates say: the profitable consolidation trade is **79% at 0.47 R:R**, not 1:1.
The video's 1:1 recommendation is the wrong shape for its own best setup. This confirms
SYSTEMIZATION s6.2.

## 3. Then costs kill it, and exactly where the video trades

Same consolidation template, lowest ER decile, across timeframes, at the repo's standing 0.08%
round-trip assumption and no slippage:

| Timeframe | n | win rate | median risk (% of price) | gross R | cost/R | **net R** |
|---|---|---|---|---|---|---|
| 5m | 39,407 | 79.02% | 0.448% | +0.0978 | 0.179 | **-0.0807** |
| 15m | 13,840 | 80.33% | 0.872% | +0.1083 | 0.092 | **+0.0165** |
| 1h | 1,702 | 77.73% | 1.680% | +0.0765 | 0.048 | **+0.0289** |
| 4H | 902 | 80.71% | 3.894% | +0.1196 | 0.021 | **+0.0991** |

This is the whole study in one table.

**Gross expectancy is roughly timeframe-invariant**: +0.077 to +0.120 R everywhere. The edge per
unit of risk does not care what timeframe you look at, which is the one part of the video's
universality claim that survives contact with data.

**Cost per R is not invariant**: 0.179 on 5m falling to 0.021 on 4H, because risk distance grows
with timeframe while the fee is a fixed percentage. Net expectancy crosses zero between 5m and
15m and grows monotonically from there.

The video teaches 20-to-40-second charts. That is two to three timeframe steps *below* the 5m row,
where cost/R is already almost double the gross edge. Extrapolating the trend, the taught
configuration is not marginally unprofitable, it is unprofitable by a wide margin, and no entry
trigger refinement closes a gap that arithmetic opened.

## 4. Non-stationarity

Splitting the headline test by year:

| year | spread |
|---|---|
| 2021 | +4.89 pts |
| 2022 | +0.30 pts |
| 2023 | +1.67 pts |
| 2024 | -1.72 pts |
| 2025 | -0.90 pts |
| 2026 | -2.45 pts |

The symmetric-barrier version of the effect has been sign-flipped for three consecutive years.
The trade-shaped version has not been split by year yet. **That is the first thing Phase 1 must
do**, because if the +0.0991 R on 4H is concentrated in 2021 then it is a bull-market artifact and
the whole thing dies there.

## 5. The session fairness check

The video's claim is NQ at the equity open, so a 24/7 crypto average could in principle wash out a
session-local effect. Testing that on BTC:

| Window (UTC) | n | ER dec 0 | ER dec 9 | spread |
|---|---|---|---|---|
| 13:30-13:55 (US open + 25m) | 10,815 | 48.33% | 50.36% | +2.04 |
| 13:30-14:30 | 32,425 | 48.75% | 51.86% | +3.11 |
| 14:30-20:00 | 130,706 | 49.34% | 51.87% | +2.53 |
| 00:00-13:30 (outside RTH) | 293,858 | 50.54% | 50.01% | -0.53 |

There is a weak, correctly-signed spread during US equity hours that is absent outside them. But
the hour-by-hour breakdown swings from -6.07 to +7.01 with rho flipping sign between adjacent
hours, which is what 240 cells of ~2,200 samples look like when they contain nothing. The
equity-open hour itself reads -2.96, the wrong way. This does not vindicate the NQ version and it
does not refute it. BTC is not NQ. It only removes "it works at the open" as a free excuse: if
that is the claim, it needs its own evidence on its own data.

---

## 6. What this means

**The framework is not nonsense.** Its core claim is real, monotone, and measurable across
roughly 400,000 samples on both trade templates. That is more than most published retail
strategies can say, and the author arrived at it by screen time and honest self-observation with
no quantitative apparatus at all. Credit where it is due.

**The framework as taught is not tradeable.** The edge is about +0.10 R gross. On 20-second charts
the toll is several times that. The video spends 41 minutes on bracket sizing, session windows,
journaling and psychology, and zero seconds on the one number that determines whether any of it
matters. Every hard-won discretionary refinement in that video is being applied inside a
configuration where the arithmetic was already lost.

**The author's own instincts point the right way and he followed them backwards.** He concluded he
should trade consolidation only [39:44] and the data agrees: the consolidation template is the
profitable one. He concluded he is "terrible on higher time frames" [18:27] and abandoned them,
and higher timeframes are the only place his edge survives costs. He recommends 1:1 [13:01] and
his best setup is 79% at 0.47 R:R. His live stats show a 1.59 payoff ratio that his own taught
rules forbid.

## 7. Honest limitations

1. **Sample sizes collapse on the timeframes that work.** 4H has 902 samples in the top cell.
   The most attractive row in section 3 is the least well-sampled. No block bootstrap has been run
   on the trade-shaped tests yet.
2. **Samples overlap.** Effective n is well below nominal n everywhere, and the 4H trades overlap
   heavily in calendar time.
3. **Horizon is long.** The 4H test allows 200 bars, up to 33 days. That is swing trading, not the
   scalping the video describes. It is a different strategy that happens to share a classifier.
4. **Costs are the repo's standing 0.08% assumption with no slippage added.** Slippage hurts the
   5m rows most and the 4H rows least, so adding it widens the conclusion rather than reversing it.
5. **Decile 0 is the best cell and it is the one being reported.** Mild selection. Deciles 1 and 2
   are also net positive on 1h and 4H, which is reassuring but does not eliminate the concern.
6. **This is BTC.** It is not NQ, it is not futures, and it has no opening auction.
7. **Not yet split by year on the trade-shaped tests.** See section 4. This is the most likely
   thing to kill the surviving result.

## 8. Recommended next step

Do not build the 5m or sub-minute version. The arithmetic is already decided.

Phase 1 candidate, if you want one: **consolidation template only, 1h or 4H, lowest ER decile,
target = range midpoint, stop = beyond the range extreme, no 1:1 bracket.** Before any of that,
run the per-year split on the trade-shaped tests. If the 4H edge lives in 2021, it dies there and
this folder becomes a well-documented negative result, which is still worth having.

Per the repo protocol: this is the end of Gate 0. Nothing proceeds without an explicit go.
