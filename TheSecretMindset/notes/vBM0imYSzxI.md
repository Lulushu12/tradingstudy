# Scalping Trading Was Impossible, Until I Found How To Combine EMA RSI ADX Indicators (FULL Strategy)

- video_id: vBM0imYSzxI
- url: https://www.youtube.com/watch?v=vBM0imYSzxI
- duration: 15:41
- classification: STRATEGY

## Summary

This video presents a scalping strategy combining three indicators to analyze price from different angles: RSI (3-period) for momentum, ADX (5-period) for volatility/trend strength, and 50-period EMA for trend direction. The strategy waits for the 3-period RSI to touch oversold (20) or overbought (80) levels, confirms with ADX above 30, and enters on a candle that breaks out of the RSI extremes. A specific momentum filter is emphasized: the candle immediately following the signal candle must break the signal candle's high/low, or the signal is skipped.

## Instruments and timeframes stated

- markets: "Forex or main indices" [13:30]
- timeframes: 5-minute (explicitly stated as "this is the timeframe I use and brought me the best results") [08:00]
- sessions/hours: "London trading session begins and when the US session ends" [13:30]; implies post-US session has lower volume and is avoided

## Strategy 1: EMA + RSI + ADX Scalping

### Indicators and settings

- RSI: period = 3 (modified from standard 14) [03:30-04:00], overbought threshold = 80 (not standard 70) [04:30], oversold threshold = 20 (not standard 30) [04:30]
- ADX: period = 5 (modified from standard 14) [05:30], key threshold = 30 [05:30]; reading below 25 = weak trend [05:30]; reading 30-50 = extremely strong trend [06:00]; reading over 50 = very strong and potential reversal [06:00]
- EMA: period = 50 [06:30], must be sloping (direction matters) [06:30]

### Context / bias filter

Trend filter using 50 EMA [06:30]:
- For long: "price is trading above the 50 EMA and ideally the average is sloping upwards" [07:00]
- For short: "price is trading below the 50 EMA and ideally the average is sloping downwards" [07:30]
- Avoid: "Never trade when the price breaks the 50 EMA several times in a short period of time" [13:00]; this signals consolidation
- Price action confirmation: "trade from levels of support and resistance" [13:30], "Fibonacci levels, or swing highs and lows" [13:30]
- Market hours: Trade "between the time the London trading session begins and when the US session ends" [13:30]; avoid off-hours due to low volume
- Spread requirement: "low spreads" essential for scalping [14:00]

### Entry trigger

Buy signal [07:00]:
1. Price above 50 EMA with EMA sloping upwards (trend condition)
2. 3-period RSI touches or goes below 20 (momentum condition)
3. ADX above 30 (volatility condition)
- Entry: "at the high of the first green candle, the candle which pulls the RSI from the oversold conditions" [07:00]
- Additional filter: "If the next candle after the signal candle, the one that pulls the RSI out of the overbought or oversold zone, doesn't break the signal candle, you skip the signal" [11:00-11:30]

Sell signal [07:30]:
1. Price below 50 EMA with EMA sloping downwards (trend condition)
2. 3-period RSI touches or goes above 80 (momentum condition)
3. ADX above 30 (volatility condition)
- Entry: "at the low of the first red candle, the candle which pulls the RSI from the overbought conditions" [07:30]
- Additional filter: Next candle must break the low of the signal candle [11:00-11:30]

### Stop loss

- Buy: "below this green candle" [08:30]; exact distance NOT STATED; example mentions "four pip stop loss" [09:30] but this is one example
- Sell: "above this red candle" [09:00]; exact distance NOT STATED
- Described as "very narrow stop loss" [08:30]

### Take profit / exit

"Aim for a 1:1 or a 1.5:1 risk-reward ratio" [09:00]
"Always close a part of your position when you reach a 1:1 risk reward ratio" [11:00]; definition of "a part" NOT STATED
Examples shown: one 2:1 risk-reward trade [09:30], multiple 1:1 trades [12:30]

### Invalidation / skip conditions

- Skip if ADX is below 30 at signal time [10:00-10:30]
- Skip if next candle after signal candle does not break the signal candle high/low [11:00-11:30]
- Skip if price is whipsawing (breaking EMA multiple times) [13:00]
- Avoid trading outside London-US session hours [13:30]

### Claimed performance

"This filter is extremely important...will save you many, many losing trades" [11:30] - referring to the momentum confirmation filter
"This filter...over 70%" - reduces false signals by over 70% [11:00]
Example win rates on specific trades: 2:1 [09:30], two 1:1 ratio trades [12:30]
Negative comparison: 2-period Connors RSI strategy "I never managed to get the win rate over 50%" [04:00]
General statement: "trade from these levels and you'll see consistent results" [13:30]

### Vagueness log

1. UNDEFINED-PARAM: "Sloping upwards" and "sloping downwards" for EMA not quantified; degree of slope NOT STATED [06:30, 07:00]
2. UNDEFINED-PARAM: "Very narrow stop loss" is subjective; specific pip distance NOT STATED [08:30]; single example of 4 pips [09:30] appears circumstantial
3. UNDEFINED-RULE: "Close a part of your position" when 1:1 is reached; what percentage constitutes a part NOT STATED [11:00]
4. UNDEFINED-RULE: What constitutes "breaking" a candle in the momentum filter; does entry mean open, close, or high/low of the next candle [11:00-11:30]
5. UNDEFINED-RULE: "Double bottom around the 50 EMA" mentioned as price action confirmation [08:30] but not formally in entry rules
6. UNDEFINED-PARAM: "Active market hours" beyond "London to US session end" - specific times NOT STATED [13:30]
7. UNDEFINED-PARAM: Spread requirements stated as "low spreads" but threshold NOT STATED [14:00]
8. SUBJECTIVE: Identifying "consolidation period" visually when price crosses EMA multiple times [13:00]

### Mechanizability

FULL - The strategy consists entirely of computable conditions: RSI period and thresholds, ADX period and threshold, EMA period and direction, price position relative to EMA, candle direction, and candle breakouts are all mechanically determinable from OHLCV data with the stated parameters. The only minor ambiguity is candle break confirmation (high vs close) which is trivial to specify once the general rule is understood.

---

## Notable claims and caveats

- Performance on 2-period Connors RSI variant was poor (never achieved 50% win rate) [04:00]
- Explicitly requires trading during liquid market hours only; volume drops significantly after US session [13:30]
- Requires narrow spreads to be profitable; scalping gains are small and easily eroded by costs [14:00]
- No mention of drawdown, maximum losing streak, or other risk metrics beyond the examples shown
- No discussion of commission impact
- Emphasis on discipline: "Be disciplined and don't ignore this filter" [11:30] regarding the momentum confirmation rule
