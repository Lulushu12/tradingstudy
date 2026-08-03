# Frozen spec: four TheSecretMindset strategies on crypto

Status: FROZEN. Written after extraction and audit, before any backtest code was run.
No amendment without an explicit logged note in this file.

Everything in a **Stated** block came from the video and is quoted in the linked note.
Everything in an **Invented** block did not. It was chosen by Claude because the strategy
cannot be coded without it. Invented choices are fixed here in advance and are never tuned
against results. If a strategy needs an invented value to work, that is a property of the
invention, not evidence about the strategy.

## Scope

Crypto only, per instruction. BTCUSDT.P is the only instrument with usable volume and full
coverage, so it is the test bed. XRPUSDT.P is excluded: its export carries no volume column
at all (207,072 of 207,072 bars NaN), which rules out the MFI strategy, and it has 90.8%
bar coverage with a 7,807-bar hole.

The channel is not a crypto channel. Of 266 extracted notes, crypto is named in 27. Running
stock and forex material on BTCUSDT is itself an untested transfer assumption, and it applies
to all four strategies below. It is the largest single caveat on every number produced.

## Data

| Series | Bars | Span | Coverage | Use |
|---|---|---|---|---|
| BTCUSDT_1D | 2479 | 2019-09-08 to 2026-06-21 | 100.0% | primary |
| BTCUSDT_4h | 11987 | 2021-01-01 to 2026-06-21 | 100.0% | S1 secondary only |

Only time/open/high/low/close/volume are read. Every indicator column present in the
TradingView exports is discarded and recomputed, so a stale study cannot leak in.

## Holdout

Studied span: start of data through **2024-12-31**.
Holdout: **2025-01-01 onward**, quarantined. Not loaded, plotted, described or counted until
a holdout run is explicitly authorised. Enforced in code by a hard date cut in the loader.

## Costs (pre-committed, before results exist)

- 0.05% per side, 0.10% per round trip. This is Binance USD-M perp taker fee (0.04%) plus
  0.01% slippage. All entries and exits are market orders.
- Every fill pays it, including partial exits and stop-outs.
- A cost sweep from 0.00% to 0.30% per side is run for every strategy to locate where
  expectancy crosses zero. The sweep is reported whatever it shows.

## Position sizing

- Strategies with a defined stop (S2, S3, S4): 1% of current equity risked per trade,
  size = risk / stop distance. Matches the convention already used in this repository.
- Strategies with no stop (S1): 100% of equity notional, no leverage, no compounding beyond
  the equity curve itself.
- No pyramiding. One position per strategy at a time.

## Execution model

- A signal on bar t uses only data up to and including bar t's close.
- Default fill: market order at the **open of bar t+1**. The one exception is S4, where the
  speaker explicitly says to enter at the close of the signal candle; that is modelled as
  stated, filled at bar t close.
- Intrabar ambiguity: if a bar's range contains both the stop and the target, the **stop is
  assumed to fill first**. This is pessimistic by construction and is never relaxed.
- Stops and trails update only on confirmed bar closes, never intrabar.

---

## S1: MACD crossover
Source: `notes/n72tM2HLv34.md`, "Ultimate MACD Trading Guide For Beginners"

**Stated**
- MACD(12, 26, 9) on close. MACD line = EMA12 - EMA26; signal = EMA9 of MACD line.
- Long when the MACD line crosses above the signal line.
- Sell signal on the reverse cross.
- Speaker notes a cross is "more significant" on the appropriate side of zero. Advisory,
  not a rule, so it is not implemented as a filter.
- No stop stated. No target stated. No timeframe stated ("no such thing as a best time").

**Invented**
1. Fill timing: next bar open. The video does not say when the order goes in.
2. Position model: **long/flat** is primary. A variant, `s1_flip` (always in the market,
   long or short), is declared here and run alongside, because the video's wording supports
   either reading. Both are reported; neither is picked after the fact.
3. Timeframe: daily primary, 4h secondary. Declared now because the video names none.
   These are the only two that will ever be run.

## S2: Donchian channel breakout
Source: `notes/fmS_rUcKF6c.md`, "Trading With EXIT Indicators To Lock More Profits"

**Stated**
- Entry: close above the 20-period Donchian high (long) or below the 20-period low (short).
- Initial stop: 2 x ATR(20).
- Two exits offered, explicitly "depends on your risk aversion":
  (a) close back through the opposite band, (b) touch of the midpoint of a 50-period channel.
- Daily charts.

**Invented**
1. The 20-period high/low **excludes the current bar**. Including it makes the breakout
   condition trivially unsatisfiable-or-always-true depending on tie handling, and the video
   does not specify. This also removes a look-ahead path.
2. Exit choice: the video mandates neither, so **both are run** as `s2_mid` and `s2_band`.
   Declared in advance, both reported.

## S3: MFI centreline crossover with 200 EMA filter
Source: `notes/bAT6F7x9K8M.md`, "RSI vs MFI Trading Strategies"

**Stated**
- MFI period 50, deliberately raised from the default 14 to cut noise.
- Long signal when MFI crosses above 50, short signal when it crosses below 50.
- 200-period EMA trend filter: only take longs when price is above it, shorts when below.
- No stop stated. No target stated. No timeframe stated.
- The speaker's own warning, quoted: a 50-level crossover system "traded by itself is not
  reliable in the long run".

**Invented**
1. Stop: 2 x ATR(14). Nothing is stated. A no-stop variant `s3_nostop`, exiting only on the
   opposite crossover, is declared here and run alongside.
2. Exit: opposite 50-crossover.
3. Timeframe: daily.

**Not done**: the speaker says "play with the periods of the MFI and even the period of the
EMA and backtest yourself to find the best settings". That is an invitation to curve-fit on
this exact data. The stated 50/200 are used and no period is swept.

## S4: Daily outside bar in the 20/50 EMA pullback zone
Source: `notes/s4DSY3Y_N4Y.md`, "If I Had $100 & Only 30 Mins to Trade, I'd Do THIS"

**Stated**
- Daily only, called non-negotiable.
- EMA20 and EMA50 on daily close.
- Trend filter, all three required: EMA20 above EMA50 for longs (below for shorts); both
  EMAs sloping the same way; price on the correct side of both.
- Pullback zone: the band between EMA20 and EMA50. Price must trade into it.
- Setup dies if a daily candle closes beyond the EMA50.
- Trigger: an outside bar whose body covers the prior candle's body and which breaks both
  the prior high and the prior low, closing in the trend direction, located inside the zone.
- Entry at the close of the outside bar.
- Stop just beyond the opposite extreme of the outside bar.
- Exit tiers: 50% off at 1R; then stop to breakeven on the remainder; then trail under the
  most recent swing low (above the swing high for shorts), updated only on daily closes.

**Invented**
1. "Sloping cleanly, not flat or tangled" is a hard pass/fail gate with no number attached.
   Implemented as: both EMAs strictly monotonic in the same direction over the last 5 bars.
2. "Most recent swing low" has no lookback. Implemented as a 5-bar fractal pivot (2 bars
   either side, confirmed 2 bars later), matching the pivot convention already used in this
   repository.
3. "Just beyond" the outside bar extreme: no buffer is added. Stop sits exactly at the bar's
   low (longs) or high (shorts).
4. **Amendment, logged before any run.** "Located inside the pullback zone" needs an operational
   test and the video gives none. Implemented as: the outside bar's low reaches at or below the
   EMA20 and its high reaches at or above the EMA50 (mirrored for shorts), with the bar's close
   still on the live side of the EMA50. This makes S4 a 4-assumption strategy, not the
   3 the audit counted. Recorded here rather than quietly absorbed into the code.

## S2 amendment, logged before any run

The 2 x ATR(20) stop is anchored to the **fill price**, not to the signal bar's close, since
the fill happens one bar later and the video says the stop is a volatility distance from the
trade. ATR is read at the signal bar. This is an implementation reading, not a new parameter.

---

## Declared run list

Fixed before execution. Nothing outside this list is run, and nothing in it is dropped
because its results are unflattering.

| id | Strategy | Timeframe |
|---|---|---|
| s1_flat | MACD crossover, long/flat | 1D |
| s1_flip | MACD crossover, always-in | 1D |
| s1_flat_4h | MACD crossover, long/flat | 4h |
| s1_flip_4h | MACD crossover, always-in | 4h |
| s2_mid | Donchian, 50-channel midpoint exit | 1D |
| s2_band | Donchian, opposite-band exit | 1D |
| s3_atr | MFI/EMA, 2xATR(14) stop | 1D |
| s3_nostop | MFI/EMA, no stop | 1D |
| s4 | Outside bar tiered exit | 1D |

Nine runs. That is nine chances for one to look good by luck, and the report must say so
rather than present the best one as a finding.

## Kill criteria (pre-committed)

A run is dead if, on the studied span after 0.10% round-trip costs, any of:
- net expectancy per trade <= 0
- fewer than 30 trades, in which case it is not dead but **undecidable**, and is reported as
  having produced too little evidence to judge either way
- profit factor < 1.0

Surviving means "not yet falsified on one instrument over one span". It does not mean the
strategy works, and the report must not imply otherwise.
