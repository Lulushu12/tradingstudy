# Ichimoku Trading Was Hard, Until I Found This Powerful Strategy (Cloud Trading Strategies)

- video_id: 9e7OUfKTw6Y
- url: https://www.youtube.com/watch?v=9e7OUfKTw6Y
- duration: 16:18
- classification: STRATEGY

## Summary
This video presents a multi-timeframe Ichimoku strategy that uses cloud color, price position relative to the cloud, baseline, and conversion line to identify trend direction across multiple timeframes. Two examples are shown: a swing trading approach using 4H-1H-15M timeframes, and a day trading approach using 1H-30M-5M timeframes. Entries are taken when baseline crosses above or below the 200 EMA on the entry timeframe.

## Instruments and timeframes stated
- markets: NOT STATED (examples shown for generic price charts)
- timeframes: Multiple timeframe analysis required; examples: 4H/1H/15M for swing trading [10:00-11:00]; 1H/30M/5M for day trading [11:30-12:30]
- sessions/hours: NOT STATED

## Strategy 1: Multi-Timeframe Ichimoku Swing Trading

### Indicators and settings
- Ichimoku Cloud (Conversion Line: 9 periods, Baseline: 26 periods, Lagging Span: 26 periods)
- 200 Exponential Moving Average

### Context / bias filter
Check three timeframes in order from highest to lowest. On the two highest timeframes, verify [10:00-10:30]:
- Price is above the Kumo cloud
- Price is above the baseline
- Kumo cloud is green (ideal but "not mandatory" on highest timeframe [10:30])

### Entry trigger
On entry timeframe (15M in example), enter when baseline crosses above the 200 EMA and baseline is above 200 EMA [11:00]

### Stop loss
Place stop on the opposite side of the 200 EMA [11:00]

### Take profit / exit
- Initial target: 2:1 risk-reward ratio [11:30]
- If trend is strong, can catch larger move and exit on opposite crossover of baseline and 200 EMA [11:30]

### Invalidation / skip conditions
If higher timeframes show conflicting signals (e.g., 4H bearish while 1H bullish), skip the trade [09:30]

### Claimed performance
"8 to 1 rescuer ratio" on rare occasions with trailing stop in backtesting [12:30]

### Vagueness log
1. "Green" Kumo on highest timeframe is not mandatory - no clear definition of when to reject based on cloud color alone
2. "Thick" vs "thin" cloud is subjective (not quantifiable as stated)
3. Crossover of baseline and 200 EMA occurs frequently - no filter specified for which crossovers are valid beyond timeframe alignment
4. "Trend is strong" (when to use trailing stop) is SUBJECTIVE

### Mechanizability
PARTIAL - The 200 EMA crossover is computable, multi-timeframe alignment is computable, but entry confirmation depends on subjective assessment of "thickness" of cloud and whether "trend is strong." The core skeleton is mechanizable but requires assumption-filling for full automation.

## Strategy 2: Multi-Timeframe Ichimoku Day Trading

### Indicators and settings
- Ichimoku Cloud (default settings)
- 200 Exponential Moving Average

### Context / bias filter
Check two higher timeframes [11:30-12:00]:
- 1H: Price below Kumo, price below baseline, Kumo red (ideal but not mandatory)
- 30M: Price below Kumo, price below baseline, Kumo red

### Entry trigger
On entry timeframe (5M), bearish crossover between baseline and 200 EMA [12:00-12:30]

### Stop loss
NOT STATED

### Take profit / exit
- Initial: 2:1 risk-reward ratio [12:30]
- Can use trailing stop based on recent swings or 200 EMA for higher ratio [12:30]

### Invalidation / skip conditions
If lagging span is still inside Kumo, ranging conditions persist - avoid entry [08:00]

### Claimed performance
"8 to 1 rescuer ratio" achievable with trailing stop in backtesting [12:30]

### Vagueness log
1. Baseline/200 EMA "bearish crossover" timing not precisely defined - multiple crossovers can occur
2. Stop loss placement is completely unspecified
3. "Recent swings" for trailing stop is VISUAL-ONLY and not defined as computable
4. When to exit on opposite crossover vs trail is SUBJECTIVE

### Mechanizability
PARTIAL - Crossover detection is computable, but stop loss is missing and trailing stop methodology is undefined. Risk management cannot be calculated without stop placement rules.

## Notable claims and caveats
- No discussion of costs, spread, slippage, or commission
- Claims "8 to 1 risk/reward ratio" are rare; no sample size or timeframe for this backtest given
- No mention of drawdown, losing streaks, or market conditions where strategy fails
- Strategy described as "multiple timeframe analysis" but rules for when timeframes disagree are vague beyond "don't enter"
