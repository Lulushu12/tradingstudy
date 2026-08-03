# My Swing Trading System Is Lazy, But It Beats 95% of Day Traders

- video_id: _8q3ZJ5afFA
- url: https://www.youtube.com/watch?v=_8q3ZJ5afFA
- duration: 25:12
- classification: MULTI-STRATEGY

## Summary

This video presents a swing trading system built on confluence of three technical tools: monthly pivot levels, three-layer Bollinger Bands, and a 21-period EMA channel, all combined with round-number support/resistance. The trader teaches bounce trades off pivots, fade trades at Bollinger Band extremes, channel-based trend confirmation, and how to combine multiple confluent signals. The approach is designed for swing trading on daily and 4-hour charts with minimal time commitment (10-minute daily routine), avoiding institutional manipulation on low timeframes by trading higher time structures instead.

## Instruments and timeframes stated

- markets: NOT STATED (examples imply multi-asset: stocks, forex indices, futures)
- timeframes: daily and 4-hour charts explicitly mentioned [04:30, 17:30]; swing trading focus implies multi-day holds
- sessions/hours: NOT STATED

## Strategy 1: Monthly Pivot Confluence Trading

### Indicators and settings

- Monthly Pivot Points: "lines are more influential than daily pivot lines for bigger moves" [00:30-01:00]; calculated as "average of prices from performance of market in prior trading period" [00:30] but exact calculation formula NOT STATED
- Pivot levels used: main pivot, R1 (resistance 1), R2, S1 (support 1), S2 [01:00-01:30]
- Demand/Supply zones: zones where "buyers showed interest before" (demand) or "sellers dominated" (supply) [02:00-02:30]; identification method NOT STATED
- Candlestick patterns: pin bar, engulfing bar [03:30-04:00], [04:00]

### Context / bias filter

Price must be approaching a monthly pivot level [01:00-01:30]. Strong signal when pivot aligns with "known support area" (demand zone) for bullish trades [02:30-03:00] or pivot aligns with "supply zone" for bearish trades [03:00-03:30]. Confluence increases reliability: "A monthly pivot by itself might be good, but if you also see that pivot align with a demand zone or a supply zone, you have a stronger reason for a trade" [02:00-02:30].

If "price has acted as support for some time but you see a daily close below it, that pivot may now turn into resistance" (pivot flip) [04:30-05:00].

### Entry trigger

Bullish entry: "When price gets there, a bullish pin bar forms. That can be your buy signal" at a monthly pivot aligned with demand zone [03:00-03:30]. Price must form a reversal pattern: "pin bar with a long wick rejecting the pivot" [04:00-04:30].

Bearish entry: "As price rallies into that zone, you watch for a reaction. Perhaps you see a bearish pin bar or a bearish engulfing bar as price touches the pivot. That can be your short trigger" [03:30-04:00].

Breakout entry: "When you see a breakout occur, you can ride the momentum in that direction" after pivot breaks [05:30-06:00].

Pattern must confirm: "Try not to jump in without a pattern. Wait for some sign that the price is responding" [04:30-05:00].

### Stop loss

- Bounce trades: "set your stop loss a bit under the pivot and demand zone" (bullish) or "stop above the pivot" (bearish) [03:00-03:30], [03:30-04:00]
- Breakout trades: "use the old pivot line as a place for a stop or a partial stop" [05:30-06:00]
- If trading on lower timeframes: stop "under the channel" for uptrends [15:00]

Exact distance from pivot NOT STATED.

### Take profit / exit

- Bounce targets: "ride the wave to the next pivot or to a prior swing high" [03:00-03:30]
- For sells: "target the next monthly pivot line or a known support" [03:30-04:00]
- Breakout targets: "next pivot might act as a magnet. That can be your target for a multi-day move" [05:30-06:00]
- Alternative: aim for "next pivot level: If you bought near the main pivot, you might target R1 or R2 if the trend cooperates. If you shorted near R1, you might target the main pivot or S1" [24:00-24:30]

### Invalidation / skip conditions

- If price closes intraday below the pivot but the daily close holds above it with a bullish candlestick, the setup remains valid [19:30-20:00]
- If "price fails to bounce and instead lingers" at the channel, the setup may be invalid [14:30-15:00]
- "If you see price striking the second or third deviation band exactly at a monthly pivot, that's a potent combination for a reversal" [08:30-09:00] but if this confluence is absent, the setup is weaker
- Do not trade if "price has wicked below the monthly pivot, but closes above it" without conviction [19:30-20:00]

### Claimed performance

"They will often see price reacting to these lines with strong wicks or consolidation" [01:30-02:00]. "Confluence is key" and "You can catch swings that last several days" [02:30-03:00]. No win rate, R multiple, or profit percentage stated.

### Vagueness log

1. Demand/supply zone identification is VISUAL-ONLY: defined as "zone where buyers showed interest before" but no specific price action pattern or volume confirmation given [02:00-02:30]
2. Monthly pivot calculation period and exact formula is UNDEFINED-PARAM: "prior trading period" could be weekly or monthly; exact mean/median calculation NOT STATED [00:30]
3. Exact distance for stop placement "a bit under the pivot" is UNDEFINED-PARAM: no number of pips/points [03:00-03:30]
4. Candlestick pattern confirmation is SUBJECTIVE: what defines a "strong" pin bar or engulfing bar? Wick length ratio? Body size? NOT STATED [04:00-04:30]
5. "Prior swing high" and "recent swing high" targets are UNDEFINED-PARAM: how recent? how many bars back? [03:00-03:30]

### Mechanizability

PARTIAL - Monthly pivot calculation is computable if the exact formula is known (standard: (H+L+C)/3), but the decision to trade depends on: (1) identifying valid demand/supply zones visually; (2) recognizing candlestick patterns (pin bar, engulfing) which requires subjective thresholds; (3) determining "trend cooperation" for targets. A coder could plot monthly pivots automatically but would struggle with pattern recognition and confluence judgment.

---

## Strategy 2: Three-Layer Bollinger Bands Trading

### Indicators and settings

- Bollinger Bands (3 layers):
  - Middle band: 50-period SMA [07:00-07:30]
  - First band: 1 standard deviation from 50 SMA [07:00-07:30]
  - Second band: 2 standard deviations from 50 SMA [07:00-07:30]
  - Third band: 3 standard deviations from 50 SMA [07:00-07:30]

### Context / bias filter

The 50 SMA "is a stable average that fits swing trading time frames" [07:00-07:30]. Price behavior relative to bands indicates regime: "Price near the middle band means a potential consolidation or transition area. Price crossing below the middle band means a shift from bullish to neutral or even bearish. Price crossing above the middle band represents a shift from bearish to neutral or bullish" [08:30-09:00].

In uptrend, "price keeps bouncing off the middle band" with "increase in bullish momentum" [11:30-12:00]. In range-bound market, "price tags the lower third deviation band" [12:00].

### Entry trigger

Trend-following entry: "If the market is going up, you watch for price to pull back to the middle band. If price prints a bullish candle there, you buy aiming for the upper bands as future target" [09:00-09:30].

Fade/reversal entry: "Suppose price slams into the third deviation upper band. Then you spot a monthly pivot or a supply zone. A bearish reversal candle forms. You have multiple factors to short expecting price to revert back to lower bands" [09:30-10:00]. "Spot a bearish engulfing bar as price touches the pivot. That can be your short trigger" [04:00].

Entry at extreme if "price closes beyond the third deviation band" and reversal pattern forms [07:30-08:00].

Can combine with pivot: "If you see price striking the second or third deviation band exactly at a monthly pivot, that's a potent combination" [08:30-09:00].

### Stop loss

- Trend-following trades: stop placement NOT STATED
- Fade trades: implied to be above/below the extreme band, but exact placement NOT STATED
- Reference: "You might aim for the upper bands as future target" suggests using band levels but stop distance NOT STATED [09:00-09:30]

### Take profit / exit

- Trend-following: "taking partial profits at the future resistance bands" [11:30-12:00] (upper bands in uptrend, lower bands in downtrend)
- Fade trades: "aim for the middle band" when shorting from third deviation band [10:00-10:30]
- Alternative: "If you fade an extreme near the third deviation band, you might aim for the middle band" [24:00-24:30]

### Invalidation / skip conditions

- "If the market experiences a major fundamental push, it can ride the outer band for days" so "don't blindly jump in just because price touches an outer band" [10:30-11:00]
- "If price keeps hugging the outer band without snapping back, that's a strong trend" (so fade reversal may not work) [08:00-08:30]
- "If you're used to day trading, is the impulse to act on every minimal movement" in swing trading you should skip most minor touches [22:30-23:00]
- Do not trade if "price meanders inside the channel for more than three candles" as this indicates indecision [15:00-15:30]

### Claimed performance

"You often see price reacting to these lines with strong wicks or consolidation" [01:30-02:00]. "Bollinger bands widen. The third deviation band is not guaranteed to cause a reversal" [10:30]. No specific win rate or profit data given.

### Vagueness log

1. "Bullish candle" at middle band confirmation is SUBJECTIVE: size, volume, wick requirements NOT STATED [09:00-09:30]
2. "Extreme move" or "overstretched" market is UNDEFINED-RULE: no specific percentage beyond third band or volume condition [07:30-08:00]
3. "Strong trend" hugging outer band is SUBJECTIVE: how many touches without snapback? [08:00-08:30]
4. Stop placement for fade trades is UNDEFINED-PARAM: "exactly where to place stop above/below outer band NOT STATED [09:30-10:00]
5. "Reversal pattern" confirmation is SUBJECTIVE: beyond "bearish reversal candle" no specifics given [09:30-10:00]

### Mechanizability

FULL - The Bollinger Bands calculation is computable with known parameters (50 SMA, 1-2-3 deviation levels, standard deviation formula). However, entry decision introduces discretion: identifying "bullish/bearish candlestick" patterns requires subjective thresholds. A coder could plot all three bands and detect price touches mechanically, but the reversal pattern recognition would need external pattern classifier or manual rules.

---

## Strategy 3: 21-Period EMA Channel Trading

### Indicators and settings

- 21-period Exponential Moving Average (EMA): "is a favorite among swing traders looking at daily charts. It reacts relatively quickly while smoothing short-term fluctuations" [12:00-12:30]
- Channel construction: "plotting an EMA of the highs and an EMA of the lows. So, you get two lines that frame price" [12:30-13:00]
- Calculation period: 21 NOT STATED if based on close, high-low, or other input

### Context / bias filter

Channel acts as "dynamic band of support and resistance" [12:30-13:00]. Combined with "static support and resistance level, like round numbers, this channel becomes very important" [12:30-13:00]. Trend identification: "If the price is above the channel, you might see a bullish environment... If price is below the channel, you likely see a bearish environment... If price is inside the channel, it might be consolidating" [13:00-13:30].

### Entry trigger

Bullish: "bull trend brings price to the top of the channel near a round number. If you see a bullish candlestick bounce off that zone, you jump in" [14:30-15:00].

Bearish: Look for "downside break of the round number" or "bounce from the channel's underside" [15:30-16:00].

Breakout: "If price breaks out of the channel with conviction before acting" then initiate breakout trade [15:00-15:30].

Channel bounce/retest: "The first bounce is important. It proves that the channel is being respected. Then you look for a round number to align with that bounce. That confluence can yield a strong trade" [14:30-15:00].

### Stop loss

- "stop under the channel" for uptrend trades [15:00]
- Exact distance from channel line NOT STATED

### Take profit / exit

- "target the next round number above" [15:00]
- If breakout occurs, use "next round number" as target [15:30-16:00]

### Invalidation / skip conditions

- "If price meanders inside the channel for more than three candles, you might skip trades. That indicates indecision" [15:00-15:30]
- "If you trade while the market is stuck, you might get whipsawed" [15:30]
- If price breaks channel, "wait for a retest from below" before shorting rather than immediately fading [23:30-24:00]

### Claimed performance

No specific win rate, R multiple, or profit percentage stated. Described as part of 10-minute daily swing trading routine [00:30].

### Vagueness log

1. "EMA of the highs and lows" calculation is UNDEFINED-PARAM: 21-period EMA applied to high-low prices, but not standard candlestick input [12:30-13:00]
2. "Bullish candlestick bounce off that zone" is SUBJECTIVE: size, volume, wick definition NOT STATED [14:30-15:00]
3. "Break out of the channel with conviction" is UNDEFINED-RULE: how far beyond channel line constitutes conviction? [15:00-15:30]
4. "Meanders inside channel for more than three candles" is UNDEFINED-RULE: exactly three or more? [15:00-15:30]
5. Stop placement "under the channel" is UNDEFINED-PARAM: distance from lower channel line NOT STATED [15:00]

### Mechanizability

FULL - 21-period EMA is fully computable (standard EMA formula on price highs/lows). Channel formation is automatic. However, entry decision relies on: (1) candlestick pattern recognition ("bullish bounce"); (2) subjective assessment of "conviction"; (3) round number alignment. The mechanical skeleton is complete; pattern recognition requires external rules or manual confirmation.

---

## Strategy 4: Round Number Support/Resistance Trading

### Indicators and settings

- Round numbers: Major psychological levels like 1.1000, 1.2000 (forex examples) [13:30-14:00, 14:00]
- Integration with channel and pivots: "Many traders fixate on these levels. They often place stops or entries around them" [13:00-13:30]

### Context / bias filter

Round numbers act as "static support and resistance level" [12:30-13:00]. Effectiveness increases with confluence: "If the market is in an uptrend, you might plan to buy a breakout above the round number. If the market is in a downtrend, you might plan to sell a breakout below a round number" [13:30-14:00]. Round numbers combined with pivot levels or Bollinger Band extremes increase probability: "Maybe price is at a monthly pivot at the third deviation Bollinger Band. Or price is in an uptrend, holds above the monthly pivot, and sits near the 21 EMA channel" [16:30-17:00].

### Entry trigger

Breakout above round number in uptrend: "If the market is in an uptrend, you might plan to buy a breakout above the round number" [13:30-14:00].

Breakdown below round number in downtrend: "If the market is in a downtrend, you might plan to sell a breakout below a round number" [13:30-14:00].

Bounce from round number within channel: "The first bounce is important. It proves that the channel is being respected. Then you look for a round number to align with that bounce. That confluence can yield a strong trade" [14:30-15:00].

### Stop loss

Placement relative to round number NOT STATED explicitly. Implied: slightly beyond the round number level.

### Take profit / exit

- "target the next round number above" (bullish) [15:00]
- "target the next round number" below (bearish) [13:30-14:00]

### Invalidation / skip conditions

- If no clear confluence with other tools (pivots, channel, bands), skip the round number level [17:00]
- Do not chase breakouts if already far beyond the level [22:00-22:30]

### Claimed performance

No specific performance metrics given. Described as part of swing trading routine that "beats 95% of day traders" [title, 00:00] but no data provided.

### Vagueness log

1. "Major round number" selection is SUBJECTIVE: which numbers count? Every 100? Every 500? [13:30-14:00]
2. Breakout "conviction" beyond round number is UNDEFINED-RULE: minimum move distance? [13:30-14:00]
3. Stop placement relative to round number is UNDEFINED-PARAM: pips/points NOT STATED [13:00-14:00]
4. Confluence requirement is SUBJECTIVE: how many confluent tools needed? [16:30-17:00]

### Mechanizability

FULL - Round numbers are definable (static price levels like X.YY00). Identifying price proximity to round numbers is fully computable. However, breakout confirmation and confluence assessment require discretion. The mechanical skeleton is complete.

---

## Notable claims and caveats

The speaker claims the system "beats 95% of day traders" [title, 00:00] by trading higher timeframes where retail institutions cannot exploit low-timeframe stop hunts [00:00-00:30]. The system requires only "10-minute daily routine" [00:30] and does not require watching every minute [18:00].

Key cautions:
- "Do not chase every minor pivot or Bollinger bands" and avoid "random trades that do not align with your strategy" [18:30-19:00]
- "Over complication" pitfall: "If you try to watch too many lines, you might get confused. So, simplify" [20:30-21:00]
- "Jumping in without seeing a candle close might lead to fake outs" [21:00-21:30]
- "Fading a strong trend without care": do not short just because price hits outer Bollinger Band; check volume and trend strength [21:30-22:00]
- "Let losers run": must "respect your stops. If price breaks the pivot you used as a support, let it go" [22:00-22:30]
- "Gap opens" after weekends or major events can invalidate setups; "do not chase" and instead "wait for a retest or a new pivot to form" [22:00-22:30]
- Psychology: swing traders often "panic" when multi-day positions retrace; must "trust your pivot or your channel" [23:00-23:30]
- "Finding the correct exit points" is a challenge; recommend "keep a record of each swing trade" to refine [24:00-24:30]

The speaker never mentions trading costs, spreads, slippage, or commissions. Risk management is mentioned only in context of respecting stops and avoiding emotional changes to the plan [23:00-23:30]. No drawdown or losing streak statistics provided.
