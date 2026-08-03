# Verification output 0

### Golden/Death Cross Strategy (Red and Blue Lines) (0nRWsm4oAss)
- verdict: TESTABLE_WITH_ASSUMPTIONS
- assumption_count: 4
- assumptions_required:
  1. Stop-loss rule/placement is not stated at all for this strategy; a coder must invent a distance/method (e.g., ATR multiple, fixed pips, beyond a swing point).
  2. Take-profit/exit rule is not stated at all; a coder must invent an exit (e.g., opposite crossover, fixed R multiple).
  3. Entry timing is unspecified — whether the trade triggers on the close of the crossover bar or the next bar's open.
  4. "Use the green line as a confirmation" is stated but never defined — no rule for what the green line must do (be above/below price, cross something, etc.) to count as confirming; a coder must invent this rule or silently drop it, which changes the described strategy.
- instrument: Forex and stocks mentioned generally, no specific pair/ticker
- timeframe: NOT STATED
- needs_data_beyond_OHLCV: no
- one_line_summary: Trade a "golden/death cross" between the Alligator's red (8-period, displaced 5) and blue (13-period, displaced 8) smoothed moving averages — long on red-over-blue, short on the reverse — using the green (fastest) line as an undefined confirmation filter.

### Opening Channel Breakout (European Session) (BvUJ9upqpyI)
- verdict: TESTABLE_WITH_ASSUMPTIONS
- assumption_count: 4
- assumptions_required:
  1. Stop-loss distance: "a few pips" below/above the channel boundary is not quantified anywhere; a coder must invent a specific pip (or ATR-based) value.
  2. Breakout confirmation: whether "breaks above/below the channel" means any intrabar touch/wick beyond the level or a candle close beyond it is not specified.
  3. Management of the remaining position after the first target is hit: the speaker explicitly says "trail remaining position to next targets or use discretionary exit," which is stated as discretionary and needs an invented mechanical rule to be backtestable.
  4. Setup invalidation: whether/when a return inside the channel after the breakout should stop out or cancel the trade is only implied by the note, never stated by the speaker.
- instrument: Forex generally (no specific pair named)
- timeframe: Intraday, keyed to Frankfurt open (7:00 GMT) and London open (8:00 GMT)
- needs_data_beyond_OHLCV: no (requires timestamped intraday OHLCV aligned to GMT session times, which is still standard OHLCV)
- one_line_summary: Mark the high/low of the 7:00-8:00 GMT "opening channel," trade breakouts above/below it after London open, and take profit at the channel range projected 1x/2x/3x from the breakout, optionally filtered by 200 EMA direction.

### Inside-Outside-Inside Pattern (IZLMN_L3b0s)
- verdict: TESTABLE_WITH_ASSUMPTIONS
- assumption_count: 3
- assumptions_required:
  1. Stop-loss placement: the transcript only says the pattern "gives you tight levels... for stops" without ever stating where the stop actually goes; the note's "use swing high/swing low" wording is the note-writer's own inference, not something the speaker said, so a coder must invent an exact placement (e.g., opposite edge of the outside bar's range, plus/minus a buffer).
  2. Take-profit/exit rule: completely unstated; a coder must invent a target or a signal-based exit.
  3. Breakout confirmation: whether the long/short trigger requires a candle close beyond the outside bar's high/low, or just an intrabar breach, is not specified.
- instrument: NOT STATED
- timeframe: NOT STATED ("all timeframes" claimed generally; "lower timeframes" mentioned as most common)
- needs_data_beyond_OHLCV: no
- one_line_summary: Trade the breakout of a three-candle inside-outside-inside sequence (small inside bar, wide engulfing outside bar, tight inside bar again), going long above the range high or short below the range low.

### Three-Layer Bollinger Bands Trading (_8q3ZJ5afFA)
- verdict: TESTABLE_WITH_ASSUMPTIONS
- assumption_count: 4
- assumptions_required:
  1. Definition of the "bullish/bearish candle" or "reversal candle" used to confirm entries at the middle band or the outer bands — no candlestick pattern, body/wick ratio, or size threshold is given.
  2. Stop-loss placement for trend-following pullback entries (not stated at all) and for fade entries at the outer bands (not stated at all beyond "above/below the outer band").
  3. Whether the described confluence (touching a monthly pivot or a supply/demand zone at the same time as the band) is required for a valid signal, or whether the bands can be traded alone — the supply/demand zone concept is itself a visually-drawn, undefined level.
  4. The threshold distinguishing an "extreme"/fadeable touch of the outer band from a strong trend that is "hugging the band" (in which case the speaker says not to fade) is never quantified.
- instrument: NOT STATED (implied multi-asset: stocks, forex, indices, futures)
- timeframe: Daily and 4-hour charts
- needs_data_beyond_OHLCV: no
- one_line_summary: Use a 50-period SMA with 1/2/3 standard-deviation bands to buy pullbacks to the middle band in an uptrend and fade reversal candles at the outer bands, optionally combined with monthly pivots or supply/demand zones.

### Chandelier Exit as Trailing Stop/Exit Indicator (fmS_rUcKF6c)
- verdict: NOT_TESTABLE
- assumption_count: 2
- assumptions_required:
  1. An entire entry rule/trigger — completely unstated. The video explicitly assumes a position already exists ("Entry trigger: NOT SPECIFIED... Assumes trader is already in a position"), so a coder would have to invent an entirely separate entry strategy (which breakout, trend, or pattern signal to use) that this video never describes.
  2. The multiplier-adjustment rule ("some stocks are more volatile than others and require a bigger buffer") has no threshold for when or how much to increase the multiplier, so only the fixed default (3x ATR, 22-period) is usable without invention.
- blocking_issues: No entry trigger of any kind is given anywhere in the video; it is presented purely as an exit/trailing-stop technique layered on top of a pre-existing position. A backtest requires trade entries, and inventing a whole independent entry strategy is not a bounded assumption — it would mean testing a different, uncited strategy rather than encoding what the speaker actually said.
- instrument: Stocks (mentioned primarily)
- timeframe: Daily charts (22-period matches "22 trading days in a month")
- needs_data_beyond_OHLCV: no (ATR and highest-high/lowest-low are derivable from OHLC)
- one_line_summary: Use a 22-period, 3x-ATR "Chandelier Exit" trailing stop set below the recent high (for longs) or above the recent low (for shorts) to manage an already-open position, with no entry rule of its own.

### MACD Crossover (n72tM2HLv34)
- verdict: TESTABLE_WITH_ASSUMPTIONS
- assumption_count: 2
- assumptions_required:
  1. Execution timing: whether the trade is taken at the close of the bar where the MACD line crosses the signal line, or at the next bar's open, is not specified.
  2. Position model: whether a "sell signal" means closing a long position (flat/long-only system) or flipping to a short position (always-in-market long/short system) is not specified.
- instrument: Forex, crypto, and stocks mentioned generally; EUR/JPY given as an example
- timeframe: NOT STATED as a rule (daily, 5-minute, weekly, 15-minute all discussed as examples; speaker says "no such thing as a 'best' time")
- needs_data_beyond_OHLCV: no
- one_line_summary: Go long when the MACD line (12,26-period EMA difference) crosses above its 9-period signal line, and go short (or exit) on the reverse cross, noting the signal is more significant on the appropriate side of the zero line.

### Daily Average Range (ADR) Tracking (vvuWY3cFzpY)
- verdict: NOT_TESTABLE
- assumption_count: 3
- assumptions_required:
  1. There is no stated entry rule at all — the video frames the ADR comparison only as a qualitative caution/expectation ("be careful about chasing further breakouts," "expect more movement ahead"), never as a concrete buy/sell trigger.
  2. There is no stated exit or stop-loss rule.
  3. The "overextended" threshold is explicitly left open — the 110-pips-vs-100-pip-ADR example is illustrative only, not a stated rule, so a coder must invent the exact percentage (100%? 110%? something else) that would trigger caution or a trade decision.
- blocking_issues: This is presented as background market context/bias, not a trade signal (the note itself flags "the use of this information...is not fully specified"). Without inventing an entry trigger, a numeric overextension threshold, and an exit/stop rule, there is no executable strategy — filling these gaps would mean authoring a new strategy around the ADR concept rather than encoding what the speaker described.
- instrument: Currency pairs (100-pip ADR example given); stocks and index futures also mentioned elsewhere in the video
- timeframe: Intraday (midday/session-progress comparisons implied, e.g. "by noon")
- needs_data_beyond_OHLCV: no
- one_line_summary: Compare the day's current high-low range at midday to its 10/20-day average true range to judge whether the market is "overextended" (caution against chasing further breakouts) or has room to run, without any concrete entry, exit, or stop rule.
# Verification output — assignment 1

### StochRSI with MACD Confirmation (Market Strength) (3GmofkcVO58)
- verdict: TESTABLE_WITH_ASSUMPTIONS
- assumption_count: 3
- assumptions_required:
  1. Stop loss: no level or distance is given anywhere in the video ("NOT STATED"). A coder must invent a stop rule (fixed pips, ATR multiple, or swing-based) from nothing.
  2. Take profit / exit: no target or exit rule is given at all. A coder must invent when a trade closes (fixed R, opposite signal, trailing rule, etc.).
  3. "200 EMA rising" / "200 EMA falling" (the trend filter) has no stated slope definition — a coder must invent a lookback (e.g., EMA now vs. EMA N bars ago) to decide "rising" vs "falling."
- instrument: Bitcoin, Forex, and stock indices (Dow Jones, DAX) shown as examples; no single instrument mandated
- timeframe: NOT STATED (video says "day trading and swing trading" generically, no chart period given)
- needs_data_beyond_OHLCV: no (StochRSI, MACD, and EMA are all price-only)
- one_line_summary: Go long when StochRSI(100,100) D-line > 50 and MACD(10,100,1) > 0 in a 200-EMA uptrend (mirror for shorts), but with no stop-loss or take-profit rule stated.

---

### Opening Channel Breakout with 200 EMA Confirmation Filter (BvUJ9upqpyI)
- verdict: TESTABLE_WITH_ASSUMPTIONS
- assumption_count: 3
- assumptions_required:
  1. Stop loss is "a few pips below/above the channel" — no numeric pip value is given; a coder must invent a specific distance (and it is instrument-dependent, so the invented value drives results).
  2. Exit management for the trailing 50% of the position after the first target is explicitly left open ("trail remaining position to next targets or use discretionary exit") — the note itself flags this as discretionary. A coder must invent a concrete trailing/exit rule to replace the undefined "discretionary" option.
  3. Exact boundary of the "opening channel" (whether the Frankfurt-open bar itself is included, or strictly the 7:00–8:00 GMT high/low window) is only loosely described; a coder must fix this convention.
- instrument: Forex, unspecified pair ("the world's largest financial market")
- timeframe: Intraday, session-anchored (Frankfurt open 7:00 GMT, London open 8:00 GMT); underlying chart timeframe (1-min/5-min) NOT STATED
- needs_data_beyond_OHLCV: no, but requires GMT-aligned intraday timestamps to compute the session channel
- one_line_summary: Trade breakouts of the 7:00–8:00 GMT opening range after London open, targeting multiples of the range with an optional 200-EMA directional filter, but stop distance and back-half exit management are undefined.

---

### Pivot Point Trend Trading with ADL Confirmation (Pdpcy_FGV7I)
- verdict: TESTABLE_WITH_ASSUMPTIONS
- assumption_count: 4
- assumptions_required:
  1. "Price rejects the central pivot point" (the long-entry trigger) has no stated candle pattern or rule — a coder must invent an operational definition (e.g., "low touches/crosses CPP then the bar closes back above it").
  2. "Price retraces to / is at the central pivot point" has no stated tolerance — a coder must invent how close price must get (exact touch vs. a band around CPP) to count as "at" the pivot.
  3. Initial stop-loss placement is never given — only "move stop to break-even after partial profit" is mentioned. A coder must invent the entry-time stop distance/rule.
  4. Timeframe is not fixed: the speaker uses 15-min (EUR/USD) and 30-min (GBP/USD) as examples but says to "backtest and see which timeframe offers higher-probability setups" — a coder must pick one specific timeframe to run.
- instrument: Forex (EUR/USD, GBP/USD examples) and cryptocurrencies; explicitly NOT stocks (speaker says AD-line gaps make it unreliable there)
- timeframe: 15-minute (EUR/USD example) or 30-minute (GBP/USD example); no single timeframe mandated
- needs_data_beyond_OHLCV: no (ADL uses volume, which is part of OHLCV; pivots are computed from prior H/L/C)
- one_line_summary: Enter at the daily central pivot point in the direction confirmed by an ADL-line/200-EMA crossover, targeting R1/R2 or S1/S2, but the pivot "rejection" entry pattern and the initial stop are never defined.

---

### 21-Period EMA Channel Trading (_8q3ZJ5afFA)
- verdict: NOT_TESTABLE
- assumption_count: 6
- assumptions_required:
  1. Instrument/asset class is never stated for the strategy itself (the video's markets are "NOT STATED"); the only clue is that the "round number" examples given are forex-style (1.1000, 1.2000).
  2. "Round number" is not defined for any instrument the strategy might run on — the granularity (every big figure? every $1? every $100 for BTC?) has to be invented and is entirely asset-dependent.
  3. "Near a round number" has no proximity tolerance stated — how close price must get to count as "at" the level is invented.
  4. "Bullish/bearish candlestick bounce off that zone" has no pattern definition (wick ratio, body size, etc.) — purely a visual judgment call in the video.
  5. Breaking the channel "with conviction" (for the breakout variant) has no quantified threshold (how far beyond the line, on what kind of candle).
  6. Stop-loss distance "under the channel" is never quantified.
- blocking_issues: The entry logic depends simultaneously on an undefined, asset-specific concept ("round number") on an unstated instrument, plus two more unquantified visual judgments ("bounce," "conviction"). None of these are parameters on an otherwise-complete rule set — they are the rule itself, and different reasonable choices for round-number granularity and bounce/conviction thresholds would produce entirely different trade sets. This is chart-reading dressed as an indicator strategy, not a backtestable rule set.
- instrument: NOT STATED (round-number examples are forex-style, but the video's markets are described as multi-asset)
- timeframe: Daily and 4-hour charts explicitly mentioned
- needs_data_beyond_OHLCV: no (EMA channel and round numbers are price-only), but the missing instrument/asset choice is itself a blocking gap
- one_line_summary: Trade bounces or breakouts of a 21-period EMA-of-high/EMA-of-low channel when they align with a round-number level, but "round number," "bounce," and breakout "conviction" are all undefined visual judgments on an unspecified instrument.

---

### Donchian Channel Breakout Entry with Channel-Based Exit (fmS_rUcKF6c)
- verdict: TESTABLE_WITH_ASSUMPTIONS
- assumption_count: 2
- assumptions_required:
  1. The video offers two alternative, individually well-defined exit rules — close-back-through-the-opposite-band vs. touch-of-the-midpoint of a 50-day channel — and says the choice "depends on your risk aversion" without mandating one. A coder must pick (and pair the midpoint variant with the stated 50-period channel, since that pairing is explicit).
  2. Standard Donchian implementation detail: whether the N-period high/low used to test "closes above/below" excludes the current (signal) bar itself is not stated; a coder must fix this convention to avoid look-ahead bias.
- instrument: Stocks mentioned primarily
- timeframe: Daily charts
- needs_data_beyond_OHLCV: no
- one_line_summary: Enter on a close above/below a 20-period Donchian channel with a 2×ATR(20) initial stop (Turtle-style), exiting on either an opposite-band close or a touch of the 50-day channel midpoint.

---

### VWAP Entry (oF_NsJLMXEs)
- verdict: TESTABLE_WITH_ASSUMPTIONS
- assumption_count: 5
- assumptions_required:
  1. VWAP requires a defined session anchor/reset time, but the instrument and trading session are both "NOT STATED" for this video — a coder must invent which market session (and hours) resets the VWAP each day.
  2. "Suddenly dips below" / "suddenly pops above" VWAP has no time or magnitude definition — a coder must invent an operational rule (e.g., treat it as a simple close-based cross) to stand in for "suddenly."
  3. "Bullish candlestick pattern with long lower wick" (the third entry signal) has no wick/body ratio defined — a coder must invent a pattern threshold.
  4. Stop loss is not stated anywhere for this strategy.
  5. Take profit / exit is not stated anywhere for this strategy.
- instrument: NOT STATED (stocks, currencies, crypto mentioned generically as examples elsewhere in the video)
- timeframe: NOT STATED (intraday day-trading system implied)
- needs_data_beyond_OHLCV: no (VWAP uses volume, part of OHLCV), but requires a defined intraday session anchor
- one_line_summary: Buy/sell on a cross of VWAP (or a long-lower-wick candle while price is above VWAP), but "suddenly," the candle pattern, the session anchor, and both exits are all undefined.

---

### VWAP Trading - Basic Buy/Sell Signals (w_VNaTAB64c)
- verdict: TESTABLE_WITH_ASSUMPTIONS
- assumption_count: 4
- assumptions_required:
  1. "Rising" / "falling" VWAP has no stated lookback — a coder must invent how many bars back to compare against to call the VWAP slope "rising" or "falling."
  2. "Exceeds" / "falls below" VWAP has no stated confirmation rule — a coder must invent whether this means an intrabar touch or a bar close beyond VWAP.
  3. VWAP session reset/anchor time must be invented since the course never states the instrument or its trading session/hours.
  4. Stop loss and take profit are both "NOT STATED" for this signal — a coder must invent both.
- instrument: NOT STATED across the course (examples reference forex and stocks generically)
- timeframe: Daily VWAP reset stated explicitly; underlying intraday chart period (5-min/15-min) not tied to this specific signal
- needs_data_beyond_OHLCV: no (VWAP uses volume, part of OHLCV)
- one_line_summary: Buy when price is above a rising VWAP and sell when price is below a falling VWAP, but "rising/falling" is unquantified and no stop-loss or take-profit is given.
# Verification output — assignment 2

### Confluence Breakout Scalping Strategy (5ZYVXiSKfxU)
- verdict: TESTABLE_WITH_ASSUMPTIONS
- assumption_count: 3
- assumptions_required:
  1. Swing-high/swing-low lookback for support/resistance identification: the note says breakout is off "support/resistance" found via "swing lows, consolidation areas" but never states how many bars back to look; a coder must invent a fractal/lookback rule (e.g., 10-bar swing).
  2. VSA volume-level thresholds: the strategy is gated on "high" vs "ultra-high" vs "average" volume from a colour-coded VSA panel, but no formula (percentile, multiple of average, stdev band) is given for where "average" ends and "high" begins — a bespoke indicator with unstated math.
  3. "Multiple consecutive" Heikin-Ashi candles required to call a trend established — no count given; a coder must invent one (e.g., 3 candles).
- instrument: NOT STATED (examples shown: Apple, Tesla, EUR/USD)
- timeframe: 5-minute chart
- needs_data_beyond_OHLCV: no (volume is standard OHLCV volume; VSA colour bands are a derived/undefined transform of it, not a new data source)
- one_line_summary: Long/short 5-minute breakout of support/resistance requiring simultaneous Heikin-Ashi trend color, RSI(50) above/below the 50 line, and high/ultra-high VSA volume, with a fixed 2:1 reward-to-risk exit.

### Multi-Timeframe Heiken Ashi Color Change (Ci1hKIHL9VY)
- verdict: TESTABLE_WITH_ASSUMPTIONS
- assumption_count: 4
- assumptions_required:
  1. Which two (or three) specific timeframes to pair — the speaker only gives examples ("e.g., 1-hour and 4-hour, or daily and weekly") and explicitly says any two consecutive timeframes work; a coder must commit to one concrete pair.
  2. Stop-loss rule/placement: not stated anywhere in the strategy.
  3. Take-profit rule/target: not stated anywhere in the strategy.
  4. Entry timing: whether the trade is taken on the close of the color-change bar or the open of the next bar is not specified.
- instrument: Forex, stocks, crypto (stated generically, no specific symbol)
- timeframe: NOT STATED as a specific pair — speaker gives only illustrative examples of "two consecutive timeframes"
- needs_data_beyond_OHLCV: no
- one_line_summary: Buy when Heikin-Ashi candles flip red-to-green (or sell on green-to-red) simultaneously on two aligned, unspecified timeframes.

### MACD Trend System (S2HaCa0b-bY)
- verdict: TESTABLE_WITH_ASSUMPTIONS
- assumption_count: 3
- assumptions_required:
  1. MACD parameter settings (fast/slow/signal periods): the note says "default settings NOT STATED but standard MACD assumed" — the speaker never actually gives 12/26/9, so using it is an invented default.
  2. "Recent swing high/low" lookback for stop placement: no bar count given for "recent."
  3. Exact number of candles to wait after crossover before entering — the speaker says "2-3 candles," which is a range, not a single rule; a coder must pick one number.
- instrument: NOT STATED
- timeframe: multiple examples used (daily, 4H, 1H, 15m) but no single timeframe is committed to for this system alone
- needs_data_beyond_OHLCV: no
- one_line_summary: Trade MACD crossovers only in the direction of the zero-line bias and only when the crossover occurs at least 0.5 away from zero, with a 2R target and stop at the recent swing point.

### Round Number Support/Resistance Trading (_8q3ZJ5afFA)
- verdict: TESTABLE_WITH_ASSUMPTIONS
- assumption_count: 5
- assumptions_required:
  1. Round-number grid/granularity: the note never defines which levels count as a "major round number" (every 0.0100, every big figure, every $1, every $100?) — this is the core signal definition and is entirely invented by whoever codes it.
  2. Breakout "conviction" distance: how far beyond the round number price must close to count as a valid breakout is not stated.
  3. Stop-loss distance from the round number: implied to be "slightly beyond" but no pip/point value given.
  4. Confluence requirement: the invalidation rule says "if no clear confluence with other tools, skip," but how many confluent tools (pivots/bands/channel) are required, or whether to test round numbers standalone (ignoring this gate), is not specified.
  5. Trend definition for this strategy segment: entries require "the market is in an uptrend/downtrend" but this segment doesn't restate how trend is determined here — a coder must borrow (or invent) a rule such as price vs. an N-period MA/channel.
- instrument: NOT STATED (examples imply multi-asset: stocks, forex indices, futures)
- timeframe: daily and 4-hour charts
- needs_data_beyond_OHLCV: no
- one_line_summary: Trade breakouts (with-trend) or bounces (in-range) at round psychological price levels, targeting the next round number, ideally when other tools (pivots, bands, channel) agree.

### 10-Period SMA Daily Chart Trend Filter (iB3dt0Kk8j0)
- verdict: NOT_TESTABLE
- assumption_count: 4
- assumptions_required:
  1. "Price near the moving average" distance threshold — not stated, needed to decide when to skip trading.
  2. Slope-direction lookback — how many bars back to measure slope is not specified.
  3. What "look for buy/sell trades on shorter timeframes" actually means as an entry — this filter names no entry trigger of its own; the downstream trade is a wholly separate, unspecified strategy.
  4. Stop-loss and take-profit — none given; the note itself states "this is a bias filter, not a complete strategy."
- blocking_issues: This is explicitly a regime/bias filter, not a tradable system — it has no entry trigger, no stop, and no target of its own, and the note admits as much ("NOT STATED; this is a bias filter, not a complete strategy"). To "backtest" it, a coder would have to invent an entire separate entry/exit system for the "shorter timeframe trades" it gestures at, which is not filling a parameter gap but fabricating the strategy wholesale. The extraction's own FULL rating directly contradicts its own text ("though the threshold for what constitutes 'near' and entry/exit rules... are left to trader discretion").
- instrument: crude oil shown as an example; forex/commodities/equities implied generally
- timeframe: Daily chart for the filter; unspecified shorter timeframes for the actual trades
- needs_data_beyond_OHLCV: no
- one_line_summary: Use the slope and position of price relative to a 10-period daily SMA as a bias filter before taking (unspecified) trades on shorter timeframes.

### Pivot Point Trading (oF_NsJLMXEs)
- verdict: TESTABLE_WITH_ASSUMPTIONS
- assumption_count: 4
- assumptions_required:
  1. Pivot-point formula: the note flags this explicitly — "which pivot formula? (standard, Fibonacci, Woodie, Camarilla?)" is never answered by the speaker; a coder must pick one (e.g., standard floor pivots).
  2. "Suddenly bounces" / "suddenly drops" threshold: no price or time definition of "sudden" is given.
  3. Stop-loss rule: not stated at all for this strategy.
  4. Take-profit rule: not stated at all for this strategy.
- instrument: stocks, currencies, crypto mentioned as examples; not a specific requirement
- timeframe: NOT STATED (intraday day-trading focus implied)
- needs_data_beyond_OHLCV: no
- one_line_summary: Buy near S1/S2 (or sell near R1/R2) when price "suddenly" reverses off the level, using standard pivot-point math computed from prior-period OHLC.

### Moving Average for Trend Direction Confirmation (yPbUn3Wuh98)
- verdict: NOT_TESTABLE
- assumption_count: 5
- assumptions_required:
  1. Moving-average period — the note literally says "Any moving average," so even the core indicator parameter is unspecified.
  2. Moving-average type (SMA vs EMA) — not stated for this sub-strategy (elsewhere in the video EMAs of specific lengths are used, but not here).
  3. Slope-threshold for "upsloping/downsloping" — no degree or lookback given.
  4. Entry trigger — the note is explicit that this is "not a direct entry signal," only a directional bias ("look for long trades" with no defined trade).
  5. Stop-loss and take-profit — neither stated.
- blocking_issues: The strategy as described has no committed indicator period, no entry rule beyond a directional bias, and no risk management — it is presented purely as a discretionary context filter ("used as a bias filter, not a primary entry signal"). Coding a backtest would mean inventing essentially every component (MA length/type, slope rule, entry, stop, target) rather than filling in a handful of missing numbers, so it fails the test even generously applied.
- instrument: Stocks (general, "good fundamentals" emphasized elsewhere in the video but not tied to this sub-strategy)
- timeframe: NOT STATED for this sub-strategy specifically (video overall recommends daily and higher)
- needs_data_beyond_OHLCV: no
- one_line_summary: Use the direction of price relative to an unspecified moving average, and its slope, as a discretionary directional bias rather than a defined trade trigger.
# Verification output — assignment 3

### Order Block with 200 EMA Channel (Long and Short) (7Zvt6efiHME)
- verdict: TESTABLE_WITH_ASSUMPTIONS
- assumption_count: 3
- assumptions_required:
  1. Swing high/low detection method and lookback for "break of structure" — the note says an order block is only valid if the move off it "breaks a previous swing high or swing low," but no swing-point definition (e.g., N-bar fractal) or lookback window is ever given. A coder must invent this, and it also implicitly defines where the "order block candle" / directional move begins.
  2. Which edge of the zone to use for the limit order when the order block and EMA channel only partially overlap. The speaker's rule ("touch or overlap... has to make contact") is binary and codable when the zones fully align, but the note itself flags that partial-overlap cases leave the entry price ambiguous.
  3. What counts as a "test" of the zone for the freshness rule (Rule 3) — is a mere wick-touch enough to consume the zone, or does price need to close inside it? Not stated, and this materially changes how many setups qualify as "fresh."
- instrument: NOT STATED
- timeframe: NOT STATED
- needs_data_beyond_OHLCV: no
- one_line_summary: Trade order blocks that touch a 200-EMA(high)/200-EMA(low) channel, break prior structure, and are untested, entering via limit order at the confluent zone edge with a stop beyond the OB candle and a 2:1 target.

### Short Entry (Red Renko Brick) (CtelYJ5lFr8)
- verdict: TESTABLE_WITH_ASSUMPTIONS
- assumption_count: 3
- assumptions_required:
  1. Definition of "new low" in OBV for the entry filter — the note explicitly flags that no lookback window is given (new low vs. the prior bar? Prior N Renko bricks?). A coder must invent this window.
  2. Quantified slope threshold for the SMA10 to be "pointing downward" vs. "flat" — the speaker treats this as an important quality filter (the two flagged bad trades in the video were flat-SMA entries) but gives no angle or rate-of-change threshold, so applying it faithfully requires an invented number; skipping it entirely means not testing the strategy as the speaker actually traded it.
  3. Specific instrument/contract to test — the video only says "stock market" generically and shows one example; the 100-point brick size is stated but only makes sense once a specific instrument (with a point value consistent with 100-point Renko bricks) is chosen, which the speaker never names.
- instrument: verbatim "stock market" (no specific ticker/index stated)
- timeframe: NOT STATED (Renko bricks are event-based, not time-based)
- needs_data_beyond_OHLCV: no
- one_line_summary: Short when a new red 100-point Renko brick forms below a 10-period SMA with OBV confirming a new low, stop 2 bricks above entry, minimum target 3 bricks below.

### MACD Confirmation System (Multi-Timeframe Filter) (S2HaCa0b-bY)
- verdict: NOT_TESTABLE
- assumption_count: 4
- assumptions_required:
  1. Swing high/low lookback for stop placement — "recent swing high/low" is never quantified anywhere in the note.
  2. Definition of "divergence forming" on the middle timeframe — the middle-timeframe signal can be either a crossover (mechanical) or a divergence (explicitly flagged elsewhere in the same note as visual-only/subjective, "connecting tops"), and the strategy description doesn't say which is required when.
  3. "Price at key level" — the speaker's own workflow for confirming this system includes "price at key level," i.e., a support/resistance level, with no formula for where that level sits.
  4. Hammer-candle and trendline-break confirmations mentioned as part of price-action confirmation are visual pattern calls with no stated formula.
- blocking_issues: The system's confirmation step is not just "MACD position + crossover + histogram flip" (which alone would be mechanizable) — the speaker's own described workflow folds in "price at key level" and other price-action confirmation (hammer candles, trendline breaks), which are drawn/read by eye with no quantified rule. That is a core, not incidental, part of how the system is described as being used, so a programmer cannot fully encode it without inventing a level-detection scheme the speaker never gave.
- instrument: NOT STATED
- timeframe: multi-timeframe by design (uses a "4x multiplier" stack, e.g. 15m/1H/4H or 1H/4H/Daily); no single timeframe stated as canonical
- needs_data_beyond_OHLCV: no
- one_line_summary: Require MACD zero-line bias on a higher timeframe, a crossover/divergence signal on a middle timeframe, and a histogram-flip trigger on the entry timeframe, confirmed by price action at key levels, with stop at recent swing and 2x-risk target.

### MFI 50-Level Crossover (bAT6F7x9K8M)
- verdict: TESTABLE_WITH_ASSUMPTIONS
- assumption_count: 2
- assumptions_required:
  1. Stop-loss rule — none is stated anywhere for this strategy (the note explicitly marks it "NOT STATED"); a coder must invent a stop methodology (e.g., ATR multiple, fixed %, or swing-based) to run any P&L backtest.
  2. Take-profit / exit rule — likewise entirely unstated. Whether the exit is an opposite MFI-50 cross, a fixed R-multiple, or something else must be invented; the video only ever describes the entry condition.
- instrument: NOT STATED for this specific sub-strategy (general "all markets" framing; stocks used as examples elsewhere in the video)
- timeframe: NOT STATED
- needs_data_beyond_OHLCV: no (MFI requires volume, which is part of standard OHLCV data)
- one_line_summary: Take MFI(50) crosses above/below the 50 level, filtered to only trade in the direction of the 200 EMA trend.

### TPO Charts (Time Price Opportunity) (luEbG761C50)
- verdict: NOT_TESTABLE
- assumption_count: 5
- assumptions_required:
  1. TPO "letter period" — classic Time-Price-Opportunity charts require a stated time-per-letter (e.g., 30 minutes); the note never states one, so bucket construction itself would have to be invented.
  2. Price increment/tick size for TPO letter rows — not stated.
  3. A concrete entry trigger — the segment only describes visual concepts (balanced session, "bullish acceptance," "quick rejection," POC, value area) with no stated buy/sell rule, e.g. no rule translating "opens above prior value area and builds letters higher" into an executable signal.
  4. Quantified thresholds for "big cluster," "balanced session," and "strong rejection" (single vs. two letters) — all explicitly flagged as subjective in the note with no numeric definition.
  5. Stop-loss and take-profit rules — neither is given anywhere in this section.
- blocking_issues: This segment of the video is descriptive market-structure commentary, not a stated trade plan — there is no entry trigger, stop, or target given at all, only qualitative descriptions of what a TPO profile can look like. Even the underlying TPO/value-area construction needs a session-letter time period and price increment that are never specified. A programmer would have to invent the entire trade rule, not just a parameter or two, so this cannot be called mechanizable even "with assumptions" in the normal sense — it would effectively be a different, invented strategy.
- instrument: NOT STATED
- timeframe: intraday/session-based (TPO is inherently a within-day profile); no specific timeframe or session hours stated
- needs_data_beyond_OHLCV: yes — needs intraday sub-bar/tick data to build time-at-price letters within each session, finer-grained than whatever OHLCV bar interval is being backtested
- one_line_summary: Read intraday Time-Price-Opportunity profiles (point of control, value area, acceptance/rejection patterns) to gauge whether the market is accepting or rejecting price at various levels.

### Mechanical Swing Trading (Daily Outside Bar) (s4DSY3Y_N4Y)
- verdict: TESTABLE_WITH_ASSUMPTIONS
- assumption_count: 2
- assumptions_required:
  1. Quantified slope/angle threshold distinguishing a "clean" sloping EMA from "flat" or "tangled." The speaker treats this as a hard pass/fail trend-filter check ("hard rule... if lines are tangled, flat, or crossing, skip the chart") but never gives an angle, rate-of-change, or lookback to compute it — a coder must invent a threshold (e.g., EMA change over N bars exceeding X%).
  2. Swing high/low lookback/definition for the Tier 3 trailing stop ("trail the stop under the most recent swing low") — no lookback window or swing-detection method is given.
- instrument: General; examples shown include Gold, Crude Oil, SPY, EUR/USD, and NAS — no single instrument mandated
- timeframe: Daily (explicitly stated as non-negotiable)
- needs_data_beyond_OHLCV: no
- one_line_summary: On daily bars, trade pullbacks into the zone between a 20 and 50 EMA (both aligned and cleanly sloped) triggered by an outside bar closing in the trend direction, with a stop beyond the outside bar and a tiered exit (50% at 1R, breakeven, then a swing-based trailing stop).
# Verification output — assignment 4

### Yellow Line Crosses 50 Level (A5IgJuaKHdc)
- verdict: TESTABLE_WITH_ASSUMPTIONS
- assumption_count: 3
- assumptions_required:
  1. Underlying RSI period feeding the TDI (and thus the yellow/middle-BB line): the speaker only gives a floor ("not below 20"), never a specific value used in the demonstration — a coder must invent an actual period (e.g. the common TDI default of 21).
  2. Stop loss: completely unstated for this signal (no distance, no reference point) — must be invented from scratch.
  3. Take profit / exit rule: completely unstated — must be invented (e.g. fixed R:R, or exit on opposite 50-level cross).
- blocking_issues: n/a
- instrument: NOT STATED (general application to any market)
- timeframe: NOT STATED (speaker says the signal is "especially significant" on "longer timeframes" but never commits to one)
- needs_data_beyond_OHLCV: no
- one_line_summary: Buy when the TDI's middle-Bollinger-Band ("yellow") line crosses the RSI centerline (50) from below, sell when it crosses from above, with no stop/target specified and the RSI period underlying the whole indicator left only loosely bounded.

### Ultimate Oscillator Divergence Trading (DQXqjjFz11k)
- verdict: TESTABLE_WITH_ASSUMPTIONS
- assumption_count: 6
- assumptions_required:
  1. Swing/pivot detection method and lookback for what counts as "a low" or "a high" feeding the divergence (not stated — classic invented-parameter case; the brief specifically flags undefined swing-high/low lookbacks).
  2. Maximum/typical bar spacing allowed between the two divergence lows (or highs) — not stated, so degenerate or extremely wide "divergences" are not excluded by any rule the speaker gave.
  3. Exact break condition for "oscillator rises above the divergence high / drops below the divergence low" — on the wick, the close, intrabar, market order vs. next-bar open? Not stated.
  4. Stop loss: not stated at all.
  5. Take profit / exit rule: not stated at all.
  6. Confirmation timeframe: the video discusses intraday/daily/weekly/monthly application and timeframe-dependent parameter tuning (7,14,28 vs 4,8,16) but never commits to one timeframe or one parameter set as "the" strategy to test.
- blocking_issues: n/a
- instrument: NOT STATED (forex and stocks mentioned generically, no named symbol)
- timeframe: NOT STATED as a single required timeframe (speaker says it works on "intraday, daily, weekly or even monthly charts," with (7,14,28) as default and (4,8,16) offered for more sensitivity)
- needs_data_beyond_OHLCV: no
- one_line_summary: Enter on a bullish/bearish Ultimate Oscillator divergence against price (confirmed by oversold/overbought origin and a break of the divergence's high/low), but with no defined swing-detection rule, entry mechanics, stop, or target.

### Momentum 0-Line Crossover (Basic Approach - Not Recommended Alone) (ULd9DYzOI7E)
- verdict: TESTABLE_WITH_ASSUMPTIONS
- assumption_count: 3
- assumptions_required:
  1. Momentum indicator period: the speaker gives three "most common" values (7, 14, or 21) without ever picking one for this strategy — a coder must invent which one to run.
  2. Stop loss: not stated.
  3. Take profit / exit rule: not stated (e.g., must invent whether exit is on the opposite zero-cross, a fixed target, or something else).
- blocking_issues: n/a
- instrument: NOT STATED (Tesla is used only as an illustrative chart example, not a prescribed instrument)
- timeframe: NOT STATED as a strict requirement (a daily/D1 chart is used for the illustrative "this doesn't work" example, but no timeframe is prescribed for the rule itself)
- needs_data_beyond_OHLCV: no
- one_line_summary: Buy when the Momentum oscillator crosses above zero and sell when it crosses below zero, with the oscillator's own period left as one of three options and no stop or target given — and the speaker explicitly frames this version as broken/not to be traded alone.

### Fibonacci Pivot Point Trend Following (bkSS_kPCctQ)
- verdict: TESTABLE_WITH_ASSUMPTIONS
- assumption_count: 5
- assumptions_required:
  1. Trend-direction rule to use: the note gives two different trend filters (visual higher-highs/higher-lows swing structure vs. objective comparison of today's central pivot to yesterday's) without saying which governs; if the swing-structure version is used, its lookback for defining a "swing" is never stated (an invented-parameter case flagged directly in the brief).
  2. Precise entry trigger: "buy at S1 or at the central Pivot Point" doesn't say which level takes priority when both are candidates, nor whether entry fires on touch or requires the "price action or any other technique you prefer" confirmation the speaker leaves fully open-ended.
  3. Stop loss: not stated at all.
  4. Take-profit target selection: "target R1 or R2" (or "S1 or S2") gives two options with no rule for choosing between them.
  5. Exit/holding-period rule if price never reaches the chosen target: not stated.
- blocking_issues: n/a
- instrument: NOT STATED (forex and stock markets mentioned generally, no specific symbol)
- timeframe: 1 hour and higher (stated; "the higher the timeframe, the stronger the signal")
- needs_data_beyond_OHLCV: no (pivot levels are derived from the prior session's H/L/C; optional 100–200 period MA is also OHLCV-only)
- one_line_summary: Trade in the direction of the prevailing trend, buying at S1/central pivot and selling at R1/central pivot with R1/R2 or S1/S2 as targets, but with the trend rule, exact entry trigger, stop loss, and target choice all left underspecified.

### Range Analysis (Bar Expansion/Contraction) (luEbG761C50)
- verdict: NOT_TESTABLE
- assumption_count: 4
- assumptions_required:
  1. Threshold for "big"/"large" range vs. "small"/"narrow" range: no baseline is given (no ATR, no N-bar average, no percentile) to compare a bar's range against.
  2. An actual directional entry rule: the material never states "buy when X, sell when Y" — it only describes what expansion/contraction supposedly signals about other participants' behavior ("many players jumped in," "some traders anticipate breakout") without committing to a trade direction or trigger.
  3. Stop loss: not stated.
  4. Take profit / exit rule: not stated.
- blocking_issues: There is no codifiable entry rule here at all, even a vague one — the section is market commentary about what large/small ranges "mean" about participant behavior, not a buy/sell trigger. Even after inventing a range-expansion threshold, there is nothing in the note specifying which direction to trade, when to enter, or when to exit. A programmer would be inventing the entire strategy, not just its parameters.
- instrument: NOT STATED
- timeframe: NOT STATED for this strategy specifically (video-wide context is intraday/scalping with a 5-minute chart shown elsewhere, but not tied to this technique)
- needs_data_beyond_OHLCV: no (bar range is simply high − low, computable from OHLCV) — though the surrounding video leans on footprint/order-flow data for other strategies, this specific technique only needs OHLCV
- one_line_summary: Interpret whether a candle's high-minus-low range is expanding (energy/volatility, possible breakout) or contracting (indecision, possible coiling before a move), without ever specifying a quantified threshold, a trade direction, an entry trigger, a stop, or a target.

### EMA + RSI + ADX Scalping (vBM0imYSzxI)
- verdict: TESTABLE_WITH_ASSUMPTIONS
- assumption_count: 5
- assumptions_required:
  1. Stop-loss buffer: the rule is "stop below this candle" / "above this candle" (one of the brief's named disqualifying phrasings) — the speaker never gives a buffer distance; the single "4 pip" mention is one anecdotal trade example, not a stated rule, so the exact stop level (candle extreme itself, or some pips beyond it) must be invented.
  2. Take-profit selection: the speaker offers both a 1:1 and a 1.5:1 risk-reward target with no rule for choosing between them, plus a partial-close instruction at 1:1 ("close a part of your position") where the percentage closed is never stated.
  3. EMA "sloping upwards/downwards" is listed as part of the trend condition but the slope magnitude/lookback needed to call it "sloping" is never quantified.
  4. Exact session-hours filter: "London session begin to US session end" is given qualitatively, but exact clock times (in a stated timezone) are not provided, so specific cutoffs must be invented if the hour filter is enforced.
  5. Optional price-action confirmation ("trade from levels of support and resistance... Fibonacci levels, or swing highs and lows") is mentioned as reinforcing context; if treated as a required filter it reintroduces subjective S/R identification with no defined swing lookback — must be either dropped (an assumption in itself) or given an invented rule.
- blocking_issues: n/a
- instrument: Forex or major indices (stated)
- timeframe: 5-minute (explicitly stated)
- needs_data_beyond_OHLCV: no
- one_line_summary: Scalp entries where price sits on the trend side of a 50 EMA, 3-period RSI touches 20/80, and 5-period ADX is above 30, entering at the signal candle's high/low only if the next candle breaks it, with stop/target/slope/session-hour specifics left short of a fully committed rule despite the note's original "FULL" rating.
