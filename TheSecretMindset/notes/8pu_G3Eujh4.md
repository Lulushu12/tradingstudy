# Best Indicator To Trade Market Cycles (Schaff Trend Cycle Forex Trading Strategy)

- video_id: 8pu_G3Eujh4
- url: https://www.youtube.com/watch?v=8pu_G3Eujh4
- duration: 10:21
- classification: STRATEGY

## Summary

This video presents the Schaff Trend Cycle (STC) indicator, a leading oscillator that combines MACD's exponential moving averages with cycle theory and stochastic smoothing to generate faster trend signals than MACD alone. The strategy involves identifying the primary trend direction, then taking buy signals when STC crosses above 25 and sell signals when STC crosses below 75, with confirmation via candle direction or price action. Exits occur when the signal line reverses at opposite thresholds or via alternative methods like trailing stops. The speaker cautions that STC can get stuck in overbought/oversold conditions for extended periods.

## Instruments and timeframes stated
- markets: verbatim: "currency markets, all markets; examples: Tesla chart, Forex"
- timeframes: verbatim: "intraday charts, such as five minutes or one hour charts, as well as daily, weekly, or monthly time frames" [01:00-01:30]
- sessions/hours: NOT STATED

## Strategy 1: Schaff Trend Cycle with Trend Filter

### Indicators and settings
- Schaff Trend Cycle (STC):
  - Short-term EMA: 23 (default) [03:00]
  - Long-term EMA: 50 (default) [03:00]
  - Cycle: 10 (default) [03:30]
  - Thresholds: 25 (uptrend/oversold level) [05:00], 75 (downtrend/overbought level) [05:00]
- Trend filter: Price action (higher highs and higher lows for uptrend, lower lows and lower highs for downtrend) [08:00-08:30]
- Confirmation: Candle direction or other technical indicators [06:00-06:30]

### Context / bias filter
[08:00-08:30] Apply trend filter first: "look to take only buy signals, when the indicator breaches 25" in uptrends; "take only shorts when the STC crosses below 75" in downtrends.

Trend identification via price action: "higher highs and higher lows" for uptrend, "lower lows and lower highs" for downtrend [08:00-08:30].

### Entry trigger
Buy entry: [06:00-07:00] "When the indicator goes above the 25 line, the trend is believed to be taking a positive turn (according to the indicator). It is when traders consider opening a buy position, but only if the confirmation is received. For example, a candle after current one that moves in the same direction can be considered a confirmation."

[07:00-07:30] "When the signal line breaches 25 and is heading up, this is a possible buy, or a long position"

[08:00] Developer recommendation: "entering on the second candle up for longs"

Sell entry: [06:30-07:00] "When the indicator goes below the 75, some traders consider opening a sell position, of course with confirmation."

[07:00-07:30] "when the signal line breaches 75 and is pointing down, this is a potential short"

[08:00] Developer recommendation: "the second candle down for shorts"

### Stop loss
NOT EXPLICITLY STATED. General statement: [07:00] "should be used in conjunction with other technical analysis tools, never on its own" implies additional risk controls needed.

### Take profit / exit
[07:30] "One exit possibility is when the short trade hits the bottom and breaches the 25 level and when the long trade hits the top and breaches 75 level."

[07:30] "But if the signal line is pointing in the right direction, you may choose to stay in the trade since currencies can easily trend to the high 90 level at the top and near zero at the bottom."

[09:30-10:00] Alternative exit methods: "you need to have an alternative exit plan, maybe a trailing stop, or a fib target, to get the most profit out of your trade."

### Invalidation / skip conditions
[05:00-05:30] "When the indicator is between the 25 and the 75 lines, the trend is developing in one of these two directions." — Do not trade in the neutral zone (between 25 and 75).

[08:00-08:30] Only trade signals that align with the primary trend direction (do not trade counter-trend signals).

### Claimed performance
NONE CLAIMED explicitly, but implied positive references to "decent signals" [08:30].

### Vagueness log
1. UNDEFINED-RULE: "Confirmation is received" is subjective; examples given (next candle, other indicators) but no specific rules [06:00-06:30].
2. UNDEFINED-RULE: "Candle after current one that moves in the same direction" is vague ("after current one" implies next candle, but exact entry bar NOT STATED).
3. UNDEFINED-RULE: "Price action, like paying attention at market swings like higher highs and higher lows" is visually subjective [08:00-08:30].
4. UNDEFINED-RULE: Trend direction identification is NOT mechanically defined; visual interpretation required [08:00-08:30].
5. UNDEFINED-PARAM: Stop loss placement is not specified.
6. UNDEFINED-RULE: Exit at opposite threshold (25 for shorts, 75 for longs) is stated but conditional ("if the signal line is pointing in the right direction") [07:30].
7. UNDEFINED-PARAM: "Alternative exit plan" such as trailing stop amount or Fibonacci target NOT SPECIFIED [09:30-10:00].
8. SUBJECTIVE: "Readings of other indicators that go in line with STC can also be treated as a confirmation" [06:00-06:30] requires undefined confirmation source selection.

### Mechanizability
PARTIAL. STC calculation is mechanizable (if algorithm is available; parameters: 23, 50, 10 are specified). Threshold crossings (25, 75) are mechanizable. However:
- Trend filter identification (higher highs/lows vs lower lows/highs) requires discretionary swing identification or algorithmic pattern matching
- Confirmation via "next candle direction" or "other indicators" lacks specificity
- Alternative exit via "trailing stop" or "Fibonacci target" requires parameter specification
- Entry bar selection ("second candle up/down") is slightly more defined but assumes swing point identification

A basic skeleton can be coded (STC crosses threshold in trending direction), but full mechanization requires specific rules for trend identification and confirmation criteria.

## Notable claims and caveats

- [00:00-00:30] "The Schaff trend cycle (STC) is a forward-looking, leading indicator that generates faster, more accurate signals than other indicators, such as the MACD because it considers both time (through cycles) and moving averages."
- [00:30-01:00] "By contrast, STC's signal line enables it to detect trends sooner. In fact, it typically identifies up and downtrends long before MACD indicator."
- [01:30-02:00] "It's basically a combination of leading and lagging indicators."
- [04:00-04:30] "One of the problems with the STC indicator is that the signal line can get stuck in overbought or oversold territories for extended periods. This is because cycles haven't completed their time."
- [07:00-07:30] "STC is a leading indicator, which means that it sends a signal before the price move has occurred. It also means that it lacks the accuracy of lagging indicators and should be used in conjunction with other technical analysis tools, never on its own."
- [09:30-10:00] "While I find this indicator to be reliable when the signal is caught correctly, there is one problem. The signal can stay in overbought or oversold conditions for extended periods."

No mention of transaction costs, spread, slippage, or commission. Drawdown and losing streak warnings are not discussed. The speaker explicitly cautions that STC is a leading indicator prone to false signals and should be combined with other tools; cautions about signal getting stuck in extremes are explicitly stated.
