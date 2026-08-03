# Ultimate RSI Trading Guide For Beginners + BEST Strategies To Trade With RSI Indicator

- video_id: fJ1_un39T1o
- url: https://www.youtube.com/watch?v=fJ1_un39T1o
- duration: 10:16
- classification: MULTI-STRATEGY

## Summary

This video presents five different trading techniques using the Relative Strength Index (RSI). The speaker warns against the common misconception of using only overbought/oversold levels and instead teaches how to combine RSI with support/resistance, divergences, trend lines, and moving average crossovers for confirmation. Emphasis is placed on avoiding false signals in ranging markets.

## Instruments and timeframes stated

- markets: Stocks (Apple, Tesla examples mentioned), general applicability implied
- timeframes: Multiple timeframes mentioned; H1 (one hour) minimum for trend line method [08:30]
- sessions/hours: NOT STATED

## Strategy 1: RSI Overbought/Oversold with Support/Resistance Confirmation

### Indicators and settings

- RSI: period = 14 (standard) [08:30], also mentions 5, 7, and 50 period alternatives [08:30]
- Overbought threshold: 70 [03:00]
- Oversold threshold: 30 [02:00]

### Context / bias filter

Do not use overbought/oversold levels in isolation. Combine with strong support and resistance levels at "areas of confluence" [02:30]. During strong trends, RSI can remain overbought or oversold for "days, weeks or even months" [02:00], so do not trade countertrend entries based on RSI alone. Only trade when RSI level coincides with a confluence area: price at resistance (for short), price at support (for long), and preferably with prior breakout levels [03:00-03:30].

### Entry trigger

For short: RSI reaches overbought level (70+) [03:00] while price is at a resistance level [03:00]. For long: RSI reaches oversold level (30 or below) [03:00] while price is at a support level. Wait for price to confirm inability to break the level before entry [03:30].

### Stop loss

NOT STATED

### Take profit / exit

NOT STATED

### Invalidation / skip conditions

Do not trade overbought/oversold signals during strong trending markets where price can remain overbought/oversold for weeks [02:00-02:30]. Do not trade without support/resistance confirmation [02:30].

### Claimed performance

The speaker shows example trades (Apple stock on 30-min chart, Tesla chart) and labels these as "no-brainer" trades when confluence is present [03:00], but provides no win rate or statistical performance claim.

### Vagueness log

1. UNDEFINED-RULE: "strong areas of support and resistance" - no definition of what constitutes "strong"; how many touches or price action patterns required
2. UNDEFINED-RULE: "areas of confluence" - no objective measure of how many confluent factors are sufficient; how to weigh different confluent elements
3. UNDEFINED-PARAM: Stop loss price level not stated
4. UNDEFINED-PARAM: Take profit price level or exit rule not stated
5. SUBJECTIVE: "important level" [02:30] - no objective criteria for identifying importance

### Mechanizability

PARTIAL. RSI calculation is mechanical. Support/resistance identification can be coded (e.g., swing highs/lows, round numbers), but "strong" levels and "confluence" detection requires subjective weighting and assumptions not provided by the speaker. Stop loss and take profit rules are completely missing.

---

## Strategy 2: RSI Divergence with Trend Line Breakout

### Indicators and settings

- RSI: period = 14 [08:30], or alternative periods 5, 7, 50 [08:30]
- Divergence type: when price makes new high but RSI does not [04:30]

### Context / bias filter

Identify divergences between price and RSI. Do not trade divergences blindly; they are "not an exceptional signal" [04:30]. Divergence alone does not guarantee reversal; price can continue in the trend despite divergence [04:30-05:00]. Divergence must be confirmed by price action, specifically a trend line breakout [05:00].

### Entry trigger

After identifying RSI divergence (e.g., price makes new high, RSI makes lower high), wait for price to break the trend line of the channel [05:00-05:30]. Example: bearish divergence with price forming a double top and RSI making lower highs; enter short when price breaks below the lower trend line of the upward channel [05:30]. Example: bullish divergence with double bottom and RSI making higher lows; enter long when price breaks above the upward trend line [05:30-06:00].

### Stop loss

NOT STATED

### Take profit / exit

NOT STATED

### Invalidation / skip conditions

Do not trade divergences without additional confirmation from price action or trend line breakout [05:00]. Divergences appearing during strong trends can be false signals leading to quick stop-outs [04:30-05:00].

### Claimed performance

The speaker illustrates one bullish and one bearish example with successful outcomes but provides no win rate or performance statistics.

### Vagueness log

1. UNDEFINED-RULE: Trend line definition - no specific rules for drawing or validating trend lines; method is acknowledged as subjective [08:00]
2. UNDEFINED-RULE: What constitutes a "valid" divergence - how many points on RSI must diverge from price
3. UNDEFINED-PARAM: Stop loss price level not stated
4. UNDEFINED-PARAM: Take profit price level or exit rule not stated
5. SUBJECTIVE: Trend line drawing and identification of divergence highs/lows require judgment

### Mechanizability

DISCRETIONARY. While divergences can be computed (comparing price peaks to RSI peaks), trend line drawing is acknowledged as subjective and imprecise [08:00]. Determining valid divergence points and confirming trend line breakouts requires human judgment. No stop loss or take profit rules provided.

---

## Strategy 3: RSI 50-Level Crossover

### Indicators and settings

- RSI: period = 14 [08:30]
- Crossover level: 50

### Context / bias filter

This method works only during trending market conditions [06:30]. Do not use in ranging or choppy markets, as it will generate false signals and "chopped out" trades [06:30].

### Entry trigger

Buy signal: RSI crosses above 50 [06:00]. Sell signal: RSI crosses below 50 [06:00].

### Stop loss

NOT STATED

### Take profit / exit

NOT STATED

### Invalidation / skip conditions

Do not use during range-bound or non-trending markets [06:30]. Signals are unreliable when market is consolidating.

### Claimed performance

The speaker shows an Apple chart with "excellent signals" during trending conditions [06:30] but provides no statistics.

### Vagueness log

1. UNDEFINED-RULE: What defines a "trending market" - no specific criteria given; how many bars or RSI bars above/below 50 needed
2. UNDEFINED-PARAM: Stop loss and take profit not stated
3. SUBJECTIVE: Market condition assessment (trending vs. ranging) is subjective

### Mechanizability

PARTIAL. RSI crossover at 50 is mechanically definable, but the requirement to trade only during "trending conditions" requires a separate trend filter that is not specified. Without a defined trend indicator or rule, a coder must assume one.

---

## Strategy 4: RSI with Moving Average Crossover

### Indicators and settings

- RSI: period = 14 [08:30]
- Moving Average applied to RSI: 50 period recommended [07:30], or 100 period [07:30]; short-term (e.g., 10 period) not recommended [07:30]

### Context / bias filter

Use only during trending markets [07:00-07:30]. Avoid range-bound markets where the approach "will lead to a lot of losing trades" [07:00-07:30].

### Entry trigger

Trade crossovers between RSI and the moving average applied to RSI [07:00]. Buy when RSI crosses above its moving average; sell when RSI crosses below it (inferred from crossover principle).

### Stop loss

NOT STATED

### Take profit / exit

NOT STATED

### Invalidation / skip conditions

Do not use in ranging markets [07:00-07:30]. Use longer-term moving averages (50 or 100 period) rather than short-term (10 period) for "fewer false signals" [07:30].

### Claimed performance

No specific performance claims or win rate provided.

### Vagueness log

1. UNDEFINED-RULE: "Trending conditions" - no specific definition or confirmation method
2. UNDEFINED-PARAM: Stop loss and take profit not stated
3. UNDEFINED-RULE: Whether to use 50 or 100 period MA on RSI is left to trader preference; no guidance on selection

### Mechanizability

PARTIAL. MA crossover is mechanically computable, but the requirement to trade only during trending markets requires a separate, unspecified trend filter.

---

## Strategy 5: Trend Line Drawing on RSI

### Indicators and settings

- RSI: period = 14 [08:30]
- Method: draw straight lines on RSI connecting support points (for uptrend) or resistance points (for downtrend) [08:00]

### Context / bias filter

Only use on H1 (one hour) or higher timeframes [08:30]. Do not use on lower timeframes due to "too much noise" [08:30]. A valid trend line should connect "two or more support points that define the trend" [08:00].

### Entry trigger

Entry when RSI trend line is broken [implied from description]. The exact entry mechanism is not explicitly stated; speaker only shows the method of drawing trend lines.

### Stop loss

NOT STATED

### Take profit / exit

NOT STATED

### Invalidation / skip conditions

Do not use on timeframes lower than H1 [08:30]. Only use with two or more confirmed support/resistance points [08:00].

### Claimed performance

No performance claims provided.

### Vagueness log

1. UNDEFINED-RULE: "Valid trend line" - requires two or more support points but no guidance on how many bars or what price distance constitutes distinct support points
2. UNDEFINED-RULE: "Support points" and "resistance points" on RSI - no definition of what constitutes a support point (e.g., local low, how many bars, how far apart)
3. UNDEFINED-PARAM: Stop loss and take profit not stated
4. SUBJECTIVE: Trend line drawing is explicitly acknowledged as "subjective, is not a precise science" [08:00]
5. UNDEFINED-RULE: Entry trigger not precisely stated

### Mechanizability

DISCRETIONARY. The speaker explicitly states that trend line drawing is subjective and not a precise science [08:00]. Identifying support/resistance points on RSI and drawing valid trend lines requires judgment. No entry, stop loss, or take profit rules are specified.

---

## Notable claims and caveats

The speaker strongly warns against the common misconception that RSI overbought/oversold levels alone constitute a trading signal; this approach "doesn't work" and traders "will not make money using the RSI in this way" [00:00-00:30]. He emphasizes that RSI is a lagging indicator [09:30] and must be combined with other tools and price action analysis [09:30]. He also warns that divergences require confirmation and are not "exceptional signals" [04:30]. During strong trends, RSI can remain in extreme territory for weeks or months [02:00]. The speaker recommends using the indicator "in combination with other tools" [09:30]. No mention of spread, slippage, or commission across all strategies.
