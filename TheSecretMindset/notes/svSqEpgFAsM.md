# The 'Volume Delta' Scalping Strategy That Quietly Prints (Orderflow Trading)

- video_id: svSqEpgFAsM
- url: https://www.youtube.com/watch?v=svSqEpgFAsM
- duration: 15:14
- classification: STRATEGY

## Summary

This video presents a 5-minute scalping strategy using the volume delta indicator to identify genuine level breaks versus traps. The key insight is that price breakouts are not entry points; instead, the strategy waits for a retest of the broken level and enters only if the volume delta on the retest candle matches the intended trade direction (green delta for longs, red delta for shorts). This approach filters out false breakouts and allows entry when institutional-level absorption of price pressure is confirmed.

## Instruments and timeframes stated

- markets: S&P futures mentioned in examples [10:30]; "futures contracts" referenced [10:30]; generalized application implied
- timeframes: 5-minute, explicitly stated as the strategy's timeframe [00:00]
- sessions/hours: NOT STATED

## Strategy 1: Volume Delta Retest Scalping

### Indicators and settings

- Volume delta indicator on TradingView [00:30]
- Delta interpretation: Green indicates buyers applying more pressure, red indicates sellers have more power [00:30]
- Delta components: candle-by-candle pressure measurement, not a calculated technical indicator with parameters
- Support/resistance levels: NOT STATED how to identify initial levels; video defers this to "next video" [15:00]

### Context / bias filter

The strategy operates on broken support and resistance levels [03:00]:
- A level is marked only when it is broken with a strong delta [03:00]
- Strong delta is required at the breakout; if delta is weak at breakout, the level is ignored [01:00-01:30]
- Definition of "strong delta": "delta bounce at the exact level" [01:30]; "strong green delta" [02:30]; "much larger than the previous delta bars" [02:30]; specific threshold NOT STATED
- Only retest phases after breakouts are tradeable [03:00-03:30]
- Target area must exist with at least 1.5:1 risk-reward ratio; "if the transaction can't offset at least one and a half times the risk, I abandon it" [05:30]
- Markets with breakable levels are assumed (volume delta is "proof that a certain level is worth noting") [01:30]

### Entry trigger

**Long Entry** [03:30-04:00]:
1. Price breaks above resistance with strong green delta at the breakout candle
2. Price retraces back to retest that resistance level
3. Retest candle may appear red or green (color irrelevant) [09:00]
4. Delta below the retest candle MUST be green [03:30, 04:00]
5. Entry: After the retest candle closes [04:00]
- Exception: "Even a perfect touch could still be a trap" if retest delta is red [05:00]

**Short Entry** [07:00-07:30]:
1. Price breaks below support with strong red delta at the breakout candle
2. Price retraces back upward to retest that support level
3. Retest candle may appear green or red (color irrelevant) [08:00-08:30]
4. Delta below the retest candle MUST be red [07:30, 08:00-08:30]
5. Entry: After the retest candle closes [07:30]
- Caution: "Most scalpers get shattered" by misreading short retests; "If the price rises above that level again, the retest will fail" [08:00-08:30]

**Key Rule** [06:30]:
"A break below a certain level acts as bait until retesting confirms it. This is a 'get in or get out' rule. If the price breaks through with a delta bounce, expect a retest."

### Stop loss

**Long**: "Stop loss is going back below the lowest level of the retest" [04:00]; exact distance NOT STATED
**Short**: "Stop loss is above the retest high" [07:30]; exact distance NOT STATED
General principle: "My stop loss is set below the retest low" [09:00] for longs

### Take profit / exit

"First goal requires at least one and a half times the risk" [04:00]
"Target requires at least one and a half times the risk" [07:30]
Minimum risk-reward ratio: 1.5:1
If target area cannot achieve 1.5:1, no trade [05:30]
Examples cited achieve targets at various multiples of risk but no specific exit trigger beyond reaching the 1.5R target area [04:00, 07:30]

### Invalidation / skip conditions

- Skip if breakout candle has weak delta; "If there is no jump in level, ignore the break" [03:00]
- Skip if retest delta does not match trade direction [05:00-05:30, 06:30]
- Skip if "The price is returning to its previous level. Contact looks perfect, but the delta in the test is red again" [05:00]
- Skip if target area is too close to achieve 1.5:1; "Beyond the entry point, a real prize area is needed" [05:30]
- Caution on short retests: If retest candle "is closing well above the broken support," no entry for shorts [08:00]
- If delta is ambiguous on retest, wait for clarity on following candle(s) [12:00-12:30]

### Claimed performance

"Chart A yields a clean 15-point scalping gain" vs "chart B instantly turns bearish and hits the $200 stop-loss" on identical-looking price patterns [00:00-00:30]; only the delta differentiated them
Multiple examples throughout video show successful retest entries that reached targets [04:00, 07:30, 11:00-11:30, 14:00-14:30]
"This filter saved you from a losing process" [12:00] - referring to delta matching rule
General claim: "Delta is your secret advantage. It protects you from chasing breakage, buying touch, and panicking over candle color" [12:30-13:00]
No statistical win rate, drawdown, or long-term performance metrics provided

### Vagueness log

1. UNDEFINED-PARAM: "Strong delta" or "strong green delta" at breakout not quantified; "much larger than the previous delta bars" [02:30] is relative and subjective; no absolute volume or delta value stated
2. UNDEFINED-PARAM: "Small delta bar" [01:00] is relative to context; no specific threshold
3. UNDEFINED-RULE: "Buyers showed strength precisely in the area" [01:30] - subjective assessment of delta
4. UNDEFINED-RULE: Identifying support and resistance levels in the first place; video defers this [15:00]: "this is the filter that separates A+ setups from random noise. This is the topic you'll cover in your next video"
5. UNDEFINED-RULE: "Real prize area" [05:30] - where a target exists; how to calculate or identify prospective target zones NOT STATED beyond "at least 1.5:1 ratio"
6. VISUAL-ONLY: "Touches the level," "breaks through," "rejects the level" are visual price action terms that assume chart observation
7. VISUAL-ONLY: "Buyers absorb it as sellers push the price down" [10:00] is visual/conceptual, not mechanically defined
8. UNDEFINED-RULE: "Delta deviation" concept [11:30] - red candle with green delta or green candle with red delta - pattern recognition based on visual anomaly
9. UNDEFINED-RULE: What constitutes "closing above" or "closing below" the level for retest candle; is it closing wick, close price, or touch [04:00, 07:30]
10. SUBJECTIVE: Determining when a retest "matches" the delta direction; "If the answer is unclear, the transaction is not available" [13:30] admits ambiguity exists
11. UNDEFINED-RULE: How to select which price levels to mark in the first place ("how to choose which levels are worth marking") [15:00]

### Mechanizability

PARTIAL - The core logic is mechanically computable: identify breakouts of user-defined levels, measure delta direction on the breakout candle and retest candle, and check if 1.5:1 risk-reward ratio exists from retest to a prospective target. However, three critical gaps prevent full automation: (1) initial support/resistance identification is deferred and not specified, (2) "strong delta" threshold is not quantified, and (3) target area placement is not algorithmically defined beyond "somewhere that achieves 1.5:1 ratio."

---

## Notable claims and caveats

- No discussion of commission, fees, or slippage impact on scalping profits
- No explicit win rate, drawdown range, or maximum losing streak disclosed
- Video emphasizes the delta indicator as "lie detector" [00:30] but relies on trader judgment to interpret delta strength
- Strategy is visual-heavy despite using quantitative delta data; trader must observe charts and "read the traces" [06:30]
- Highly specific to level-based trading; applicability to trend-following or momentum strategies not addressed
- Strategy deferral on level identification suggests this is only half of a complete system
- Video includes cautionary examples where valid setups failed ("didn't change the rules just because a valid transaction was lost") [06:00]
- Psychological warning: "In long retest, most people prefer a green candle...However, the market doesn't always give you a candle that looks clean" [09:30-10:00]; suggests trader bias toward "clean-looking" setups may cause missed entries
