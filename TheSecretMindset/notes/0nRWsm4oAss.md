# How to Increase Day Trading Profits Using Alligator Indicator (Forex & Stocks Strategies)

- video_id: 0nRWsm4oAss
- url: https://www.youtube.com/watch?v=0nRWsm4oAss
- duration: 10:24
- classification: MULTI-STRATEGY

## Summary
This video explains the Alligator indicator, created by Bill Williams, which uses three time-shifted smoothed moving averages to identify market structure, trend formation, and direction. The indicator is presented as a tool for recognizing when markets are trending (15-30% of the time) versus ranging (70-85% of the time). The video covers six distinct approaches to trading with Alligator: basic trend following, perfect order confirmation, dynamic support/resistance, fake crossover detection, golden/death crosses, and trend absence avoidance.

## Instruments and timeframes stated
- markets: Forex and stocks mentioned generally
- timeframes: NOT STATED (indicator can be applied to any timeframe)
- sessions/hours: NOT STATED

## Strategy 1: Basic Alligator Trend Entry and Exit

### Indicators and settings
- Green line (Lips): 5-period smoothed MA, displaced 3 periods forward
- Red line (Teeth): 8-period smoothed MA, displaced 5 periods forward
- Blue line (Jaws): 13-period smoothed MA, displaced 8 periods forward

### Context / bias filter
Alligator has "woken up" and is forming a trend. "A successful awakening of the alligator is a crossover of the fast green line through the slower lines, plus the slower lines following that direction, and all three lines spreading apart." [03:30]

### Entry trigger
"You want to see the green line cross both of the slower moving averages. You will also see the lips and the jaw start to turn in the direction of the green line. As an entry point, many traders will enter the market following a candle close above/below all 3 lines." [04:30]
Direction signal: "The green line crossing above the slower lines represents a buy signal. Crossing below represents a sell signal." [05:00]
Confirmation: "If all three move higher and widen, it confirms an uptrend. If the balance lines move downward and widen after a sell signal, it confirms a downtrend." [05:00]

### Stop loss
NOT STATED

### Take profit / exit
"As the trend comes to an end, the balance lines draw closer together. The fast green line crossing back over the slower lines is the signal to take your profit." [05:30]

### Invalidation / skip conditions
NOT STATED

### Claimed performance
"The key strength of the indicator is the way that it helps you to stick with a persistent trend." [05:30]
Also: "These periods of persistent trends are when the indicator tends to be more effective." [04:00]

### Vagueness log
1. "Candle close above/below all 3 lines": Exact condition not specified (does close need to clear all three, or just touch) (UNDEFINED-RULE)
2. "Following a candle close" entry timing: NOT STATED (entry on close, on next open, on next touch)
3. Stop loss placement: NOT STATED
4. Take profit target: NOT STATED
5. How much do lines need to "widen" to confirm: NOT STATED (UNDEFINED-PARAM)

### Mechanizability
PARTIAL - Moving average crossovers and candle placement relative to MA levels are mechanically computable. However, the specific entry rules (candle close above/below "all 3 lines") lack precision, and exit based on "lines drawing closer together" requires threshold definition.

## Strategy 2: Perfect Order Trend Confirmation

### Indicators and settings
- Same three Alligator lines (5, 8, 13 period SMAs with displacement)

### Context / bias filter
An uptrend or downtrend is forming

### Entry trigger
"The classical way to use The Alligator is to look for 'the perfect order'. The three moving averages should NOT cross. When doing that, the perfect order forms. Moreover, this signals a strong trend." [06:00]

### Stop loss
NOT STATED

### Take profit / exit
NOT STATED

### Invalidation / skip conditions
NOT STATED

### Claimed performance
Signals a "strong trend" [06:00]

### Vagueness log
1. "Perfect order" definition: Implied but not explicitly stated - presumably green > red > blue in uptrend or green < red < blue in downtrend (UNDEFINED-RULE)
2. Stop loss placement: NOT STATED
3. Take profit target: NOT STATED
4. Entry point when perfect order is achieved: NOT STATED

### Mechanizability
PARTIAL - The line order relationship can be tested mechanically, but entry timing once perfect order is detected is not specified.

## Strategy 3: Dynamic Support/Resistance Channel Trading

### Indicators and settings
- Green line (Lips): weak support/resistance
- Red line (Teeth): medium support/resistance
- Blue line (Jaws): strong support/resistance
- The channel between green and blue lines: dynamic support/resistance area [07:00]

### Context / bias filter
A trend is established (Alligator is "feeding" or active)

### Entry trigger
"When the Alligator is feeding, watch for pullbacks against the main trend direction and trade those moves with a pullback strategy." [07:30]
Specific application: "In a bullish trend, it shows support. In a downtrend, it show resistance." [07:30]
Structure: "The lips offer weak support. If bears push stronger, they might reach the teeth. Jaws represent the final support." [08:00]

### Stop loss
NOT STATED

### Take profit / exit
NOT STATED

### Invalidation / skip conditions
"Any move beyond and the trend is in danger." [08:00] (If price breaks below blue line in uptrend)

### Claimed performance
Described as offering "more value" than horizontal support/resistance [07:00]

### Vagueness log
1. "Pullbacks against the main trend direction": NOT DEFINED quantitatively (UNDEFINED-RULE)
2. Stop loss placement: NOT STATED
3. Take profit target: NOT STATED
4. Entry point on pullback to which line (green, red, or blue): NOT STATED (SUBJECTIVE)

### Mechanizability
PARTIAL - Support/resistance levels at MA lines can be computed, but pullback entry rules are not mechanically defined.

## Strategy 4: Fake Crossover Entry Strategy

### Indicators and settings
- Green line (fastest)
- Red line (medium)
- Blue line (slowest)

### Context / bias filter
The indicator is in a potential crossover situation

### Entry trigger
"When the green line crosses the red one and then turns again without reaching the blue line, a fake move just forms. Hence, in a bullish trend, you can search for long entries after this crossover. Or, in a bearish trend, go short when the perfect order gets back in place." [08:30]

### Stop loss
NOT STATED

### Take profit / exit
NOT STATED

### Invalidation / skip conditions
If the green line does cross the blue line, it's not a fake move but a real trend reversal

### Claimed performance
NONE CLAIMED

### Vagueness log
1. "Turns again without reaching the blue line": Exact threshold NOT STATED - how close does green need to come to blue (UNDEFINED-PARAM)
2. Entry timing after fake crossover: NOT STATED
3. Stop loss placement: NOT STATED
4. Take profit target: NOT STATED

### Mechanizability
DISCRETIONARY - Detecting a "fake crossover" where green crosses red but "turns again without reaching" blue requires subjective assessment of how close is "close enough."

## Strategy 5: Golden/Death Cross Strategy (Red and Blue Lines)

### Indicators and settings
- Red line (treated as faster MA): 8-period with 5-period displacement
- Blue line (treated as slower MA): 13-period with 8-period displacement
- Green line used as confirmation

### Context / bias filter
NOT STATED

### Entry trigger
"When the fast one moves above the slow one, a golden cross forms. This is bullish. When a death cross appears, the opposite is true. Bears are in control." [09:00]
Red crossing above blue = bullish (golden cross)
Red crossing below blue = bearish (death cross)
Green line used as confirmation [09:30]

### Stop loss
NOT STATED

### Take profit / exit
NOT STATED

### Invalidation / skip conditions
NOT STATED

### Claimed performance
NONE CLAIMED

### Vagueness log
1. Stop loss placement: NOT STATED
2. Take profit target: NOT STATED
3. "Green line confirmation" criteria: NOT SPECIFIED (UNDEFINED-RULE)
4. Entry timing after golden/death cross: NOT STATED

### Mechanizability
FULL - Red/blue line crossovers are mechanically computable. However, confirmation rules using green line are not specified, making the complete entry signal only PARTIAL.

## Notable claims and caveats

- Markets trend only 15-30% of the time while ranging 70-85% of the time [00:30]
- "Bill Williams was insistent that a successful trader will know the structure of the market" [01:30]
- The "sleeping alligator" metaphor: "the longer it has slept, the hungrier will be — in other words, the more pronounced the trend will be" [01:00]
- Indicator shifts moving averages forward in time (like Ichimoku Cloud), allowing future support/resistance to appear at present [06:30]
- "One of the drawbacks is the difficulty in successfully reading the opening signals in a timely manner" [05:30]
- During sleep/ranging periods, many false signals appear [05:30]
- "The bigger the distance between the lines, the stronger the support and resistance area. The bigger the time frame, the more difficult for the price to break through." [07:00]
- Indicator has "limited usefulness during choppy and trendless periods" [09:30]
- Recommendation for choppy periods: "use a different tool, such as a Momentum Indicator or a different oscillator to look for price/momentum divergence" [09:30]
- No discussion of transaction costs, spreads, slippage, or commissions
