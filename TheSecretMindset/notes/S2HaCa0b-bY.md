# My Boring MACD Trading Strategy Just Hit 71% Win Rate This Month

- video_id: S2HaCa0b-bY
- url: https://www.youtube.com/watch?v=S2HaCa0b-bY
- duration: 15:20
- classification: MULTI-STRATEGY

## Summary
This video presents three separate MACD trading systems: System 1 for catching trends via zero-line and distance-filtered crossovers, System 2 for catching reversals via divergence and histogram patterns, and System 3 for filtering false signals via triple-timeframe alignment and price action confirmation. These three systems can be used independently or combined with multi-timeframe filtering.

## Instruments and timeframes stated
- markets: NOT STATED
- timeframes: Multiple timeframe analysis; examples use daily, 4-hour, 1-hour, 15-minute timeframes [09:30-10:00]
- sessions/hours: NOT STATED

## Strategy 1: MACD Trend System

### Indicators and settings
- MACD (fast line, slow line, histogram); default settings NOT STATED but standard MACD assumed
- Zero line is critical reference

### Context / bias filter
**Zero Line Foundation** [01:30-03:00]:
- MACD above zero = bullish bias; ONLY look for buy signals [02:00]
- MACD below zero = bearish bias; ONLY look for sell signals [02:00]
- No exceptions; "The Zero Line is absolute law" [02:00]

### Entry trigger
**Crossover Entry** [03:00-05:00]:
When MACD is above zero, take BULLISH CROSSOVER (fast line crosses above slow line) ONLY when MACD is above 0.5 on the chart [04:00] (or below -0.5 for shorts) [04:00-04:30]
- Crossovers near zero are false signals in "chop zone" [03:30]
- Only take crossovers far from zero (Distance Rule): above 0.5 or below -0.5 [04:00]
- Wait 2-3 candles after crossover before entering to allow price to confirm the move is real [05:00]

### Stop loss
Place stop at recent swing high (for longs) or swing low (for shorts) [13:00]

### Take profit / exit
Target is 2× risk [13:00]. Close 50% at target, move stop to breakeven, trail remainder with opposite MACD cross [13:30]

### Invalidation / skip conditions
If crossover is near zero (within ±0.5), skip it as false signal. If MACD crosses back across zero, trend is invalid.

### Claimed performance
"My win rate jumped to 60% just by following this one rule" (Zero Line rule alone) [02:30]

### Vagueness log
1. "Recent swing high/low" is VISUAL-ONLY; no definition of "recent" (last 5 bars? 10 bars? how many?)
2. "Wait 2-3 candles" is imprecise - does this mean exactly 2-3 or approximately?

### Mechanizability
FULL - MACD crossover and distance from zero line are computable from OHLCV. Zero line is fixed at 0. Swing high/low can be identified mechanically though "recent" requires parameter.

---

## Strategy 2: MACD Reversal System

### Indicators and settings
- MACD (fast line, slow line, histogram)

### Context / bias filter
Look for divergence between price and MACD:
- **Bearish divergence** [06:00]: Price makes higher high, but MACD makes lower high = reversal coming [06:30]
- **Bullish divergence** [07:00]: Price makes lower low, but MACD makes higher low = reversal forming [07:00]

### Entry trigger
**Divergence Detection + Histogram Confirmation** [06:00-08:30]:

1. Spot divergence (price vs MACD disagreement) [06:00-06:30]
2. Wait for histogram confirmation pattern [07:30-08:00]:
   - **The Flip**: Red bars turn green (or vice versa) after 5+ bars of opposite color [07:30]
   - **The Shrinking Tower**: Bars getting progressively smaller = momentum dying [08:00]
   - **The Zero Bounce**: Histogram bounces away from zero line = trend continues [08:30]

3. Entry trigger is the histogram pattern confirmation, NOT divergence alone [07:30]

Example: Bearish divergence on 4H, shrinking green bars on histogram, then first red bar = entry [08:30]

### Stop loss
NOT STATED

### Take profit / exit
NOT STATED

### Invalidation / skip conditions
Divergence alone is not sufficient; divergence without histogram confirmation should not be traded [07:00]

### Claimed performance
"Caught a 100 pip reversal" on one example trade [08:30]

### Vagueness log
1. Stop loss completely unspecified
2. Take profit target NOT STATED
3. "5+ red bars" before flip is mentioned for one example but not as a rule
4. What constitutes "shrinking" towers is SUBJECTIVE - how much smaller?
5. Divergence drawing (connecting tops) is VISUAL-ONLY and subjective

### Mechanizability
PARTIAL - Histogram patterns can be mechanized (bar height comparison), but divergence identification is VISUAL-ONLY and subjective. Stop and target are missing.

---

## Strategy 3: MACD Confirmation System (Multi-Timeframe Filter)

### Indicators and settings
- MACD on three different timeframes
- No other indicators required

### Context / bias filter
**Triple Timeframe Stack** [09:30-10:30]:

Stack three timeframes using 4× multiplier rule [10:30]:
- If entering on 15-minute: check 1-hour and 4-hour
- If entering on 1-hour: check 4-hour and daily
- If entering on 4-hour: check daily and weekly

For each timeframe:
- **Highest timeframe (e.g., daily)**: MACD position vs zero line = your bias [09:30]
- **Middle timeframe (e.g., 4-hour)**: Crossover or divergence forming = your signal [09:30]
- **Entry timeframe (e.g., 1-hour)**: Histogram flip = your trigger [09:30]

All three must be aligned. If daily is bullish but 4-hour is bearish, skip [10:30]

### Entry trigger
Example (bullish) [09:30-10:00]:
1. Daily MACD above zero (bullish bias) ✓
2. 4-hour showing bullish crossover above [10:00] ✓
3. 1-hour histogram just flipped from red to green (entry trigger) ✓
= High probability trade, entry here = 200 pip winner [10:00]

### Stop loss
At recent swing high/low, NOT STATED precisely [13:00]

### Take profit / exit
2× risk target [13:00]

### Invalidation / skip conditions
If any timeframe disagrees (e.g., 4-hour has no signal while 1-hour does), wait [10:30]

### Claimed performance
"200 point winner" on the example provided [10:00]

### Vagueness log
1. "Recent swing" high/low is VISUAL-ONLY
2. Price action confirmation required [11:00-11:30] but not quantified - "key levels matter more than signal itself" is vague
3. Hammer candles and trendline breaks are VISUAL-ONLY confirmations

### Mechanizability
FULL for the core timeframe filtering and histogram pattern detection, but PARTIAL once price action confirmation is introduced (hammer candles, trendline breaks).

---

## Morning Routine Example [12:00-14:00]

Workflow:
1. Check daily MACD vs zero (5 seconds, determines bias for entire day)
2. Scan for System 1 or System 2 signals on charts
3. Mark 3 best setups
4. Confirm System 3 (three timeframes aligned, price at key level, histogram confirming)
5. If everything aligned, enter at candle close
6. Stop at recent swing high/low
7. Target 2× risk
8. Take half profit at target, move stop to breakeven, trail remainder

---

## Notable claims and caveats
- **Performance claim**: "71% win rate this month" [title]
- **Performance claim**: "60% win rate just by following Zero Line rule" [02:30]
- **Performance claim**: "200 point winner," "100 pip reversal" on example trades [08:30, 10:00]
- No sample size given for "71% win rate" - could be 7 trades or 70 trades
- "This month" suggests not a long-term backtest result
- No discussion of costs, spread, slippage, commission
- No mention of drawdown, consecutive losses, or market conditions where strategy fails
- Speaker claims "these three systems working together" are "absolutely unstoppable" [01:00] but provides limited evidence
