# How To Combine LEADING & LAGGING Indicators (Best Trading Indicators for Beginners)

- video_id: PJwrmBlAULA
- url: https://www.youtube.com/watch?v=PJwrmBlAULA
- duration: 10:41
- classification: CONCEPT

## Summary

This video is an educational framework on how to combine leading indicators (which anticipate future price moves) with lagging indicators (which confirm trends already underway). The speaker argues that almost all common indicators are lagging (moving averages, MACD, RSI, Stochastics) and that true leading indicators are price-based levels like pivot points, Fibonacci retracements, and support/resistance. The video presents the principle of mixing leading and lagging indicators across timeframes to reduce false signals while avoiding late entries.

## Instruments and timeframes stated

- markets: NOT STATED (generic education)
- timeframes: Multiple timeframes for mixing indicators [08:30-09:00]
- sessions/hours: NOT STATED

## Definitions

### Leading Indicators [00:00, 05:30-07:00]

"A leading indicator is a tool designed to anticipate the future direction of a market, in order to enable traders to predict market movements ahead of time" [00:00]. "Leading indicators are able to anticipate when major moves in the markets would occur" [06:00].

**Characteristics [06:00-06:30]:**
- Allow traders to enter at or before the start of a move
- Can generate false breakouts and minor retracements look like reversals

**Examples of leading indicators [06:30-08:00]:**
- Pivot points [06:30-07:00]
- Fibonacci retracements and extensions [07:30]
- Volume (in conjunction with price) [07:30]
- Trend lines, support and resistance levels [08:00]

### Lagging Indicators [00:30, 02:00-05:30]

"A lagging indicator is a tool that provides delayed feedback, which means it gives a signal once the price movement has already passed or is in progress" [00:30]. "These indicators lag the market. This means that traders can witness a move before the indicator confirms it" [02:00-02:30].

**Characteristics [01:30, 04:30-05:30]:**
- React slowly, providing more accuracy but late entry
- Only provide "today's value based on historical data" [04:30]
- "First there's a move in price, then sometime later in the game, the indicator signals buy or sell signal" [05:00-05:30]
- "Price moves indicators – not the other way around" [05:30]

**Examples of lagging indicators [04:00, 05:00]:**
- Moving averages [03:00, 05:00]
- MACD [05:00]
- RSI [04:00, 05:00]
- Stochastics [04:00, 05:00]

**Important Clarification [04:00-04:30]:**
RSI, Stochastic, and other momentum oscillators are NOT leading indicators, despite being called so by some traders. They are lagging indicators; "just because they tell you how overbought or oversold a market is, this doesn't mean that they are leading the price" [04:00-04:30].

---

## Example 1: 50 EMA / 200 EMA Golden Cross / Death Cross (Lagging Indicator Problem)

### Indicators and settings
- 50-period Simple Moving Average [03:00]
- 200-period Simple Moving Average [03:00]

### Context / bias filter

Entry signal: "Generally, the asset is said to be bearish when the 50 SMA crosses below the 200 SMA and bullish when the 50 SMA crosses above the 200 SMA" [03:30].

### Entry trigger

50 SMA crosses above 200 SMA (bullish) or crosses below 200 SMA (bearish) [03:00-03:30].

### Stop loss

NOT STATED

### Take profit / exit

NOT STATED

### Invalidation / skip conditions

NOT STATED

### Claimed performance

"If you went short after the bearish signal, it would have been a losing trade. This is because by the time price moved lower and the moving average reacted to this, price already fell significantly and started to pull back higher" [03:30-04:00]. This demonstrates the lagging indicator problem.

### Vagueness log

1. Stop loss: NOT STATED
2. Take profit: NOT STATED
3. Position sizing: NOT STATED
4. Entry candle/price: NOT STATED

### Mechanizability

FULL for the entry signal (SMA crossover is mechanically computable), but stop and target are not defined, making the strategy incomplete.

---

## Example 2: 200 EMA (Lagging) + Pivot Points (Leading) Combined Strategy

### Indicators and settings

- 200 EMA: period stated as 200 [09:00]
- Pivot Points: daily pivot point, S1 level [09:30]

### Context / bias filter

"First, determine the context for the trade using the lagging indicators. So if the price is below the 200 EMA, we have a downtrend, and above 200 EMA, an uptrend" [09:00-09:30].

### Entry trigger

"You can buy a pullback for example, at the central pivot point, when the market is above 200 EMA, in the direction of the trend" [09:30].

Entry levels specified:
- Uptrend (price above 200 EMA): Enter at central pivot point on pullback
- Downtrend (price below 200 EMA): Implied inverse (enter at pivot point resistance in shorts)

### Stop loss

"You can continue to use the leading indicator to find a stop placement point...In the case of this uptrend, this would be below a substantial support level, maybe below S1 level" [09:30-10:00].

### Take profit / exit

NOT STATED

### Invalidation / skip conditions

NOT STATED

### Claimed performance

NONE CLAIMED

### Vagueness log

1. "Pullback": UNDEFINED-RULE (how far? how many candles?)
2. "Central pivot point": UNDEFINED-RULE (entry at exact level? close? open of what candle?)
3. "Below a substantial support level": VISUAL-ONLY (what makes a level "substantial"?)
4. S1 level calculation: NOT STATED (pivot point formula is standard, but context of use here is vague)
5. Take profit: NOT STATED
6. Position sizing: NOT STATED

### Mechanizability

PARTIAL. Pivot point calculation is mechanically standard; 200 EMA is standard. However, entry mechanics ("pullback at central pivot") and what constitutes a "pullback" are not defined. Stop placement ("below S1 level") is vague regarding exact stop price.

---

## Example 3: Fibonacci Retracement (Leading) + Stochastic (Lagging) Combined Strategy

### Indicators and settings

- Fibonacci retracements: NOT STATED which levels
- Stochastic oscillator: period NOT STATED, overbought/oversold levels NOT STATED

### Context / bias filter

"You can enter after a Stochastic divergence, or an oversold Stochastic, when the price rejected an important FIB level" [10:00].

### Entry trigger

Two conditions:
1. Stochastic divergence occurs, OR
2. Stochastic is oversold

AND price rejects an important Fib level [10:00].

### Stop loss

NOT STATED

### Take profit / exit

NOT STATED

### Invalidation / skip conditions

NOT STATED

### Claimed performance

NONE CLAIMED

### Vagueness log

1. Fibonacci levels: UNDEFINED-PARAM (which retracement levels to use? how to identify "important" ones?)
2. Stochastic period: UNDEFINED-PARAM
3. Stochastic overbought/oversold threshold: UNDEFINED-PARAM (standard is 80/20, but not stated here)
4. Divergence definition: UNDEFINED-RULE (standard vs. hidden; confirmed how?)
5. "Price rejected": VISUAL-ONLY (what constitutes rejection? wick only? close?)
6. "Important FIB level": UNDEFINED-RULE (which Fib levels? how to determine importance?)
7. Stop loss: NOT STATED
8. Take profit: NOT STATED
9. Position sizing: NOT STATED

### Mechanizability

PARTIAL. Stochastic divergence can be coded if standard parameters are used (period 14, levels 80/20), and Fibonacci levels are mechanically computable. However, the video specifies neither parameters nor what constitutes "rejection" or "importance."

---

## General Framework: The Balance

### Leading Indicators Only [08:00-08:30]
"Rely only on leading indicators and chances are you will see a lot of false signals" [08:00-08:30].

### Lagging Indicators Only [08:30]
"Rely only on lagging indicators and you will likely enter late and hold on your trades too long and give back most of the profits" [08:30].

### Combined Approach [08:30-09:00]
"The trick is to achieve the proper balance by mixing leading and lagging indicators across time frames. If you can accomplish this objective, you can come up with a trading approach which is far superior to using either of the two exclusively" [08:30-09:00].

---

## Notable claims and caveats

- "Almost every technical indicator is a lagging indicator. Moving averages, MACD, the RSI, Stochastics, you name it, are lagging" [04:30-05:00].
- "Always remember that the price moves indicators – not the other way around" [05:30].
- Lagging indicators are "never profitable when you look at them at the left side of the chart when the price action is already unfolded" [05:30-06:00]. (Speaker means: they only look good in hindsight after the move is complete.)
- "Do not let this draw you into a false sense of security that you can make the best decisions and make money consistently" when using multiple lagging indicators [02:30-03:00].
- Video warns against false confidence in using only lagging indicators [02:30-03:00].
- No mention of costs, spread, slippage, or commission.
- No mention of drawdown, losing streaks, or risk management specifics.
- No quantified performance metrics provided.

## Video Classification Note

This is a CONCEPT/EDUCATIONAL video providing a framework for thinking about indicator categories and their combination. It does not present a complete, standalone trading strategy, though it gives two examples of how to combine leading and lagging indicators. All three examples (EMA crossover, 200 EMA + Pivot Points, Fibonacci + Stochastic) lack complete stop/target specifications, making them unsuitable for direct backtesting without additional assumptions.
