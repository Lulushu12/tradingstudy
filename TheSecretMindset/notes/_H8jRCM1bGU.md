# How I Trade Order Flow With $0 (Full Price Action Strategy)

- video_id: _H8jRCM1bGU
- url: https://www.youtube.com/watch?v=_H8jRCM1bGU
- duration: 24:44
- classification: MULTI-STRATEGY

## Summary

The video teaches a framework for reading institutional order flow directly from candlestick patterns without additional software. It covers three main trading approaches: identifying liquidity sweeps followed by reversals, using imbalances as entry confirmation, and trading fair value area breakouts using auction market theory. The core philosophy is that price moves to hit stop-losses (liquidity) rather than for technical reasons, and every candle is a "receipt" of institutional activity.

## Instruments and timeframes stated

- markets: Pound/Dollar (GBP/USD), NAS 100, Gold, S&P 500, Euro/Dollar (EUR/USD) mentioned in examples
- timeframes: 5-minute, 1-hour, 15-minute mentioned in examples; NOT STATED for general application
- sessions/hours: London session, New York session, session highs/lows referenced; NOT STATED for specific time windows

## Strategy 1: Liquidity Sweep Reversal

### Indicators and settings

- candle body location: upper third (bullish), lower third (bearish), or middle (neutral) - no mathematical definition
- wick length: compared to body length, but NOT STATED as specific ratio
- liquidity pool: identified by "almost perfectly equal" prior highs or lows - NOT STATED how close they must be

### Context / bias filter

Price must show a liquidity pool (equal highs or equal lows from prior session) where retail traders are likely to have placed stops. The trader must be able to identify the exact location of "trapped" stops before taking the trade [03:30]. Market must be actively testing those levels [04:30].

### Entry trigger

Price sweeps (pokes) above equal highs or below equal lows by a small amount (few pips), then the candle closes back inside the prior range, leaving a wick. This is the "absorption receipt" [05:00]. Entry occurs when this absorption receipt is followed by an imbalance pointing in the direction of the reversal, at the 50% mark of that imbalance [06:30].

### Stop loss

Stop loss goes just below the sweep wick in long trades; NOT STATED explicitly for short trades but implied to be above [10:30].

### Take profit / exit

Target is the next liquidity area (obvious swing high or low where other traders may have stops), NOT STATED with a specific R multiple or pip target [17:00].

### Invalidation / skip conditions

- If the sweep is not followed by an imbalance, skip the trade [09:30]
- If the imbalance fires against the sweep direction (distribution trap), skip it [07:00]
- If the signal prints mid-range with no pre-marked level underneath, skip it [08:30]
- Wicks in the middle of a range are noise and should be ignored [08:00]

### Claimed performance

NONE CLAIMED - no win rate, profit target, or drawdown metrics are stated.

### Vagueness log

1. "few pips" - UNDEFINED-PARAM: no specific distance stated for sweep depth
2. "almost perfectly equal" - UNDEFINED-PARAM: no tolerance defined for equal highs/lows
3. "upper third of range" - UNDEFINED-RULE: the exact percentile calculation not stated
4. "imbalance" defined as big candle with little wicks - UNDEFINED-RULE: no specific candle body vs wick ratio provided
5. "aggressive move away from level" - UNDEFINED-RULE: how much movement constitutes aggressive
6. Exact methodology for identifying "pre-marked level" - UNDEFINED-RULE: only session highs/lows mentioned but not systematically defined
7. "clean imbalance" - SUBJECTIVE: no objective criteria for identifying cleanliness

### Mechanizability

PARTIAL - The skeleton (sweep detection, candle close location, imbalance presence) can be coded from OHLCV data, but at least 7 critical parameters must be filled in by assumption: tolerance for "equal" levels, definition of upper/lower thirds, candle clustering criteria for imbalances, and what constitutes "aggressive" continuation.

## Strategy 2: Fair Value Area Breakout and Rejection

### Indicators and settings

- Value area: identified by rotating price and finding where candles keep closing and pausing over 40-90 minute periods, NOT STATED as fixed minutes
- VWAP: mentioned at end as upgrade but NOT STATED with parameters

### Context / bias filter

First identify the fair value area by finding where price spent the most time and kept rotating [23:30]. Determine auction type: rotating (price rejects at both edges and returns to center) or trending (value keeps shifting in one direction) [22:00-23:00].

### Entry trigger

For continuation: Price breaks above or below the fair value area, creates an imbalance (no two-sided trading), pulls back but holds above/below the old value edge without falling back inside [18:30]. Entry after the pullback holds.

For rejection: Price breaks outside value but the next candle closes back inside the old box [17:30]. Then trade the return move toward the middle of the value area or the opposite edge [20:00].

### Stop loss

Stop goes behind the accepted area (above the breakout level for long continuations, below it for short) [17:00].

### Take profit / exit

Target is the next liquidity area (next obvious high/low where traders may have stops) [17:00]. For rejected breakouts, target the middle of the old value area or the opposite edge [20:00].

### Invalidation / skip conditions

- If price breaks above value but the pullback falls back inside old value completely, the breakout is invalidated (called "failed auction" or "rejection") [20:00]
- If the fast move (imbalance) fills completely back into old value, the continuation idea is dead [21:30]
- Do not chase breakouts; only trade after the market gives a verdict (acceptance outside value) [16:30]

### Claimed performance

NONE CLAIMED - the speaker does not provide win rate, profit targets, or drawdown statistics.

### Vagueness log

1. Fair value area size and formation - UNDEFINED-RULE: "40-90 minute rotation" is a range, exact duration not stated; "where candles keep closing and pausing" is SUBJECTIVE
2. "clean close" and "clean edge" - SUBJECTIVE: no mechanical definition
3. "builds value higher" - UNDEFINED-RULE: no quantitative criteria for what constitutes building value
4. Imbalance on fair value area - UNDEFINED-PARAM: relationship between fast candles and two-sided trading NOT STATED with specific metrics
5. "pulls back" - UNDEFINED-RULE: how much pullback before holding is confirmed
6. Rotating vs. trending auction classification - SUBJECTIVE: judgment call on what constitutes each type
7. VISUAL-ONLY: Multiple references to watching price "on the chart" visually without stated rules

### Mechanizability

PARTIAL - The entry and exit logic (breakout direction, pullback behavior, candle closes inside/outside zones) is mechanically computable, but the core definition of fair value area is subjective and non-computable without assumptions about rotation periods and what "keeps pausing" means.

## Strategy 3: Candle Receipt Reading (Foundation Framework)

### Indicators and settings

- None - purely candlestick price action reading, no external indicators
- Candle body position: upper third (bullish), lower third (bearish), middle (noise)
- Wick evaluation: compared to body length to identify rejections

### Context / bias filter

Only trade at pre-marked levels (session highs, session lows, previous day levels). Signal must have a level underneath it to have meaning [08:30]. Middle-of-range trading is to be avoided [24:00].

### Entry trigger

Binary rule [02:00]: If candle closes in upper third of range after sweeping a level, buyers won (long). If candle closes back inside the range after breaking it, sellers absorbed (short). Middle close is noise.

### Stop loss

NOT STATED - only mentioned that stop goes "just below the sweep wick" in the liquidity sweep example [10:30].

### Take profit / exit

NOT STATED in this section; referenced in other strategies.

### Invalidation / skip conditions

- A wick in the middle of a range is just noise [08:00]
- Red candle in upper third is actually bullish, not bearish [01:00]
- The identical wick at different locations (mid-range vs. at a level) has different meanings; only trade at pre-marked levels [08:00]

### Claimed performance

NONE CLAIMED

### Vagueness log

1. "upper third," "lower third" - UNDEFINED-RULE: no specific percentile range defined (e.g., 67-100%, or something else)
2. "receipt lies four times out of 10" - UNDEFINED-RULE: refers to which receipt type but does not specify conditions
3. Wick "almost twice the body length" - UNDEFINED-PARAM: no specific ratio provided; described as example not as rule
4. "big bodies" and "long wicks" - SUBJECTIVE: no quantitative thresholds

### Mechanizability

PARTIAL - Candle close location relative to range can be computed, but the definition of "upper third" is ambiguous, and the interaction with liquidity sweeps and imbalances adds layers of context that are subjective without stated parameters.

## Notable claims and caveats

- The speaker lost "hundreds of trades" by chasing momentum and being the last into the party, emphasizing importance of waiting for confirmation [06:30]
- Risk management: Speaker warns against trading mid-range noise and emphasizes location confirmation [08:30]
- Psychology: Retail traders panic on red candles and chase breakouts; the edge is waiting for market verdict, not speed [01:00]
- The speaker does NOT discuss spread, slippage, commissions, or drawdown periods
- Advanced traders know the same setup changes depending on auction type (rotating vs. trending) [22:00]
- The first sweep isn't always the trade; the imbalance signature is the filter [10:00]
