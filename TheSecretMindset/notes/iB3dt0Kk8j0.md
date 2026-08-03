# Smart Money Concepts Without The Confusion (My Clean SMC Strategy)

- video_id: iB3dt0Kk8j0
- url: https://www.youtube.com/watch?v=iB3dt0Kk8j0
- duration: 30:04
- classification: MULTI-STRATEGY

## Summary

This video teaches a framework for day trading based on "smart money concepts" emphasizing market structure reading, liquidity hunting by institutional traders, and supply/demand zone identification. The speaker covers how to identify bullish/bearish trends via swing highs and lows, how to spot supply/demand imbalances, how big players exploit retail trader stops, and how to use tools like volume profile, discount/premium areas (Fibonacci-based), and inducement (fake breakouts) to find entries. The final filter is a 10-period simple moving average on the daily timeframe to align with the larger trend.

## Instruments and timeframes stated

- markets: Crude oil example shown [19:00]; implies forex, commodities, equities
- timeframes: Daily chart emphasized for trend filter [28:00]; trades executed on multiple shorter timeframes (1-hour, 4-hour implied) [28:30]
- sessions/hours: Asian, London, New York sessions mentioned [16:30] but not detailed

## Strategy 1: Market Structure - Swing High/Low Identification and Trend Confirmation

### Indicators and settings
- Swing highs: peak with lower highs on both sides [01:00]
- Swing lows: trough with higher lows on both sides [01:00]
- Bullish structure: higher highs and higher lows [00:30]
- Bearish structure: lower highs and lower lows [02:00]
- Break of structure: price breaks previous high (bullish) or low (bearish) [01:00]

### Context / bias filter
Larger timeframe must show clear trend direction [01:30]; avoid zooming too close to the chart or will miss bigger picture [01:30]

### Entry trigger
Bullish: price makes break of structure (breaks previous swing high) [01:00]; expect pullback, then wait for pullback completion before entering [02:30]
Bearish: price makes break of structure (breaks previous swing low) [02:00]
Entry occurs after pullback completes within the trend [02:30]

### Stop loss
NOT STATED (implied: below swing low for long, above swing high for short, but not explicitly stated)

### Take profit / exit
Target weak highs in bullish markets [03:30]; target weak lows in bearish markets [03:30]
Weak high: a high that fails to make a lower low below it [03:30]
Weak low: a low that fails to make a higher high above it [03:30]

### Invalidation / skip conditions
Trend change occurs when [04:00]:
- In bullish trend: price breaks below a strong low and forms a lower low = bearish change
- In bearish trend: price breaks above a strong high and forms a higher high = bullish change
Some traders require seeing both lower low AND lower high before confirming trend change [04:30]; speaker keeps it simple and trades trend change on first lower low [04:30]

### Claimed performance
NONE CLAIMED

### Vagueness log
1. Defining "obvious" swing highs and lows is SUBJECTIVE [01:00]; requires trader judgment
2. "Clear trend" and "bigger picture" are qualitative judgments - SUBJECTIVE
3. What constitutes "clear break of structure" is vague - needs definition of how far above/below previous level - UNDEFINED-RULE
4. "Strong low" vs. generic low not mechanically defined - SUBJECTIVE
5. "Weak high/low" concept depends on forward-looking price action, making entry timing unclear - UNDEFINED-RULE
6. "Clear" pullback completion is visual and subjective - SUBJECTIVE

### Mechanizability
PARTIAL. Once swing points are identified (which requires subjective judgment), the logic of higher highs/lows vs. lower highs/lows is mechanically checkable. However, defining which swing points to use and when a pullback has "completed" requires trader discretion. The concept of "strong" vs. "weak" highs/lows also introduces subjectivity.

## Strategy 2: Supply and Demand Zones

### Indicators and settings
- Zone types: base zones (range breakout edges), pivot zones (turning points), continuation zones (pullbacks before trend resume), reversal zones (trend direction changes) [06:30-07:30]
- Zone identification: find quick, strong price moves that suddenly reverse [06:00]
- Candlestick signals: For demand zone, strong down candle + next candle closes above its high [07:00]; for supply zone, strong up candle + next candle closes below its low [07:00]

### Context / bias filter
Zones should show clear imbalance between buyers and sellers [08:00]
Prefer fresh (untested) zones over repeatedly-tested zones [08:30]
Zones must have "inducement" - liquidity stacked in front of them [09:00]

### Entry trigger
Price returns to supply/demand zone [06:00]; specific entry signal NOT STATED (presumably related to candlestick confirmation)

### Stop loss
NOT STATED

### Take profit / exit
NOT STATED

### Invalidation / skip conditions
Zone strength weakens each time it is tested/hit [08:30]
Zone validity requires clear break of structure away from zone [09:00]
If zone gets tested multiple times, its effectiveness declines [08:30]

### Claimed performance
Zones are "key spots on charts where big players make their moves" [06:00]; strong zones show price moving sharply after formation [09:30]

### Vagueness log
1. "Quick, strong price moves" - no speed or magnitude threshold specified - UNDEFINED-PARAM
2. "Suddenly reverse" - how much reversal (5 pips, 20 pips?) - UNDEFINED-PARAM
3. Defining zone boundaries (from where to where exactly) is VISUAL-ONLY
4. "Clear break of structure" away from zone - threshold undefined - UNDEFINED-PARAM
5. "Inducement" concept is liquidity-based and difficult to quantify without order book data - UNDEFINED-RULE
6. What constitutes "fresh" vs. "tested" zone is subjective - SUBJECTIVE
7. "How long price stays at the level" [10:00] is vague - no time threshold - UNDEFINED-PARAM

### Mechanizability
DISCRETIONARY. While some elements are mechanically computable (candlestick patterns following strong moves), the core of supply/demand zone identification relies on visual chart observation of "quick, strong reversals," which cannot be precisely defined without parameters. The entry and exit rules are not specified at all.

## Strategy 3: Liquidity Concepts - Stop Loss Hunting

### Indicators and settings
- Liquidity accumulates at swing highs and lows [12:30]
- Liquidity types: Sell-side (below swing lows), Buy-side (above swing highs) [15:00]
- Previous week's high/low, previous day's high/low [16:30]
- Session highs and lows (Asian, London, New York) [16:30]

### Context / bias filter
Markets move based on where order clusters form [12:00]
Retail traders place stops just below support (sell-side liquidity) and above resistance (buy-side liquidity) [12:30]

### Entry trigger
Price approaches liquidity level; smart money initiates opposite-direction move to trigger stops [13:30]; after triggering stops, price reverses in original direction [15:30-16:00]

### Stop loss
NOT STATED

### Take profit / exit
After liquidity is cleared, price continues in the direction of the original trend [15:30-16:00]

### Invalidation / skip conditions
NOT STATED

### Claimed performance
Understanding liquidity levels helps predict "where big moves might start or end" [17:00]; useful for "planning trades within each trading day" [17:00]

### Vagueness log
1. "Liquidity accumulation" is not mechanically defined - UNDEFINED-PARAM (how many orders constitute a liquidity cluster?)
2. How big players decide to hunt liquidity is speculative - SUBJECTIVE
3. "Clear break of market structure" required to test zone [09:00] but not defined - UNDEFINED-RULE
4. Smart money strategy (triggering stops before moving) is observational, not mechanically tradeable - SUBJECTIVE
5. Identifying where "order clusters" exist requires order flow data not available to retail traders - UNDEFINED-RULE

### Mechanizability
DISCRETIONARY. The concept relies on observing where retail traders place stops (require order book/flow data), predicting when smart money will target those levels, and then positioning accordingly. This is a psychological/game-theory framework rather than a mechanically computable strategy.

## Strategy 4: Discount and Premium Areas (Fibonacci 50% Equilibrium)

### Indicators and settings
- Fibonacci tool: 50% level [18:00]
- Range: from swing low to end of move (marked manually) [18:00]
- Equilibrium: 50% Fib level divides discount/premium [18:00]
- Discount: below 50% level
- Premium: above 50% level [18:00]

### Context / bias filter
After range forms or break of structure identified [18:00]
Ranges expand as price moves, so Fibonacci tool must be moved up as price rises [19:00]

### Entry trigger
Buy in discount zone (below 50% equilibrium) [18:30]; short in premium zone (above 50% equilibrium) [18:30]
Example: Price pulls back to discount zone where demand zone exists [19:30]
Example: Price rises to premium zone where supply zone exists [19:30]

### Stop loss
Stop at the opposite end of range: for long stops at swing low, for short stops at swing high [18:30]

### Take profit / exit
Target at the opposite end of range: for long targets swing high, for short targets swing low [18:30]

### Invalidation / skip conditions
If entry in discount/premium zone but price breaks range opposite to trade direction

### Claimed performance
NONE CLAIMED numerically; theory: "deeper into discount you go, the better your risk to reward gets" [18:30]

### Vagueness log
1. "Ranges expand as price moves" - when/how often to adjust Fibonacci tool not specified - UNDEFINED-RULE
2. Range boundaries themselves are identified visually - VISUAL-ONLY
3. What constitutes clear range start is subjective - SUBJECTIVE
4. No confirmation signal for entry in discount/premium specified beyond supply/demand zones - UNDEFINED-RULE

### Mechanizability
PARTIAL. Once a range is identified (subjectively) and Fibonacci tool applied, the discount/premium zones are mechanically computable. However, identifying initial range boundaries and knowing when to extend the Fibonacci tool requires subjective chart observation. Entry and exit are defined but lack confirmation signals.

## Strategy 5: Inducement (Fake Breakout Setup)

### Indicators and settings
- Levels to target: strong highs and lows [21:30]
- Inducement pattern: price breaks level (triggering stops), then reverses sharply [20:30]

### Context / bias filter
Inducement works best aligned with overall trend or at key reversal points [25:00]
In uptrend: look for inducement down at major demand [25:00]
In downtrend: look for inducement up at major supply [25:00]

### Entry trigger
Price breaks above previous high, triggering buy stops [20:30]; but fails to continue, and reverses downward = inducement to sell detected [20:30]
Alternative: price touches swing low, causing inducement (creates new low, then bounces) [23:30]
Entry on the bounce after inducement (after reversal begins) [23:00-24:00]

### Stop loss
NOT STATED

### Take profit / exit
Ride the trend in the direction of original trend after inducement clears [23:00]

### Invalidation / skip conditions
If price continues in the breakout direction instead of reversing = not an inducement, inducement failed [21:00]
Requires patience; don't enter at absolute bottom of inducement move or you risk false signal [24:30]

### Claimed performance
Inducement "signals a significant reversal" when aligned with major demand/supply [25:00]

### Vagueness log
1. "Big players" placing orders for inducement is speculative without order flow data - SUBJECTIVE
2. How to distinguish inducement from legitimate breakout is not mechanically defined - UNDEFINED-RULE
3. "Quick jump up" before dropping and "quick dip" before climbing [21:00] - no time or distance threshold - UNDEFINED-PARAM
4. "Quickly bounces back" [24:00] - no definition of speed or magnitude - UNDEFINED-PARAM
5. How to confirm inducement setup is complete before entering [24:00] is vague - UNDEFINED-RULE
6. Entry timing relative to low/high is imprecise - UNDEFINED-RULE

### Mechanizability
DISCRETIONARY. While the pattern (breakout followed by reversal) is observable, distinguishing legitimate breakouts from inducement traps requires real-time judgment. The entry signal (when to enter after reversal begins) and the stop placement are not specified, making this impossible to code mechanically without adding subjective thresholds.

## Strategy 6: Volume Profile Analysis

### Indicators and settings
- Tool: Anchored volume profile [25:30]
- Point of Control (POC): price level with most volume [26:00]
- High-volume zones: bars taller than neighboring bars [26:00]

### Context / bias filter
Apply at start of price move [26:00]
Combine with key levels and reversal points [27:00]
Use on larger chart areas to find best zones across wider range [28:00]

### Entry trigger
Price returns to high-volume zone / point of control [26:00-26:30]
Combine with reversal point alignment for stronger signal [27:00]

### Stop loss
NOT STATED

### Take profit / exit
POC acts as potential reversal or exit target [26:00]
Larger high-volume zone combined with reversal point creates strong target [27:00]

### Invalidation / skip conditions
NOT STATED

### Claimed performance
High trading volume shows where traders had "lots of interest" [26:00]; "more likely" to react when price returns [26:00]

### Vagueness log
1. "High trading volume" threshold not defined - UNDEFINED-PARAM (how much higher than neighboring bars?)
2. Profile window selection not specified (what period to analyze?) - UNDEFINED-PARAM
3. How to "combine" volume profile with market structure not precisely defined - UNDEFINED-RULE
4. "Higher quality zones" combining volume and reversal points is subjective judgment - SUBJECTIVE
5. When to enter if price approaches POC without touching it is unclear - UNDEFINED-RULE

### Mechanizability
PARTIAL. Volume profile generation is mechanically computable from OHLCV data. However, defining which price levels constitute "high volume" requires a subjective threshold or standard deviation measure. The entry rule (when price returns to zone) and the combination with reversal points lack specificity.

## Strategy 7: 10-Period SMA Daily Chart Trend Filter

### Indicators and settings
- Moving average: 10-period Simple Moving Average [28:00]
- Timeframe: Daily chart [28:00]
- Slope direction: upward = bullish, downward = bearish [28:30]

### Context / bias filter
Use to filter overall market bias before entering shorter timeframe trades

### Entry trigger
Price above 10-SMA on daily chart + upward slope = look for buy trades on shorter timeframes [28:30]
Price below 10-SMA on daily chart + downward slope = look for sell trades on shorter timeframes [28:30]
Price near or crossing 10-SMA = avoid trading, wait for clear trend [29:00]

### Stop loss
NOT STATED

### Take profit / exit
NOT STATED; this is a bias filter, not a complete strategy

### Invalidation / skip conditions
When price crosses the 10-SMA, the trend is unclear = skip trading [29:00]

### Claimed performance
"Solution was extremely simple" [28:30]; problem: "biggest problem was trading the wrong trends...caught in false moves and choppy markets" - solved by this filter [28:00]

### Vagueness log
1. "Price near the moving average" - no distance threshold specified - UNDEFINED-PARAM (how many pips/% away = "near"?)
2. Defining slope direction requires looking at recent bars - not mechanically specified how many bars back to measure - UNDEFINED-PARAM
3. "Clear trend or avoid trading" - no definition of what constitutes "clear" - UNDEFINED-RULE

### Mechanizability
FULL. The 10-period SMA is mechanically computable. Price position relative to the MA is mechanically checkable. Slope direction is computable. This is the most mechanizable concept in the video, though the threshold for what constitutes "near" and entry/exit rules for shorter timeframe trades are left to trader discretion.

## Notable claims and caveats

The speaker claims to have solved a personal problem: "In my first 2 years of day trading, my biggest problem was trading the wrong trends. I kept getting caught in false moves and choppy markets" [28:00]. The speaker attributes improvement to starting with 10-SMA daily filter and "I saw immediate improvement once I started using volume profile" [25:30].

The speaker mentions the target of "$100 a day from trading" in the intro [00:00] but never quantifies win rate, profit factor, or actual results for any of the strategies presented.

The video does NOT mention transaction costs, spread, slippage, or commission impact at any point.

The video does NOT discuss drawdown periods, losing streaks, or maximum consecutive losses.

The speaker notes that "changes of character...will often give false signals, because we bet on a reversal" [05:00] but does not provide statistics on false signal frequency.

The speaker emphasizes that "big players," "smart money," and "institutions" hunt retail trader stops [12:30-15:00], but this is presented as market theory rather than tested methodology.

All supply/demand, liquidity, and inducement concepts require visually identifying price reactions on charts, with no backtest data provided.
