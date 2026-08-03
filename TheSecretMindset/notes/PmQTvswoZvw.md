# The Best Way To Combine Tradingview Indicators For Day Trading

- video_id: PmQTvswoZvw
- url: https://www.youtube.com/watch?v=PmQTvswoZvw
- duration: 13:07
- classification: TOOLING

## Summary

This video teaches the principle that redundant indicators create "echo" rather than confirmation. The speaker categorizes all indicators into four types (trend, momentum, volume, volatility) and argues that you should use one indicator from each category, never two from the same one. The video uses examples to show how a signal stack of three indicators (direction, momentum, participation) combined with a "location filter" (price at a tested level) improves trade quality compared to stacking redundant momentum indicators.

## Instruments and timeframes stated

- markets: Tesla (example at 15-minute), Euro-Yen (example at 1-hour), NOT STATED for general application
- timeframes: 15-minute [05:00], 1-hour [10:30], NOT STATED in general
- sessions/hours: NOT STATED

## The Indicator Classification Framework

This is not a tradeable strategy but a taxonomy the speaker uses to organize thinking:

### Trend indicators (answer: Where is price headed?)
- Examples given: EMA, VWAP, moving average crosses [03:30]
- Parameters: NOT STATED

### Momentum indicators (answer: How much force is behind the move?)
- Examples given: RSI, MACD, Stochastic [03:30]
- Parameters: NOT STATED
- Note: Speaker clarifies "all watching the same tape regardless of how different they look" [04:00]

### Volume indicators (answer: Is real money backing this move?)
- Examples given: Volume profile, OBV [04:00]
- Parameters: NOT STATED

### Volatility indicators (answer: How much room does price have?)
- Examples given: ATR, Bollinger Bands [04:30]
- Parameters: NOT STATED

### Core Rule
"Use one from each box, never two from the same one" [04:30]. Do not need all four categories; only need "the right two answering two different questions" [05:00].

## Strategy 1: Tesla 15-minute Signal Stack (VWAP + RSI)

### Indicators and settings
- VWAP: NOT STATED (period/parameters)
- RSI: above 50 is bullish direction [05:30], no period stated

### Context / bias filter
- Price below VWAP holding steady for several candles [05:30]
- Direction is down (VWAP below price for downtrend examples) [05:30]
- RSI below 50 means push still pointed the right way (downtrend) [05:30]

### Entry trigger
Price has drifted back into a zone where sellers already showed up and held. Old support acting as resistance. That's the entry [05:30-06:00].

### Stop loss
Stop goes above the level where sellers stepped in [06:00].

### Take profit / exit
Target is the support sitting below [06:00].

### Invalidation / skip conditions
NOT STATED

### Claimed performance
Around 3R trade, $600 the next day [06:30].

### Vagueness log
1. VWAP period: UNDEFINED-PARAM
2. RSI period: UNDEFINED-PARAM
3. "Holding steady for several candles": UNDEFINED-RULE (how many is several?)
4. "Zone where sellers showed up and held": VISUAL-ONLY (requires chart inspection)
5. "Drifted back into the zone": UNDEFINED-RULE (no quantified distance specified)
6. Entry price not mechanically defined: UNDEFINED-RULE

### Mechanizability
DISCRETIONARY. The entry is defined as a visual level ("old support") without numerical parameters; requires visual inspection of the chart to identify the zone where sellers previously held.

## Strategy 2: Failed Trade Leading to OBV Addition

This section describes why adding OBV (a volume indicator) caught a failed trade that the VWAP+RSI stack missed.

### Indicators and settings
- VWAP: NOT STATED (period)
- RSI: below 50 for downtrend [07:00]
- OBV: NOT STATED (period/settings)

### Context / bias filter
Same as Strategy 1.

### Entry trigger
VWAP trending down, RSI below 50, both looked clean. Entered [07:00].

### Stop loss
NOT STATED

### Take profit / exit
NOT STATED

### Invalidation / skip conditions
OBV showed flat reading with divergence—nobody with real money was behind the move [07:30]. Price was walking alone [07:30].

### Claimed performance
Failed trade: $300 lost in several candles [07:00-07:30].

### Vagueness log
1. VWAP period: UNDEFINED-PARAM
2. RSI period: UNDEFINED-PARAM
3. "Flat the entire build up" and "formed a divergence": UNDEFINED-RULE (no specific OBV threshold or divergence definition)
4. What constitutes "real money backing" vs. "just watching": SUBJECTIVE
5. Entry and stop not fully specified: UNDEFINED-RULE

### Mechanizability
PARTIAL. OBV divergence can be coded, but the threshold for "flat" and what constitutes a "valid" divergence are not specified.

## Strategy 3: Three-Indicator Signal Stack (EMA + RSI + OBV + Location Filter)

### Indicators and settings
- EMA: period NOT STATED, used for direction
- RSI: period NOT STATED, above/below 50 for direction
- OBV: period NOT STATED, used to confirm real money participation

### Context / bias filter
"Signal stack fires at a level that's already been tested and held" [09:30-10:00]. Price must be at:
- A prior resistance that buyers broke through and came back to defend, OR
- A swing low that formed a demand level [10:00]

NOT acceptable: "floating in the middle of a range with open space below and no level that buyers have shown up for" [10:00].

### Entry trigger
All three indicators align:
1. EMA trending in direction [11:00]
2. RSI above/below 50 (depending on direction) with a slight pullback [11:00]
3. OBV rising alongside higher lows, real money stepping in [11:00]

AND price is at a tested level as defined in context filter [11:00].

Entry on the candle close [11:00].

### Stop loss
Stop below the level buyers defended [11:00].

### Take profit / exit
Target is the resistance above [11:00].

### Invalidation / skip conditions
"The signal stack said go, but the location filter said wait" [11:30]. If any one of the three indicators disagrees, skip the trade—"One indicator pushing back when the other two say go isn't noise. It's the one honest friend in a group full of yes-men" [08:30].

### Claimed performance
Backtested for past eight weeks [09:00]. "Every indicator green on every entry. And the results weren't great" [09:00]. Problem identified: Most times entering in open space when price was floating between levels [09:00-09:30].

### Vagueness log
1. EMA period: UNDEFINED-PARAM
2. RSI period: UNDEFINED-PARAM
3. OBV period: UNDEFINED-PARAM
4. "Slight pullback": UNDEFINED-RULE (no quantified amount)
5. "Prior resistance that buyers broke through": VISUAL-ONLY (requires chart analysis)
6. "Swing low that formed a demand level": VISUAL-ONLY (requires chart analysis)
7. "Real money stepping in": SUBJECTIVE (how much OBV rise constitutes participation?)
8. "Tested and held": UNDEFINED-RULE (how many touches? how recent?)

### Mechanizability
PARTIAL. The indicator stack can be coded with default parameters (e.g., RSI period 14, OBV standard), but the location filter requires visual level identification. Price must be within X pips/points of a previously-tested level, but no tolerance is specified.

## Strategy 4: Euro-Yen 1-hour Example (Positive Signal)

### Indicators and settings
- EMA: period NOT STATED
- RSI: above 50 [11:00], period NOT STATED
- OBV: NOT STATED, rising alongside higher lows [11:00]

### Context / bias filter
EMA trending, price above it and holding [11:00].

### Entry trigger
Price sitting at a prior resistance that buyers broke through and came back to hold [11:00-11:30]. Entry on candle close [11:00].

### Stop loss
Stop below the level buyers defended [11:00].

### Take profit / exit
Target is the resistance above [11:00].

### Invalidation / skip conditions
NOT STATED

### Claimed performance
No performance claim made for this specific trade.

### Vagueness log
1. EMA period: UNDEFINED-PARAM
2. RSI period: UNDEFINED-PARAM
3. "Prior resistance...came back to hold": VISUAL-ONLY
4. Entry mechanics (which candle, which price): VISUAL-ONLY

### Mechanizability
VISUAL-ONLY. Entirely dependent on identifying tested levels from the chart visually.

## Strategy 5: Euro-Yen 1-hour Example (Negative Signal - Should Avoid)

### Indicators and settings
- EMA: trending
- RSI: above 50
- OBV: rising

### Context / bias filter
Same as other setups, except:

### Entry trigger
Price floating in the middle of the range, halfway between support below and resistance above [11:30].

### Stop loss
NOT STATED

### Take profit / exit
NOT STATED

### Invalidation / skip conditions
Price has no level beneath the entry that buyers have ever shown up to defend [11:30]. "Nothing holding the trade up if momentum pauses" [11:30]. Location filter says WAIT [11:30].

### Claimed performance
"The signal stack said go, but the location filter said wait. Two trades, same indicators and same stack. One at a proven level, one in open space. They're not the same trade. They're not even close" [12:00-12:30].

### Vagueness log
1. Same as Strategy 4

### Mechanizability
VISUAL-ONLY. Same mechanics as Strategy 4, but this one demonstrates how the same signal stack in a different location has opposite win probability.

## Notable claims and caveats

- "That's why your best looking signals failed the fastest. You didn't have confluence, you had echo" [00:00]. Stacking three momentum indicators produces one opinion, not confirmation [01:30-02:00].
- "The most common mistake I see everywhere" is stacking redundant indicators [02:00].
- "Every indicator on the planet answers one of four questions" [03:30]. Framework for categorizing indicators to avoid redundancy.
- "A signal from the right level is worth more than three signals from the wrong one" [09:30]. Location matters more than indicator alignment.
- "The location filter doesn't complicate your system. It stops you from taking high probability signals and placing them in a low probability zones" [12:00-12:30].
- The speaker backtested the signal stack for eight weeks and found it produced "all green signals" but the results were not good due to poor location selection [09:00-09:30].
- No mention of costs, spread, slippage, or commission.
- No mention of drawdown or losing streaks.
- Video concludes hinting at another issue: "You can have...a proven level beneath the entry, and still lose because one thing on your chart is lying to you every single session, and it looks completely legitimate" [12:30-13:00].

## Video Classification Note

This video is primarily **TOOLING** — it teaches a framework for combining indicators rationally but does not present a standalone, self-contained trading strategy with complete entry/exit rules. The examples are illustrative of the principle, not complete strategies. To backtest any of these setups, significant parameter definition and discretionary level-finding would be required.
