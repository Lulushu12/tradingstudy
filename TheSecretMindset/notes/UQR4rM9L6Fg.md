# Ultimate Entry Strategy For Day Trading (Found 7 Sniper Entry Models That Print Every Day)

- video_id: UQR4rM9L6Fg
- url: https://www.youtube.com/watch?v=UQR4rM9L6Fg
- duration: 25:55
- classification: MULTI-STRATEGY

## Summary
This video presents eight distinct price action entry models for day trading. Each model is based on market structure and price behavior at key levels, with no reliance on oscillator indicators. The models range from simple candle patterns at support/resistance to timing breakouts and mean reversion trades. No performance metrics are claimed; the speaker emphasizes mechanical entry execution and risk management through clearly defined stops.

## Instruments and timeframes stated
- markets: NOT STATED
- timeframes: "first stretch after the open, maybe 5, 15, or 30 minutes" mentioned for opening range breakout [13:00]; otherwise NOT STATED
- sessions/hours: "at the open, during big sessions, or when volume is strong" for pivot bounces [18:00-18:30]; otherwise NOT STATED

## Strategy 1: Engulfing Candles at Supply or Demand Levels

### Indicators and settings
- Price action only: engulfing candle pattern
- No moving averages, no RSI, no MACD

### Context / bias filter
Price must be at a "supply or demand level. It's where lots of trades happened before. It's where people expect a fight" [01:00-01:30]. Bullish setup: a big green candle fully covers the previous red candle [00:00]. Bearish setup: a big red candle swallows a green one [00:00].

### Entry trigger
"When the candle closes, you enter your trade" [01:30]. For longs: "you buy at the close" [02:00]. For shorts: "you sell at the close" [02:00].

### Stop loss
"The low of the engulfing candle for longs and a high for shorts" [02:00].

### Take profit / exit
NOT STATED

### Invalidation / skip conditions
Only valid when price is at a supply or demand level [01:00-02:30].

### Claimed performance
NONE CLAIMED

### Vagueness log
1. UNDEFINED-PARAM: "supply or demand level" - speaker says "where lots of trades happened before" but provides no computable definition or method to identify these levels
2. UNDEFINED-RULE: "fully covers the previous bar" - what percentage or exact rule defines "full" coverage? 100% overlap required?
3. SUBJECTIVE: Identifying which price levels qualify as supply/demand zones

### Mechanizability
PARTIAL — The engulfing candle pattern itself is computable (current candle's high > previous candle's high AND current candle's low < previous candle's low), but the context filter "supply or demand level" lacks a mechanical definition. Without knowing how to identify these levels, the entry cannot be automated.

---

## Strategy 2: Support and Resistance Flip

### Indicators and settings
- Support and resistance levels drawn as "bands, not razor thin lines" [04:30-05:00]
- No technical indicators

### Context / bias filter
Strong uptrend [03:00]. "Price reaches a resistance area. Sellers try to stop the move here. You may see price bounce down a few times, but each bounce is weaker. Then price finally breaks through resistance" [03:00-03:30]. After breakout, price pulls back and "the old support acts like a ceiling" (in downtrend analog) [03:30]. The flip is "where old sellers turn into new buyers" [04:00].

### Entry trigger
"When price breaks out, pulls back and holds at the flip, you see real strength. The market is showing which side is in control. This is your entry spot" [04:30]. "The first retest is usually the strongest. After the initial breakout, the first time price comes back to test the flipped level, the reaction is often fast and clear" [05:00-05:30].

### Stop loss
Implied: just on the other side of the flipped level, though NOT STATED explicitly.

### Take profit / exit
NOT STATED

### Invalidation / skip conditions
"The more times a level gets tested, the weaker it becomes" [05:30]. Later retests work but "the edge is strongest on the first or second touch" [05:00-05:30].

### Claimed performance
NONE CLAIMED

### Vagueness log
1. UNDEFINED-RULE: "each bounce is weaker" - what metric defines weakness? Lower low? Lower volume? Lower candle size?
2. UNDEFINED-RULE: "finally breaks through" - what constitutes a break? Close above the line? How far above?
3. UNDEFINED-PARAM: Support/resistance "bands" - what width? How to determine band edges?
4. SUBJECTIVE: Drawing support/resistance levels and identifying when they're "broken"

### Mechanizability
PARTIAL — The flip concept (break of resistance followed by retest) can be coded if swing highs/lows are used to define S/R, but identifying when "each bounce is weaker" requires defining weakness, and the "band" concept vs. a single price line is ambiguous.

---

## Strategy 3: First Pullback After Market Structure Shift

### Indicators and settings
- Moving average mentioned as potential pullback target: "maybe to a moving average, maybe to a previous level" [06:30] — NO PERIOD SPECIFIED
- No other indicators

### Context / bias filter
"Price going down for days. Suddenly it flips. It breaks a recent high, showing buyers finally took control. That's a market structure shift" [06:00-06:30]. The first move after a shift is "often wild and sharp. It's full of traders bailing out of all trades, stops triggering, and late chasers piling in" [06:00-06:30].

### Entry trigger
"Wait for the first pullback. After that shift, price makes its first move in the new direction, then pauses or retraces" [06:30]. "Enter as soon as you see buyers or sellers step back in, and price runs the new trend" [06:30]. Watch for "signs that selling is drying up, like smaller candles, lower volume, or even a reversal bar. As soon as price pushes back up, resuming the trend, you buy" [07:30-08:00].

### Stop loss
"Your stop goes below the pullback low" for longs [08:30]. "just above the pullback high for shorts" [08:30].

### Take profit / exit
"Your target is the next swing high or low or even further if the trend keeps running because you enter after some profit taking or counter trend action" [08:30-09:00].

### Invalidation / skip conditions
NOT STATED

### Claimed performance
NONE CLAIMED

### Vagueness log
1. UNDEFINED-PARAM: Moving average period — NOT STATED. Speaker says "maybe to a moving average" but doesn't specify MA length [06:30]
2. UNDEFINED-RULE: "breaks a recent high" - what qualifies as "recent"? How many bars back?
3. UNDEFINED-RULE: "first pullback" — how to distinguish first from subsequent pullbacks after the shift move?
4. UNDEFINED-RULE: "smaller candles, lower volume" - what size/volume constitutes "smaller" and "lower"?
5. SUBJECTIVE: "buyers or sellers step back in" — what price action qualifies as "stepping back in"?

### Mechanizability
PARTIAL — The market structure shift (break of recent swing high) can be identified, and pullback can be defined as a reversal off the shift move. However, the entry signal "buyers step back in" and the pullback depth targets are subjective and not specified with parameters.

---

## Strategy 4: Liquidity Grab Against Main Trend

### Indicators and settings
- Price action only: recent swing lows/highs
- No indicators

### Context / bias filter
Strong uptrend "making higher highs and higher lows. Everyone sees it. Traders want in. They chase price buying late and footing their stops just below the last swing low or the nearest support" [09:30]. Big traders need liquidity and "hunt for liquidity. Liquidity is where lots of orders wait to be triggered. in an uptrend. Think of all those stop-losses sitting just under the last low" [09:30-10:00].

### Entry trigger
"You wait for price to drop below a recent low in an uptrend or above a recent high in a downtrend. You know, that's where liquidity pools sit. You want to see a quick flush, price slices through, then price snaps right back up. That's your signal" [11:30-12:00]. "You enter as soon as price comes back above the broken support or as soon as the candle closes back inside the range" [12:00].

### Stop loss
"Your stop goes just below the liquidity grab low" [12:00].

### Take profit / exit
NOT STATED. Implies: catch the trend resumption move.

### Invalidation / skip conditions
NOT STATED

### Claimed performance
NONE CLAIMED

### Vagueness log
1. UNDEFINED-RULE: "recent low" - how recent? How many bars back?
2. UNDEFINED-RULE: "quick flush" — what duration or speed qualifies as "quick"? Is there a bar count or time threshold?
3. SUBJECTIVE: Identifying exactly where traders have placed stops (liquidity pools)

### Mechanizability
PARTIAL — A break below recent swing lows and a sharp retracement can be coded, but the "quick flush" filter is undefined, and the actual location of liquidity (other traders' stops) is not visible to the trader.

---

## Strategy 5: Opening Range Breakout

### Indicators and settings
- Opening range high and low over: "maybe 5, 15, or 30 minutes" [13:00] — SPECIFIC PERIOD NOT SPECIFIED (speaker leaves choice open)
- No indicators

### Context / bias filter
"Every morning, markets wake up with a bang. There's a rush of orders, leftover trades from the night before, and new bets for the day ahead. And this chaos sets up one of the simplest, sharpest entries you can use, the opening range breakout" [12:30-13:00].

### Entry trigger
"Mark the highest point and the lowest point price reaches in that window. That's your opening range" [13:00]. "Once the opening range is set, you watch for a clean break above or below" [13:30]. "As soon as price breaks out and trades in the new zone, you enter in that direction" [14:00]. Entry is at the breakout, "You're in right at the start of the move when momentum is strongest" [14:00-14:30].

### Stop loss
"If you enter on a break above the high, your stop is at the low. If you go short on a break below, your stop is at the high" [14:30-15:00].

### Take profit / exit
NOT STATED

### Invalidation / skip conditions
"false breakout. Sometimes price pokes above the high or below the low only to snap right back into the range" [15:00-15:30]. "breakouts fail more often when the opening range is unclear or choppy. If the first candles are wild and overlapping with no clear direction, you're more likely to get faked out" [15:30-16:00]. "only act when the range is clean and price action is decisive" [16:00].

### Claimed performance
No win rate stated, but notes: "Some days you get trapped and stopped out quickly" [15:30].

### Vagueness log
1. UNDEFINED-PARAM: Opening range period — speaker says "maybe 5, 15, or 30 minutes" [13:00] but does not specify which to use
2. UNDEFINED-RULE: "clean break" — what distance or percentage above/below the line qualifies as a "clean" break? One tick? One bar?
3. UNDEFINED-RULE: "clean and price action is decisive" — what defines "clean" and "decisive"? No metrics given
4. SUBJECTIVE: Determining if range is "unclear or choppy" vs. clean

### Mechanizability
PARTIAL — The entry mechanics (breakout of opening range high/low) can be coded once the period is selected, but the period itself is unspecified, and the "clean break" and "clean range" filters lack definition.

---

## Strategy 6: Pivot Point Bounce

### Indicators and settings
- Daily or weekly pivot points [16:00]
- Calculation formula: NOT STATED (standard pivot calculation implied but not confirmed)

### Context / bias filter
Direction bias: "If today's main pivot sits above yesterday's, it shows buyers control the market. You look for long trades" [17:00-17:30]. "If the pivot is lower than yesterday's, sellers have the edge. So, you look for shorts" [17:30].

### Entry trigger
"You wait for price to hit the pivot, then watch for a reaction. If price wakes hard, prints a reversal bar, or bounces back with energy, that's your signal. You enter in the direction of the move away from the pivot" [16:30-17:00].

### Stop loss
"If you enter on a bounce, your stop is close just on the other side of the pivot" [18:00].

### Take profit / exit
NOT STATED

### Invalidation / skip conditions
"Pivots work best when the market is active, at the open, during big sessions, or when volume is strong. In slow times, the bounce can be weak or fizzle out fast" [18:00-18:30].

### Claimed performance
NONE CLAIMED

### Vagueness log
1. UNDEFINED-PARAM: Pivot calculation — NOT STATED; standard formula is assumed but not confirmed
2. UNDEFINED-RULE: "wakes hard" — what defines this? Speed of move? Candle size? Volume?
3. UNDEFINED-RULE: "reversal bar" — what constitutes a reversal bar? Pin bar? Engulfing? Any counter-trend candle?
4. UNDEFINED-RULE: "bounces back with energy" — what is "energy"? Volume? Candle size? Speed?
5. SUBJECTIVE: Assessing whether price is reacting with "energy" or bouncing "hard"

### Mechanizability
PARTIAL — Pivot points can be calculated (if standard formula is assumed), but the entry trigger ("wakes hard" / "reversal bar" / "with energy") requires definition or subjective interpretation.

---

## Strategy 7: Snapback from Overextended Move

### Indicators and settings
- VWAP and VWAP bands (period: NOT STATED)
- Channels (definition: NOT STATED)
- Average price range (calculation: NOT STATED)

### Context / bias filter
"Price can run far in one direction, sometimes too far. You see this in big moves that stretch past normal ranges, break out of channels or push beyond VWAP bands" [18:30-19:00]. "At some point it has to slow down or turn back" [18:30].

### Entry trigger
Wait for exhaustion signs: "a reversal candle, a big wick, or a sudden spike in volume" [19:30-20:00]. "As soon as price snaps back inside the band, you enter" [20:30]. This is mean reversion: "Price usually moves around an average. When it goes too far from that average, it often comes back" [19:30-20:00].

### Stop loss
"Your stop goes just past the extreme" [20:30].

### Take profit / exit
"if price returns to the average or further" [21:00].

### Invalidation / skip conditions
"The biggest risk is trying to call the top or bottom too soon. A lot of times price will go further than you think, blowing past your levels and stopping you out" [21:30-22:00].

### Claimed performance
"Even if you catch one out of three reversals, you will still be in profit" [21:30]. This implies a minimum 3:1 risk-reward requirement. "This entry is not for everyone. It's tailored for aggressive traders" [21:30-22:00].

### Vagueness log
1. UNDEFINED-PARAM: VWAP period — NOT STATED
2. UNDEFINED-PARAM: VWAP band width/settings — NOT STATED
3. UNDEFINED-PARAM: Channel definition — NOT STATED
4. UNDEFINED-PARAM: "average price range" calculation — NOT STATED
5. UNDEFINED-RULE: "far outside normal ranges" — what distance or ATR multiple?
6. UNDEFINED-RULE: "reversal candle" — what pattern qualifies?
7. UNDEFINED-RULE: "big wick" — what size is "big"?
8. UNDEFINED-RULE: "sudden spike in volume" — what level is "sudden"? 2x average? 3x?
9. SUBJECTIVE: Identifying price as "overextended"

### Mechanizability
DISCRETIONARY — Even with VWAP indicators defined, this strategy requires multiple judgment calls: identifying overextension, calling reversals, and timing the snapback. The entry signals are subjective and the strategy is explicitly described as discretionary ("This entry is not for everyone").

---

## Strategy 8: Range Expansion After Compression

### Indicators and settings
- Compression zone high and low (marked manually)
- No technical indicators

### Context / bias filter
Compression: "tight range, candles with small bodies, and no one really winning. Buyers and sellers both wait. Volume drops and the chart goes quiet" [22:30-23:00]. "Something big is coming. Compression shows up as a tight range" [22:30]. "Pressure builds, orders stack up on both sides" [22:30-23:00].

### Entry trigger
"Mark the high and bottom of this zone. Now comes the entry. You wait for the breakout. A big candle, strong volume. Price bursts out of the tight box. The expansion must be sudden and sharp. This is the moment you enter, right as the market wakes up" [23:00-23:30]. "As soon as price breaks out with a strong candle and increased volume, you enter in the direction of the move" [24:00-24:30].

### Stop loss
"If you go long on a breakout up, your stop goes just inside the compression zone. If you go short on a breakdown, your stop goes just above the range" [24:30-25:00].

### Take profit / exit
"The move after compression often runs far, giving you a strong risk-to-reward setup" [24:30].

### Invalidation / skip conditions
"If price never breaks out, you don't enter. If the breakout is weak, like a small candle and no volume, again, you skip it. Only the clean, strong expansions, get your trade" [25:00-25:30].

### Claimed performance
NONE CLAIMED

### Vagueness log
1. UNDEFINED-RULE: "tight range" — what ATR multiple or pip range constitutes tight?
2. UNDEFINED-RULE: "small bodies" — what candle size is "small"?
3. UNDEFINED-RULE: "big candle" in breakout — what size is "big"?
4. UNDEFINED-RULE: "strong volume" — what volume level qualifies as "strong"?
5. UNDEFINED-RULE: "sudden and sharp" — what speed or size threshold?
6. UNDEFINED-RULE: "clean, strong expansions" — no numerical definition
7. SUBJECTIVE: Identifying compression zones and expansions

### Mechanizability
PARTIAL — The general structure (identify low-volatility period, wait for breakout) can be coded once thresholds are set, but the key filters ("tight", "big", "strong", "clean") lack numerical definitions.

---

## Notable claims and caveats
- No backtested win rates or profit claims are made for any strategy
- Opening range breakout model: "Some days you get trapped and stopped out quickly" [15:30]
- Snapback model: "Even if you catch one out of three reversals, you will still be in profit" [21:30] (implies high losers, but big winners)
- Snapback model: "There's always the chance the move keeps going and you're caught fading a trend that isn't finished" [21:30-22:00]
- Speaker does not mention transaction costs, slippage, commission, or spreads anywhere in the video
- No discussion of drawdown, losing streaks, or what these strategies fail at

