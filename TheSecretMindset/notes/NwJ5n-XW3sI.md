# Forex Swing Trading Strategies That Work (1 Hour & 4 Hour Strategy)

- video_id: NwJ5n-XW3sI
- url: https://www.youtube.com/watch?v=NwJ5n-XW3sI
- duration: 10:22
- classification: MULTI-STRATEGY

## Summary

The video presents three swing trading strategies applicable to forex, stocks, and crypto. Strategy 1 uses monthly pivots as magnet levels combined with supply/demand confluences and candlestick patterns. Strategy 2 employs three Bollinger Bands (periods 50, SD 1/2/3) to assess trend strength and identify pullback trades at support/resistance. Strategy 3 combines a 50-EMA channel (applied to high/low prices) with round-number psychology for directional breakouts. All three emphasize confluence-based entries.

## Instruments and timeframes stated

- markets: Forex, stocks, crypto (general) [00:00]
- timeframes: NOT STATED explicitly; title references "1 Hour & 4 Hour Strategy"
- sessions/hours: NOT STATED

## Strategy 1: Monthly Pivot Confluence with Supply/Demand

### Indicators and settings

- Monthly pivots: calculated from "previous month's high, low, and close" [00:00]
- Optional candlestick patterns: pin bars, engulfing bars [02:00]

### Context / bias filter

- Monthly pivots act as "magnet" levels; "They carry a lot more weight than your average daily pivot. That's because they represent a whole month's worth of price action" [00:00-00:30]
- Reliability increases with time spent: "The more time the price spends above the pivot, the more reliable it becomes as a support level. And, the more time the price spends below the pivot, the more reliable it becomes as a resistance level" [00:30]
- "Look for confluences between the monthly pivot and supply/demand areas" [01:00]

### Entry trigger (LONG)

"Let's say you're looking at a chart and you notice that the price is approaching a key demand area that lines up with a monthly pivot... If the price bounces off that area, it could be the start of a beautiful uptrend that you can ride for weeks or even months" [01:00-01:30]

Optional candlestick confirmation: "When you find a candlestick with a long wick, rejecting the monthly pivot, that's a really good signal" [02:00]

### Entry trigger (SHORT)

"If you see the price approaching a major supply area that coincides with the monthly pivot, it could be a sign that the buyers are about to run out of steam. If the price gets rejected at that level, it might be time to start hunting for short opportunities" [01:30-02:00]

### Stop loss

NOT STATED

### Take profit / exit

"ride for weeks or even months" [01:30] — no specific numerical targets

Additional context: "if the price breaks above the monthly pivot, it could be a sign that the buyers are in control... The pivot that once acted as resistance now becomes a new support, helping the price to reach new heights" [02:30]

### Invalidation / skip conditions

- "Of course, no level is unbreakable... sometimes the market will just keep moving with momentum, even on higher time frames. Even if the price does break through the monthly pivot, it can still give you valuable information about the strength and direction of the trend" [02:00-02:30]

### Claimed performance

NONE CLAIMED

### Vagueness log

1. UNDEFINED-RULE: Supply/demand areas are NOT formally defined; their identification method not stated
2. SUBJECTIVE: "Key demand area" — what criteria define "key"? [01:00]
3. UNDEFINED-RULE: "The price bounces off that area" — what constitutes a bounce? Exact candle close level? Magnitude? [01:30]
4. UNDEFINED-RULE: Pin bars and engulfing bars mentioned as candlestick patterns but NOT defined [02:00]
5. SUBJECTIVE: "Price gets rejected" — exact rejection pattern and entry timing not specified [01:30]
6. UNDEFINED-PARAM: Stop loss NOT stated
7. UNDEFINED-PARAM: Profit targets NOT stated (only vague "weeks or months" timeframe)

### Mechanizability

DISCRETIONARY

Monthly pivots are mechanically computable from prior month OHLC data. However, the strategy's core entries are discretionary: (1) supply/demand zones have no objective definition in the transcript; (2) bounce detection lacks mechanical criteria; (3) rejection patterns (pin bar, engulfing) are not mechanically defined; (4) stop and profit target placement are entirely unstated. Cannot be coded without inventing missing rules.

## Strategy 2: Triple Bollinger Bands (3 BB) Trend and Pullback

### Indicators and settings

- Bollinger Band 1: Period 50, Standard Deviation 1 [03:00-03:30]
- Bollinger Band 2: Period 50, Standard Deviation 2 [03:30]
- Bollinger Band 3: Period 50, Standard Deviation 3 [03:30]
- 50 EMA (middle line of bands) [03:30]

### Context / bias filter

Trend strength assessment:
- "When price is between the middle line, the 50 EMA, and the first band, that's a weak uptrend" [03:30-04:00]; "You can buy in this area, but only if you have other factors lining up" [04:00]
- "When price is between the first and second Bollinger Bands above the 50 EMA, that's a strong uptrend. There's a better chance that price will keep going up" [04:00-04:30]
- "When price is between the second and third Bollinger Bands, above the middle line, that's a very strong uptrend. Price is stretched and I would avoid buying if price goes outside the bands" [04:30]

Downtrend equivalent applies to lower bands [05:00-05:30]

- Look for confluence: "Looking for overlaps of major support and resistance levels with Bollinger Bands is a great way to find swing trading setups" [04:30]

### Entry trigger (uptrend pullback)

"When a market is in an uptrend (meaning price is above the middle Bollinger Band) and you find a confluence between a recent support or resistance level and one of the standard deviation bands, you can trade a bounce off that area" [05:00]

### Entry trigger (downtrend pullback)

"When price is in a downtrend (below the middle band) and a recent support or resistance lines up with one of the lower bands, a decent pullback trade might be setting up" [05:00-05:30]

### Stop loss

NOT STATED

### Take profit / exit

"Finding profit targets is very easy. You just aim for the next bands. The first take profit is at the second band, and the next target is the last band" [06:00]

"Always expect momentum to slow down when price reaches the next set of bands. That's why it's best to take some of your profits at these levels" [06:00]

### Invalidation / skip conditions

- NOT STATED

### Claimed performance

NONE CLAIMED

### Vagueness log

1. UNDEFINED-RULE: "Confluence between recent support/resistance and bands" — how far back in time? Minimum move magnitude to qualify as support/resistance? [04:30]
2. SUBJECTIVE: "Bounce off that area" — exact candle structure or price level not defined; when to enter on bounce? [05:00]
3. UNDEFINED-RULE: "Best to take some of your profits at these levels" — what percentage to take at each band? [06:00]
4. UNDEFINED-PARAM: Stop loss NOT stated
5. UNDEFINED-RULE: Hold remainder of position — exit timing not specified

### Mechanizability

PARTIAL

Bollinger Bands (period 50, SD 1/2/3) are mechanically computable. Support/resistance detection can be automated by identifying local highs/lows, though "recent" and "major" are subjective. Profit targets (next bands) are clear. However, critical gaps: (1) bounce entry timing not specified; (2) percentage of profits at each level not quantified; (3) stop loss entirely missing; (4) confluence definition vague. The setup structure is computable, but entry and exit logistics require manual interpretation.

## Strategy 3: 50-EMA Channel with Round Number Breakouts

### Indicators and settings

- Two 50-period Exponential Moving Averages: one applied to high prices, one to low prices [06:30]
- Round numbers: "levels that end in double or triple zeros" [07:00]

### Context / bias filter

- Trend determination by channel: "When the price is trading above the channel, it's a bullish signal" [06:30-07:00]
- "When the price is below the channel, it's a bearish signal" [07:00]
- Initial bounce confirmation: "an initial rejection of the channel is a good sign that the channel is holding firm and that the price is likely to respect it in the future" [09:00]
- Subsequent bounces validated: "When you have an initial bounce, be ready to trade the next bounces, near round numbers" [08:30-09:00]

### Entry trigger (LONG)

"If the price is in an uptrend, supported by the moving averages, and approaching a round number from below, you look to buy a breakout ABOVE the level" [08:00]

Second/third bounces: "When you have an initial bounce, be ready to trade the next bounces, near round numbers" [08:30-09:00]

### Entry trigger (SHORT)

"If the price is in a downtrend and approaching a round number from above, you look to sell a breakout BELOW the psychological level" [08:00]

### Stop loss

NOT STATED (implied: possibly related to channel reversal breach)

### Take profit / exit

NOT STATED

### Invalidation / skip conditions

"When the price is caught inside the channel for more than three candles, and is located near a round number, avoid taking a trade. In this situation, the market is experiencing consolidation... Trying to trade during this period is like trying to predict the outcome of a coin toss, it's like a gamble" [09:00-09:30]

Proper signal: "You want to see an immediate reaction around the channel, a quick rejection of the area" [10:00]

### Claimed performance

NONE CLAIMED

### Vagueness log

1. UNDEFINED-PARAM: Round numbers defined as "double or triple zeros" — unclear if this includes decimals (e.g., 1.0000?) or only whole numbers (1000, 10000) [07:00]
2. UNDEFINED-RULE: "Approaching a round number from below/above" — how close to the level counts as "approaching"? Within pips/percentage? [08:00]
3. UNDEFINED-RULE: Initial bounce as confirmation — what magnitude or duration qualifies as a bounce? [09:00]
4. UNDEFINED-RULE: Breakout entry timing — immediate on touch or after confirmation candle close? [08:00]
5. UNDEFINED-PARAM: Stop loss NOT stated
6. UNDEFINED-PARAM: Profit target or exit rules NOT stated
7. SUBJECTIVE: "Quick rejection of the area" — how quick? Exact candle count or magnitude? [10:00]

### Mechanizability

PARTIAL

EMA channel (high/low applied to 50-period EMA) is mechanically computable. Identification of round numbers is straightforward (1000, 10000, 100000, etc.). However, significant gaps prevent full automation: (1) what counts as "approaching" a round number lacks numerical precision; (2) bounce/rejection magnitude not quantified; (3) stop loss entirely missing; (4) profit targets not stated; (5) the three-candle consolidation rule is mechanical, but entry timing on breakout is discretionary. The skeleton is computable, but entry confirmation and exit logic require human judgment.

## Notable claims and caveats

- Monthly pivots described as "the secret weapon of swing trading" and "the big boss of support and resistance levels" [00:00-00:30]
- Triple Bollinger Bands strategy emphasizes that "price respects the bands" but shows example of price reaching lower bands [05:30]
- No discussion of commissions, spreads, slippage, or transaction costs
- No win rate, Sharpe ratio, or performance metrics provided
- "Avoid buying if price goes outside the bands" in very strong uptrend [04:30]
- Strategy applicable to "any market, whether it's Forex, stocks or crypto" [00:00]
