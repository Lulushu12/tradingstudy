# A Scalping Price Action Trading Strategy I Never Shared Before

- video_id: UI2vRZN78F8
- url: https://www.youtube.com/watch?v=UI2vRZN78F8
- duration: 12:03
- classification: STRATEGY

## Summary
A scalping strategy based on the opening price matching the day's high or low, which signals institutional buying or selling pressure. The strategy uses the first 5-minute candle to identify momentum direction and provides two entry approaches: aggressive entries at the breakout of the 5-minute range, or conservative entries on pullbacks to the 50% Fibonacci retracement or midpoint of the opening candle. Exits use scaled profit-taking with anchored VWAP bands to adapt to real-time momentum.

## Instruments and timeframes stated
- markets: NOT STATED (examples use daily reference, but trades on 5-minute timeframe)
- timeframes: 5-minute candles [02:00]; trades during first 5-15 minutes of trading day [04:00]
- sessions/hours: trading day open [04:00]

## Strategy 1: Open Matches High/Low Scalping

### Indicators and settings
- Open Price indicator: displays horizontal line marking open level [01:30]
- Opening Range Breakout indicator: draws upper and lower lines connecting highs and lows of first 5 minutes [02:00]; set to 5-minute timeframe [02:00]
- Optional: Anchored VWAP bands around the first 5-minute open candle [09:00]
  - Upper and lower bands anchored to opening price [09:00]
  - Parameters: NOT STATED for VWAP period or band width

### Context / bias filter
Setup occurs when the day's open price matches the day's high or low. This indicates institutional participation and directional bias [00:00], [03:30].

**Bullish signal:** Open equals the day's low [00:30]. Green candle [01:00]. "Sellers didn't have any power to move price, not even one tick below the open" [05:00]. Indicates buyers stepped in early and established clear support [00:30].

**Bearish signal:** Open equals the day's high [00:30]. Red candle [01:00]. Sellers wasted no time capping upwards moves [00:30]. Indicates institutional profit-taking or short positioning pre-market [05:30].

Setup is most powerful during first 5-15 minutes when volume increases and causes wider oscillations [04:30].

### Entry trigger
Two entry approaches:

**Aggressive Entry (Bullish on open = low):** Enter long on first push above the first 5-minute candle high, or immediately after the candle forms [06:00]. Volume-backed breakouts spark continuation [07:30].

**Aggressive Entry (Bearish on open = high):** Set sell order a tick below the 5-minute candle's low [06:30]. Smart money likely capped upside there [06:30].

**Conservative Entry:** Wait for 50% Fibonacci retracement of initial candle if candle is larger in size, then enter in direction of initial candle [06:00]. Alternatively, wait for pullback/retracement back to midpoint of opening 5-minute candle before triggering entry [07:30]. This avoids getting stopped out on volatile opening candles [08:00].

**Bullish triggers specifically:** Buy on push above 5-minute high when open matches day's low [07:00]. Low confirms underlying support [07:00].

**Bearish triggers specifically:** Sell below 5-minute low when open matches day's high [06:30].

### Stop loss
"Always risk small with tight stops above or below the 5-minute range" [07:00]. Alternative: "Stop placement near the open price often offers the best compromise" [08:30]. Avoid trailed stops as they exit positions too hastily [08:30]. Raise stops proactively to lock profits as swings develop [08:30].

### Take profit / exit
Use scaled profit-taking with anchored VWAP bands [09:30]:
- Target 2nd or 3rd VWAP band in direction of entry for partial profits [09:30]
- For long entries: target upper anchored VWAP bands for first take profit [09:30]
- For short entries: aim for lower VWAP bands for initial gains [09:30]
- Scale out a portion of position while trailing stop on remainder to lock further profits if momentum continues [10:00]

Alternative approach: Reduce position size if entering on wider opening candles [11:00]. Trail stops incrementally to lock in profits as momentum extends [11:30]. Scale out partial profits in pieces rather than exiting entire trade at once [11:30].

### Invalidation / skip conditions
Setup is invalidated if open does not match day's high or low. Momentum stalls may invalidate follow-through; speaker recommends "waiting for modest retracement often helps manage risk better" [08:00], suggesting pullback without follow-through cancels trade.

### Claimed performance
"Creates a scalping opportunity" [00:00]. "Provides prime entries" [00:00]. "High-probability buy entry" when open matches low [01:00]. "Short setup" when open matches high [01:30]. Describes examples as working out with multiple targets hit [09:30]. States: "overextended openings frequently pull back within the range" [08:00].

### Vagueness log
1. UNDEFINED-PARAM: "A tick below the 5-minute candle's low" [06:30] - tick size depends on instrument, not specified
2. UNDEFINED-PARAM: VWAP bands - which specific bands? (2nd and 3rd mentioned but not defined) [09:30]
3. UNDEFINED-PARAM: 50% Fibonacci retracement - applied to which candle? What size threshold for "larger in size"? [06:00]
4. UNDEFINED-RULE: Pullback retracement threshold - how much pullback to "midpoint" triggers entry? [07:30]
5. UNDEFINED-RULE: Stop placement "near the open price" - what tolerance? [08:30]
6. UNDEFINED-RULE: "Quality liquidity below" - not mechanically defined [06:00]
7. SUBJECTIVE: Identifying when "momentum continues" vs "stalls" [08:00]
8. SUBJECTIVE: Determining when to "raise stops proactively" [08:30]
9. UNDEFINED-RULE: Position sizing based on "wider opening candles" - threshold not specified [11:00]

### Mechanizability
PARTIAL — The core setup (open matches high or low) is mechanically identifiable from OHLCV data. The 5-minute breakout entry is computable (price crosses 5-min high/low). However, the conservative entry requires defining exact Fibonacci retracement level and "larger candle" threshold; VWAP band targets are unspecified; stop placement "near open" requires tolerance definition; and position sizing rules are vague.

## Notable claims and caveats
Speaker emphasizes simplicity as main advantage - "no complex indicators or customized formulas" [03:30]. States strategy exploits early momentum during first 5-15 minutes when volume increases [04:30]. Notes that "some momentum surges will exhaust quickly after your entry signal" [10:30], while "others may continue trending strongly" [10:30], requiring adaptive exits. Explicitly advises: "managing risk smartly is the foundation to your long-term success" [11:00]. Never mentions transaction costs, slippage, or commission. No discussion of losing streaks or drawdown risk. Emphasizes avoiding wide stop losses on volatile opening candles [08:00].
