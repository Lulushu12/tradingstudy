# I Simplified Fair Value Gaps to One Profitable Strategy (FVG Trading Strategy)

- video_id: gOTFa4aNF04
- url: https://www.youtube.com/watch?v=gOTFa4aNF04
- duration: 28:54
- classification: MULTI-STRATEGY

## Summary

This video teaches Fair Value Gap (FVG) trading as a tool for identifying market imbalances where price moved so fast that certain price levels went untested. It presents the core FVG concept (gaps between candle shadows showing liquidity voids) then expands into multiple trading setups that combine FVGs with Break of Structure, supply/demand zones, premium/discount zones, and Fibonacci levels. The speaker emphasizes that FVGs alone are unreliable but gain strength when combined with other market structure elements.

## Instruments and timeframes stated

- markets: NOT STATED; references "all time frames" [02:30]
- timeframes: Shorter timeframes (more frequent gaps, less significance) [07:00-07:30]; 4-hour and daily (more impact, fewer gaps) [07:30]; 5-minute, hourly, 4-hour mentioned as examples [07:30, 26:30]; specific recommended timeframes NOT STATED
- sessions/hours: NOT STATED

## Strategy 1: Basic Fair Value Gap Return Trading

### Indicators and settings

- Fair Value Gap identification: three-candle pattern [03:00-03:30]
  - Bullish FVG: upper shadow of first candle does not touch lower shadow of third candle [03:00-03:30]
  - Bearish FVG: lower shadow of first candle does not touch upper shadow of third candle [03:30]
- Candle type: any timeframe; specific settings NOT STATED
- Confirmation pattern: bullish engulfing pattern at lower edge [12:00-12:30], long wick at upper edge of bearish gap [12:30]

### Context / bias filter

Fair value gaps represent liquidity voids where trading did not occur [03:30]. Gaps form when "big players make aggressive moves" [03:30]. Market structure context: bullish gaps often show up at support [04:30]; bearish gaps tend to form after a rise to resistance [04:30].

### Entry trigger

Wait for price to return to the gap before entering [08:00-08:30]. For a bullish setup, wait for price to return to the lower edge of the gap; if price bounces off this level, it signals a good entry point for a long trade [11:30-12:00]. For a bearish setup, watch for price to come back to the upper edge of the gap; if it struggles to break above this level, it might be a good spot to enter a short trade [12:00].

### Stop loss

Stop loss placement NOT STATED in the basic strategy section.

### Take profit / exit

Exit target NOT STATED. Implied: when the gap is "filled" (price tests the opposite side of the gap).

### Invalidation / skip conditions

Hundreds of fair value gaps appear every day on all timeframes [02:30]. If you trade every gap you see, you will "slowly burn" your account [02:30]. FVGs on their own do not give reliable signals [03:00]. Gaps might get filled quickly on shorter timeframes, requiring fast action [07:00-07:30].

### Claimed performance

NONE CLAIMED

### Vagueness log

1. UNDEFINED-PARAM: What constitutes the exact "edge" of a FVG for entry NOT DEFINED (upper shadow vs lower shadow vs wick endpoints)
2. UNDEFINED-RULE: How much wick overlap defines "no touch" – exact measurement NOT STATED [03:00-03:30]
3. UNDEFINED-RULE: What qualifies as a "bounce" from the gap level NOT DEFINED
4. UNDEFINED-PARAM: Gap "fill" completion – does price need to reach the opposite shadow or close at that level? NOT STATED
5. UNDEFINED-PARAM: Stop loss placement NOT SPECIFIED

### Mechanizability

PARTIAL – Fair value gap identification via candle shadow overlap can be mechanized once wick overlap thresholds are defined (currently missing). Entry on price return to gap is mechanizable. However, "bounce off" interpretation and confirmation via candlestick patterns require subjective judgment. The gap fill definition must be specified.

---

## Strategy 2: Fair Value Gap with Break of Structure

### Indicators and settings

- Fair value gap: as defined in Strategy 1 [03:00-03:30]
- Break of Structure: price runs through previous swing highs or lows with force [12:30-13:00]

### Context / bias filter

A break in market structure happens when price runs through previous swing highs or lows with force [12:30-13:00]. The break of structure must have a gap inside it to count as valid [12:30-13:30]. Picture the market moving up in higher highs and higher lows, then suddenly price drops hard through a previous swing low [13:00-13:30]. This combination is powerful because it shows: (1) the market structure break tells us the trend is changing [13:30], (2) the gap shows us exactly where big players left their footprint [13:30-14:00].

### Entry trigger

After spotting the break in structure and gap, don't chase the initial move [15:30-16:00]. The best trades come when price revisits the fair value gap level and shows clear reaction [16:00]. For a buy signal: look for a clear break of previous swing highs, check for a gap forming during this break, then wait for price to return to the fair value gap level [15:00-15:30]. Watch how price reacts when it hits the zone [15:30].

### Stop loss

Stop loss placement NOT STATED. Implied: beyond the break of structure level.

### Take profit / exit

Exit when the structure break is confirmed and gap is filled.

### Invalidation / skip conditions

The break in structure must be "clean and strong" [14:30]. Three conditions must be met: (1) the break in structure is clean and strong, (2) the fair value gap forms right at the point where structure breaks, (3) price moves away quickly after creating the gap [14:30-15:00]. If these conditions are not all met, the setup is weakened or invalidated.

### Claimed performance

NONE CLAIMED

### Vagueness log

1. UNDEFINED-RULE: What constitutes a "break" of swing highs/lows – exact distance past the level NOT STATED
2. UNDEFINED-RULE: "Clean and strong" break – measurement criteria NOT DEFINED [14:30]
3. UNDEFINED-RULE: "Moves away quickly" – speed or distance NOT SPECIFIED [15:00]
4. VISUAL-ONLY: Identifying previous swing highs/lows requires visual chart inspection [12:30]
5. UNDEFINED-PARAM: Stop loss placement NOT SPECIFIED

### Mechanizability

PARTIAL – Swing point detection is mechanizable via local extrema. Structure break detection can be coded once "clean" and "strong" are quantified (currently vague). Gap formation during the break is mechanizable. However, invalidation criteria require subjective judgment.

---

## Strategy 3: Fair Value Gap with Supply and Demand Zones

### Indicators and settings

- Fair value gap: as per Strategy 1 [03:00-03:30]
- Supply zones: areas where price moves down fast [17:30-18:00]
- Demand zones: areas where price moves up from [17:30-18:00]

### Context / bias filter

The strategy works through a simple market truth: price wants to trade where it hasn't traded before [17:00]. Gaps represent prices where little to no trading happened [17:00]. When a fair value gap sits near supply or demand zones, you've spotted a place where institutional traders showed their hand twice [16:30-16:45]: first building positions, then moving price fast enough to leave a gap [16:30-16:45]. Price builds up in a supply or demand zone, then moves explosively, creating the gap [17:00-17:30]. This fast move shows institutional conviction [17:30].

### Entry trigger

First, you'll see price moving normally. Then suddenly, a large candle appears with no overlap to nearby candles – that's the gap [17:00]. If this happens near a supply or demand zone, pay extra attention [17:00]. Wait for price to return to the FVG area [17:30]. Watch how it reacts when it hits the zone [17:30]. Strong moves often follow once the gap starts filling [17:30-18:00]. Combined with a supply or demand zone, the trader "doesn't mind if price completely fills the gap, and even moves past it" [18:00-18:30]. Always wait for it to return to the origin point, to the demand zone [18:00-18:30].

### Stop loss

Stop loss placement NOT STATED. Implied: beyond the zone level.

### Take profit / exit

Exit when price returns to the origin zone or when the gap is fully filled.

### Invalidation / skip conditions

If the gap does not occur near a supply/demand zone, signal is weaker. Multiple factors increase setup strength: zone location, gap presence, break in structure, and clear price action [21:30-22:00].

### Claimed performance

NONE CLAIMED

### Vagueness log

1. VISUAL-ONLY: Supply and demand zones require visual identification and marking on chart [17:00-17:30]
2. UNDEFINED-PARAM: Zone size/width NOT DEFINED; what constitutes "near" a zone NOT SPECIFIED
3. UNDEFINED-RULE: How to quantify "strong" price reaction [17:30]
4. UNDEFINED-RULE: "Institutional conviction" shown by gap – measurement criteria NOT STATED
5. UNDEFINED-PARAM: Stop loss placement NOT SPECIFIED

### Mechanizability

DISCRETIONARY – Gap identification is mechanical. However, identifying and validating supply/demand zones is discretionary and chart-dependent. Price reaction interpretation requires subjective judgment. The combination setup is only as strong as zone identification, which is subjective.

---

## Strategy 4: Fair Value Gap in Premium and Discount Zones

### Indicators and settings

- Fair value gap: as per Strategy 1
- Premium zone: above equilibrium (50% level between swing highs and lows) [20:00-20:30]
- Discount zone: below equilibrium [20:00-20:30]
- Equilibrium: 50% point between recent swing highs and lows [20:00]

### Context / bias filter

Market makers work in specific ways at premium/discount zones [19:30]. In discount zones, they start buying [19:30]. In premium zones, they start selling [19:30]. After big market moves, most traders chase the trend, but smart money does the opposite – they expect a pullback before the next move [20:30]. These pullbacks often happen right at fair value gaps in premium or discount areas [20:30].

### Entry trigger

You need to see the bigger picture first [19:30-20:00]. Look at the total range of the larger price move [20:00]. Find where price sits compared to recent highs and lows [20:00]. Then spot the reference points market makers watch – the fair value gaps and liquidity voids [20:00]. In premium areas with a fair value gap, look for selling pressure [21:00]. In discount areas with gaps, watch for buying pressure [21:00]. Watch how price behaves in these zones [21:00]. The mix of zone location and the gap creates stronger signals [21:00-21:30].

### Stop loss

Stop loss placement NOT STATED. Implied: beyond the opposite zone boundary.

### Take profit / exit

Exit when price reverses or breaks through the zone.

### Invalidation / skip conditions

True breaks in structure often leave gaps behind; these gaps confirm the break's strength [21:30]. When they form in premium or discount zones, they show even more power [21:30]. Market makers accumulate in discount zones and distribute in premium zones [21:30-22:00]. Again, the best trades come when multiple factors line up – zone location, gap presence, break in structure, and clear price action [21:30-22:00].

### Claimed performance

NONE CLAIMED

### Vagueness log

1. UNDEFINED-PARAM: Equilibrium calculation – is it simple midpoint or using volume-weighted methods? NOT STATED [20:00]
2. UNDEFINED-RULE: What constitutes "selling pressure" vs "buying pressure" NOT DEFINED [21:00]
3. UNDEFINED-RULE: How far must price move to "break through" the zone NOT SPECIFIED
4. UNDEFINED-RULE: Zone width/boundaries for premium/discount designation NOT DEFINED

### Mechanizability

PARTIAL – Equilibrium calculation is mechanizable (midpoint between swing extremes). Gap identification is mechanical. However, pressure interpretation ("buying" vs "selling") requires subjective judgment. Zone boundary definitions are missing.

---

## Strategy 5: Fair Value Gap with Fibonacci Confluence

### Indicators and settings

- Fair value gap: as per Strategy 1
- Fibonacci levels: drawn from highest high to lowest low in recent price action [24:00-24:30]
- Key Fibonacci zones: 50% to 61% zone called "golden zone" [23:00-23:30]
- Recommended timeframes: 4-hour and hourly charts [26:30]

### Context / bias filter

Fibonacci levels match natural market moves [23:00]. When they line up with Fair Value Gaps, they create strong trade opportunities [23:00]. The "golden zone" between 50% and 61% Fibonacci levels attracts smart money attention [23:00-23:30]. When a gap sits in this area, you've found a place where two powerful forces meet [23:30].

### Entry trigger

In an uptrend, look for gaps that line up with Fibonacci levels for buying opportunities [24:00]. In a downtrend, search for gaps matching Fibonacci levels for selling chances [24:00]. The real power comes from understanding what these confluences mean [24:30-25:00]. Wait for price to reach the Fibonacci level, where your gap sits [26:00]. Look for signs that price respects both the level and the gap [26:00]. The best trades come when price pierces the confluence zone, and rejects it with a strong candlestick signal [26:00-26:30]. Look mainly for candles with large wicks, or engulfing patterns [26:00-26:30].

### Stop loss

Stop loss placement NOT STATED.

### Take profit / exit

Exit when price moves away from the confluence zone or trend reversal occurs.

### Invalidation / skip conditions

Markets rarely turn exactly at a specific price [28:00]. Instead, they often react within a zone [28:00]. Give trades room to breathe by thinking in zones, rather than exact prices [28:00]. The better timeframes are 4-hour and hourly charts [26:30].

### Claimed performance

NONE CLAIMED

### Vagueness log

1. UNDEFINED-PARAM: Fibonacci levels drawn from which timeframe swing extremes NOT SPECIFIED [24:00-24:30]
2. UNDEFINED-RULE: What constitutes "lining up" – price proximity to Fibonacci level NOT DEFINED (e.g., within X pips/points)
3. UNDEFINED-PARAM: Golden zone width – is it exactly 50%-61% or a range around those levels? NOT SPECIFIED [23:00-23:30]
4. UNDEFINED-RULE: What constitutes "strong candlestick signal" – exact wick length or pattern NOT DEFINED [26:00-26:30]
5. UNDEFINED-PARAM: Zone size for confluence – exact width in price NOT SPECIFIED [28:00]
6. UNDEFINED-RULE: Stop loss placement NOT SPECIFIED

### Mechanizability

PARTIAL – Fibonacci levels can be calculated mechanically from swing extremes. Gap identification is mechanical. However, "lining up" proximity threshold is undefined, golden zone boundaries require clarification, and candlestick signal confirmation criteria lack specificity. Zone-based thinking reduces mechanical precision.

---

## Notable claims and caveats

- **"There are hundreds of fair value gaps every day, on all time frames"** [02:30]. "If you trade every gap you see, you'll slowly burn your account" [02:30]. This is a critical caveat: FVGs alone are unreliable.

- "On their own, they don't give reliable signals. They work with other market signs to give a full picture" [03:00]. This is emphasized repeatedly: FVGs must be combined with other confirmation elements.

- "Fair value gaps will help you see the market's 'memory'. It remembers these gaps and often comes back to them" [02:30-03:00]. Market has a magnetic pull back to gap levels.

- "The return to this area often shows clear price action signals. You might see price slow down as it approaches the gap, or notice smaller timeframe consolidation patterns forming" [11:00-11:30].

- On shorter timeframes, gaps are more frequent but less significant; they can be filled quickly so you need to be fast to act [07:00-07:30].

- On longer timeframes (4-hour, daily), gaps are fewer but have more impact and can influence price movements for several days [07:30].

- "Price is fractal. Patterns that appear on monthly charts can also be seen on daily or even 5-minute charts" [07:30-08:00].

- The speaker uses "multiple timeframe analysis" – spots a gap on higher timeframe, marks the zone, but zooms to lower timeframe to fine-tune entry/exit [07:30-08:00].

- Market makers must find fair value for their positions and use gaps as reference points [09:00-09:30].

- Balancing of market imbalance happens for 3 reasons: (1) market makers need to fill unfilled orders, (2) other traders spot the imbalance, (3) market naturally seeks equilibrium [09:30-10:00].

- **No mention of costs, spreads, slippage, or commissions.**

- **No mention of drawdown or losing streaks.**

- **No win rate or performance statistics claimed for any strategy variation.**

- The video emphasizes confluence and context: "Again, the best trades come when multiple factors line up – zone location, gap presence, break in structure and clear price action" [21:30-22:00].
