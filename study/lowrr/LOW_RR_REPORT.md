# Low R:R, high winrate, high timeframe, high frequency, on Breakout

Question asked: can we build a system with reward:risk below 1 and a high winrate,
on a high timeframe so fees stay small, that still trades often enough to matter and
still fits Breakout's rules?

Short answer: the low R:R part is easy and free, the high winrate part is easy and
free, and neither of them creates a single basis point of edge. One rule family
survives at rr below 1 after honest treatment, and it is small. On a single
instrument it earns about 0.3 R per month, which at a Breakout-safe risk size is
roughly 0.15% per month. That is not a system, it is a rounding error. The frequency
you want has to come from instrument count, not from cutting R:R.

All numbers below come from real code in `study/lowrr/`. Nothing is estimated.

---

## 1. The cost model changed, and it matters

The earlier study (`study/STRATEGY_FINDINGS.md`) used 0.08% round-trip commission and
nothing else. Breakout's published schedule has a second term:

- commission: $3.50 per side per $10,000 notional, so 0.07% round trip
  (one source quotes 0.04% per side, i.e. 0.08% round trip; the difference is inside
  the slippage headroom reported below)
- **overnight financing: 5 bps of notional at 00:00 UTC, every night the position is open**

Expressed in R, where 1R is the risk budget per trade:

```
notional / equity   = risk_frac / stop_frac
cost_R              = (commission_rt + slippage_rt + 0.0005 * nights) / stop_frac
```

Both terms are divided by the stop distance, which is why a wide stop makes fees look
small. But the carry term keeps accruing. On 4H with a 1.5 x ATR14 stop (2.47% of
price on average), one night costs 0.020 R. A 2:1 trade holds 2.2 nights on average,
so carry adds 0.045 R, which is **larger than the entire commission** (0.036 R).

So "high timeframe means low fees" is only half true at Breakout. Commission scales
down with stop width; carry scales up with holding time. This is the one genuine
structural point in favour of low R:R: a 0.25:1 trade on 4H is held about 6 hours and
crosses 0.2 nights, so it pays almost no carry.

Verify the exact schedule with Breakout directly before trusting any of this. It is a
Gate 0 item and I have only public sources.

## 2. The barrier ladder: what cutting R:R actually buys

`lowrr/barrier.py` resolves a hypothetical long AND short at every single 4H and 1D
bar, on the true 5-minute price path, across an R:R ladder. Stop = 1.5 x ATR14. No
signal, no filter. This is the geometry with the edge removed.

4H, 11,128 bars, 2021-05 to 2026-06:

| rr | realised WR | fair 1/(1+rr) | nights | cost R | breakeven WR | **edge needed** |
|----|------------|---------------|--------|--------|--------------|-----------------|
| 0.25 | 80.4% | 80.0% | 0.32 | 0.052 | 83.4% | **+3.1 pts** |
| 0.33 | 75.5% | 75.2% | 0.41 | 0.054 | 78.6% | **+3.1 pts** |
| 0.50 | 66.9% | 66.7% | 0.60 | 0.058 | 69.9% | **+3.0 pts** |
| 0.75 | 57.0% | 57.1% | 0.87 | 0.064 | 60.2% | **+3.3 pts** |
| 1.00 | 50.0% | 50.0% | 1.14 | 0.070 | 53.0% | **+3.0 pts** |
| 2.00 | 34.0% | 33.3% | 2.21 | 0.091 | 36.0% | **+2.0 pts** |

The market hands you the fair line to within a few tenths of a point at every rung.
An 80% winrate at 0.25:1 is not an achievement, it is the default. Gross expectancy
along the whole ladder is +0.005 R or less.

The winrate edge you must supply is about 3 points at every rr below 1, and it is
*smaller* at 2:1 (2.0 points), because the wider target dilutes the fixed cost faster
than it widens the odds.

1D behaves worse, not better: unconditional winrates come in 1 to 2.4 points *below*
fair, and at 2:1 the carry cost triples to 0.096 R because trades hold 12 nights.

## 3. Why low R:R throws edge away (the important table)

`lowrr/edge_scaling.py`. For each rule, `lift` is the conditional winrate minus the
unconditional winrate at the same rr, so it isolates what the signal contributes. The
identity `grossR = (1 + rr) * lift` is exact.

4H, 1.5 x ATR stop, non-overlapping trades, 5m path resolution:

```
rule                  rr     WR  uncond   lift  grossR  costR   netR  t/mo   R/mo
S_dntrend_at_200    0.25  83.8%   80.4%  +3.4%  +0.047  0.050 -0.003   6.7  -0.02
S_dntrend_at_200    0.50  73.3%   66.9%  +6.4%  +0.100  0.057 +0.043   4.5  +0.19
S_dntrend_at_200    1.00  61.8%   50.0% +11.8%  +0.236  0.066 +0.170   3.2  +0.55
S_dntrend_at_200    2.00  45.6%   34.0% +11.5%  +0.368  0.094 +0.273   2.3  +0.63

L_volspike18_up     0.25  82.1%   80.4%  +1.7%  +0.026  0.054 -0.028   6.3  -0.18
L_volspike18_up     0.50  71.0%   66.9%  +4.1%  +0.065  0.058 +0.007   6.3  +0.05
L_volspike18_up     1.00  57.7%   50.0%  +7.7%  +0.154  0.068 +0.086   5.6  +0.48
L_volspike18_up     2.00  45.8%   34.0% +11.8%  +0.375  0.088 +0.287   4.1  +1.17

S_bb_break_dn       0.25  86.0%   80.4%  +5.6%  +0.074  0.045 +0.029  10.6  +0.31
S_bb_break_dn       0.50  72.4%   66.9%  +5.6%  +0.086  0.049 +0.037   8.8  +0.33
S_bb_break_dn       1.00  54.0%   50.0%  +4.0%  +0.081  0.057 +0.024   6.5  +0.15
S_bb_break_dn       2.00  38.1%   34.0%  +4.0%  +0.142  0.075 +0.067   4.6  +0.31
```

There are two distinct shapes here, and the distinction is the answer to the question.

**Drift edges** (trend continuation: `S_dntrend_at_200`, `L_volspike18_up`). The lift
GROWS with rr, from ~2-3 points at 0.25:1 to ~12 points at 2:1. Drift needs distance
and time to express itself. Harvesting these at low R:R destroys most of the edge:
`L_volspike18_up` goes from +1.17 R/month at 2:1 to +0.05 R/month at 0.5:1. This is
the family the earlier study found, and it is emphatically a high-R:R family.

**Front-loaded edges** (`S_bb_break_dn`: 4H close below the lower Bollinger band,
short). The lift is FLAT or slightly higher at low rr: +5.6 points at 0.25:1 and 0.5:1
versus +4.0 at 1:1. The follow-through happens in the first few hours and then dies.
This one genuinely does not care whether you take 0.25:1 or 2:1, and it is the only
family where "low R:R" is not a self-inflicted wound.

So a low R:R system is possible, but only on the second kind of signal, and only
because that signal's edge happens to be front-loaded. Cutting R:R never creates the
front-loading; you have to find a signal that already has it.

## 4. What survives at rr below 1 on BTC

`lowrr/scan.py` sliced the full outcome universe by 492 causal conditions. 58 showed
positive net expectancy in both train (pre-2025) and test (2025+). At a nominal 5%
level, 492 hypotheses buy you about 25 false positives for free, so that count alone
means very little.

`lowrr/finalists_lowrr.py` then applies the treatment that matters:

- **de-overlap**: only trades you could actually hold one at a time. The scan's
  n=728 for `bb_break_dn` becomes n=533. Consecutive bars satisfying the same
  condition are one opportunity, not many.
- **stationary block bootstrap** (block=10) on the non-overlapping sequence, which
  keeps the streakiness that makes naive standard errors a lie.
- 3 stop widths x 7 R:R rungs, so a survivor has to survive a grid, not a point.

Result at rr below 1, across the whole grid, exactly one rule is positive in train
AND test at every rung and every stop width:

**`S_bb_break_dn`: 4H close below the lower Bollinger(20, 2) band, go short,
stop 1.5 x ATR14.**

| rr | n | trades/mo | WR | breakeven WR | net R | train | test | bootstrap 95% CI |
|----|---|-----------|----|--------------|-------|-------|------|------------------|
| 0.25 | 641 | 10.6 | 86.0% | 83.0% | +0.029 | +0.031 | +0.026 | -0.002 to +0.060 |
| 0.33 | 609 | 10.0 | 80.6% | 78.1% | +0.026 | +0.024 | +0.029 | -0.011 to +0.064 |
| 0.50 | 533 | 8.8 | 72.4% | 69.4% | +0.037 | +0.033 | +0.048 | -0.023 to +0.097 |
| 0.75 | 441 | 7.3 | 61.5% | 59.7% | +0.022 | +0.030 | +0.004 | -0.053 to +0.102 |

Read the last column. **Every confidence interval contains zero.** Train and test
agree, the grid is stable, the sign is consistent, and the effect is still not
statistically established on five years of one instrument. It is not refuted either.
That is the honest status: a plausible small edge, not a demonstrated one.

Everything on the long side fails out of sample at rr below 1. `L_bb_break_up`,
`L_uptrend_run3` and `L_volspike18_up` are all negative in test. The low R:R edge such
as it is, is short-only, which is its own problem for a bull-market challenge and for
the psychology of trading it.

For scale, the same machinery at rr >= 1 on the same data:

```
rule                 am    rr    n  t/mo     WR     be    expR   ci_lo   R/mo
L_volspike18_up     1.5  2.00  240   4.1  45.8%  36.1%  +0.287  +0.099  +1.17
S_bb_break_dn       1.0  1.00  478   7.9  58.4%  53.0%  +0.095  +0.009  +0.75
S_dntrend_at_200    1.5  2.00  136   2.3  45.6%  36.1%  +0.273  +0.025  +0.63
```

Those CIs exclude zero. The best low R:R config earns +0.33 R/month; the 2:1 volume
spike earns +1.17 R/month, roughly 3.5x more, from the same five years and the same
instrument.

## 5. Breakout compliance

`lowrr/breakout_sim.py`. Rules used (1-step): +10% target, -4% daily cap, -6% max
drawdown as a STATIC floor at 0.94 x initial, no consistency rule, no minimum days, no
time limit. Method: start a challenge at every trade in the real sequence and run it
forward on real trades until it passes, busts, or the data ends.

The one place low R:R wins outright:

```
config                              risk  P(pass) P(daily) P(maxDD) medDays  unres
LOW  S_bb_break_dn  am1.5 rr0.25   0.50%   100.0%     0.0%     0.0%     889  98.9%
LOW  S_bb_break_dn  am1.5 rr0.25   1.00%    93.8%     0.0%     6.2%     430  77.2%
MID  S_bb_break_dn  am1.0 rr1.00   1.50%    54.9%    10.8%    34.3%      80   6.7%
HIGH L_volspike18_up am1.5 rr2.00  1.00%    86.0%     0.0%    14.0%     139  25.4%
```

**The 4% daily cap is never breached by any low R:R configuration at any risk size
tested up to 1%.** Zero out of hundreds of rolling starts. That is a real structural
fit: small wins, high hit rate, short holds and a static (non-trailing) floor combine
so that the only thing that can kill you is slow bleed into the -6% floor, and you can
see it coming for weeks. That is a genuinely better failure mode than a 2:1 system
that can take three stops in a day.

The problem is the other column. `medDays = 889` and `unres = 98.9%`. At a Breakout-
safe 0.5% risk, the 0.25:1 system passes essentially every challenge it finishes, and
finishes 1.1% of them inside five years. Full-history equity:

```
config                              risk    n    total    CAGR  per-mo   maxDD
LOW  S_bb_break_dn  am1.5 rr0.25   0.50%  641    +9.7%   +1.8%  +0.15%   -3.5%
LOW  S_bb_break_dn  am1.5 rr0.25   1.00%  641   +20.0%   +3.7%  +0.30%   -6.9%
LOW  S_bb_break_dn  am1.5 rr0.50   1.00%  533   +20.5%   +3.8%  +0.31%  -13.6%
MID  S_bb_break_dn  am1.0 rr1.00   1.00%  478   +53.9%   +8.9%  +0.71%  -13.4%
HIGH L_volspike18_up am1.5 rr2.00  1.00%  240   +93.8%  +14.4%  +1.13%   -9.7%
```

0.15% per month means the 10% target takes about 5 years. At 1% risk it takes 2.8
years and the historical drawdown is -6.9%, which busts the -6% floor. There is no
risk size at which this passes in a reasonable time on one instrument.

Note also that rr=0.25 has a much shallower drawdown than rr=0.50 (-6.9% vs -13.6% at
the same risk). High winrate does control drawdown. It just does not produce return.

Caveat stated rather than hidden: equity steps at trade EXIT, so intraday unrealised
excursion is not charged against the daily cap. With one position open the unrealised
excursion is bounded by about one risk unit, so real daily-cap breaches are slightly
more likely than modelled. With four concurrent positions the understatement is larger.

## 6. Frequency: the only lever left

See section 7. A 4H chart produces what it produces. `S_bb_break_dn` fires 10.6 times
a month on BTC and that is the ceiling for one instrument at that timeframe. The only
honest way to raise frequency without dropping to a lower timeframe (where the earlier
study already showed fee drag kills everything) is to run the same rule on more
instruments. Breakout lists 100+ perps, so this is available.

It is also the strongest falsification test available: the rules were selected by
scanning BTC, so their BTC numbers are contaminated by construction. Eleven other
perps were never scanned.

## 7. Multi-asset results

### 7a. Pre-registration (written before running the test)

`S_bb_break_dn` was selected by scanning BTC, so its BTC numbers are contaminated.
The eleven other perps are a clean test. Committing to the reading in advance so the
result cannot be reinterpreted afterwards:

- **Real**: at least 8 of 11 non-BTC perps show positive net expectancy at rr = 0.25
  and at rr = 0.5, with a pooled winrate lift in the +4 to +6 point range over each
  asset's own unconditional baseline.
- **Noise**: 5 to 7 of 11 positive. That is what a coin flip looks like, and the rule
  should be treated as dead regardless of how good the BTC numbers are.
- **Ambiguous**: exactly at the boundary, or positive count high but pooled expectancy
  near zero. Report as unresolved, do not promote.

Separately, the long-side mirror `L_bb_break_up` was negative out of sample on BTC. If
it comes back positive across the alts, the short-only asymmetry was a BTC artefact
and the whole family needs re-examining rather than celebrating.

Frequency expectation: about 10 trades per month per asset, so 100+ per month gross
across 12 instruments before any concurrency cap. Whether that survives a cap of 4
concurrent positions is the thing that decides section 5's verdict.

### 7b. Result: the pre-registration was half met, and the reason matters

Counts (non-BTC perps with positive net expectancy, threshold was 8 of 11):

| rr | non-BTC positive | pooled expR | pooled lift | day-clustered 95% CI | P(<=0) |
|----|------------------|-------------|-------------|----------------------|--------|
| 0.25 | 8 / 11 | +0.008 | +3.6 pts | -0.016 to +0.030 | 24.3% |
| 0.50 | 9 / 11 | +0.024 | +4.5 pts | -0.013 to +0.060 | 9.6% |
| 1.00 | 9 / 11 | +0.046 | +4.8 pts | -0.016 to +0.109 | 7.4% |
| 2.00 | 9 / 11 | +0.082 | +4.7 pts | -0.027 to +0.190 | 7.6% |

The count criterion passed comfortably (well clear of the 5-to-7 noise band). The
magnitude criterion did not: at rr 0.25 the lift is +3.6 points, below the
pre-registered +4 to +6 band, and a quarter of bootstrap draws are at or below
zero. By the rule written in advance, rr 0.25 is **unresolved, do not promote**
and rr 0.5 is the closest thing to confirmed, without clearing a 95% bar.

**The decisive number is the lift column.** On BTC alone the lift looked
front-loaded (+5.6 points at 0.25:1 falling to +4.0 at 1:1), which is what made
this the sole low R:R survivor. Across twelve instruments it is **flat**: +3.6,
+4.5, +4.8, +4.7. The front-loading was noise. And since expectancy is exactly
`(1+rr) * lift`, a flat lift means **expectancy is strictly increasing in R:R**.
The one rule that appeared to justify sub-1 R:R does not.

The long mirror confirms the asymmetry is real rather than fitted. `L_bb_break_up`
lift across the ladder: +0.6, +0.7, -0.2, +0.1. Exactly zero. Longing an upper-band
break has no edge at all and simply pays the fees, while shorting a lower-band
break has a genuine +4.5. That is consistent with the leverage effect (downside
moves carry stronger short-horizon follow-through), so it is a mechanism and not
just a pattern.

**Cross-asset correlation is not optional bookkeeping.** The day-clustered CI is
about 3x wider than the naive one, and the stacking work below puts the inflation
factor at 4 to 6x. Twelve correlated perps are nowhere near twelve experiments.
Any pooled figure in crypto quoted with a naive standard error is overstated by
roughly a factor of five.

### 7c. Frequency does multiply, and it does not rescue anything

Concurrency-capped portfolio (max 4 open, 1 per symbol, 0.25% risk per trade):

| rule | rr | trades/mo | R/mo | maxDD | CAGR/maxDD |
|------|----|-----------|------|-------|------------|
| S_bb_break_dn | 0.25 | 82.9 | +1.12 | -9.4% | 0.35 |
| S_bb_break_dn | 0.50 | 61.5 | +1.00 | -9.8% | 0.30 |
| S_bb_break_dn | 1.00 | 40.8 | +0.91 | -12.6% | 0.21 |
| S_bb_break_dn | 2.00 | 25.4 | +1.20 | -20.6% | 0.17 |
| S_volspike18_dn | 0.50 | 45.5 | +1.09 | -8.2% | 0.40 |
| S_volspike18_dn | 1.00 | 36.2 | +1.71 | -10.1% | 0.50 |
| S_volspike18_dn | 2.00 | 23.1 | +2.06 | -12.2% | 0.51 |

Frequency reaches 83 trades a month, which is what the question asked for. But
R/month barely moves, because the position cap binds and the per-trade edge at low
R:R is near zero. For the Bollinger rule, low R:R does win on risk-adjusted terms
(0.35 vs 0.17) purely because trades cycle faster through the four slots. For the
volume-spike rule, high R:R wins on every measure. There is no general answer.

### 7d. Breakout challenge outcomes

Rolling starts on the real portfolio trade sequence, 0.25% risk:

| config | P(pass) | P(daily bust) | P(maxDD bust) | median days | per-month | maxDD |
|--------|---------|---------------|---------------|-------------|-----------|-------|
| S_volspike18_dn rr 0.5 | 89.7% | 0.0% | 10.3% | 379 | +0.27% | -8.2% |
| S_bb_break_dn rr 0.5 | 79.4% | 0.0% | 20.6% | 313 | +0.24% | -9.8% |
| S_volspike18_dn rr 1.0 | 79.1% | 0.0% | 20.9% | 256 | +0.42% | -10.1% |
| S_volspike18_dn rr 2.0 | 71.1% | 0.0% | 28.9% | 232 | +0.50% | -12.2% |

**The 4% daily cap is never breached, by any short-side configuration, at any risk
size tested, at either a 4% or a stricter 3% cap.** That is the one place low R:R
wins outright and it is a genuine structural fit with Breakout's rule set. The
binding constraint is the static -6% floor and, far more, the time to target: a
median of 8 to 12 months.

Read the pass rates honestly. They are computed from a trade series whose
expectancy CI still contains zero. If the true edge is zero the pass rate collapses
toward the bust rate. An 89.7% historical pass rate is not an 89.7% probability.

## 8. Should overlapping signals be stacked?

De-overlapping was applied for MEASUREMENT, and that is justified: overlapping
trades on one instrument resolve unanimously **61% to 89%** of the time, and the
naive standard error overstates the evidence by **4.2x to 6.3x** versus a
day-clustered one. Five entries on consecutive bars are not five trades' worth of
proof.

It was never justified as a TRADING choice, and testing it (`lowrr/stacking.py`)
shows the collapse was too conservative:

- the marginal stacked entry pays. At 1:1 on `S_bb_break_dn`, depth 0 earns +0.055
  R and depth 1 earns +0.066 R. Degradation starts at depth 3 (-0.059) and depth 4
  (-0.090).
- at FIXED TOTAL risk, which is the honest comparison since a 3-deep stack is one
  3R bet with staggered entries, stacking 2-deep at 1:1 improves return per unit
  drawdown from 0.39 to 0.51. Beyond 2-deep it stops helping.
- at 2:1 stacking hurts (0.21 down to 0.13).

Verdict: stack at most 2 deep, size the stack as one position, and only at rr <= 1.

## 9. Exit management: a clean negative, and one live warning

52 variants (`lowrr/exits.py`): break-even moves, ATR trailing, partial take-profits,
time stops, on both surviving rules across 12 perps, with an extra commission and
slippage charged for every additional fill so nothing gets a free exit.

**Zero variants beat plain fixed-R by more than noise.** Trailing stops and long
time stops had the best point estimates and agreed in sign across train and test,
but every CI includes zero, and the two closest sit at P(<=0) of 2.5 to 3% out of
52 draws, which is the multiple-comparisons floor rather than evidence.

One result is robust in the other direction and is actionable today:
**moving to break-even at +0.25R costs about -0.07 R per trade**, -0.072
[-0.096, -0.050] and -0.071 [-0.098, -0.043], CI entirely negative on both rules.
On high-winrate short signals an early break-even converts eventual winners into
scratches. Enter-and-forget stands.

## 10. Oscillator divergence stacks

`lowrr/oscillators.py` + `lowrr/osc_test.py`. See the scope warning in those files:
the port is NOT validated against TradingView, only Variant A is implemented, and
this is not the Gate 0 audit. It cannot kill anything.

**0 of 280 cells survive** train, test and a day-clustered CI. Not one, at any
timeframe, R:R, stop rule or level filter.

Two things are worth keeping anyway:

- **On 4H the stacks are genuinely front-loaded.** WT+MFI margin over breakeven runs
  +2.2, +1.9, +2.7 points at rr 0.25, 0.5, 0.75 and then turns NEGATIVE at 1:1
  (-2.2) and 2:1 (-3.1). That is the opposite of every trend-continuation rule here,
  and front-loaded is precisely the signal shape a sub-1 R:R target suits. The
  intuition that low R:R fits a divergence system is structurally correct. The
  margin simply never separates from zero, and frequency is only 4.3 trades/month
  with primary filters.
- **On 15m the cost model is decisive.** A 1.5 x ATR stop on 15m puts the breakeven
  winrate at **91.1%** at 0.25:1, because the stop is tight enough that commission
  plus slippage eats 15% of R. Every 15m cell returns -0.09 to -0.26 R with CIs
  entirely below zero. The spec's wider ATR-band stop plus its 0.6% invalidation
  cuts breakeven to 86.9%, which helps and is nowhere near enough.

## 11. Session, cross-sectional and ensemble

470 hypotheses (`lowrr/crosssec.py`). All three negative.

- **Session/time of day**: one borderline cell (hour 12 UTC on the Bollinger short,
  CI lower bound +0.000) with train-to-test decay from +0.096 to +0.015. Noise.
- **Cross-sectional relative strength**: all 60 cells negative at every rung. Best
  is -0.020 with CI [-0.031, -0.008], which excludes zero on the LOSING side. Beta
  neutrality was achieved (correlation to BTC daily return between -0.055 and
  +0.121) but there is no edge to be neutral about, and a flat-to-negative
  market-neutral book is the worst thing to hold under a static floor: it bleeds
  with no upside to recover through. The leg breakdown shows why it fails, and it
  is the study's recurring finding: short leg roughly flat (+0.006 to -0.019), long
  leg a consistent drag (-0.043 to -0.059).
- **Ensemble scoring**: only full 9-of-9 consensus is positive in both train and
  test, CI [-0.007, +0.145], smallest-n and most cherry-picked cell of a 9-point
  sweep.

## 12. Funding rate: the first non-OHLCV information, and it fails too

175 hypotheses (`lowrr/funding.py`), 12 symbols. Causality was verified three ways:
zero rows where the funding timestamp exceeds the bar close, hand-printed rows
across a settlement boundary, and a deliberately broken forward-merge control
showing the 50%-leak signature the real merge does not have.

**0 of 175 cells are positive in train, positive in test, and CI-excluding-zero.**

The stronger finding is the sign. **35 of 175 cells have a CI entirely BELOW zero,
and 0 have a CI entirely above.** The textbook trade of fading crowded positioning
via funding is not merely unprofitable at Breakout costs, it is reliably
money-losing, up to -0.21 R per trade. And every one of the significantly negative
cells is a LONG-side signal (`div_bull`, `flip_to_neg`, `fund_bot_pct365d`,
`cum*_top_decile`). The cross-sectional funding book is negative at every rung
(-0.036, CI [-0.045, -0.027]) with a BTC correlation of -0.205.

## 13. The ceiling, and what it means

Across roughly 1,900 hypotheses in this study, spanning price, volume, momentum,
volatility, candle structure, higher-timeframe levels, oscillator divergences,
session effects, cross-sectional ranking, ensembles, exit management and funding
positioning, on 12 instruments over five years:

**No condition has ever produced a winrate lift above about +6 points over its own
barrier baseline.** The cost hurdle is +3 points. Everything real operates at one
to two times the hurdle, which is why every result comes out thin regardless of
which indicator generates it.

That consistency does not look like "the right indicator has not been found yet".
It looks like a ceiling on how much an OHLCV bar, and now also funding positioning,
knows about a liquid perp on a high timeframe. The 1,901st price-derived condition
will very likely land in the same band.

Against that, the two rules still standing are the volume-spike short at 1:1
(+0.074 R, CI [+0.005, +0.141], the only cell in the entire study whose
day-clustered CI excludes zero) and, more weakly, the Bollinger-break short.

## 14. Direct answer to the question

Can we build a sub-1 R:R, high-winrate, high-timeframe, high-frequency,
Breakout-compliant system?

- **Sub-1 R:R and high winrate: trivially yes, and worth nothing.** 4H BTC hands you
  80.4% at 0.25:1 and 66.9% at 0.5:1 with no signal at all, and all twelve perps sit
  within a few tenths of a point of the fair line at every rung. It is arithmetic.
- **High frequency: yes, via instruments, not via timeframe.** 83 trades a month
  across 12 perps at 0.25:1.
- **Breakout-compliant: yes on the daily cap, which is never breached.** The static
  -6% floor and a median 8-to-12-month time to target are the real constraints.
- **Positive expectancy at sub-1 R:R: not demonstrated.** The one candidate that
  looked front-loaded on BTC turned out flat across 12 instruments, which makes
  expectancy strictly increasing in R:R for it.

The honest recommendation is to stop trying to buy winrate with R:R. It is not a
lever, it is a change of units. The levers that showed anything here are instrument
count (frequency), the short side only (the long side is a reliable drag
everywhere), stacking at most 2 deep at fixed total risk, and NOT touching the exit.

## 8. Data and methods

- BTC 4H/5m: existing TradingView exports of Binance BTCUSDT.P in `study/data/`.
- Multi-asset 4h/15m: `data.binance.vision` monthly archives, Binance USDT-M perps,
  fetched by `lowrr/fetch_binance.py`.
- `lowrr/check_data.py` verifies the two BTC feeds agree (max relative difference
  under 1 bp on all but 2 of 11,987 overlapping 4H bars) and quantifies the
  5m-vs-15m path resolution bias (+0.002 to +0.004 R at rr below 1, i.e. the coarser
  15m path used for alts flatters results by about that much).
- Signals read at bar close, entry at next bar open, resolved on the fine path. No
  look-ahead anywhere.
- Train pre-2025, test 2025 onward, same split as the earlier study.

## 9. Reproduce

```
python3 lowrr/fetch_binance.py 4h,15m   # 12 perps, OHLCV
python3 lowrr/fetch_flow.py funding     # funding rate, 12 perps
python3 lowrr/fetch_flow.py metrics     # open interest + positioning, BTC/ETH/SOL

python3 -m lowrr.barrier          # unconditional barrier ladder, writes barrier_*.parquet
python3 -m lowrr.scan             # 492-condition slice, writes scan_results.csv
python3 -m lowrr.finalists_lowrr  # de-overlapped finalists + block bootstrap
python3 -m lowrr.edge_scaling     # lift vs rr decomposition
python3 -m lowrr.multiasset       # 12-perp portfolio
python3 -m lowrr.pooled_test      # per-asset baselines + day-clustered CIs
python3 -m lowrr.breakout_sim     # Breakout 1-step rolling-start challenge sim
python3 -m lowrr.stacking         # overlapping-entry analysis
python3 -m lowrr.exits            # exit-management overlays
python3 -m lowrr.osc_test         # WT/MFI/RSI divergence stacks
python3 -m lowrr.crosssec         # session, cross-sectional, ensemble
python3 -m lowrr.funding          # funding-rate conditions
python3 -m lowrr.openinterest     # open interest and positioning
python3 -m lowrr.check_data       # feed agreement + path resolution bias
```

## 10. Hypothesis budget

Stated so results are read against it rather than in isolation.

| source | hypotheses |
|--------|-----------|
| scan.py condition sweep | 492 |
| finalists grid (9 rules x 3 stops x 7 rr) | 189 |
| multiasset per-asset and pooled cells | ~260 |
| pooled_test + stacking | ~50 |
| exits.py | 52 |
| osc_test.py | 280 |
| crosssec.py | 470 |
| funding.py | 175 |
| **total** | **~1,970** |

At a nominal 5% level that budget buys roughly 99 false positives for free. Exactly
one cell in the whole study has a day-clustered CI excluding zero on the positive
side: the volume-spike short at 1:1.

## 15. Open interest: the one result that survives

Added after the sections above. This is the only finding in the study that clears
every check applied to it, and it argues against the premise of the question.

**The claim.** The edge in both surviving short rules lives almost entirely in
periods when open interest is in the top decile of its trailing 90-day range.
Filtering on that roughly triples net expectancy per trade.

Pooled over BTC, ETH and SOL, day-clustered CI on the DIFFERENCE (filtered minus
unfiltered), which is the quantity that has to exclude zero:

| rr | base expR | OI-filtered expR | delta | 95% CI on delta |
|----|-----------|------------------|-------|-----------------|
| 0.25 | +0.015 | +0.056 | +0.041 | -0.005 to +0.083 |
| 0.50 | +0.013 | +0.084 | +0.071 | -0.007 to +0.141 |
| 0.75 | +0.023 | +0.146 | +0.124 | **+0.018 to +0.231** |
| 1.00 | +0.040 | +0.215 | +0.175 | **+0.040 to +0.308** |
| 2.00 | +0.086 | +0.331 | +0.245 | **+0.018 to +0.476** |

**Why it is not the usual false positive.**

- *Independently replicated.* `lowrr/oi_verify.py` reimplements the merge, the
  rolling percentiles and the conditions from scratch rather than reusing the
  original script, and reproduces the effect.
- *Out of sample on instruments.* The conditions were searched on BTC. ETH and SOL
  were not searched. 69 of 81 BTC-positive cells stay positive on ETH (median
  expR +0.086 to +0.082, essentially unchanged) and 50 of 71 on SOL. The
  cross-instrument correlation of cell expectancy is +0.79 for ETH and +0.74 for
  SOL. Every previous candidate in this study flattened when instruments were
  added. This one holds its shape.
- *It separates rather than selects.* The complement matters more than the filter:
  when OI is NOT elevated, the base rules earn a median +0.006 R and are negative
  at 0.75:1 and 1:1. Essentially all of the edge in the Bollinger-break and
  volume-spike shorts is conditional on elevated open interest.
- *Not a volatility proxy.* Correlation of the OI percentile with the ATR
  percentile is -0.275, -0.157 and +0.024 across the three instruments, with only
  6 to 16% overlap between the two top deciles. A selectivity-matched ATR filter,
  keeping the same share of bars, beats the base rule in only 2 of 15 cells
  (median -0.056) while the OI filter wins 15 of 15 (median +0.130). The OI edge
  survives inside both volatility halves: +0.153 in high vol (15/15 positive) and
  +0.060 in low vol (12/15).

**Mechanism, which is at least coherent.** Shorting a breakdown or a volume spike
pays when there is a crowded long position to liquidate, and does not pay when
there is not. That is a liquidation-cascade trade, and open interest is the direct
measure of how much fuel is present. It is not a price pattern, which is why it
was invisible to roughly 1,900 OHLCV-derived hypotheses.

**What it does NOT support.** The delta rises monotonically with R:R (+0.041,
+0.071, +0.124, +0.175, +0.245) and the CI only excludes zero at 0.75:1 and above.
This is a drift edge that needs distance, exactly like the volume-spike family.
The single genuine discovery in this study points at 1:1 or 2:1, not below 1.

**Honest limits.**

- Three instruments, not twelve. The rest of the study used twelve, and twelve is
  what has been killing false positives.
- The CHOICE of this filter came from searching 360 cells on BTC, so filter
  selection is contaminated even though the instrument replication is not.
- Pooled filtered sample is 289 to 612 trades depending on rung.
- ETH and SOL metrics only start 2021-12; BTC starts 2021-01.
- Live feasibility is untested. This needs a real-time open-interest feed, Binance
  OI is not Breakout's book, and the 5-minute metrics series has a publication lag
  that this backtest does not model. Treat as a research finding, not a system.

**Next step, not taken here.** Fetch the metrics series for the other nine perps
and re-run. That is the same twelve-instrument bar every other candidate had to
clear, and until it is cleared this stays provisional.
