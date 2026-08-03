# 99% Of Scalpers Missed This "Double VWAP" Hack (VWAP Heiken Ashi Trading Strategy)

- video_id: 4xIAZ7vSsRY
- url: https://www.youtube.com/watch?v=4xIAZ7vSsRY
- duration: 15:03
- classification: STRATEGY

## Summary
This video presents a scalping/day trading strategy combining Heikin Ashi candlesticks, Volume Weighted Average Price (VWAP) indicator with bands, and optional momentum oscillators (RSI, MACD). The strategy identifies confluence zones where support/resistance levels align with VWAP bands, then uses Heikin Ashi price action for entry confirmation. The core thesis is that institutional traders use VWAP to execute large positions, creating tradeable opportunities for retail traders who align with this activity.

## Instruments and timeframes stated
- markets: NOT STATED (examples shown on various charts but no specific instruments recommended)
- timeframes: NOT STATED (strategy appears applicable to intraday trading but no specific timeframe designated)
- sessions/hours: NOT STATED

## Strategy 1: VWAP Confluence with Heikin Ashi Confirmation

### Indicators and settings
- Heikin Ashi candles: enabled [01:00-01:30]
- VWAP (Volume Weighted Average Price): standard calculation, NOT STATED which price source [03:00-03:30]
- VWAP bands: two sets recommended [06:00-06:30]
  - First set: standard deviation = 1 [06:30]
  - Second set: standard deviation = 2 [06:30]
- Optional momentum oscillator: RSI [11:30-13:30] or MACD [13:00-13:30] for divergence confirmation [11:30]

### Context / bias filter
- Price must be in a clear trend, not sideways [05:30]
- Confluence areas require overlap of support/resistance levels with VWAP bands [08:00-08:30]
- For long entries: look for confluence in support zones aligned with lower VWAP bands [08:30-09:00]
- For short entries: look for confluence in resistance zones aligned with upper VWAP bands [09:00-09:30]
- Market participants must show institutional activity through price rejection at confluence [06:00-06:30]

### Entry trigger
**Long entry:** 
- Price tests a confluence zone (support level meets lower VWAP band) [09:00-09:30]
- Heikin Ashi shows green candle with minimal or no lower shadow [09:00-09:30]
- Price action shows rejection with bullish reversal candlestick [09:30]

**Short entry:**
- Price tests a confluence zone (resistance level meets upper VWAP band) [09:00-09:30]
- Heikin Ashi shows red candles with strong downtrend (no upper shadows) [09:30-10:00]
- Price action shows rejection with bearish reversal candlestick [09:30]

Optional: Momentum divergence on RSI or MACD for additional confirmation [11:30-13:30]

### Stop loss
- Longs: placed below the confluence area/support level [09:00-09:30]
- Shorts: placed above the confluence area/resistance level [09:30]

Exact distance NOT STATED.

### Take profit / exit
- Partial position closure at intermediate VWAP band levels [09:00-09:30]
- Primary targets at VWAP bands (outer bands at standard deviation 1 and 2) [09:00-09:30]
- Exact target levels: NOT STATED which band is first/second target
- Depends on "recent price action" [09:30]

### Invalidation / skip conditions
- If price trades sideways near VWAP with no institutional interest, stay away [05:30]
- If confluence area is unclear or weak, skip the setup [11:30]
- If no momentum confirmation is visible, avoid the trade [11:30]

### Claimed performance
- "A high-probability resistance confluence point" [12:00-12:30]
- "High-probability support level" with bullish divergence confirmation [12:30-13:00]
- "Strong uptrend" and "strong downtrend" moves demonstrated in examples [10:00-10:30]
- NONE CLAIMED in terms of specific win rate, profit factor, or R-multiple

### Vagueness log
1. UNDEFINED-PARAM: Exact number of periods/bars for VWAP calculation not stated
2. UNDEFINED-PARAM: Which price source (close, HL2, etc.) for VWAP calculation
3. UNDEFINED-RULE: How to identify "clear trend" vs. sideways market—no specific thresholds
4. UNDEFINED-RULE: Definition of "strong reaction" or "rejection" at confluence—subjective pattern recognition
5. UNDEFINED-PARAM: Distance from support/resistance for stop loss placement
6. UNDEFINED-RULE: Which VWAP band(s) to use as first/second take profit target
7. SUBJECTIVE: Identification of "confluence" zones depends on subjective level drawing
8. SUBJECTIVE: "Strong downtrend shown by consecutive red candlesticks" is visual pattern recognition
9. UNDEFINED-RULE: Criteria for using momentum oscillator vs. ignoring it
10. VISUAL-ONLY: "Observe how the price rejected our area" with specific candle patterns relies on chart visualization

### Mechanizability
**PARTIAL** — The skeleton is computable (VWAP + band calculation + confluence detection) but critical gaps require subjective judgment: identifying confluence zones depends on manually drawn support/resistance levels, and entry confirmation ("strong reaction," "rejection") requires pattern recognition that cannot be coded from OHLCV alone without specifying exact candle characteristics.

## Notable claims and caveats

- Speaker emphasizes that professionals use price and volume as the two key elements [00:30]
- Institutional traders use VWAP to optimize large position entry/exit, which creates opportunities for retail traders [04:00-05:30]
- VWAP bands with standard deviation (1 and 2) reveal "hidden support and resistance" [06:00-06:30]
- Strategy requires "confluence" (multiple signals at one price level) for best setups [07:30-08:00]
- No discussion of drawdown, losing streaks, or conditions where strategy fails
- No mention of trading costs, spread, slippage, or commissions
- No specific performance statistics (win rate, profit factor, etc.) provided
