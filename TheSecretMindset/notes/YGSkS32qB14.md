# How to Trade Multiple Moving Averages (GMMA Forex & CFD Stock Guppy Trading Strategy)

- video_id: YGSkS32qB14
- url: https://www.youtube.com/watch?v=YGSkS32qB14
- duration: 11:44
- classification: STRATEGY

## Summary
The Guppy Multiple Moving Average (GMMA) strategy uses 12 exponential moving averages split into two groups to identify trend strength and reversals. The short-term group (3, 5, 8, 10, 12, 15-day EMAs) tracks trader activity, while the long-term group (30, 35, 40, 45, 50, 60-day EMAs) tracks investor activity. Wide separation between groups signals a strong trend; narrow separation or convergence signals consolidation or reversal. Trades are entered on crossovers of the two groups, pullbacks within trends, or breakouts of support/resistance, and should be avoided during consolidation periods.

## Instruments and timeframes stated
- Markets: Forex, CFD stocks [title]
- Timeframes: can be applied to intraday, daily, or weekly charts [10:30]; suitable for day trading, swing trading, or longer-term trading [10:30]
- Sessions/hours: NOT STATED

## Strategy 1: GMMA Trend and Crossover Trading

### Indicators and settings
- Indicator: Guppy Multiple Moving Average (GMMA)
- Composition: 12 exponential moving averages [00:00]
  - Short-term group (green): 3, 5, 8, 10, 12, 15-day EMAs [01:00]
  - Long-term group (red): 30, 35, 40, 45, 50, 60-day EMAs [01:30]
  - Tracks trader and investor behavior respectively [01:00], [01:30]

### Context / bias filter
GMMA works best in trending markets with clear directional bias [03:00]. Market sentiment is determined by:
- **Wide separation between groups** = strong, well-supported trend [03:30]
- **Narrow separation or lines crisscrossing** = weakening trend or consolidation [03:30]
- **Both groups moving horizontally/sideways with heavy intersection** = no trend; may be good for range trading instead [04:00]

Price direction agreement between groups indicates confirmation [05:30]. Do NOT trade when both groups agree to move sideways [04:00], [05:00].

### Entry trigger
**Primary Signal - Crossover Entry (Bullish):**
1. Short-term MA group (green) crosses above long-term MA group (red) [04:30]
2. Signals change in market sentiment toward bullish [04:30]
3. Avoid signal if price and MAs are moving sideways [05:00]
4. Following consolidation, pay attention to crossovers and separation [05:00]

**Primary Signal - Crossover Entry (Bearish):**
1. Short-term MA group crosses below long-term MA group [04:30]
2. Signals bearish trend change [04:30]
3. Avoid signal if price and MAs are moving sideways [05:00]

**Secondary Signal - Pullback Entry (Bullish):**
During a strong uptrend, when short-term MAs move back toward longer-term MAs (but do not cross) and then move back up, enter long trades [05:30]. This represents a buying opportunity within the trending direction.

**Secondary Signal - Pullback Entry (Bearish):**
Same concept applies to downtrends for entering short trades [05:30].

**Tertiary Signal - Breakout Entry:**
Enter long after price breaks above resistance with increased volume [09:00]. Enter short after price breaks below support with increased volume [09:00]. Look for agreement between short-term and long-term MAs to confirm trend direction [10:00].

### Stop loss
Short-term option: "Set the stop loss just above or below short term moving averages" [10:30]. 

Conservative option: "If you want more room, decrease your lot sizes and place it below or above the longer term moving averages" [10:30].

### Take profit / exit
Exit when short-term and long-term MA groups compress, indicating consolidation or reversal [08:00]. Exit on opposite crossover signal. No specific take profit targets stated.

### Invalidation / skip conditions
1. Do NOT trade signals when price and MAs moving sideways [05:00]
2. Avoid trading during consolidation periods when lines are crisscrossing or intersecting heavily [03:30], [04:00]
3. Crossover signals during consolidation often result in whipsaws [08:30]
4. When MAs are converging (narrowing), momentum is declining and reversal/consolidation could follow [06:30]

### Claimed performance
GMMA "will allow anyone to determine the overall trend of the market quickly and without personal bias" [02:30]. Wide separation between groups "helps confirm the price trend in the current direction" [10:00]. Claims "greatest returns when combining Guppy with price action" [11:00]. Breakout trading is "the starting point for future volatility increases, large price swings and, in many circumstances, major price trends" [09:30].

### Vagueness log
1. UNDEFINED-RULE: "Heavily intersected" or "crisscrossing" - what percentage or number of crossovers qualifies? [03:30]
2. UNDEFINED-RULE: "Well spaced apart" vs "narrow separation" - what distance threshold? [02:30]
3. UNDEFINED-RULE: "Lines start to separate" - how much separation triggers breakout? [05:00]
4. UNDEFINED-PARAM: Stop loss placement "just above/below" - how many pips/points? [10:30]
5. UNDEFINED-RULE: "Increased volume" for breakout confirmation - what volume level? [09:00]
6. UNDEFINED-RULE: Pullback entry - how close must short-term move to long-term without crossing? [05:30]
7. UNDEFINED-RULE: "Moving sideways" condition - what angle/slope threshold? [04:00]
8. UNDEFINED-RULE: Take profit levels NOT STATED
9. SUBJECTIVE: "Clear trade setup" determination [10:00]

### Mechanizability
PARTIAL — The GMMA calculation is fully mechanical (EMA values are computable from OHLCV). Crossover detection is mechanical. However, defining "wide vs narrow" separation, "heavily intersected," "crisscrossing," and determining when pullbacks should be traded requires threshold definitions. Stop loss placement, take profit levels, and volume confirmation thresholds are not specified.

## Notable claims and caveats
Speaker explicitly states: "I am not the biggest fan of moving average crossovers" [07:30]. Acknowledges major limitation: "Each EMA represents the average price from the past. It does not predict the future. Waiting for the averages to cross can at times mean an entry or exit that is far too late, as the price has already moved aggressively" [08:00].

Notes "All moving averages are also prone to whipsaws. This is when there is a crossover, potentially resulting in a trade, but the price doesn't move as expected and then the averages cross again resulting in a loss" [08:30].

GMMA "tends to underperform" during consolidation [11:00] and "runs into problems when price consolidates" [07:30]. Recommends combining with price action analysis to address consolidation weakness [08:30], [11:00].

Advocates using additional confirmations: RSI, chart patterns (channels, triangles, flags) [09:00], [10:00]. Never mentions transaction costs, slippage, or commission. No discussion of drawdown risk or losing streaks.
