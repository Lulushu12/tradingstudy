# The ONLY Moving Average Strategy That Hasn't Let Me Down

- video_id: 28H31JdMXaQ
- url: https://www.youtube.com/watch?v=28H31JdMXaQ
- duration: 10:51
- classification: STRATEGY

## Summary
This video teaches a single, high-conviction strategy based on detecting false moving average breakouts caused by institutional liquidity hunting. The core mechanism is identifying when price briefly breaks through the 50-period moving average, triggers retail trader stops, and then reverses back to continue the original trend. The strategy relies on recognizing four key components: an obvious trend, a short break below the MA, low volume on the break, and a liquidity sweep of a previous swing level.

## Instruments and timeframes stated
- markets: Gold, indexes, forex pairs mentioned in examples [06:00, 07:00, 08:30]
- timeframes: 50-day moving average explicitly stated [00:00]; examples appear to be intraday with references to candles [03:00]
- sessions/hours: NOT STATED

## Strategy 1: Moving Average Liquidity Trap (50-Period MA)

### Indicators and settings
- 50-period moving average (simple or exponential NOT STATED)
- No other indicators; volume is monitored but not an indicator per se
- "50-day moving average" and "50-period moving average" used interchangeably [06:00, 08:30]

### Context / bias filter
An obvious, clear trend must be established. [03:00]
Uptrend: "Higher highs and higher lows that are crystal clear" [03:00]
Downtrend: "Lower highs and lower lows, no ambiguity" [03:00]
Speaker states: "If I can't see the trend in three seconds, I don't trade it." [03:00]

### Entry trigger
Four sequential conditions must be met:

1. Price breaks through the 50-period MA in the opposite direction of the trend: "a short break of the 50 moving average. And I mean short. I'm looking for one to three candles. If it lasts more than five candles, I usually back out." [03:00-03:30]

2. Volume on the break is lower than average: "When I check the volume of that fake, it should be lower than average. Real fakes have conviction behind them. Many traders accumulate. High volume bars appear. Fake fakes are silent. The volume bar is smaller." [04:00]

3. Liquidity sweep: "The price doesn't just drop below the line. Go ahead and eliminate this previous minimum." [04:30] Price must break to a previous swing low (in downtrend fakes) or swing high (in uptrend fakes) where stops are clustered.

4. Entry signal: "Once all four components are present, I expect the price to return to the correct side of the moving average. In an uptrend, this means waiting for the price to close above the 50-day moving average again after the false breakout. That candle close is my entry signal. In a downtrend, I expect the price to close below it again after the false rise." [05:00]

### Stop loss
"My stop goes a little beyond the liquidity flow. If the price broke above a swing low during the trap, my stop goes just below that low. It is a tight stop, but it is protected behind the level that has already been swept." [05:30]

### Take profit / exit
"For targets, I look at the next significant level of the structure in the direction of the trend. Previous highs in an uptrend. Previous lows in a downtrend. This usually gives me at least 2R, often more." [05:30]

### Invalidation / skip conditions
1. If break lasts more than 5 candles: "If it lasts more than five candles, I usually back out." [03:00] "If the price breaks the moving average and stays on the wrong side for more than five candles, this is not a false breakout. This could be a real trend change." [03:30]

2. If volume is high on the break: "If the volume is high at break, be careful. This could actually be a real trend change, not a trap. Low volume is your confirmation that the move is fake." [09:30]

3. If all four components are not present: "If all four components are not present, I do not trade." [09:00] "The best configurations are obvious. If you look closely at it, it's not there." [09:30]

### Claimed performance
"This moving average strategy only works after the market first fools the wrong traders. But the second you apply this hidden liquidity rule, it turns into a system that averages 2.8R per trade." [00:00]
Also: "This usually gives me at least 2R, often more" on take profit targets [05:30]

### Vagueness log
1. Moving average type (SMA or EMA): NOT STATED (UNDEFINED-PARAM)
2. "Obvious" trend definition: Somewhat defined as "crystal clear higher highs/lows" but no quantitative threshold (SUBJECTIVE)
3. "Previous swing low/high": NOT DEFINED - how many prior swings, timeframe, which one to target (UNDEFINED-RULE)
4. "Liquidity flow" or "liquidity race": While examples are given visually, the exact definition is not quantitatively specified - relies on chart observation (VISUAL-ONLY)
5. "Significant level of structure": NOT DEFINED - speaker uses "next significant level" but criteria are not stated (UNDEFINED-RULE)
6. Volume comparison: "Lower than average" - average over what period NOT STATED (UNDEFINED-PARAM)
7. Position size: NOT STATED
8. Multiple examples shown (gold, indexes, forex) but no explicit statement that strategy works across all markets

### Mechanizability
PARTIAL - The 50-period MA and candle close can be coded mechanically. Volume comparison can be coded if the lookback period for "average" is defined. However, the core concept of "liquidity sweep" requires visual interpretation of whether price touched a specific prior swing level, and "obvious trend" requires subjective assessment. The strategy heavily relies on chart observation and pattern recognition.

## Notable claims and caveats

- "Only about 15 to 20% of mobile media breaches go as the manuals show. The other 80% looks exactly like what I just showed you: a liquidity trap." [01:00]
- Moving average breakouts "do not fail randomly. Fail intentionally" [01:00]
- The strategy is presented as working across multiple markets: "You've now seen this model in four different markets. The setup works the same every time. That makes it reliable." [09:00]
- Speaker explicitly warns against "forcing the setup": "This liquidity pattern occurs several times a day in the markets I follow. If all four components are not present, I do not trade." [09:00]
- High-conviction entry: "When I see an increase in liquidity combined with the other three components, a clear trend, a short pause, and low volume, I approach that trade with confidence." [04:30]
- Short stops are emphasized: "It is a tight stop, but it is protected behind the level that has already been swept." [05:30]
- No discussion of transaction costs, spreads, slippage, or commissions
- Speaker recommends backtest by reviewing charts: "Open the graphs. Pull up the 50-period moving average. Find the fake breaks from the last few days. Check the volume. Look for liquidity flow. See how the transaction would have unfolded." [10:00]
