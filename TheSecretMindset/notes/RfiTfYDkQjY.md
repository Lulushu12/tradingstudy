# Actually Profitable AVWAP - CPR - VSA Strategy (3 Rules Only)

- video_id: RfiTfYDkQjY
- url: https://www.youtube.com/watch?v=RfiTfYDkQjY
- duration: 29:39
- classification: MULTI-STRATEGY

## Summary
This video teaches three distinct trading strategies: Anchored VWAP for identifying trend pullbacks, Central Pivot Range (CPR) for market structure analysis and psychological levels, and Consecutive Candles Volume Spread Analysis (VSA) for trend-continuation pullback setups. Each strategy can be applied across multiple timeframes and emphasizes market structure, volume analysis, and confluence of signals. The strategies work best in trending markets and capitalize on the behavior of price around key support and resistance levels.

## Instruments and timeframes stated
- markets: NOT STATED
- timeframes: "all timeframes" [02:00], "daily charts" mentioned for VSA [24:30], "higher timeframes (4-hour and above)" recommended [24:30]
- sessions/hours: "market open" works best for CPR [13:30], "morning trades" versus "afternoon" mentioned [13:30]

## Strategy 1: Anchored VWAP Pullback Trading

### Indicators and settings
- Anchored VWAP: anchor point = high-volume bar [01:00], parameters NOT STATED
- VWAP bands: "typically set at one, or two standard deviations" [02:30], which standard deviations NOT SPECIFIED, upper band definition = bands above VWAP line, lower band definition = bands below VWAP line

### Context / bias filter
Strategy works best in trending markets [03:30]. Requires identification of clear uptrend or downtrend before setup is valid. VWAP is lagging indicator and works poorly in sideways or choppy markets [03:30-04:00]. Volume analysis must complement strategy to confirm strength of pullbacks [04:00].

### Entry trigger
In uptrend: Buy pullbacks when price pulls back to the Anchored VWAP line [01:30-02:00]. Price may pull back "to the VWAP lines, or even at the bands below the main line" [02:00]. In downtrend: Mirror opposite - sell pullbacks to VWAP. Look for rejection candles or price action signs that price is respecting VWAP as support/resistance [04:30-05:00]. Entry bar should show momentum - "relatively large candle body indicating strong buying pressure" [23:30] (referenced from VSA section but applicable to VWAP).

### Stop loss
"Place them beyond the recent swing high or low, on the other side of the VWAP" [05:00]. Specific distance NOT STATED.

### Take profit / exit
"Look at previous support or resistance levels, or at the next bands" [05:00-05:30]. Specific target levels NOT PRE-COMPUTED.

### Invalidation / skip conditions
NOT STATED. Market structure is sideways or choppy [03:30]. Pullback happens on low volume [04:15].

### Claimed performance
NONE CLAIMED.

### Vagueness log
1. High-volume bar: "exceptionally high volume" [01:00] not defined numerically or relative to period - UNDEFINED-PARAM
2. "Rejection candles" [04:30]: pattern characteristics NOT STATED - UNDEFINED-RULE
3. "Engulfing bars" [04:30]: exact definition and confirmation criteria NOT STATED - UNDEFINED-RULE
4. VWAP bands standard deviations: "one, or two standard deviations" [02:30] - which value to use NOT STATED - UNDEFINED-PARAM
5. "Trending market" vs "choppy market" [03:30]: no numerical definition of what constitutes each - SUBJECTIVE
6. Multiple timeframe approach [05:30]: specific rules for higher vs lower timeframe NOT STATED - UNDEFINED-RULE
7. Chart examples show visual anchoring points: "this bar with exceptionally high volume" [06:00, 06:30, 07:00] - trader visually identifies anchor, rule not mechanically computable - VISUAL-ONLY

### Mechanizability
PARTIAL. The skeleton (anchor at high volume, pull back to VWAP line, trade in direction of trend) is computable given OHLCV data. However, 4 critical gaps must be filled: (1) definition of "high volume" for anchor selection, (2) specific standard deviations for VWAP bands, (3) rejection/engulfing candle patterns, (4) how many bars back to compute pullback confirmation. The visual identification of "good" anchor points requires discretionary judgment.

## Strategy 2: Central Pivot Range (CPR) Trading

### Indicators and settings
- Central Pivot Range (CPR): calculation formula NOT STATED, consists of three lines [09:00], "pivot" and "two more lines above and below" [09:00]
- Daily CPR comparison: compares "today's CPR" to "yesterday's CPR" [10:00-10:30]

### Context / bias filter
Daily market structure bias set by comparing CPR level to previous day [10:00-12:30]. If today's CPR is higher than yesterday's = look to buy, market mood is positive [10:00-10:30]. If today's CPR is lower than yesterday's = look to sell, market mood shifted [10:30]. A rising CPR day-after-day = strong uptrend signal [11:00]. A falling CPR day-after-day = downtrend signal [11:00]. Market structure: wide CPR indicates "calm" market [09:30], narrow CPR indicates market "ready to sprint" [10:00].

### Entry trigger
In uptrend (CPR rising): "Buy the pullbacks to the CPR. The CPR acts as support" [12:30-13:00]. Price bounces at CPR. In downtrend (CPR falling): "Sell when price rallies to the CPR. The CPR becomes resistance" [13:00]. Entry requires price "to show its hand" - wait for confirmation signals [13:00-13:30]. More signs of confirmation = stronger trade [13:30].

### Stop loss
NOT STATED.

### Take profit / exit
NOT STATED.

### Invalidation / skip conditions
NOT STATED. Works best at market open [13:30], loses power as day goes on [13:30]. Accuracy diminishes by afternoon [13:30].

### Claimed performance
NONE CLAIMED.

### Vagueness log
1. CPR calculation: formula NOT STATED (appears to be standard three-line pivot calculation but never explicitly defined) - UNDEFINED-RULE
2. "Higher" or "lower" CPR: no quantification of threshold for deciding bias shift - SUBJECTIVE
3. "Wide" vs "narrow" CPR: no numerical threshold for width differentiation [09:30-10:00] - UNDEFINED-PARAM
4. Confirmation signals [13:30]: "more signs you see, the stronger your trade" but signs NOT SPECIFIED - UNDEFINED-RULE
5. Fresh CPR concept [17:00-18:30]: "Fresh CPR" defined as CPR not touched on given day, but exact candle-closure rules unclear ("full candlesticks form inside the CPR" [18:30]) - UNDEFINED-RULE
6. Price interaction with CPR: visual examples show bounces at drawn lines [06:00, 06:30, 07:00] - traders see visual chart, rule partially VISUAL-ONLY

### Mechanizability
PARTIAL. If CPR formula is assumed to be standard three-line pivot calculation (which is computable from OHLCV), the daily bias rule (compare today's CPR to yesterday's) is mechanical. However, multiple gaps prevent full automation: (1) CPR formula assumed not stated, (2) "wide" vs "narrow" threshold undefined, (3) confirmation signals undefined, (4) Fresh CPR touch detection rules ambiguous ("full candlesticks" criterion unclear), (5) timeframe optimization for market open unknown.

## Strategy 3: Consecutive Candles VSA (Pullback Entry)

### Indicators and settings
- Consecutive candles: defined as "red candles" (close < open) for downward moves [22:00], or "closes above its open" for up candles [24:00]
- Minimum consecutive candles required: Four or more [22:00], [24:00]
- Volume: "increase in volume on our entry bar" [23:30], "ideal scenario is to see the highest volume in the past bars" [23:30] - number of past bars NOT SPECIFIED
- Entry candle body: "relatively large candle body indicating strong buying pressure" [23:30]
- Entry candle wicks: "Low spread candles or those with wicks on both ends are generally avoided" [23:30]
- Moving averages (optional): 50-period and 200-period mentioned as example [26:30-27:00], specifically "if the 50-period moving average is above the 200-period one, it confirms an uptrend" [26:30-27:00]

### Context / bias filter
Market structure must be respected [21:30-22:00]. Uptrend defined by "higher highs and higher lows" [21:30-22:00]. Downtrend defined by "lower highs and lower lows" [21:30-22:00]. For long entry: price has not breached the last swing low in uptrend structure [22:30]. For short entry: price has not breached the last swing high in downtrend structure [24:00]. Strategy turns pullback into trend-continuation play [22:30].

### Entry trigger
Long entry: After four or more consecutive down days (red candles where close < open), enter on the next bullish bar showing momentum [23:00-24:00]. Volume on entry bar must increase, ideally "highest volume in the past bars" [23:30]. Short entry (mirror): After four or more consecutive up days, enter on the next bearish bar with increased volume [24:00-24:30]. Entry bar should have relatively large body, avoid low-spread or dual-wick candles [23:30].

### Stop loss
Long trades: NOT STATED. Short trades: "just above the high of the bearish setup bar" [24:30].

### Take profit / exit
NOT STATED.

### Invalidation / skip conditions
Works best in trending markets [24:30]. "In choppy markets, the consecutive up or down pattern may occur more frequently, but be less meaningful" [25:00]. Strategy less reliable in sideways/choppy markets [25:00]. Volume context matters: large volume on small price range might indicate "battle between buyers and sellers, rather than a clear directional move" [25:15-25:30], less ideal than volume spike with decisive price move [25:30].

### Claimed performance
NONE CLAIMED.

### Vagueness log
1. "Relatively large candle body" [23:30]: size threshold NOT SPECIFIED relative to prior candles or fixed measure - UNDEFINED-PARAM
2. "Highest volume in the past bars" [23:30]: number of past bars to reference NOT STATED - UNDEFINED-PARAM
3. "Low spread candles" [23:30]: definition (High-Low range relative to body) NOT STATED - UNDEFINED-PARAM
4. "Strong buying/selling pressure" [23:30]: no quantitative threshold - SUBJECTIVE
5. "Magnitude of moves diminishing" [26:00]: no percentage or fixed threshold for "diminishing" - SUBJECTIVE
6. "Decisive price move" [25:30]: definition NOT STATED - UNDEFINED-RULE
7. "Near recent support or resistance levels" [26:30]: proximity threshold NOT STATED - UNDEFINED-PARAM
8. Moving average confirmation [26:30-27:00]: described as "useful" but not required, conditional criteria NOT SPECIFIED - UNDEFINED-RULE
9. "Dynamic zone" of moving average [27:00-27:30]: exact price range definition of zone NOT STATED - UNDEFINED-RULE
10. Pullback "not too far" [27:30]: distance definition NOT STATED - UNDEFINED-PARAM

### Mechanizability
PARTIAL. The core skeleton (count N consecutive candles, wait for reversal candle on increased volume, trade in direction of trend) is mechanically computable. However, 7 significant gaps block full automation: (1) "relatively large" candle body threshold undefined, (2) number of past bars for volume comparison undefined, (3) "low spread" definition missing, (4) moving average "dynamic zone" not precisely defined, (5) "near" support/resistance proximity not quantified, (6) entry timing precision unclear for when to enter relative to reversal candle close, (7) stop loss missing for long trades.

## Notable claims and caveats
Video emphasizes that VWAP "is still a lagging indicator" and "can't predict future price movements with certainty" [03:00-03:30]. Strategy works best in trending markets; in sideways or choppy markets pullbacks may be unreliable [03:30-04:00]. Volume spikes on small price ranges may indicate indecision rather than directional momentum [25:15-25:30], making them less reliable. False breakouts can occur more frequently in choppy markets [28:30]. Video does NOT discuss transaction costs, spreads, slippage, or commission impact on any strategy.
