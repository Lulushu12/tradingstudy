# I Simplified Fibonacci Trading to One Profitable Strategy

- video_id: NnUnk7HffHo
- url: https://www.youtube.com/watch?v=NnUnk7HffHo
- duration: 30:08
- classification: MULTI-STRATEGY

## Summary

This video teaches how to use Fibonacci retracements effectively in trending markets by identifying clear swing highs and lows and watching for price reactions at key Fib levels. The speaker covers multiple methods including the Golden Zone approach (50%-61% confluence), using candlestick patterns as confirmation, combining Fibonacci with moving averages, and identifying supply/demand areas that coincide with Fib levels. The core theme is that Fibonacci levels work best on larger timeframes where the trend is clear and levels are spaced far enough apart to be mechanically tradeable.

## Instruments and timeframes stated

- markets: Any market with trends mentioned [00:00]; implied forex/crypto/equities
- timeframes: Larger timeframes emphasized [06:30]; examples given include daily chart, 4-hour chart, 1-hour chart [17:00-19:30]
- sessions/hours: NOT STATED

## Strategy 1: Basic Fibonacci Retracement Confirmation with Candlestick Patterns

### Indicators and settings
- Fibonacci levels: 23%, 38%, 50%, 61%, 78%, 88% [03:30]
- Candlestick patterns: engulfing patterns, candles with long wicks [10:30]
- Timeframe: Larger timeframes preferred [11:30]

### Context / bias filter
Trending market with clear trend identified [02:30]; avoid sideways/ranging conditions [04:30]; use obvious swing highs and swing lows, not forced fits [02:00]

### Entry trigger
Price reaches a Fibonacci level and forms either [10:30]:
- Engulfing pattern (bullish engulfing at support in uptrend, bearish engulfing at resistance in downtrend), or
- Candle with long lower wick at Fibonacci support level (showing rejection of lower prices), or
- Candle with long upper wick at Fibonacci resistance level (showing rejection of higher prices)

### Stop loss
In uptrend: just above the Golden Zone (61% level) if entering near the 50-61% zone [15:00]
In downtrend: NOT STATED for stop placement in uptrends

### Take profit / exit
Uptrend pullback scenario: take profit at 38% level, then at 23% level, then at 100% retracement (full reversal to start of move) [15:30-16:00]
Downtrend bounce scenario: NOT STATED for profit targets

### Invalidation / skip conditions
Skip if price never pulls back to Fib level and instead continues trending [15:00]
Avoid on short timeframes where levels are too close together and create noise [05:00-06:00]
Avoid in sideways/consolidating markets without clear breakout [04:30]

### Claimed performance
NONE CLAIMED

### Vagueness log
1. "Clear trend" and "most obvious swing high/low" are subjective - different traders choose different points [00:30]
2. "Look for a clearer setup" if you're "squinting at the chart" - SUBJECTIVE threshold for quality
3. "True market trend or important levels" on short timeframes is a judgment call - SUBJECTIVE
4. "Narrow confluences" concept depends on trader perception of distance - UNDEFINED-RULE
5. Identifying which price swing is "most relevant" to current market conditions [03:00] - SUBJECTIVE
6. Determining when levels are "spaced far enough apart" - UNDEFINED-PARAM (no specific minimum distance stated)

### Mechanizability
PARTIAL. The core logic (price reaches X% level and forms candlestick pattern) is mechanically computable from OHLCV data. However, three critical gaps remain unspecified: (1) which swing high/low to use for drawing Fibs (requires subjective judgment), (2) what constitutes "obvious" vs. forced fits, and (3) the exact distance threshold between candlestick open/close for pattern confirmation.

## Strategy 2: Golden Zone Method (50%-61% Confluence)

### Indicators and settings
- Fibonacci levels: 50% and 61.8% [14:30]
- Timeframe: Larger timeframes [11:30]

### Context / bias filter
Downtrend established [14:00]; price pulls back against the trend direction [14:00]

### Entry trigger
Price reaches the 50-61% zone during pullback [14:30]. Key entry moment: when price returns below the 61.8% line after testing or going slightly above it [14:30]. Wait for bearish candle or "other factors lining up" [15:00] [VISUAL-ONLY]

### Stop loss
Just above the 61% line [16:30]

### Take profit / exit
First target: 38% level [15:30]
If breaks above 38%, next target: 23% level [15:30]
Final target: 100% retracement (full return to start of downtrend) [16:00]
Alternative: partial profit-taking at 38%, more at 23% [16:00]

### Invalidation / skip conditions
If price closes above 61% level (invalidates the setup) [14:30]
If price makes new low that significantly exceeds the original downtrend start - NOT STATED

### Claimed performance
NONE CLAIMED

### Vagueness log
1. "Bearish candle forming or other factors lining up" [15:00] - SUBJECTIVE, "other factors" undefined
2. "Price returns below 61.8%" is slightly vague on whether it means close, wick, or just touch - UNDEFINED-RULE
3. Identifying the "original trend" that triggers the pullback - SUBJECTIVE
4. "Price goes a bit above this area" [14:30] - no quantified threshold for how much is acceptable - UNDEFINED-PARAM

### Mechanizability
PARTIAL. The core structure (price pulls back to 50-61% zone and reverses) is mechanically checkable. However, the entry signal relies on observing an unspecified "bearish candle" or undefined "other factors," and the exact threshold for invalidation if price breaks above 61% needs specification (close, wick, or how much above).

## Strategy 3: Multi-Timeframe Confluence (Different Timeframes)

### Indicators and settings
- Fibonacci levels on multiple timeframes (e.g., daily and 4-hour; 4-hour and 1-hour)
- Example: 61% on 4-hour aligned with 38% on daily [18:00]
- Example: 4-hour 38% aligned with 1-hour 50% [19:30]

### Context / bias filter
Larger timeframe shows overall trend [07:00]; zoom to smaller timeframes for entry

### Entry trigger
Price reaches confluence zone where multiple Fibonacci levels from different timeframes overlap [17:00-18:00]. Entry when price bounces from this zone [19:00]

### Stop loss
NOT STATED

### Take profit / exit
Use the confluence zone as a reversal point; continue in the direction of the larger trend [18:30]

### Invalidation / skip conditions
If confluence zone doesn't hold and price breaks through - NOT STATED what happens next

### Claimed performance
NONE CLAIMED

### Vagueness log
1. "Overlap creates a strong area to watch" [17:30] - VISUAL-ONLY, no mechanical definition of overlap threshold
2. "Traders using different timeframes will all see this area as significant" [18:30] - this is psychological/observational, not mechanically computable
3. Which specific timeframe pairs to use is not specified - UNDEFINED-PARAM
4. "Bounce" signal is vague without candlestick pattern or volume confirmation - UNDEFINED-RULE

### Mechanizability
PARTIAL. Identifying overlapping Fib levels is mechanically computable once the initial swing highs/lows are chosen. However, identifying what constitutes an "overlap" (how close do levels need to be to the same price?) is undefined, and the entry signal (when to enter after overlap) lacks specificity.

## Strategy 4: Fibonacci + Moving Average Confluence

### Indicators and settings
- Fibonacci retracement: 50% level [21:00]
- Moving average: 200-period exponential moving average [21:00]
- Other example: 61% Fib with 200-period moving average [22:30]; 50% Fib with 50-period average [22:30]

### Context / bias filter
Uptrend established; price pulling back [21:00]

### Entry trigger
Fibonacci level aligns with moving average at same price level [21:00]. Example: 50% Fib level at same price as 200-period EMA [21:30]

### Stop loss
NOT STATED

### Take profit / exit
NOT STATED; speaker notes price "may pause, bounce, or even reverse" [21:30]

### Invalidation / skip conditions
NOT STATED

### Claimed performance
"Confluence increases the odds of price reacting at this level" [21:30]; described as "strong hint from the market" [21:30]

### Vagueness log
1. Different traders use different MA periods (200 vs. 50 vs. others) and different Fib levels [22:30] - UNDEFINED-PARAM for which combination is optimal
2. What constitutes alignment between Fib level and MA is not precisely defined - UNDEFINED-RULE (price range where they're considered aligned?)
3. "Understanding structure" and "big players active" concepts are qualitative - SUBJECTIVE
4. No entry or exit rules specified - UNDEFINED-RULE

### Mechanizability
PARTIAL. Once MA period and Fib level are chosen, alignment is computable. However, defining what qualifies as "alignment" (exact match, within 5 pips, within 10 pips?) is not specified, and no complete entry/exit rules are given.

## Strategy 5: Volume Confirmation at Fibonacci Levels

### Indicators and settings
- Fibonacci levels: any level (example uses 50%) [23:00]
- Volume: declining volume into level, then spike on bounce [23:00-24:00]

### Context / bias filter
Price approaching Fibonacci support level in uptrend [23:00]

### Entry trigger
Price approaches Fib support with declining volume (fewer sellers) [23:30]. Wait for volume spike after bounce [23:30]. High volume spike upwards signals entry [24:00]

### Stop loss
NOT STATED

### Take profit / exit
NOT STATED

### Invalidation / skip conditions
Price dips significantly below Fib level with low volume during dip may indicate fake-out [24:00], but is potentially still tradeable if followed by volume spike on recovery

### Claimed performance
"Big jump in volume...is like a green light" [24:00]; "sign that the upward move might continue" [24:00]

### Vagueness log
1. "Declining volume" - no absolute threshold specified (how much lower than previous? what timeframe?) - UNDEFINED-PARAM
2. "Big jump in volume" - UNDEFINED-PARAM (how big? compared to what baseline?)
3. "Smart buyers see this as a chance" [23:30] - SUBJECTIVE interpretation of market participant intent
4. Exact entry point after volume spike unclear - UNDEFINED-RULE
5. Downtrend/resistance level dynamics mentioned but details not specified - UNDEFINED-RULE

### Mechanizability
PARTIAL. Volume spike detection is mechanically computable if thresholds are defined. However, the definitions for "declining volume" and "big jump" are absent, requiring assumption of baseline values and sensitivity thresholds.

## Strategy 6: MACD Divergence at Fibonacci Levels

### Indicators and settings
- Fibonacci levels: example uses 50% level [25:30]
- Momentum indicator: MACD [25:30]
- Divergence type: price makes higher highs while indicator makes lower highs (or opposite) [26:00]

### Context / bias filter
Price at Fibonacci level in trend [25:30]

### Entry trigger
Divergence between price and MACD at Fibonacci level [25:30]. In downtrend: price bounces to 50% Fib, if MACD shows lower highs while price shows higher highs = reversal signal [26:00]. In uptrend: price retraces to 61% Fib, divergence on MACD = buy signal [26:30]

### Stop loss
NOT STATED

### Take profit / exit
NOT STATED

### Invalidation / skip conditions
Divergence doesn't guarantee reversal, requires other confirmation (candlestick patterns, volume changes) [26:30]

### Claimed performance
Divergence described as "leading indicator" and "strong buy signal" [26:30]

### Vagueness log
1. Defining divergence precisely (how many bars? how much lower/higher for lower highs/lows?) - UNDEFINED-PARAM
2. Which MACD settings to use (12-26-9 default assumed but not stated) - UNDEFINED-PARAM
3. When to confirm divergence with other signals is vague - UNDEFINED-RULE
4. "Leading indicator" is more theoretical than mechanically defined - SUBJECTIVE

### Mechanizability
PARTIAL. Divergences are mechanically detectable once MACD settings are chosen, but the exact definition of a divergence (how many bars to compare, how much difference constitutes divergence) is not specified. The requirement for "other signals" to confirm makes this dependent on multiple undefined criteria.

## Strategy 7: Supply/Demand + Fibonacci Confluence

### Indicators and settings
- Fibonacci levels: aligned with supply and demand zones
- Supply and demand zones: identified visually as areas where large reversals occurred [27:30]

### Context / bias filter
Uptrend for demand area confluence; downtrend for supply area confluence [28:00]

### Entry trigger
Price approaches demand area that lines up with Fib level - potential buy entry [27:30]
Price approaches supply area that matches Fib level - potential short entry [27:30]
"Bounce off that area" = entry in direction of trend [27:30]

### Stop loss
NOT STATED

### Take profit / exit
NOT STATED; implies riding the trend that follows the bounce [27:30-28:00]

### Invalidation / skip conditions
If price breaks through the zone instead of bouncing - NOT STATED how to handle

### Claimed performance
Described as "confluence perfect for a trade" [27:30]; supply/demand + Fib combo as "secret messages in the market" [29:00]

### Vagueness log
1. "Supply and demand areas" are identified as places where large reversals occurred - VISUAL-ONLY, not mechanically defined (how large? how fast?)
2. "Coincides with a Fib level" needs definition of how close they need to be - UNDEFINED-RULE
3. "Bounce" entry signal is vague - UNDEFINED-RULE (which candlestick confirms the bounce?)
4. "Big players in the market might be active" - SUBJECTIVE interpretation
5. Identifying where supply/demand zones start and end requires visual judgment - SUBJECTIVE

### Mechanizability
DISCRETIONARY. While Fib levels are mechanical, supply/demand zones depend entirely on visual identification of where reversals occurred. The entry signal ("bounce off the area") is subjective and lacks mechanically computable criteria. This strategy requires trader judgment at its core.

## Notable claims and caveats

The speaker emphasizes Fibonacci levels are NOT exact support/resistance points but rather zones [04:30]. The speaker warns that Fibonacci levels struggle in sideways/ranging markets and recommends avoiding these conditions [04:30]. Short timeframe usage is discouraged because levels cluster too closely together, creating false signals [05:00-06:00].

The speaker notes that Fibonacci levels can become self-fulfilling prophecies due to many traders watching the same levels [04:30]. 

Notably, the speaker does NOT mention transaction costs, spreads, slippage, or commissions at any point in the video. No discussion of drawdown periods, losing streaks, or risk management beyond stop loss placement is included.

No win rate statistics or backtest results are provided for any of the seven methods described.
