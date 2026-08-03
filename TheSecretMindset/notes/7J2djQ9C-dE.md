# This Heiken Ashi & 50-EMA Strategy Is The Best Kept Secret In Day Trading

- video_id: 7J2djQ9C-dE
- url: https://www.youtube.com/watch?v=7J2djQ9C-dE
- duration: 13:29
- classification: STRATEGY

## Summary

The video teaches a bearish reversal/continuation strategy using Heiken Ashi candles combined with rising wedge pattern recognition and an exponential moving average for confirmation. The strategy enters short when price breaks below the support line of a rising wedge and closes below the EMA, with profit targets equal to the widest distance of the wedge and a minimum 2:1 risk-reward ratio.

## Instruments and timeframes stated

- markets: NOT STATED
- timeframes: NOT STATED (mentions "depending on the time frame you're analyzing") [03:30]
- sessions/hours: NOT STATED

## Strategy 1: Rising Wedge Breakdown with Heiken Ashi and EMA Confirmation

### Indicators and settings

- Heiken Ashi: standard chart type (no parameters); "filters out market noise and reduces small corrections making the signals more transparent" [04:00]
- EMA: 50 or 100 period; "A 50 EMA or 100 EMA are good potential averages you could use" [03:30]; choice "is largely dependent on the time frame you're analyzing and your trading style" [03:30]

### Context / bias filter

- A prior trend must exist to qualify as a reversal pattern [04:00-04:30]
- Rising wedge pattern must form with two converging trendlines, both pointing upwards [03:00]
- Upper resistance line: at least 2 reaction highs required, ideally 3; "Each reaction high should be higher than the previous high" [04:30]
- Lower support line: at least 2 reaction lows required; "Each reaction low should be higher than the previous low" [04:30]
- Lower support line slope must be steeper than upper resistance line slope [02:30]
- Volume should decline as prices rise and the wedge evolves [05:30]

### Entry trigger

"Once support is broken" [05:30], "entry below the breakout point" [07:30]

"When you identify a wedge breakout, you want to see price moving below the EMA, to confirm the momentum shift to the downside" [03:30]

"After the market breaks down through the lower support line, it should also break below the EMA, and ideally should remain below it" [06:00]

### Stop loss

"The high of the wedge is a good start for an initial stop loss, which could be moved as the market makes lower lows" [06:30]

Placed "above the high of the wedge" [07:30]

### Take profit / exit

Profit target: "Rising wedges are said to have a price target that's equal to the widest distance of the wedge. You measure the distance of the wedge and you project the distance on the breakout point" [06:00]

Risk-reward ratio: "Usually, you should aim to have a risk-reward ratio of 2 or more" [06:00]

### Invalidation / skip conditions

- "False breakouts are quite common" [06:30]
- "There are many false patterns or patterns in disguise that may come off as a rising wedge" [11:00]
- Use Heiken Ashi instead of traditional candlesticks "to eliminate noise on the chart and keep the dominant trend in display" [11:00]

### Optional confirmation signals

"Another effective confirmation is a bearish divergence on a momentum indicator" [08:30]. Can use RSI, MACD, or Stochastic [09:00] where "a technical indicator begins to establish a trend that disagrees with the actual price movement. The disagreement or divergence between bullish price action (higher highs) and the trend of the oscillator (lower highs) is another clue that the market could go down" [09:00]

"Another way to differentiate a true rising wedge from a false one is by finding price/volume divergences" [11:30]

### Claimed performance

NONE CLAIMED. The speaker mentions "back testing lately with promising results" [00:00] but provides no specific win rate, profit metrics, or Sharpe ratio.

### Vagueness log

1. UNDEFINED-PARAM: EMA period choice is left to the trader based on timeframe and style, with 50 or 100 as "good potential" but no decision criteria given [03:30]
2. SUBJECTIVE: "reaction high" and "reaction low" are not formally defined; unclear what distinguishes a reaction point from noise or smaller oscillations [04:30]
3. UNDEFINED-PARAM: How much higher must each reaction high be than the previous? "Higher" is stated without a percentage or absolute threshold [04:30]
4. UNDEFINED-RULE: What constitutes "convincing fashion" for the support line breakout? No candle structure, volume, or magnitude criteria given [05:30]
5. UNDEFINED-RULE: "Volume will decline as prices rise" — by how much? No percentage or threshold specified [05:30]
6. UNDEFINED-RULE: "Expansion of volume on the support line breakout" — how much expansion qualifies as confirmation? [05:30]
7. VISUAL-ONLY: The comparison of slope angles (lower support steeper than upper resistance) requires visual judgment [05:00]
8. UNDEFINED-PARAM: "Give the market some room to play with" for the stop loss — the buffer distance is not quantified [06:30]
9. SUBJECTIVE: Divergence confirmation using momentum indicators is optional and subjective in interpretation [08:30-09:00]

### Mechanizability

PARTIAL

Wedge formation detection (converging trendlines, higher highs, higher lows) can be automated computationally, and EMA breakout is mechanically straightforward. However, critical gaps prevent full automation: (1) what counts as a "reaction" point has no objective definition; (2) "convincing fashion" breakout lacks a numerical threshold (e.g., % beyond support); (3) volume expansion is not quantified; (4) the stop buffer is left to discretion; (5) divergence signals are optional and require subjective interpretation. The skeleton is computable, but entry confirmation and false-breakout filtering require manual judgment.

## Notable claims and caveats

- "Back testing lately with promising results" but no specific performance metrics [00:00]
- "False breakouts are quite common" [06:30]
- "There are many false patterns or patterns in disguise" [11:00]
- The pattern can also function as a bearish continuation pattern (not just reversal) in downtrends [10:00+]
- No discussion of commissions, spreads, slippage, or transaction costs
- Optional use of momentum divergence (RSI, MACD, Stochastic) for additional confirmation [08:30-09:00]
