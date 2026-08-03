# This Price Action Strategy Beats 10,000 Hours of Day Trading

- video_id: owz1w37cVHs
- url: https://www.youtube.com/watch?v=owz1w37cVHs
- duration: 13:10
- classification: TOOLING

## Summary
A comprehensive trading framework presenting seven sequential filters for validating trade setups. The filters are: direction (impulse vs correction), location (key support/resistance levels), trigger (specific entry confirmation), volume confirmation, timeframe alignment, risk-to-reward calculation, and psychology/mental state. Rather than a single strategy, this teaches a decision-making methodology applicable to any entry pattern. Examples include engulfing candles, pin bars, and long wicks as potential triggers, but no single strategy is fully defined.

## Instruments and timeframes stated
- markets: Not specified (examples use various charts)
- timeframes: Higher timeframe for context (hourly, 4-hour mentioned), lower timeframe for entries (5-minute, 15-minute mentioned for day trading)
- sessions/hours: NOT STATED

## Seven-Filter Trading Framework (Not a complete single strategy)

### Filter 1: Direction Filter

**Context**: Identify impulse vs correction. Impulses are larger moves; corrections are smaller retracements [00:00 - 01:00]. Only trade in impulse direction [00:30]. A correction is still part of trend if it remains smaller than the impulse [01:00].

**Shift condition**: When a correction grows larger than the previous impulse, it signals potential trend reversal; stop trading that direction until market proves itself again [01:30 - 02:00].

### Filter 2: Location Filter

Key levels are areas where price "tends to bounce or break" [02:30]. Price moves toward levels "like a magnet" [02:30]. Mark these levels on higher timeframe (hourly or 4-hour) first [03:30 - 04:00]. Examples: resistance zones that rejected price multiple times, support levels [03:00 - 03:30].

Do NOT enter just because price reaches a level; location alone is not sufficient trigger [03:30].

### Filter 3: Trigger Filter

Entry requires "something concrete" that "either happens or it does not" [04:00 - 04:30]. Examples of triggers mentioned:
- Bearish engulfing candle (red candle body completely swallows previous green one) [04:30]
- Long wick rejection candle at level [04:30 - 05:00]
- Pin bar [05:30]
- Break of mini trend line inside correction [05:30]

**Backup trigger required** [05:30 - 06:00]: If primary trigger doesn't form, have a plan B trigger showing the same idea.

**Rule**: "If I cannot point to the exact candle or pattern that told me to enter, then I did not have a trigger" [05:00].

### Filter 4: Volume Filter

Entry must be accompanied by above-average or increasing volume [07:00 - 07:30]. Weak or declining volume on entry trigger reduces confidence [07:30]. Examples:
- Breakout on below-average volume often reverses [06:30 - 07:00]
- Breakout on above-average volume tends to hold [07:00]

**Rationale**: "Volume tells you whether other participants agree with your idea. If they do not, you are trading alone" [07:30].

### Filter 5: Timeframe Alignment Filter

Use exactly two timeframes: higher timeframe for context, lower for entries [08:00]. Both must agree on direction [08:30 - 09:00].

**Violation example** [08:00 - 08:30]: 15-minute downtrend with bearish rejection candle (short setup) conflicts with 4-hour uptrend. Result: trade loses because shorting into bigger wave of buyers.

**Rule**: "If both time frames agree on direction, I take the trade. If they conflict, I walk away. No alignment, no trade" [08:30 - 09:00].

### Filter 6: Risk-to-Reward Filter

Stop loss placed at point where idea is proven wrong [09:30 - 10:00]:
- For long: below support
- For short: above resistance

Target placed at next level that could cause reversal against you [10:00]:
- For long: next resistance
- For short: next support

**Requirement**: "I need at least 2:1 or better" reward-to-risk [10:00 - 10:30].

Example: 20 pips risk, 60 pips target = ~3R (acceptable). 40 pips risk, 30 pips target = fail math (rejected) [10:30 - 11:00].

### Filter 7: Psychology Filter

Before entering, ask: "Does this feel like patience or desperation?" [11:30]. Best setups "jump out" with no forcing or convincing [11:30 - 12:00]. Skip if:
- Tired, distracted, unfocused [11:30 - 12:00]
- Revenge trading after losses [11:30]
- Hesitating or talking self into it [11:30 - 12:00]

**Rule**: "If I am not mentally right, stressed, frustrated, unfocused, whatever, I do not trade that day. Period" [12:00].

### Entry Summary (All seven filters required)

"All seven filters have to pass. Not five. Not six. All seven" [12:30].

### Claimed performance
"My routine takes less than 30 seconds" [00:00]. "This filter would have saved me thousands of dollars if I had learned it earlier" (referring to timeframe alignment filter) [08:00]. "This is only the foundation video" [12:30]. No specific win rate, profit metric, or R multiple stated.

### Vagueness log
1. UNDEFINED-PARAM: "Impulse" and "correction" are identified visually; no specific ratio or pip-count threshold stated [00:00 - 00:30].
2. UNDEFINED-PARAM: "Significantly larger" correction that triggers reversal alert has no quantified threshold [01:30 - 02:00].
3. UNDEFINED-PARAM: "Key levels" and "spots where price tends to bounce or break" are identified by past price action but no specific rules stated [02:30].
4. UNDEFINED-PARAM: Engulfing candle definition requires visual interpretation; no ratio stated for what counts as completely "swallowing" [04:30].
5. UNDEFINED-PARAM: "Long wick" trigger is subjective; no ratio stated [04:30 - 05:00].
6. UNDEFINED-PARAM: "Above-average volume" not quantified (how many standard deviations?) [07:00 - 07:30].
7. UNDEFINED-RULE: "Increasing volume" has no specific increase threshold stated [07:00].
8. SUBJECTIVE: Pin bar identification and mini trendline break are visual; no mechanical definition stated [05:30].
9. SUBJECTIVE: Psychology assessment ("does this feel like patience or desperation") is entirely judgment-based [11:30].

### Mechanizability
PARTIAL - The skeleton is mechanizable (impulse/correction identification via candle heights, volume comparison, timeframe alignment on direction, risk-to-reward calculation), but the core components cannot be fully coded without assumptions: what constitutes an "impulse" vs "correction" (requires ratio threshold), what counts as "above-average volume" (statistical threshold), and trigger identification (engulfing candle, pin bar, long wick all require wick/body ratio thresholds). At least 5 specific parameter gaps must be filled before a complete backtest is possible.

## Notable claims and caveats
- "Do not trade the correction. Trade the impulse direction, not the correction" [01:00].
- "If I cannot answer that [direction question] clearly, I do not have a trade. I have a guess" [02:00].
- "Price does not wander randomly. It moves toward these levels like a magnet" [02:30].
- On premature entries: "That is not a system. That is gambling with extra steps" [03:30].
- On volume: "Trading alone usually means losing" [07:30].
- On setup quality without proper filters: "Even with direction, location, and a clean trigger, you can still lose" [06:00 - 06:30].
- No mention of spread, slippage, commission, or drawdown.
- No historical backtest results or performance data provided.
