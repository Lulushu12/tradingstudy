# An Incredibly Easy Strategy to Trade Price Action Using ENGULFING Candlestick Pattern

- video_id: a6dblH5IopQ
- url: https://www.youtube.com/watch?v=a6dblH5IopQ
- duration: 10:09
- classification: STRATEGY

## Summary

The video teaches a trend-following strategy using engulfing candlestick patterns as entry signals. A bullish engulfing occurs when a green candle closes above the high of the previous red candle (enveloping its body). The strategy trades bullish engulfings in established uptrends after pullbacks, and bearish engulfings in downtrends. Entries are filtered by support/resistance confluence and optionally by the 200 EMA. Target is minimum 2:1 risk-reward ratio.

## Instruments and timeframes stated

- markets: NOT STATED (general application)
- timeframes: NOT STATED
- sessions/hours: NOT STATED

## Strategy 1: Bullish Engulfing Continuation in Uptrend

### Indicators and settings

- No indicators required (pure price action candlestick pattern)
- Optional: 200 EMA for confluence [09:00], support/resistance levels [08:00], pivot points, Fibonacci levels [09:30]
- Bullish engulfing definition: "a candle whose length completely covers the previous candle with a close above the high of the previous candle" [00:00-00:30]
- Body engulfment most important: "the green body of the second candle fully engulfs the whole previous candle" [01:00]; speaker emphasizes real body over shadows/wicks [02:00]

### Context / bias filter

- Uptrend established: "An uptrend is defined by higher highs and higher lows in price" [05:00-05:30]
- "The advancing waves are larger than the pullbacks, pushing the market higher" [05:30]
- Pullback occurs: "During an uptrend, you should take only long positions... Waiting for a pullback means you're getting a better price for the next wave of the trend when it unfolds" [05:30-06:00]
- Valid pullback constraint: "The pullback should not drop below the low of the prior pullback as this violates the rules of an uptrend" [06:00]

### Entry trigger

"With the trend determined and a pullback occurring, you just wait for the engulfing candle trade signal" [06:30]

"During a downtrend, wait until a down candle engulfs an up candle and vice versa for an uptrend" [06:30]

"The engulfing candle that occurs after a pullback in an overall uptrend is designed to get you into a trade as the next wave of the trend is likely to unfold" [06:30-07:00]

Optional confluence confirmation: at support/resistance level [08:00], with 200 EMA above [09:00]

### Stop loss

"for a long position... below the recent low" [07:00]

### Take profit / exit

"Our rule of thumb is to make sure your winners are at least two times bigger than your losers" [07:00]

Minimum 2:1 risk-reward ratio: "measure the distance between your entry point and where you placed the stop loss... Your target price should be at least 60 pips or 60 cents to compensate yourself for the risk you've taken" [07:00-07:30]

### Invalidation / skip conditions

- "No need to take a bullish engulfing candle in a downtrend or a bearish engulfing candle in an uptrend. If you do so, you're practically trading against the main direction" [06:30]
- "You cannot just enter a trade every time you see the engulfing pattern. Be smart. Use support and resistance and trade the pattern near those levels" [08:30]
- Pullback must respect prior pullback lows [06:00]

### Claimed performance

NONE CLAIMED

## Strategy 2: Bearish Engulfing Continuation in Downtrend

### Indicators and settings

- Bearish engulfing definition: "a small bullish candle followed by a larger red bearish candle covering or engulfing the small green candle" [04:00-04:30]
- "bearish engulfing pattern stands pure price action. What matters is that the number of sellers outweighs the number of buyers" [04:30]

### Context / bias filter

- Downtrend established: "A downtrend is defined by lower lows and lower highs in price" [05:30]
- "The declining waves are larger than the pullbacks, pushing the market lower" [05:30]
- Pullback occurs: "you wait for a pullback" [06:00]
- Valid pullback constraint: "The pullback should not rally above the high of the prior pullback. This violates the rules of a downtrend" [06:00]

### Entry trigger

"During a downtrend, wait until a down candle engulfs an up candle" [06:30]

Preferably at support/resistance confluence [08:30]

### Stop loss

"for a short position [stop loss is placed] above the recent high" [07:00]

### Take profit / exit

Minimum 2:1 risk-reward ratio [07:00]

### Invalidation / skip conditions

- Do not trade bearish engulfing in an uptrend [06:30]
- Trade only near strong support/resistance levels [08:30]

### Claimed performance

NONE CLAIMED

## Multi-Candle Extensions

The speaker notes that engulfing patterns can extend beyond two candles: "it doesn't matter how many candles you have forming a bullish engulfing candlestick pattern. What matters is that the body of the red candle is fully engulfed... multiple candles forming a bullish engulfing pattern" [03:30-04:00]

## Vagueness log

1. UNDEFINED-RULE: Engulfing definition — "completely covers" — does this require high-to-high and low-to-low match, or only open-to-close body coverage? [00:00]
2. SUBJECTIVE: Speaker emphasizes body over wicks as most important, "but one thing to remember is to learn how to read a pattern" — different traders disagree [01:30, 02:00]
3. UNDEFINED-RULE: "prior pullback" in uptrend — how many bars back to check? Minimum swing size? [06:00]
4. UNDEFINED-PARAM: "recent high/low" for stop loss placement — how many bars back? Most recent? Swing high/low? [07:00]
5. UNDEFINED-RULE: Pullback definition — "may move in the opposite direction of the trend or may just move sideways" — no minimum size or duration specified [06:30]
6. UNDEFINED-PARAM: Support and resistance levels — NOT defined; "major" and "strong" levels not specified [08:00, 08:30]
7. SUBJECTIVE: Trend, pullback, and support/resistance identification are visual assessments [various]
8. UNDEFINED-PARAM: Profit target is ratio-based (2:1 minimum) but reference level (swing high/low?) not always specified [07:30]

## Mechanizability

PARTIAL

Engulfing candle detection (comparing candle OHLC across two or more bars) is mechanically computable. 200 EMA is standard. However, significant gaps prevent full automation: (1) pullback validation (checking that it doesn't breach prior pullback extremes) requires swing detection, which is discretionary; (2) support/resistance identification is manual; (3) "recent high/low" for stop requires defining the swing lookback period; (4) confluence filtering adds discretion. The core engulfing signal is mechanizable, but entry filtering and stop placement require manual interpretation.

## Notable claims and caveats

- "Trading with the trend is one of the most effective things a trader learns" [00:00]
- "In other words, engulfing candlesticks are reversal patterns" [00:30]
- "The power of the bearish and bullish engulfing pattern is in following the trend. They are most powerful when the market takes a break, makes a correction, and then forms an engulfing pattern" [05:00]
- "bullish and bearish engulfing candlesticks are extremely powerful when they are used in conjunction with the existing trend and are having an extremely strong connotation especially around support and resistance areas and moving averages" [09:30]
- No specific win rate, Sharpe ratio, or performance metrics provided
- No discussion of commissions, spreads, slippage, or transaction costs
- Multi-candle engulfing patterns are valid (not just classic two-candle) [03:30]
