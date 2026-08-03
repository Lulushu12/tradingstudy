# How I Use AI For Trading To Build Tradingview Indicators (Zero Money Spent)

- video_id: dYb7o9YFHss
- url: https://www.youtube.com/watch?v=dYb7o9YFHss
- duration: 25:05
- classification: TOOLING

## Summary

This video teaches how to use AI (specifically language models) to generate custom TradingView indicators in Pine Script without coding knowledge. The speaker demonstrates five specific indicator concepts that can be automated: momentum candle detection, three-line strike pattern recognition, hourly opening range breakouts, pin bar scanning, and gap fill detection. The focus is on the process of translating trading ideas into prompt-based indicator code generation.

## Instruments and timeframes stated

- markets: Mentioned as general (crypto, stocks implied through examples)
- timeframes: 5-minute (for opening range), 1-minute implied for scalping; no comprehensive specification
- sessions/hours: Asian sessions, London, New York sessions mentioned in examples; NOT STATED as requirements

## Process Framework

The speaker outlines a three-step framework for converting trading ideas into AI-generated indicators [21:00-24:00]:

1. **Capture core observation**: Identify specific market behavior that creates an edge, with concrete conditions [21:30]
2. **Define entry and exit criteria**: Specify trigger, confirmation, and invalidation conditions [22:00]
3. **Specify visual requirements**: Arrows, colored bars, background highlights, text labels [22:30]

Workflow [24:00-24:30]:
1. Crystallize idea without coding terms
2. Structure specific prompt with inputs, conditions, and outputs
3. Feed to AI model (e.g., ChatGPT, Claude)
4. Paste generated code into TradingView Pine editor
5. Visually verify indicator works
6. Refine by requesting modifications

## Indicator Concept 1: Momentum Candle Detector

### Logic and settings

- Calculation: Compare current bar spread (high minus low) to average spread of last 10 bars [01:00]
- Signal: Bar spread >= 1.5x the average spread [01:00]
- Inputs: Look-back length (adjustable), multiplier (adjustable, default 1.5) [02:00]

### Entry concept

Trade momentum candles at key support or resistance levels [02:30]. Adapt to strategy: for breakout traders, use at levels; for reversal traders, watch for exhaustion. Best performance when candle appears at key level with rejection wicks or continuation patterns [03:00].

### Performance claim

"Roughly 60% of momentum candles led to continued movement in direction" [03:30]

### Vagueness log

1. "Key support and resistance levels" - UNDEFINED-RULE: not specified how to identify these
2. "Rejection wicks or continuation patterns" - SUBJECTIVE: not quantified
3. "Breakout continuations" - UNDEFINED-RULE: how far into the move to enter

### Mechanizability

FULL - The indicator logic (spread calculation and comparison) is entirely mechanical and computable from OHLCV data.

## Indicator Concept 2: Three Line Strike Pattern Recognition

### Logic and settings

- Pattern: Three consecutive same-color candles in one direction, followed by a fourth candle that completely engulfs all three prior bars [04:30]
- Bullish strike: Three bearish candles followed by massive bullish engulfing bar
- Bearish strike: Three bullish candles followed by massive bearish engulfing bar
- Optional enhancement: Volume confirmation - fourth candle volume > 20-period average volume [06:00]

### Entry concept

Entry on breakout in the direction of reversal (after the pattern completes). Can also trade continuation if the box is broken to the upside [06:30]. Best at support/resistance levels [07:00].

### Performance claim

"Not every strike leads to full reversal, but most provide profitable scalps" [06:30]

### Vagueness log

1. "Completely engulfing" - UNDEFINED-PARAM: does this allow equality at open/close or require strict containment?
2. "Most provide profitable scalps" - UNDEFINED-PARAM: no definition of "most" or profit target
3. Continuation trade logic - UNDEFINED-RULE: no specific entry for continuation direction

### Mechanizability

FULL - Engulfing detection and candle color tracking is entirely mechanical.

## Indicator Concept 3: Hourly Opening Range Breakout

### Logic and settings

- First 5-minute bar of each hour establishes the range (high and low) [08:00]
- Range boundaries extend until the next hour begins [09:00]
- Signal: Price closes outside the box before the next hour begins [08:30]

### Entry concept

Entry on close outside the range (not just a wick touch) [09:30]. Stop inside the box, usually at midpoint [10:00]. Target = 1.5x the box height [10:00].

### Performance claim

NONE CLAIMED, but speaker notes: "During quiet Asian sessions, price often chops around the range without clear direction" [10:30], implying poor performance during those hours.

### Enhancement mentioned

Volume confirmation: Only signal breaks where volume exceeds a threshold [10:30]

### Vagueness log

1. "Close outside the range" - UNDEFINED-PARAM: by how many points or pips?
2. "Stop inside box at midpoint" - UNDEFINED-RULE: the exact calculation for midpoint
3. "1.5x box height" - Specified but NOT STATED which direction if there's a large gap

### Mechanizability

FULL - Range establishment and close detection are entirely mechanical.

## Indicator Concept 4: Pin Bar Scanner

### Logic and settings

- Bullish pin bar: Long lower wick and tiny body near top [12:30]
- Bearish pin bar: Long upper wick and small body near bottom [12:30]
- True pin bar threshold: Wick must be at least 3x the body size [12:00]
- OR wick >= 50% of total candle range (default) [13:00]
- Comparison filter: Current wick must be significantly larger than recent wicks (default 1.5x larger) [13:30]
- Minimum size filter: Candle must be minimum size relative to ATR [13:30]

### Entry concept

Enter in the direction of the pin bar reversal. Bullish pin at support = buy signal. Bearish pin at resistance = short signal [14:30]. Best performance when location, volume, and context align [15:30].

### Performance claim

"Not every pin starts a new trend. But most produce profitable bounces" [15:00]

### Vagueness log

1. "Tiny body" - SUBJECTIVE: when does body stop being "tiny"?
2. "50% of total candle range" - UNDEFINED-PARAM: does this include shadows or just high-to-low?
3. "Support/resistance levels, moving averages, round numbers" - UNDEFINED-RULE: how to identify these objectively
4. "Volume and context align" - SUBJECTIVE: no mechanical definition

### Mechanizability

PARTIAL - Wick and body measurement is mechanical, but the identification of support/resistance and the determination of "significance" based on location involves subjective judgment.

## Indicator Concept 5: Gap Fill Detector

### Logic and settings

- Gap up: Today opens above yesterday's high [16:30]
- Gap down: Today opens below yesterday's low [16:30]
- Indicator displays shaded box between open and prior extreme [17:30]
- Box disappears when price trades into the gap area (fill) [17:30]

### Entry concept

Enter to fade (in the direction of gap fill) when gaps appear. Buy gap downs near support. Short gap ups near resistance [18:00]. Stop beyond gap extreme. Target at fill completion [18:30].

### Performance claim

"Some say 70% of gaps fill eventually" [16:30]. "Morning gaps frequently fill before lunch, especially in high-volume stocks" [18:00]

### Enhancement mentioned

50% fill line and alert [18:30]. Also "gap and go" setups: if price holds above/below gap after 60 minutes, trade continuation instead [19:30].

### Vagueness log

1. "Near support" - UNDEFINED-RULE: how close to support, and which support level if multiple exist?
2. "Fill completion" - UNDEFINED-PARAM: does this mean touching it, or closing inside it?
3. "70% of gaps fill" - Vague statistic; no timeframe or market specification

### Mechanizability

FULL - Gap detection (comparing opens and prior day extremes) is entirely mechanical.

## General framework insights

The speaker emphasizes [23:00-24:00]:
- Test first version, find weaknesses, request improvements
- Refine by changing line thickness, adding labels, including multiple timeframes
- Backtest across different market conditions: trending, range-bound, high volatility, low volume
- Complex indicators often fail; best indicators solve one specific problem well
- Focus on single, observable market behaviors

## Notable claims

- "Trading with AI lets you merge these concepts effortlessly" [20:00]
- "Every profitable trading strategy started as a simple observation about market behavior" [20:00]
- "You don't need to think like a programmer. You just need to think like a trader who can explain their edge" [21:00]
- AI indicator consistency: "Your indicator never misses an hour, never forgets to draw the lines, and never gets distracted by other chart patterns" [10:30]

## Caveats

- Speaker "wasted months using terrible pin bar indicators" that marked every candle [12:00]
- Fake breaks exist: "Many traders exit half at 50% fill, keeping half for complete fill" emphasizes that not all gap fills complete immediately [18:30]
- Context matters: "A pin bar in empty space means little" [14:30]
- Market condition dependency: Asian session choppy behavior vs. London/New York activity [10:30]
- The speaker does NOT discuss spread, slippage, or commissions
- Position sizing is NOT addressed
