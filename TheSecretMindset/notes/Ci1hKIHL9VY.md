# Heiken Ashi CHEAT Strategies For Scalping & Day Trading (Forex, Stocks & Crypto)

- video_id: Ci1hKIHL9VY
- url: https://www.youtube.com/watch?v=Ci1hKIHL9VY
- duration: 10:10
- classification: MULTI-STRATEGY

## Summary

This video teaches Heiken Ashi candlesticks as an objective, quantifiable alternative to traditional Japanese candlesticks. It presents three trading strategies using Heiken Ashi: multi-timeframe color changes, Heiken Ashi with RSI confirmation, and Heiken Ashi with Ichimoku Cloud. The speaker emphasizes that Heiken Ashi filters noise and makes trends, reversals, and consolidations clearer than traditional candles.

## Instruments and timeframes stated

- markets: Forex, stocks, crypto [00:00]
- timeframes: Multiple timeframes for multi-timeframe strategy [04:00-04:30]; not specified for other strategies
- sessions/hours: NOT STATED

## Strategy 1: Multi-Timeframe Heiken Ashi Color Change

### Indicators and settings

- Heiken Ashi candlesticks (modified price representation using Heikin-Ashi calculation)
- No other indicators

### Context / bias filter

Use two consecutive timeframes (e.g., 1-hour and 4-hour, or daily and weekly) [04:30]. Ideally, three timeframes align in the same direction for maximum edge [04:00]. The video recommends two consecutive timeframes as a compromise if three are not available [04:30].

### Entry trigger

Buy: when the current candle color changes from red to green in both consecutive timeframes [04:30]. Sell: when the current candle color changes from green to red in both consecutive timeframes [04:30].

### Stop loss

NOT STATED

### Take profit / exit

NOT STATED

### Invalidation / skip conditions

Do not trade if the two timeframes show conflicting signals (one red-to-green, one green-to-red). Wait for alignment.

### Claimed performance

No specific performance claims, win rate, or profit targets provided.

### Vagueness log

1. UNDEFINED-PARAM: No specific timeframe pairs recommended; which two consecutive timeframes to use
2. UNDEFINED-PARAM: Stop loss and take profit not stated
3. UNDEFINED-RULE: Entry timing - does entry occur on the first bar of color change or after candle close

### Mechanizability

FULL. Heiken Ashi color is mechanically computable, and color changes are objectively detectable. The strategy logic is simple and mechanically implementable once timeframe selection is made.

---

## Strategy 2: Heiken Ashi with RSI Centerline Crossover

### Indicators and settings

- Heiken Ashi candlesticks
- RSI (Relative Strength Index): period = NOT STATED (standard is typically 14), centerline level = 50

### Context / bias filter

For uptrends: Heiken Ashi trend built primarily by bullish (green) candles with no or minimal lower shadows, AND RSI above 50 [06:30-07:00]. For downtrends: Heiken Ashi trend built primarily by bearish (red) candles with no or minimal upper shadows, AND RSI below 50 [07:00].

### Entry trigger

Buy: when current Heiken Ashi candle color changes from red to green (indicating uptrend initiation) AND RSI is above 50 (indicating rising trend strength) [06:00]. Sell: when current Heiken Ashi candle color changes from green to red AND RSI is below 50 [06:00-06:30].

### Stop loss

NOT STATED

### Take profit / exit

NOT STATED

### Invalidation / skip conditions

Do not enter if Heiken Ashi color changes but RSI does not confirm (e.g., color change to green but RSI below 50). Do not trade during consolidation (indicated by small Heiken Ashi bodies with both upper and lower shadows) [02:30].

### Claimed performance

The speaker shows chart examples of uptrends and downtrends using this approach [07:30] but provides no specific performance statistics or win rate.

### Vagueness log

1. UNDEFINED-PARAM: RSI period not stated
2. UNDEFINED-RULE: "Minimal" lower/upper shadows - no specific definition of how much shadow length is acceptable; is 5% of body height acceptable, 10%?
3. UNDEFINED-RULE: "Primarily by bullish candles" - no specific percentage or number of green candles required in a row
4. UNDEFINED-PARAM: Stop loss and take profit not stated

### Mechanizability

PARTIAL. Heiken Ashi color change and RSI level are mechanically computable, but the context rules ("primarily by bullish candles," "minimal shadows") require assumptions and subjective thresholds not specified by the speaker.

---

## Strategy 3: Heiken Ashi with Ichimoku Cloud

### Indicators and settings

- Heiken Ashi candlesticks
- Ichimoku Cloud indicator, specifically the Kumo (cloud) component
- Kumo color interpretation: green cloud = bullish, red cloud = bearish [08:30]

### Context / bias filter

For uptrends: Heiken Ashi trend built primarily by bullish candles with no or minimal lower shadows, AND price is above the Kumo cloud [09:00]. For downtrends: Heiken Ashi trend built primarily by bearish candles with no or minimal upper shadows, AND price is below the Kumo cloud [09:00-09:30]. Thicker Kumo indicates stronger support/resistance [08:00]. Longer price duration above or below Kumo indicates stronger trend [08:00-08:30].

### Entry trigger

Buy: when current Heiken Ashi candle color changes from red to green, Kumo cloud is green, and price is above the cloud [08:30]. Sell: when current Heiken Ashi candle color changes from green to red, Kumo cloud is red, and price is below the cloud [08:30].

### Stop loss

NOT STATED

### Take profit / exit

NOT STATED

### Invalidation / skip conditions

Do not trade if price is not aligned with Kumo position (e.g., Heiken Ashi signals green but price is below red cloud). Do not trade during consolidation (small Heiken Ashi bodies).

### Claimed performance

The speaker shows chart examples [09:30] but provides no specific performance statistics.

### Vagueness log

1. UNDEFINED-RULE: "Primarily by bullish candles" - no specific percentage or count of consecutive green candles required
2. UNDEFINED-RULE: "Minimal" lower/upper shadows - no specific threshold for shadow length relative to body size
3. UNDEFINED-PARAM: Ichimoku Cloud parameter settings (Tenkan, Kijun, Senkou Span B periods) not stated; defaults assumed
4. UNDEFINED-PARAM: Stop loss and take profit not stated

### Mechanizability

PARTIAL. Heiken Ashi color and Ichimoku Cloud position are mechanically computable, but context rules ("primarily by bullish candles," "minimal shadows") require subjective thresholds.

---

## Heiken Ashi Rules (Educational Reference)

The speaker presents five core rules for interpreting Heiken Ashi candlesticks [03:00-03:30]:

1. Sequence of green bodies = uptrend; sequence of red bodies = downtrend
2. Stronger trend: longer bodies with no opposite-direction shadows (no lower shadows on green, no upper shadows on red)
3. Weaker trend: smaller bodies, possibly with both upper and lower shadows
4. Consolidation: small bodies with both upper and lower shadows
5. Trend reversal: small body with long upper and lower shadows (doji-like) or sudden color change

---

## Notable claims and caveats

The speaker claims Heiken Ashi is more "objective, quantifiable" than traditional Japanese candlesticks [00:30-01:00], which are described as "subjective, artistic, and challenging" [00:30]. He emphasizes that Heiken Ashi "filters out price noise" making trends clearer [00:30-01:00]. He advocates for multiple timeframe analysis to improve odds of catching trends [04:00], stating that trend alignment across three timeframes offers "far bigger" winning odds than single-timeframe entry [04:00]. The speaker describes the strategies as "simple, and powerful" [07:00] and "simple, and effective" [09:30], but no drawdown, losing streak data, or risk warnings are provided. No mention of spread, slippage, or commission. All three strategies lack explicit stop loss and take profit rules, which the speaker acknowledges are areas for trader discretion in trade management [09:00].
