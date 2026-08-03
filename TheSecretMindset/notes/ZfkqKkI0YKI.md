# I Built The BEST Chart Analysis System For Day Trading (Complete Strategy)

- video_id: ZfkqKkI0YKI
- url: https://www.youtube.com/watch?v=ZfkqKkI0YKI
- duration: 22:32
- classification: STRATEGY

## Summary

This video presents an integrated day trading strategy built around market structure analysis and confluence-based entries. The system uses a 1-hour timeframe for trend bias and a 5-minute timeframe for entry timing. Core elements include: identifying trends via 50 EMA, finding support/resistance zones, spotting liquidity traps, using VWAP as an entry anchor, waiting for outside candle confirmation, and employing Fibonacci levels for precise targeting. A five-point scorecard filters high-probability setups.

## Instruments and timeframes stated

- markets: Euro/Dollar, Tesla, Bitcoin mentioned as examples; NOT STATED as specific requirement
- timeframes: 1-hour (structure and trend) and 5-minute (entry timing) [05:00]
- sessions/hours: NOT STATED

## Strategy 1: Confluence-Based Pullback Entry

### Indicators and settings

- 50 EMA: Added to identify trend direction. Price above = uptrend bias, below = downtrend bias [03:30]
- VWAP: Added to 5-minute chart; acts as entry anchor [12:30]. VWAP is "the true mean price for the day, weighted by volume" [12:30]
- Fibonacci retracement: 61.8% level (golden pocket) is the primary retracement level [18:00]
- Fibonacci extension: 1.618 and 2.618 extension levels used for profit targets [18:30]
- No other indicators used [05:00]

### Context / bias filter

**Trend confirmation:** 1-hour chart must show clear uptrend (price above 50 EMA with higher highs and higher lows) or downtrend (price below 50 EMA with lower lows and lower highs) [11:30].

**Market state:** Must identify if market is trending or ranging. In trending markets, look for dips to buy (uptrend) or rallies to short (downtrend). In ranging markets, look for bounces off boundaries [03:30-04:00].

**Location:** Price must be pulling back to a major support zone (uptrend) or resistance zone (downtrend) [11:30]. Best if this zone is a "role reversal" (former resistance that is now support in uptrend, or vice versa) [07:30].

### Entry trigger

**Setup (confluence location):**
1. 1-hour trend is established (uptrend or downtrend)
2. Price pulls back to key structural support or resistance zone
3. On 5-minute chart, that pullback is testing the VWAP line

**Signal (confirmation):**
The specific entry signal is an "outside candle" pattern at the VWAP level [16:00]:
- Bullish outside candle: A large green candle that completely engulfs the body of the previous red candle, showing buyers taking control [16:30]
- Bearish outside candle: A large red candle that engulfs the previous green candle's body [16:30]

Entry only occurs when this outside candle appears at the VWAP within the support/resistance zone [16:30]. "An outside candle in the middle of nowhere is meaningless" [16:30].

### Stop loss

NOT STATED explicitly. Implied to be just below the key support zone for long trades (the low of the support zone that price pulled back to).

### Take profit / exit

Use Fibonacci extension levels, specifically the 1.618 and 2.618 extension levels [18:30] as "where institutional traders often take profits" [18:30].

When the VWAP test also aligns with the 61.8% Fibonacci retracement level, the Fibonacci extension tool can be drawn from the start of the pullback swing, through the end of the pullback, to provide target levels [19:00].

### Invalidation / skip conditions

- If 1-hour chart is not trending or is ranging (50 EMA flat, price chopping around it), do not trade [03:30]
- If price does not pull back to a key support or resistance zone, skip the setup [20:30]
- If price is not testing VWAP on the 5-minute chart within that zone, do not trade [20:30]
- If no outside candle forms at the VWAP test, skip the trade [20:30]
- Do not take trades below a score of 4 out of 5 on the A+ Setup Scorecard [21:00]

### Claimed performance

NONE CLAIMED - No win rate, profit factor, or drawdown metrics are stated.

### Vagueness log

1. "Clear uptrend" / "clear downtrend" - SUBJECTIVE: higher highs and lows is qualitative, no specific percentage thresholds for minimum swing sizes
2. "Major support zone" / "key structural level" - SUBJECTIVE: determined by price having "repeatedly shown interest" (touched 2+ times) but no specific number defined
3. "Fresh zones" vs "tested zones" - SUBJECTIVE: "fresh" means "hasn't been revisited" but the definition of revisit is not quantified
4. "Role reversal" - SUBJECTIVE: determined by whether a level is now acting as opposite of original purpose, which is visually assessed
5. VWAP reacting "like a magnet" - SUBJECTIVE: no specific proximity defined for what constitutes a "test" of VWAP
6. "Outside candle" completely swallows body - UNDEFINED-PARAM: the exact percentage or pip tolerance for "engulfing"
7. "Large candle with high volume" - SUBJECTIVE: "large" and "high" are relative terms with no quantitative thresholds
8. "Market is screaming" vs "whispering" - SUBJECTIVE: no mechanical distinction
9. "Liquidity hunting" exact mechanics - UNDEFINED-RULE: how much price needs to move to "trigger" stops, and which stops are considered

### Mechanizability

PARTIAL - The 50 EMA trend identification and VWAP line tracking are mechanical. Fibonacci retracement levels are computed from swings. However, the core system requires subjective judgment on: identifying key support/resistance zones, determining what constitutes a "pull back" to that zone, assessing outside candle size and strength relative to "screaming" or "whispering," and selecting which Fibonacci levels to use. The system skeleton is codable, but critical entry confirmation relies on subjective candle pattern evaluation.

## Supporting Concepts

**Break of Structure [01:00-01:30]:** In an uptrend, price breaks above a previous swing high, confirming the trend is "still alive and kicking." This is a directional confirmation, not an entry signal on its own.

**Change of Character [01:30-02:00]:** In an uptrend, price breaks below the last major swing low. This signals the trend "might be in trouble" and is a warning to "be careful" or take profits and step aside, NOT a reversal signal.

**Liquidity and Inducement [08:30-10:30]:** The market is designed to hunt stop-losses placed at obvious levels (above resistance highs for shorts, below support lows for longs). Smart money pushes price to trigger these stops, collects the liquidity, then reverses for the real move. This teaches the trader to place stops in less obvious locations or use the concept to anticipate fake moves.

**Zone vs. Line [06:00-07:00]:** Support and resistance are "zones" (areas of interest), not thin lines. A zone is where price has "repeatedly shown interest," not a single price point.

## A+ Setup Scorecard

This is the quality-control system that filters trades. Every setup gets scored on five criteria; only take if score is at least 4 out of 5 [19:30-20:30]:

1. **Trend point:** Is the 1-hour chart trending (price clearly above/below 50 EMA with clean structure)? Yes = 1 point
2. **Zone point:** Is price testing a key support or resistance zone? Yes = 1 point
3. **VWAP point:** On 5-minute, is price testing VWAP inside that zone? Yes = 1 point
4. **Fibonacci point:** Does VWAP test align with 61.8% Fibonacci retracement? Yes = 1 point
5. **Signal point:** Is there a clear outside candle signal showing strong rejection/conviction? Yes = 1 point

**Scoring interpretation [21:00-21:30]:**
- 5 points: Perfect trade
- 4 points: Excellent trade (recommended minimum)
- 3 points: Average trade (pass according to strategy)
- Below 3 points: Do not trade

## Notable claims and caveats

- "All those indicators are just fancy ways to lose money faster" - The 50 EMA and VWAP are positioned as the only necessary indicators [00:30]
- "Price is the only thing that pays you. Everything else is just noise" [05:30]
- "The market is designed to take your money" - Emphasizes liquidity hunting as a real market mechanism [08:30]
- "Most traders get stopped out right before the move goes in their favor. They're not unlucky—they're predictable" [10:30]
- "Most traders take three-point trades and wonder why they're not making money. You're going to wait for four and five-point trades" [21:00]
- The strategy requires discipline to wait for confluence alignment rather than trading "because you're bored or feel like you should be in the market" [20:30]
- Does NOT discuss spread, slippage, commissions, or position sizing
- Does NOT discuss drawdown, losing streaks, or what the strategy fails at
- Does NOT mention volume thresholds for outside candle confirmation, only that "high volume" is better than low volume [17:30]
