# Trading With EXIT Indicators To Lock More Profits (Chandelier Exit & Donchian Channel Strategies)

- video_id: fmS_rUcKF6c
- url: https://www.youtube.com/watch?v=fmS_rUcKF6c
- duration: 10:35
- classification: STRATEGY

## Summary
This video focuses specifically on trade exit strategies and presents two technical indicators designed to lock in profits and manage risk: the Chandelier Exit and Donchian Channels. The speaker emphasizes that proper exit management is often the difference between profitable trades and losing trades, and that staying in trades too long typically leads to emotional exits and losses. The video teaches how to use volatility-based exits and channel-based exits to ride trends while protecting capital.

## Instruments and timeframes stated
- markets: Stocks mentioned primarily
- timeframes: Daily charts mentioned; 22-period Chandelier Exit (based on 22 trading days per month); 20-period Donchian Channels are standard; 50-period Donchian mentioned as alternative [10:00]
- sessions/hours: NOT STATED

## Strategy 1: Chandelier Exit as Trailing Stop/Exit Indicator

### Indicators and settings
- Chandelier Exit: volatility-based indicator
- Average True Range (ATR): used in calculation [02:30]
- Default period: 22 (matches trading days per month) [02:30]
- Default multiplier: 3 × ATR [03:00]
- Alternative: Can increase multiplier (e.g., 5) for volatile stocks [05:00]

### Context / bias filter
Used primarily to maintain position in established trend until clear reversal occurs [02:00]
"High probability of a trend reversal whenever the price of a stock moves against the prevailing trend by a distance equal to three times the average volatility" [02:30]

### Entry trigger
NOT SPECIFIED in this video (focus is on exit)
Assumes trader is already in a position

### Stop loss
Chandelier Exit acts as dynamic stop loss:
- For long positions: "Chandelier Exit three average true range values below the period high" [03:00]
- For short positions: "Chandelier Exit is set three average true range values above the period low" [03:30]

### Take profit / exit
"When the price closes below the Chandelier Exit, you should re-evaluate your long position" [03:30]
For shorts: "If an advance strong enough to exceed this level is a sign that you might want to take your profits" [03:30]

### Invalidation / skip conditions
For volatile stocks: increase multiplier to avoid premature exits [04:30]
"Some stocks are more volatile than others and require a bigger buffer, which means that the multiplier should be increased" [04:30]

### Claimed performance
Examples shown on charts [04:00-05:00] demonstrating Chandelier Exit following strong trends

### Vagueness log
1. "Close below Chandelier Exit" for long: exact entry timing NOT STATED (UNDEFINED-RULE)
2. Multiplier adjustment: "some stocks are more volatile" but no criteria for when to increase (SUBJECTIVE)
3. How much to increase multiplier: NOT SPECIFIED (UNDEFINED-PARAM)
4. Entry trigger: NOT STATED (assumes position already exists)

### Mechanizability
FULL - Chandelier Exit is mechanically computable using ATR (or highest high/lowest low) with stated parameters (22 periods, 3 × ATR). Multiplier adjustments would need to be defined by user.

## Strategy 2: Donchian Channel Breakout Entry with Channel-Based Exit

### Indicators and settings
- Donchian Channels: highest high and lowest low over specific period [05:00]
- Default period: 20 [05:30]
- Alternative period: 50 [10:00]
- Based on "Turtle Trading" strategy [06:00]
- Alternative exit uses midpoint line of channel [09:30]

### Context / bias filter
Breakout of channel indicates trend development, not overbought/oversold (common misconception) [07:00]

### Entry trigger
"When a price action breaks through and closes above the upper Donchian band, this signals an upward movement and a possible buy signal." [07:00]
"When a price action breaks through and closes below the lower Donchian band, this signals a downward movement and a possible sell signal." [07:00]

### Stop loss
Original Turtle trading strategy uses "stop loss of two volatility units, which basically equals two to times the average true range of the last 20 periods" [08:30]
Placement: "just below the support for a long position, or just below the resistance for a short position" [08:30]

### Take profit / exit
Exit signal 1: "Breakout of the channel to the opposite side" [06:30]
- Long: Close below upper Donchian band
- Short: Close above lower Donchian band

Exit signal 2 (Alternative): "Touch of the midpoint line of the channel" [09:30]
"Using a 50-day period for the Donchian channels... long trade if there's a close above the channel with a closing of the trade when touching the midpoint line" [10:00]

### Invalidation / skip conditions
NOT STATED

### Claimed performance
Examples shown on charts [09:00] demonstrating trend riding
"Able to ride the trend until the break of the upper resistance line, which initiated a new uptrend afterwards" [09:00]

### Vagueness log
1. Entry timing precision (on break, on close above break): NOT SPECIFIED precisely (UNDEFINED-RULE)
2. Midpoint exit trigger: "when touching the midpoint" - exact entry/exit timing NOT SPECIFIED (UNDEFINED-RULE)
3. Position sizing: NOT STATED
4. Which exit method to use (opposite break vs midpoint): "depends on your trading risk aversion" (SUBJECTIVE)

### Mechanizability
FULL - Donchian Channels are mechanically computable (highest high/lowest low of last N periods). Channel breaks are detectable. Midpoint is mechanically defined as (high + low) / 2.

## Notable claims and caveats

- "The most emotionally and complicated aspect of trading is knowing how to set up take profit and stop loss orders" [00:00]
- "Two traders can use the same strategy entering at the same price on a chart, but record different results. Why is that? Because of trade management." [00:00]
- "If you enter a trade without any kind of exit strategy, you will put yourself in the situation to take premature profits or worse, to run losses" [00:00]
- "Money management is one of the most important aspects of trading often neglected by a lot of traders and investors" [00:30]
- "The complicated part when it comes to trading or investing is to exit a position when you have a respectable profit rather than waiting for the market to come back against you and exiting out of fear" [01:00]
- Psychological trap: "You will not want to exit a trade when it is in profit and moving in your favor as it feels like the trade will continue in that direction" [01:30]
- "Not exiting the moment the trade is significantly in your favor usually means that you will make an emotional exit because at some point the trade will come back crashing against your current position" [01:30]
- Chandelier Exit "helps you to avoid early exits and maximize returns" [02:00]
- Chandelier Exit reversal principle: "high probability of a trend reversal whenever the price of a stock moves against the prevailing trend by a distance equal to three times the average volatility" [02:30]
- "Sometimes you will see a strong uptrend but not know where to jump the trade. The Chandelier exit can be used to define the trend and set as a trailing stop loss" [04:00]
- Donchian Channels used in "turtle trading" strategy [06:00]
- "Trading with Donchian channels is similar to support and resistance trading" [07:30]
- Common misconception: "Many traders assume that a breakout above upper or lower Donchian channels signals an overbought and oversold area and a reversal could be on the cards. This assumption is wrong." [07:30]
- "If the market momentum is able to surpass Donchian upper channel, then an uptrend could be developing" [07:30]
- "Once a support level is broken, becomes a resistance level, and once a resistant line is broken, becomes a support line" [08:00]
- Midpoint exit trades off profit vs trend continuation: "If you use the midpoint, you will leave some profits on the table more often" [10:00]
- During strong trends, midpoint often acts as support/resistance for trend resumption [10:00]
- Exit choice depends on "risk aversion" [10:00]
- No discussion of transaction costs, spreads, slippage, or commissions
