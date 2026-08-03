# Bollinger Bands Strategies THAT ACTUALLY WORK (Trading Systems With BB Indicator)

- video_id: 2G9fHBEsauE
- url: https://www.youtube.com/watch?v=2G9fHBEsauE
- duration: 11:15
- classification: MULTI-STRATEGY

## Summary

The video teaches three Bollinger Bands strategies: (1) Range trading: buy lower band, sell upper band in non-trending sideways markets; (2) Trend trading: buy pullbacks to lower band in uptrends, sell pullbacks to upper band in downtrends (direction of main trend only); (3) Squeeze breakout: identify consolidation (narrow bands), watch for expanding band "hooks" (upper rising, lower falling), and trade breakouts in direction of trend. Default settings are 20-period SMA with 2 standard deviations; higher SD (2.5-3.0) generates fewer, higher-probability signals.

## Instruments and timeframes stated

- markets: NOT STATED (general application)
- timeframes: NOT STATED
- sessions/hours: NOT STATED

## Bollinger Bands Setup

### Indicators and settings

- 20-period Simple Moving Average (middle band) [00:00]
- Upper band: 2 standard deviations above SMA [00:00]
- Lower band: 2 standard deviations below SMA [00:00]
- Default: (20,2) [02:00]
- Alternative: 2.5 or 3.0 standard deviation for higher probability [03:30-04:00]

### Statistical Properties

- 65% of price action within 1 SD [02:30]
- 95% of price action within 2 SD [03:00]
- 99% of price action within 3 SD [03:00]

## Strategy 1: Range Trading (Sideways Market)

### Context / bias filter

- "In a sideways market, when there isn't a clear trend on the chart, Bollinger bands provide very good support and resistance" [05:00]
- Bands should be parallel: "when the bands are parallel, the signal is even more powerful" [06:00]

### Entry trigger

"we want to sell at the upper bb and buy at the lower bb, when the bands are parallel, and preferably, if we see addition confirmation of a support or resistance" [06:00-06:30]

"buy when prices near the lower band and sell when prices near the upper range band" [06:00]

### Stop loss

NOT STATED

### Take profit / exit

- Buy at lower band → sell at middle band or upper band [04:00]
- Sell at upper band → cover at lower band or middle band [04:00]

### Invalidation / skip conditions

"This strategy is suited in non-trending markets, when there isn't a clear direction" [06:00]

Do NOT trade in trending markets using this approach [07:00]

## Strategy 2: Trend Trading (Directional Market)

### Context / bias filter

- Uptrend: "price is making higher highs and higher lows" [07:30]
- Downtrend: "price is making lower lows and lower highs" [07:30]

### Entry trigger (Uptrend)

"buy the lower bb in uptrends, when the price is making higher highs and higher lows" [07:30]

"we look for pullbacks or corrections, but in the direction of the trend, we don't chase reversals" [07:30]

### Entry trigger (Downtrend)

"we look to sell the upper bb during downtrends, meaning when the price is making lower lows and lower highs" [07:30]

### Stop loss

NOT STATED (implied: beyond opposite band or recent swing)

### Take profit / exit

NOT STATED; implied movement to middle band or opposite band

### Invalidation / skip conditions

"Just because prices hit the upper or lower Bollinger does not necessarily mean that it is a good time to sell or buy. Strong trends will 'ride' these bands" [07:00]

"price will be making new highs in an uptrend and new lows in a downtrend, hitting and exceeding the bands, quickly taking out the stops on trades taken directly on the bands" [07:00-07:30]

## Strategy 3: Bollinger Bands Squeeze Breakout

### Context / bias filter

"A narrow band means indecision on price movement and when this happens, it is almost always guaranteed that markets are about to move either up or down" [08:30]

"If the market has recently experienced a lot of volatility and the bands are far apart, this is a sign that the market will settle down and trade into a range in the near future" [08:30]

Squeeze identification: "You can visually identify when the price is consolidating as the lower and upper bands get closer together on the chart" [09:00]

### Entry trigger

Breakout signal: "Look at the hooks of Bollinger bands. We want to see the upper band pointing up and lower band pointing down" [10:00]

"if upper band is rising while the lower band is falling, after a period of consolidation and tight range, this signifies that a potential explosion in price action is about to occur, in the direction of the candlestick pushing against the band" [10:00-10:30]

Volume confirmation: "Expanding volume on a breakout is a sign that traders are expecting that the price will continue to move in the breakout direction" [09:30]

Trend alignment: "especially if this event occurs in the direction of the previously established longer-term trend" [09:30]

### Stop loss

NOT STATED

### Take profit / exit

NOT STATED

### Invalidation / skip conditions

"If the bands remain flat or just one band hooks while the other does not, the breakout isn't there yet" [10:00-10:30]

## Claimed performance

- "Studies have shown that the penetration of Bollinger bands with a standard deviation of 3 occurs rarely" [05:00]
- "on a 2.5 standard deviation or even a 3 standard deviation will generate fewer, but high-probability signals" [03:30]
- No specific win rate or Sharpe ratio provided

## Vagueness log

1. UNDEFINED-PARAM: "Near" the bands — how close? Touching? Within X% of band value? [05:30]
2. UNDEFINED-PARAM: "Additional confirmation of support or resistance" — what constitutes confirmation? [06:30]
3. UNDEFINED-RULE: Pullback definition in trending market — how deep? What prevents reversal vs. continuation? [07:30]
4. UNDEFINED-PARAM: Stop loss placement — NOT specified for any strategy
5. UNDEFINED-PARAM: Profit targets — NOT specified; only implied "opposite band"
6. UNDEFINED-RULE: Band "hooks" definition — what angle qualifies as "pointing up/down"? Exact slope threshold? [10:00]
7. UNDEFINED-PARAM: "Tight consolidation" duration — how long? Minimum narrowing duration? [09:00]
8. UNDEFINED-RULE: "The more vertical, the stronger the potential move" — quantified how? [10:30]
9. SUBJECTIVE: "Squeeze" identification — visual assessment of band narrowing [09:00]
10. UNDEFINED-PARAM: Volume confirmation — "expanding" means what? How much expansion? [09:30]

## Mechanizability

PARTIAL

Bollinger Bands calculation (20-period SMA and 2/3 SD) is fully mechanically computable. Band width and trend detection are mechanical. However, significant gaps prevent full automation: (1) "near" the band lacks quantitative definition; (2) pullback depth identification is discretionary; (3) band "hooks" and "slopes" require visual interpretation; (4) support/resistance confirmation is manual; (5) stop and profit targets not specified; (6) squeeze entry timing relies on subjective band narrowing assessment. The framework is mechanizable, but entry timing and exit placement require manual judgment.

## Notable claims and caveats

- "Bollinger bands are one of the most popular technical analysis tools" [00:00]
- "Bollinger bands seem to act like rubber bands that can only stretch so far before snapping back to the middle" [05:30]
- "the greater odds that price will be contained within the bands instead of penetrating them, one of the surest and most common ways of trading the bands is to buy when prices near the lower band and sell when prices near the upper range band" [05:30-06:00]
- "Strong trends will 'ride' these bands and wipe out any trader attempting to buy on the 'low' prices in a downtrend or sell on the 'high' prices of an uptrend" [07:00]
- "Timing is everything, however, and just we don't know how long the squeeze will last" [09:30]
- No specific win rate or Sharpe ratio provided
- No discussion of commissions, spreads, slippage, or transaction costs
