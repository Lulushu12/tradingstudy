# 5‑Min Scalping ONLY Works If You See This Hidden Fibonacci Line (Full Strategy)

- video_id: OM042f4rWoc
- url: https://www.youtube.com/watch?v=OM042f4rWoc
- duration: 13:48
- classification: STRATEGY

## Summary
A two-timeframe scalping strategy that uses supply/demand zones identified by the last opposing candle before a structural break, combined with Fibonacci trend-based extension tools (1.61 level). The 1-hour chart identifies zones, while the 5-minute chart triggers entry via rejection candles (pin bars or outside candles). Exit targets are the 100% fib level for partial profit and 0% fib level for final exit. The strategy only trades the first touch of each zone.

## Instruments and timeframes stated
- markets: Gold futures, S&P futures, Euro Yen mentioned as examples; primary market not specified
- timeframes: 1-hour chart (zone identification), 5-minute chart (entry trigger)
- sessions/hours: London session and New York session mentioned

## Strategy 1: Fibonacci Demand/Supply Zone Scalp

### Indicators and settings
- Fibonacci trend-based extension: levels used are 1.61, 100%, and 0%
- Supply/demand zone: defined as the high-to-low range of the last opposing candle before a structural break

### Context / bias filter
Price must first break a recent high or low on the 1-hour chart, indicating a clear structural change [01:00 - 02:00]. This break must be "clear" and must lead to a "clear structural break" [02:30]. The zone is only valid on its first return since formation [10:30 - 11:00]. Check: "Is this the first time price is returning to the zone since it formed?" [10:30]. Do not use retested zones because orders may already be consumed [10:00]. No other bias filter stated.

### Entry trigger
1-hour chart: Mark the last opposing candle before the structural break (last down candle before break higher for bullish zone; last up candle before break lower for bearish zone) [01:30 - 02:00]. Draw Fibonacci trend-based extension from swing start to swing low to correction high [03:00 - 03:30]. Verify the 1.61 extension lands inside the supply/demand zone [04:00 - 04:30].

5-minute chart: Enter when price returns for the first time and prints either a pin bar (wick rejected, body closes away) or an outside candle (closes opposite direction, covers previous candle body) at the fib level, after the candle closes [06:00 - 07:30].

### Stop loss
Place above the wick of the 5-minute rejection candle [06:00]. Typical size is described as "around 15 pips" [06:00]. Stop can be much tighter using 5-minute candle than 1-hour zone (which would require 30-50 pips) [06:00 - 06:30].

### Take profit / exit
First target: the 100% Fibonacci level. Close half position here and move stop to entry [08:30].
Second target: the 0% Fibonacci level. Close remaining position [08:30 - 09:00].
The "runner" (remaining half after first target) trails above the most recent swing [08:30].

### Invalidation / skip conditions
Skip if Fibonacci 1.61 extension does NOT land inside the supply/demand zone [04:30 - 05:00].
Skip if the zone has already been touched/visited before (not the first return) [10:30 - 11:00].
Skip if the resulting move does not cause a clear structural break [02:30].

### Claimed performance
"This scalping strategy is highly accurate" [13:30]. "The structure of this trade is designed to target 3R" [13:00]. "Our losses will be much smaller than the winners" [12:30]. "This one hit the 50% target, then took us out at break even" (one example shown) [12:00]. One loss example shown with "20 pip loss" [09:30]. No specific win rate or profit metric stated.

### Vagueness log
1. UNDEFINED-PARAM: "Clear structural break" is not precisely defined in terms of minimum pip move or candle size.
2. VISUAL-ONLY: "The zone" and "structural break" rely on visual chart reading; no mechanical threshold stated for what constitutes a break.
3. UNDEFINED-PARAM: Pin bar definition ("wick is long on one side and the body closes away from that wick") is qualitative; no ratio or threshold for wick length stated.
4. UNDEFINED-PARAM: "Reject" on the fib level is not defined mechanically; unclear if price must touch exactly at 1.61 or within a range.
5. UNDEFINED-RULE: "Most recent swing" for trailing stop is not quantified; swing identification method not stated.
6. UNDEFINED-PARAM: Engulfing candle definition (outside candle that covers previous candle) lacks precision on minimum body overlap.
7. SUBJECTIVE: Determining "first touch" requires visual inspection of all prior price history for that zone; no automated rule stated.

### Mechanizability
PARTIAL - The skeleton is computable (Fibonacci extension calculation is mechanical, zone high-low is defined), but several core components cannot be coded without assumption: structural break detection, pin bar vs. engulfing candle detection (requires wick/body ratio thresholds), first-touch verification, and the exact definition of "rejection" at a price level. At least 5 specific gaps must be filled by assumption before backtesting.

## Notable claims and caveats
- Zones are "strongest on the first clean return" [10:00]; retested zones are weaker [09:30 - 10:00].
- The strategy works on "any market because the rule never changes" [11:30].
- The speaker warns against using "dead zones" (already-tested zones) and states "I've made this mistake a lot of times in the past, and I blamed the strategy" [11:00].
- The speaker notes: "Without knowing exactly where to take profit, you will watch green trades flip red while you sit there frozen" [08:00].
- Examples given on gold, S&P, and Euro Yen all show positive results except one break-even and one 20-pip loss [12:00 - 12:30].
- No mention of spread, slippage, commission, or drawdown.
