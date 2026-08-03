# My Complete Price Action System (I Only Use These Strategies Now)

- video_id: 1BA9pq7v0SI
- url: https://www.youtube.com/watch?v=1BA9pq7v0SI
- duration: 29:19
- classification: MULTI-STRATEGY

## Summary

This video presents nine distinct pure price action strategies that use no technical indicators. The speaker covers candlestick-based patterns (engulfing momentum, long wick engulfing), breakout strategies (buildup, no retest, trap detection), structural analysis (over and under pattern, weak break of structure), supply/demand zone trading, and momentum analysis. Each strategy is grounded in supply-demand imbalance psychology and market structure, focusing on price action and volume confirmation.

## Instruments and timeframes stated
- markets: NOT STATED (references "all markets and all time frames" for bull/bear traps [06:30])
- timeframes: Strategies work on all timeframes [06:30]
- sessions/hours: NOT STATED

## Strategy 1: Engulfing Momentum Candlestick

### Indicators and settings
- Pattern: Large candle fully engulfs the body of previous two candles [00:00-00:30]
- No additional indicators
- Volume: High trading volume ideally [02:00-02:30]

### Context / bias filter
Should occur at support area (for bullish pattern) or resistance area (for bearish pattern) [01:00]. Should ideally be accompanied by a clear prevailing trend before the pattern [00:30-01:00]. At demand zone for bullish engulfing, at supply zone for bearish engulfing [01:00].

### Entry trigger
Large candle that completely covers the range of previous 2 candles [00:00-00:30]. For bullish: "buyers have overwhelmed the sellers, pushing the price up and covering the range of the previous 2 candles" [01:30]. For bearish: "sellers have come in strong" [01:30].

### Stop loss
NOT STATED

### Take profit / exit
"Please wait for the candle to close, to confirm the signal" [02:30]. Do not prematurely react [02:30].

### Invalidation / skip conditions
Candle must close as engulfing pattern; if it does not close that way, signal is false [02:30].

### Claimed performance
NONE CLAIMED

### Vagueness log
1. UNDEFINED-PARAM: "High trading volume" - no threshold specified [02:00-02:30]
2. UNDEFINED-RULE: What constitutes "a clear trend" before pattern is not defined [00:30-01:00]
3. UNDEFINED-RULE: "Support area" and "resistance area" are not defined as computable price levels [01:00]
4. UNDEFINED-RULE: "Demand zone" and "supply zone" lack precise definitions [01:00]
5. UNDEFINED-PARAM: Stop loss NOT STATED
6. UNDEFINED-PARAM: Take profit NOT STATED
7. SUBJECTIVE: Whether volume is "ideally" high enough is subjective judgment

### Mechanizability
PARTIAL. Identifying the engulfing candle is straightforward: compare current candle body to previous two candles' bodies and check if current fully covers both. However, the volume condition is undefined, location context (support/resistance/zone) is not precisely defined, and stop loss / take profit are completely missing, leaving trade management to assumption.

## Strategy 2: Breakout Buildup

### Indicators and settings
- Consolidation pattern: Price moves in narrow range, tight consolidation [03:30-04:00]
- Volume: Decreases during buildup phase [04:00-04:30]
- Pattern: "Coiling" motion, price hugging support/resistance level [04:30-05:00]

### Context / bias filter
Occurs during accumulation (smart money buying) or distribution (smart money selling) phases [03:30]. Market shows no clear winner between buyers and sellers initially [03:30-04:00]. Before strong uptrend or downtrend in market. Setup is stronger if it occurs near a resistance level after a strong uptrend [05:30].

### Entry trigger
"Strong price move out of the coiling pattern" [05:00-05:30]. "Breakout can happen in either direction, but typically follows the prevailing trend or the pressure from the dominant market side" [05:15-05:30]. Confirmation: "price action signal closing well beyond the level, or an increase in trading volume that supports the direction of the breakout" [05:30-06:00].

### Stop loss
NOT STATED

### Take profit / exit
NOT STATED (though references "price moving beyond the level" [05:30])

### Invalidation / skip conditions
"Not every buildup leads to a breakout. Sometimes, the price might just hover around the level and then drift away without any significant movement" [05:30-06:00]. Therefore, wait for the breakout before making a trade [05:30-06:00].

### Claimed performance
NONE CLAIMED

### Vagueness log
1. UNDEFINED-PARAM: "Narrow range" - width or percentage range not specified [03:30-04:00]
2. UNDEFINED-PARAM: "Decreases" in volume - no threshold [04:00-04:30]
3. UNDEFINED-RULE: "Accumulation" and "distribution" phases - how to identify them is not explicitly stated here
4. UNDEFINED-PARAM: "Tight consolidation" - tightness threshold not specified [03:30-04:00]
5. UNDEFINED-RULE: "Prevailing trend" - how identified not stated in this section [05:15]
6. UNDEFINED-PARAM: "Strong price move" - magnitude threshold not stated [05:00]
7. UNDEFINED-PARAM: "Increase in trading volume" - how much increase is not defined [05:30-06:00]
8. UNDEFINED-PARAM: Stop loss NOT STATED
9. UNDEFINED-PARAM: Take profit NOT STATED

### Mechanizability
PARTIAL. The skeleton of the pattern (narrowing range, volume decrease, then breakout) can be coded with OHLC and volume data. Range width threshold, volume decrease percentage, and what constitutes "strong" move would need to be assumed, and all exit rules are missing.

## Strategy 3: Bull and Bear Trap Recognition

### Indicators and settings
- False breakout: Price moves beyond obvious level but quickly reverses [06:30-07:00]
- Volume: Low volume on breakout is a warning sign [06:30-07:00]
- Price action: Observation of reversal pattern immediately after breakout [07:00]

### Context / bias filter
Occurs in ranges or when market lacks clear trend [07:30-08:00]. Multiple retests of a level suggest weakness [08:00-08:30].

### Entry trigger
This is primarily a RECOGNITION strategy to AVOID trades, not to ENTER them. For bull trap: "Price pushing through a resistance level but then quickly pulling back and closing below it" [06:30-07:00]. For bear trap: "Price might dip below a support level, only to rebound and close above it" [07:00-07:30].

### Stop loss
NOT STATED. (Strategy is defensive: "be wary" and avoid the trap)

### Take profit / exit
NOT STATED

### Invalidation / skip conditions
A genuine breakout might initially retreat back to the breakout point "but it usually won't penetrate back through it" [08:00-08:30]. Multiple retests suggest the breakout lacks strength [08:00-08:30].

### Claimed performance
NONE CLAIMED

### Vagueness log
1. UNDEFINED-PARAM: "Low volume" - no threshold specified [06:30]
2. UNDEFINED-RULE: "Lacks conviction" - not defined as computable [06:30-07:00]
3. UNDEFINED-RULE: "Obvious level" - what makes a level obvious is not specified [06:30]
4. UNDEFINED-RULE: "Clear trend" - how to identify is not stated [07:30]
5. UNDEFINED-PARAM: "Quickly pulling back" - timing threshold not specified [06:30]
6. UNDEFINED-PARAM: "Multiple retests" - how many constitutes multiple is not defined [08:00]
7. SUBJECTIVE: Entry/exit rules are based on avoidance rather than entry timing

### Mechanizability
PARTIAL. Detecting a price move beyond a level followed by reversal is mechanically observable. However, "low volume," "quick reversal," "obvious level," and "multiple retests" require threshold assumptions. Since this is a recognition strategy to avoid trades rather than enter them, it lacks positive entry/exit rules.

## Strategy 4: Long Wick Engulfing Candlestick

### Indicators and settings
- Pattern: Large body with long wick extending far beyond body's edges [08:30-09:00]
- Engulfing: Body is larger than previous candle's body [09:00]
- Wick placement: Upper wick (rejection of highs) or lower wick (rejection of lows) [09:00-09:30]
- Volume: NOT STATED (implied important but not quantified)

### Context / bias filter
Look for these patterns at major resistance or support levels [11:00]. Bullish pattern at key support level might signal upward reversal [11:00-11:30]. Bearish pattern at key resistance might signal downward reversal. Pattern more significant if confirmed by volume.

### Entry trigger
Upper wick: "Buyers tried to push the price up, but the overwhelming number of sellers at that level rejected this move" [09:30-10:00]. Lower wick: "Sellers drove the price down, but buyers stepped in, finding the lower price attractive, thus pushing the price back up, showing rejection of lower prices" [10:00-10:30]. If body also engulfs previous candle, momentum is intensified [10:00-10:30].

### Stop loss
NOT STATED

### Take profit / exit
NOT STATED

### Invalidation / skip conditions
Pattern is more reliable when accompanied by high volume, though not always required. Pattern validity depends on location (support/resistance level) [11:00].

### Claimed performance
NONE CLAIMED

### Vagueness log
1. UNDEFINED-RULE: "Major resistance or support levels" - how to identify these is not stated [11:00]
2. UNDEFINED-PARAM: "Long wick" - minimum length not specified [08:30-09:00]
3. UNDEFINED-PARAM: "Large body" - size threshold not specified [09:00]
4. UNDEFINED-PARAM: Volume confirmation - level not specified [02:30]
5. UNDEFINED-PARAM: Stop loss NOT STATED
6. UNDEFINED-PARAM: Take profit NOT STATED
7. SUBJECTIVE: "Significant" shift in sentiment is observed visually, not measured [10:30]

### Mechanizability
PARTIAL. Identifying the candle structure (wick length, body size, engulfing) is computable from OHLC data. However, the "major" resistance/support level identification requires context, volume confirmation is undefined, and all exit rules are missing.

## Strategy 5: No Retest Breakout

### Indicators and settings
- Breakout with momentum: Price breaks above resistance and doesn't return to test it [11:30-12:00]
- Volume: NOT EXPLICITLY STATED but "intense momentum" implied [11:30]
- Strong, sustained move after breakout [12:00-12:30]

### Context / bias filter
Prior strong uptrend establishing resistance level. Many traders are watching the same resistance level [12:00]. Some waiting to buy after breakout, others waiting for retest [12:00-12:30].

### Entry trigger
"Price breaks through the resistance level with strong momentum and doesn't retest" [12:30]. This move creates "fear of missing out" in traders who were waiting for the retest [12:30-13:00].

### Stop loss
NOT STATED explicitly, though "point of pain" at the breakout level is mentioned as psychologically important [13:00-13:30]. This is where traders in losing positions might be forced to cover.

### Take profit / exit
NOT STATED. Video mentions the "point of pain" (the initial breakout level) as significant because "return to the breakout level will often trigger a surge in trading activity" [14:00], but this is not positioned as a take profit target.

### Invalidation / skip conditions
If price does eventually return to the initial breakout level (the "point of pain"), the previous signal is invalidated [13:00-14:00]. At that point, price reaction "won't be that explosive as the first one" [14:00-14:30].

### Claimed performance
NONE CLAIMED

### Vagueness log
1. UNDEFINED-PARAM: "Strong momentum" - magnitude or velocity threshold not specified [11:30-12:00]
2. UNDEFINED-RULE: "Intense momentum" - not quantified [11:30]
3. UNDEFINED-PARAM: Stop loss NOT STATED
4. UNDEFINED-PARAM: Take profit NOT STATED
5. UNDEFINED-RULE: "Point of pain" location (initial breakout) is clear, but how to trade it is not specified [13:00]
6. SUBJECTIVE: "Fierce" or "explosive" price action is observed visually, not measured

### Mechanizability
PARTIAL. Detecting a price breakout and checking whether it retests the breakout level is computable. However, "strong momentum" is not numerically defined, stop loss is missing, take profit is missing, and whether to re-enter at the "point of pain" is unclear.

## Strategy 6: Multiple Rejection Wicks + Color Change

### Indicators and settings
- Pattern: Multiple consecutive candles at similar price level [14:30-15:00]
- First candle: Bullish with long upper wick [14:30-15:00]
- Second candle: Bearish with similar long upper wick [14:30-15:00]
- Color change: Bullish to bearish indicates reversal of momentum [14:30]

### Context / bias filter
Pattern is stronger if it appears at a known resistance level [15:30-16:00]. Traders often place stops around these levels, amplifying the move [15:30-16:00].

### Entry trigger
Occurrence of two consecutive candles with long upper wicks at the same price level, with color change from bullish to bearish [14:30-15:00]. "The repeated rejection at this price level signifies that the supply has surpassed the demand, possibly leading to a trend reversal or at least a significant pullback" [15:30-16:00].

### Stop loss
NOT STATED

### Take profit / exit
NOT STATED

### Invalidation / skip conditions
Pattern appears to be a confluence signal; if resistance level does not hold, pattern loses significance.

### Claimed performance
NONE CLAIMED

### Vagueness log
1. UNDEFINED-PARAM: "Multiple" consecutive candles - how many required is not specified [14:30]
2. UNDEFINED-PARAM: "Similar price level" - tolerance range not specified [14:30-15:00]
3. UNDEFINED-PARAM: "Long wick" - minimum length not specified [14:30]
4. UNDEFINED-RULE: "Known resistance level" - how to identify is not stated [15:30]
5. UNDEFINED-PARAM: Stop loss NOT STATED
6. UNDEFINED-PARAM: Take profit NOT STATED

### Mechanizability
PARTIAL. Detecting consecutive candles with wicks and color changes is computable from OHLC data. However, exact thresholds for "similar level," "multiple," and "long wick" would need to be assumed. Stop loss and take profit are missing entirely.

## Strategy 7: Supply/Demand Zone Trading

### Indicators and settings
- Zones: Identified as areas where price was previously supported (demand) or resisted (supply) [17:00-17:30]
- Volume: Naturally higher at these zones, but no specific threshold stated
- Trend context: Uptrend vs downtrend determines which zones to trade

### Context / bias filter
During uptrends: "demand levels are respected, and supply zones are taken out" [17:30]. During downtrends: "supply zones are respected, and demand zones are taken out" [19:00]. Zones are defined by prior price action at those levels.

### Entry trigger
Uptrend: "When price retraces to a lower level (a demand zone), it finds strong buying interest" [17:30]. Buy on dips at demand zones [18:00]. Downtrend: "When the price goes up to test a previous high (a supply zone), it often finds strong selling interest" [19:00]. Sell rallies at supply zones [19:30].

### Stop loss
NOT STATED

### Take profit / exit
NOT STATED

### Invalidation / skip conditions
Uptrend: Avoid trading supply zones; supply zones are "often breached" in strong uptrends [18:00-18:30]. Downtrend: Avoid trading demand zones; they "start to break" as downtrend deepens [19:00-19:30]. "During uptrends, don't even try to trade supply zones. Focus only on buying on dips, at demand zones" [18:30]. "During downtrends, ignore the demand zones. Focus only on selling at supply zones" [19:30].

### Claimed performance
NONE CLAIMED

### Vagueness log
1. UNDEFINED-RULE: "Demand zone" - exact definition or size of zone not specified [17:30]
2. UNDEFINED-RULE: "Supply zone" - exact definition or size of zone not specified [17:30]
3. UNDEFINED-PARAM: "Dips" - magnitude or percentage pullback not specified [18:00]
4. UNDEFINED-PARAM: "Rallies" - magnitude or percentage retracement not specified [19:00]
5. UNDEFINED-PARAM: Stop loss NOT STATED
6. UNDEFINED-PARAM: Take profit NOT STATED
7. SUBJECTIVE: Trend identification (uptrend vs downtrend) likely relies on visual assessment

### Mechanizability
PARTIAL. The concept can be coded: identify prior resistance and support levels, then wait for price to retrace to them in context of current trend. However, the exact definition of a "zone" (how wide?), what constitutes a "dip" or "rally" (how much?), and all exit rules are missing.

## Strategy 8: Over and Under Pattern

### Indicators and settings
- Structure break: Price breaks below previous major low (downtrend) or above previous high (uptrend) [20:30-21:00]
- Formation: After breaking structure, price makes a lower high (uptrend scenario) or higher low (downtrend scenario) [20:30-21:00]
- Trend context: Indicates weakening or reversal of existing trend

### Context / bias filter
Pattern signals trend structure is being violated. In uptrend: price fails to maintain higher highs [20:30-21:00]. In downtrend: price fails to maintain lower lows [21:30].

### Entry trigger
Uptrend scenario: Price drops below previous major low, then makes a lower high [20:30-21:00]. "This unexpected change often leads to uncertainty and a shift in sentiment" [21:30-22:00]. Downtrend scenario: Prices push above previous low, but then form a higher high [21:30].

### Stop loss
NOT STATED

### Take profit / exit
NOT STATED

### Invalidation / skip conditions
Pattern indicates the prevailing structure is broken. Once a lower high is made in an uptrend or higher low is made in a downtrend, the prior trend context is invalidated.

### Claimed performance
NONE CLAIMED

### Vagueness log
1. UNDEFINED-RULE: "Previous major low" - what makes a low "major" is not specified [20:30]
2. UNDEFINED-RULE: "Previous major high" - what makes a high "major" is not specified [21:00]
3. UNDEFINED-PARAM: "Lower high" - how much lower is not specified [21:00]
4. UNDEFINED-PARAM: "Higher low" - how much higher is not specified [21:30]
5. UNDEFINED-PARAM: Stop loss NOT STATED
6. UNDEFINED-PARAM: Take profit NOT STATED

### Mechanizability
PARTIAL. Identifying prior highs/lows and comparing subsequent price extremes is computable. However, the definition of "major" is subjective, the threshold for "lower" or "higher" is not specified, and stop/take profit are completely missing.

## Strategy 9: Weak Break of Structure

### Indicators and settings
- Pattern: Price marginally surpasses previous high or low, but quickly retraces [23:30-24:00]
- Context: Occurs at points where supply/demand balance is delicate [24:00]
- Momentum: Weak conviction, lack of follow-through

### Context / bias filter
Typically occurs at key resistance/support levels [24:00-24:30]. Single weak break may not be meaningful, but consecutive weak breaks form a pattern [24:30-25:00]. Consecutive weak breaks often precede a stronger move in opposite direction [25:30].

### Entry trigger
Price level has historically acted as resistance; price approaches and marginally breaks above it but quickly retraces [24:00-24:30]. Repeated: "if the market attempts to break a low multiple times but each time only succeeds marginally before retracing, it suggests a consistent lack of supply at lower price levels" [25:00-25:30].

### Stop loss
NOT STATED

### Take profit / exit
NOT STATED

### Invalidation / skip conditions
Single weak break is not meaningful; pattern requires multiple attempts [24:30-25:00]. Consecutive weak breaks suggest buyers are losing power (in uptrend scenario) and price will likely fall.

### Claimed performance
NONE CLAIMED

### Vagueness log
1. UNDEFINED-PARAM: "Marginally surpasses" - how small a move counts as marginal? Not specified [23:30-24:00]
2. UNDEFINED-PARAM: "Quickly retraces" - how fast? What time frame? Not specified [24:00]
3. UNDEFINED-PARAM: "Multiple times" - exact count not specified [25:00-25:30]
4. UNDEFINED-PARAM: Stop loss NOT STATED
5. UNDEFINED-PARAM: Take profit NOT STATED
6. SUBJECTIVE: "Strong" move in opposite direction is not quantified [25:30]

### Mechanizability
PARTIAL. Detecting a price move that slightly exceeds a level and then retraces is computable. However, the threshold for "marginal," the retracement timing, and the count of "multiple" attempts are undefined. Stop loss and take profit are entirely missing.

## Strategy 10: Momentum Gain vs Momentum Loss

### Indicators and settings
- Candle size: Consecutive candles getting larger = momentum gain [26:00-26:30]
- Candle size: Consecutive candles getting smaller = momentum loss [27:00-27:30]
- Volume confirmation: Increasing volume on larger candles = momentum gain; decreasing volume on smaller candles = momentum loss [28:30-29:00]

### Context / bias filter
Pattern occurs within trends [26:00-26:30]. Stronger signal if occurring after prolonged move at key resistance level [28:00]. Momentum gain suggests continuation; momentum loss suggests potential reversal or pause.

### Entry trigger
Momentum gain: "When you see consecutive candles getting larger and larger, this usually signals a momentum gain" [26:00-26:30]. "Each candle is getting larger and moving a greater distance per candle" [26:30-27:00]. Ride the wave during momentum gain [28:30].

### Stop loss
NOT STATED

### Take profit / exit
Momentum loss: "Candles start to decrease in size. This suggests that the movement in price is losing strength" [27:00-27:30]. "Be cautious" when seeing momentum loss [28:30].

### Invalidation / skip conditions
Momentum loss at key resistance level is strong indicator that trend might reverse or stall [28:00]. Volume confirmation is important: if candle sizes diminish but volume increases, it contradicts momentum loss signal [28:30-29:00].

### Claimed performance
NONE CLAIMED

### Vagueness log
1. UNDEFINED-PARAM: "Consecutive candles" - how many consecutive required? Not specified [26:00]
2. UNDEFINED-PARAM: "Getting larger and larger" - minimum size increase not specified [26:00-26:30]
3. UNDEFINED-PARAM: "Larger distance per candle" - exact threshold not specified [26:30]
4. UNDEFINED-PARAM: "Significant size decrease" - threshold not specified [27:00-27:30]
5. UNDEFINED-PARAM: Stop loss NOT STATED
6. UNDEFINED-PARAM: Take profit NOT STATED
7. SUBJECTIVE: "Be cautious" does not specify an action or exit level
8. UNDEFINED-RULE: How to interpret contradictions between candle size and volume trends

### Mechanizability
PARTIAL. Comparing consecutive candle sizes (close - open, or high - low) is straightforward and computable from OHLC data. Volume comparison is also possible. However, the threshold for what constitutes "getting larger" or "getting smaller" requires assumption, and there are no defined stop loss or take profit levels.

## Notable claims and caveats

The speaker claims these are "the best price action strategies" and states "I Only Use These Strategies Now" [00:00], implying personal validation, but provides no performance data, win rate, profit factor, or backtest results. No mention of transaction costs, spread, slippage, or commission is made throughout the video. No drawdown warnings or losing streak scenarios are discussed. The video emphasizes "pure price action" without indicators [00:00], but success depends heavily on subjective judgment of price levels, trend identification, volume levels, and pattern recognition. Volume is frequently mentioned as "confirmation" but thresholds are never quantified. The video assumes traders can identify support, resistance, and supply/demand zones visually, but provides no precise definition of these zones.
