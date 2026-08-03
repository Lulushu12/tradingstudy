# How To Trade With Rate Of Change To Forecast Price Momentum (Day Trading Strategies)

- video_id: FuAkbgDgX_4
- url: https://www.youtube.com/watch?v=FuAkbgDgX_4
- duration: 11:26
- classification: MULTI-STRATEGY

## Summary

The video teaches three different approaches to trading with the Rate of Change (ROC) momentum oscillator. Strategy 1 uses ROC zero-line crossovers filtered by a 50-period moving average to time entries within established trends. Strategy 2 uses ROC divergences to detect potential reversals (though the speaker notes this is unreliable without confirmation). Strategy 3 uses overbought/oversold extreme levels, but the speaker explicitly discourages this approach in trending markets. ROC periods commonly used are 9, 14, 21, or 50, with no universally "correct" setting.

## Instruments and timeframes stated

- markets: stocks, currencies (general application) [02:00]
- timeframes: ROC works on "various time frames" [02:00]; better for "identifying the long-term trend" [02:00]
- sessions/hours: NOT STATED

## Strategy 1: ROC Zero-Line Crossover with Moving Average Trend Filter

### Indicators and settings

- ROC: period NOT SPECIFIED for this strategy; common settings are 9, 14, 21, or 50 periods [02:30]
- Moving Average: 50-period simple moving average [05:30-06:00]

### Context / bias filter

- Determine prevailing trend using the moving average [05:30]
- "When the price trades above the 50-period simple moving average, consider taking only long entries. And when the price trades below the 50-period SMA search for short entries" [06:00]
- "As most of the oscillators, the rate of change works well in a trending scenario" [05:30]

### Entry trigger (LONG)

Price above 50 SMA AND ROC crosses above zero line [06:00]

"take the zero line crossovers only in confirmation with the 50-period moving average" [06:00]

### Entry trigger (SHORT)

Price below 50 SMA AND ROC crosses below zero line [06:00]

### Stop loss

NOT STATED

### Take profit / exit

"Consider exiting your position when the slope of the rate of change turns in the opposite direction" [06:00]

### Invalidation / skip conditions

- "sometimes, the ROC can dip below the zero-line only to reverse back higher" [05:00]
- "By itself, this signal is not reliable" without the moving average filter [04:30]
- "The ROC reacts to the price and not the other way around. Therefore, you need to focus on the price and price action as well" [05:00]

### Claimed performance

"here are some examples of zero line crossovers confirmed by the moving average" [06:30] — shown as working examples

### Vagueness log

1. UNDEFINED-PARAM: ROC period NOT specified for this strategy [05:30]
2. UNDEFINED-RULE: "the slope of the rate of change turns in the opposite direction" — what constitutes a turn? A single candle reversal or trend reversal? [06:00]
3. UNDEFINED-PARAM: Stop loss NOT stated
4. UNDEFINED-PARAM: Profit target NOT stated; only exit rule given as slope reversal
5. SUBJECTIVE: "prevailing trend" determination not precisely defined; only says to look at moving average [05:30]

### Mechanizability

PARTIAL

Zero-line crossover detection is fully computable. 50 SMA calculation is standard. However, gaps remain: (1) ROC period not specified (default of 12 or user-selected?); (2) slope reversal as exit is vague (exact threshold for "turn"?); (3) no stop loss defined; (4) no profit target defined. The entry signal is mechanizable, but exit logic and risk management are discretionary.

## Strategy 2: ROC Divergence Detection (Potential Reversals)

### Indicators and settings

- ROC: period NOT SPECIFIED

Definition of divergence: "When the oscillator forms a fresh low but price does not, or when price forms a high but the oscillator does not, it can indicate a possible divergence" [07:00]

### Context / bias filter

- Works in trending markets [06:30]
- "A divergence is a leading signal but could prove to be a notoriously poor timing signal since a divergence can last a long time and won't always result in a price reversal" [08:00]
- "Timing a divergence is maybe even more important than spotting the pattern" [08:00]

### Entry trigger - Bearish Divergence

Price rising while ROC progressively moving lower: "the ROC is indicating bearish divergence from price, which signals a possible trend change to the downside" [07:30]

### Entry trigger - Bullish Divergence

Price moving down while ROC moving higher [07:30]

Example: "price posted a lower low, but the ROC oscillator posted a higher low. This divergence, known as bullish divergence" [08:30]

Confirmation required: "wait for a trend line breakout on the chart. Also, you could wait for the price rate of change to cross below zero level" [08:30]

For bullish entry: "after the ROC indicator crosses above 0, indicating a bullish momentum" [09:00]

### Stop loss

NOT STATED

### Take profit / exit

NOT STATED

### Invalidation / skip conditions

- "There are several peaks for the ROC reading, and all of them would have given wrong trading signals" [08:00]
- Divergences can be false/prolonged [08:00]
- Requires additional confirmation (trendline breakout or zero-line crossover) to filter signals [08:30-09:00]

### Claimed performance

"This example shows the ROC indicator posting a long term divergence. There are several peaks for the ROC reading, and all of them would have given wrong trading signals" [08:00-08:30]

### Vagueness log

1. UNDEFINED-PARAM: ROC period NOT specified
2. UNDEFINED-RULE: Divergence identification — which specific swing highs/lows to compare? How many to confirm a divergence pattern? [07:00]
3. UNDEFINED-RULE: "price forms a high but oscillator does not" — at which exact swing? [07:00]
4. UNDEFINED-RULE: "progressively moving lower" for ROC — minimum count of lower peaks? 2, 3, or more? [07:30]
5. UNDEFINED-RULE: Trendline breakout confirmation — which trendline? How many points to draw objectively? [08:30]
6. UNDEFINED-PARAM: Stop loss NOT stated
7. UNDEFINED-PARAM: Profit target NOT stated

### Mechanizability

DISCRETIONARY

Comparing price extrema to ROC extrema is conceptually computable but requires defining "corresponding" highs/lows, which is subjective in multi-wave charts. Trendline breakout confirmation is not mechanically defined (which points to use, how many). Zero-line crossover is computable. However, critical gaps: (1) no objective rule for identifying which price/ROC swings form a divergence; (2) trendline drawing criteria not specified; (3) stop and profit targets entirely missing. Cannot be automated without inventing these definitions.

## Strategy 3: ROC Overbought/Oversold Levels (DISCOURAGED)

### Indicators and settings

- ROC: period NOT SPECIFIED
- Extreme levels: NOT FIXED; "each asset will generate its own extreme levels" [01:30]

### Context / bias filter

- "Overbought and oversold levels are not fixed on the ROC" [01:30]
- "These levels are not fixed, but will vary depending on the market being traded" [09:00]
- "I don't like this approach at all. This strategy might work in a non-trending market, but during strong trends traders often get false signals" [09:30]
- "In a very strong uptrend the ROC oscillator could show readings outside the usual range" [10:00]

### Entry trigger

- ROC reaches extreme high/low values that historically preceded price reversals [09:00]
- Wait for price to confirm reversal: "watch for the price to start reversing to confirm the ROC signal" [09:00]

### Stop loss

NOT STATED

### Take profit / exit

NOT STATED

### Invalidation / skip conditions

- "This strategy might work in a non-trending market, but during strong trends traders often get false signals" [09:30]
- "these extreme values are highly subjective" [10:00]

### Claimed performance

"In a very strong uptrend the ROC oscillator could show readings outside the usual range... These overbought or oversold extremes could be monitored as they could indicate a trend reversal, but these extreme values are highly subjective" [10:00]

### Vagueness log

1. UNDEFINED-PARAM: ROC period NOT specified
2. UNDEFINED-RULE: How to identify "extreme levels"? Method to look at past readings and find breakpoints not specified
3. UNDEFINED-RULE: "overbought" and "oversold" are market-dependent; no criteria to define them for a new market
4. SUBJECTIVE: "extreme values are highly subjective" (speaker's own admission) [10:00]
5. UNDEFINED-PARAM: Stop loss NOT stated
6. UNDEFINED-PARAM: Profit target NOT stated
7. SPEAKER EXPLICITLY DISCOURAGES: "I don't like this approach at all" [09:30]

### Mechanizability

DISCRETIONARY

Identifying "extreme" ROC values requires defining what counts as extreme for each market and timeframe, which is inherently subjective. The speaker explicitly states these values are "highly subjective" and discourages this approach in strong trends. Cannot be reliably automated.

## Notable claims and caveats

- "Another potential problem with using the ROC indicator is that its calculation gives equal weight to the most recent price and the price formed a number of periods ago, despite the fact that some traders consider more recent price action to be of more importance" [10:30]
- "Using too small a number (like 9 for example) can lead to very choppy readings, while using a higher configuration setting could potentially lag the ROC to the point that signals can be very delayed" [03:00]
- "the ROC will provide little insight except for confirming the sideways movement" during consolidation [01:30]
- "There is no absolute number that can magically give the right settings" [02:30]
- "I don't like [the overbought/oversold] approach at all" [09:30]
- "it's important to keep an eye on the price action, on recent market swings and always look at the big picture, on multiple time frames, to increase you odds of trading in the right direction" [10:30]
- No discussion of commissions, spreads, slippage, or transaction costs
- No overall win rate or Sharpe ratio provided
