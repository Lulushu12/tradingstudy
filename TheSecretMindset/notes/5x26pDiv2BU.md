# The Last Order Block Strategy You'll Ever Need For SMC Trading

- video_id: 5x26pDiv2BU
- url: https://www.youtube.com/watch?v=5x26pDiv2BU
- duration: 28:26
- classification: STRATEGY

## Summary

The video presents the order block strategy, a Smart Money Concepts (SMC) approach based on identifying candles where institutional traders initiate positions after liquidity runs. Bullish order blocks form on the last red candle before an upswing; bearish order blocks form on the last green candle before a downswing. The strategy combines order block identification on higher timeframes with entry confirmation on lower timeframes, using fair value gaps and liquidity pools as confirmation. The video emphasizes that the best order blocks are preceded by liquidity runs, followed by market structure breaks, and contain fair value gaps.

## Instruments and timeframes stated

- markets: NOT STATED (examples mention "stock" and "currency" but no specific instruments)
- timeframes: "Order blocks work on all time frames, but they are most powerful on the higher ones. An hourly order block is usually more significant than a 5-minute one." [16:15-16:30]. Specific recommendation: identify on higher timeframe (example: "hourly chart" [23:00]), then zoom to lower timeframe for entry (example: "5-minute chart" [25:15]).
- sessions/hours: NOT STATED

## Strategy 1: Order Block (Bullish)

### Indicators and settings

- Order block candle type: Last red candle before the bullish reversal (last candle in down-move before price shoots up) [05:00-06:00]
- Midpoint threshold: "draw it right through the middle at the 50% level of the candle" [06:15]
- Candle body confirmation: "For a top-notch bullish order block, we don't want to see price trading below the midpoint of that candle." [06:30]
- Entry timeframe: Higher timeframe for identification [23:00]; lower timeframe for entry (e.g., 5-minute if hourly identified) [25:15]
- Fair value gap: "To spot a fair value gap, look at three candles in a row. In a bullish gap, the low of the third candle is above the high of the first." [17:15-17:30]

### Context / bias filter

"In an uptrend, focus on bullish order blocks that form within the current upswing" [22:15-22:30]. Bias must be uptrend; order block must align with prevailing trend direction [22:15].

Price must have made a liquidity run prior: "A bunch of stop losses sitting just below a low point in an uptrend. If price dips down and triggers the stops before shooting back up, that's a liquidity run." [23:30-24:00]

Market structure break must follow: order block "should trigger a break in market structure. This shows strength and commitment to the move." [24:00]

### Entry trigger

On the higher timeframe, identify the bullish order block (last red candle before upswing).

On the lower timeframe, wait for price to return to the order block zone [25:15-25:30]. Entry occurs: "The plan is to enter your trade on the breakout of the lower time frame order block." [26:30]

Additional confirmation on lower timeframe: "Look for a smaller version of the order block you found earlier" [25:45-26:00], or "Look for a small liquidity grab just before your entry" [26:00-26:15], or "look for any patterns forming on your lower time frame chart. If you see small double bottoms, that's a decent setup. Or maybe there are small change of character. Price is breaking previous swing highs." [26:15-26:30]

### Stop loss

"Place your stop loss just below a recent swing low. And please give it enough room to breathe. Don't try to be too precise with your stop." [27:00]

Exact stop price: NOT STATED (definition of "recent swing low" is not quantified; "enough room to breathe" is subjective).

### Take profit / exit

"Your take profit should be ideally at least three times higher than your risk." [27:15]

"Look at the chart and find the next logical high point within the higher time frame trend." [27:15-27:30]

"Consider using multiple take profit levels. You could close half your position at your first target, then let the rest run to a higher target." [27:30]

Additional rule: "Order blocks must have a liquidity pool to target. Identify clear liquidity pools above your chosen order block. These pools act as magnets for price." [27:45]

### Invalidation / skip conditions

"Not every order block will lead to a good trade." [23:00]

"A successful order block strategy combines trend analysis, order block identification, and precise entry timing." [23:00]

If the midpoint of the order block is breached: "For a top-notch bullish order block, we don't want to see price trading below the midpoint of that candle. If it does, it might be telling us our block isn't as solid as we thought." [06:30-07:00]

If order block fails to be re-tested: "How do you know which ones to trust? It all comes down to liquidity." [09:30]. Order blocks without nearby liquidity zones may not be re-tested.

### Claimed performance

NONE CLAIMED. The video provides no win rate, R-multiple, or historical backtest results for the strategy.

### Vagueness log

1. UNDEFINED-PARAM: "Recent swing low" for stop placement — lookback period not specified (5 candles, 10, 20?).
2. SUBJECTIVE: "Give it enough room to breathe" — no quantified buffer distance (e.g., 10 pips, 2 ATR, 0.5%).
3. UNDEFINED-PARAM: "Logical high point within the higher time frame trend" — no rule for identifying major resistance levels or swing highs.
4. UNDEFINED-RULE: "Next major level" — no method to distinguish between minor and major liquidity pools.
5. SUBJECTIVE: "Most powerful on the higher ones" (timeframes) — no quantification of relative power by timeframe.
6. UNDEFINED-RULE: Confirmation on lower timeframe uses subjective patterns: "look for small double bottoms" or "change of character" — no precise entry candle defined.
7. UNDEFINED-PARAM: "Liquidity run" magnitude — how many stops must be triggered? What percentage of volume must participate?
8. UNDEFINED-PARAM: "Fair value gap" size — any gap qualifies or must it be of minimum size?
9. SUBJECTIVE: "Recently" and "current" — temporal references are not quantified.

### Mechanizability

PARTIAL. The skeleton is mechanically computable: identifying the last red candle before an upswing, detecting the midpoint level, waiting for price to return to the zone, and measuring 3R risk/reward are all OHLCV-based and codable. However, several key decision points require assumption:
- Definition of "recent swing low" for stop placement
- Entry confirmation on lower timeframe relies on visual pattern recognition ("double bottoms," "change of character") without precise trigger candles
- Identification of "next logical high point" for TP requires subjective selection of support/resistance levels
- Liquidity pool identification is visual and not quantified

A backtest would require filling in: stop ATR distance, specific lookback for swing lows, candle-based entry trigger on lower timeframe, and TP level selection rules. These are not trivial assumptions.

## Strategy 2: Order Block (Bearish)

### Indicators and settings

- Order block candle type: Last green candle before the bearish reversal (last candle in up-move before price drops) [05:00-06:00]
- Midpoint threshold: "50% level of the candle" [06:15]; for bearish blocks, price should not rise above this midpoint [06:30]
- Candle body confirmation: "For a bearish block, we need a candle to trade through the low of our highest green candle. And for a bearish block, we don't want price popping above the midpoint of the green candle." [06:45-07:00]

### Context / bias filter

"In a downtrend... focus on ... bearish order blocks from ... downswings" [22:15-22:30]. Bias must be downtrend; order block must align with prevailing trend direction [22:15].

Price must have made a liquidity run: price moves to hit stop losses above the market (in a downtrend) [20:00-20:15].

Market structure break must follow: "The downtrend is now in doubt" after the order block forms [21:45-22:00], suggesting a break in downtrend structure confirms the block.

### Entry trigger

On the higher timeframe, identify the bearish order block (last green candle before downswing).

On the lower timeframe, wait for price to return to the order block zone [25:15-25:30]. Entry occurs on breakout of the lower timeframe order block [26:30].

Confirmation on lower timeframe: Look for mini versions of the bearish order block or liquidity grabs [25:45-26:15].

### Stop loss

"Place your stop loss just [above a recent swing high]" — NOT EXPLICITLY STATED for bearish setup, but implied by mirror of bullish rule. "Give it enough room to breathe." [27:00]

### Take profit / exit

"Your take profit should be ideally at least three times higher than your risk." [27:15]

"Look at the chart and find the next logical low point within the higher time frame trend." [27:15-27:30] — implied parallel to bullish TP rule.

Liquidity pools below the bearish order block act as targets [21:00-21:30].

### Invalidation / skip conditions

"Not every order block will lead to a good trade." [23:00]

If the midpoint of the order block is breached (price rises above 50% of the green candle), the block integrity is questioned.

### Claimed performance

NONE CLAIMED.

### Vagueness log

1. UNDEFINED-PARAM: "Recent swing high" for stop placement — lookback period not specified.
2. SUBJECTIVE: "Give it enough room to breathe" — no quantified buffer distance.
3. UNDEFINED-PARAM: "Logical low point within the higher time frame trend" — no rule for identifying major support levels.
4. UNDEFINED-RULE: Confirmation on lower timeframe relies on subjective patterns without precise candle-based triggers.
5. VISUAL-ONLY: The strategy relies on chart visual inspection for pattern recognition that cannot be fully reconstructed from transcript alone.

### Mechanizability

PARTIAL. Same justification as Bullish Order Block: the skeleton (identify last green candle, midpoint rule, wait for return, 3R TP) is mechanically detectable, but entry confirmation and stop/TP level selection require undefined parameters or assumptions.

## Strategy 3: Failed Order Block

### Entry trigger

"Failed order blocks often lead to strong moves." [16:00]. When price returns to an order block but "pushes right through" instead of bouncing [15:45-16:00], this breakout is a tradeable signal.

The failed order block breakout creates strong moves because "a lot of traders are caught on the wrong side. They were expecting the block to hold and now they're scrambling to get out." [16:00]

### Context / bias filter

The order block must first exist as a valid identified block. A failed breakout of that block signals the opportunity.

### Stop loss

NOT STATED

### Take profit / exit

NOT STATED

### Invalidation / skip conditions

NOT STATED

### Claimed performance

NONE CLAIMED

### Vagueness log

1. UNDEFINED-PARAM: No definition of what constitutes a "breakout" through an order block (close below candle low, close below midpoint, minimum move distance).
2. UNDEFINED-RULE: How to distinguish a failed order block from normal retesting behavior.
3. UNDEFINED-PARAM: Entry price for the failed block breakout not specified (at the breakout, after confirmation).

### Mechanizability

PARTIAL. Identifying a price breakout through a prior order block level is mechanically detectable, but the exact trigger price (the level definition itself can vary: candle low vs. midpoint vs. other) and the confirmation candle are not precisely defined.

## Notable claims and caveats

- "Order blocks aren't magic bullets." [02:45]. The speaker acknowledges that not all order blocks are tradeable.
- "In fact, most of them break as soon as the price comes back to them." [02:45-03:00]. Majority of order blocks fail, yet the strategy is still promoted.
- "Not every order block will lead to a good trade." [23:00]. Reiterated caveat about selectivity required.
- "A successful order block strategy combines trend analysis, order block identification, and precise entry timing." [23:00] — success requires additional factors beyond order block identification alone.
- No discussion of transaction costs, spread, slippage, or commission.
- No win rate, drawdown, losing streaks, or historical performance data provided.
- The video does not address what happens during consolidations or choppy markets where order blocks may form frequently without reliable direction.
- "You won't see them every day." [21:15] — the high-quality setups (with all three elements: liquidity run, structure break, fair value gap) are rare.
- The speaker promotes additional educational content ("watch one of these videos next" [28:00]) suggesting this is part of a larger course ecosystem.
