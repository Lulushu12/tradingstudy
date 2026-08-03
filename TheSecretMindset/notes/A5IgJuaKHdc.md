# BEST 3-in-1 Indicator | Traders Dynamic Index Trading Strategies (TDI Explained for Beginners)

- video_id: A5IgJuaKHdc
- url: https://www.youtube.com/watch?v=A5IgJuaKHdc
- duration: 10:02
- classification: MULTI-STRATEGY

## Summary
This video teaches the Traders Dynamic Index (TDI), a hybrid indicator combining RSI, a moving average, and Bollinger Bands into one tool. The video covers five distinct trading signals that can be extracted from the TDI: line crossovers (RSI/MA, MA/middle BB, and the 50 level), volatility/trend strength analysis, and divergences. The approach emphasizes combining TDI signals with price action and key support/resistance levels.

## Instruments and timeframes stated
- markets: NOT STATED (general application to any market)
- timeframes: "Longer timeframes" mentioned for the 50-level crossing signal as being especially significant [06:30]. 5-minute example shown for pattern illustration but no specific timeframe requirement stated
- sessions/hours: NOT STATED

## Strategy 1: Green/Red Line Crossover (RSI/Moving Average Crossover)

### Indicators and settings
- TDI with RSI settings: Period NOT STATED for default, speaker recommends NOT below 20 [02:30]
- Moving average applied to RSI: period 12 or 21 preferred [03:00]
- Bollinger Bands: period NOT below moving average period, speaker prefers 50 or 100 [03:00]

### Context / bias filter
Must first identify major support and resistance levels on the chart [04:30]. Speaker states: "Before acting on the crossover of the green and red lines, examine price action and make sure you identified all major support and resistance points on your chart and take signals from these key areas" [04:30]

### Entry trigger
"If the green line crosses the signal red line from below, it is a signal to buy; if it crosses the red line from above, this is a signal to sell." [04:00]

### Stop loss
"Place the stop loss behind the nearest swing high/low" [04:00]

### Take profit / exit
"Take the profit at the channel bands (the blue lines) or after an inversed crossing of the green and red lines." [04:00]

### Invalidation / skip conditions
Can generate false signals when price trend isn't strong: "if the price trend isn't strong, you have multiple crossovers in a short period of time, offering many false signals." [04:00]

### Claimed performance
Described as part of a strategy framework for "trading consistency" [00:00]. Noted as having "false signals" under certain conditions [04:00]

### Vagueness log
1. RSI period for TDI: NOT STATED (range given: NOT below 20, but no specific default stated)
2. What constitutes an "important" support/resistance level: SUBJECTIVE
3. "Nearest swing high/low" precise definition: NOT STATED (UNDEFINED-RULE)
4. How far is "behind" the swing point: NOT STATED (UNDEFINED-PARAM)
5. Take profit precision at "channel bands": NOT STATED (edge, middle, or which specific band level)

### Mechanizability
PARTIAL - Crossovers can be coded mechanically, but entry depends on identifying major support/resistance levels which is subjective, and stop loss placement at "nearest swing" requires definition of swing criteria.

## Strategy 2: Red/Yellow Line Crossover (MA/Middle Bollinger Band Levels)

### Indicators and settings
- Yellow line: Middle Bollinger Band, period 50 preferred [03:00]
- Red line: Moving average of RSI, period 12 or 21 preferred [03:00]
- Key levels: 30 and 70 on the RSI scale

### Context / bias filter
Yellow line typically trades in 30-70 range [05:00]. Used to define "key turns for a change in the trend" [05:30]

### Entry trigger
Multiple conditions defined:
1. Yellow crosses 30 upward: "potential reversal or the beginning of an ascending correction" [05:30]
2. Yellow crosses 70 downward: "beginning of a descending correction" [05:30]
3. Global trend combination: "When the yellow line is pointing down and the red line is below it − the trend is considered bearish; for a bullish market you need a mirror image − the yellow line turns up and the red line moves above it." [06:00]

### Stop loss
NOT STATED

### Take profit / exit
NOT STATED

### Invalidation / skip conditions
"You don't take crossover signals blindly, you take them after you identified the key levels in the market." [06:00]

### Claimed performance
Describes yellow line as long-term trend indicator defining "key turns" [05:30]

### Vagueness log
1. Stop loss placement: NOT STATED
2. Take profit target: NOT STATED
3. Entry timing precision on the exact crossover or confirmation: NOT STATED
4. How to identify "key levels" for taking signals: SUBJECTIVE

### Mechanizability
PARTIAL - 30/70 level crossovers are mechanically computable, but entries require identifying subjective support/resistance levels first.

## Strategy 3: Yellow Line Crosses 50 Level

### Indicators and settings
- Yellow line (middle Bollinger Band): period 50 preferred
- Crossover level: 50 (the center of the RSI scale)

### Context / bias filter
Described as "long-term trading signal, especially if it appears on longer timeframes" [06:30]

### Entry trigger
"If the yellow line crosses the centerline from below, this is a signal to buy; if it crosses the level from above, it's a signal to sell." [06:30]

### Stop loss
NOT STATED

### Take profit / exit
NOT STATED

### Invalidation / skip conditions
Speaker recommends combining with "breakouts of the support/resistance levels or lines, the formation of new price patterns" for stronger signals [07:00]

### Claimed performance
Described as powerful signal, especially on longer timeframes [06:30]

### Vagueness log
1. Stop loss placement: NOT STATED
2. Take profit target: NOT STATED
3. What additional price patterns constitute confirmation: NOT STATED

### Mechanizability
FULL - The 50 level crossover is mechanically computable from OHLCV data with stated parameters.

## Strategy 4: Volatility and Trend Strength Analysis

### Indicators and settings
- Blue Bollinger Bands (upper and lower)
- Green line (RSI)
- Yellow line slope and position

### Context / bias filter
Used to assess market conditions rather than direct entry signals

### Entry trigger
Not an entry signal itself, but assessment tool for market state:
- "If the channel bands diverge or expand and the green line forms a strong direction (up or down), then there is active volatility on the market (and the probability of strong directional movements or continuation of the current trend is high)" [07:30]
- "If the channel lines converge or become narrow, and the RSI line shows short movements − the market is ranging, or is preparing for this state" [08:00]
- "The closer the green line to the centerline (level 50), the less the market is active" [08:00]

### Stop loss
NOT STATED

### Take profit / exit
NOT STATED

### Invalidation / skip conditions
NOT STATED

### Claimed performance
Used to evaluate when to actively trade (trending) vs avoid (ranging)

### Vagueness log
1. What defines "strong direction": NOT STATED (UNDEFINED-PARAM)
2. "Diverge or expand" criteria: NOT STATED (UNDEFINED-RULE)
3. This is more of a market assessment than actionable strategy - no specific entry/exit

### Mechanizability
PARTIAL - Band convergence/divergence is computable, but "strong direction" of green line is subjective.

## Strategy 5: TDI Divergence Trading

### Indicators and settings
- TDI with same parameters as above
- Look for divergences between price and TDI (green RSI line)

### Context / bias filter
Price has reached a new extreme (high or low)

### Entry trigger
"Occasionally, price makes a new (higher) high and TDI fails to do so (the new high on TDI is lower than the previous high). Conversely, sometimes price makes new lower low, but TDI does not get below its previous low." [08:30]
Entry occurs after spotting divergence: "A high probability signal would be a crossover between the RSI line and the moving average, after you spot a divergence. Of course, this must occur at an important level of support or resistance." [09:00]

### Stop loss
NOT STATED

### Take profit / exit
NOT STATED

### Invalidation / skip conditions
Entry must occur at important support or resistance level [09:00]

### Claimed performance
Described as "high probability signal" when combined with price extremes and key levels [09:00]

### Vagueness log
1. Stop loss placement: NOT STATED
2. Take profit target: NOT STATED
3. "Important level of support or resistance": SUBJECTIVE
4. Which type of divergence (regular vs hidden): NOT STATED

### Mechanizability
PARTIAL - Divergence detection is computable (comparing price and TDI extremes), but confirmation requires subjective identification of support/resistance levels.

## Notable claims and caveats

- TDI is described as combining three pillars: "finding the market direction, evaluating the strength of the trend and effectively assessing the volatility" [00:00]
- Crossover signals can generate "many false signals" if price trend isn't strong [04:00]
- Speaker recommends always checking support/resistance levels before taking crossover signals [04:30]
- Yellow line is preferred by speaker over red line to "smooth out the noise of shorter-term price fluctuations" [07:00]
- No discussion of transaction costs, spreads, slippage, or commissions
- Heavy emphasis on combining TDI signals with price action analysis
