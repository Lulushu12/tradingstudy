# BTC Strategy Study — Findings

Data: BINANCE BTCUSDT.P, 2021-01 → 2026-06. All indicators recomputed causally from
raw OHLCV (no repainting, no look-ahead). Signals read on bar close, entry next bar
open. Fees 0.08% round-trip. Train = pre-2025, Test = 2025-01 onward. Finalist win/loss
resolved on the true 15-minute price path, not an intrabar heuristic.

## Verdict on your two targets

| Target | Achievable? | Best robust result found |
|--------|-------------|--------------------------|
| 60% winrate @ 1:1 | **No** (not out-of-sample) | ~56% @ 1:1 (test 53%) |
| 50% winrate @ 2:1 | **No** | ~42% @ 2:1 (test 40%) |
| 10%/month & max DD ≤6% | **No** | ~1.8%/month @ 12% max DD, or ~1%/month if sized to a 6% DD cap |

Why: at 1:1 with realistic fees the net breakeven winrate is 51–56% depending on
timeframe, and BTC's *unconditional* 1R-before-stop rate is ~50%. No causal condition
tested clears 60% on unseen data. Separately, 10%/month compounding = ~214%/year; pairing
that with a 6% max drawdown implies a Calmar ratio near 35, which effectively does not
exist for a single liquid asset. The return target and the drawdown cap are mutually
incompatible, independent of the winrate.

## The genuine edge that DOES exist

**4H volume-spike trend-continuation.**

- Trend filter: close vs EMA200 on the 4H chart.
- Trigger: a bar whose volume > 1.8× its 20-bar average, closing in the trend direction
  (up bar in an uptrend → long; down bar in a downtrend → short).
- Stop: 1.5 × ATR(14). Target: 2 × stop (2:1). Entry: next 4H bar open.
- One position at a time (skip new signals while a trade is open).

Performance (2021–2026, 15m-path-resolved, 1% risk/trade, single position):

- Winrate 41.7% @ 2:1, expectancy **+0.21R net per trade**.
- Train 42.2% / Test 40.4% → stable out-of-sample.
- CAGR +21.6%, max drawdown -12.3%, ~8 trades/month, 67% of months positive,
  worst losing streak 9.
- Positive expectancy in every year 2021–2026 and in both trend regimes.

This is a real, multi-year, positive-expectancy strategy. It is *profitable and robust* —
it simply does not reach the specific winrate numbers or the 10%/6% return/DD combo.

## Sizing it to your risk rules

Drawdown scales ~linearly with risk-per-trade. To respect a 6% hard max-DD cap given the
observed 9-trade losing streak at 2:1, cap risk near **0.5–0.6% per trade**. Expected
outcome: roughly **1%/month** with max DD held around 6%. Accepting a ~12% DD budget
instead lets you run 1% risk for ~1.8%/month.

## What was tested and rejected

Timeframes 15m/1h/4H/1D; setups: trend pullback, RSI divergence, WaveTrend cross,
Bollinger reversion, liquidity-sweep reclaim, Donchian breakout, MACD momentum,
candle patterns (engulfing/hammer/shooting-star/marubozu), volume spikes, BB squeeze.
On 15m and 1h the fee drag (breakeven WR 54–56% @ 1:1) kills most edges. 4H is the sweet
spot because wide ATR stops make fees negligible (breakeven ~51.5%). Lower timeframes did
not yield a robust edge net of costs.

## Follow-up: confluence, HTF levels, and multi-candle patterns (confluence.py)

Tested three families that the first pass under-covered. On 1h the fee drag still
kills almost everything; results below are 4H (net breakeven WR: 51.5% @1:1, 34.3% @2:1).

**A) Richer lowTF+highTF confluence (1D + 4H trend + HTF momentum + LTF trigger).**
Did NOT help. Stacking 1D+4H+RSI+candle-trigger shrank samples and most conditions fell
*below* breakeven out-of-sample. The thin single EMA200 trend filter from the first pass
was about as good — extra confluence layers added constraints without adding edge.

**B) HTF significant levels + LTF entry.** The most promising *new* leads, all on the
short side into resistance during a higher-TF downtrend:
- Short at a held **4H swing resistance** in a 4H downtrend: 61% train / 64% test @1:1
  (also 44%/55% @2:1). Clears breakeven both sides — but only ~104 trades in 5.5 yr.
- Short at a held **prior-week high**: 52% train / 68% test @1:1 (38%/55% @2:1), n~370.
- Short at **prior-day high**: large sample (~1150) but sits right on breakeven — no edge.
- Long at support levels: consistently weaker / fails out-of-sample.
These reach or beat 60% @1:1, but at ~1.5-3 trades/month the frequency is far too low to
compound toward the return goal, and the high-winrate variants are small-sample (SE ~5%,
so a measured 62% could truly be low-50s). Promising but not bankable alone.

**C) Multi-candle chart patterns.**
- **Double top -> short**: a real modest edge (57%/54% @1:1; 35%/39% @2:1), consistent
  with the trend-continuation family.
- **Double bottom -> long**: works in-sample, decays out-of-sample.
- **Head & Shoulders / inverse H&S**: NO robust edge — at or below breakeven out-of-sample.

Net: the level-rejection shorts and double-tops confirm the same underlying edge
(trend-continuation / rejection into resistance) already captured by the 4H volume-spike
strategy, and the only signals that *touch* 60%/1:1 do so at unusably low frequency. None
change the headline verdict.

## Follow-up: divergence restricted to the swing-extreme candle (sfp_divergence.py)

Hypothesis tested: the baseline RSI divergence fires at pivot *confirmation* — 3 bars
after the swing extreme — so part of the reversal is already spent by entry. Restrict
the divergence to be valid only when the **signal candle IS the extreme candle** (it
sweeps the prior pivot high/low with weaker RSI and closes back through it = swing
failure pattern, "offset 0") **or is the candle right after** the extreme ("offset 1").
Reference swing = last confirmed fractal pivot (causal, same left/right=3 machinery).

**The hypothesis is confirmed on 4H.** Catching the divergence at the extreme instead
of 3 bars late improves winrate across the board (4H, atr_mult=1.2, train/test):

- Bearish @1:1: baseline 51.5%/51.6% (≈breakeven 51.9%) → SFP-timed 57.1%/53.0% (n=310/83).
- Bullish @1:1: baseline 52.7%/43.5% (fails OOS) → SFP-timed 53.7%/56.3% (n=229/103).
- Offset 0 and offset 1 perform about equally; the union is fine. On the bull side the
  candle-after variant is slightly more reliable than the extreme candle itself.

**Standout: SFP-timed bearish divergence WITH the trend (short, close<EMA200 on 4H)** —
i.e. a failed sweep of a prior swing high inside a downtrend (a lower-high rejection):

- @1:1 (1.5×ATR stop, sim): 64.1% train / 64.0% test (breakeven 51.5%), expR ~+0.24 both.
- @2:1: 45.7%/56.0% (breakeven 34.3%), expR +0.33 train / +0.64 test.
- Survives dedup to first-signal-per-swing (63%/71% @1:1, expR +0.31/+0.67 @2:1).
- BUT: n=117 raw (~1.8/month), n=63 deduped (~1/month). Small sample (test SE ~9%),
  same caveat as the level-rejection shorts in the confluence pass — the true rate
  could be mid-50s. It is the only divergence variant in the whole study that clears
  60% @1:1 out-of-sample.

The classic *counter-trend* use (shorting bearish divergence in an uptrend, longing
bullish divergence in a downtrend) is negative even with SFP timing — the edge is the
trend-continuation rejection, consistent with everything else in this study.

On 1h the fee drag still kills it (SFP bear+dn: 64.3% train but 53.9% test vs 54.6%
breakeven @1:1) — no robust 1h edge, matching the earlier passes.

Net: the timing restriction genuinely rescues divergence from "rejected" to "modest
real edge" on 4H, and the with-trend short variant is the best @1:1 signal found so
far — but at ~1-2 trades/month it complements, rather than replaces, the volume-spike
strategy (which delivers ~8/month at expR +0.21).

### Lower timeframes: 1h / 30m / 15m / 5m — the SFP timing does NOT survive below 4H

Same variants, trade-sim evaluated (1.5×ATR stop, rr=1 and rr=2, entry next bar open;
30m synthesized by resampling the 15m data since there is no native 30m export).
The fee arithmetic is the whole story — as the timeframe drops, the ATR stop shrinks
as a fraction of price and the 0.08% round-trip fee eats a growing share of every R:

| TF  | stop ~% of price | fee in R | breakeven WR @1:1 | @2:1 |
|-----|-----------------|----------|-------------------|------|
| 4H  | ~2.3%           | ~0.04R   | 51.5%             | 34.3% |
| 1h  | ~1.10%          | ~0.07R   | 53.6%             | 35.8% |
| 30m | ~0.89%          | ~0.09R   | 54.5%             | 36.3% |
| 15m | ~0.62%          | ~0.13R   | 56.5%             | 37.6% |
| 5m  | ~0.32%          | ~0.25R   | 62.6%             | 41.7% |

- **1h — fails out-of-sample.** The 4H star (SFP bear + downtrend) looks great in
  train (69.0% @1:1, expR +0.30) and dies in test (52.0% vs 53.6% breakeven, -0.05R;
  @2:1 +0.20 train → -0.06 test). The only both-positive cell is baseline
  bull-div + uptrend (n=29/43 — too small to mean anything).
- **30m — breakeven at best.** SFP bear + downtrend @2:1: +0.015R train / +0.186R
  test; baseline bear + downtrend: +0.119/+0.004. Train and test never agree on
  anything being solidly positive; @1:1 everything is negative.
- **15m — uniformly negative.** Every variant, both sides, both rr, train and test
  (expR -0.05 to -0.35). Widening the stop to 3×ATR to dilute fees does not help.
- **5m — hopeless.** Fees are 0.25R per trade; every variant loses -0.32 to -0.48R
  @2:1. With 3×ATR stops still -0.11 to -0.32R. The with-trend SFP short remains the
  *least bad* variant on every TF (the pattern is real), but the edge is ~5-8 WR
  points over unconditional and the fee hurdle grows faster than that as TF drops.

Conclusion: the swing-failure timing is a genuine ~4-6pp winrate improvement over
late-confirmed divergence at every timeframe, but below 4H that improvement is
smaller than the fee hurdle. The signal's home is 4H (and the ordering matches the
study's standing result: no lower-TF edge survives costs). 1m was skipped — only ~3
months of data, and 5m already settles the direction of travel.

### Exit engineering on the SFP entries (sfp_exits.py)

Tested on the same entries: higher fixed targets (2R-6R), the earlier hybrid
(half@2R + half on a 3-ATR chandelier trail), and the partial-TP family — 50% off
at +1R with stop to entry, then either (a) 50% of the remainder at every further R
multiple, (b) 50% of the remainder at each significant level (confirmed pivots known
at entry), or (c) the whole remainder riding the 3-ATR trail. Stops ratchet behind
each filled rung. 4H star entries (SFP bear + downtrend, n=92 train / 25 test):

| Exit                        | train expR | test expR | WR tr/te | median R | shape |
|-----------------------------|-----------|-----------|----------|----------|-------|
| fixed 2R                    | +0.33 | +0.64 | 46%/56%  | -1.0 | baseline |
| **fixed 3R**                | +0.49 | +0.88 | 38%/48%  | -1.0 | best pure target |
| fixed 4R                    | +0.43 | +0.36 | 29%/28%  | -1.0 | decaying |
| fixed 5R / 6R               | +0.6/+0.8 | +0.16/+0.36 | ~20% te | -1.0 | tail overfit |
| hybrid half@2R + 3ATR trail | +0.40 | +1.36 | 44%/56%  | -0.3 | biggest tail |
| **half@1R->BE + 3ATR trail**| +0.36 | +0.98 | **64%/64%** | **+0.47** | high WR + runners |
| ladder R-multiples          | +0.28 | +0.43 | 64%/64%  | +0.47 | smooth, capped |
| ladder pivot levels         | +0.26 | +0.32 | 64%/64%  | +0.71 | smooth, capped |

Findings:

- **The 1R partial + breakeven move is the valuable half of the idea.** It lifts
  winrate from ~46% to 64% (71% on deduped entries) and turns the median trade
  positive — the SFP entry almost always gets >=1R of follow-through, and the BE
  stop converts many would-be -1R losers into scratches.
- **Halving at every subsequent rung is the costly half.** Geometric scale-out caps
  a full winner near 2R (sum k/2^k = 2), so both ladders give back expectancy
  (+0.28/+0.43 vs +0.49/+0.88 for plain 3R). Pivot-level rungs sit even closer than
  R-multiples and cap harder. Smoothest equity of everything tested, but the
  weakest per-trade edge of the positive schemes.
- **Best combination: take 50% at 1R, stop to entry, and trail the ENTIRE remainder
  (3-ATR chandelier) instead of laddering it out.** Keeps the 64% WR and the +0.5R
  median AND keeps the +5R to +7R runners: +0.36R train / +0.98R test (deduped:
  +0.35/+1.43). Per-trade edge on par with fixed 3R, with a far friendlier
  distribution (most trades small wins instead of 60% -1R losers).
- **Fixed 3R is the best simple target** (+0.49/+0.88). Beyond 3R the train edge
  keeps "improving" while test collapses — the extra R is in-sample tail fitting.
  The long side (SFP bull + uptrend) peaks at 3-4R too (+0.61/+0.66, +0.66/+1.09).
- **No exit scheme rescues the lower timeframes.** 1h: every scheme positive in
  train, negative in test (half@1R: +0.20/-0.12). 30m: train and test never agree
  on a positive sign (best: +0.015/+0.19 fixed 2R). 15m: all schemes negative in
  both halves. The exit changes the shape of the distribution, not the sign of the
  edge minus fees.

Caveat as before: the star test set is 25 trades (14 deduped) — the trail/test
expectancies above carry ~0.2-0.4R standard errors and the hybrid's +1.36 is
driven by a handful of +6R runners. The robust statements are the WR jump from the
1R/BE step (consistent train==test) and the 3R-over-2R improvement (both halves).

### Year-by-year walk-forward of the 4H star (sfp_walkforward.py)

Fixed rules, zero fitting, evaluated per calendar year 2021-2026 (2026 = half year):

- **half@1R->BE + 3-ATR trail: positive in ALL SIX years**, raw (+0.49R avg, worst
  year 2024 at +0.20) and deduped (+0.59R avg, worst year +0.04). WR by year stays
  in the 56-78% band, never below the 51.5% 1:1 breakeven.
- **Fixed 1R: also 6/6 positive years** (+0.24R avg) — the winrate floor of the
  signal is real, not a train/test artifact.
- **Fixed 2R and 3R: 5/6** — both lose only 2024 (-0.28R / -0.53R), the chop year.
  Full-distance targets die in chop; the 1R-partial + breakeven schemes survived
  2024 because most trades banked the partial before the reversal.
- **The bull mirror (SFP bull + uptrend, trail exit) is also 6/6 positive**
  (+0.50R avg, n=82) — weaker per the train/test split but consistent per year.
  Both sides together = ~200 trades, ~3/month.

This is the same per-year consistency profile that qualified the volume-spike
strategy as "real". The star + partial-TP exit is now validated by: train/test
split, dedup, exit-scheme robustness, and year-by-year walk-forward. Remaining
weaknesses: single asset, single venue fee model, and ~1-2 trades/month.

### Five-part validation & extension sweep (xrp_validation / sfp_intrabar / portfolio / maker_entry / unify)

**1) Cross-asset (XRP): the edge does NOT transfer.** Identical star rules on
XRPUSDT.P 4H (resampled from the 15m exports, fees identical, feeR tiny at 0.02):
train expectancy negative on every exit (-0.11 to -0.26R), 3-4/7 positive years,
and the strong 2025-26 test numbers mirror BTC's — regime, not signal. The
unified sweep family (below) also fails on XRP (both sides negative, 2/7 and 2/6
positive years). Conclusion: this is a BTC-specific edge (or at least not a
universal one) — deploy only where validated.

**2) True 15m-path resolution: PASSED.** Every star trade replayed on the 15m
path (fixed 1R/2R/3R and the partial+trail with causally-ratcheted 4H trail):
results match the 4H nearest-open sims to the third decimal (trail +0.355/+0.976
train/test, identical WR). With a 1.5*ATR stop, same-bar collisions are too rare
to matter. The exit numbers are not an intrabar artifact.

**3) Portfolio (volspike 2R + star short trail + bull mirror trail).** Monthly
net-R correlations: volspike-star 0.20, volspike-bull 0.19, star-bull -0.03 —
genuine diversification (only 14% of months have volspike and star both
negative, despite 56% of star entries opening during a live volspike trade).
Combined book: 1057 trades, expR +0.264, positive EVERY year 2021-2026.
Sizing (concurrent, all signals): 1% risk -> CAGR +63%, maxDD -21.6%; 0.5% ->
+28.5%, -11.3%; single-position 0.5% -> +14.3%, -8.2%. To respect the 6% DD cap:
~0.25-0.3% risk concurrent, giving roughly 1.1-1.3%/month — the diversification
roughly doubles the return available at the same DD budget vs volspike alone.

**4) Maker entries: marginal on 4H, interesting on 1h.** Limit at the signal
close fills ~100% (next bar opens there) and saves only ~0.01R on 4H — fees were
already negligible there. A 0.2R-retracement limit fills 56%, improves per-trade
train expectancy (+0.50R @2R) but skips the best immediate-dump winners; total R
favors taking every signal at market. On 1h the retracement limit @2R is the
first both-halves-positive 1h cell with real sample (+0.35/+0.09, n=51/99) — but
the trail exit on the same entries disagrees (-0.12 test), so: candidate bin.

**5) Unification: the sweep is the edge; divergence is a booster.** Decomposing
"failed sweep of the last confirmed 4H swing high, downtrend" into with-div
(=star) and without-div parts:

| variant (short) | n | 2R tr/te | trail tr/te |
|---|---|---|---|
| SWEEP (all)   | 485 | +0.28/+0.31 | +0.18/+0.47 |
| STAR (w/ div) | 117 | +0.33/+0.64 | +0.36/+0.98 |
| NODIV         | 368 | +0.26/+0.23 | +0.12/+0.36 |

The no-divergence rejections are positive in both halves on every exit — the
base edge is the failed sweep itself. RSI divergence adds a real increment
(~+0.1-0.3R when present) but is not load-bearing. The long mirror behaves the
same (SWEEP long n=468, trail +0.26/+0.25). Walk-forward: SWEEP short 6/6
positive years, SWEEP long 5/6 (2022 flat). Both sides together: ~950 trades,
**~14.5/month** — the frequency problem of the star is solved by trading the
whole family and treating divergence as a sizing/quality tier rather than a
requirement. (XRP caveat from part 1 applies: BTC-only.)

### Sweep-family portfolio + ETH validation (portfolio.py / eth_validation.py)

**ETH (ETHUSDT.P 4H, 2021-01..2026-07, Binance archive data): weakly positive —
between BTC and XRP.** Sweep short trail: +0.02R train / +0.18R test, 5/6 positive
years (only 2024 negative, the same chop year that dented BTC); sweep long:
+0.08/+0.11, 4/6 years. Roughly a third of BTC's per-trade edge, same direction.
The divergence booster does NOT help on ETH (star short trail -0.01/-0.09).
Asset ladder: BTC strong, ETH weak-positive, XRP negative — consistent with a
liquidity/structure-dependent microstructure edge, not pure curve-fit (a fit
artifact would not order itself by asset liquidity). Deployment stays BTC-only;
ETH is a no at current fees.

**Portfolio with the unified sweep streams (BTC: volspike 2R + sweep short trail +
sweep long trail).** Correlations: A-B 0.27, A-C 0.29, B-C -0.18; only 11% of
months have all three streams negative. Combined: 1811 trades (~28/month),
expR +0.238, positive every year (sumR +58 to +98 per year). Sizing:

- concurrent 0.5% risk: CAGR +47%, maxDD -19.2%, mo_mean +3.4%;
- concurrent ~0.15% risk fits the 6% DD cap -> roughly 1.0-1.1%/month;
- single-position 0.5%: CAGR +9.4%, maxDD -7.7% (the conservative floor —
  concurrent assumes every overlapping signal can be sized independently).

Same headline as ever: the 6% DD cap prices returns at ~1%/month regardless of
how the edge is packaged; the sweep streams raise trade count and smoothness,
not the DD-capped return ceiling.

### Multi-TF filters on the lower-TF entries (mtf_stack.py)

The lower-TF samples are large (star shorts: 1h=236, 30m=709, 15m=1395), so we
tried buying back edge with harder filters: 4H bias (trend on the last closed 4H
bar; active 4H SFP divergence within 6 closed 4H bars) and a divergence stack from
the timeframe below (15m->1h, 15m->30m, 5m->15m), all merged as-of by bar close.
Exits: fixed 1R, fixed 2R, half@1R->BE+trail. Result: **no rescue.**

- **The 4H trend gate HURTS.** Everywhere, replacing or adding the 4H trend to the
  local trend made both halves worse (1h star&4H-dn: -0.12R test @1R vs -0.05
  unfiltered). The local-TF EMA200 was already the informative conditioning; the
  4H bias adds correlation, not information.
- **The 4H-divergence gate shrinks samples to anecdotes.** 4H divergences are rare,
  so requiring one leaves n=12/19/46 trades on 1h/30m/15m — the shiny cells in
  those rows (e.g. 80% WR on 10 test trades) are unusable noise, and on 15m the
  same gate is strongly negative.
- **The lower-TF divergence stack fails out-of-sample.** On 1h it is the classic
  overfit signature: train improves (+0.51R @2R), test worsens (-0.26R). On 15m it
  changes nothing. The single both-halves-positive cell in the whole grid is
  30m star + 15m stack @2R (+0.07 train / +0.11 test, n=300/126) — but its test
  edge is within one standard error of zero, the other two exits on the same
  entries don't confirm it, and its per-trade edge is a quarter of the 4H star's.
- **Full stack (everything at once): n=2 (1h), 10 (30m), 23 (15m)** — and the 15m
  version goes 60% WR train -> 0% test. Maximum confluence = maximum overfit.

Verdict: confluence layers repeat the Section-A lesson from the confluence pass —
each added filter shrinks the sample faster than it adds edge. The lower-TF SFP
entries stay dead; the 4H signal stays the tradeable one.

### 4H oscillator-state filters (osc4h_filter.py)

Follow-up idea: gate the lower-TF SFP shorts by 4H momentum STATE instead of the
(failed) 4H EMA200 — WaveTrend cross recency (fresh = leg young; many bars back =
leg exhausting; wt1/wt2 gap closing = reversal imminent), MFI regime (low = money
leaving, 40-60 = chop), and ADX (>=25 trending / <20 chop, with DI direction).
Added causal `mfi()` and Wilder `adx()` to indicators.py. 13 filters x 3 exits
(fixed 1R, 2R, half@1R->BE+trail) x 1h/30m/15m star entries, ~117 cells.

- **The chop-exclusion logic is directionally right.** On 15m the two "chop"
  states are among the worst cells in the whole grid (4H MFI 40-60: -0.19/-0.44R
  train/test; 4H ADX<20: -0.34/-0.46R @1R) — clearly worse than the unfiltered
  reference. The oscillators do carry real information about when the setup is
  WORSE.
- **But the good states still don't clear fees.** On 1h, every filter that looks
  brilliant in train (WT bear @2R: +0.99R; WT fresh: +1.07R; ADX>=25&DI-: +0.37R)
  lands at -0.03 to +0.05R in test — the filters compress toward zero, not above
  it. On 15m nothing reaches positive in both halves.
- **Filters are inconsistent across TFs — the signature of noise.** 4H ADX<20 is
  strongly negative on 15m but the best trail-cell on 30m (+0.15/+0.38); MFI<40 is
  test-positive/train-negative on 30m while MFI<30 is the exact opposite. A real
  regime variable should not flip sign between adjacent timeframes and thresholds.
- **The one defensible cell:** 30m star + 4H WT fresh bearish cross (<=3 closed
  bars) @2R: +0.17R train / +0.36R test, n=63/32, ~1.5 trades/month. Consistent
  with the "young 4H down-leg" story. BUT: with 32 test trades the SE is ~0.23R,
  and across ~117 cells (plus ~60 in the mtf pass) several such cells are expected
  by chance. Filed as a candidate to re-test on future data, not a tradeable
  result.
- The full oscillator stack (fresh WT + MFI<40 + ADX>=25 simultaneously) almost
  never happens: n=0 on 1h, 2 on 30m, 23 on 15m. Demanding all oscillators agree
  at once selects a state that barely exists.

Verdict unchanged: 4H context (trend, structure, or momentum state) modulates the
lower-TF edge but cannot overcome the fee hurdle. The exclusion findings (skip 4H
chop states) would matter if a lower-TF edge existed to protect — none does.

### 1D oscillator states on the 4H star + filters combined with the exit schemes

Two follow-ups (same osc4h_filter.py grid, src=1D; exits now fixed 2R, fixed 3R,
and half@1R->BE+trail so the partial-TP risk rules are applied INSIDE the filter
tests):

**1D states do not improve the 4H star — they only shred its sample.** The star
has 117 trades; requiring 1D WT bear state keeps just 29 of them (the 4H signal
usually fires while the 1D oscillators haven't turned yet — consistent with it
catching lower-high rejections in *developing* downtrends). No 1D filter beats the
unfiltered star's train expectancy (+0.50R @3R, +0.36 trail); the cells that shine
in test (1D MFI<40: +2.2R @3R; 1D ADX>=25: +1.3R @3R) do so on 10-12 test trades.
1D WT fresh cross is actively bad (test 0% WR), and the 1D chop states are NOT
worse (ADX<20 trail: +1.10/+0.96) — the chop logic inverts yet again. Conclusion:
trade the 4H star unfiltered; 1D gating discards most of the real signals to
chase context the entry already prices in.

**Filters + higher R / partial exits on the lower TFs: still no rescue.** With a
3R target the 1h/15m filter grids stay negative out-of-sample (1h WT-fresh: +1.07R
train -> -0.08 test; 15m all cells negative), and several "chop" cells flip mildly
positive — more sign-instability. The one consistent cell remains **30m star + 4H
WT fresh bearish cross**: @2R +0.17/+0.36, @3R +0.35/+0.23, trail-positive in
test, n=63/32, ~1.5 trades/month. It is now positive in both halves across two
targets (not independent evidence — same trades), still small, still within
multiple-testing expectations across the ~300 cells scanned in this family.
Status: the single lower-TF candidate worth re-testing as new data accumulates;
not yet a tradeable edge.

## Reproduce

`study/` — `dataload.py` (clean parquet), `indicators.py` (causal indicators),
`engine.py` (fee/R backtest), `research.py`/`batch_scan.py` (edge scan),
`fourh_deep.py` (per-year stability), `finalists.py` (equity/DD), `intrabar.py`
(15m-path validation), `sfp_divergence.py` (swing-failure-timed divergence),
`sfp_exits.py` (exit engineering on the SFP entries), `mtf_stack.py` (multi-TF
filters on lower-TF entries), `osc4h_filter.py` (oscillator-state filters), `sfp_walkforward.py` (per-year walk-forward), `xrp_validation.py` (cross-asset),
`sfp_intrabar.py` (15m-path resolution), `portfolio.py` (combined book),
`maker_entry.py` (maker-fee entries), `unify.py` (sweep-family decomposition),
`eth_validation.py` (ETH data + validation).
Run via `./run.sh <script>`.
