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

## Reproduce

`study/` — `dataload.py` (clean parquet), `indicators.py` (causal indicators),
`engine.py` (fee/R backtest), `research.py`/`batch_scan.py` (edge scan),
`fourh_deep.py` (per-year stability), `finalists.py` (equity/DD), `intrabar.py`
(15m-path validation), `sfp_divergence.py` (swing-failure-timed divergence),
`sfp_exits.py` (exit engineering on the SFP entries). Run via `./run.sh <script>`.
