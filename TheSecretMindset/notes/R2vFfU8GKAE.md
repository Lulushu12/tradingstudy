# I Unlocked The Most Accurate Price Action Course For Heikin Ashi Traders (Best Strategy)

- video_id: R2vFfU8GKAE
- url: https://www.youtube.com/watch?v=R2vFfU8GKAE
- duration: 29:16
- classification: MULTI-STRATEGY

## Summary

This video teaches price action analysis using Heiken Ashi candles, which smooth price data to filter noise and make trends clearer. It covers identifying uptrends (green candles with small lower wicks) and downtrends (red candles with small upper wicks), reading market structure through swing highs/lows, and identifying support/resistance levels. Multiple trading applications are demonstrated: supply and demand zone bounces, volume confirmation of moves, and combining Heiken Ashi with moving averages for additional confirmation.

## Instruments and timeframes stated

- markets: NOT STATED
- timeframes: NOT STATED (mentions "higher time frames" for more important levels but no specific periods)
- sessions/hours: NOT STATED

## Strategy 1: Supply and Demand Zone Trading with Heiken Ashi

### Indicators and settings

- Heiken Ashi candles: (standard calculation, no adjustable parameters mentioned)
- Volume indicator: (used qualitatively, no settings specified)

### Context / bias filter

Zone must be "fresh" (not yet tested by price return) for strongest signals [16:30-17:00]. Zones should be near current price [17:30-18:00]. Mark no more than 3 to 5 zones at a time to keep chart clean [17:00-17:30]. Identify zones by looking for big, bold Heiken Ashi candles where price "left in a hurry" [18:00-18:30]. For long trades, find demand zones (where buyers overpowered sellers); for shorts, find supply zones (where sellers took control) [15:15-15:30].

### Entry trigger

For buy: "wait for price to touch a demand zone, and bounce up with a green Heiken Ashi candle. Ideally, this candle won't have a lower wick" [19:15-19:30]. For sell: "look for price to hit a supply zone, and bounce down with a red Heiken Ashi candle. A candle with no upper wick is better" [19:30-19:45].

### Stop loss

"Place your stop loss just below the demand zone for buy trades, or just above the supply zone for sell trades" [19:45-20:00].

### Take profit / exit

"Hold it until price reaches the opposite type of zone. So if you bought at a demand zone, you'd aim to sell when price hits the next supply zone up" [19:45-20:15]. Alternatively, "close part of your trade when you see the candles change color, signaling a potential shift in momentum" [19:45-20:00].

### Invalidation / skip conditions

NOT STATED explicitly. Implied: if zone has been tested multiple times, it weakens with each test [14:00-14:30]. Used-up zones (price bounced off them several times) are "not great for big trades" [17:00-17:30].

### Claimed performance

NONE CLAIMED (no win rate, drawdown, or profit figures given)

### Vagueness log

1. UNDEFINED-PARAM: "Big, bold Heiken Ashi candles" - no quantitative definition of size or boldness
2. UNDEFINED-PARAM: Zone identification based on visual inspection of where "price left in a hurry" - speed of exit not quantified
3. UNDEFINED-PARAM: "Ideally, this candle won't have a lower wick" - not a hard requirement, and wick size threshold is not stated
4. UNDEFINED-RULE: "Fresh zones are better" - freshness is ordinal (1st touch, 2nd touch, etc.) but decay formula is subjective
5. SUBJECTIVE: Determination of supply vs demand zone origin point requires visual chart inspection; the "beginning" of the move is not mechanically defined
6. VISUAL-ONLY: Identifying zones requires seeing chart and recognizing "structure" and move initiation visually, not from price data alone
7. UNDEFINED-PARAM: Zone width (upper/lower bounds of the zone) is not specified

### Mechanizability

PARTIAL - The skeleton is computable (find local swing highs/lows, mark zones, wait for reversals), but zone identification, width definition, and the distinction between "fresh" and "used" zones require subjective visual judgment or heuristics not stated by the speaker.

---

## Strategy 2: Support and Resistance with Heiken Ashi Markers

### Indicators and settings

- Heiken Ashi candles: (standard)
- Support/Resistance levels: (identified visually from prior price action)

### Context / bias filter

In uptrends, "old broken highs tend to act as support" [09:45-10:00]. In downtrends, "old broken lows often act as resistance" [09:45-10:00]. Price approaches support or resistance level.

### Entry trigger

"When candles change their color and form wicks, it often happens at support or resistance" [11:30-12:00]. Buy: "red candles turn green at support. This shows buyers stepping in" [11:45-12:00]. Sell: "green candles turn red at resistance. This shows sellers taking control" [12:00-12:15]. Optimal: "long lower wick on a green candle, at support, shows strong buying. A long upper wick on a red candle, at resistance, shows strong selling" [12:00-12:30].

### Stop loss

For buy at support: place below the support level. For sell at resistance: place above the resistance level (implied from structure).

### Take profit / exit

NOT STATED - no explicit exit rule given for this setup.

### Invalidation / skip conditions

"False breakouts" can occur: "you might see a candle break past support or resistance, but with a long wick pointing back into the range. This could be a fake out" [13:30-14:00]. "In this case, you wait for more candles to confirm the break" [13:45-14:00].

### Claimed performance

NONE CLAIMED

### Vagueness log

1. UNDEFINED-PARAM: "Support and resistance aren't exact prices. They're more like zones" [13:45-14:00] - zone width not specified
2. VISUAL-ONLY: Support and resistance levels are identified visually from prior price action, not mechanically computed
3. UNDEFINED-PARAM: Color change timing relative to level crossing is not defined; candles may change color "near a level, not exactly at it" [13:45-14:00]
4. UNDEFINED-RULE: What constitutes "strong buying pressure" vs normal green candle not specified beyond "long lower wick"
5. SUBJECTIVE: Determining when a level has been "held" or "broken" requires visual inspection of price proximity to level

### Mechanizability

PARTIAL - Support and resistance can be identified algorithmically (prior swing highs/lows), and candle color is computable, but proximity threshold ("near a level") and confirmation criteria ("wait for more candles") are not quantified.

---

## Strategy 3: Moving Average + Heiken Ashi Combination

### Indicators and settings

- Moving averages: "fast and slow" mentioned [28:15-28:30], but period lengths: NOT STATED
- Heiken Ashi candles: (standard)

### Context / bias filter

"First, you see the trend from moving averages. Then, you evaluate the momentum from Heiken Ashi" [24:45-25:00]. Trend direction: "When price stays above a moving average, it's likely an uptrend. If it's below, it's probably a downtrend" [25:00-25:30].

### Entry trigger

"When price crosses a moving average, it could mean the trend is shifting" [25:45-26:00]. "If the candles don't show a clear trend change, after crossing the moving average, it might be a false signal" [27:15-27:30]. Pullbacks: "In strong trends, price often pulls back to the moving average before continuing. This can be a good entry point" [27:30-28:00]. "When they start showing strong trend candles again, it might be time to enter" [28:00-28:15].

### Stop loss

NOT STATED explicitly (implied: beyond the moving average or prior swing)

### Take profit / exit

NOT STATED

### Invalidation / skip conditions

Whipsaw: "price might briefly cross a moving average but not start a new trend. This is called a whipsaw. Heiken Ashi candles can help avoid these false signals" [27:00-27:30].

### Claimed performance

NONE CLAIMED

### Vagueness log

1. UNDEFINED-PARAM: Moving average periods NOT STATED - "fast and slow" is relative
2. UNDEFINED-RULE: "Clear trend change" in Heiken Ashi candles not defined; color change alone is ambiguous
3. UNDEFINED-PARAM: Pullback depth and reversion to moving average timing not quantified
4. SUBJECTIVE: Determining when candles show "strong trend" vs "weak trend" is qualitative
5. UNDEFINED-RULE: Whipsaw avoidance criteria based on visual inspection of subsequent candles, not a stated rule

### Mechanizability

PARTIAL - Moving average crossovers are computable, but the critical rule ("Heiken Ashi candles must show a clear trend change") is not mechanically defined. Entry on pullback to MA requires threshold definition.

---

## Notable claims and caveats

The speaker notes that Heiken Ashi candles "lag behind real-time price movements" [02:30-02:45], making them "great for finding trends" but "might not be the best tool for pinpointing exact entry and exit points for trades" [02:30-02:45]. 

Heiken Ashi "doesn't show gaps between trading sessions" which can be "both an advantage and a disadvantage, depending on your trading style" [03:00-03:30]. Recommends using Heiken Ashi "in combination with traditional candlestick charts" for gap-sensitive markets like stocks or forex [03:15-03:30].

The speaker does NOT discuss transaction costs, slippage, commission, or spread implications. No discussion of drawdown, losing streaks, or market conditions where the strategy fails. The video frames Heiken Ashi as a "noise filter" [00:30] but does not quantify which noise is removed or under what market conditions the filter breaks down.
