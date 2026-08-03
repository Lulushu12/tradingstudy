# I Finally Found A 5-Minute Scalping Trading Strategy That ACTUALLY Works

- video_id: 5ZYVXiSKfxU
- url: https://www.youtube.com/watch?v=5ZYVXiSKfxU
- duration: 14:54
- classification: STRATEGY

## Summary
This video presents a 5-minute scalping breakout strategy requiring confluence of three signals: Heikin-Ashi trend candles, RSI momentum (50-period, 50 line), and Volume Spread Analysis (VSA). Trades are taken when price breaks above resistance (long) or below support (short) with all three indicators aligned and high/ultra-high volume confirming the breakout.

## Instruments and timeframes stated
- markets: NOT STATED (examples shown: Apple, Tesla, EUR/USD)
- timeframes: 5-minute chart (with mention of alternatives using other timeframes if adjusted) [00:00]
- sessions/hours: NOT STATED

## Strategy 1: Confluence Breakout Scalping Strategy

### Indicators and settings
1. **Heikin-Ashi Candles** (no parameters, standard HA):
   - Green candles = uptrend
   - Red candles = downtrend
   - Candles without lower wicks (green) = strong bullish [02:30]
   - Candles without upper wicks (red) = strong bearish [02:30]

2. **RSI Bars / RSI Indicator**:
   - Period: 50 [04:00]
   - Threshold: 50 line (center) [04:00]
   - Green bars: RSI above 50 = upward momentum [04:30]
   - Red bars: RSI below 50 = downward momentum [04:30]

3. **Volume Spread Analysis (VSA) Indicator**:
   - Red = ultra-high volume [05:00]
   - Yellow = high volume [05:00]
   - Green = average volume [05:00]
   - Blue = low volume [05:00]

### Context / bias filter
Look for a clear trend established by Heikin-Ashi candles (multiple consecutive green or red candles).

### Entry trigger
**For LONG Entry** [07:20]:
- Heikin-Ashi candles are GREEN (trend is up) ✓
- RSI candles are GREEN (momentum is up) ✓
- Price breaks ABOVE resistance level ✓
- Volume shows HIGH or ULTRA-HIGH (red or yellow on VSA) ✓
- Confluence: All four conditions must be present

Wait for candle close beyond support/resistance level before confirming breakout [08:00]

**For SHORT Entry** [07:25]:
- Heikin-Ashi candles are RED (trend is down) ✓
- RSI candles are RED (momentum is down) ✓
- Price breaks BELOW support level ✓
- Volume shows HIGH or ULTRA-HIGH volume ✓
- Confluence: All four conditions must be present

### Stop loss
Place above the breakout candle (for longs) or below the breakout candle (for shorts) [09:00-09:15]
- If high volume on breakout, set stop above that particular candle [09:00]
- Aim for 2:1 risk-to-reward ratio [09:00]

### Take profit / exit
Take profit target is 2:1 risk-reward ratio (double the risk amount) [09:00, 09:15, 11:25]

### Invalidation / skip conditions
- If Heikin-Ashi color doesn't match (mix of green and red), trend is unclear - skip
- If RSI doesn't confirm (wrong color candles), momentum is not aligned - skip
- If breakout occurs on low or average volume, it is likely false - skip [06:30]

### Claimed performance
"Strategy which I'm currently backtesting on 5-minute timeframe" [00:00] - no specific win rate or results stated

### Vagueness log
1. "Multiple consecutive" green/red candles for establishing trend - exact count NOT STATED
2. "High or ultra-high volume" - exact threshold is NOT STATED (is yellow alone sufficient or only red?)
3. Support and resistance levels are identified via price action ("swing lows," "consolidation areas") - VISUAL-ONLY identification
4. "Obvious increase in volume" at breakout is SUBJECTIVE
5. No specific rules for position sizing beyond risk management framework

### Mechanizability
FULL - Heikin-Ashi candles are computable. RSI above/below 50 is computable. Volume levels (VSA) are computable. Resistance/support breakout is computable IF defined by prior swing highs/lows. All rules can be coded from OHLCV.

---

## Risk Management Notes [13:00-13:30]

- Never risk more than 1-2% of initial deposit on single trade [13:00]
- This allows 2-3 positions at once without excessive exposure [13:00]
- Scalping produces many trades; position sizing must be scaled down accordingly

---

## Customization Notes [13:30-14:00]

Speaker notes strategy can be modified:
- Can replace Heikin-Ashi with regular candlesticks + moving average [13:30]
- Can remove RSI candles (Heikin-Ashi alone shows momentum via wicks) [14:00]
- Can remove volume confirmation (breakouts on average volume can still work) [14:00]
- No specific rules provided for these modifications

---

## Notable claims and caveats
- Title claims "ACTUALLY Works" but no backtesting results or win rate provided
- Speaker says "I'm currently backtesting" [00:00] - suggests this is a work-in-progress, not proven strategy
- Confluence concept strongly emphasized - "This is the power of confluence" [08:30]
- No discussion of costs, spread, slippage, or commission
- No mention of drawdown, consecutive losses, or market conditions where strategy fails
- No mention of varying performance across different currency pairs or asset classes
