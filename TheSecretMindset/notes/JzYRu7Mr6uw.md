# Trading With VWAP Indicator For Beginners (Best Ways To Trade Stocks & Forex With VWAP)

- video_id: JzYRu7Mr6uw
- url: https://www.youtube.com/watch?v=JzYRu7Mr6uw
- duration: 10:07
- classification: MULTI-STRATEGY

## Summary

This video covers the Volume Weighted Average Price (VWAP) indicator as a day trading tool with two main applications: VWAP breakout trades and VWAP pullback trades. VWAP is calculated as the sum of price multiplied by volume, divided by total volume, representing the average price a stock has traded throughout the day. The speaker explains that institutional traders use VWAP to minimize market impact when entering large positions, while retail traders use it as a trend confirmation and support/resistance level. The video presents two mechanical trading setups: (1) buying after price drops below and then closes above VWAP, and (2) buying pullbacks to VWAP in established uptrends. Stop losses should be placed at logical support/resistance levels or swing points, not close to VWAP itself.

## Instruments and timeframes stated
- markets: verbatim: "stocks, Forex"
- timeframes: verbatim: "intraday charts (1 minute, 15 minute); shorter-term charts preferred (1-minute or 5-minute)" [07:00-07:30]; caution against longer-term (30-minute, 60-minute) charts [06:30-07:00]
- sessions/hours: NOT STATED

## Strategy 1: VWAP Breakout

### Indicators and settings
- VWAP: calculated as (sum of price × volume) / total volume [00:00-00:30]
- VWAP data resets each trading day at open [08:30-09:00]

### Context / bias filter
[04:30-05:00] Breakout setup initiates during periods when "stock price drops below the VWAP. This can often signal that buyers are exiting their long positions, which lowers the price compared to the VWAP."

Bullish bias implied: Expectation that price will "bounce back and continue its upward movement" [05:00-05:30].

### Entry trigger
[05:00-05:30] Three-step entry process:
1. "wait for the stock to test the VWAP to the downside" — price must drop below VWAP line
2. "look for the stock to close above the VWAP" — candle closes above VWAP
3. "buy above the high of the candle that closed above the VWAP" — entry is above the high of the breakout candle

### Stop loss
[07:30-08:00] "If you use VWAP pullback trade, you should look to place your stop-loss on the other side of a key chart level. That level may be below a pivot point or previous strong support level."

[08:00-08:30] Alternative: "if there's no major level, you can also look to keep your stock on the other side of a recent swing point. So if you're long a stock that's making higher highs and higher lows, you can place your stop-loss just below the previous swing low."

Caution: [07:30] "A common mistake is to place your stops few points below the VWAP. You will be stopped out often of you place your stops close to the VWAP."

### Take profit / exit
NOT EXPLICITLY STATED. Implied exit: when price stops making higher highs and higher lows or reverses.

### Invalidation / skip conditions
[07:00-07:30] Do not use VWAP on longer timeframes (30-minute or 60-minute): "your VWAP data will greatly lag behind a shorter-term chart (like the 1-minute or 5-minute). On a longer-term chart, the speed at which the VWAP generates a signal could mean that you completely miss the move."

[07:30] "So, if you use VWAP, opt for the shorter-term charts."

## Strategy 2: VWAP Pullback

### Indicators and settings
- VWAP: calculated as (sum of price × volume) / total volume [00:00-00:30]

### Context / bias filter
[06:00-06:30] "To trade a VWAP pullback setup, you have to find a stock that's in a clear uptrend, consistently making higher highs and higher lows."

Bullish bias required: Only trade pullbacks in established uptrends.

### Entry trigger
[06:00-06:30] Multi-step entry:
1. Identify stock in clear uptrend with "higher highs and higher lows"
2. "stock price makes a pullback to the downside, returning to the VWAP level on the chart"
3. "buy the stock at the daily average price" (at VWAP level)

Entry is at or near the VWAP level during a pullback.

### Stop loss
[07:30-08:00] "If you take a VWAP pullback trade, you should look to place your stop-loss on the other side of a key chart level. That level may be below a pivot point or previous strong support level."

[08:00-08:30] Alternative: "if there's no major level, you can also look to keep your stock on the other side of a recent swing point. So if you're long a stock that's making higher highs and higher lows, you can place your stop-loss just below the previous swing low."

### Take profit / exit
[06:30-07:00] "After you enter your long, you're looking for price to continue its uptrend, gradually pulling the VWAP up along with it."

Exit when uptrend reverses or price stops making higher highs/lows. NOT MECHANICALLY SPECIFIED.

### Invalidation / skip conditions
[06:00-06:30] Skip if stock is NOT in "clear uptrend, consistently making higher highs and higher lows."

[07:00-07:30] Do not use on longer timeframes (30-minute or 60-minute) where VWAP lags significantly [06:30-07:00].

### Claimed performance
NONE CLAIMED explicitly.

### Vagueness log
1. UNDEFINED-RULE: "stock to test the VWAP to the downside" [05:00-05:30] — no specific magnitude or percentage below VWAP required
2. UNDEFINED-RULE: "close above the VWAP" [05:00-05:30] — unclear if close must be within a candle body, or just above the VWAP line
3. UNDEFINED-RULE: "buy above the high of the candle that closed above the VWAP" [05:00-05:30] — entry is "above" but by how much? Not specified
4. UNDEFINED-RULE: "clear uptrend, consistently making higher highs and higher lows" [06:00-06:30] — subjective; no count of required HH/HL specified
5. UNDEFINED-RULE: "pullback to the downside, returning to the VWAP level" [06:00-06:30] — how close to VWAP? Touching is sufficient, or does price need to close at VWAP?
6. UNDEFINED-RULE: "key chart level" [07:30-08:00] — not mechanically defined; requires subjective identification
7. UNDEFINED-RULE: "previous strong support level" [07:30-08:00] — no definition of "strong" provided
8. UNDEFINED-RULE: "recent swing point" [08:00-08:30] — how recent? No timeframe specified
9. UNDEFINED-PARAM: Take profit target not specified for either strategy
10. SUBJECTIVE: Entry confirmation relies on price action ("close above VWAP") without quantified rules

### Mechanizability
PARTIAL. VWAP calculation is mechanizable (if volume data available). Entry setups are partially mechanizable:
- Strategy 1: Detect price below VWAP, then close above VWAP, then buy above candle high (mechanizable with candle-by-candle logic)
- Strategy 2: Detect uptrend (higher highs/lows), detect pullback to VWAP, buy at VWAP (mechanizable with trend detection and distance thresholds)

However, critical gaps remain:
- Stop loss placement depends on "key chart level" or "swing point" identification (not mechanically defined)
- Take profit targets entirely absent
- Pullback magnitude in Strategy 1 not specified
- Entry offset "above the high" in Strategy 1 not quantified

A basic skeleton can be coded, but complete mechanization requires specification of: pullback thresholds, trend confirmation parameters, stop placement rules, and take profit targets.

## Notable claims and caveats

- [00:00-00:30] "The volume weighted average price (VWAP) is a trading benchmark used by traders that gives the average price a stock has traded throughout the day, based on both volume and price."
- [01:00-01:30] "VWAP lags price because it is an average based on past data."
- [01:30] "A rising VWAP, with the price above the VWAP line, means the price is likely in a short term uptrend. A declining VWAP, with the price below the VWAP line, means the price is likely in a short term downtrend."
- [03:00-03:30] "This is why day traders love the VWAP indicator, because more than often, the price finds support and resistance around the VWAP."
- [04:00] "VWAP is a simple indicator: the price is either above it or below it. When it comes to day trading, simplicity often rules."
- [04:00] "It can help you determine trend changes, often quicker than moving averages."
- [06:30-07:00] "Also, you have to be smart with where you place your stop-loss. A common mistake is to place your stops few points below the VWAP. You will be stopped out often of you place your stops close to the VWAP."
- [08:30-09:00] "VWAP is considered a single-day indicator, and is restarted at the open of each new trading day."
- [08:30-09:00] "VWAP is based on historical values and does not have predictive qualities."
- [09:00] "For this reason, it is best suited for intraday analysis."
- [09:00-09:30] "This is why VWAP lags price and this lag increases as the day extends."
- [09:30] "There are some stocks and markets where it will pinpoint entries just right and in others it will appear worthless."

No mention of transaction costs, spread, or slippage. No drawdown or losing streak warnings. The speaker cautions against placing stops too close to VWAP and warns that VWAP performance varies significantly by instrument. Explicitly states VWAP should be combined with price action.
