# The Moving Average No One Talks About | Volume Weighted Moving Average (VWMA) Trading Strategy

- video_id: FfHrlRQUOTs
- url: https://www.youtube.com/watch?v=FfHrlRQUOTs
- duration: 10:08
- classification: MULTI-STRATEGY

## Summary

This video covers the Volume Weighted Moving Average (VWMA) as a trading tool with multiple applications. VWMA weighs prices by trading volume, making it more responsive to volume confirmation than standard moving averages. The video presents four main approaches: (1) using VWMA with SMA to identify trends and volume confirmation, (2) using VWMA alone to identify trend direction, (3) using VWMA as dynamic support/resistance, and (4) trading VWMA breakouts. The speaker emphasizes that VWMA performs best in trending markets and should be combined with other confirmation signals.

## Instruments and timeframes stated
- markets: verbatim: "all markets"
- timeframes: NOT STATED specifically; mentioned: "fast-moving trend" and "slow-moving trend" requiring different period lengths [09:00]
- sessions/hours: NOT STATED

## Strategy 1: VWMA + SMA Trend and Volume Confirmation

### Indicators and settings
- VWMA: period: 50 (used in example) [01:30-02:00]; flexible based on trading style [09:00]
- SMA: period: 50 (used in comparison) [01:30-02:00]; flexible [09:00]

### Context / bias filter
[03:00-03:30] "When the 50 volume weighted moving average is between price and the 50 simple moving average SMA(50), then volume confirms we are trending in that direction."

Bullish bias: [04:00-04:30] "A volume weighted ma above an SMA indicates bullish conditions. So, if the volume weighted moving average moves above the simple moving average, a bullish trend change is likely."

Bearish bias: [03:30-04:00] "A volume weighted ma moving below an simple moving average indicates bearish conditions. So, if the volume weighted moving average crosses below the simple moving average, this implies that a bearish move is on the horizon."

### Entry trigger
Long entry: [04:00-04:30] "Once the price is able to break both the volume weighted ma and the SMA to the upside, you can start searching for long opportunities."

Short entry: [03:30-04:00] "If the price is able to break through both the volume weighted ma and the SMA a bearish trend is confirmed and you can start searching for short positions."

### Stop loss
NOT STATED

### Take profit / exit
[05:00-05:30] "Both moving averages closer together might suggest an exit point. This signal is pretty much the opposite of the previous one. You look for a contrary signal to the primary trend. For example, you have taken a long position and you notice no separation between the volume weighted ma and the simple ma. This is the moment where you might want to consider exiting the market and to collecting your profits."

Exit when VWMA and SMA converge (no separation).

### Invalidation / skip conditions
[04:30-05:00] "These tests can be considered as potential trend reversals. It doesn't mean that the market will reverse, it may continue its direction, like in this example, you just have to pay attention to possible turning points."

## Strategy 2: VWMA Solo - Trend Identification

### Indicators and settings
- VWMA: period: flexible based on trading style [09:00]; "fast-moving trend" uses faster (shorter period); "slow-moving trend" uses slower (longer period) [09:00]

### Context / bias filter
[06:00-06:30] Trend direction:
- "A possible uptrend is when the price is above a moving average and the slope of the moving average is upward"
- "A possible downtrend is when the price is below the moving average and its slope is downward"

### Entry trigger
Not explicitly defined; implied to enter when trend is confirmed by price position and slope.

### Stop loss
NOT STATED

### Take profit / exit
NOT STATED

### Invalidation / skip conditions
[06:00] "don't forget that a moving average is a lagging indicator, so it doesn't predict new trends, just confirms the market trends once they have been developed."

## Strategy 3: VWMA Support/Resistance Trading

### Indicators and settings
- VWMA: period: flexible [09:00]

### Context / bias filter
[07:00-07:30] "As the price finds it hard to break through, it means that the sellers are stronger than buyers. The volume weighted moving average above the price becomes a resistance and price is likely to bounce back offering short opportunities. Likewise when price stays above at the volume weighted moving average, it becomes a support and therefore is likely to bounce back, offering buy opportunities."

### Entry trigger
Long entry: [07:30-08:00] "Likewise when price stays above at the volume weighted moving average, it becomes a support and therefore is likely to bounce back, offering buy opportunities."

Short entry: [07:00-07:30] "The volume weighted moving average above the price becomes a resistance and price is likely to bounce back offering short opportunities."

### Stop loss
NOT STATED

### Take profit / exit
NOT STATED

### Invalidation / skip conditions
[07:30-08:00] "Like any other support and resistance level, price cannot hold forever, and sometimes these levels are violated and price breaks through."

## Strategy 4: VWMA Breakout

### Indicators and settings
- VWMA: period: flexible [09:00]

### Context / bias filter
NOT STATED

### Entry trigger
[08:00-08:30] "You can also take advantage of a strong break below or above the volume weighted moving average to trade a breakout. A classic way to trade a break out is to wait for a price retest after the break, to avoid a fake out. Another strategy for overcoming the problem with false signals is to wait a certain number of candles after the moving average line has been crossed by the price before you enter your trade."

Enter on breakout after: (1) price retest, or (2) waiting N candles after crossover.

### Stop loss
NOT STATED

### Take profit / exit
NOT STATED

### Invalidation / skip conditions
[08:30] "This way, you filter out a lot of the choppy price movements during times when the market is not showing any clear direction."

## Claimed performance
NONE CLAIMED

## Vagueness log
1. UNDEFINED-PARAM: Period selection is flexible and subjective; no standard recommended periods [09:00].
2. UNDEFINED-RULE: "Slope of moving average" is visually interpreted; no quantification for what constitutes "upward" or "downward" [06:30].
3. UNDEFINED-RULE: "Separation between" VWMA and SMA is not quantified; no threshold given [04:30].
4. UNDEFINED-RULE: "Volume confirms we are trending" [03:00-03:30] is not mechanically defined.
5. UNDEFINED-RULE: "Strong break below or above" is not defined quantitatively [08:00-08:30].
6. UNDEFINED-PARAM: Number of candles to wait after crossover is not specified ("wait a certain number of candles") [08:00-08:30].
7. UNDEFINED-RULE: "High selling pressure" is subjective; no quantification [07:00-07:30].
8. UNDEFINED-RULE: "Price retest" is not mechanically defined [08:00-08:30].
9. UNDEFINED-PARAM: Stop loss placement is not specified in any strategy.
10. UNDEFINED-PARAM: Take profit levels are not specified; exit only on VWMA/SMA convergence in Strategy 1.

### Mechanizability
PARTIAL. VWMA calculation is mechanizable (if algorithm is available). Price-vs-line and slope comparisons are mechanizable. However, all four strategies lack complete entry/exit specifications:
- Strategy 1: Entry requires "separation" between VWMA and SMA (quantifiable but threshold not stated); exit on convergence (quantifiable)
- Strategy 2: Entry is implicit from trend confirmation; no quantified rules
- Strategy 3: Entry on "bounce" (undefined); exit not stated
- Strategy 4: Entry requires "strong break" + retest OR N candles wait (parameters not specified); exit not stated

A basic skeleton can be coded with stated indicators and direction rules, but complete mechanization requires assumptions for separation thresholds, retest criteria, and candle wait counts.

## Notable claims and caveats

- [00:00-00:30] "When a market makes a strong move on volume, this means that the price movement is confirmed by a simultaneous rise in volume. So volume means strength."
- [01:00-01:30] "This is very important information because you can make better decisions when you add volume into your trading strategy."
- [02:00-02:30] "When the volume is stronger, the volume weighted moving average will follow price more closely, and when volume decreases, it will mimic a simple moving average."
- [03:00-03:30] "At the exact moment of the breakout, the volume weighted moving average was well above the SMA already, showing us that volume confirms the uptrend."
- [06:00] "However, don't forget that a moving average is a lagging indicator, so it doesn't predict new trends, just confirms the market trends once they have been developed."
- [09:30] "The volume weighted moving average is suited to trend following strategies, because this indicator performs best in trending markets."

No mention of transaction costs, spread, slippage, or commission. No drawdown or losing streak warnings. The speaker explicitly states VWMA is a lagging indicator and works best in trending markets, suggesting caution in choppy/range-bound conditions.
