# Elite Renko Trading Strategy (How To Trade Renko Charts Successfully)

- video_id: CtelYJ5lFr8
- url: https://www.youtube.com/watch?v=CtelYJ5lFr8
- duration: 10:51
- classification: STRATEGY

## Summary

This video presents a Renko chart trading strategy combining 100-point Renko bricks with a 10-period SMA for trend direction and On-Balance Volume (OBV) for momentum confirmation. The strategy filters entries by requiring that Renko bars form above (for longs) or below (for shorts) the SMA, then confirms with OBV moving to new highs (for longs) or lows (for shorts). Stop losses are placed 2 Renko bricks away from entry; minimum take profit is 3 Renko bricks away. The speaker emphasizes entering when the SMA slope points in the trade direction, avoiding flat SMA conditions, and using OBV to verify that volume confirms the price direction. Exits can be manual at SMA crossover or trailing stops to capture larger moves.

## Instruments and timeframes stated
- markets: verbatim: "stock market; example shown"
- timeframes: NOT STATED explicitly; Renko charts are time-independent [00:30-01:00]
- sessions/hours: NOT STATED

## Strategy 1: Long Entry (Green Renko Brick)

### Indicators and settings
- Renko chart: brick size: 100 points [03:30-04:00]; "brick is formed in the next column once the price exceeds the top or bottom of the previous brick by a predefined amount" [00:30-01:00]
- SMA: period: 10 [04:30]
- OBV: On-Balance Volume; period: NOT STATED (default assumed)

### Context / bias filter
[06:00-06:30] Trend must favor longs: "We only take trades in the direction of the SMA. When the Renko bars are traded above SMA10, we look for long entries"

[07:30-08:00] SMA slope quality: "For better quality signals, try to enter the market when the ma is pointing upward."

### Entry trigger
Three conditions must be met [06:00-06:30]:

1. "A new green Renko bar forms above the SMA10" [06:00-06:30]
2. "We filter the signal with the on balance volume. We look for a new high in the OBV, which indicates that buyers are stronger than sellers, and the price is likely to increase. When OBV increases in correlation with the price, the upward trend is confirmed." [06:00-06:30]
3. (Recommended) SMA slope is upward: "For better quality signals, try to enter the market when the ma is pointing upward" [07:30-08:00]

Entry occurs when green Renko bar closes above SMA10 with OBV confirmation.

### Stop loss
[06:30] "Stop loss will be placed 2 Renko bars below the entry point."

Stop placed 2 × 100 = 200 points below entry (for 100-point bricks).

### Take profit / exit
[06:30-07:00] Primary take profit: "Minimum take profit should be 3 Renko bars into the future, to cover the spread and commissions."

Target = 3 × 100 = 300 points above entry (for 100-point bricks).

[07:00] After reaching minimum TP: "When the price reach this target, we can move our stop loss to break even and let the trade ride, or we can use a trailing stop to capture a larger part of the move."

[06:30] Manual exit: "We can exit the position manually if the price falls below the simple moving average."

### Invalidation / skip conditions
[07:30-08:00] Skip when SMA slope is flat: "For better quality signals, try to enter the market when the ma is pointing upward. In our case, the first 2 signals appeared when the 10 SMA was flat, so a conservative trader would have ignored these entries and focused on the last ones, when the slope was clearly pointing upward."

Only enter when SMA slope is upward-pointing.

## Strategy 2: Short Entry (Red Renko Brick)

### Indicators and settings
- Renko chart: brick size: 100 points [03:30-04:00]
- SMA: period: 10 [04:30]
- OBV: On-Balance Volume; period: NOT STATED (default assumed)

### Context / bias filter
[08:00-08:30] Trend must favor shorts: "We only take trades in the direction of the SMA. When the Renko bars are traded below SMA10, we look for short entries only"

SMA slope quality: Similar to longs, downward slope is preferred [10:00-10:30]: "try to enter long during long term upward trends and go short during long-term downtrends."

### Entry trigger
Three conditions must be met [08:00-08:30]:

1. "A new red Renko bar forms below the SMA10" [08:00-08:30]
2. "We filter the signal with the on balance volume. We look for a new low in the OBV, which indicates that sellers are stronger than buyers, and the price is likely to decrease. When OBV decreases in correlation with the price, the downward trend is confirmed." [08:30]
3. (Recommended) SMA slope is downward: "For better quality signals, try to enter the market when the ma is pointing upward" [applied inversely for shorts]

Entry occurs when red Renko bar closes below SMA10 with OBV confirmation.

### Stop loss
[08:30] "Stop loss will be placed 2 Renko bars above the entry point."

Stop placed 2 × 100 = 200 points above entry (for 100-point bricks).

### Take profit / exit
[08:30-09:00] Primary take profit: "Minimum take profit should be 3 Renko bars into the future."

Target = 3 × 100 = 300 points below entry (for 100-point bricks).

[09:00] After reaching minimum TP: "When the price reaches this target, we can move our stop loss to break even and let the trade ride, or we can use a trailing stop to capture a larger part of the move."

[08:30] Manual exit: "We can exit the position manually if the price increases above the simple moving average."

### Invalidation / skip conditions
[09:00-10:00] Skip when SMA slope is flat or pointing upward: First short entry in example had "some risk because the SMA slope was pointing upward"; third entry "riskier because the SMA was flat."

Only enter when SMA slope is downward-pointing.

### Claimed performance
NONE EXPLICITLY STATED. Implied positive via examples [07:00]: "In this example, we have 4 valid buy entries, all of them bringing decent returns."

### Vagueness log
1. UNDEFINED-RULE: "New green Renko bar forms above SMA10" — "forms above" unclear; does bar need to close above or merely open above? [06:00-06:30]
2. UNDEFINED-RULE: "OBV shows new high" [06:00-06:30] — no specific definition of what constitutes a "new high" (higher than previous bar? Previous 5 bars?)
3. UNDEFINED-RULE: "OBV increases in correlation with the price" [06:00-06:30] — "in correlation" is vague; no quantified divergence threshold
4. UNDEFINED-RULE: "SMA slope pointing upward" [07:30-08:00] — no angle threshold; visual assessment
5. UNDEFINED-RULE: "Buyers are stronger than sellers" [06:00-06:30] — quantified by OBV but threshold NOT STATED
6. UNDEFINED-RULE: Manual exit "if the price falls below the simple moving average" [06:30] — on close or just touch?
7. UNDEFINED-PARAM: "Trailing stop" parameters NOT SPECIFIED [07:00]
8. SUBJECTIVE: SMA slope determination is visual; no quantified slope angle or gradient

### Mechanizability
FULL (with stated parameters). The strategy is mechanizable:
- Renko brick formation: Requires price > previous high + 100 points (mechanizable)
- SMA 10 calculation: Mechanizable
- OBV calculation: Mechanizable
- Entry conditions: Renko bar closes above/below SMA + OBV new high/low (mechanizable with "new high" defined as higher than prior bar or N-period high)
- Stop loss: Fixed at 2 bricks = 200 points (mechanizable)
- Take profit: Fixed at 3 bricks = 300 points (mechanizable)
- SMA slope direction: Can be calculated (positive/negative gradient)
- Manual exit at SMA crossover: Mechanizable

The main assumption is that "OBV new high/low" means highest/lowest of the current candle vs previous (or prior N candles). With this clarification, the strategy is fully codable.

## Notable claims and caveats

- [00:00-00:30] "Renko charts are one of the most valuable and underrated instruments, which offer a great value to patient traders."
- [00:30-01:00] "The uniqueness of Renko charts is that this technique plots a brick only when the price moves a certain amount of pips /ticks in one direction or the other."
- [01:30-02:00] "Renko charts are very effective for traders to identify key support/resistance levels"
- [02:00-02:30] "Renko charts offer a simpler look of the market and indicate trends in a more clean way"
- [02:30-03:00] "it removes the 'market noise' seen on typical candlestick charts or bar charts, including wicks, false breakouts and price volatility."
- [03:00-03:30] "Renko charts are suitable for scalping and short-term trading. So, if you want to scalp the market, I would say it's better to use a Renko chart than trading on the 1-min timeframe."
- [03:00-03:30] "One of the most important advantages of Renko charts is a better determination of stop losses and take profit targets."
- [03:30] "Renko trading minimize overtrading and increase patience, which will make a better trader overall"
- [07:30-08:00] "For better quality signals, try to enter the market when the ma is pointing upward."
- [09:00-10:00] "First one was a losing trade, but we could easily avoided if we looked at the slope of the SMA, which was flat."

No mention of transaction costs, spread (though spread is mentioned as covered by 3-brick TP), or slippage. No drawdown or losing streak analysis. The strategy acknowledges losses and recommends filtering via SMA slope to improve quality. Examples show 4 buy entries with "decent returns" and 4 short entries with mixed results (1 loss, 3 gains).
