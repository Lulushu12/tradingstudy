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

TO BE FILLED

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
python3 -m lowrr.barrier          # unconditional barrier ladder, writes barrier_*.parquet
python3 -m lowrr.scan             # 492-condition slice, writes scan_results.csv
python3 -m lowrr.finalists_lowrr  # de-overlapped finalists + block bootstrap
python3 -m lowrr.edge_scaling     # lift vs rr decomposition
python3 -m lowrr.breakout_sim     # Breakout 1-step rolling-start challenge sim
python3 lowrr/fetch_binance.py 4h,15m
python3 -m lowrr.multiasset       # 12-perp portfolio
python3 -m lowrr.check_data       # feed agreement + path resolution bias
```
