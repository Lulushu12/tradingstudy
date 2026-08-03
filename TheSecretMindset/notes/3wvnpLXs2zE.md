# I Tried Every Strategy, This Scalping Trading Course Changed Everything

- video_id: 3wvnpLXs2zE
- url: https://www.youtube.com/watch?v=3wvnpLXs2zE
- duration: 30:01
- classification: MULTI-STRATEGY

## Summary

This video presents six distinct scalping strategies for small account traders trading on lower timeframes (1m, 3m, 5m). Each strategy combines price action patterns (pin bars, inside bars, engulfing candles, power candles, tower formations) with supply/demand zone confluence. The core thesis is that smart money leaves recognizable price action signatures at key levels, and retail traders can exploit these by identifying specific candlestick patterns in combination with support/resistance zones and optional indicators like VWAP and volume.

## Instruments and timeframes stated

- markets: Examples shown on: Crude Oil, Apple, EUR/JPY, Tesla (stocks and forex implied)
- timeframes: 1-minute, 3-minute, 5-minute examples shown; speaker mentions can adapt strategies to 15m or higher for day trading/swing trading [29:15-29:30]
- sessions/hours: NOT STATED

## Strategy 1: Pin Bar + Inside Bar at Supply/Demand Zones

### Indicators and settings

- Candlestick patterns: Pin bar (long wick, small body), Inside bar (range fits inside prior candle's range)
- Supply/Demand zones: identified visually from prior price action (areas of "huge volumes of orders") [02:15-02:30]
- Volume: used qualitatively for confirmation

### Context / bias filter

"Supply and demand zones are areas of market where there is a lot of liquidity at the particular price" [02:15-02:30]. Price must approach or return to a supply/demand zone. "In scalping, candlesticks have very little value if you don't see them in the right price action context, namely near a supply or demand zone" [01:30-02:00]. Supply zone: "sellers outnumber buyers" [02:45-03:00]. Demand zone: "where buyers had previously stepped in and pushed the price higher" [07:45-08:00].

### Entry trigger

Pin bar followed by inside bar at supply/demand zone. For short at supply: "you place a sell stop order below the low of the pin bar with a stop loss above the high of the pin bar or above the supply zone" [03:15-03:30]. For long at demand: "a buy stop order above the high of the pin bar with a stop loss below the demand zone" [04:00-04:30]. "You simply mark the area containing the pin bar and the inside bar, and you trade the breakout of that area" [01:45-02:00].

### Stop loss

For sell: "stop loss above the high of the pin bar or above the supply zone" [03:15-03:30]. For buy: "stop loss below the demand zone" [04:00-04:30].

### Take profit / exit

"Even though it's a scalping setup, you target the next major demand level taking partial profits at minor ones" [03:15-03:30]. Implied: scale out at intermediate supply/demand zones before final target.

### Invalidation / skip conditions

"This combination forms quite often, but that doesn't mean all pin bars followed by an inside bar are valid trading signals" [01:30-02:00]. Only trade when pattern forms "near a supply or demand zone" [01:30-02:00]. NOT STATED: what conditions would invalidate an otherwise well-positioned pattern.

### Claimed performance

"If you back test pin bars and inside bars, and you take the trades at an area of supply or demand, you will notice they continuously produce consistent responses from the market. The odds are in your favor simply because you found the point of confluence in the market" [01:45-02:15] - qualitative claim, no numbers given.

### Vagueness log

1. UNDEFINED-PARAM: Supply/demand zone width/boundaries not specified
2. VISUAL-ONLY: Zone identification is manual chart inspection; no computable definition given for zone location or size
3. UNDEFINED-PARAM: Pin bar "wick length" - longer wick = more powerful [00:15-00:30] but no threshold stated
4. UNDEFINED-PARAM: Inside bar formation - "must completely fit within the range of the previous candle" [00:30-01:00] is computable, but how many inside bars can follow a pin bar? Examples show "multiple inside bars" [01:45-02:00] but no limit specified
5. UNDEFINED-PARAM: What constitutes "the next major demand level" for exit - intermediate vs final target not quantified
6. SUBJECTIVE: Freshness of zone (first touch vs multiple touches) affects reliability but is not stated as a rule

### Mechanizability

PARTIAL - Pin bar and inside bar formation can be computed (wick ratio, range containment), and supply/demand zones can be marked algorithmically (prior swing highs/lows), but zone boundaries and when to consider a zone "major" vs "minor" require manual definition or heuristic thresholds.

---

## Strategy 2: VWAP Rejection with Engulfing Pin Bar

### Indicators and settings

- VWAP (Volume Weighted Average Price): NOT STATED if daily, weekly, or intraday calculation; speaker specifies "added the daily VWAP on the 1-minute time frame" in one example [06:00-06:30]
- Engulfing pin bar: body completely covers previous candle body + contains a wick [04:30-05:15]

### Context / bias filter

"VWAP as a trend indicator. Price trading above the VWAP as the line rises shows that buyers are in control. And trading below the VWAP as the line declines shows that sellers are in control" [05:30-06:15]. "If you find an engulfing pin bar forming near the VWAP line, you have a good chance to initiate a trade" [06:00-06:15].

### Entry trigger

Bullish: "engulfing bar signifying that the strength of bulls have overcome the strength of bears. We also have a wick below the bar rejecting the VWAP line" [06:15-06:45]. Entry method: "You can enter right away after the candle was formed. Or you can place a buy stop at the high of the trigger candle" [06:15-06:45]. Bearish: symmetric (wick above, rejected resistance).

### Stop loss

"Stop loss is placed below the engulfing pin bar or below the VWAP" [06:30-06:45] (for long; mirror for short).

### Take profit / exit

"You target double the amount you risked. Or you set a take profit at the previous market swing" [06:30-06:45].

### Invalidation / skip conditions

NOT STATED - no skip conditions given for this pattern.

### Claimed performance

NONE CLAIMED

### Vagueness log

1. UNDEFINED-PARAM: VWAP period/length NOT STATED; speaker says "daily VWAP" but mechanism unclear for intraday timeframes
2. UNDEFINED-PARAM: What constitutes "near the VWAP line" - proximity threshold not stated
3. UNDEFINED-RULE: "Engulfing bar" definition is computable (body covers previous body) but wick size/type requirement is not specified ("the candle must contain a wick" [05:00-05:15] but wick length is NOT quantified)
4. UNDEFINED-PARAM: "Wick shows the area of price that was rejected" [05:15-05:30] - but wick rejection is treated as binary present/absent, not quantified by length
5. UNDEFINED-PARAM: "Double the amount you risked" is standard 2:1 R:R, but "previous market swing" is visual/manual identification

### Mechanizability

PARTIAL - Engulfing candle formation is computable (body overlap), VWAP can be calculated, and 2:1 risk/reward is computable, but the determination of "near VWAP" and the significance of wick presence (without length thresholds) introduce subjectivity.

---

## Strategy 3: Inside Bar Liquidity Clear Out

### Indicators and settings

- Inside bar: (as defined in Strategy 1)
- Liquidity clear out: "false break of the inside bar structure" followed by reversal [08:45-09:15]
- Pin bar: forms after the false breakout

### Context / bias filter

"Trade this setup in the direction of the most recent trend on the time frame you are monitoring" [11:15-11:30]. "Trade the setup as a continuation one and not a reversal one" [11:45-12:00]. This is critical: "If you short the market here, you are trading against the current momentum. You would have lost the trade" [11:45-12:00]. Pattern is: inside bar(s) → breakout of inside bar range → pin bar forms (false break) → reversal back into inside bar range.

### Entry trigger

"Once stop losses are hit, the market goes in their desired direction" [09:45-10:00]. "You place a buy stop on the other side of the inside bar with a stop loss below the liquidity run or below the pin bar" [11:00-11:30]. Buy setup: inside bar forms low, price breaks below (pin bar), then enters buy stop above the inside bar range. Sell setup: symmetric.

### Stop loss

"Stop loss below the liquidity run or below the pin bar" for long trades [11:15-11:30]. Mirror for short.

### Take profit / exit

NOT STATED - no explicit exit rule given.

### Invalidation / skip conditions

"Trade this setup in a trending market" [10:45-11:15]. If pattern forms while price is in a range (choppy conditions), not suitable [06:15-06:45 context from VWAP example]. "If you short the market here, you are trading against the current momentum. You would have lost the trade" [11:45-12:00] - so setup must align with trend direction.

### Claimed performance

NONE CLAIMED

### Vagueness log

1. UNDEFINED-RULE: "Inside bar liquidity clear out is a strong scalping signal" [08:45-09:15] - what makes a clear out "strong" vs weak is not quantified
2. UNDEFINED-PARAM: Multiple inside bars can form (examples show 2-4) [10:30-11:00] but no guidance on when to stop waiting for a false break
3. UNDEFINED-PARAM: "Direction of the most recent trend" not defined - how many bars back? What slope threshold?
4. VISUAL-ONLY: Identifying the "liquidity run" (stop loss location) requires visual inspection of where stops likely sit
5. SUBJECTIVE: Determining if market is "trending" vs "choppy" is qualitative

### Mechanizability

PARTIAL - Inside bar structure is computable, and false breaks can be detected (price outside inside bar range, then reversal back inside), but determining trend strength/direction and the exact "liquidity run" level require heuristics.

---

## Strategy 4: Multiple Consecutive Wicks Pattern

### Indicators and settings

- Candlestick wicks: (OHLC derived; wick length is high-low minus body range)
- Support/Resistance levels: visually identified

### Context / bias filter

"Look for periods when momentum is fading away and the potential price change may happen" [12:45-13:00]. In uptrend: "find corrections, pullbacks, with candlesticks starting to become smaller and more evenly sized. This is the first sign that the uptrend is losing momentum" [13:00-13:30]. In downtrend: "look for pullbacks with candlesticks becoming smaller" [13:30-14:00]. Location matters: "the better setups usually happen at key price levels" [14:15-14:30].

### Entry trigger

"The plan is to find two or three consecutive bars with overlapping upper or lower wicks" [13:45-14:15]. Buy: "consecutive candles having lower wicks, indicating that buyers are pushing the price up and rejecting lower prices" [15:15-15:30]. Sell: mirror (upper wicks). Wicks must overlap to create "a price zone that is more likely to display the buying or the selling pressure you anticipate" [14:15-14:30].

### Stop loss

"Stop loss is placed below the demand area and the take profit is set at the next supply area" [15:15-15:30] (for long). For the wick setup specifically: "Stop loss placement is obvious, above the multiple wicks" [14:45-15:00] (for short; mirror for long).

### Take profit / exit

"Target the next demand zone or double the amount you've risked" [14:45-15:00]. "Take partial profits as the price goes in your favor" [14:45-15:00]. "Take partial profits when price hits a minor supply area" [15:45-16:00].

### Invalidation / skip conditions

"Don't have a decent location to trade it, one single candle might not be sufficiently reliable for an entry" [13:30-14:00]. Requires setup at support/resistance or supply/demand zone; standalone wick pattern is weak.

### Claimed performance

Example trade on Dollar/Yen: "we have the chance to secure some profits when price hits this area" [15:45-16:00] but "the final target wasn't reached" [15:45-16:00] - no aggregate performance claimed.

### Vagueness log

1. UNDEFINED-PARAM: "Two or three consecutive bars with overlapping wicks" - exactly how many is optimal? Variance from 2-4+ shown in examples [13:45-14:15]
2. UNDEFINED-PARAM: Wick overlap threshold - do wicks need to touch? Fully overlap? Not specified [14:15-14:30]
3. UNDEFINED-PARAM: "Candlesticks starting to become smaller and more evenly sized" - no size threshold or variance limit stated
4. VISUAL-ONLY: Support/resistance/supply/demand zone identification
5. UNDEFINED-PARAM: "Consecutive candles with lower wicks" - wick must be below what? Previous candle low? A zone? Not stated beyond the price action interpretation

### Mechanizability

PARTIAL - Wick overlap can be computed (comparing wick highs/lows across consecutive bars), but the decision threshold (2 vs 3+ wicks needed, overlap distance, size decrease) requires heuristic parameters. Momentum "fading" is qualitative.

---

## Strategy 5: Power Candles (Large Spread Candles)

### Indicators and settings

- Power candle: "Candlesticks with a very large body or spread" [17:15-17:30]; "spread of the candle must be larger than the surrounding candles" [18:15-18:30]
- Volume: CRITICAL REQUIREMENT - "volume should therefore reflect the strong sentiment with strong volume" [18:45-19:00]; "If the volume is below average or low, this is not a valid candle to trade" [19:00-19:15]
- Two types:
  - Type A: "solid candle with little or no wick at the top or the bottom, it's suggesting strong and continued sentiment in the direction of the candle" [17:45-18:15]
  - Type B: "price action initially creates a solid candle, but then the sentiment starts to change, and the candle finishes with a wick at the top or at the bottom" [17:45-18:30]

### Context / bias filter

"During an uptrend, for example, and break some important resistance level, might be a decent indication of the continuation of the trend" [18:45-19:15]. Applied at support/resistance breakouts, or when momentum is picking up.

### Entry trigger

"When the candle breaks below the support level, because we also have the volume confirmation" [20:30-21:00]. Entry at close of candle or on market order. For retest entry: "wait for a retest of the breakout and then place a stop loss above this area" [20:30-21:00], but "in some cases, you won't have the chance for a retest. The power candle breaking an important level will lead price with even more momentum" [20:45-21:15].

### Stop loss

Initial: "above the high of the candle" [20:15-20:30]. Alternate (if waiting for retest): "place a stop loss above this area" (retest level) [20:30-21:00]. Tesla example: "depending on the range of the candle, you have to be flexible with the stop loss and the take profit" [20:15-20:30].

### Take profit / exit

"Next major resistance level or 2:1 risk-reward ratio" [implied from strategy language]. No specific exit rule stated; speaker emphasizes trade management complexity: "Depending on the range of the candle, you have to be flexible with the stop loss and the take profit" [20:15-20:30]. Look for retests after breakout as secondary entry opportunity [21:45-22:30].

### Invalidation / skip conditions

"If the volume is below average or low, this is not a valid candle to trade" [19:00-19:15]. Critical: power candle must break an important level (support/resistance) to be valid; standalone large candle at no key level is not a trade.

### Claimed performance

NONE CLAIMED with numbers, but example trades shown in Tesla and another chart [19:45-21:30].

### Vagueness log

1. UNDEFINED-PARAM: "Larger than the surrounding candles" - how much larger? 1.5x? 2x? Not stated [18:15-18:30]
2. UNDEFINED-PARAM: "Strong volume" - no threshold or comparison method stated (vs 20-day average? Previous 5 candles? Not specified [19:00-19:15])
3. UNDEFINED-PARAM: "Little or no wick" - what constitutes "little"? Wick length as percentage of body range not specified
4. UNDEFINED-PARAM: "Important level" - only stated as support/resistance breakouts; no definition of importance
5. UNDEFINED-RULE: Trade management flexibility due to candle range size - no framework given for deciding stop placement

### Mechanizability

PARTIAL - Power candle detection (spread relative to prior candles) is computable, and volume can be measured, but thresholds for "larger," "strong volume," and "little wick" are not specified. The discretionary trade management rule (flexible stops based on range size) is a judgment call.

---

## Strategy 6: Tower Top / Tower Bottom (Reversal Formation)

### Indicators and settings

- Candlestick patterns: Tower formation (3-candle pattern minimum)
- Volume: CRITICAL - "the volume of the bearish candle must be higher than the previous two candles. This is very important" [23:45-24:15]
- Tower Top: large bullish candle → several small candles → large bearish candle [22:45-23:00]
- Tower Bottom: large bearish candle → several small candles → large bullish candle [23:00-23:30]

### Context / bias filter

At resistance (for tower top) or support (for tower bottom). "It appeared at an obvious resistance level" [23:45-24:00] (AMD example). Optional: "liquidity clear out" adds confluence [24:00-24:15]; "if you see the pattern, and you also spot a liquidity clear out, the setup is even more powerful" [25:30-26:00].

### Entry trigger

"Entry is right after the large bearish candlestick forms with a stop above the bearish candle" [24:15-24:30] (for tower top). Mirror for tower bottom. Pattern completion is entry signal.

### Stop loss

For tower top: "stop above the bearish candle" [24:15-24:30]. For tower bottom: below the bullish candle (implied).

### Take profit / exit

"You target the next demand area" [24:00-24:15] (for tower top). Mirror for tower bottom (next supply area).

### Invalidation / skip conditions

"The volume of the bearish candle must be higher than the previous two candles. This is very important and it tells you that sellers are gaining strength. If you don't have the volume confirmation, you simply skip the trade" [24:00-24:30]. Critical: volume on final candle must exceed prior 2 candles, or trade is invalid.

### Claimed performance

NONE CLAIMED with numbers. Speaker notes one example trade (AMD tower top) would have been valid but says "in hindsight" regarding another example where volume confirmation was missing [24:45-25:30].

### Vagueness log

1. UNDEFINED-PARAM: "Several small bodied candlesticks" - how many is "several"? Minimum 1, but examples show 2-3 [23:00-23:30]
2. UNDEFINED-PARAM: "Small bodied" - no size threshold stated relative to the large candle
3. UNDEFINED-PARAM: Volume requirement is "higher than the previous two candles" [24:00-24:30] - exactly how much higher? 5% higher? 20% higher? Not specified
4. UNDEFINED-PARAM: "Spinning top" candles mentioned as typical consolidation pattern but not required [23:15-23:30]
5. VISUAL-ONLY: Location at "obvious resistance" or support is manual identification
6. UNDEFINED-RULE: Liquidity clear out confluence condition is binary but not mechanically defined

### Mechanizability

PARTIAL - Pattern structure (large → small → large candle sequence) is computable, and volume comparison ("higher than previous two") is computable, but the thresholds (how much higher, what constitutes "small body") are not specified. The optional liquidity clear out condition is not mechanically defined.

---

## Notable claims and caveats

Speaker emphasizes: "minimize the use of indicators" [26:45-27:00]. "As a scalper, you want to catch minor movements in a market, which means you need to make quick decisions. I prefer scalping based on price action and smart money concepts without using lagging indicators" [26:45-27:15].

Risk management rules stated [27:15-29:00]:
- "Always use a stop-loss when you're scalping and always respect it" [27:45-28:15]
- "Avoid overtrading and revenge trading. This is when, after a series of losing trades, you try to compensate your losses by opening more and more positions, each one bigger in size than the previous one" [27:45-28:30]
- "If you lose three or four trades in a row, just stop scalping for that day" [28:00-28:30]
- "I personally never risk more than 1% of my capital when I'm scalping" [28:30-28:45]
- "Scalping is very fast-paced, especially if you're trading the 1-minute time frame. If it's too quick for you, move to the 3-minute, or even better, to the 5-minute time frame" [29:00-29:30]

No discussion of transaction costs, slippage, commissions, or spread impact. The speaker does NOT address drawdown periods, losing streaks beyond emotional management, or market conditions where these strategies fail (e.g., during news events, gaps, or low liquidity).

Claims that strategies can be "adapted for day trading and even swing trading" on higher timeframes [29:15-29:30] but does NOT state specific parameter changes for these adaptations.

No performance metrics (win rate, profit factor, expectancy) claimed for any strategy.
