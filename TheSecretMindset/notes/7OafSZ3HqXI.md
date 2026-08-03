# The "2-Level" Signal Hiding on Every Chart | Simple 50 EMA Trading Strategy

- video_id: 7OafSZ3HqXI
- url: https://www.youtube.com/watch?v=7OafSZ3HqXI
- duration: 15:25
- classification: STRATEGY

## Summary

This video teaches "confluence" trading: the intersection of static support/resistance levels with a dynamic 50-period exponential moving average (EMA). The strategy focuses exclusively on bounce trades at these confluence zones, never breakouts. Entry rules are strict: price must approach the zone from the correct direction, bounce, and close away from it on the next candle. Risk is managed by placing stops just outside the confluence zone, with target set at 2x the risk.

## Instruments and timeframes stated
- markets: Examples show Pound/Yen, Dow Jones Index, Euro/Yen [10:00-13:00]; NOT STATED which markets required
- timeframes: 1-hour, 4-hour mentioned in examples [10:00, 10:30]; NOT STATED if required
- sessions/hours: NOT STATED

## Strategy 1: Confluence Zone Bounce Trading

### Indicators and settings
- Moving Average: 50 EMA (exponential, period 50) [03:30]
- Static levels: horizontal support/resistance identified by: prior price action bounces, recent 3-4 most significant levels [03:30], round numbers [02:30]
- Confluence zone: static level + 50 EMA within ~10 pips [05:00], or near-miss zones 15-20 pips apart [05:30]

### Context / bias filter
- Only trade bounces, NEVER breakouts [08:00]
- 50 EMA must be angled up (for long) or down (for short) [05:30]
- Only buy at support confluence; only sell at resistance confluence [05:30]
- Static level must be "real money has changed hands" - at least 1 bounce [02:00]
- Level carries more weight if recent rather than ancient history [03:00]

### Entry trigger
- Price approaches confluence zone from the correct direction [06:30]
- Price touches the zone and shows rejection ("kiss and bounce") [06:00]
- Price can poke through slightly; think in zones not exact lines [06:00]
- **Entry candle closes AWAY from the confluence zone** [07:00]
- NOT when price touches; NOT when inside zone; only after full candle closes in favor [07:00]

### Stop loss
- Buy trades: 10 pips below support [07:30]
- Sell trades: 10 pips above resistance [07:30]

### Take profit / exit
- Target: double the amount risked (1R = risk, target = 2R) [07:30]

### Invalidation / skip conditions
- If 50 EMA is flat, trend is weak; static levels become more important [04:30]
- If price breaks through confluence zone, do nothing and wait for next setup [08:00]
- Never try to pick tops in uptrend or catch falling knives in downtrend [07:30]
- Do not chase price to the zone; price must come to you [06:30]

### Claimed performance
- NONE CLAIMED (strategy presented without performance data)

### Vagueness log

1. UNDEFINED-PARAM: "Recent 3 or 4 levels that really stand out" - how to objectively select which 3-4? What if 5 levels appear equally significant? [03:30]
2. UNDEFINED-PARAM: "Round numbers" as psychological levels - no definition of what constitutes a round number [02:30]
3. UNDEFINED-RULE: "Breathing room" of 5-10 pips for zones [03:00] is stated but how strictly should this be applied?
4. UNDEFINED-PARAM: "Strong uptrend," "strong downtrend" - slope angle of 50 EMA NOT STATED [04:00]
5. UNDEFINED-RULE: "Rejection signal" / "kiss and bounce" [06:00] - how many candle wicks does it take before it's not a rejection?

### Mechanizability

PARTIAL. Entry logic is mostly computable: identify static levels from prior bounces, plot 50 EMA, check for confluence within defined pips, watch for close away from zone. Stops and targets are fixed. However, identifying "levels that really stand out" requires subjective interpretation of which bounce points matter most, and the definition of a valid "rejection" vs. a minor wick touch is vague.

## Notable claims and caveats

The speaker asserts that institutional traders are "placing orders in the same area" at confluence zones and these setups "don't come every hour" but "tend to work beautifully" [09:30]. One failed trade example is shown where price breaks through both support levels; the speaker notes "sometimes large institutional orders are placed beyond your levels" and advises never chasing a failed trade [13:30-14:30]. No win rate, draw-down, or R-multiple claims provided. No mention of costs, spreads, slippage, or commissions.
