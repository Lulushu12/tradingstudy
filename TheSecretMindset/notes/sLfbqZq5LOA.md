# A Reliable Scalping Strategy I Discovered After 1 Month of Price Action Trading

- video_id: sLfbqZq5LOA
- url: https://www.youtube.com/watch?v=sLfbqZq5LOA
- duration: 16:00
- classification: MULTI-STRATEGY

## Summary

The video teaches a scalping and day trading strategy based on identifying double inside bars as contraction signals followed by expansive directional breakouts. The core concept trades both trend continuations and reversals based on market regime (trending vs. range-bound). Optional 200 EMA filter can bias trade direction. Key emphasis is on entry location quality at technical levels (support/resistance, trendlines, moving averages, Fibonacci, pivots, round numbers).

## Instruments and timeframes stated

- markets: stocks (Tesla), forex (GBP/USD), crypto (Bitcoin) [05:00, 09:00, 11:30]
- timeframes: 5-minute chart demonstrated [05:00]; principle applies to "lower time frames" [02:30]
- sessions/hours: NOT STATED

## Strategy 1: Double Inside Bar Trend Continuation

### Indicators and settings

- Inside bar detector: description provided ("finds and reveals all inside bars on the chart") [04:00], but specific indicator NOT named
- Inside bar definition: "a given bar's high and low are fully contained by the bar directly preceding it" [02:00]
- Double inside bar definition: "two consecutive 'inside bars' which have failed to breach the high and low of the previous bar" [02:30]

### Context / bias filter

- Market must show clear trend: "lower lows and lower highs" (downtrend) or "higher highs and higher lows" (uptrend) [05:00]
- "In a trending market, you will trade only with the trend, by trading continuation breakouts" [04:00]
- Preferred entry location quality: "near: 1. Levels of support and resistance 2. Trend lines 3. Moving averages 4. Fibonacci levels 5. Daily Pivots 6. Round numbers" [04:30]

### Entry trigger

Double inside bar pattern followed by a breakout in the direction of the prevailing trend.

Example (downtrend): "Here's our double inside bar setup. As we are near the resistance level of the range, the plan is to short a breakout to the downside. Price broke the upper level of the channel, but we ignore the signal. Remember, you don't want to fight the existing trend. Next candle brought a downside breakout, so we entered short." [05:00-05:30]

### Stop loss

"Stop loss goes on the other side of the channel, or above the previous swing high. It all depends on the size of the channel and recent price action." [05:30]

For long trades with EMA: "Stop loss below the channel and below the 200 EMA" [11:00]

### Take profit / exit

"as I'm trading the 5 minutes charts and I'm scalping, I target the next swing in the price structure, at least" [06:00]

"your trade should offer a positive risk to reward ratio" [06:00]

Examples show varied targets: 2:1 R:R [10:00], 3:1 R:R [07:30], 4:1 R:R [11:00], 2.3:1 [12:00]

Can use "a trailing stop, a breakeven stop, or whatever money management technique you prefer" [06:00]

### Invalidation / skip conditions

If already in an active trade, ignore other double inside bar signals in that same direction [06:30]

Ambiguous setups (e.g., double bottom near swing high in downtrend): "this situation isn't so clear. I still favor the short trade, but if the breakout occurs to the upside, I'll still risk a long trade" [08:30]

## Strategy 2: Double Inside Bar Range Reversal

### Context / bias filter

- Market is range-bound; price oscillating between defined support and resistance [04:30]
- "In a range bound market, you will sell the top of the range and buy the bottom" [04:30]

### Entry trigger

- Double inside bar near resistance → short the downside breakout
- Double inside bar near support → long the upside breakout

### Claimed performance

NONE CLAIMED. One explicit losing trade shown: "We lost the trade, despite the fact it was actually a pretty good signal" [11:00]

## Strategy 3: Double Inside Bar with 200 EMA Directional Bias

### Context / bias filter

- "If price is above the 200 EMA, you'll trade only long breakouts above the double inside bar setup" [09:30]
- "If price is below the 200 EMA, you'll trade only short breakouts below the double inside bar pattern" [09:30]

### Entry trigger

Double inside bar + breakout in EMA-confirmed direction.

Example: "Price is below the 200 EMA, so in this case we'll target short positions. Here's the signal. We have consecutive inside bars around this resistance area... As price broke the channel to the downside, we entered short" [09:30-10:00]

## Vagueness log

1. UNDEFINED-PARAM: Inside bar detection indicator is described functionally but NOT specifically named [04:00]
2. SUBJECTIVE: What constitutes a "clear downtrend" or "clear uptrend"? Exact number of lower lows / higher highs required? [05:00]
3. UNDEFINED-RULE: "Preferred locations" include support/resistance/trendlines/Fibonacci/pivots/round numbers, but no hierarchy or weighting provided [04:30]
4. UNDEFINED-PARAM: "Round numbers" — which round numbers? Every 100? Every 50? [04:30]
5. UNDEFINED-RULE: For range-bound markets, what defines the "top" and "bottom" of the range? Most recent high/low? [04:30]
6. UNDEFINED-PARAM: "Stop loss goes on the other side of the channel" — exact price-level calculation not specified; "It all depends on the size of the channel and recent price action" [05:30]
7. SUBJECTIVE: "Previous swing high/low" — how many candles back? Minimum move size to qualify as a swing? [05:30]
8. UNDEFINED-PARAM: "Target the next swing in the price structure" — which swing? By what criteria is the "next" swing chosen? [06:00]
9. VISUAL-ONLY: "I see a downtrend, lower lows, lower highs" — visual inspection without quantified threshold [05:00]
10. SUBJECTIVE: Risk-reward targets range from 2:1 to 4:1 with no rule for selecting the target in each case [06:00-11:00]
11. UNDEFINED-RULE: EMA filter rule reversed in ambiguous setups ("if breakout occurs to upside, I'll still risk a long trade") despite prior EMA bias [08:30]

## Mechanizability

PARTIAL

Double inside bar detection (checking if candle high/low is within previous candle's range) is fully computable. Breakout direction (above/below the double bar range) is mechanically identifiable. However, critical gaps prevent full automation: (1) stop loss placement discretion ("depends on channel size and price action"); (2) profit target has no objective rule (which swing to select); (3) "trend" and "range" regime detection lacks quantitative criteria; (4) "preferred locations" and "round numbers" add manual filtering; (5) the contradiction in the rule when facing ambiguous setups (EMA bias reversed) requires discretionary judgment. The setup signal is mechanizable, but entry timing and exit logic require human interpretation.

## Notable claims and caveats

- "Does it feel time and time again like you are being watched and your stops are being hunted? Then you are not alone. This is a common complaint of many retail traders." [00:00]
- "This is not a perfect strategy, you will encounter losing trades" [15:00]
- "you could put your own spin on it, additional confirmations or other types of analysis. If you can back up consecutive inside bars with other technical tools, it might be worth opening a position" [15:00]
- "Just make sure you don't overcomplicate it and stick to the main concepts of this strategy" [15:30]
- No mention of commissions, spreads, slippage, or transaction costs
- No win rate or Sharpe ratio provided
- One explicitly losing trade demonstrated [11:00]
