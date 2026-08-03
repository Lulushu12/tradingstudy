# My Best Trend Following Strategy (Forex & Stock Trading System)

- video_id: McZJPGsuYXQ
- url: https://www.youtube.com/watch?v=McZJPGsuYXQ
- duration: 09:19
- classification: STRATEGY

## Summary

This video presents a swing trading strategy that uses hidden divergences between price and the Stochastic indicator to generate high-probability entry signals in the direction of the main trend (identified by the 200 EMA). The core principle is to ignore all divergences except those aligned with the prevailing trend direction. The strategy is designed for higher timeframes (hourly, 4-hour, daily) to reduce noise and filter false signals.

## Instruments and timeframes stated

- markets: Forex (GBP/USD, Gold examples), cryptocurrency (Bitcoin example)
- timeframes: Hourly, 4-hour, daily recommended [03:00-03:30]; higher timeframes more reliable [08:30]
- sessions/hours: NOT STATED

## Strategy 1: Hidden Divergence Trend Following

### Indicators and settings

- 200-period Exponential Moving Average (EMA): for trend identification
- Stochastic Indicator: period = NOT STATED (default assumed)
- Divergence types: Hidden divergence (preferred) [02:00] and Classic divergence [01:00-01:30]

### Context / bias filter

Establish the main trend first with the 200 EMA [03:00]:
- Price above 200 EMA = uptrend confirmed; only search for long entry signals [03:30]
- Price below 200 EMA = downtrend confirmed; only search for short entry signals [03:30]

For uptrends: search for divergences on the LOWER side of the Stochastic [04:00]. For downtrends: search for divergences on the UPPER side of the Stochastic [04:00]. This filters out countertrend signals [04:00-04:30].

**Critical rule**: "We don't trade all the divergencies...most of the signals were false" [02:30]. Trade only divergences in the direction of the main trend [04:00].

### Entry trigger

**For Long Entries (Uptrend - Price above 200 EMA)**:

Search for hidden divergences on the lower side of Stochastic: price makes higher lows while Stochastic makes lower lows [04:30-05:00]. Also accept classic divergences: price makes lower lows while Stochastic makes higher lows [05:00].

Examples: GBP/USD 4-hour chart [04:30-06:00]:
- First signal: hidden divergence, "price was making higher lows, but the indicator was making lower lows" [04:30-05:00]
- Second signal: classic divergence, "price is making lower lows, but the indicator makes higher lows" [05:00-05:30]

**For Short Entries (Downtrend - Price below 200 EMA)**:

Search for hidden divergences on the upper side of Stochastic: price makes lower highs while Stochastic makes higher highs [06:30].

Examples: Gold 4-hour chart [06:30-07:30]:
- First signal: hidden divergence, "price was making lower highs, but the stochastic was making higher highs" [06:30]
- Second signal: classic divergence, "price is making higher highs, but the indicator is making lower highs" [06:30-07:00]

### Stop loss

NOT STATED

### Take profit / exit

NOT STATED

### Invalidation / skip conditions

Ignore all divergences on the opposite side of the Stochastic from the trend direction [06:00]. Do not trade divergences that signal reversals or countertrend positions [04:00-04:30]. Do not trade on lower timeframes (15-minute) [03:30]; use hourly or higher [03:00-03:30].

### Claimed performance

The speaker claims this strategy generates "high probability entry signals" [00:30]. He shows multiple chart examples (GBP/USD with 6 signals, Gold with 6 signals) all producing winning setups, but provides no overall win rate or statistical performance measure. He acknowledges the strategy is "more reliable when you are using higher time frames" [08:30].

### Vagueness log

1. UNDEFINED-PARAM: Stochastic period not stated; default assumed
2. UNDEFINED-RULE: Divergence definition - how many price lows/highs constitute a valid divergence; tolerance/tolerance for "higher low" vs "same low"
3. UNDEFINED-PARAM: Stop loss level not stated; distance from entry
4. UNDEFINED-PARAM: Take profit level or exit rule not stated
5. UNDEFINED-RULE: Entry confirmation - when exactly to enter after divergence is spotted; at divergence candle close, next candle, or specific price action confirmation

### Mechanizability

PARTIAL. The 200 EMA and Stochastic are mechanically computable. Divergence detection can be algorithmic if tolerance thresholds are defined (e.g., "higher low" means within X% of previous low but above it). However, the exact entry point within a divergence setup is not specified, and stop loss/take profit rules are entirely missing.

---

## Divergence Types (Educational Reference)

**Regular Divergence** (reversal signal - NOT traded in this strategy):
- Uptrend: higher high prices, lower indicator values (market exhaustion) [01:00-01:30]
- Downtrend: lower low prices, higher indicator values [01:30]

**Hidden Divergence** (continuation signal - PREFERRED in this strategy):
- Uptrend: higher lows of price, lower indicator values (momentum building) [02:00]
- Downtrend: lower highs of price, higher indicator values [02:00]

---

## Notable claims and caveats

The speaker emphasizes that divergences are "one of your most important tools" for trend traders [01:00]. He states that a divergence "signals momentum coming into the main trend" and suggests "a possible continuation in the prevailing direction" [01:00-01:30]. However, he warns that "during strong trends, the Stochastic will generate divergence after divergence, and most of the signals will probably fail" [02:30-03:00] if not filtered by trend direction.

The key insight is: "The trick of this strategy is to determine the main trend with the 200 EMA and only take positions in the direction of the trend" [08:00]. He emphasizes the importance of higher timeframes: "A signal that is produced on the 4-hour or on the daily chart is more reliable than a signal produced on the 15-minutes chart" [08:30].

The speaker advises traders to "train your eyes to spot the divergences on different charts" [08:00-08:30] and test the strategy on their charts [09:00]. He acknowledges that traders will have different results depending on market conditions. No mention of spread, slippage, or commission. No discussion of drawdown, losing streaks, or risk management beyond timeframe selection and trend filtering.
