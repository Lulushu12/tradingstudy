# This AI-Built RSI+VWAP Indicator Quietly Prints Profits (Claude Strategy)

- video_id: H1x_XUEL2aY
- url: https://www.youtube.com/watch?v=H1x_XUEL2aY
- duration: 12:35
- classification: STRATEGY

## Summary
A trading system built using Claude AI that combines RSI and VWAP into a three-color indicator: green for bullish agreement, red for bearish agreement, and white for disagreement (hold zone). The strategy trades only when both indicators agree and price is at a key support/resistance level. The trader emphasizes that signal quality matters less than location quality, and implements strict filters: minimum 30-minute timeframe, trending markets only, no entries in hold zones, and retest confirmation on breakouts. Win rate claimed at roughly 60% in trending conditions.

## Instruments and timeframes stated
- Markets: Forex (Pound Yen, Euro Yen, Euro Dollar), stocks (Nasdaq), crypto (Bitcoin), commodities (Gold) [09:30], [10:30]
- Timeframes: minimum 30-minute chart [09:00]; examples use 4-hour [00:00], 30-minute [10:30]
- Sessions/hours: NOT STATED

## Strategy 1: RSI+VWAP Agreement Trading with Location Filter

### Indicators and settings
- Indicator: Custom AI-built RSI+VWAP indicator
- Components:
  - VWAP: standard Volume Weighted Average Price [02:30]
  - RSI: 21 relative strength period [10:30]; midline at 50 [02:30]
  - Signals: three colors based on indicator agreement
    - Green: VWAP and RSI both agree bullish [01:00]
    - Red: VWAP and RSI both agree bearish [01:00]
    - White: VWAP and RSI conflict (hold zone) [01:00], [04:00]
- Source: speaker mentions using "open instead of close" for signal timing [10:30]
- Code provided in description (Pine Script for TradingView) [02:00]

### Context / bias filter
Only trade in trending markets with clear directional bias [09:30]. Skip ranging markets where "candle colors are flipping every few bars" [10:00]. White candles indicate "hold zones" where momentum is split; these are "minefields" [03:30] to avoid [04:30].

**Critical filter: Location** [05:00], [06:00]:
- Green candles only qualify when price is near a support level with "real significance" [05:30]
  - A previous swing low
  - A zone where buyers stepped in hard before
  - A level that previously was resistance and flipped to support
- Red candles only qualify at resistance [06:00]
  - A level the market has already rejected
  - A weekly high
  - A zone with clear selling pressure above it
- Without a key level underneath, skip the signal regardless of color [06:00]

### Entry trigger
**Bullish entries (Green candles):**
1. Green candles appear at support level [05:00]
2. RSI above 50 [05:00]
3. Price above VWAP [05:00]
4. Signal fires only after market is committed: "consecutive candles hold the same color for a real stretch" [10:00]
5. For breakout above resistance: wait for retest below the level before entering; enter on close if price holds above VWAP on retest and RSI stays above 50 [11:00], [11:30]

**Bearish entries (Red candles):**
1. Red candles appear at resistance level [06:00]
2. RSI below 50 (implied by analogy to bullish entry)
3. Price below VWAP (implied)
4. Example shows white-to-red transition at resistance as highest quality setup [07:30]; wait for hold phase to resolve before entering [08:00]
5. For breakout below support: analogous retest required (not explicitly stated but follows pattern)

**Zone definition:** Don't enter during white (hold) candles; wait for market to choose direction and agreement to return [08:00]

### Stop loss
"Place my stop just above resistance" for shorts [00:30]. "Stop above the level" for short at resistance [07:30]. "Stop below the retest low" for longs after breakout retest [11:30]. Implied: stop placed just outside the key level being used as reference point.

### Take profit / exit
"Target sits at the next support below, roughly two and a half times my risk" [00:30]. Implied risk-reward ratio of 1:2.5. Exit at next significant support or resistance in the direction of trade.

### Invalidation / skip conditions
1. White candles (hold zones) - do not enter, close chart until agreement returns [04:30]
2. Signals without key level support - skip regardless of color quality [06:00]
3. Ranging markets - close chart and wait for trending conditions [10:00]
4. Timeframe conflicts - if lower timeframe shows agreement but higher timeframe (30-min or above) shows hold/disagreement, invalidate signal [09:00]
5. No entries on first breakout of resistance; must see retest and confirmation [11:00]

### Claimed performance
"Roughly 60% win rate" across 200 signals in trending conditions on Euro Dollar, Bitcoin, and Nasdaq [09:30]. Notes that "trending markets are where this system earns" [09:30]. In ranging markets, the system "shreds it" [10:00]. Claims early losses were from "agreement signal, but no obvious level" which were all "avoidable" [06:30].

### Vagueness log
1. UNDEFINED-PARAM: "Real significance" of support/resistance levels [05:30] - depends on trader interpretation
2. UNDEFINED-RULE: What determines "a zone where buyers stepped in hard before"? [05:30] - visual/subjective
3. UNDEFINED-RULE: "Consecutive candles hold the same color for a real stretch" - how many candles minimum? [10:00]
4. UNDEFINED-RULE: "The entire market is watching" [12:00] - how is this determined?
5. SUBJECTIVE: Identifying levels that "actually hold" versus "random wick from last Tuesday" [12:00]
6. UNDEFINED-PARAM: RSI settings for different timeframes beyond the 21-period mentioned for 30-minute [10:30]
7. UNDEFINED-RULE: Exact profit target calculation - "next support below" distance not specified; only ratio of 2.5R mentioned [00:30]

### Mechanizability
PARTIAL — The RSI+VWAP agreement detection is fully computable from OHLCV data. However, the critical location filter requires identifying "key levels" which depends on subjective interpretation of prior swings, zones where "buyers stepped in", and zones "the entire market is watching." Without mechanical definition of these levels, strategy requires discretionary judgment for entry point determination, even if the indicator signals are clean.

## Notable claims and caveats
Speaker emphasizes that agreement signals alone "nearly cost me more than disagreement did" [04:30] and reveals the major breakthrough was the location filter, not the indicator itself [06:30]. States "the wins weren't better signals. They were better locations" [06:30]. Notes: "Every one of those trades happened inside what I now call a hold zone" [03:30] for losses. 

Explicitly warns against time-frame confusion: "One of my worst losses came from a 5-minute chart that looked flawless... $1,100 gone" [08:30], which led to rule of "no signals below the 30-minute chart" [09:00]. 

Strategy breaks down in ranging/choppy markets [10:00]. In the 60% win rate study, 200 signals were reviewed in "trending conditions" [09:30], but win rate in ranging markets is not specified.

Never mentions transaction costs, slippage, or commission. No discussion of drawdown or losing streaks beyond the retrospective analysis of past losses. Recommends location analysis training inside "academy" [12:30].
