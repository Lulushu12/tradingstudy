# ULTIMATE Moving Average Trading Guide (Only A+ Strategies)

- video_id: lRnR3UbNRww
- url: https://www.youtube.com/watch?v=lRnR3UbNRww
- duration: 28:11
- classification: MULTI-STRATEGY

## Summary
This video presents 14 chapters on moving average trading techniques, covering pullback patterns, slope analysis, channels, bounce patterns, envelopes, ribbons, displaced and adaptive averages, and clusters. The instructor emphasizes waiting for pullbacks rather than chasing breakouts, using slope to confirm momentum, and avoiding crossover strategies. Multiple timeframe analysis and mean reversion techniques are also covered.

## Instruments and timeframes stated
- markets: NOT STATED
- timeframes: Daily chart for trend direction, 1-hour chart for entry timing [20:30]
- sessions/hours: NOT STATED

## Strategy 1: Pullback to Moving Average After Breakout

### Indicators and settings
- Moving Average: 50-period exponential moving average [01:30]

### Context / bias filter
Price must break above the 50-period EMA with strong volume before the setup is valid [01:30]. This is an uptrend context.

### Entry trigger
Price breaks above the 50-period EMA with volume, rises 10-20 pips, then pulls back to touch the moving average. Enter when price touches the MA and shows signs of bouncing [01:30].

### Stop loss
NOT STATED

### Take profit / exit
NOT STATED

### Invalidation / skip conditions
Do not chase breakouts immediately. The pullback must occur and show confirmation before entry. If price does not pull back, skip the setup.

### Claimed performance
"Made easy 30 pips on that trade" [01:30]. No systematic win rate or R-multiple stated.

### Vagueness log
1. "Signs of bouncing" - SUBJECTIVE, not mechanically defined
2. "Strong volume" - UNDEFINED-PARAM, no volume threshold specified
3. Stop loss price level - UNDEFINED-RULE
4. Take profit price level - UNDEFINED-RULE
5. Definition of "clean break" - SUBJECTIVE

### Mechanizability
PARTIAL. The breakout and pullback can be coded using price above/below the 50-period EMA and volume confirmation, but the bounce signal, stop loss, and take profit levels require manual definition or assumption.

---

## Strategy 2: Moving Average Bounce Patterns

### Indicators and settings
- Moving Average: 20-period or 50-period EMA (market-dependent) [12:00]

### Context / bias filter
Strong uptrend must be present before the setup is valid [11:00]. Price must show a clean pullback to the moving average [12:00].

### Entry trigger
Price trends up strongly, pulls back to the MA, and shows either a pin bar or an engulfing candle at the moving average. Enter on the break of the reversal candle high [12:00].

### Stop loss
NOT STATED

### Take profit / exit
NOT STATED

### Invalidation / skip conditions
If the trend is not strong before the pullback, skip the setup [11:00]. If price does not show a reversal candle pattern, do not trade.

### Claimed performance
"Each bounce led to perfect moves" [12:30]. No specific numbers or win rate stated.

### Vagueness log
1. "Pin bar or engulfing candle" - VISUAL-ONLY, depends on visual chart pattern recognition
2. "Strong trend before pullback" - SUBJECTIVE, no quantitative definition
3. "Clean approach to the moving average" - UNDEFINED-RULE, not defined as computable
4. "Signs of buying interest" - SUBJECTIVE
5. Which MA to use (20 or 50) - UNDEFINED-RULE, requires market-specific backtesting [12:30-13:00]
6. Stop loss level - UNDEFINED-RULE
7. Take profit level - UNDEFINED-RULE

### Mechanizability
DISCRETIONARY. The reversal candle patterns (pin bar, engulfing) are visual and require discretionary judgment. While pullback and trend detection can be coded, the core entry signal depends on visual pattern recognition.

---

## Strategy 3: Moving Average Envelopes

### Indicators and settings
- Moving Average: 20-period or 50-period MA [18:00]
- Envelope offset: 2% to 3% above and below the MA [17:30]

### Context / bias filter
Works in both trending and ranging markets [17:00]. The envelope bands adapt to market structure automatically.

### Entry trigger
When price hits the upper envelope band, look for short setups. When price hits the lower envelope band, look for long setups [17:30].

### Stop loss
NOT STATED

### Take profit / exit
NOT STATED. Implied that price reverts toward the moving average (mean reversion) [16:30].

### Invalidation / skip conditions
Do not treat envelopes as only for sideways markets; they work in trends where price can ride the upper band [17:00].

### Claimed performance
"See how price bounced perfectly between the envelope bands. Upper band rejections led to profitable shorts. Lower band bounces led to profitable longs" [17:00-17:30]. No specific win rate or R-multiple.

### Vagueness log
1. Envelope percentage (2% or 3%) - UNDEFINED-PARAM, no guidance on which to use
2. Which MA to use (20 or 50) - UNDEFINED-PARAM
3. Stop loss level - UNDEFINED-RULE
4. Take profit level - UNDEFINED-RULE
5. "Bounced perfectly" - SUBJECTIVE

### Mechanizability
PARTIAL. Envelope bands can be calculated precisely from OHLCV, and entry signals (price touching bands) are computable. However, stop loss and take profit levels must be assumed.

---

## Strategy 4: Moving Average Mean Reversion (Extended Price)

### Indicators and settings
- Moving Average: 200-period EMA [23:00]
- Extension threshold: Price more than 3% away from the 200-period EMA signals extended price [23:00]

### Context / bias filter
Works best when slope is gentle or flat, not during strong uptrends [22:30]. Should only be used in ranges or mild trends, not robust uptrends [22:00].

### Entry trigger
When price is more than 3% away from the 200-period EMA, it is extended. Enter only on the first sign of reversal after a divergence at the top or bottom of the channel, or after a trendline breakout [23:00].

### Stop loss
NOT STATED

### Take profit / exit
Target the moving average [23:30]. Price was back at the EMA by the next day [23:00].

### Invalidation / skip conditions
If slope is steeply up, reversion trades are risky and should be avoided [22:30]. Do not trade if the trend is robust and strong.

### Claimed performance
"Easy 100 pip profit" after price gapped 4% below the 200 EMA and reverted the next day [23:00].

### Vagueness log
1. "Divergence at the top or bottom of the channel" - UNDEFINED-RULE, divergence type not specified (price? indicator?)
2. "Trendline breakout" - UNDEFINED-RULE, how to draw the trendline not explained
3. "First sign of reversal" - SUBJECTIVE
4. Stop loss level - UNDEFINED-RULE
5. "Gentle or flat" slope - UNDEFINED-PARAM, no threshold for slope angle

### Mechanizability
PARTIAL. The 3% extension threshold is computable, and the 200-period EMA is well-defined. However, the entry confirmation (divergence or trendline breakout) must be manually defined or assumed, making the strategy incompletely mechanizable without additional rules.

---

## Strategy 5: Moving Average Cluster Breakout and Bounce

### Indicators and settings
- Multiple Moving Averages: 20-period, 50-period, 100-period, and 200-period EMAs [26:30]

### Context / bias filter
Setup is valid when multiple moving averages converge at the same price level, creating a cluster [26:30].

### Entry trigger
If price bounces off a cluster, trade the bounce direction. If price breaks through a cluster with volume, trade the breakout direction [27:00].

### Stop loss
NOT STATED

### Take profit / exit
NOT STATED

### Invalidation / skip conditions
Clusters are only valid setups; if moving averages are not converged, there is no cluster to trade.

### Claimed performance
"Observe how the 20, 50, and 100-period moving averages all converged around this area. Well, price bounced over 100 pips off that cluster level" [27:30].

### Vagueness log
1. "Cluster" definition - UNDEFINED-PARAM, no specific distance or tolerance for convergence stated
2. "Bounce direction" - UNDEFINED-RULE, how to determine which direction is not specified
3. "Volume" - UNDEFINED-PARAM, no volume threshold for breakout confirmation
4. Stop loss level - UNDEFINED-RULE
5. Take profit level - UNDEFINED-RULE

### Mechanizability
PARTIAL. Cluster detection is computable (find where multiple MAs converge), and bounce/breakout mechanics can be coded. However, the proximity tolerance for a "cluster," volume confirmation threshold, and exit rules must all be assumed.

---

## Supporting Concepts and Filters (Not Complete Strategies)

### Moving Average Slope / Momentum Filter
Check moving average slope before every trade [03:00-03:30]. If steep upward, look for longs. If steep downward, look for shorts. If flat, stay out of the trade. This is a bias/confirmation filter rather than a complete strategy.

### Moving Average High-Low Channel
Use a moving average based on high/low prices instead of just close price to create a channel [03:30-04:30]. Price above channel = bullish bias (long opportunities at channel top). Price below channel = bearish bias (short opportunities at channel bottom). This provides context and structure.

### Fake-Out Filter
When price breaks a moving average, wait 15 minutes [06:00]. If it cannot stay on the new side with volume, it's probably fake. If it creeps back above the moving average within 10 minutes, this is a classic fake-out [06:30]. Check slope—if it's still pointing in your favor, the quick breach might be noise [06:30]. This is an invalidation/filter rule.

### Displaced Moving Averages
Use a 50-period EMA displaced forward 10 periods to create future support and resistance levels [08:00-08:30]. For shorter MAs, shift forward proportionally. This is a structure/visualization tool.

### Ribbon Trend Filter (Not Recommended as Standalone Strategy)
Use a 12-ribbon system with periods from 5 to 50 [14:30]. When lines fan out nicely, trade with the trend. When they tangle up, stay out [14:30]. Wide spaces mean strong trends; narrow spaces mean weak trends. This is a trend confirmation filter.

### Crossover Strategy (Explicitly Discouraged)
The speaker tested hundreds of combinations of moving average crossovers and found win rate was always under 20%, with average losing trades bigger than winning trades [09:30-10:00]. The instructor explicitly states: "Moving-average crossovers are probably the worst moving-average trading strategy ever created" [09:00]. **This strategy is NOT recommended and is excluded from mechanizability analysis.**

### Volume-Weighted Moving Average (Alternative Tool)
Using volume-weighted moving averages instead of regular moving averages can create more accurate support and resistance levels [18:00-19:30]. This is an indicator choice, not a complete strategy.

### Multiple Timeframe Analysis (Confirmation Framework)
Daily chart for trend direction; 1-hour chart for entry timing [20:30]. Use 10-period SMA on daily and 20-period on hourly. Both must agree before risking money [20:30]. Never trade when timeframes disagree; this filter alone improves win rate by 20-30% [21:30]. This is a confirmation filter and multi-timeframe framework.

### Adaptive Moving Averages (Alternative Tool)
Kaufman adaptive moving average adjusts sensitivity based on market volatility [24:30]. When markets are trending strongly, it speeds up. When choppy, it slows down [24:30]. Works especially well during news events and market open [26:00]. This is an alternative indicator choice.

---

## Notable claims and caveats

The instructor emphasizes that 99% of traders use moving averages wrong [00:00] and that chasing breakouts instead of waiting for pullbacks is the most common mistake [00:30].

The speaker warns that markets chop 70% of the time, making trend-based strategies risky in sideways conditions [10:00]. Crossover strategies are explicitly discouraged after testing hundreds of combinations with sub-20% win rates [09:30-10:00].

The value of multiple timeframe analysis is highlighted: "Last week I took a long trade on the hourly chart, not realizing the daily average was sloping downward. That daily line crushed my trade" [20:30-21:00].

No discussion of trading costs, spread, slippage, or commission. No mention of drawdown, losing streaks, or risk management except for the implied stop losses discussed in individual strategies.

Most performance claims are anecdotal ("easy 30 pips," "perfect moves") rather than systematic backtested results.
