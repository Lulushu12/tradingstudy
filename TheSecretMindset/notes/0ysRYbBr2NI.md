# I Spent 500 Hours Learning Smart Money Concepts & ICT (Here's The Shortcut)

- video_id: 0ysRYbBr2NI
- url: https://www.youtube.com/watch?v=0ysRYbBr2NI
- duration: 30:51
- classification: MULTI-STRATEGY

## Summary

This video teaches Smart Money Concepts (SMC) and Inner Circle Trader (ICT) methodology as a framework for identifying institutional trading activity and institutional entry zones. The course covers trend structure analysis (BOS and CHOCH), Fair Value Gaps as entry setups, Order Blocks as support/resistance zones, liquidity pool concepts, and premium/discount pricing zones using Fibonacci. These concepts are presented as tools to align retail trading with institutional activity.

## Instruments and timeframes stated
- markets: NOT STATED
- timeframes: "4-hour or H1 time frames" mentioned as preference [28:00], also mentions "five-minute chart" [11:00], "one-hour timeframe or zoom in further on the 15-minute chart" [29:30]; speaker states "feel free to use lower or higher timeframes based on your preference" [28:00]
- sessions/hours: NOT STATED

## Strategy 1: Fair Value Gap Trade

### Indicators and settings
- Fair Value Gap: defined as imbalance between three consecutive candles where "the price movement doesn't have a Fair Value Gap, as the previous candle's high level has counterbalanced the low level of the third candle" [08:00]; requires "a set of three candles characterized by heavy buying or selling in the same direction" [07:30] with "a gap will be formed between the first candle's wick and the wick of the last candle" [08:00]
- Entry trigger location: gaps that "coincide with a break in market structure caused by an impulsive move, or a change of character" [08:15]
- Fibonacci retracement: optional use of "50% level can serve as an alternative entry point" [10:30]
- Fibonacci levels 50%, 61.8%, 78.6% mentioned as refinement options [17:15]

### Context / bias filter
Market must be trending and must experience "a break in market structure" or "a change of character" before the FVG can be considered valid [08:15]. For bullish setup: "market in an uptrend...followed by a pullback and another impulsive move that breaks the previous swing high" [09:15]. For bearish setup: "market breaks below a significant swing low, the market structure shifts lower...indicating potential short opportunities" [08:45]. Speaker states "you can anticipate the price to return to these Fair Value Gaps before continuing in the same direction as the impulse move" [10:00].

### Entry trigger
"You simply wait for the price to reach the area of interest and then look for a trigger, targeting a trend continuation" [10:15]. Retracement into the FVG after the impulsive move that created it.

### Stop loss
NOT STATED

### Take profit / exit
"Targeting a trend continuation" [10:15]. Price is expected to "return to these Fair Value Gaps before continuing in the same direction as the impulse move" [10:00]. Exit point not mechanically specified.

### Invalidation / skip conditions
NOT STATED explicitly. Implied: FVGs not aligned with BOS/CHOCH may be invalid; if price does not retrace to FVG, setup is voided.

### Claimed performance
NONE CLAIMED. Speaker only states the concept theoretically: "the market will eventually come back to these inefficiencies in the market before continuing in the same direction" [07:15].

### Vagueness log
1. UNDEFINED-RULE: What constitutes "heavy buying or selling" - no percentage, volume, or candle-size parameter given
2. UNDEFINED-RULE: "Look for a trigger" - what specific trigger condition enters the trade is not defined
3. UNDEFINED-PARAM: Stop loss price is not stated
4. UNDEFINED-PARAM: Take profit target or exit rule is not stated
5. UNDEFINED-RULE: How to determine if FVG is "high probability" vs lower probability
6. SUBJECTIVE: "You can anticipate the price to return" - no rule for if price fails to return to FVG

### Mechanizability
PARTIAL. The FVG pattern itself is mechanically identifiable (three-candle no-wick-overlap structure), and the Fibonacci 50% level is computable. However, the entry trigger ("look for a trigger"), stop loss, and exit are undefined. An implementation would require inventing rules for: what counts as a valid retracement entry, where to place stops, and where to exit. The core pattern is detectable but the full trade logic is incomplete.

---

## Strategy 2: Order Block Trade

### Indicators and settings
- Bullish Order Block: "the last down candle or series of down candles before an upward impulse price move" [12:30]; "will act as a support for the price to run higher" [12:30]
- Bearish Order Block: "the last up candle or series of up candles before a downward impulse price move" [12:45]; "will act as a resistance for the price to run lower" [13:00]
- FVG alignment: "When an Order Block forms with a Fair Value Gap to its right, this makes it a high probability Order Block" [14:30]. "When an Order Block does not have a Fair Value Gap to its right, this makes it a low probability Order Block, and the price tends to run the stops below or above the Order Block" [14:45]
- Fibonacci refinement: "Fibonacci retracement levels can be used, particularly between the 50%, 61.8% and 78.6% levels" [17:15]; "you may focus on the candle body or include the wick as well" [17:30]

### Context / bias filter
"Order blocks should not be identified everywhere on the charts, but rather in specific locations. You want to enter trades in areas where price retraces back into previous broken swing areas, providing the best risk-reward scenarios" [13:00]. Order block must occur after "a break of structure" or "change of character" [14:30-15:30]. Context example: "The recent market structure indicates an uptrend. Price formed a new swing high, declined, then formed a swing low. Prices then rallied again to exceed the previous high (making a higher high). This a BOS" [16:15].

### Entry trigger
"We then look for a retracement back into the area where the price broke out, which serves as a potential entry point" [13:30]. For bullish: "consolidation or candle formation where buyers take control, absorbing the selling pressure at the bottom. This leads to a breakout above a previous swing high. We then look for a retracement back" [13:15]. For bearish: "wait for price to retrace back into the release point or the area just before the move occurred. This becomes an opportunity to enter short trades" [13:30].

### Stop loss
For bearish order block trade: "placing the stop loss above the swing high" [13:30]. For bullish order block trade: stop implied below but NOT EXPLICITLY STATED.

### Take profit / exit
"You target these order blocks for continuation trades in the direction of the previous trend" [14:15]. Exit is implied as trend continuation but NOT SPECIFIED mechanically.

### Invalidation / skip conditions
"Low probability Order Block" occurs when "an Order Block does not have a Fair Value Gap to its right, and the price tends to run the stops below or above the Order Block" [14:45], implying setup is voided or has lower probability.

### Claimed performance
NONE CLAIMED

### Vagueness log
1. UNDEFINED-RULE: "Buyers take control" - what specific price action or volume defines this
2. UNDEFINED-PARAM: Stop loss for bullish order blocks not stated
3. UNDEFINED-PARAM: Take profit target/exit level not stated
4. UNDEFINED-RULE: "High probability" vs "low probability" defined only by FVG presence, but no other criteria given
5. SUBJECTIVE: When to use candle body vs include wick for Fibonacci is discretionary ("Depending on the context")

### Mechanizability
PARTIAL. Identifying the last candle before an impulse is mechanically possible (compare consecutive candles' direction). Identifying a retracement is mechanically possible. However, entry trigger ("look for retracement"), stop loss for bullish, and profit target are not specified. FVG alignment rule can be coded but is presented as a probability filter, not a hard invalidation rule.

---

## Strategy 3: Break of Structure (BOS) and Change of Character (CHOCH)

### Indicators and settings
- Break of Structure (BOS): "a significant price movement that surpasses a level of support or resistance on a chart, in the direction of the previous trend" [03:15]. "A BOS is simply a break above a previous higher high in an uptrend, or a break below a lower low in a downtrend" [03:30]. Uptrend BOS: "you mark the most recent swing high, and if you have another impulse move closing above this point, with several candles, then you found a BOS" [03:45]. Downtrend BOS: "you mark the most recent swing low, and if you have another move closing below this low, with several candles, again, you have found a BOS" [04:00]
- Change of Character (CHOCH): "represents a trend reversal in the market after a break of highs or lows" [04:15]. "A sudden and significant shift in the price action of a market" [04:30]. Example: "market that has been in a downtrend, making lower highs and lower lows. Once the price breaks above this previous major swing high, this is a change of character that signals a possible reversal of the downtrend" [04:30-05:00]

### Context / bias filter
BOS indicates trend continuation; CHOCH indicates trend reversal. Speaker states: "BOS means continuation in market structure, CHOCH means reversal" [06:00]. BOS is identified by continuing higher highs/lower lows; CHOCH is identified by reversal of that pattern.

### Entry trigger
After BOS: wait for trend to continue. After CHOCH: expect reversal and prepare to trade the new trend direction. No specific entry trigger price stated beyond the break itself.

### Stop loss
NOT STATED

### Take profit / exit
NOT STATED

### Invalidation / skip conditions
NOT STATED

### Claimed performance
NONE CLAIMED

### Vagueness log
1. UNDEFINED-RULE: "Impulse move" - what defines an impulse move, no candle-count or volatility threshold specified
2. UNDEFINED-RULE: "Several candles" - how many candles constitute "several"
3. UNDEFINED-PARAM: Entry price for trades based on BOS/CHOCH not specified
4. UNDEFINED-PARAM: Stop loss not stated
5. UNDEFINED-PARAM: Take profit target not stated
6. SUBJECTIVE: "Significant shift in price action" for CHOCH is not quantified

### Mechanizability
PARTIAL. Identifying swing highs/lows is mechanically possible. Identifying breaks above/below previous swings is mechanically possible. However, "impulse move," "several candles," and "significant shift" are subjective. The framework identifies trend structure but does not provide complete entry/exit rules for trading.

---

## Strategy 4: Liquidity-Based Entry Framework

### Indicators and settings
- Liquidity definition: "Liquidity primarily refers to the presence of orders at various price levels. These orders influence the price movements, often causing highs and lows in the market to be breached" [18:15]
- Liquidity points: "older highs and previous lows as liquidity points. Equal highs and equal lows are other liquidity areas. Liquidity can be found along trend lines, within chart patterns, at support and resistance levels" [18:30-18:45]
- Buy-side liquidity: "buy stop orders, which are placed above the resistance level" [21:00]; "activation of buy stop orders and the triggering of stop-loss orders lead to an influx of buying liquidity" [21:15]
- Sell-side liquidity: "sell stop orders...waiting to be triggered if the market continues to decline. When the market pushes lower, these sell stops and stop-loss orders will contribute to selling liquidity" [21:45-22:00]

### Context / bias filter
Market must be in a trading range or structure where liquidity clusters are identifiable. The framework assumes: "for big institutions, opening large orders in the market requires reaching these liquidity points" [22:30]. Speaker emphasizes understanding where "stop-loss orders placed by buyers" sit below support and "stop losses of sellers" sit above resistance [21:00].

### Entry trigger
"By understanding these dynamics, you can incorporate this knowledge into your trading strategy" [23:00] - entry trigger not explicitly mechanized. Implied: enter when institutional players are likely to push through liquidity clusters, but specific trigger price not given.

### Stop loss
NOT STATED explicitly. Framework suggests understanding where opposing liquidity clusters, implying stops should be placed there, but no specific rule given.

### Take profit / exit
NOT STATED

### Invalidation / skip conditions
NOT STATED

### Claimed performance
NONE CLAIMED

### Vagueness log
1. UNDEFINED-RULE: How to identify where liquidity is concentrated beyond "previous lows," "equal highs," "support/resistance" - no quantitative method given
2. UNDEFINED-PARAM: Entry price for a liquidity-based trade not stated
3. UNDEFINED-PARAM: Stop loss price not stated
4. UNDEFINED-PARAM: Take profit not stated
5. SUBJECTIVE: When institutions will "push through" liquidity - timing is not mechanized
6. UNDEFINED-RULE: How to distinguish "old" liquidity from current liquidity, no age parameter given

### Mechanizability
DISCRETIONARY. This is a conceptual framework for understanding market structure, not a complete trading strategy. Identifying support/resistance levels is mechanically possible, but the framework does not provide rules for when to enter, where to stop, or when to exit based on liquidity concepts.

---

## Strategy 5: Premium/Discount Trade

### Indicators and settings
- Fibonacci 50% level: Mark "a range, or a swing, using a Fibonacci retracement with only the 50% level marked" [23:45]
- Premium: "higher 50% of the range" [24:15]; "when you aim to sell when prices are in the premium range, meaning you sell at higher prices" [24:15]
- Discount: "lower 50% of the range" [24:15]; "when prices are in the discount range, which corresponds to the lower 50% of the range" [24:30]
- Application: "If you're looking for a long entry, you should focus on areas that are not in a premium or above the 50% Fibonacci level" [25:00]

### Context / bias filter
Use after identifying a break of structure or change of character. Apply Fibonacci "from the low to the high of that range" after a BOS [24:45], or "from the high to the low" if looking to short in premium [25:30]. Speaker states: "price tends to trend and respect premium and discount in the longer term rather than in the short to medium term" [25:45].

### Entry trigger
"If you have a fair value gap or an order block right here, above the fair value line, you wouldn't consider it for a long entry. Instead, you would concentrate on this area for potential long positions" [25:00]. For shorts: "if you observe a shift in market structure, a change of character, followed by a retracement, you would be interested in shorting above the middle line" [25:15].

### Stop loss
NOT STATED

### Take profit / exit
NOT STATED

### Invalidation / skip conditions
Speaker warns: "being overly reliant on it can cause you to miss good quality trade setups just because they aren't in premium or discount" [25:45], implying the filter should not be used as hard invalidation.

### Claimed performance
NONE CLAIMED

### Vagueness log
1. UNDEFINED-RULE: Which "range or swing" to apply Fibonacci - what makes a valid selection vs. an arbitrary one
2. UNDEFINED-PARAM: Entry price within the discount zone not specified
3. UNDEFINED-PARAM: Stop loss not stated
4. UNDEFINED-PARAM: Take profit not stated
5. UNDEFINED-PARAM: Timeframe context - speaker states it works better "longer term" but no threshold given
6. SUBJECTIVE: "Better" entry points within premium/discount zone not quantified

### Mechanizability
PARTIAL. Fibonacci 50% calculation is mechanically precise given endpoints. However, the framework is presented as a filter/confluencer, not a standalone strategy. Choosing which range to apply the tool to is discretionary. Entry, stop, and exit are not mechanized.

---

## Strategy 6: Mitigation Trade

### Indicators and settings
- Mitigation definition: "the process of reducing losses or offsetting unfavorable positions in the market" [26:15]
- Trigger condition: "break in market structure or a change of character, such as breaking the previous higher low, it indicates that more sellers are entering the market" [26:30-27:00]
- Institutional behavior: "Due to the size of their orders, they can't buy or sell randomly at any given level. They often need more time and multiple revisits to accumulate or distribute their positions" [27:00]

### Context / bias filter
Must have an uptrend with break of structure to lower lows indicating change in sentiment [26:15-27:00]. Example: "let's consider this upward trend, it means there are buy orders pushing the price higher. When we see a break in market structure or a change of character, such as breaking the previous higher low, it indicates that more sellers are entering the market" [26:15-27:00]. Speaker states institutions may need to "return to the previous level or even slightly higher before continuing the downward move" [27:30].

### Entry trigger
After break of structure: "If this level gets violated to the downside, we can expect a potential return to this area, possibly slightly above it, before the market continues its downward move. Once we witness this break, indicated by a strong candle, we can start looking for potential selling setups" [28:30-29:00]. On pullback: "After breaking the previous level, you would anticipate a retracement to the upside. You'll often see bullish momentum on lower timeframes, inducing traders to go long...look for short opportunities. In this case, you are capitalizing on the market's manipulation" [29:30-30:00].

### Stop loss
NOT STATED explicitly

### Take profit / exit
"continue the downward move" [27:00] - vague, no specific target given

### Invalidation / skip conditions
NOT STATED

### Claimed performance
NONE CLAIMED

### Vagueness log
1. UNDEFINED-RULE: "Strong candle" - what defines strength (close position, range, volume)
2. UNDEFINED-PARAM: Entry price for the short after mitigation move not specified
3. UNDEFINED-PARAM: Stop loss not stated
4. UNDEFINED-PARAM: Take profit target not stated
5. UNDEFINED-RULE: "Possibly slightly above it" - how much above the previous level, no range given
6. SUBJECTIVE: "Bullish momentum" on lower timeframe - what constitutes momentum

### Mechanizability
PARTIAL. The concept is based on identifying BOS/CHOCH (mechanically possible) and anticipating a retracement (mechanically identifiable when it occurs). However, entry trigger, stop loss, and exit are not specified. The framework assumes institutional behavior but does not quantify entry conditions or exits.

---

## Notable claims and caveats

**Risk and drawdown**
- Speaker emphasizes repeatedly that "don't think smart money have perfect entries or strategies. They are susceptible to losses, as we are" [27:00]
- Warns against over-reliance on premium/discount filter: "being overly reliant on it can cause you to miss good quality trade setups" [25:45]
- Critical caveat at end: "now, all these smart money concepts will help you to read the market better and make better decisions. But, they are missing one important piece of the puzzle, and that is the volume. Trading without volume is one it is one of the biggest mistakes you could make" [30:00-30:15]

**Costs and friction**
- Never mentions commission, spread, slippage, or transaction costs
- Assumes frictionless execution in all examples

**Performance claims**
- No win rate, R multiple, or profit claims stated
- Only theoretical assertions: "the market will eventually come back to these inefficiencies" [07:15]
- Encourages backtesting: "I highly encourage you to watch one of these trading courses next, to learn more about how to add the volume component into your strategies...start studying historical market data and conduct your backtest" [23:00, 30:15]
