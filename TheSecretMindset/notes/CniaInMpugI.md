# Trading Pivot Points With A Twist (Central Pivot Range Strategy For Forex & Stock Market)

- video_id: CniaInMpugI
- url: https://www.youtube.com/watch?v=CniaInMpugI
- duration: 11:02
- classification: STRATEGY

## Summary

This video presents the Central Pivot Range (CPR) strategy, a daily-level technique to identify support, resistance, and market sentiment. The strategy calculates a pivot range using the previous day's high, low, and close, then interprets intraday price behavior relative to that range. Long entries occur when price bounces off pivot range support or breaks through resistance to the upside; short entries occur when price easily breaks through support or rejects resistance. Stop losses are placed on the opposite side of the pivot range.

## Instruments and timeframes stated
- markets: verbatim: "Forex, stock market; examples: ExxonMobil"
- timeframes: verbatim: "daily pivot range, intraday"
- sessions/hours: NOT STATED

## Strategy 1: Central Pivot Range (CPR) Daily Support/Resistance

### Indicators and settings
- Daily Pivot = (Previous High + Previous Low + Previous Close) / 3; NOT STATED which period of "previous day"
- Half-Range = (Previous High + Previous Low) / 2
- Pivot Differential = Daily Pivot - Half-Range
- Pivot Range = Pivot +/- Pivot Differential (produces upper and lower bounds)

### Context / bias filter
[00:30] Determine market sentiment by comparing previous day's close to today's pivot range:
- Bullish bias if previous close > pivot range (closes above the range) [02:30]
- Bearish bias if previous close < pivot range (closes below the range) [02:30]
- Neutral if previous close is within the pivot range [09:00]

### Entry trigger
Multiple entry scenarios stated:

1. [05:30-06:00] Long entry: "market bounces off the pivot range" when identified as support, "the market has snapped back near the pivot range area and it reversed quickly." Trade after the bounce occurs.

2. [07:00-07:30] Short entry: "the market sliced easily through the pivot range" after approaching it from above. Enter short "once the stock does indeed trade below the pivot range."

3. [08:00-08:30] Short entry: "market touched the edge of the pivot range but it couldn't trade the resistance zone." Enter short expecting downward move.

4. [10:00] Long entry: "pivot range acting as resistance broken to the upside." Enter long after pivot range is broken above.

### Stop loss
[06:00] "your stop would be on the other side of the Peapod range" (opposite side of the pivot range from entry)
[07:30] "your stop at the top of the pivot range"
[08:30] "your risk to the upside would be the other side of the pivot range"
[10:00] "your stop is of course the bottom of the pivot range"

### Take profit / exit
NOT STATED. No explicit take profit levels or exit conditions are provided beyond reversal from the pivot range area.

### Invalidation / skip conditions
[04:30-05:00] Bullish bias is invalidated if "the market broke with a daily pivot range and traded lower." At this point, consider shorting.
[09:00] Do not trade while market is inside the pivot range: "you don't take any positions while the market is inside the pivot range" (neutral area).

### Claimed performance
NONE CLAIMED

### Vagueness log
1. UNDEFINED-PARAM: "Bounce off the pivot range" is not defined with specific price action rules (e.g., how many bars, what magnitude).
2. UNDEFINED-RULE: "The market sliced easily through" lacks quantification; "easily" is subjective.
3. UNDEFINED-RULE: "Selling intensity increased" is not mechanically defined.
4. UNDEFINED-RULE: Entry is implied to occur after bounce/break reversal, but exact candle/bar criteria for entry not specified [06:00].
5. UNDEFINED-RULE: "Rejection" of support/resistance is visual/subjective; no specific reversal confirmation rules stated.
6. UNDEFINED-PARAM: Take profit target is not specified.

### Mechanizability
PARTIAL. The pivot range calculation is fully computable from OHLCV of the previous day. However, the entry trigger "bounce off support" or "reverses at resistance" requires defining what constitutes a bounce/reversal in bars/pips/%, and take profit targets are entirely absent. A basic skeleton can be coded (e.g., long when price >= lower bound of range), but the actual entry reversal logic and profit-taking are discretionary judgments.

## Notable claims and caveats

- [00:30] The daily pivot range "can offer a certain bias about the current day's price action."
- [03:00-03:30] "The daily pivot range will help you to see where something has to happen. If the market is below the pivot range and makes a move upward it will meet resistance at that level."
- [04:00] "if the market settled within the daily pivot range it will be neutral."
- [04:30-05:00] "the market broke through the daily pivot range so easily and is likely to go much lower."
- [10:30] "using the daily pivot range is one of the most powerful ways to establish the potential movement of the upcoming day."

No mention of transaction costs, spread, slippage, or commission. No drawdown or losing streak warnings provided. The strategy concept originated from "mark fisher in his book the logical trader" [01:00].
