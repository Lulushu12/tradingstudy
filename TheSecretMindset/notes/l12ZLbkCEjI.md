# The Ultimate Guide To HULL Moving Average (From Novice To Pro)

- video_id: l12ZLbkCEjI
- url: https://www.youtube.com/watch?v=l12ZLbkCEjI
- duration: 10:05
- classification: TOOLING

## Summary

This video explains the Hull Moving Average indicator, its advantages over simple moving averages, and how to use it in trading. The speaker emphasizes using HMA slope rather than price crossovers, and demonstrates a dual-HMA approach for trend following. The video explicitly warns against trading HMA crossovers as they produce excessive false signals.

## Instruments and timeframes stated

- markets: NOT STATED
- timeframes: NOT STATED
- sessions/hours: NOT STATED

## Strategy 1: Dual Hull MA Trend Following (7/50 Period)

### Indicators and settings

- Hull Moving Average (50 period): period = 50, purpose = trend identification
- Hull Moving Average (7 period): period = 7, purpose = entry signals

### Context / bias filter

The 50-period HMA must be rising (for long) or falling (for short) to indicate the prevailing trend direction. Long trades only when "higher highs and higher lows" [08:30]; short trades when "lower lows and lower highs" [08:30].

### Entry trigger

For long: When the 7-period HMA "turns up" [07:30-08:00] and the 50-period HMA is pointing upwards [08:00]. For short: When the 7-period HMA "turns down" [07:30-08:00] and the 50-period HMA is pointing downwards.

### Stop loss

NOT STATED

### Take profit / exit

Exit when the "hook" of the moving average turns in the opposite direction [05:30]. The speaker states "you got in the trade once, captured the move and got out when the hook of the moving average turned upwards" [05:30] (in a downtrend).

### Invalidation / skip conditions

Do not trade during ranging/consolidation periods; only trade "during trending scenarios" [08:00]. Avoid trading the strategy "when the price crosses the hull moving average" [04:30-05:00] or when "two hull moving averages cross" [06:00-06:30].

### Claimed performance

NONE CLAIMED

### Vagueness log

1. UNDEFINED-RULE: "7 hull ma turns up" - not defined as a specific numerical change in slope or rate of change
2. UNDEFINED-RULE: "hook of the moving average" - not defined precisely; whether it refers to a specific candle bar turning point or a change in slope is unclear
3. UNDEFINED-RULE: "higher highs and higher lows" / "lower lows and lower highs" - no definition of what timeframe or bars count; how many bars needed to confirm this pattern
4. UNDEFINED-PARAM: Stop loss not mentioned; take profit level not mentioned
5. SUBJECTIVE: "trending scenarios" - criteria for identifying a trending market is subjective; "higher highs and higher lows" is subjective without specifics on how many bars

### Mechanizability

PARTIAL. The skeleton of dual-HMA slope comparison is mechanically computable, but the entry trigger (when HMA "turns up") and exit trigger (when "hook" reverses) lack precise computational definitions. A coder would need to assume what constitutes a "turn" or "hook" (e.g., three consecutive up bars, change in direction of slope, crossover of a reference level), which was not stated.

## Notable claims and caveats

The speaker is emphatic that price-crossover signals are ineffective and produce "a trader's nightmare" [06:00] of false signals, especially in ranging markets [06:00-06:30]. He also warns that HMA is "not quite consistent with reality" [09:00] and should not be used as a standalone system but only as confirmation for price action and support/resistance analysis [09:30]. The speaker explicitly dismisses MA crossover strategies as unprofitable long-term [06:30]. No mention of costs, spread, slippage, or commission.
