# Breakoutprop scalping research: results (September 2026)

## Bottom line

No system tested here is tradeable on a Breakoutprop 1-step $10k account (3% daily, 6% static drawdown).
The best historical edges worked from 2020 to September 2025 and then went flat or negative in the
locked holdout year (October 2025 to September 2026). 10% per month was not achievable at any risk level
that respects a 6% static floor.

## Setup

- Data: Binance USDT-M perps, 1m klines, Jan 2020 to Sep 2026: BTC, ETH, XRP, SOL, ADA, AVAX.
- Costs: 0.04% fee per side, 0.02% slippage on market fills. Stop assumed hit first when a 1m candle is ambiguous.
- Periods: in-sample 2020-2023, out-of-sample 2024 to Sep 2025, holdout Oct 2025 to Sep 2026 (used once).
- Execution timeframes tested: 5m and 15m, with higher-timeframe bias from 15m, 30m, 1h, 2h, 4h, 12h, 1D.

## What was tested

About 340 signal variants x 85 higher-timeframe filters x several exit templates, per coin, on 5m and 15m
(over 750,000 backtests), plus dedicated labs:

- Trend: EMA crosses, EMA pullbacks, MACD, Supertrend, Heikin Ashi, Donchian and squeeze breakouts,
  opening-range breakouts (Asia, London, New York), prior-day high/low breaks, break of structure.
- Mean reversion: Bollinger, Keltner, z-score, RSI, CCI, MFI, VWAP bands, consecutive-candle fades.
- Candlesticks: engulfing, pin bar, hammer, morning/evening star, piercing, three soldiers, outside bar,
  marubozu, tweezer, three-bar reversal (with and without location context).
- Support/resistance: floor pivots, Camarilla, prior-day sweeps, Asia-range sweeps, swing failure patterns.
- Divergences: RSI, MACD, histogram, Stochastic, OBV, volume delta, MFI (regular and hidden).
- Volume: climax, thrust, taker buy ratio, volume profile (POC, VAH/VAL, 80% rule).
- Fibonacci: retracements on objectively confirmed swings.
- Other: time-of-day, BTC lead-lag, cross-sectional long/short, funding-rate extremes, time-series momentum.

## Key findings

1. **Pure 5m scalping does not beat costs.** Round-trip cost is about 0.12%. On BTC 5m that is 0.85R on a
   1-ATR stop. Only 0.1% of 5m configs had a positive risk-adjusted return out of sample, and none held up.
2. **15m roughly halves cost per R**, and some edges looked real there, but all required holds of hours to days.
3. **Crypto volatility halved from 2021 to 2025-26** while costs stayed fixed, which steadily eroded every
   short-horizon edge.
4. **The only persistent historical effects were trend continuation (8h to 3 days) and the Asia opening-range
   fade.** Trend continuation is correlated across all 6 coins, producing drawdowns far beyond 6%.
5. **The Asia opening-range fade** was the most robust finding historically: 92% of 6,480 parameter variants
   profitable out of sample, all coins, all years 2020-2025, both directions. In the holdout year, it fell to
   a coin flip (52% of variants positive, median +0.004R).

## Holdout results (frozen spec in FINAL_SPEC.md, 0.25% risk per trade)

| Period | Trades | Avg R | Avg month | Max drawdown |
|---|---|---|---|---|
| 2020-2023 | 1,705 | +0.187 | +1.86% | 13.1% |
| 2024 to Sep 2025 | 1,082 | +0.166 | +2.14% | 8.4% |
| Oct 2025 to Sep 2026 | 604 | +0.005 | +0.07% | 13.3% |

Other historical survivors in the holdout year: 4h momentum -0.069R/trade, 2h momentum -0.023R,
RSI(3) dip -0.017R, Asia 60m fade (12h EMA200) +0.037R.

## Follow-up: swap fee, 30m/1h entries, walk-forward (after the holdout failed)

- **Breakoutprop daily swap (0.033% of position size for every position open at 00:00 UTC)** was not in
  the first round of tests. Added in `src/engine2.py`. It makes every multi-day strategy above worse,
  and favours being flat before 00:00 UTC.
- **Execution on 15m, 30m and 1h**, with the swap fee, and exits either flat before 00:00 UTC or a
  48h max hold: about 380,000 configs (all signal families x 21 trend filters x 12 exits), monthly P&L
  for Jan 2020 to Sep 2026.
- **Walk-forward test** (the holdout was spent, so this is the only honest method left): every quarter from
  Jan 2022, pick the best configs using only the previous 12/24/36 months, trade them the next 3 months.
  24 selector rules, all reported.

| Universe | Configs | Best rule, monthly Sharpe | Typical rule | Random picks |
|---|---|---|---|---|
| 1h | 123,882 | 0.23 | about 0.03 | -0.39 |
| 30m | 127,188 | 0.05 | about -0.07 | -0.49 |
| 15m | 128,346 | 0.02 | about -0.13 | -0.98 |
| All three | 379,416 | 0.11 | about -0.09 | -0.67 |

Most rules lost money over the last 12 months on every timeframe. Choosing strategies by their recent past
performance had no out-of-sample skill: what worked over the previous 1 to 3 years did not keep working over
the next 3 months. Full tables in `results/wf_select_*.txt`.

## Final conclusion

With Binance OHLCV (plus funding) data, 0.04% fees, slippage and the 0.033% daily swap, no strategy family
tested here shows an edge that persists into the most recent year, on 5m, 15m, 30m or 1h entries.
Nothing here should be traded on a Breakoutprop account.

## Files

- `src/`: data download, trade engine, indicators (TradingView-compatible definitions), signal library,
  scanners, labs, prop account simulator, holdout scripts.
- `results/holdout_report.txt`, `results/holdout_diag_others.txt`: holdout outputs.
- `FINAL_SPEC.md`: the strategy frozen before the holdout (commit a0c8862).
