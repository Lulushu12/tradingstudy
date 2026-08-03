# Chaikin Money Flow Volume Trading Strategies To Find High-Probability Signals

- video_id: XsZI_Mn42z8
- url: https://www.youtube.com/watch?v=XsZI_Mn42z8
- duration: 11:08
- classification: MULTI-STRATEGY

## Summary

This video presents Chaikin Money Flow (CMF), a volume indicator that identifies accumulation/distribution pressure by comparing closing prices to the high-low range with volume confirmation. Three trading strategies are covered: (1) CMF Zero-Line Crossover—entering when CMF crosses above/below 0 with 200-EMA trend confirmation, (2) CMF Levels—trading above the 0.05 level for longs and below -0.05 for shorts to filter choppiness around zero, and (3) CMF Moving Average Crossover—using a 200-period MA on CMF with Ichimoku Kumo cloud as trend filter. The speaker emphasizes that CMF works best in trending markets, generates false signals in choppy ranges, and should not be used on very short timeframes.

## Instruments and timeframes stated
- markets: verbatim: "stocks (implied)"
- timeframes: NOT STATED for specific strategies; caution against M1/M5 (1-minute, 5-minute) [10:30]
- sessions/hours: NOT STATED

## Strategy 1: CMF Zero-Line Crossover with 200-EMA Trend Filter

### Indicators and settings
- Chaikin Money Flow: period: 20 or 21 (default) [01:00]; or 50 for longer-term [01:00]
- CMF threshold: 0 level [05:30]
- 200-period EMA: applied to close price [06:00-06:30]

### Context / bias filter
[01:30-02:00] CMF interpretation: "when the Chaikin Money Flow indicator is above 0-level this is a bullish signal; when the Chaikin Money Flow indicator is below 0-level this is a bearish signal"

[06:00-06:30] 200-EMA trend filter: "When the price trades above the 200-period exponential moving average, we consider taking only long entries. When the price trades below the 200-period exponential moving average we consider taking only short entries."

### Entry trigger
[05:30-06:30] Long entry: "We wait for the Chaikin Money Flow indicator to cross above the 0-level, above 200-EMA for a long entry"

Short entry: "we wait Chaikin Money Flow indicator to cross below the 0-level, below 200-EMA for a short entry"

Requirements:
1. CMF crosses above 0 (for long) or below 0 (for short)
2. Price is above 200-EMA (for long) or below 200-EMA (for short)

### Stop loss
NOT SPECIFIED

### Take profit / exit
NOT SPECIFIED

### Invalidation / skip conditions
[02:00] "A movement of the Chaikin Money Flow oscillator from negative to positive or vice versa does not suggest a change in trend. So remember this observation because in choppy markets the CMF generates many false signals."

Skip if market is choppy (trading between -0.05 and 0.05 CMF range) [05:00-05:30].

## Strategy 2: CMF Levels (0.05 / -0.05 Filter)

### Indicators and settings
- Chaikin Money Flow: period: 20-21 [01:00]
- Levels: 0.05 (upper filter), -0.05 (lower filter) [07:00]

### Context / bias filter
[05:00] Neutral zone definition: "values between -0.05 – 0.05 signals a decision-making period. When the CMF trades between these levels, the bulls and bears are putting pressure to take control of the market. This area is often marked by choppiness and is better to be avoided."

### Entry trigger
[07:00] Long entry: "Take long positions above the 0.05 level"

Short entry: "Take short entries below -0.05 level"

Levels act as filters to avoid choppy zero-line region.

### Stop loss
NOT SPECIFIED

### Take profit / exit
NOT SPECIFIED

### Invalidation / skip conditions
[07:00] Avoid trading between -0.05 and 0.05 (neutral zone).

## Strategy 3: CMF Moving Average Crossover with Ichimoku Trend Filter

### Indicators and settings
- Chaikin Money Flow: period: 21 (stated for this setup) [08:30]
- Moving Average applied to CMF: 200-period; longer-term preferred [08:00-08:30]
- Ichimoku Kumo cloud: trend filter [08:30-09:00]

### Context / bias filter
[08:30-09:00] Ichimoku cloud defines trend: "Buy only signals above the Kumo cloud...Sell only signals below the Kumo cloud"

[09:00-09:30] Price position relative to cloud: "We don't take entries when the price is inside the Kumo cloud. If a crossover between Chaikin Money Flow and the 200 EMA occurs when the market price is inside the Kumo cloud, we ignore the setup."

### Entry trigger
[08:30-09:00] Long entry: "Buy only signals above the Kumo cloud, when the Chaikin Money Flow crosses above the 200-period moving average"

Short entry: "Sell only signals below the Kumo cloud, when the Chaikin Money Flow crosses below 200-period moving average"

Conditions:
1. CMF crosses above its 200-MA (for long) or below its 200-MA (for short)
2. Price is above Kumo cloud (for long) or below Kumo cloud (for short)
3. Price is NOT inside Kumo cloud

### Stop loss
NOT SPECIFIED

### Take profit / exit
NOT SPECIFIED

### Invalidation / skip conditions
[09:00-09:30] "We could enter a trade once the price closes above or below the cloud, in the direction indicated by the crossover. But never when the price is inside."

Skip if price is inside Kumo cloud, even if CMF/MA crossover occurs.

### Claimed performance
NONE EXPLICITLY STATED

### Vagueness log
1. UNDEFINED-PARAM: CMF setting is "generally" 20-21 but can vary [01:00]; no specific optimization rule stated
2. UNDEFINED-PARAM: Stop loss NOT SPECIFIED for any strategy
3. UNDEFINED-PARAM: Take profit targets NOT SPECIFIED for any strategies
4. UNDEFINED-RULE: "choppy market" [02:00] — no quantified choppiness threshold
5. UNDEFINED-RULE: "false signals" [05:30-06:00] — frequency/type not mechanically defined
6. UNDEFINED-RULE: "new highs/lows" in CMF context [03:00] — relative to what period?
7. UNDEFINED-RULE: "confirms breakouts" [03:00] — specific CMF value or direction NOT STATED
8. UNDEFINED-RULE: "big gaps" [10:30] — no size threshold specified for CMF impact
9. UNDEFINED-PARAM: Moving average period applied to CMF: "longer-term preferred" but no specific recommendations (90, 200, 50?)
10. SUBJECTIVE: "Valid trades" examples shown but no rule for entry confirmation beyond crossover

### Mechanizability
PARTIAL. CMF calculation is mechanizable (if algorithm is provided). 200-EMA is mechanizable. However:
- Strategy 1: CMF crossing 0 is mechanizable; price vs 200-EMA check is mechanizable; but "choppy market" skip condition is subjective
- Strategy 2: CMF reaching 0.05/-0.05 is mechanizable; 0-level crossing still occurs, so stop-to-level rules needed
- Strategy 3: CMF crossing its MA is mechanizable; Ichimoku cloud calculation is mechanizable; but "inside cloud" detection requires defined cloud bounds

All strategies lack stop loss and take profit rules. A basic skeleton can be coded with crossover detection + trend filters, but complete mechanization requires: choppiness detection algorithm, Ichimoku cloud generation, and exit rules.

## Notable claims and caveats

- [00:00-00:30] "Chaikin Money Flow is a technical indicator which determines if an instrument is under accumulation or distribution."
- [00:00-00:30] "if the price closes near the high of the session with increased volume, the Chaikin Money Flow increases in value"
- [02:30] "The Chaikin Money Flow is also used by traders to confirm the strength behind an uptrend or a downtrend."
- [02:30-03:00] "During an uptrend, if a breakout of a resistance occurs while the CMF reaches new highs, this suggests that the bulls are taking control of the market."
- [03:00-03:30] "However, the Chaikin Money Flow has a flaw. The CMF is not handling gaps very well. For example, if a gap occurs on the upside and closes at a lower price, the money flow would give you a negative figure, despite the bullish price increase."
- [05:30-06:00] "But being a volume indicator, by itself, the CMF is not so reliable and it will offer many false signals. It's better to confirm the trend with another indicator."
- [08:00-08:30] "A longer-term moving average added on Chaikin Money Flow will work better than short-term moving average. A longer-term moving average will produce fewer signals."
- [08:00-08:30] "This approach will generate many false signals if you don't confirm the trend with other indicators."
- [10:00-10:30] "Chaikin Money Flow is a very useful indicator for confirming the direction of the main trend. It works well during trending market conditions and is very good at confirming the strength of the main trend."
- [10:00-10:30] "in a choppy market, many false signals are generated around the zero level, so be aware of this."
- [10:30] "Also, CMF value is not accurate when big gaps occur on the market so when you spot larger gaps, maybe you should re-analyze the setup."
- [10:30] "I also found the Chaikin Money Flow quite unreliable on smaller time frames like M1 or M5, so I would pay extra attention when using it for scalping."

No mention of transaction costs, spread, or slippage. No drawdown or losing streak analysis. The speaker explicitly cautions against using CMF alone, recommends trend confirmation via 200-EMA or Ichimoku, and warns of false signals in choppy markets and on small timeframes. Acknowledges CMF has difficulty with gaps on price charts.
