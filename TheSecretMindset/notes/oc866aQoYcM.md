# A Day Trading Strategy I Wish I Knew In My First Years (For Beginners)

- video_id: oc866aQoYcM
- url: https://www.youtube.com/watch?v=oc866aQoYcM
- duration: 15:11
- classification: STRATEGY

## Summary
A pin bar reversal trading strategy that trades pullbacks in the direction of established trends. Pin bars are candlesticks with wicks 2-3 times the body length, and they're only traded when they form at dynamic support/resistance levels (between two EMAs) with above-average volume. The strategy uses 50-period and 100-period EMAs to identify trend direction and creates confluence at value areas. Trades are entered only after pin bar formation is confirmed (high for longs, low for shorts is broken) with stops at pin bar extremes and take profits at next swing levels.

## Instruments and timeframes stated
- Markets: Forex (GBP/JPY, EUR/JPY), stocks (Amazon), crypto (Bitcoin) [07:00], [08:00], [08:30], [12:30]
- Timeframes: works on any timeframe; speaker prefers H4 and daily [06:30]; examples shown on hourly, M30, H4 [07:00], [08:00], [08:30]
- Sessions/hours: NOT STATED

## Strategy 1: Pin Bar Trading with EMA Confluence

### Indicators and settings
- Indicator 1: Exponential Moving Averages (EMAs)
  - 50-period EMA [02:00]
  - 100-period EMA [02:00]
  - Speaker prefers these but notes "choice is completely up to you. Just understand the concept and adapt it to your needs" [06:30]
  
- Indicator 2: Pin Bar (candlestick pattern)
  - Wick length: at least 2x, ideally 3x the length of the body [03:30]
  - Body position: at either upper or lower extreme of the pin bar [03:30]
  - Wick appearance: should stand out when compared to surrounding bars [03:30]
  - Duration: most impact within 4-5 bars/periods of formation [04:00]

### Context / bias filter
Only trade pin bars in clear trending markets, not in "heavy traffic or choppy, range bound markets" [04:30].

**Trend identification:**
- Uptrend: 50 EMA above 100 EMA [02:00]; look for long (buy) trades [08:30]
- Downtrend: 50 EMA below 100 EMA [02:30]; look for short (sell) trades [07:00]

**Value areas (confluence):** Pin bar must form between the two EMAs in the pullback area [03:00]. "The area between the 2 EMA is the 'sweet spot' for our entries" [03:00]. Pin bars "should only be traded when they form in areas of 'value' or 'interest'" [05:00]. Can use support/resistance levels, supply/demand areas, EMAs as dynamic levels [05:30].

### Entry trigger
**Setup requirement:** High volume pin bar forming in pullback to EMAs, showing rejection of the area [07:00], [09:00].

**Bullish entry (Long):**
1. Trend is up (50 EMA above 100 EMA) [02:00]
2. Price pulls back to the EMAs [08:30]
3. High volume pin bar forms rejecting this level [09:00]
4. Volume must be higher than previous 3-4 bars [03:00], [08:00]
5. Body positioned at lower extreme with upper wick [03:30]
6. Enter long when high of pin bar is broken [09:00], [10:00]

**Bearish entry (Short):**
1. Trend is down (50 EMA below 100 EMA) [02:30]
2. Price pulls back to the EMAs [07:00]
3. High volume pin bar forms rejecting this level [07:00]
4. Volume must be higher than previous 3 bars [03:00]
5. Body positioned at upper extreme with lower wick [03:30]
6. Enter short when low of pin bar is broken [07:00]

**Critical rule:** "In order to be a valid tradeable pattern, the pin bar must reject the area between the 2 EMAs. This is a key point in trading pin bars" [09:30].

### Stop loss
Place stop loss just beyond the pin bar extreme:
- For longs: below the low of the pin bar and below the relevant EMA [09:00]
- For shorts: above the high of the pin bar and above the relevant EMA [07:30]
- More precise example: when entering long at 100 EMA, "stop loss below the low of the pin bar, and below the 100 EMA" [11:00]

Money management adjustment: Once price moves in profit and consolidates above/below the relevant EMA, "move the stop loss to break even" to prevent profitable trades from becoming losing trades [12:00].

### Take profit / exit
Exit at next significant swing level in the direction of trade:
- For longs: next swing high [09:00]
- For shorts: next swing low [07:30]

Risk-to-reward ratio target: typically 2 to 3 [07:30], [09:30], [11:00], [11:30].

If next swing level doesn't provide positive risk-reward ratio, "estimate yourself a potential target" [09:30]. "Close to the most recent high" suggests using recent extremes as targets [10:00].

### Invalidation / skip conditions
1. Pin bar not in value area (between EMAs) - no trade [03:00]
2. Heavy traffic or choppy, range-bound markets - no trade [04:30]
3. Volume not higher than previous 3-4 bars - no trade [08:00]
4. Pin bar much larger than average trading range of preceding bars - becomes continuation pattern rather than reversal; "stay on the sidelines and wait for a better opportunity" [12:30]
5. Pin bar not showing clear rejection of EMA area [09:30]

### Claimed performance
Through multiple worked examples: "perfect trade" with 2.8 risk-reward ratio [07:30]; another trade with 2.5 risk-reward achieving 3+ R before reversing [11:00]; another with 2-3 R target [10:00]. Shows example of stopped-out trade with lesson on moving stop to breakeven [11:30]. Notes: "in the long run, the volume confirmation will save your account for many losing trades" [08:30].

### Vagueness log
1. UNDEFINED-RULE: "Stand out when compared to surrounding bars" [03:30] - how much more prominent should wick be?
2. UNDEFINED-RULE: "Heavy traffic" or "choppy" market definition - what price action frequency qualifies? [04:30]
3. UNDEFINED-RULE: "Much larger than the average trading range" [12:30] - what multiple or percentage qualifies as "much larger"?
4. UNDEFINED-RULE: Pullback entry point - "before the market resumes its trend" [02:30] is vague; how deep into pullback before entering?
5. UNDEFINED-RULE: When price "consolidates above the 50 EMA" - what consolidation pattern or duration? [12:00]
6. SUBJECTIVE: Determining "areas of value" and "confluence" from multiple levels [05:00], [05:30]
7. UNDEFINED-PARAM: "Next swing high/low" - how far forward? How does speaker identify which swing level is "next"?
8. UNDEFINED-RULE: Estimated target setting [09:30] - no mechanical rule given

### Mechanizability
PARTIAL — Pin bar pattern identification (wick to body ratio, position) is mechanically detectable from OHLCV. Volume confirmation (higher than previous 3-4 bars) is computable. EMA crossover and position (above/below) is mechanical. However, defining "stand out" wicks, identifying value areas and confluence (which involve support/resistance levels not mechanically specified), and determining which swing level is "next" requires subjective judgment. Stop loss placement rules are clear, but take profit identification needs swing point definition.

## Notable claims and caveats
Speaker emphasizes avoiding trades based on pin bar alone: "Pin Bars should not be traded on their own" [04:00]. They are "short duration setups" with impact only "within 4-5 days of its creation" [04:00]. 

Warns against large pin bars: "if the Pin Bar is much larger than the average trading range of the preceding bars, then it will most likely become a continuation pattern rather than a reversal pattern" [12:30].

Notes volume filter importance: "The volume condition isn't met...the volume confirmation will save your account for many losing trades" [08:00], [08:30]. 

Shows mixed outcomes: successful trades with 2-3R but also stopped-out trades, teaching money management lesson of moving stop to breakeven when price consolidates in profit [12:00].

Never explicitly mentions transaction costs, slippage, or commission. No discussion of overall win rate or drawdown. Emphasizes EMA period choice is flexible: "once you get some experience under your belt, you will start to learn how they behave in different market conditions" [06:00].
