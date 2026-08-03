# EASY Moving Average ENVELOPES Strategies for Scalping & Day Trading (For Beginners)

- video_id: X1UeebLbz30
- url: https://www.youtube.com/watch?v=X1UeebLbz30
- duration: 10:33
- classification: MULTI-STRATEGY

## Summary
The video explains Moving Average Envelopes as a tool to filter false signals from moving averages. Envelopes consist of an SMA plotted with parallel bands positioned at a fixed percentage above and below. The speaker presents four distinct strategies: breakout trading when price breaks the envelope bands, range trading with overbought/oversold entries when the MA is flat, pullback trading at envelope levels, and dynamic support/resistance trading in trending markets.

## Instruments and timeframes stated
- markets: NOT STATED
- timeframes: varies by strategy; day traders/scalpers use shorter periods [01:30]; swing traders use longer periods [01:30]
- sessions/hours: NOT STATED

## Strategy 1: Envelope Breakout Trading

### Indicators and settings
- Indicator: Moving Average Envelopes
- MA period: varies by timeframe and volatility (example given: 21-day SMA) [02:30]
- Envelope percentage: varies (examples given: 3% for short-term traders, 5% for swing traders) [03:00]
- Notes: Day traders/scalpers use shorter MAs and relatively tight envelopes [01:30]; swing traders use longer MAs and wider envelopes [01:30]

### Context / bias filter
Use this strategy when the market is not ranging flat. Price breakouts signal potential start of extended trend [05:00]. Narrow envelopes help identify strong moves [05:00].

### Entry trigger
**Long:** Price breaks above the upper envelope band [04:30]. Can be confirmed by buying strength or price continuing to move above the band [05:00].

**Short:** Price breaks below the lower envelope band [04:30]. Can be confirmed by weakness or price continuing below the band [05:00].

### Stop loss
NOT STATED

### Take profit / exit
NOT STATED

### Invalidation / skip conditions
"The majority of price breakouts do not go on to form new trends. They will instead more frequently revert back into the previous price range" [05:30]. This is a risk acknowledged but not an explicit skip condition.

### Claimed performance
Shows breakout continuing above upper envelope as "buying strength" [05:00]. "A strong move below the lower envelope signals weakness that can foreshadow an extended downtrend" [05:00].

### Vagueness log
1. UNDEFINED-PARAM: MA period choice - no specific rule given; depends on "characteristics of the market you are trading" [01:30]
2. UNDEFINED-PARAM: Envelope percentage - depends on volatility and timeframe; must be set via trial and error [05:00]
3. UNDEFINED-RULE: Confirmation of breakout - speaker mentions "buying strength" and "continued moving" but no mechanical confirmation given
4. UNDEFINED-RULE: Stop loss placement NOT STATED
5. UNDEFINED-RULE: Take profit levels NOT STATED

### Mechanizability
PARTIAL — The breakout condition is mechanically identifiable (price crosses envelope band), but without specified MA period and percentage parameters, plus undefined stop/take profit levels, the strategy cannot be fully coded without making assumptions.

---

## Strategy 2: Range Trading with Overbought/Oversold

### Indicators and settings
- Indicator: Moving Average Envelopes
- MA period: varies (higher parameters for range trading) [05:30]
- Envelope percentage: varies based on volatility [02:30]
- Critical condition: Moving Average must be FLAT (horizontal) [06:00]

### Context / bias filter
Only use when the moving average is flat or nearly horizontal, indicating no strong trend [06:00]. When MA is flat, price moving to envelopes indicates overbought/oversold [06:00]. Speaker notes: "price can become overbought and remain overbought when the bullish trend is strong" [06:30], so flat MA is essential for this strategy.

### Entry trigger
**Long:** Price penetrates lower envelope and closes back inside the envelope [05:30], [06:00]. This occurs when MA is flat [06:00].

**Short:** Price penetrates upper envelope and closes back down inside the envelope [05:30], [06:00]. This occurs when MA is flat [06:00].

### Stop loss
NOT STATED

### Take profit / exit
NOT STATED. Implied: close when price returns inside the envelope bands [05:30].

### Invalidation / skip conditions
Do not use when MA has a strong bullish or bearish slope [06:30]. Price can remain overbought/oversold during strong trends, invalidating the strategy [06:30].

### Claimed performance
NONE CLAIMED

### Vagueness log
1. UNDEFINED-PARAM: MA period - not specified; depends on market characteristics
2. UNDEFINED-PARAM: Envelope percentage - not specified; depends on volatility
3. UNDEFINED-RULE: "Flat" MA definition - what slope threshold qualifies as flat?
4. UNDEFINED-RULE: Entry confirmation - "closes back inside" is not precisely defined (next candle? at what point in candle?)
5. UNDEFINED-RULE: Stop loss NOT STATED
6. UNDEFINED-RULE: Take profit levels NOT STATED

### Mechanizability
PARTIAL — Entry condition (price penetrates then closes back inside) is mechanically identifiable, but the definition of "flat" MA and lack of stop/take profit levels make this incomplete without assumptions.

---

## Strategy 3: Pullback Trading at Envelopes

### Indicators and settings
- Indicator: Moving Average Envelopes
- MA period: based on recent swing highs/lows [07:30]
- Envelope percentage: set to match recent price extremes (example: if last high was 5% above MA, set upper envelope to 5%) [07:30]

### Context / bias filter
Market has made prior swings and established envelope levels. Use when market respects these dynamic support/resistance levels [07:30]. Pullback occurs to these previously established levels [07:30].

### Entry trigger
Buy at lower envelope when price makes a swing low that respects the dynamic support offered by lower envelope [07:30]. Sell at upper envelope when price makes a swing high that respects dynamic resistance [07:30]. The second touch of the envelope level can confirm the setup [07:30].

### Stop loss
NOT STATED

### Take profit / exit
NOT STATED

### Invalidation / skip conditions
If envelope levels are not respected (price does not bounce), the setup is invalidated.

### Claimed performance
"This shows...great entry at the lower envelope. The market made a swing low here, and respected the dynamic support offered by the lower envelopes the second time the price reached the area" [07:30].

### Vagueness log
1. UNDEFINED-RULE: Envelope percentage setting - "if the last high was let's say five percent above" - how is "last" defined? How many swings back?
2. UNDEFINED-RULE: Entry timing - "second time" is vague; what if price touches envelope three times?
3. UNDEFINED-RULE: Stop loss NOT STATED
4. UNDEFINED-RULE: Take profit levels NOT STATED
5. SUBJECTIVE: Identifying "swing highs/lows" is not mechanically specified

### Mechanizability
PARTIAL — The concept of using prior extremes for envelope settings is computable, but the definition of "last high" and confirmation via "second touch" requires clarification. Stop and take profit are undefined.

---

## Strategy 4: Dynamic Support/Resistance in Trends

### Indicators and settings
- Indicator: Moving Average Envelopes
- MA period: NOT STATED (varies by strategy)
- Envelope percentage: NOT STATED (varies by strategy)

### Context / bias filter
**Uptrend:** Price is above the MA. Upper envelope acts as dynamic resistance/take profit zone; lower envelope acts as dynamic support [08:00], [08:30].

**Downtrend:** Price is below the MA. Lower envelope acts as dynamic support/take profit zone; upper envelope acts as dynamic resistance/overbought zone [08:30], [09:00].

### Entry trigger
**Uptrend entries:** When price crosses above the moving average, assume next rally will advance to upper envelope [08:00]. Buy pullbacks at moving average (which will act as support) targeting the upper envelope [08:00].

**Downtrend entries:** When price crosses below moving average, assume downside potential is to lower envelope [08:30]. Sell rallies at moving average (which will act as resistance) targeting the lower envelope [08:30].

### Stop loss
NOT STATED

### Take profit / exit
**Uptrend:** Upper envelope line acts as take profit zone [08:30]. In uptrend, lower envelope offers buying opportunity (oversold area) [09:00].

**Downtrend:** Lower envelope line acts as take profit zone [08:30]. In downtrend, upper envelope offers selling opportunity (overbought area) [09:00].

### Invalidation / skip conditions
If trend reverses (MA slope changes), the setup is invalidated.

### Claimed performance
NONE CLAIMED

### Vagueness log
1. UNDEFINED-PARAM: MA period - not specified
2. UNDEFINED-PARAM: Envelope percentage - not specified
3. UNDEFINED-RULE: "Pullback to MA" trigger - how deep must pullback be? Exact entry price not specified
4. UNDEFINED-RULE: Stop loss NOT STATED
5. SUBJECTIVE: Determining trend direction and MA slope direction is subjective

### Mechanizability
PARTIAL — The concept of envelopes as dynamic support/resistance is sound and mechanically identifiable, but without specific MA period and percentage parameters, plus undefined pullback depth and stop loss levels, implementation requires parameter assumptions.

---

## Notable claims and caveats
Speaker emphasizes that parameter selection is critical and "takes practice, trial and error" [05:00]. Notes that "different traders have their own way in which they use the envelope" [04:00]. Acknowledges that moving averages are lagging indicators [09:00] and that "the majority of price breakouts do not go on to form new trends" [05:30]. Recommends backtesting "different periods in different time frames" [09:30]. Explicitly states: "Building a complete Envelope strategy is not just about signals informing you when to buy and sell. Envelopes are just a part of the full story. Price action, support and resistance and a solid risk management are also needed" [10:00]. Never mentions transaction costs, slippage, or commission.
