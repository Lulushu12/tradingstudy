# The 200 EMA Confluence Trading Strategy You've Been Waiting For

- video_id: imp63ZnLyck
- url: https://www.youtube.com/watch?v=imp63ZnLyck
- duration: 16:05
- classification: STRATEGY

## Summary

The video teaches a confluence-based trading strategy using a 200-period EMA channel combined with static price levels (support/resistance, chart patterns, trendlines) and optional Fibonacci retracements. The 200 EMA is plotted twice: once on high prices (upper band), once on low prices (lower band), forming a dynamic channel. Entries occur when price reaches a confluence zone where the EMA channel aligns with a static resistance/support level. The strategy targets minimum 3:1 risk-reward; stops are moved to breakeven once price breaks important swing levels.

## Instruments and timeframes stated

- markets: EUR/JPY, Nvidia stock, DAX index (forex, equities, indices) [04:00, 06:00, 07:00]
- timeframes: 5-minute, 15-minute, 30-minute examples shown [06:00, 04:00, 07:00]
- sessions/hours: NOT STATED

## Indicators and Settings

- 200-period EMA applied to high prices (upper band) [03:00-03:30]
- 200-period EMA applied to low prices (lower band) [03:00-03:30]
- This creates a "channel which is much better than a simple line" [03:30]
- Optional: Fibonacci retracement for additional confluence [05:30, 06:30, 09:30]
- Optional: Chart patterns, trendlines, round numbers [04:30, 10:00, 09:30]

## Strategy: Confluence Zone Entry

### Core Principle

"Confluence is when there is more than one signal coming together at point in the market. The more technical tools that validate a price move or simply confirm the significance of a price level, the stronger that level is" [00:00-00:30]

"When you find a setup that has the same price signal from multiple methodologies, you have found a high probability trading opportunity" [01:00]

### Context / bias filter

Determine market bias (trend direction) using:
- EMA channel position: price above = bullish, below = bearish [04:00, 07:00]
- Price structure: higher highs/lows = uptrend, lower highs/lows = downtrend [05:30-06:00]
- Chart patterns and trendlines [10:00-12:00]

### Entry trigger (LONG setup)

1. Market in confirmed uptrend
2. Price above 200 EMA channel
3. Price approaches confluence zone where:
   - Static support/resistance level (break-and-retest, swing low, etc.)
   - Aligns with 200 EMA channel (lower band for support, upper band for resistance)
   - Optional: Fibonacci level, round number, chart pattern (double bottom, etc.) [05:30, 09:30, 11:00]

Example: "If price reaches this zone, we'll go long... The confluence zone is more evident now. It's right here where the 200 EMA channel and the resistance area meet" [06:00]

### Entry trigger (SHORT setup)

Inverse of long:
1. Market in confirmed downtrend
2. Price below 200 EMA channel
3. Price approaches confluence zone where:
   - Static resistance level (break-and-retest, swing high, etc.)
   - Aligns with 200 EMA channel
   - Optional additional confluence factors

### Stop loss

"Stop loss above the EMA channel" (for shorts) [05:00]
"Stop loss below the channel" (for longs) [06:30]

Implied: stop placed just beyond the opposite edge of the EMA channel

### Take profit / exit

Primary target: "target the next swing low/high in the price structure" [05:00, 06:00]

Minimum risk-reward: 3:1 [05:00]

Better target with more confluence: 5:1 [06:30, 11:30]

Risk management: "Once price breaks an important swing in the price structure, remove the risk from the trade and move your stop to break even. Now, we can't lose money. We are in a risk-free trade" [08:00]

### Invalidation / skip conditions

- Do NOT trade if confluence zone is weak or single-signal only [04:00]
- Example failure: "The confluence zone wasn't strong enough" [09:00]
- Skip if price moves straight through without pullback to confluence: "sometimes you'll miss the opportunity" [14:00]

### Claimed performance

NONE CLAIMED. Multiple examples shown (some wins, some losses):
- EUR/JPY: win [05:00]
- Nvidia: win [06:00]
- DAX: initially loss, then wins [08:00-09:30]
- One explicit loss shown [14:00]

## Confluence Factors (Ordered by Power)

Speaker emphasizes different types of confluence:
1. EMA channel + static price level (foundational)
2. + Fibonacci level [05:30, 06:30]
3. + Chart pattern (double bottom, head-and-shoulders, double top, etc.) [10:00, 11:00, 12:00]
4. + Trendline breakout [11:30, 12:30]
5. + Round numbers [09:30]
6. + Volume analysis (liquidity clearout) [09:00]

## Vagueness log

1. UNDEFINED-PARAM: Support/resistance level identification — which previous reaction points matter? [02:00]
2. UNDEFINED-RULE: "Important" swing high/low — what minimum move size qualifies? [05:00]
3. UNDEFINED-RULE: Fibonacci "golden zone" — which levels? 38.2%, 50%, 61.8%? [06:30]
4. UNDEFINED-PARAM: Exact entry candle — at confluence zone touch or after confirmation candle? [04:30]
5. UNDEFINED-RULE: EMA channel width — how far from channel to consider "aligned"? [04:30]
6. UNDEFINED-PARAM: Chart pattern completion — at what point is double bottom/top "confirmed"? [10:00]
7. SUBJECTIVE: "Strong confluence" vs "weak confluence" — no quantitative criteria [09:00]
8. UNDEFINED-PARAM: Round numbers — which values? 100, 1000? Depends on market? [09:30]
9. UNDEFINED-RULE: "Liquidity clearout" signal — how to identify mechanically? [09:00]
10. UNDEFINED-PARAM: Risk-reward calculation — reference points for swing highs/lows? [05:00]

## Mechanizability

PARTIAL

EMA channel calculation (200-period on high/low) is fully mechanized. Swing high/low detection can be automated. Support/resistance from prior swings is mechanizable. Fibonacci levels are standard calculations. However, significant gaps: (1) confluence "alignment" is vague (how close must levels be?); (2) chart pattern recognition (double bottom, head-and-shoulders) is discretionary; (3) trendline identification is subjective; (4) "liquidity clearout" has no clear definition; (5) "strong" vs "weak" confluence has no objective criteria; (6) exact entry candle within confluence zone not specified. Framework is partially mechanizable, but confluence filtering and entry timing require manual judgment.

## Notable claims and caveats

- "In day trading, there are many conflicting concepts. Trend lines are broken. Fibonacci is irrelevant. Chart patterns don't work. Support and resistance trading is broken" [00:00]
- "I'll tell you what worked for me. Confluence" [00:00]
- "The more technical tools that validate a price move or simply confirm the significance of a price level, the stronger that level is" [00:30]
- "Finding a confluence is key and could eliminate noise when it comes to validating a signal" [01:00]
- "I always pay close attention to support and resistance areas... The break and retest pattern is especially important in our strategy" [01:30-02:00]
- "Lately, I've stopped using moving averages which are applied to the close price. I prefer to use two moving averages with the same period... This creates a channel which is much better than a simple line" [03:00-03:30]
- "The strategy consists in finding areas where critical price levels and the EMA channel converge. One static support and resistance level and a dynamic one aligning on the same area" [04:00]
- "That's a risk-to-reward ratio of three, which is the minimum target you should aim" [05:00]
- "It's important to remain disciplined and patient, and don't get frustrated or angry. You will see many similar setups, and you will wait for a retracement to your confluence zone, but sometimes you'll miss the opportunity" [13:30-14:00]
- No overall win rate or Sharpe ratio provided
- No discussion of commissions, spreads, slippage, or transaction costs
