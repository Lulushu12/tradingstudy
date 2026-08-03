# Private EMA Heikin Ashi Scalping | How To Scalp Forex & Stocks Using HI-LO Trading Strategy

- video_id: 48gxeTt-Sdw
- url: https://www.youtube.com/watch?v=48gxeTt-Sdw
- duration: 13:28
- classification: STRATEGY

## Summary
A scalping strategy that combines a Moving Average High-Low Channel (upper and lower moving averages plotted on bar highs and lows) with Heikin Ashi candlesticks to reduce false breakout signals when trading moving averages. The channel acts as a dynamic support/resistance zone, and trades are entered only on clear breakouts above or below the channel when Heikin Ashi color aligns with the channel direction. Optional filters include ADX for trend strength confirmation and divergence signals for entry timing. The strategy avoids ranging markets and consolidation periods.

## Instruments and timeframes stated
- Markets: Forex and stocks [01:30]; volatile markets recommended [13:00]
- Timeframes: 1-minute to 15-minute charts for scalping/day trading [13:00]
- Sessions/hours: NOT STATED

## Strategy 1: Moving Average High-Low Channel with Heikin Ashi Breakout Trading

### Indicators and settings
- Indicator 1: Moving Average High-Low Channel
  - Two moving averages: one applied to bar high prices, one to bar low prices [01:00]
  - Period: 50 bars (can experiment with different lookback periods) [04:00]
  - Color coding: Green when sloping upward [04:30], Red when sloping downward [04:30], Gray when flat [04:30]
  - Creates a zone of support and resistance instead of a single line [01:30]

- Indicator 2: Heikin Ashi candlesticks [02:00]
  - Candlestick colors: Green for bullish candles, Red for bearish candles
  - Strong trends show minimal upper wicks in uptrends and minimal lower wicks in downtrends [03:30]
  - Consistency of color indicates direction more clearly than traditional candles [02:30]

- Optional Filter 1: ADX (Average Directional Index) [08:00]
  - Values 0-100 [08:00]
  - Non-directional; measures trend strength [08:00]
  - Speaker ignores all signals if ADX below 20 [08:30]
  - ADX above 20 indicates trend strong enough for trend trading [08:30]
  - Low ADX (below 20) for 20-30+ bars indicates accumulation/distribution; price ranges [08:30]

- Optional Filter 2: Divergence (MACD histogram) [10:30]
  - Regular bullish divergence: price makes lower low but indicator makes higher low [11:00]
  - Regular bearish divergence: price makes higher high but indicator makes lower high [11:00]

### Context / bias filter
Only trade when market is trending clearly [04:00]. Channel direction determines bias:
- Uptrend: channel slopes upward (green), price above channel, Heikin Ashi candles are green [05:00]
- Downtrend: channel slopes downward (red), price below channel, Heikin Ashi candles are red [05:00]

Market is "slowing down and might be reversing or retracing" when price structure opposes channel direction [04:30].

**Avoid trading when:**
1. Price is inside the channel ("no man's land") [06:00]
2. Channel slope changes from up to down to flat in very short period [06:30]
3. Price breaks channel in both directions (consolidation) [06:30]
4. Sideways market with little gap between price and moving average channel [06:30]
5. ADX below 20 (if using ADX filter) [08:30]
6. In accumulation/distribution phase (ADX below 20 for 20-30+ bars) [08:30]

### Entry trigger
**Long entry (Bullish breakout):**
1. Price breaks above the moving average channel [07:00]
2. With green Heikin Ashi candles [07:00]
3. Channel is green (sloping upward) [07:00]
4. ADX above 20 if using ADX filter [08:30]
5. In a healthy bull trend, price stays a fair distance above channel, not just at the edge [06:30]

**Short entry (Bearish breakout):**
1. Price breaks below the moving average channel [07:00]
2. With red Heikin Ashi candles [07:00]
3. Channel is red (sloping downward) [07:00]
4. ADX above 20 if using ADX filter [08:30]

**Divergence confirmation (optional):**
- Regular bullish divergence: add to long entries to anticipate upward move [11:00]
- Regular bearish divergence: add to short entries to anticipate downward move [11:00]

### Stop loss
NOT STATED

### Take profit / exit
NOT STATED

### Invalidation / skip conditions
1. Price inside channel - avoid positions [06:00]
2. Channel slope changing rapidly - no clear trend [06:30]
3. Price breaking channel in both directions (ranging) [06:30]
4. ADX below 20 indicates low probability setups [08:30]
5. In ranging market with sideways price action and minimal channel-price distance [06:30]
6. When ADX has been below 20 for 20-30+ bars (accumulation/distribution phase) [08:30]

### Claimed performance
"A breakout above the moving average channel with green high kanashii candles signals buying pressure" [07:00]. "A breakout below the moving average channel with red high kanashii candle signals selling pressure" [07:00]. Claims strategy "will filter a lot of all signals and will save you a lot of losing trades and lost money" [01:30]. States divergence formations "are leading signals" that "occur before the actual move" [11:00].

### Vagueness log
1. UNDEFINED-PARAM: "Different lookback periods" [04:00] - no guidance on how to select optimal period
2. UNDEFINED-RULE: "Fast moving averages" vs "slow moving averages" - no specific definition [06:00]
3. UNDEFINED-RULE: "Price stays a fair distance above the moving average channel" [06:30] - what distance qualifies as "fair"?
4. UNDEFINED-RULE: "Very short period of time" for channel slope change [06:30] - how many bars?
5. UNDEFINED-RULE: "Clear breakout" - how many pips or percentage beyond channel?
6. UNDEFINED-RULE: "High number of moves" for market selection [13:00] - volatility threshold not specified
7. UNDEFINED-PARAM: "Any time frame between one minute and 15 minutes" [13:00] - no specific recommendation on which to use
8. UNDEFINED-RULE: Stop loss NOT STATED
9. UNDEFINED-RULE: Take profit levels NOT STATED
10. UNDEFINED-RULE: Divergence confluence with channel - when divergence conflicts with channel signal, which takes priority?

### Mechanizability
PARTIAL — The high-low channel construction is fully mechanical from OHLCV data. Heikin Ashi color is computable. ADX calculation is standard. However, several key rules lack precision: "fair distance" between price and channel, "clear breakout" definition, "very short period" for slope changes, and no specified stop loss or take profit levels. Divergence integration is optional but not precisely defined in relation to primary signal.

## Notable claims and caveats
Speaker emphasizes problem of "false breakouts or whipsaws" with traditional moving average strategies [00:00], and claims the high-low channel and Heikin Ashi combination "will filter a lot of all signals and will save you a lot of losing trades" [01:30]. Notes that "nice and clean trends don't always happen" and "ranging markets come" causing losses [00:30]. Emphasizes that "you must analyze it together with price action" [02:00] and specific attention to "slope of the channel, distance between the candles and the channel" [07:00]. Recommends market selection should be volatile markets [13:00]. Never mentions transaction costs, slippage, or commission. No discussion of drawdown or losing streak risks. Strategy explicitly avoids consolidation periods, making it inapplicable in ranging markets.
