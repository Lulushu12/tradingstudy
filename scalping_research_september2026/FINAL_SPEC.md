# Final strategy spec (frozen BEFORE the holdout test)

**Name:** Asia Opening-Range Fade (AORF)
**Markets:** Binance USDT-M perps BTC, ETH, XRP, SOL, ADA, AVAX
**Chart:** 15 minute, UTC

## Rules

1. **Opening range (OR):** high and low of the first 45 minutes of the UTC day
   (the 00:00, 00:15 and 00:30 candles).
2. **Signal window:** candles that open from 00:45 to 04:30 UTC (the 4 hours after the OR).
3. **Fade signal (first one of the day only):**
   - Long setup: previous candle closed **below** OR low and this candle closes **back above** OR low.
   - Short setup: previous candle closed **above** OR high and this candle closes **back below** OR high.
   - Only the first setup of the day counts. If that first setup is filtered out by rule 4, there is no trade that day.
4. **Trend filter:** yesterday's daily close vs the daily EMA(200) (on yesterday's completed daily candle).
   Longs only if above, shorts only if below.
5. **Entry:** market order at the open of the next 15m candle.
6. **Stop:** 4 x ATR(14) of the 15m chart (value on the signal candle), measured from the entry price.
7. **Breakeven:** once price has moved +1R in your favour (checked on candle closes using the candle's
   high for longs / low for shorts), move the stop to entry + 0.12% (long) / entry - 0.12% (short) to cover fees.
8. **No profit target.**
9. **Time exit:** close at market 72 hours (288 x 15m candles) after entry if still open.
10. **One position per coin.** If a coin still has an open trade, ignore its new signals.

## Sizing (Breakoutprop 1-step, $10k, 3% daily, 6% static)

- Risk **0.25% of the initial balance ($25) per trade**, position size = $25 / stop distance in %.
- Up to 6 positions at once (one per coin), so max simultaneous risk = 1.5%, which stays inside the 3% daily limit.

## Backtest assumptions

- Fees 0.04% per side, slippage 0.02% on market fills (entry, stop, time exit).
- Stop/target conflicts inside a candle resolved with 1m data, stop assumed first when ambiguous.
- Data: Binance USDT-M 1m klines, Jan 2020 to Sep 2026.

## Selection history (so the holdout can be judged honestly)

- In-sample 2020-2023 and out-of-sample 2024 to Sep 2025 were both looked at while choosing this.
- **Holdout Oct 2025 to Sep 2026 has not been used for any decision.** It is run once, after this file is committed.
