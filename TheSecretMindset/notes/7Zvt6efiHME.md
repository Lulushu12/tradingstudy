# The 200 EMA Order Block Strategy That Quietly Prints Profits

- video_id: 7Zvt6efiHME
- url: https://www.youtube.com/watch?v=7Zvt6efiHME
- duration: 10:49
- classification: STRATEGY

## Summary

This video presents an order block trading strategy filtered by a 200 EMA channel. The key innovation is using the 200 EMA applied to highs and lows (rather than closes) to create a dynamic channel. Order blocks are only traded when they meet three mechanical conditions: (1) the order block zone touches or overlaps the EMA channel, (2) the move off the order block breaks prior swing structure, and (3) the zone is fresh (first test only). Entries are placed via limit orders at the edge of the confluent zone; stop losses are placed beyond the order block candle; take profits target a 2:1 reward-to-risk ratio. A directional filter restricts longs to price above the channel and shorts to price below the channel.

## Instruments and timeframes stated
- markets: NOT STATED (implied multi-instrument, equities or forex)
- timeframes: NOT STATED explicitly (charts shown but no timeframe specified)
- sessions/hours: NOT STATED

## Strategy 1: Order Block with 200 EMA Channel (Long and Short)

### Indicators and settings
- EMA Channel:
  - Upper band: 200-period EMA applied to highs [02:30-03:00]
  - Lower band: 200-period EMA applied to lows [02:30-03:00]
- Order block: the candle immediately before the directional move (last bearish candle for bullish OB, last bullish candle for bearish OB) [05:30-06:00]

### Context / bias filter
Directional filter [08:30]: "When price is above the channel, you only take longs. When it's below, shorts only."

[08:30] "This one filter alone removes half the bad trades you would have taken."

Price position relative to EMA channel determines bias: above = bullish only, below = bearish only.

### Entry trigger
Three mechanical conditions must ALL be met [03:30-07:00]:

**Rule 1: Touch the channel** [04:00]:
"the order block must touch or overlap the EMA channel. Not close to it, not near it. The actual zone has to make contact with the channel. If there's empty space between the order block and the channel, it doesn't qualify. This is black and white. Either it touches or it doesn't."

**Rule 2: Break of structure** [04:00-04:30]:
"the order block must cause a break of structure. Look at the move that resulted from the order block. Did it break a previous swing high or swing low? If yes, the order block is valid. If price just moved, but didn't break structure, that's not a real order block. That's just a candle. Skip it."

**Rule 3: Fresh** [04:30-05:00]:
"the order block must be fresh. This is the one most traders ignore. Every time price returns to a zone, it fills some of those pending orders. Test it twice, orders are gone. The zone is used up. You want first touch only. If price already came back and bounced, that was your chance. Don't expect it to work again."

Entry execution [07:00-07:30]:
"Your entry triggers when price enters your confluent zone. When a candle touches or enters the zone, you're in. Here's how I do it. I set a limit order at the edge of the zone, the common zone between the order block and the channel. For a bullish setup, I set it at top of the zone and at the bottom for a bearish setup. Price comes back. Order fills. I'm in at the best possible price."

### Stop loss
[08:00-08:30] "Stop loss goes beyond the order block candle. For longs, that means below the low. For shorts, above the high."

Longs: Below the low of the order block candle.
Shorts: Above the high of the order block candle.

### Take profit / exit
[08:00-08:30] "Targets are simple, two to one reward to risk. If your stop is 20 pips, your target is 40. Mechanical, no thinking required."

Take profit at 2:1 reward-to-risk: If stop loss is X pips away, target is 2X pips in profit direction.

### Invalidation / skip conditions
Any failure of the three mechanical rules [07:00]:
1. No touch of channel [04:00]
2. No break of structure from the move [04:00-04:30]
3. Order block already tested; not fresh [04:30-05:00]

[08:30] Skip if price direction conflicts with channel position (e.g., trading long when price is below channel).

[07:30-08:00] Price entering zone and continuing through (no bounce) is a loss, but acceptable: "Sometimes price enters your zone and keeps going. That's trading. No system works every time. But here's the thing, you're not trying to win every trade. You're trying to win over many trades."

### Claimed performance
NONE EXPLICITLY STATED. Implied positive edge via confluence concept and examples shown bouncing at zones [09:30]: "Watch price tap the zone and bounce. This is what happens when the rules align. You're not hoping, you're actually executing a system."

### Vagueness log
1. UNDEFINED-RULE: "Touch or overlap" [04:00] — degree of overlap/touch not specified (1 pip? 10 pips?)
2. UNDEFINED-RULE: "Break of structure" [04:00-04:30] — no quantified break distance (full reversal? Just beyond swing?)
3. UNDEFINED-RULE: "Fresh" [04:30-05:00] — "first touch" defined but what if price approaches but doesn't close through zone? Does it consume the setup?
4. UNDEFINED-RULE: "Last bearish/bullish candle" [05:30-06:00] — if multiple candles before move, which is "last"? Closest to move?
5. UNDEFINED-RULE: "Confluent zone" edge location [07:00-07:30] — top/bottom of zone but what if OB and channel only partially overlap?
6. UNDEFINED-RULE: "Swing high/low" for break-of-structure — relative to what timeframe? Intraday high/low?
7. SUBJECTIVE: Order block identification requires visual inspection of candle wicks and shapes (not algorithmically defined)

### Mechanizability
FULL (with stated parameters). The strategy is mechanizable:
- 200 EMA(highs) and 200 EMA(lows) calculation: Mechanizable
- Channel bounds defined: Mechanizable
- Order block identification: Requires defining "last candle before directional move" — candle identification can be automated with color/direction detection
- Rule 1 (touch channel): Mechanizable with overlap detection
- Rule 2 (break structure): Mechanizable with swing point detection (prior swing highs/lows)
- Rule 3 (fresh): Mechanizable by tracking zone test count
- Entry: Limit order at zone edge — mechanizable if zone bounds are defined
- Stop loss: Below/above OB candle low/high — mechanizable
- Take profit: 2:1 ratio from stop — mechanizable

The main assumption is that order block identification (the candle immediately before the directional move) is either manual or automated via trend/color change detection. With this clarification, the strategy is fully codable.

## Notable claims and caveats

- [00:00-00:30] "Order blocks are supposed to be the edge. You mark the zone. You wait for price and then take the trade. But you've done that and half the time price slices through like the zone meant nothing."
- [00:30-01:30] "I'm using it as a channel. And when an order block sits inside that channel, the probability isn't just good. It's scary good."
- [01:00-01:30] "Not all order blocks are equal. Some have institutional interest behind them. Some are just random candles that happen to precede a move. If you're trading every order block you see, you're gambling."
- [01:30-02:00] "A level where big players are watching" — implies institutional confluence theory
- [02:30-03:00] "Any order block that forms here isn't random. It's forming at a level with real interest behind it."
- [03:00-03:30] "Order block plus the 200 high low channel equals two reasons for price to react. That's not a guess. That's confluence. And confluence is where probability lives."
- [03:30-04:00] "There are three rules that separate high probability setups from garbage. Miss anyone and you skip the trade. No exceptions."
- [07:30-08:00] "No staring at charts, no second-guessing. The order does the work."
- [08:30] "This one filter alone removes half the bad trades you would have taken. Fight it and you're fighting the institutions. Don't do that."
- [07:30-08:00] "Sometimes price enters your zone and keeps going. That's trading. No system works every time. But here's the thing, you're not trying to win every trade. You're trying to win over many trades. This system stacks the odds and over time stacked odds pay."
- [09:00-09:30] "This is what happens when the rules align. You're not hoping, you're actually executing a system."

No mention of transaction costs, spread, slippage, or commission. No explicit drawdown or losing streak analysis. The speaker emphasizes the mechanical nature of the system ("no thinking required," "no exceptions") and the confluence theory. Cautions against trading every order block and stresses the importance of all three rules being met simultaneously.
