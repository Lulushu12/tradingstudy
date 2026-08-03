# How To Trade Multiple Time Frames | The Triple Screen System For Forex & Stock Trading

- video_id: m0HjACP6sC4
- url: https://www.youtube.com/watch?v=m0HjACP6sC4
- duration: 10:06
- classification: STRATEGY

## Summary

This video presents Alexander Elder's Triple Screen System, a multi-timeframe trend-following strategy that uses three chart timeframes with a ratio of 3-5 between each to identify entries at market corrections. The system uses the longest timeframe to confirm the primary trend direction (via trend indicator like Hull MA), the intermediate timeframe to identify an opposing correction and confirm momentum recovery (via oscillator like RSI), and the shortest timeframe to pinpoint the exact entry point (via price action like trendline breakouts). Exits use trailing stop losses.

## Instruments and timeframes stated
- markets: verbatim: "Forex, stock market"
- timeframes: verbatim: "Multiple; examples given: (weekly, daily, h4), (daily, 4h, 1h), (4h, 1h, 15m); time ratio between screens: 3-5" [02:00-02:30]
- sessions/hours: NOT STATED

## Strategy 1: Triple Screen System (Multi-Timeframe Trend Following)

### Indicators and settings
First Screen (Long-term trend):
- Trend indicator: Speaker uses "100 hull moving average line" [05:00]; alternatively "MACD" (Elder's original) or "your favorite trend indicator" [05:00]
- Period: NOT STATED for Hull MA (assumed 100 based on statement)

Second Screen (Intermediate correction):
- Momentum oscillator: Speaker uses "RSI" [05:30]; originally Elder used "MACD and force index"
- RSI threshold: "below 50" for sell signals in downtrend [06:00]; "above 50" for buy signals in uptrend [08:00-08:30]

Third Screen (Execution):
- Entry method: Speaker uses "simple price action, most of the times i search for trendline breakouts" [06:00-06:30]
- Period: NOT STATED

### Context / bias filter
[04:30-05:00] "The time to buy in the triple screen is when a bull trend has just undergone a correction and is beginning to turn up again. Conversely, the time to sell in the triple screen is when a bear trend has just undergone a correction and is beginning to turn down again."

[05:00-05:30] First screen determines trend direction using long-term indicator (100 Hull MA): identify if trend is bullish or bearish on the daily chart.

### Entry trigger
Entries require agreement (confluence) across all three screens:

Sell example (downtrend):
[05:30-06:00] "On this chart we're looking for the optimum time to execute the sell order. That means we look for evidence that the pullback is completing and the market is reaching an overbought point on this time scale."

[06:00-06:30] "On this chart we see this upslope trendline, which was broken to the downside, after a correction, in the direction of the primary trend on the daily chart." Enter short when trendline breakout occurs on 1h chart confirming downtrend.

Buy example (uptrend):
[08:00-08:30] "Any sell signals in this case would be ignored because the uptrend from the first screen has already filtered those out. We move to the third screen once we get an agreement from the first and second screen: that is, when the larger trend is up, and an intermediate decline has generated a buy signal from our oscillator."

[08:30-09:00] "We have a nice trend line breakout on the h1 chart, which gave us the green light to enter long."

### Stop loss
NOT EXPLICITLY STATED as a fixed level. 

[07:00] "For this sell order, the exit stop loss is gradually moved downwards as the market makes lower lows. This is done to lock in the profit."

[07:00] "The loss amount and the order sizes are set according to your desired risk limits."

### Take profit / exit
[06:30-07:00] "Normally there isn't any take profit defined for each order. I prefer to use a trailing stop loss."

[07:00] Use trailing stop loss: "exit stop loss is gradually moved downwards as the market makes lower lows" for short positions; inverse for long positions.

No fixed take profit level specified.

### Invalidation / skip conditions
[05:30-06:00] "If the upward correction is particularly strong, you need to wait." — Do not enter if correction is too strong, indicating possible trend reversal.

[08:00-08:30] "Any sell signals in this case would be ignored because the uptrend from the first screen has already filtered those out." — Ignore signals that conflict with primary trend direction.

No explicit skip conditions beyond trend confirmation and correction confirmation rules.

### Claimed performance
NONE CLAIMED

### Vagueness log
1. UNDEFINED-PARAM: First screen indicator (100 Hull MA) period is stated as 100, but Hull MA calculation is complex (NOT STATED which variant). MACD parameters also NOT STATED if used.
2. UNDEFINED-RULE: "Pullback is completing" [06:00] lacks quantifiable definition; depends on subjective price action interpretation.
3. UNDEFINED-RULE: "Overbought point on this time scale" [06:00] is subjective; RSI reading alone (e.g., above/below 50) is insufficient.
4. UNDEFINED-RULE: "Trendline breakout" is visual and requires manual identification [06:30]; exact definition of what constitutes a valid trendline NOT STATED.
5. UNDEFINED-RULE: "Correction is particularly strong" [05:30] is subjective; no threshold given for rejecting a setup.
6. UNDEFINED-PARAM: Trailing stop loss movement rule: "gradually moved downwards as the market makes lower lows" lacks definition (e.g., how many pips, how many lows).
7. SUBJECTIVE: Trend indicator choice is flexible ("your favorite trend indicator") [05:00], allowing significant discretion in bias determination.

### Mechanizability
PARTIAL. The trend confirmation on the first screen is mechanizable if Hull MA parameters are fixed (period: 100; direction above/below price). RSI thresholds on the second screen (above/below 50) are mechanizable. However, the third screen entry "trendline breakout" requires manual visual identification or complex algorithmic trendline detection. The trailing stop loss rule lacks specific parameters for "gradually moved as lower lows" are made. A basic skeleton can be coded, but trendline identification and stop movement require discretionary inputs or assumptions.

## Notable claims and caveats

- [00:00-01:00] Discusses the problem that single indicators fail under different market conditions; trend indicators fail in ranges, oscillators give premature signals in trends.
- [01:30] "The root of elder's triple screen is that it tries to time trade entries to coincide with market corrections or pullbacks."
- [04:00] "Triple screen doesn't have a definitive buy or sell signal. It works as a system of confirmations from one time frame to the next."
- [04:00] "Because while there are no rigid criteria, this does mean you can incorporate your own thinking into the strategy."
- [09:30] "Its big advantage is the confluence of time frames, with following only a long-term trend. It's not a perfect system by any means, but it surely reduces the risk of entering at wrong times in the market."

No mention of transaction costs, spread, slippage, or commission. No drawdown or losing streak warnings provided. The strategy explicitly acknowledges flexibility and subjectivity as features, not drawbacks.
