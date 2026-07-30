# Frozen system spec

Written 2026-07-30, BEFORE the holdout was unsealed. Nothing below may change
based on holdout results. If the holdout disagrees with this spec, the spec is
what was tested and the holdout is the verdict.

## Universe
BTCUSDT.P, ETHUSDT.P, SOLUSDT.P, XRPUSDT.P, BNBUSDT.P (Binance USD-M perp data;
traded on Breakout).

## Timeframe
4h bars, UTC aligned (00:00, 04:00, ...).

## Signal (evaluated only on a CLOSED 4h bar)
Let:
- `trades` = number of trades in the bar
- `trade_intensity` = trades / mean(trades, last 96 bars)
- `atr` = ATR(14), Wilder/RMA smoothing
- `disp96` = (close - close[96]) / atr

LONG when all hold:
1. `trade_intensity > 1.8`
2. `disp96 > 0`
3. `close > open` (the spike bar closed in the trend direction)

SHORT is the exact mirror: `trade_intensity > 1.8`, `disp96 < 0`, `close < open`.

No other filters. No per-asset parameters. No session filter.

## Execution
- Entry: market order at the open of the next 4h bar, filled 1 minute after the
  bar opens (semi-automatic: alert fires on close, human clicks).
- Slippage: 0.02% per fill, charged against the trader on entry and exit.
- Commission: 0.04% per side (Breakout published taker).

## Risk
- Stop: 2 x ATR(14) from the signal bar close.
- Target: 2R (twice the stop distance). Fixed. No trailing, no partials, no
  break-even move.
- Time stop: close at market after 60 bars (10 days) if neither is hit.
- Risk per trade: 0.25% of current equity.
- Portfolio heat cap: 2.0% total risk live at once. A signal arriving when heat
  would exceed the cap is SKIPPED, not queued.
- Leverage cap: 5x BTC/ETH, 2x others. Where the stop is tight enough that the
  required notional exceeds the cap, size is reduced (the trade is not skipped).

## Why 0.25% and 2% heat
Not an optimisation. The account Monte Carlo shows mean monthly return is flat
at ~1.2-1.5% across every risk setting from 0.25% to 3%, while bust probability
rises from 3% to 69%. Since extra risk buys no extra mean return, the correct
choice is the smallest risk that still produces the return, which is the lowest
setting tested.

## Expected performance (studied data, 2021-01 to 2026-06, n=3391)
- Net expectancy +0.1426R per trade, 95% block-bootstrap CI [+0.040, +0.249]
- Win rate 35.1% at 2:1, 9.4% time-stopped
- ~51 signals/month across the 5 assets
- Mean monthly return +1.24%, P(bust in 30d) 3.2%, P(+10% in 30d) 9.1%

## Pre-registered holdout pass/fail
The holdout is 2026-06-22 to 2026-07-29, all five assets, never examined.

PASS if pooled net expectancy on the holdout is > 0.
FAIL if it is <= 0.

This is a weak test and is stated as such: ~5.5 weeks yields roughly 60 trades,
whose expectancy standard error is about 0.17R. It can detect a catastrophic
break. It cannot confirm the edge. A pass means "not falsified", nothing more.
