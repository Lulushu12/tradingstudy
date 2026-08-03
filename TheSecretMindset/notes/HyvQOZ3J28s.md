# I Decoded The Liquidity & Manipulation Algorithm In Day Trading

- video_id: HyvQOZ3J28s
- url: https://www.youtube.com/watch?v=HyvQOZ3J28s
- duration: 14:47
- classification: STRATEGY

## Summary
This video teaches a liquidity clearout trading strategy that exploits predictable institutional behavior: market makers deliberately trigger stop losses at symmetric price structures, absorb the resulting sell-off liquidity, and then rapidly reverse price back into the structure. The strategy focuses on identifying symmetrical support/resistance zones with multiple historical bounces, placing price alerts at structural extremes, monitoring volume, and entering after the clearout reversal begins. The speaker emphasizes timing (the reversal should happen within 3-10 candles) and volume confirmation as key entry signals.

## Instruments and timeframes stated
- markets: Mentions Forex, crypto, stocks but does NOT specify which markets the strategy applies to; notes that crypto and Forex are "very liquid markets" where clearouts happen frequently [03:00-04:00]
- timeframes: Examples use 1-minute charts; notes that reversal speed varies by market liquidity ("1-15 min in crypto/FX" vs "15-30 minutes" in less liquid markets) [06:30-07:00]; also mentions using multiple timeframes
- sessions/hours: NOT STATED

## Strategy 1: Liquidity Clearout Entry (Breakout and Reclaim)

### Indicators and settings
- Structural support/resistance levels: NOT STATED (visual identification required)
- Volume: Essential but no specific threshold defined
- Lowest low or highest high of structure: NOT STATED (requires visual measurement)
- "10 candles rule" timer: Maximum 10 candles for reversal; "best scenario" = 3-5 candles [09:30-10:00]
- Structural symmetry: Must have multiple bounces from the same level [04:30-05:00]

### Context / bias filter
1. Identify a symmetrical structure with multiple bounces from support/resistance [04:30-05:00]
2. Structure must be "clean and symmetric" with evenly positioned lows (for longs) or highs (for shorts) [13:30-14:00]
3. Multiple bounces confirm the level is "defended"; the more bounces, the better [04:30-05:00]
4. Time element: "The more time passes, the more the liquidity will increase" if price cannot break the area [05:00-05:30]
5. Avoid asymmetric structures where highs or lows are unevenly positioned - "hard to base the entry" [14:00-14:30]

### Entry trigger
1. Price alert set below the structural low (for long entries) or above the structural high (for short entries) [10:00-10:30]
2. Alert fires: Price breaks through the structural support/resistance level (liquidity clearout) [10:00-10:30]
3. Significant volume traded at the clearout level [11:00-11:30]; "increased considerably once the lowest low in the structure was taken out" [11:30]
4. Wait for rapid price reversal back into support/resistance [06:30-07:00]
5. Enter on the reversal move back above support (for long) or below resistance (for short) [11:30-12:00]
6. Speed is critical: "The faster the price reclaims support and pushes above after the clearout, the better the trade" [13:30]. "Best trades" reclaim support within 5 candles [13:30]

### Stop loss
- Below the most recent low of the clearout / lowest low of the structure [11:30-12:00]
- Speaker specifies: "Your risk should be the lowest low of the clear-out. This is where your stop loss should be." [11:30-12:00]

### Take profit / exit
NOT STATED. The video does not specify profit target placement or exit conditions.

### Invalidation / skip conditions
1. Price does not reclaim support after clearout: "If it does not reclaim, there is no trade in the first place, it's a breakout" [13:00-13:30]
2. Reversal takes longer than 10 candles (the "10 candles rule") [09:30-10:00]
3. Structure is asymmetric with unevenly positioned lows/highs [14:00-14:30]
4. No significant volume at the clearout level [11:00-11:30]
5. Clearout triggered in the middle of the structure (non-targeted) rather than at clear extremes [08:30-09:00]

### Claimed performance
NONE CLAIMED. No specific win rate, risk-reward multiple, profit statistics, or drawdown mentioned.

### Vagueness log
1. VISUAL-ONLY: Symmetrical structure identification - speaker shows examples but does not provide quantifiable definition of "symmetrical" or "evenly positioned lows"
2. UNDEFINED-PARAM: Lowest low / highest high measurement - how to measure the "deepest" low in an asymmetric structure is shown but rules are not mechanically defined [07:30-08:00]
3. UNDEFINED-PARAM: Volume threshold - "significant volume traded" is not quantified (e.g., 2x average? above 90th percentile?)
4. UNDEFINED-RULE: "Targeted vs non-targeted" clearout distinction - speaker says targeted attempts are "initiated in the middle of the structure where not much liquidity sits" but boundary is not defined [08:30-09:00]
5. UNDEFINED-PARAM: Multiple bounces "quality" - "the more bounces, the better" but no minimum threshold given
6. SUBJECTIVE: Time passed creating liquidity buildup - "more time = more liquidity" is stated but no quantifiable threshold (days? weeks?)

### Mechanizability
PARTIAL. The core entry (wait for price to break structural low + wait for reversal) can be coded if structural lows/highs are pre-defined. The 10-candle timing rule is mechanizable. However, identifying "symmetrical structures" and determining "evenly positioned lows" requires human visual judgment or external input. Volume confirmation lacks a defined threshold. Stop loss placement is clear (lowest low), but profit taking is undefined.

## Notable claims and caveats
- "Price tends to move from structure to structure" [00:30]
- "Smart money knows how retail traders think" and uses stops clustering at key levels against them [02:30-03:00]
- "Institutional players cannot trade the same as retail traders because in low liquidity price areas, they might push price too much" - so they target high liquidity zones [03:30-04:00]
- Liquidity clearouts are especially common in crypto and Forex because "inexperienced traders...usually buying around the lows and highs" [04:00]
- Reversal speed varies by market: "1-15 min in crypto/FX" vs "15-30 minutes" in less liquid markets [06:30-07:00]
- "The fastest the price reclaims support and pushes above after the clearout, the better the trade" - confirms timing is critical for quality [13:30]
- No mention of transaction costs, spread, slippage, or commission
- No mention of drawdown, maximum losing streak, or underperformance periods
