# I Made My Own AI Trading Bots & Indicators - Copy This (Free & Easy)

- video_id: 4jlAz--4YFU
- url: https://www.youtube.com/watch?v=4jlAz--4YFU
- duration: 25:46
- classification: TOOLING

## Summary

This video is a tutorial on using AI (Claude, Deepseek, O1) to create custom trading indicators and strategies in TradingView without coding knowledge. The speaker demonstrates five indicator builds: colored EMA, hourly pivot points, high-volume engulfing detector, body-size momentum indicator, and daily range boxes. The video also includes one complete strategy example using the momentum indicator combined with a 100 SMA filter. The focus is on the process of prompting AI to build tools, not on providing production-ready strategies.

## Instruments and timeframes stated

- markets: NOT STATED (mentioned stocks and other symbols for testing, but no specific market focus declared)
- timeframes: Multiple timeframes used in examples; speaker notes "I like using it on the 4-hour time frame" [13:00] for the momentum indicator, "30 minutes time frame" for strategy backtest [15:30]
- sessions/hours: NOT STATED

## Strategy 1: Momentum Crossover with SMA Filter

This is a strategy example embedded within a tooling-focused video. [14:00-17:00]

### Indicators and settings

- Momentum indicator: "measures the strength of price action over the last X candles. This indicator will count recent bars and measure the body of bullish candles, versus bearish candles" [10:00]. "Loop through the last X candles, to measure each body size, and to add them to either a bullish or bearish total" [11:00].
  - Look-back period: 10 candles [15:30]
  - Calculation: Sum of bullish candle body sizes vs. sum of bearish candle body sizes
  
- SMA filter: "100 SMA" [14:00], used as context filter. Later refined to "200 SMA as a filter" [15:30]

### Context / bias filter

"Enter long when bullish strength crosses above bearish strength, and price is above the 100 SMA. Enter short when bearish strength crosses above bullish strength and price is below the 100 SMA" [14:00]. Later optimization: "The best results were on the 30 minutes time frame, with the 200 SMA as a filter" [15:30]. "The strategy showed positive returns and a decent win rate" when "we're essentially trading with the more dominant market force, while also respecting the overall trend direction with the SMA filter" [15:30].

### Entry trigger

"Enter long when bullish strength crosses above bearish strength, and price is above the 100 SMA" [14:00]. "Enter short when bearish strength crosses above bullish strength and price is below the 100 SMA" [14:00]. "The strategy logic is to check for crossovers between the bullish and bearish strength lines, while confirming the price position relative to the 100 SMA. When all conditions align, the strategy enters a position" [14:00-14:30].

Technical implementation note: "One issue was with the crossover detection - we needed to make sure we were only entering on the bar where the crossover happened, at the candle close, not in the middle of it" [14:30].

### Stop loss

NOT STATED

### Take profit / exit

NOT STATED

### Invalidation / skip conditions

NOT STATED

### Claimed performance

"The backtest results were promising. The strategy showed positive returns and a decent win rate" [15:00]. "The best results were on the 30 minutes time frame, with the 200 SMA as a filter, and the indicator measuring the strength of the last 10 candles. This makes sense because we're essentially trading with the more dominant market force, while also respecting the overall trend direction with the SMA filter" [15:30]. "Sharpe ratio: relatively low" [16:00]. "Sortino ratio: relatively high. This is important because the Sortino ratio focuses specifically on downside risk - the bad volatility that hurts us - rather than all volatility. A high Sortino ratio means our strategy is making money, while controlling drawdowns effectively" [16:00-16:30]. The assistant "suggested we might improve performance by refining entry and exit conditions or adjusting position sizing. One specific recommendation was to test increasing position size, since the strategy appeared reliable enough to potentially handle larger positions" [16:30-17:00].

### Vagueness log

1. "Bullish strength crosses above bearish strength" - UNDEFINED-PARAM: The momentum indicator calculates sums of body sizes, but the exact crossover logic is not specified. Is it a simple crossing of two lines? Does it require confirmation?

2. "Price is above the 100 SMA" - UNDEFINED-PARAM: Does price need to close above? Exact threshold not stated.

3. "Candle body" measurement - UNDEFINED-PARAM: Speaker says "body of a candle tells us about strength" [10:30] and "measure each body size" [11:00], but does not specify: is the body calculated as (close - open) for bullish and (open - close) for bearish? In points, pips, or percentage?

4. "Promising backtest results" - VAGUE CLAIM: No specific numbers provided (win rate %, profit factor, max drawdown, etc.). Only relative statements like "positive returns" and "decent win rate" [15:00].

5. "Low Sharpe ratio" vs. "high Sortino ratio" - SUBJECTIVE: What constitutes "low" or "high" is not quantified.

6. Stop loss and take profit - NOT STATED: The strategy has no defined exit rules beyond entry conditions.

### Mechanizability

PARTIAL. The entry logic is computationally identifiable (compare sums of bullish vs. bearish body sizes over 10-candle window, check SMA position), but critical gaps remain: (1) body calculation method is implied but not formally specified, (2) crossover detection method is mentioned in passing [14:30] but not fully defined, (3) no exit rules are provided, (4) backtest results are claimed but not quantified (no win rate %, profit factor, max drawdown), (5) the "improvements" suggested by the AI [16:30] were not implemented in the video.

## No additional strategy content

The remainder of the video presents only indicator-building demonstrations (daily boxes, average daily range), not complete trading strategies. These tools are presented as aids to trading decisions but lack entry/exit logic.

## Notable claims and caveats

The speaker emphasizes that "the strategy doesn't try to predict the future. It just measures what's happening right now - which side is showing more strength - and trades accordingly" [16:30-17:00]. The speaker also notes that the process is iterative and error-prone: "When the code had bugs, I simply copied the error messages and asked the AI to fix them. And this takes minutes, not days or weeks of debugging" [23:30].

The speaker suggests that the strategy is "a decent combination of high returns, high win rate, and controlled risk" [17:30] but provides no absolute performance metrics (win rate %, Sharpe ratio number, max drawdown, etc.). The backtest used only the momentum indicator with a 200 SMA filter on a 30-minute timeframe.

The video does NOT mention transaction costs, slippage, spread impact, or commission. No forward-test or live trading results are discussed. The speaker notes this strategy will require ongoing adjustment: "So I'll keep adjusting and back testing it in the future!" [17:30].

The speaker does NOT provide entry parameters for the ADR indicator (lookback period used is mentioned as "usually 20 days" [22:00]) or exact usage rules for the Daily Boxes indicator beyond visual pattern recognition.
