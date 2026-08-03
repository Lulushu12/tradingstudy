# Candle Range Theory, Done Right (The Real CRT Strategy)

- video_id: Qh6EjfNQ3hw
- url: https://www.youtube.com/watch?v=Qh6EjfNQ3hw
- duration: 12:53
- classification: STRATEGY

## Summary

This video presents Candle Range Theory (CRT), a three-candle pattern strategy. The speaker defines the "anchor candle" (a candle with clear direction), identifies it at key levels (trend pullbacks or swing extremes), then looks for a "sweep candle" that spikes outside the anchor's range and closes back inside. The entry is then found on a lower timeframe using either a supply/demand zone or a break-and-retest pattern. The stop is placed above the sweep high (or below for shorts) and the target is the anchor candle's low (or high for longs).

## Instruments and timeframes stated

- markets: Pound Dollar (4-hour example) [00:00], Bitcoin daily (long example) [07:00], Bitcoin daily, Tesla 4-hour, Euro Dollar 1-hour (general examples) [01:30]
- timeframes: 4-hour [00:00], daily [07:00], 1-hour [01:30], 30-minute [08:30], 15-minute [05:30], lower timeframes for entry refinement [05:30]
- sessions/hours: NOT STATED

## Strategy 1: Candle Range Theory (CRT)

### Indicators and settings

No indicators used. Pure price action pattern based on candle bodies and wicks.

### Context / bias filter

**Valid Anchor Candle locations [02:30-03:30]:**
1. Inside a clear trend pullback: "price is trending up, pulls back, prints a bearish candle" [03:00]
2. At an obvious swing high or swing low where stops are stacked [03:00-03:30]

**Invalid locations [03:00-03:30]:**
- "If price is just chopping sideways in the middle of nowhere, I leave it alone. No trend, no obvious level, no trade" [03:30]

**Anchor Candle Requirements [02:30-03:00]:**
- Decent size, not a tiny candle that can barely commit to a direction [02:30]
- A strong close, meaning the candle actually went somewhere during that session [03:00]
- Sitting at a level where a trap actually makes sense [03:00]

### Entry trigger

**Step 1: Identify the Anchor Candle [02:30-03:30]**
"The anchor candle draws the map. The high is one target, the low is the other" [03:30-04:00]. Mark the high and low of the anchor candle.

**Step 2: Wait for the Sweep Candle [04:00-05:00]**
"It needs to spike outside the range and close back inside it. Spike above the high, close back inside. Setup is valid" [04:00]. The sweep must close back inside the anchor range—"The candle has to close back inside the range. That's the entire filter. No close, no trade" [05:00].

Note: The sweep does not always happen on the second candle [11:00]. It can happen on the third, fourth, or later candle, as long as no intervening candle closes beyond the anchor range [11:30].

**Step 3: Zoom to Lower Timeframe for Entry [05:30-07:00]**
"After the sweep candle closes back inside the range, zoom into a lower time frame. If you're trading a 1 hour setup, drop to the 15 minute" [05:30-06:00].

**Entry Methods on Lower Timeframe [06:00-06:30]:**

Option A: Supply/Demand Zone Entry
"You're looking for the trigger zone. My best option, a supply or demand zone, a place where price moved fast and left in a hurry" [06:00]. "Find the nearest one sitting between current price and the sweep level. Enter when price taps it" [06:00-06:30].

Option B: Break and Retest Entry
"If the zone isn't clean, I use the simplest entry model in trading, the break and retest" [06:00-06:30]. "On the lower time frame, after the sweep, price will often drop, break a short-term level, then pull back up to retest that same level before continuing lower. That retest is your entry" [06:00-06:30].

### Stop loss

Stop goes above the sweep high (for shorts) or below the sweep low (for longs) [06:30] / [07:30].

### Take profit / exit

"Target is the low of the original candle" (for shorts) [01:00] or "the high of the anchor candle" (for longs) [07:30].

Example: Bitcoin long setup, "First target is the high of the anchor candle. That's where candle range theory says the move is done. I take 50% off there and move my stop to break even. If price keeps going, I let it ride" [07:30-08:00].

### Invalidation / skip conditions

1. **Any candle between anchor and sweep closes beyond anchor range [11:30]:** "If candle three closes above the anchor high before the sweep happens, the structure is broken, walk away" [11:30].

2. **No candle closes beyond the range before sweep fires [11:00-11:30]:** Candles can chop inside the anchor range for multiple candles before the sweep fires without invalidating the setup. "If price just chops inside the range for a candle or two before the sweep fires, that's not a failed setup. That's a coiled one" [11:30].

3. **Market chopping with no trend [09:00]:** "If the market has been chopping sideways for days with no real direction, the sweeps mean nothing. There's no script running, just price wandering around like it lost its keys. No trend, no obvious level, no trade" [09:00].

4. **Obstruction between entry and target [10:00]:** "Before every trade, one question, is there anything between me and my target that could kill this move? If yes, skip it. The best setups have nothing in the way" [10:00-10:30].

### Claimed performance

No specific win rate or R-multiple claimed. Example trades shown:
- Bitcoin daily long: "That's my entry. My stop sits under the zone. First target is the high of the anchor candle" [07:30-08:00]. No result stated.
- Pound Dollar 4-hour short: "Short there, stop above the sweep high. Target is the low of the anchor candle" [08:30-09:00]. No result stated.

Historical note: "I used to trade the daily candle and didn't want to miss the move, so I ignored the close condition. Guess what? I missed the setup about 70% of the time. The other 30% I got lucky and convinced myself I was disciplined. I wasn't. I was just occasionally right for the wrong reason" [04:30-05:00].

### Vagueness log

1. "Decent size" for anchor candle: UNDEFINED-RULE (no ATR multiple, no pip threshold specified)
2. "Strong close": UNDEFINED-RULE (no definition of strong vs. weak close within the candle)
3. "Clear trend": UNDEFINED-RULE (how many candles constitute a trend?)
4. "Sweep high/low" exact price: VISUAL-ONLY (depends on wick precision)
5. "Supply or demand zone": VISUAL-ONLY (requires visual identification of where price "moved fast and left in a hurry")
6. "Nearest one sitting between current price and sweep level": UNDEFINED-RULE (no tolerance or distance metric)
7. "Break and retest": VISUAL-ONLY (requires visual level identification on lower timeframe)
8. Entry timing "when price taps": UNDEFINED-RULE (market order? limit order? at what exact price?)
9. "50% off at first target": mentioned in example [07:30] but not formalized as part of core strategy
10. Position sizing: NOT STATED
11. Risk-reward targets: NOT STATED

### Mechanizability

PARTIAL. The core pattern (anchor candle + sweep candle closing back inside) is computable from OHLCV data. However, several critical gaps prevent full automation:
- Identifying an "anchor candle" requires distinguishing "trend pullback" or "swing high/low" locations, which are inherently visual/subjective
- Identifying supply/demand zones is visual-only
- The "break and retest" entry requires identifying short-term levels on the lower timeframe, also visual
- No quantified thresholds for what constitutes "obstruction between entry and target"
A framework to identify valid anchor candle locations (support/resistance levels, trend context) must be defined before this becomes fully mechanizable.

## Additional Considerations

### Time Delay in Setup Formation
Contrary to typical CRT teachings, the sweep may not fire on the second candle [11:00-11:30]. Multiple candles can chop inside the anchor range before the sweep candle appears. "Every candle that sits inside the range adds more trapped positions near those levels. By the time the sweep finally fires, there's more fuel behind the move than an immediate sweep would ever have" [12:00].

### Filter: Lower Half vs. Upper Half Entry
"If I'm looking for a long, I prefer my lower time frame entry to happen in the lower half of the anchor candle. For shorts, I prefer my entry in the upper half. Better price, tighter stop, and cleaner reward" [10:00-10:30].

### Relationship to Larger Trend
"Every setup I showed you today ran in the same direction as the bigger trend. That wasn't a coincidence. CRT without the bigger picture is like knowing which room to enter, but not which building you're in" [12:00-12:30]. Speaker references another video on the "bigger picture" framework.

## Notable claims and caveats

- Fair value gaps (commonly taught in CRT) are dismissed as "a gimmick. Three candle gaps on a five-minute chart that disappear the moment you switch brokers because the data doesn't match" [05:15-05:30].
- The speaker emphasizes discipline: "If your entry needs three candles, four acronyms, and a seminar to explain it, you don't have an edge" [06:30-07:00].
- Trading the spike before the candle closes causes losses: "Most traders get chopped up. They see a spike, get excited, enter too early before the candle closes, and then watch price just keep going without them, or worse, going against them" [04:30].
- No mention of costs, spread, slippage, or commission.
- No mention of drawdown or losing streaks beyond the historical note about missing setups 70% of the time without proper candle close discipline.
- The strategy depends on larger market structure (trend, support/resistance levels) to be effective. Trading CRT in choppy markets is warned against.

## Video Classification Note

This is a complete STRATEGY with a clear mechanical framework (three-candle pattern identification and sweep condition). However, significant portions (anchor candle location identification, supply/demand zone finding, break-and-retest entry) depend on visual price action interpretation and are not fully computable without additional rules for level identification.
