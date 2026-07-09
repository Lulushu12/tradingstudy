# FROZEN SPEC: XRP HA/SHA/MFI TREND CONTINUATION

Drafted 2026-07-09 from the trader's written rule, before any signal count,
backtest, or P&L number existed on this data. IMMUTABLE once the trader
approves it in conversation. Any request to change it after results exist
will be refused; the refusal is the point.

## Instrument and data

- BINANCE XRPUSDT perpetual, 15m bars, TradingView export chunks in
  "HA SHA MFI/" (chunks 1-22 plus the unnumbered base file).
- Span: 2020-01-06 08:15 UTC through 2026-07-09 15:15 UTC bar opens.
- Known hole: 2025-09-08 21:00 through 2025-09-09 10:45 UTC (about 56
  bars). Any other hole found at Gate 0 gets documented before anything
  runs.
- Exported columns: real OHLC ("Bars"), Hollow Candles OHLC, Smoothed
  Heiken Ashi OHLC, main chart series, "Mny Flow". Column identity is
  verified at Gate 0, not assumed.

## Indicators (all parameters fixed here)

- Heikin Ashi, standard: haClose = (o+h+l+c)/4; haOpen = (prev haOpen +
  prev haClose)/2, seeded (o+c)/2 on the first bar; haHigh = max(h,
  haOpen, haClose); haLow = min(l, haOpen, haClose). Computed from real
  OHLC.
- Smoothed Heikin Ashi: before-smoothing SMA length 1 (identity), then
  Heikin Ashi, then EMA length 10 on each HA component. Verified against
  the exported SHA columns at Gate 0.
- Money Flow: mfi_clone in audit/mcb_port.py with period 60, mult 150,
  posY 2.5, stdev length 7, outer EMA smooth 4. The output already
  includes the Y offset; "above 0" means this displayed value > 0, per
  the trader 2026-07-09. Whether the chart fed it real or HA candles is
  resolved empirically at Gate 0 against the exported Mny Flow column;
  whichever matches is the spec.

## Rule (long side; shorts fully mirrored)

Definitions on HA candles: red = haClose < haOpen; green =
haClose > haOpen. A momentum candle is a green HA candle with no lower
wick: haLow >= haOpen minus float tolerance (1e-9 relative).

Window: let bar r be the most recent red HA candle. The window is bars
r+1, r+2, r+3. Signal conditions at bar t close, where t is in the
window:

1. Mny Flow at t > 0 (displayed value).
2. SHA bullish at t: shaClose > shaOpen.
3. Bar t is a momentum candle.
4. No earlier bar in this window already produced an ENTRY (the first
   actual entry in the window consumes it; signals skipped by the
   minimum stop distance rule do not, per R7 below).

Entry: market at bar t+1 open.

Stop loss: the real (not HA) low of bar t. If the stop distance is less
than 0.6% of the entry price the entry is INVALID and skipped
(resolution R7, amended by the trader 2026-07-09 pre-freeze: a skipped
entry does NOT consume the window; a later bar inside the same 3-candle
window that meets all conditions is still a valid entry. Only an actual
entry consumes the window).

Take profit: 2R (entry + 2 x stop distance for longs).

No time exit. A position runs until SL or TP.

Concurrency: every valid signal opens an independent position at 0.5%
risk, same or opposite direction as anything already open.

## Execution and cost model (identical to AUDIT_COMMITMENTS.md)

- Commission 0.08% of notional per round trip.
- Slippage 1 bp per fill (entries, stops, targets). Sweep reported over
  {0, 1, 2, 3, 5, 10} bp with breakeven level.
- Swap 0.0055% of notional per 4h UTC boundary (00/04/08/12/16/20)
  crossed while open.
- Risk 0.5% of current equity per trade.
- Same-bar SL+TP ambiguity resolved as SL (worst case), counted.
- Adverse gap through SL exits at the bar open (worse than SL);
  favorable gap through TP exits at the bar open (symmetric).

## Segments

- SANDBOX: 2020-01-06 through 2023-12-31.
- VALIDATION: 2024-01-01 through 2026-06-21 16:45 UTC bar opens. Touched
  exactly once, only after the sandbox verdict, only with the trader's
  explicit written go.
- TAIL (unscored): everything after 2026-06-21 16:45 stays out of every
  report, mirroring the BTC holdout boundary. It is semi-clean at best
  (the trader's charts have shown it) and is reserved for a possible
  forward check, never for selection.

## Pass bars and kill checks (frozen)

- Sandbox: net expectancy >= +0.15R and more than half of the half-year
  windows nonnegative. Fail either: DEAD.
- Validation: net expectancy >= +0.10R on >= 100 trades, majority of
  windows nonnegative. Fail: DEAD.
- K1 pooled net expectancy <= 0: KILL. K2 more than half of windows
  negative: KILL. K3 breakeven slippage < 3 bp: KILL. K4 pooled net
  expectancy <= 0 after removing the single best window: KILL.
- K5 for any final survivor: bootstrap at 0.5% sizing against the
  Breakout 1-Step Classic $10k limits (3% daily, 6% static, equity
  including floating PnL, one touch forfeits). Breach probability
  within one year > 50%: untradeable at the venue.
- A kill is a kill. No re-thresholding, no reruns, no optimization.

## Contamination statement (trader, 2026-07-09, verbatim substance)

The idea came from a YouTube video. The trader once built a spreadsheet
backtest showing an "insane winrate" and does not trust it; that
spreadsheet is the reason for this audit. Last touched at least 6 months
ago (not in 2026). The rule was not derived from recent XRP price
action. The trader has seen the full chart history on TradingView, so no
segment of this export is blind; only future forward data is clean.

## Family prior (required honesty clause)

HA and momentum-candle TA families were scanned in the prior BTC study
(study/STRATEGY_FINDINGS.md) and nothing from them survived the cost
stack. Different instrument, same family. Base-rate expectation is
death. Spreadsheet win rates without frozen costs and window discipline
routinely evaporate under this audit; that is the working hypothesis
until the data says otherwise.

## Process

- Gate 0 first: merge, dedup, integrity check, column identification,
  port validation of HA, SHA, and Mny Flow against exported columns.
  Tolerance target 1e-7 relative or an explained, bounded mismatch. Port
  failure stops the study.
- Every executed test is logged in "HA SHA MFI/TEST_LEDGER.md".
- Each phase (Gate 0, sandbox, validation) requires the trader's
  explicit written go before it runs.
