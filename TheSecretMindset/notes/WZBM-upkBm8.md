# Ichimoku Day Trading Strategy | Cloud Trading Explained (For Beginners)

- video_id: WZBM-upkBm8
- url: https://www.youtube.com/watch?v=WZBM-upkBm8
- duration: 08:32
- classification: MULTI-STRATEGY

## Summary

This video is an educational overview of the Ichimoku indicator and presents four trading techniques using its components. Ichimoku is described as a trend-following system that predicts price movement and provides unique dynamic support/resistance levels through the Kumo cloud. The four trading techniques are: (1) Base/Conversion line crossover with Lagging Span filter, (2) Base/Conversion line crossover with Kumo cloud filter, (3) Kumo cloud breakouts, and (4) Ichimoku cloud span line crossovers. No specific stop loss or take profit rules are defined for any technique.

## Instruments and timeframes stated

- markets: NOT STATED (general applicability implied)
- timeframes: NOT STATED
- sessions/hours: NOT STATED

## Ichimoku Indicator Components

### 1. Conversion Line (Tenkan-sen)

- **Purpose**: Short-term line, also known as turning line [00:30]
- **Use**: Signals minor support or resistance [00:30]. Follow if focusing on short-term or scalping [00:30]
- **Interpretation**:
  - Price above conversion line = short-term upward momentum [02:00]
  - Price below conversion line = short-term downward momentum [02:00]
  - Increasing conversion line = upward trend [02:00]
  - Decreasing conversion line = downward trend [02:00]

### 2. Base Line (Kijun-sen)

- **Purpose**: Confirmation line, medium-term support/resistance [01:00]
- **Use**: Medium-term trading signal; some traders use as trailing stop level [01:00]
- **Interpretation**:
  - Price above base line = medium-term upward momentum [02:30]
  - Price below base line = medium-term downward momentum [02:30]
  - Increasing base line = upward trend [02:30]
  - Decreasing base line = downward trend [02:30]

### 3. Lagging Span (Chikou Span)

- **Purpose**: Confirmation line for signals [01:00]; shows big-picture trend [03:00]
- **Interpretation**:
  - Lagging span above current price = current prices higher than previously, bullish bias [03:00-03:30]
  - Lagging span below current price = current prices lower than previously, bearish bias [03:00-03:30]
  - Lagging span near current price = trading range [03:30]

### 4. Kumo Cloud (Senkou Span A and B)

- **Calculation**: Formed from 2 lines (Span A and Span B) [01:30-02:00]
- **Purpose**: Major areas of dynamic support and resistance [01:30-02:00]
- **Characteristics**:
  - Longer price stays above/below cloud, stronger trend [03:30]
  - Wide cloud = strong expected support/resistance [04:00]
  - Thin cloud = weak expected support/resistance [04:00]
  - Span lines projected forward by 26 periods [07:00]
- **Key Rule**: "You should never trade inside the Kumo cloud, very important rule" [04:00]

---

## Strategy 1: Base Line - Conversion Line Crossover (with Lagging Span Filter)

### Indicators and settings

- Base Line (Kijun-sen): period = NOT STATED (standard Ichimoku periods assumed)
- Conversion Line (Tenkan-sen): period = NOT STATED
- Lagging Span (Chikou Span): NOT STATED

### Entry trigger

**Buy Signal**:
1. Base line crosses above Conversion line [04:30]
2. Lagging span indicates bullish bias (above current price) [05:00]

**Sell Signal**:
1. Base line crosses below Conversion line [04:30]
2. Lagging span indicates bearish bias (below current price) [05:00]

### Stop loss

NOT STATED

### Take profit / exit

NOT STATED

### Vagueness log

1. UNDEFINED-PARAM: Base line and Conversion line periods not stated
2. UNDEFINED-RULE: "Bullish bias" - how to confirm lagging span indicates this without detailed look-back window
3. UNDEFINED-PARAM: Stop loss placement not stated
4. UNDEFINED-PARAM: Take profit target not stated

### Mechanizability

PARTIAL. Line crossovers are mechanically computable. However, Lagging Span interpretation requires subjective judgment. Stop loss and take profit are missing.

---

## Strategy 2: Base Line - Conversion Line Crossover with Kumo Cloud Filter

### Entry trigger

**Strong Buy**: Base line crosses above Conversion line, AND price is above Kumo cloud [05:30]

**Weak Buy**: Base line crosses above Conversion line, AND price is below Kumo cloud [05:30]

**Strong Sell**: Base line crosses below Conversion line, AND price is below Kumo cloud [05:30-06:00]

**Weak Sell**: Base line crosses below Conversion line, AND price is above Kumo cloud [06:00]

### Context / bias filter

Use Kumo cloud position (above/below price) to filter signal strength. Stronger signals occur when crossover and cloud position align with trend direction [05:30-06:00].

### Stop loss

NOT STATED

### Take profit / exit

NOT STATED

### Vagueness log

1. UNDEFINED-RULE: Cloud thickness not specified for trade decisions (weak vs. strong already implies thickness consideration [04:00], but no exact rule)
2. UNDEFINED-PARAM: Stop loss and take profit not stated

### Mechanizability

PARTIAL. Crossovers and cloud position are mechanical. However, no stop loss or take profit rules defined.

---

## Strategy 3: Kumo Cloud Breakout

### Entry trigger

**Bullish Signal**: Price enters Kumo cloud and breaks the upper wall upward [06:00-06:30]

**Bearish Signal**: Price enters Kumo cloud and breaks the lower wall downward [06:30]

### Stop loss

NOT STATED

### Take profit / exit

NOT STATED

### Vagueness log

1. UNDEFINED-RULE: "Breaks upward" - by how much (1 pip, 10 pips, candle close above upper wall)
2. UNDEFINED-RULE: Confirmation requirement - does price need to close above/below wall or just touch it
3. UNDEFINED-PARAM: Stop loss and take profit not stated

### Mechanizability

PARTIAL. Cloud position is mechanical. However, breakout confirmation criteria (how much, what timeframe) not specified. Stop loss and take profit missing.

---

## Strategy 4: Ichimoku Cloud Span Line Crossover

### Entry trigger

Note: Span lines are projected forward 26 periods [07:00].

**Strong Buy**: Span A crosses Span B from below to above, AND price is above Kumo cloud [07:00]

**Strong Sell**: Span A crosses Span B from above to below, AND price is below Kumo cloud [07:00]

**Weak Buy**: Span A crosses Span B from below to above, AND price is below Kumo cloud [07:00-07:30]

**Weak Sell**: Span A crosses Span B from above to below, AND price is above Kumo cloud [07:30]

### Stop loss

NOT STATED

### Take profit / exit

NOT STATED

### Vagueness log

1. UNDEFINED-PARAM: Cloud span periods not stated; standard assumed
2. UNDEFINED-PARAM: Stop loss and take profit not stated
3. UNDEFINED-RULE: Entry timing - when exactly to enter after Span A/B crossover

### Mechanizability

PARTIAL. Span line crossovers are mechanical. However, stop loss and take profit are entirely missing.

---

## General Rules and Caveats

**Key Rule**: "You should never trade inside the Kumo cloud" [04:00]. This is a critical invalidation criterion across all strategies.

**Cloud Thickness Interpretation**:
- Wide cloud: strong support/resistance expected [03:30-04:00]
- Thin cloud: weak support/resistance expected [04:00]

**Trend Requirement**: "Just be careful and use it in trending conditions, because during non-trending markets it will offer a lot of false signals" [08:00-08:30]. This is the only performance caveat provided.

---

## Notable claims and caveats

The speaker emphasizes that Ichimoku "predicts price movement and not only measures it" [00:00-00:30], differentiating it from other indicators. However, he immediately warns that "during non-trending markets it will offer a lot of false signals" [08:00-08:30].

He notes that while Ichimoku "might seem complicated," once you learn to interpret it, you'll "spot great trading signals" [00:30]. This suggests a learning curve and subjective interpretation component.

The speaker describes Ichimoku as "excellent at offering dynamic support and resistance levels" and "good at measuring the direction and intensity of the current market trend" [07:30-08:00]. However, these claims lack supporting statistical evidence.

No specific win rate, R-multiple, or profit targets provided across any of the four techniques. No mention of spread, slippage, or commission. No discussion of drawdown or losing streaks. All four techniques have identical gaps: missing stop loss and take profit rules.
