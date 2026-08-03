# Support & Resistance: The Part Everyone Gets Wrong (Complete SR Strategy)

- video_id: WXqqgvdzsg8
- url: https://www.youtube.com/watch?v=WXqqgvdzsg8
- duration: 29:31
- classification: MULTI-STRATEGY

## Summary

This video teaches support and resistance as a foundational trading concept, covering how to identify high-quality levels, interpret their behavior, and build multiple trading strategies around them. The core approach uses price zone identification combined with volume analysis and multi-timeframe confirmation to time entries and exits in both trending and ranging markets.

## Instruments and timeframes stated

- markets: NOT STATED
- timeframes: NOT STATED (but mentions 5-minute vs daily; weekly, daily, 4-hour, hourly charts discussed)
- sessions/hours: NOT STATED

## Strategy 1: Support/Resistance Level Identification and Bouncing

### Indicators and settings

- Support/Resistance zones: identified visually based on sharp reversals, multiple bounces, swing highs/lows, role reversal capability, visual prominence, and recent tests [00:30-08:00]
- Fibonacci retracements: ratios NOT SPECIFIED [24:54-25:30]
- Pivot Points: based on previous day's high, low, and close; S1, R1, S2, R2 levels mentioned but NOT CALCULATED [25:30-26:00]
- Volume profile: Point of Control, Profile High, Profile Low [17:30-18:30]

### Context / bias filter

Valid when: support/resistance level is visually obvious on chart with clear markers (sharp reversals, multiple bounces, or swing highs/lows) [06:30]. Recent tests are more reliable than distant past levels [07:00-07:30]. Combining multiple characteristics (round number + past support/resistance + multiple bounces + visual prominence) creates stronger levels [08:00].

### Entry trigger

Buy when price approaches support with high volume and shows strong rejection (bounces upward with force) [20:00-20:30]. Sell when price approaches resistance with high volume and shows strong rejection downward [20:00-20:30]. Wait for retest of broken support/resistance level before entering [10:30].

### Stop loss

Place stop just beyond the support or resistance level being traded. For longs at support, stop goes below the low of the bounce area. For shorts at resistance, stop goes above the high of the bounce area [13:00-13:30]. Use wider stops to avoid liquidity runs triggering false stops [14:00].

### Take profit / exit

NOT STATED explicitly for standard bounces. Mentioned: scale out as price reaches next resistance (for longs from support) or next support (for shorts from resistance) in the trend direction [22:00-23:30].

### Invalidation / skip conditions

Invalidate if price breaks through the level decisively on high volume - the level has broken [10:30]. False breakouts occur when price pokes beyond a level on low volume then reverses, which should be avoided in favor of waiting for confirmation [20:30-21:00]. Ranging markets are trickier and require waiting for clear rejection signals [22:30-24:00].

### Claimed performance

NONE CLAIMED

### Vagueness log

1. UNDEFINED-PARAM: "Sharp reversals" at support/resistance - the threshold for "sharp" is not quantified [04:30]
2. UNDEFINED-RULE: "Multiple bounces" - the number of bounces required to establish a level is not specified [05:15]
3. UNDEFINED-RULE: "Visually obvious" - this is subjective assessment, no objective criteria given [06:30]
4. UNDEFINED-PARAM: Fibonacci ratios - specific ratios to use are NOT STATED [24:54-25:30]
5. UNDEFINED-PARAM: Pivot Points calculation - the speaker references S1, R1, S2, R2 but does NOT provide the formulas [25:30-26:00]
6. UNDEFINED-PARAM: "High volume" and "low volume" - absolute or relative thresholds are NOT SPECIFIED [20:00-20:30]
7. UNDEFINED-RULE: "Force" in price rejection - what constitutes sufficient force is NOT DEFINED [23:00-23:15]
8. VISUAL-ONLY: "Structure" in trending markets - what price structure looks like on chart cannot be determined from audio [22:00]

### Mechanizability

PARTIAL - The core concept of identifying support/resistance zones can be coded (finding swing highs/lows, identifying price bounces), and volume checks are computable. However, the "visually obvious" and "sharp reversal" requirements require subjective visual interpretation. Without specified Fibonacci ratios or Pivot Points formulas, those tools cannot be applied programmatically.

## Strategy 2: Liquidity Run Trading (Buying/Selling into Stop Runs)

### Indicators and settings

- Stop-loss clustering: traders place stops just beyond obvious support/resistance levels [13:00-13:30]
- Volume spikes: used to identify liquidity grabs, but threshold NOT SPECIFIED [15:00-15:30]
- Momentum near levels: increasing momentum into level suggests potential liquidity run [15:00-15:30]
- Candlestick patterns: long wicks or dojis around levels indicate liquidity runs [15:15-15:30]

### Context / bias filter

Valid when: price is approaching a key support or resistance level with these markers: increasing momentum, unusual volume spikes, quick reversals after breaking level, unusual candlestick patterns with long wicks, multiple tests of level in short time frame [15:00-15:30]. Most common at obvious levels: previous day highs/lows, round numbers, major swings, levels tested multiple times [14:30-15:00]. Liquidity runs against the main trend often present good opportunities [16:30-17:00].

### Entry trigger

Instead of buying at support directly, wait for price to break below support triggering the stop run, THEN buy when price starts to recover and forms bullish candles [14:00-14:30]. At resistance, wait for price to push above the level before looking to sell [14:30]. Time entry after observing signs of move losing steam or reversing [16:00].

### Stop loss

Place stop below the recent low formed during the liquidity grab [16:00-16:30]. For shorts into resistance, place stop above the recent high [NOT EXPLICITLY STATED for this direction].

### Take profit / exit

NOT STATED - focus is on entry alignment with big players rather than exit mechanics [14:00-16:30].

### Invalidation / skip conditions

Skip if level breaks cleanly and continues strongly in breakout direction - this indicates a genuine move, not a liquidity run [15:30-16:00]. Liquidity runs on lower timeframes may be insignificant noise in context of larger trends; always verify on higher timeframe [16:30-17:00].

### Claimed performance

NONE CLAIMED

### Vagueness log

1. UNDEFINED-PARAM: "Increasing momentum" - what metric or threshold defines increased momentum is NOT SPECIFIED [15:00-15:30]
2. UNDEFINED-PARAM: "Unusual volume spikes" - the volume threshold or multiplier to identify unusual is NOT STATED [15:00-15:30]
3. UNDEFINED-PARAM: "High volume on break and retest" - specific volume levels or percentiles NOT SPECIFIED [11:30]
4. UNDEFINED-RULE: "Forms bullish candles" - how many candles, what size, what pattern specifically? NOT DEFINED [14:00-14:30]
5. UNDEFINED-RULE: "Signs that move is losing steam" - specific indicators or bars not defined [16:00]
6. SUBJECTIVE: Assessment of whether a break is "clean" vs a liquidity run trap [15:30-16:00]
7. UNDEFINED-PARAM: Timeframe selection - which timeframes to trade on NOT SPECIFIED [16:30-17:00]

### Mechanizability

PARTIAL - Volume spikes can be detected programmatically (above moving average or threshold), and stop runs can be identified as price breaking level then reversing. However, the identification of "bullish candles," "move losing steam," and the distinction between genuine breakouts and liquidity runs requires subjective judgment. Without specific thresholds for momentum and volume, the pattern is not fully codeable.

## Strategy 3: Support/Resistance Flips (Trading Breakouts and Role Reversals)

### Indicators and settings

- Volume: high volume on initial break and retest increases likelihood of successful flip [10:30-11:30]
- Trend strength: strong trends make flipped levels more likely to hold [11:00-11:30]
- Market structure: market conditions determine how reliably flips work [11:00-11:30]

### Context / bias filter

Valid when: price breaks through a support or resistance level decisively [09:00]. Strong trends favor reliable flips; choppy/ranging markets make flips less reliable [11:00-11:30]. A strong high-volume break is more likely to result in reliable flip than weak break on low volume [10:00-10:30].

### Entry trigger

When former support level breaks to the downside and price reverses back up to test that level, treat it as new resistance [09:00-09:30]. When former resistance level breaks to the upside and price reverses back down to test it, treat it as new support [09:30-10:00]. Wait for retest of broken level for confirmation before entering [10:30]. After a retest holding as flipped level, enter the trade [10:30-11:00].

### Stop loss

NOT EXPLICITLY STATED for the flip strategy itself. Referenced in context: traders place stops beyond levels [09:00-09:30].

### Take profit / exit

NOT STATED. Mentioned that flips can mark the beginning of new trends [12:00-12:30].

### Invalidation / skip conditions

Failed flips occur when a broken level fails to hold after flipping (e.g., broken support does not hold as resistance) - this can lead to strong moves opposite to expectations [10:30-11:00]. Not all levels will flip cleanly; market is dynamic and even strong levels can be broken [11:30].

### Claimed performance

Successful flips often mark the beginning of new trends: "when a longstanding resistance level is finally broken and then holds as support it can signal the start of a significant uptrend" [12:00-12:30]; "when a strong support level breaks and then acts as resistance it might indicate the beginning of a downtrend" [12:00-12:30].

### Vagueness log

1. UNDEFINED-PARAM: "Decisively breaks" - what constitutes a decisive break (distance, volume, candle size) is NOT SPECIFIED [09:00]
2. UNDEFINED-RULE: "Strong break on high volume" vs "weak break on low volume" - specific volume thresholds NOT GIVEN [10:00-10:30]
3. UNDEFINED-PARAM: "Choppy or ranging" markets - the criteria to distinguish these from trending is NOT DEFINED [11:00-11:30]
4. UNDEFINED-RULE: What constitutes a successful retest - how far back into broken level, what volume needed? NOT SPECIFIED [10:30-11:00]
5. SUBJECTIVE: Determining if market conditions are "trending" or "ranging" [11:00-11:30]

### Mechanizability

PARTIAL - Breakouts can be identified (price breaks previous support/resistance), and level flips are simple structural markers. Volume can be measured programmatically. However, the definitions of "decisive," "strong," "choppy," and successful "retest" are not quantified, requiring assumption or subjective interpretation.

## Strategy 4: Multi-Timeframe Analysis (Hierarchical Entry Framework)

### Indicators and settings

- Higher timeframe levels: gain strength when visible on multiple timeframes [27:00-27:30]
- Lower timeframe refinement: used for entry timing and precision [27:30-28:00]

### Context / bias filter

Start with higher timeframe (daily) to identify major support/resistance levels and overall market context [28:00-28:30]. Levels visible on higher timeframes are more significant and more likely to hold [27:00-27:30]. A level on weekly chart may hold even if price dips below it briefly on hourly chart [27:00-27:30].

### Entry trigger

Multi-timeframe approach: (1) identify trend direction and key levels on daily chart, (2) find setups on hourly chart matching daily direction, (3) use lower timeframe to fine-tune entry and exit [28:00-28:30]. Specific example: use weekly chart for major levels, daily for trend direction, 4-hour chart for entries [28:30-29:00].

### Stop loss

NOT STATED for this framework.

### Take profit / exit

NOT STATED for this framework.

### Invalidation / skip conditions

Avoid trading against a bigger trend identified on higher timeframe [28:30]. Lower timeframe moves are often just noise; validate them against higher timeframe context [27:30-28:00].

### Claimed performance

NONE CLAIMED

### Vagueness log

1. UNDEFINED-RULE: The exact number of timeframes to analyze - speaker suggests examples but no hard rule given [28:00-28:30]
2. UNDEFINED-PARAM: Which specific timeframes are "higher" vs "lower" - depends on trader's timeframe; no absolute standard given [27:00-28:00]
3. UNDEFINED-RULE: "Small price dips" on lower timeframe that don't invalidate higher timeframe level - what constitutes "brief" or "small"? NOT DEFINED [27:00-27:30]
4. SUBJECTIVE: Determining which levels on higher timeframe to focus on vs ignore [28:00-28:30]

### Mechanizability

PARTIAL - The concept is sound and can be partially coded: find support/resistance on multiple timeframes, check if price is aligned with higher timeframe trend, execute entries on lower timeframe. However, the selection of which levels matter on higher timeframes requires subjective interpretation of "major levels."

## Notable claims and caveats

The speaker emphasizes that support and resistance levels are ZONES, not exact prices [00:30-01:00]. Levels are self-fulfilling prophecies - they work because traders expect them to work and act accordingly [01:30-02:00]. False breakouts are common, so waiting for confirmation is essential [20:30-21:00]. Big players exploit obvious levels through liquidity runs, deliberately pushing price through levels to trigger stops [12:00-14:00]. The speaker does NOT mention trading costs, spread, slippage, or commission. No discussion of maximum drawdown, losing streak frequency, or strategy edge in different market conditions.
