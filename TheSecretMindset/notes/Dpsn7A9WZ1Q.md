# The Complete RENKO Trading Strategy For Scalping & Day Trading

- video_id: Dpsn7A9WZ1Q
- url: https://www.youtube.com/watch?v=Dpsn7A9WZ1Q
- duration: 26:37
- classification: MULTI-STRATEGY

## Summary

This video explains Renko chart fundamentals and presents multiple trading strategies adapted to price-action-based Renko bars. It covers how Renko charts filter noise by plotting only when price moves a fixed amount, then details various entry and exit approaches including breakouts, pullbacks, supply/demand zones, pivot points, and channel trading. The video emphasizes that brick size selection is critical and that multiple timeframe confirmation reduces false signals.

## Instruments and timeframes stated

- markets: Currency pairs (pips mentioned), stocks (dollar amounts mentioned); NOT STATED specifically which instruments recommended
- timeframes: Intraday (scalping, day trading mentioned at [00:00]); multi-timeframe analysis mentioned [14:30]; daily chart for bigger swings [14:30]; specific timeframe settings NOT STATED
- sessions/hours: NOT STATED

## Strategy 1: Price Action – Trend Following with Color Flips

### Indicators and settings

- Renko brick size: Fixed size examples given ($0.10-$0.20 for stocks, 5-10 pips for currency pairs) [06:30], OR ATR-based dynamic sizing [07:00]; exact period for ATR NOT STATED
- Brick display: wicks optional [08:00]; no specific setting recommended

### Context / bias filter

Look for a series of consecutive bricks of the same color representing a trending condition [09:00]. A series of 4-5 green bricks in a row signals a strong bullish push [09:00]. Identify the broader trend direction using a larger-brick Renko chart or daily chart [14:30].

### Entry trigger

Enter on small pullbacks within an established uptrend [09:00-09:30]. When you see green bricks dominating, wait for one or two red bricks forming as a pullback, then enter on the next green brick [19:30-20:00]. Watch for a color flip from red to green bricks near a demand zone [20:30].

### Stop loss

Place stop "a few bricks behind your entry" [23:00]. If going long on a green brick above resistance, "tuck your stop behind the last red brick" [23:00]. Number of bricks for stop NOT SPECIFIED.

### Take profit / exit

Exit when color changes to red [23:30]. Alternatively, trail stop by "a certain number of bricks" as price moves in your favor [23:00]; specific number NOT STATED. Exit when bricks break below a channel boundary [25:30].

### Invalidation / skip conditions

Skip trading if the range is too narrow [11:00]. Pass on the trade if the big-brick Renko has not reversed color but the small-brick chart indicates a short signal [15:30]. If the setup breaks below support line drawn at swing low, consider the pattern invalidated [22:00].

### Claimed performance

NONE CLAIMED

### Vagueness log

1. UNDEFINED-PARAM: "Small pullback" size not quantified
2. UNDEFINED-PARAM: Number of bricks for stop loss ("a few bricks")
3. UNDEFINED-PARAM: ATR period for dynamic brick sizing NOT STATED
4. UNDEFINED-RULE: "A few bricks behind entry" is vague for exact stop placement
5. UNDEFINED-PARAM: Trail stop increment ("by a certain number of bricks")
6. UNDEFINED-RULE: How to determine "too narrow" for a range

### Mechanizability

PARTIAL – The basic framework (consecutive same-color bricks = trend, opposite color flip = reversal) is mechanically identifiable from OHLCV. However, determining optimal brick size, "appropriate" pullback size, and stop loss placement requires assumptions. Entry and exit signals can be coded, but the confidence rules are subjective.

---

## Strategy 2: Breakout from Consolidation/Range

### Indicators and settings

- Renko chart: brick size as per Strategy 1
- Consolidation identification: mark the highest up-brick and lowest down-brick within a region [11:00]

### Context / bias filter

Market is in a consolidation phase with alternating up and down bricks staying within a horizontal band [10:30-11:00]. Price fails to exit a defined "box" or "range" for a period [11:00].

### Entry trigger

Wait for a multi-brick consolidation, then enter on the brick that closes beyond the range [19:00-19:30]. If bricks move sideways around a specific level, entry is on the green brick that closes above that zone for a bullish breakout [19:00-19:30]. A breakout brick closing beyond the range signals potential bullish momentum [19:00].

### Stop loss

Stop placement NOT STATED for this strategy specifically. Assume placement below the consolidation range (implied from context) [11:00].

### Take profit / exit

Hold for a bigger wave following the breakout [19:00]. Exit when momentum fades or price returns to the breakout level [19:30].

### Invalidation / skip conditions

If you see no major supply zone close by the breakout, the move might run further [19:30]. If bricks quickly retreat into the range, the breakout is false [22:30].

### Claimed performance

NONE CLAIMED

### Vagueness log

1. UNDEFINED-PARAM: What constitutes "sideways" bricks duration NOT STATED
2. VISUAL-ONLY: "Highest up-brick and lowest down-brick" requires visual marking on chart [11:00]
3. UNDEFINED-RULE: When does a consolidation "persist" long enough for trade NOT STATED
4. UNDEFINED-PARAM: Stop loss placement not specified
5. UNDEFINED-RULE: What qualifies as a "major supply zone" NOT DEFINED

### Mechanizability

PARTIAL – Consolidation can be identified by alternating brick colors within a price range. Breakout above/below range can be coded. However, confirmation via supply/demand zones and determining when consolidation "ends" requires subjective judgment. The strategy skeleton is mechanizable but requires zone identification assumptions.

---

## Strategy 3: Pullback Entry in Uptrend

### Indicators and settings

- Renko chart with appropriate brick size

### Context / bias filter

Established uptrend: series of green bricks [19:30]. A strong bullish move has been in progress [19:30].

### Entry trigger

Watch for a series of green bricks, then watch for one or two red bricks forming as a pullback [19:30]. Entry on the next green brick appearing, potentially near a demand zone or moving average [19:30-20:00].

### Stop loss

Stop loss NOT SPECIFIED. Implied: below the pullback lows or below the last significant low [19:30].

### Take profit / exit

Hold as the trend resumes [19:30]. Exit on reversal or color flip to red bricks.

### Invalidation / skip conditions

If the pullback exceeds 2-3 red bricks and momentum continues downward, the uptrend may be broken [12:00].

### Claimed performance

NONE CLAIMED

### Vagueness log

1. UNDEFINED-PARAM: Pullback size ("one or two red bricks") is relative
2. UNDEFINED-RULE: How many red bricks before the trend is considered broken NOT STATED
3. UNDEFINED-PARAM: Stop loss placement not specified

### Mechanizability

PARTIAL – Uptrend identification and pullback detection (color flip) are mechanizable. However, determining "acceptable" pullback depth and entry confirmation timing requires rule assumptions.

---

## Strategy 4: Supply and Demand Zone Trading

### Indicators and settings

- Renko chart for zone identification
- Supply zones: drawn from areas of fast downward brick moves [17:30]
- Demand zones: drawn from areas of strong upward brick moves [17:30]

### Context / bias filter

Price has previously moved rapidly from a zone, leaving a cluster of bricks [17:30]. The zone acts as either support (demand) or resistance (supply) [17:30].

### Entry trigger

Watch for bricks approaching a known supply or demand zone [17:30]. If bricks reach the supply zone and flip from green to red, that might be a short signal [20:30]. If bricks drop to a demand zone and flip from red to green, that might be a long signal [20:30]. Some traders set entry one brick beyond the flip [20:30], others wait for two bricks to confirm [20:30].

### Stop loss

Stop loss placement NOT STATED. Implied: beyond the opposite side of the zone.

### Take profit / exit

Hold position as the zone holds as support/resistance [17:30]. Exit when price decisively breaks through the zone.

### Invalidation / skip conditions

If price stalls near a zone but does not flip color, the zone may not be valid [17:30]. If price consolidates near a zone without clear directional intent, skip the trade [18:00].

### Claimed performance

NONE CLAIMED

### Vagueness log

1. VISUAL-ONLY: Supply and demand zones require visual identification on chart; exact price levels not defined mechanically [17:30]
2. UNDEFINED-PARAM: "One brick beyond the flip" vs "two bricks to confirm" – which to use NOT SPECIFIED [20:30]
3. UNDEFINED-RULE: How to distinguish a valid zone from noise NOT STATED
4. UNDEFINED-PARAM: Zone width/boundaries not defined

### Mechanizability

DISCRETIONARY – While brick identification is mechanical, identifying and drawing supply/demand zones is discretionary and chart-dependent. Price action at zones is mechanizable, but zone validity requires subjective judgment.

---

## Strategy 5: Candlestick Patterns Adapted to Renko

### Indicators and settings

- Renko chart without wicks preferred for clean patterns [20:30-21:00]

### Context / bias filter

Renko bricks near a supply or demand zone gain weight in pattern confirmation [21:00-21:30].

### Entry trigger

Observe quick color flips that mimic bullish or bearish pin bars [21:00]. One color brick quickly replaced by the other color brick with a wick signals a reversal [21:00-21:30]. A long upper wick might reflect strong selling pressure at resistance [21:00-21:30]. A long lower wick can hint that buyers stepped in at support [21:00].

### Stop loss

Place stop beyond the opposite extreme of the pattern wick [21:30].

### Take profit / exit

Exit when the pattern fails to confirm reversal.

### Invalidation / skip conditions

A tiny wick indicates only a small hesitation, not a major shift [21:30]. No wicks can reflect a clean, forceful run with strong momentum [21:30], suggesting the original direction continues.

### Claimed performance

NONE CLAIMED

### Vagueness log

1. UNDEFINED-RULE: What constitutes a "long" wick vs "tiny" wick NOT DEFINED in measurement units
2. VISUAL-ONLY: Pin bar and engulfing pattern identification depends on visual inspection [21:00]
3. UNDEFINED-PARAM: Minimum wick length for signal NOT STATED
4. UNDEFINED-RULE: How many bricks must reverse to confirm the pattern NOT STATED

### Mechanizability

PARTIAL – Wick presence and direction are mechanizable. However, "long" vs "short" wick is undefined, and pattern significance depends on zone proximity (discretionary). Threshold definitions required for automation.

---

## Strategy 6: Support and Resistance Line Breakout

### Indicators and settings

- Renko chart
- Horizontal lines drawn at swing highs or lows [22:00-22:30]

### Context / bias filter

Repeated attempts to break a horizontal level at the same brick level form a line [22:00].

### Entry trigger

Wait for a decisive move beyond the horizontal line [22:00]. If multiple bricks reverse color at the exact line, that detail confirms a breakout or false break [22:00-22:30].

### Stop loss

Stop placement NOT STATED. Implied: on opposite side of the line.

### Take profit / exit

Exit when price retreats back below the line.

### Invalidation / skip conditions

A false break shows a single brick trying to push beyond the line, but the next brick forms back in the old range [22:30].

### Claimed performance

NONE CLAIMED

### Vagueness log

1. VISUAL-ONLY: Drawing support/resistance lines requires visual identification [22:00]
2. UNDEFINED-RULE: "Repeated attempts" at a level – how many constitutes a valid line NOT STATED
3. UNDEFINED-PARAM: How far must price move beyond the line to confirm breakout NOT STATED

### Mechanizability

DISCRETIONARY – Identifying levels where price "repeatedly" reversed requires visual chart inspection. A support/resistance detector could be built with swing point detection, but line validity remains subjective.

---

## Strategy 7: Pivot Point Trading

### Indicators and settings

- Pivot levels: daily or weekly pivot lines [22:30-23:00]
- Specific pivot calculation method NOT STATED

### Context / bias filter

Bricks respect those lines [22:30].

### Entry trigger

If bricks hover near an "R1" pivot, wait for a color flip for a short [22:30]. If bricks push above main pivot, hold a bullish view [23:00].

### Stop loss

Stop placement NOT STATED.

### Take profit / exit

Exit when price moves away from the pivot level.

### Invalidation / skip conditions

If bricks do not respect the pivot, the level is not valid [22:30].

### Claimed performance

NONE CLAIMED

### Vagueness log

1. UNDEFINED-PARAM: Pivot calculation method (standard, Camarilla, Woodie, etc.) NOT STATED
2. UNDEFINED-RULE: How to determine if bricks "respect" a level NOT DEFINED
3. UNDEFINED-PARAM: Entry trigger timing relative to pivot level not quantified

### Mechanizability

PARTIAL – Pivot levels can be calculated mechanically if the method is specified (currently NOT STATED). Color flip and proximity to pivot are mechanizable, but "respecting a level" requires threshold definition.

---

## Strategy 8: Divergence Trading with Oscillators

### Indicators and settings

- Oscillator: RSI mentioned [14:00], or similar momentum indicator; parameters NOT STATED
- Renko chart

### Context / bias filter

A streak of bricks making new highs/lows while indicator does not [23:30].

### Entry trigger

If bricks make new highs but the oscillator does not, momentum is declining and a color flip is expected soon [23:30]. Short when bricks turn red right as RSI is below its 50-level [14:00].

### Stop loss

Stop placement NOT STATED.

### Take profit / exit

Exit when the divergence resolves or price reverses.

### Invalidation / skip conditions

Divergences can show momentum loss but do not guarantee immediate reversal [23:30].

### Claimed performance

NONE CLAIMED

### Vagueness log

1. UNDEFINED-PARAM: RSI period NOT STATED; default 14 assumed but not confirmed
2. UNDEFINED-RULE: What constitutes a "new high" or "new low" – over what period NOT STATED
3. UNDEFINED-RULE: How significant must the divergence be to trade NOT DEFINED
4. SUBJECTIVE: Divergence interpretation is inherently subjective

### Mechanizability

PARTIAL – Divergence detection is mechanizable if parameters are defined (currently missing). However, divergence significance and trade timing remain subjective.

---

## Strategy 9: Channel Trading

### Indicators and settings

- Renko chart
- Channel: upward channel around bricks forming higher highs and higher lows [25:30]

### Context / bias filter

Bricks form a consistent pattern of higher highs and higher lows [25:30].

### Entry trigger

Ride the trend within the channel [25:30].

### Stop loss

Exit when price breaks below the channel boundary with a red brick [25:30].

### Take profit / exit

Exit when bricks break outside the channel [25:30]. Or look for a brand-new trade in the opposite direction [25:30].

### Invalidation / skip conditions

If channel lines are broken, the established trend has ended [25:30].

### Claimed performance

NONE CLAIMED

### Vagueness log

1. VISUAL-ONLY: Drawing channel lines requires visual inspection [25:30]
2. UNDEFINED-RULE: How many bricks are needed to establish a channel NOT STATED
3. UNDEFINED-PARAM: Channel slope sensitivity NOT DEFINED

### Mechanizability

PARTIAL – Channel detection can use trend line fitting on swing highs/lows. Breakout identification is mechanical. However, channel establishment period is undefined.

---

## Strategy 10: Area-Based/Range Trading with Breakout

### Indicators and settings

- Renko chart
- Consolidation area: mark where price consolidated [24:30]

### Context / bias filter

Price has consolidated in a defined area [24:30].

### Entry trigger

Wait for either a breakout or a bounce from that range [24:30]. If bricks break the top side, go long [24:30]. If bricks form below, go short [24:30].

### Stop loss

Stop placement NOT STATED. Implied: opposite side of range.

### Take profit / exit

Follow the breakout direction [24:30].

### Invalidation / skip conditions

If price reverses back into the range immediately, the breakout is false.

### Claimed performance

NONE CLAIMED

### Vagueness log

1. VISUAL-ONLY: Identifying consolidated areas requires visual chart inspection [24:30]
2. UNDEFINED-RULE: How long must consolidation persist to be valid NOT STATED

### Mechanizability

PARTIAL – Range identification and breakout from range edges are mechanizable. However, consolidation validity and minimum duration are undefined.

---

## Strategy 11: Reversal Strategy

### Indicators and settings

- Renko chart

### Context / bias filter

After a strong run of several bricks of the same color [25:00], followed by a shift in color.

### Entry trigger

If you see several bricks of the same color, and then you get a shift in color, that might point to a change [25:00]. Trade in the direction of the color shift [25:00]. Strength increases if the reversal aligns with a big supply or demand zone [25:00].

### Stop loss

Stop placement NOT STATED. Implied: beyond the prior highs/lows.

### Take profit / exit

Exit when the reversal exhausts or price re-enters original direction.

### Invalidation / skip conditions

Riskier strategy because going against prior momentum [25:00]. Price may resume the original direction if the color flip is just a pullback.

### Claimed performance

NONE CLAIMED

### Vagueness log

1. UNDEFINED-RULE: What constitutes "several bricks" – minimum number NOT STATED
2. UNDEFINED-PARAM: How many bricks of color flip confirm the reversal NOT STATED
3. UNDEFINED-RULE: Zone proximity requirement not defined

### Mechanizability

PARTIAL – Color shift detection is mechanical. However, distinguishing reversal from pullback requires assumptions about brick counts and zone proximity.

---

## Strategy 12: Moving Average Confirmation

### Indicators and settings

- Moving average period: 20-brick (20 bricks, not time-based) [12:30], 50-brick [13:00]; examples given but not definitive
- Renko chart with moving average overlay

### Context / bias filter

Bricks stay above or below the moving average consistently [18:30]. Moving average points up and bricks stay green indicates uptrend [18:30].

### Entry trigger

When bricks remain stacked above the moving average for multiple bricks, bullish environment [13:00]. When bricks cross decisively below the moving average, momentum is turning bearish [13:00].

### Stop loss

Stop placement NOT STATED.

### Take profit / exit

Exit on opposite-side moving average crossover.

### Invalidation / skip conditions

If the moving average flattens and bricks keep flipping color, stay out [18:30].

### Claimed performance

NONE CLAIMED

### Vagueness log

1. UNDEFINED-PARAM: Which moving average period to use – examples given (20, 50) but no rules for selection [12:30-13:00]
2. UNDEFINED-RULE: What constitutes "multiple bricks" above the line [13:00]
3. UNDEFINED-RULE: How decisively must bricks cross below to be significant NOT DEFINED
4. NOTE: Moving average on Renko measures last N bricks (not time), so behavior differs from time-based charts [12:30]

### Mechanizability

PARTIAL – Moving average calculation is mechanical; crossover detection is mechanical. However, period selection is undefined and confirmation rules ("multiple bricks", "decisive cross") lack thresholds.

---

## Notable claims and caveats

- Brick size selection is crucial [02:30, 05:00]. Too small brick size creates choppy charts with false signals [04:30-05:00]. Too large brick size causes missed subtle turning points [02:30].
- ATR-based dynamic sizing can adapt to changing volatility but requires accepting that Renko chart appearance shifts as ATR changes [07:30-08:00].
- Time-based candle charts show noise that Renko filters [03:00]; this is Renko's primary advantage [12:30].
- Time-less structure means you cannot see how long a move took to develop [04:30].
- Selecting the wrong brick size can undermine Renko's benefits [04:30].
- Indicators on Renko measure last N bricks, not time periods, so they behave differently than on time-based charts [12:30].
- Multi-timeframe confirmation reduces false positives [15:30-16:00].
- Speaker emphasizes testing approaches on historical charts before live trading [24:00].
- Speaker notes: "You do not watch time-based developments in the same way. You watch price-based developments" [24:30-25:00].
- **No mention of costs, spreads, slippage, or commissions.**
- **No mention of drawdown or losing streaks.**
