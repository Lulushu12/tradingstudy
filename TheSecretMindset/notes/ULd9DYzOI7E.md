# This Indicator Will Make You Trade Better (Trading Strategies With Momentum Indicator)

- video_id: ULd9DYzOI7E
- url: https://www.youtube.com/watch?v=ULd9DYzOI7E
- duration: 10:11
- classification: MULTI-STRATEGY

## Summary
This video teaches the Momentum indicator, which measures price velocity by comparing the current price to a price from a previous period. The video covers how to read momentum signals, explains why basic 0-line crossovers fail as a standalone strategy, and presents three refined approaches: combining momentum with price action and key levels, using momentum divergence with a 200-period EMA trend filter, and using momentum moving average crossovers. The recurring theme is that momentum is most effective as a confirmation tool, not as a primary signal generator.

## Instruments and timeframes stated
- markets: Stocks (Tesla mentioned [04:00, 07:00])
- timeframes: Daily (D1) and hourly mentioned in examples [04:00, 07:00]
- sessions/hours: NOT STATED

## Strategy 1: Momentum 0-Line Crossover (Basic Approach - Not Recommended Alone)

### Indicators and settings
- Momentum indicator: period 7, 14, or 21 most common [01:30]
- Period over 21: less sensitive, fewer signals, smoother line [01:30]
- Period below 10: oversensitive, more noise, many false signals [01:30]

### Context / bias filter
None specified for basic crossover approach; this is presented as flawed

### Entry trigger
"When momentum indicator crosses above zero, a buy signal is generated. When momentum indicator crosses below zero, a sell signal is generated." [03:30]

### Stop loss
NOT STATED

### Take profit / exit
NOT STATED

### Invalidation / skip conditions
NOT STATED

### Claimed performance
"Despite the fact we are analyzing the d1 chart, we can clearly see that the indicator is not reliable for generating good signals when used alone" [04:30]
"At least 4 or 5 false signals which would have damaged your account" in range-bound markets [04:00]

### Vagueness log
1. Stop loss placement: NOT STATED
2. Take profit target: NOT STATED
3. Position sizing: NOT STATED

### Mechanizability
FULL - Momentum calculation and 0-line crossovers are mechanically computable with stated period parameters.

## Strategy 2: Momentum with Price Action and Key Levels

### Indicators and settings
- Momentum indicator: period NOT SPECIFIED (presumably 14 default)
- Support and resistance lines (drawn on price chart)
- Trend identification via price action (lower lows/highs for downtrend, higher lows/highs for uptrend)

### Context / bias filter
1. Identify the main trend using price action first [05:00]
2. In a downtrend: ignore momentum crosses above 0, focus only on short signals [05:00]
3. In an uptrend: ignore momentum crosses below 0, focus only on long signals (implied)

### Entry trigger
Momentum confirmation of price action setup:
"We have a breakout of a key support line, with the retest of the breakout level and the momentum staying below 0 line. A short around this area was a high probability trade, because we had price action and momentum indicating the same thing." [05:30]

Entry requires:
1. Price action signal (breakout + retest of key level)
2. Momentum alignment with trend (below 0 for shorts in downtrend)

### Stop loss
NOT STATED

### Take profit / exit
NOT STATED

### Invalidation / skip conditions
Momentum should align with trend direction; counter-trend momentum signals should be ignored [05:00]

### Claimed performance
"A short around this area was a high probability trade, because we had price action and momentum indicating the same thing" [05:30]

### Vagueness log
1. Support/resistance line identification: SUBJECTIVE
2. "Key" support/resistance: NOT DEFINED (UNDEFINED-RULE)
3. Stop loss placement: NOT STATED
4. Take profit target: NOT STATED
5. Breakout confirmation: NOT SPECIFIED (UNDEFINED-RULE)

### Mechanizability
PARTIAL - Momentum below/above 0 is computable, but identifying key levels and price action breakouts requires subjective judgment.

## Strategy 3: Momentum Divergence with 200 EMA Trend Filter

### Indicators and settings
- Momentum indicator: period NOT SPECIFIED (presumably 14)
- 200-period exponential moving average (trend filter)
- Divergence: price and momentum moving in opposite directions [05:30]

### Context / bias filter
Trend established by 200 EMA:
- Price above 200 EMA: uptrend context, search for divergences on lower side of momentum [06:30]
- Price below 200 EMA: downtrend context, search for divergences on upper side of momentum [07:00]

Only take divergences in the direction of the main trend [06:30]

### Entry trigger
Divergence in direction of trend + momentum 0-line cross:
"I enter when i spot a divergence in the direction of the trend, when the momentum crosses below or above the 0 line." [07:00]

Examples given [07:30-08:00]:
- Price making higher highs but momentum indicating lower highs = bearish divergence in downtrend
- Price making lower highs but momentum showing higher highs = hidden divergence in downtrend
- Entry on momentum 0-line cross

### Stop loss
NOT STATED

### Take profit / exit
NOT STATED

### Invalidation / skip conditions
Do not take divergences counter to main trend [08:30]: "I trained myself to ignore the signals that aren't in line with the main trend"
Speaker warns: "I lost a lot of money entering countertrend positions" [08:30]

### Claimed performance
Examples show good trades with divergences in trending direction [07:30-08:00]
Caveat: "The price could increase even more" without the 0-line cross protection buffer [08:00]

### Vagueness log
1. Momentum period: NOT STATED (UNDEFINED-PARAM)
2. Divergence definition: "regular divergence" vs "hidden divergence" mentioned but not fully defined (UNDEFINED-RULE)
3. "Lower highs" / "higher lows" exact threshold: SUBJECTIVE
4. Stop loss placement: NOT STATED
5. Take profit target: NOT STATED
6. 0-line cross timing relative to divergence: unclear if immediate or any cross works (UNDEFINED-RULE)

### Mechanizability
PARTIAL - 200 EMA is fully computable, momentum 0-line crosses are computable, but divergence detection requires comparing price and momentum extremes with subjective thresholds.

## Strategy 4: Momentum Moving Average Crossover

### Indicators and settings
- Momentum indicator: period NOT SPECIFIED
- Moving average applied to momentum: period NOT SPECIFIED ("many traders prefer to add a moving average on it")
- Oscillator-MA crossover signals

### Context / bias filter
Works best in trending markets; not effective in ranging markets [09:00]
"If the trend is up, make a long trade only after the indicator has moved above the moving average" [09:30]

### Entry trigger
"Crossover will be effective when markets are trending" [09:00]
Entry when momentum crosses its moving average in the direction of the trend [09:00-09:30]

### Stop loss
NOT STATED

### Take profit / exit
NOT STATED

### Invalidation / skip conditions
Do not use in ranging markets [09:00]
Only take crossovers in trending direction [09:30]

### Claimed performance
NONE CLAIMED (presented as an alternative but speaker prefers 0-line cross with price action)

### Vagueness log
1. Moving average period: NOT STATED (UNDEFINED-PARAM)
2. Momentum period: NOT STATED (UNDEFINED-PARAM)
3. Stop loss placement: NOT STATED
4. Take profit target: NOT STATED
5. "Effective when markets are trending": NOT DEFINED quantitatively (UNDEFINED-RULE)

### Mechanizability
PARTIAL - Moving average crossovers are mechanically computable once periods are defined, but identifying trending vs ranging markets requires subjective assessment.

## Notable claims and caveats

- Momentum indicator "identifies the strength or speed of a price movement" [01:00]
- Calculated as "difference between the most recent price and the closing price of a previously determined period" [01:00]
- "When you have momentum on your side, trading becomes easy" [00:30]
- "When you enter during a lack of momentum, your trade will stagnate or even worse, you will get chopped out by lateral price movement" [00:30]
- Zero-line crossover is "not the smart way" to trade momentum [03:30]
- "Should never use momentum as a standalone tool" [04:30]
- "Use momentum as an additional confirmation instrument, to confirm your bias" [04:30]
- Lower momentum settings (below 10) result in "more market noise" and "many false signals" [01:30-02:00]
- Higher momentum settings (over 21) result in "fewer, but better quality signals and a smoother line" [01:30]
- Momentum divergence "could be an early indicator of a reversal" [06:00]
- 0-line cross provides "a protection buffer" and prevents entering too early on divergence [08:00]
- Speaker learned painful lesson: "I lost a lot of money entering countertrend positions" [08:30]
- Recommends "ride the main trend, and all the setups that occur in the opposite direction will be ignored" [09:00]
- Moving average crossovers "will not work" in ranging markets [09:00]
- Speaker prefers 0-line cross with price action to moving average crossover [09:30]
- No discussion of transaction costs, spreads, slippage, or commissions
