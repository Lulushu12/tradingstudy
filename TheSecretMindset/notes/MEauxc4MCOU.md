# I Studied Smart Money Trading for 8 Years — Found This Strategy

- video_id: MEauxc4MCOU
- url: https://www.youtube.com/watch?v=MEauxc4MCOU
- duration: 30:11
- classification: MULTI-STRATEGY

## Summary
The video teaches a smart money trading system using supply and demand zones identified on a 30-minute chart, with entry confirmation on a 5-minute chart. The framework combines market structure analysis (impulsive vs. corrective moves, higher highs/lows for bullish trends, lower lows/highs for bearish) with three confluence factors: ultra-high-volume candles, VWAP band rejection, and change of character (CHoCH). Trades are only taken during London or New York sessions for adequate liquidity.

## Instruments and timeframes stated
- markets: Forex, indices, crypto (during London/NY sessions), stocks (NY session) [07:00-07:30]
- timeframes: 30-minute for market structure analysis, 5-minute for entry confirmation [00:00-00:30]
- sessions/hours: London and New York sessions [07:00-07:30]

## Strategy 1: Supply and Demand Zone Trading with Ultra-High-Volume Confirmation

### Indicators and settings
- Market structure identification: Bullish = higher highs and higher lows; Bearish = lower lows and lower highs [01:00-01:30]
- Supply/demand zone construction: Identify rally-base-rally (demand) or rally-base-drop (supply) patterns [04:00-04:30]
- Ultra-high-volume candles: Pin bars and engulfing candles [08:00]
- Volume threshold: NOT STATED (only described as "ultra high volume" or "high volume")

### Context / bias filter
Analyze the 30-minute chart for market structure direction. Trade only in markets showing strong trending with clear impulsive moves [00:30-01:30]. Focus on markets where momentum is strong and significant price movements (impulsive moves) are occurring [06:00]. Only trade during London or New York sessions for adequate liquidity and volatility [07:00-07:30].

### Entry trigger
1. Price retraces from an impulsive move and touches a supply or demand zone on the 30-minute chart [05:30].
2. Switch to 5-minute chart.
3. Look for a pin bar or engulfing candle with ultra-high volume at the zone [08:00-08:30, 12:00-12:30].
4. For long trades: pin bar or engulfing bar with high volume in a demand zone [08:30-09:00].
5. For short trades: pin bar or engulfing bar with high volume in a supply zone [08:30, 12:30].

### Stop loss
- For long trades: Below the demand zone [09:00, 19:30].
- For short trades: Above the supply zone [08:30, 13:00].
- Conservative interpretation: Place stop loss slightly beyond the zone boundary [13:00].

### Take profit / exit
At the next major supply or demand zones in the market structure [08:30, 09:00, 13:00]. Partial profits can be taken as the market moves in the trade direction [08:30].

### Invalidation / skip conditions
Do not trade outside main market hours (London or New York sessions) [12:30-13:00]. Do not take trades during Tokio session if the setup occurs there; wait for London open [12:30-13:00]. If price ignores the supply/demand zone completely, the imbalance may be invalidated and should not be traded [05:30-06:00].

### Claimed performance
NONE CLAIMED (Video presents setups as examples, not as backtested performance metrics.)

### Vagueness log
1. UNDEFINED-PARAM: "Ultra high volume" / "high volume" — no specific volume threshold, multiplier, or reference point given.
2. UNDEFINED-PARAM: "Pin bar" and "engulfing candle" — no wick-to-body ratio, size parameters, or confirmation rules specified.
3. UNDEFINED-RULE: "Market structure" and "impulsive move" — no quantitative definition; relies on visual pattern recognition (higher highs/lows or lower lows/highs).
4. UNDEFINED-RULE: "Strong market" — no definition of minimum move magnitude or volatility threshold.
5. SUBJECTIVE: "Rejection" of price at a zone — no specific candle pattern or continuation rule beyond a visual rejection.
6. VISUAL-ONLY: "Supply zone" and "demand zone" location — while the framework is described (rally-base-rally, rally-base-drop), exact zone boundaries depend on visual chart reading.

### Mechanizability
PARTIAL — The skeleton (identify structure, find zones, detect volume spikes) is codeable from OHLCV data, but three critical gaps must be filled by assumption: (1) volume threshold for "ultra high," (2) exact pin bar / engulfing candle parameters, and (3) zone boundary precision. The session filter and timeframe rules are mechanical, but the confluence signal requires manual parameter definition.

---

## Strategy 2: VWAP Band Trading

### Indicators and settings
- VWAP (Volume-Weighted Average Price): period NOT STATED (likely daily)
- VWAP bands: "First and second set of bands" plotted with "multiples of standard deviation" [16:30]
- Standard deviation multiplier: NOT STATED
- Entry zone: Between first and second VWAP band [16:30]

### Context / bias filter
Use within a supply/demand zone framework on the 30-minute chart. VWAP bands provide dynamic support/resistance as price retests zones identified on the higher timeframe. Works best when price is trending (not in choppy consolidation) [16:30].

### Entry trigger
1. Identify a supply or demand zone on the 30-minute chart [17:00-17:30].
2. On the 5-minute chart, observe price approaching the zone and the VWAP bands.
3. Enter when price enters the area between the first and second VWAP band, aligned with the zone [16:30, 19:00-19:30].
4. Optionally wait for a pin bar or engulfing candle for extra confirmation [18:30, 19:30].

### Stop loss
Above the supply zone (for shorts) or below the demand zone (for longs). Use the VWAP band as dynamic support/resistance reference [18:30, 19:30].

### Take profit / exit
At the next major supply or demand zones in the market structure [18:30, 19:30].

### Invalidation / skip conditions
If VWAP bands do not align with the identified supply/demand zone, the confluence is weak and the trade should be reconsidered [18:00-18:30].

### Claimed performance
NONE CLAIMED

### Vagueness log
1. UNDEFINED-PARAM: VWAP period — no specific lookback stated (assumed daily, but not confirmed).
2. UNDEFINED-PARAM: "First and second set of bands" — exact standard deviation multiples NOT STATED.
3. UNDEFINED-RULE: "Multiples of standard deviation" — the exact values (e.g., 1.0, 2.0) are never given.
4. SUBJECTIVE: "Aligned with the zone" — visual judgment of how closely VWAP bands must match the zone boundaries.
5. SUBJECTIVE: Confluence with pin bar or engulfing candle — extra confirmation is optional and subjective.

### Mechanizability
PARTIAL — VWAP calculation is deterministic, but the band multipliers are not stated. Once standard deviation multiples are defined, the entire signal is mechanical: detect price in the band range + detect zone. However, without the exact parameters, the strategy cannot be coded without assumptions.

---

## Strategy 3: Change of Character (CHoCH) Trading

### Indicators and settings
- Change of Character: defined as the first time a lower high or higher low is removed from a chart [22:00].
- No additional indicator parameters stated.

### Context / bias filter
Use CHoCH as a confluence factor only, not as the sole signal for market direction [22:30]. Primarily used on the 5-minute chart to confirm a directional bias established on the 30-minute chart. Most conservative when combined with a supply or demand zone retest [24:30-25:00].

### Entry trigger
Two entry methods provided:

**Risky approach:** Enter right after the CHoCh appears on the 5-minute chart [24:00-24:30]. This carries the risk that price may be sweeping the zone before continuing in the previous direction.

**Conservative approach:** Wait for price to retrace to another lower-timeframe supply or demand zone after the CHoCH has formed, then enter from that zone [24:30-25:00]. This requires both a CHoCH and a secondary zone retest.

### Stop loss
Conservative placement: slightly below the lower timeframe demand zone (for longs) or above the supply zone (for shorts) after the CHoCh. NOT STATED for risky entry approach.

### Take profit / exit
At the next major supply or demand zones in the market structure [NOT EXPLICITLY STATED for CHoCH in isolation, but implied to follow the multi-timeframe framework].

### Invalidation / skip conditions
- CHoCH signals can produce "quite a few false signals" if used without additional confluences [24:30].
- Do not rush to enter immediately after CHoCH; be patient and wait for active market hours [24:30].
- If momentum is very strong at the CHoCH, price may not retrace to a secondary zone, and entry opportunity may be missed entirely [28:00].
- CHoCH happened outside trading hours but very close to London session — skip trades outside main market hours [24:00-24:30].

### Claimed performance
NONE CLAIMED

### Vagueness log
1. UNDEFINED-RULE: "Lower high" and "higher low" — no specific price range, candle count, or lookback period to identify which swing is the reference.
2. UNDEFINED-RULE: "Shift in order flow" — no objective measure of what constitutes a true shift vs. a false break.
3. SUBJECTIVE: "Confluence factor" — CHoCH alone is flagged as unreliable; only in combination with other signals is it valid.
4. SUBJECTIVE: Decision to use risky vs. conservative entry — no rules for when to choose which.
5. VISUAL-ONLY: "Liquidity run" — price sweeping the zone before continuing in original direction is mentioned but not formally defined [27:00].

### Mechanizability
PARTIAL — Identifying a break of the prior lower high or higher low is mechanical (compare swing high/low prices), but determining "which" swing is the target and filtering false signals requires the additional confluence factors (demand zone, session timing, volume). The CHoCH alone is not tradeable without invention; the strategy skeleton is computable, but the entry signal filtering requires manual parameter definition or additional rules.

---

## Notable claims and caveats
The speaker emphasizes that "even if you see a very strong imbalance, the market doesn't always react at the supply or demand zone as you would expect" [05:30-06:00]. This acknowledges that setups can fail. The speaker cautions against relying on CHoCH signals alone, noting they "can produce quite a few false signals" [24:30]. 

The speaker advises trading only during London and New York sessions to ensure liquidity and volatility [07:00-07:30]. Outside main market hours, trades should be avoided [12:30-13:00]. The speaker demonstrates examples across multiple markets (Yen Futures, British Pound Futures, EUR Futures, Aussie Dollar Futures) but provides no aggregate performance metrics, win rates, or risk-to-reward ratios.

No mention is made of transaction costs, spread, slippage, or commission in any of the examples.
