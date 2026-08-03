# I Studied Order Flow Trading for 5 Years — Footprint Charts Beat Everything

- video_id: kcglxDJ_ZF0
- url: https://www.youtube.com/watch?v=kcglxDJ_ZF0
- duration: 16:01
- classification: STRATEGY

## Summary

Teaches how to read footprint charts to see the distribution of buyers and sellers at each price level, revealing smart money activity hidden in regular candles. Explains three core concepts: delta (cumulative buyers minus sellers), imbalances (price levels where one side massively dominates), and absorption (high volume with no price movement indicating accumulation). Combines these into a three-step entry framework for identifying high-probability longs at demand zones and shorts at supply zones.

## Instruments and timeframes stated

- markets: NOT STATED
- timeframes: NOT STATED
- sessions/hours: NOT STATED

## Strategy 1: Footprint Chart Long Entry at Demand Zone

### Indicators and settings

- Footprint chart displaying bid/ask volume at each price level [01:00-01:30]
- Delta calculation: buyers (ask hits) minus sellers (bid hits), displayed as net at bottom of candle [03:00-04:00], color-coded green (positive) or red (negative) [04:00]
- Stacked imbalances: defined as "three or more imbalances in a row at consecutive prices" indicating institutional activity [08:30-09:00]
- Ask imbalance (at low): buyers lifting offers, bullish pressure [08:00-08:30]
- Volume: general high/low comparison, no moving average or specific period stated
- No traditional indicators (moving averages, RSI, etc.) mentioned

### Context / bias filter

- Identify key support, resistance, supply, demand zones via structure first [13:00-13:30]
- Price pulls back into a demand zone [13:30]
- Demand zone should have prior stacked ask imbalances showing "where aggressive buying or selling already proved itself" [09:00-09:30]

### Entry trigger

- Price approaches demand zone where stacked ask imbalances previously appeared [13:30-14:00]
- Check delta: turning positive, indicating buyers starting to win [14:00]
- Look for stacked ask imbalances at current zone: buyers attacking aggressively with conviction [13:30-14:00]
- Check for absorption: price should respond to buying, NOT be absorbed (high volume with no movement) [14:00-14:30]
- All three conditions met ("three green lights") = enter [14:30]

### Stop loss

NOT STATED

### Take profit / exit

NOT STATED

### Invalidation / skip conditions

- If absorption occurs (massive buying/delta but price doesn't move), DO NOT enter; wait for the absorbed side to break [12:00-12:30]
- If delta diverges from price (price higher but delta shrinking/negative = exhaustion), hold off entry [05:00-05:30]

### Claimed performance

NONE CLAIMED

### Vagueness log

1. Supply/demand zone identification – VISUAL-ONLY: video says "identify your key levels" but only shows this visually on chart; no algorithmic definition provided [13:00-13:30]
2. "Stacked imbalances" – UNDEFINED-PARAM: states "three or more in a row at consecutive prices" but "consecutive" at what price interval? [08:30-09:00]
3. "Consecutive prices" – UNDEFINED-RULE: does this mean every single price level, or adjacent price clusters?
4. Delta "turning positive" – SUBJECTIVE: no threshold for what constitutes a "turn"; how many candles must delta be positive?
5. "Conviction" from imbalances – SUBJECTIVE: no quantified threshold for imbalance size
6. "Price responds to buying" / "no absorption" – SUBJECTIVE: what % movement = responds? How is "tiny candle body" quantified? [11:30-12:00]
7. Stop loss placement – NOT STATED
8. Take profit targets – NOT STATED

### Mechanizability

PARTIAL. The core framework (delta calculation, imbalance detection, absorption identification) is mechanically computable if you have footprint/tick data. However, the entry setup critically depends on pre-identified "supply/demand zones" which are shown visually in the video with NO stated algorithmic definition [VISUAL-ONLY]. Additionally, thresholds for "stacked" imbalances (exact count and price interval), confirmation that delta is "turning," and whether "absorption" is occurring are all SUBJECTIVE without defined parameters. Stop loss and profit targets are not stated. A discretionary trader could reliably spot these patterns visually; a programmer would need to invent multiple threshold assumptions.

## Notable claims and caveats

- Claims 95% of traders only see candles and don't have footprint edge [02:30]
- Says reading footprints is "10 times easier" once delta is understood [03:00]
- Footprint reveals when "big money is quietly selling into that strength" even when candle closes green [00:00-02:00]
- Describes imbalances as showing "conviction, not just participation" [07:00-07:30]
- Compares absorption to "a wall eating everything thrown at it" [10:30-11:00]
- Presented as confirmation tool, NOT standalone system: "footprint is never a standalone system. It's confirmation. Structure tells you where to look. Footprint tells you what's happening there." [13:00-13:30]
- Never mentions: transaction costs, spreads, slippage, commission
- Requires access to footprint chart data (NOT available on all brokers or markets)
