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

## Reproduce

`study/` — `dataload.py` (clean parquet), `indicators.py` (causal indicators),
`engine.py` (fee/R backtest), `research.py`/`batch_scan.py` (edge scan),
`fourh_deep.py` (per-year stability), `finalists.py` (equity/DD), `intrabar.py`
(15m-path validation). Run via `./run.sh <script>`.
