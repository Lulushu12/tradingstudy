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

## Follow-up: is the edge already priced in? (decay.py)

Objection raised: if this worked for years on public price data, it should already be
arbitraged away, and we should instead hunt systems that exploit the crowd trading the
old one. That is a testable claim, not a philosophical one. A crowded-out edge decays.

Test: no refitting. Take the finalists exactly as frozen above, split realised net_R by
year and by first/second half, and regress net_R on time. A real decay shows a
significantly negative slope.

| strategy | slope (R per year) | 95% CI | p | second half minus first |
|---|---|---|---|---|
| volspike 2:1 | -0.055 | -0.140 .. +0.030 | 0.21 | -0.13 R (p=0.31) |
| volspike 1:1 | -0.045 | -0.093 .. +0.003 | 0.06 | -0.11 R (p=0.13) |
| trig 2:1 | -0.013 | -0.081 .. +0.055 | 0.71 | -0.07 R (p=0.52) |
| trig 1:1 | -0.022 | -0.057 .. +0.014 | 0.23 | -0.05 R (p=0.43) |

Per-year expectancy, volspike 2:1: 2021 +0.28, 2022 +0.42, 2023 +0.36, 2024 +0.35,
2025 +0.14, 2026 +0.12. Expectancy stays positive every year but the last two years are
roughly a third of the 2022-2024 level.

Reading this honestly:
- All four slopes are negative. None is significant at 5%. The consistent sign across
  variants is weak evidence for decay, not proof, and the variants share trades so they
  are not four independent tests.
- The test has poor power. Over this span it can only detect a slope beyond roughly
  ±0.12 R/yr (volspike 2:1). A slow real decay would be invisible here.
- If the volspike 2:1 point estimate were real, expectancy would cross zero about 8.3
  years after 2021, i.e. around 2029. At 1:1 it is about 5.7 years, i.e. around 2027.
  These are extrapolations from a non-significant slope and should not be planned on.

Confound, and it is the main one. Per-year market character on 4H:

| year | trend efficiency | annualised vol | year return |
|---|---|---|---|
| 2021 | 0.187 | 81% | +36% |
| 2022 | 0.203 | 57% | -64% |
| 2023 | 0.219 | 38% | +156% |
| 2024 | 0.216 | 49% | +121% |
| 2025 | 0.181 | 41% | -6% |
| 2026 | 0.194 | 42% | -27% |

2025 and 2026 are the two lowest trend-efficiency years in the sample. A
trend-continuation strategy is supposed to earn less when price travels less
efficiently. Spearman rho between yearly efficiency and yearly expectancy is +0.66 on
n=6, which is directional and nowhere near significant. So the recent softness is
equally consistent with "2025-26 chopped" and with "the edge is being competed away",
and 5.5 years of one asset cannot separate the two. Anyone claiming otherwise is
reading noise.

On the proposed alternative (trade against the crowd running the old system): it is not
testable with anything in this repo. Crowding is a positioning variable. OHLCV cannot
see it. Doing it properly needs funding rates, open interest, and liquidation data,
pre-registered the same way as the current spec. Note also that the price-only proxy
for this idea, liquidity-sweep reclaim, was already scanned and rejected above.

## Follow-up: cross-asset replication (fetch_alt.py, crossasset.py)

The BTC-only decay test has poor power and another BTC year adds almost nothing. A far
stronger test is the same rule, zero refitting, on assets never looked at while building
it. Data: OKX 4H perps, 2021-01 onward (Binance and Bybit are geo-blocked from this
environment). Rule taken verbatim from `finalists.make_signals("volspike")`.

**rr=2:1, single position, 0.08% round trip:**

| asset | n | WR | expR | 95% CI | decay slope |
|---|---|---|---|---|---|
| BTC | 549 | 44.3% | +0.290 | +0.166 .. +0.415 | -0.055/yr |
| ETH | 525 | 43.6% | +0.280 | +0.152 .. +0.407 | +0.013/yr |
| SOL | 506 | 39.7% | +0.172 | +0.044 .. +0.300 | -0.044/yr |
| LINK | 454 | 38.8% | +0.143 | +0.008 .. +0.277 | -0.027/yr |
| XRP | 541 | 38.6% | +0.135 | +0.012 .. +0.258 | -0.024/yr |
| DOGE | 525 | 38.1% | +0.122 | -0.002 .. +0.247 | +0.012/yr |
| ADA | 476 | 35.7% | +0.053 | -0.076 .. +0.182 | -0.001/yr |
| LTC | 483 | 35.6% | +0.044 | -0.084 .. +0.173 | -0.043/yr |
| BNB | 366 | 35.0% | +0.011 | -0.136 .. +0.158 | -0.020/yr |

9/9 positive point estimates, 5/9 with CI excluding zero. Pooled ex-BTC: n=3876,
expR +0.126, p<0.0001 naive. These assets are not independent: mean pairwise correlation
of monthly strategy returns is 0.29, so 9 assets behave like about 2.7 independent ones,
giving a correlation-adjusted **p of about 0.003**. At 1:1 the same picture holds weaker:
8/9 positive, pooled ex-BTC +0.052, adjusted p about 0.033.

What this changes:

1. **The edge is not a BTC curve-fit.** It replicates on eight assets and a different
   exchange with nothing re-tuned. That is the strongest evidence in this repo.
2. **"Already priced in" gets weaker, not stronger.** Decay slopes flip sign across
   assets (6 negative, 2 positive, 1 flat). There is no consistent cross-sectional decay.
   If a crowd were competing this away it should show up worst on BTC, the most
   systematically traded name. BTC is instead the *best* performer.
3. **The headline +0.21R is probably optimistic.** BTC sits at the top of the
   cross-sectional distribution and the median alt is about +0.13R, roughly half. Some of
   the BTC number is luck in the one sample that was studied. Plan on the lower figure.
4. Alts have thinner books, so real slippage on the smaller names is worse than the
   0.08% modelled. The alt numbers are upper bounds on what is tradeable there.

## Reproduce

`study/` — `dataload.py` (clean parquet), `indicators.py` (causal indicators),
`engine.py` (fee/R backtest), `research.py`/`batch_scan.py` (edge scan),
`fourh_deep.py` (per-year stability), `finalists.py` (equity/DD), `intrabar.py`
(15m-path validation), `decay.py` (alpha-decay / priced-in test),
`fetch_alt.py` + `crossasset.py` (cross-asset replication).
Run via `./run.sh <script>`.
