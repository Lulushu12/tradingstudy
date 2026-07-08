# AUDIT COMMITMENTS

Frozen 2026-07-08, before any backtest or P&L computation existed.
IMMUTABLE once Phase 1 results exist. Any request to change this file after
results exist will be refused; that refusal is the point of this file.

## Data

- Studied set: merged Binance BTCUSDT perp 15m bars, 2021-01-07 07:00 UTC
  through 2026-06-21 16:45 UTC bar opens (audit/data_check.py output),
  191,170 bars, integrity as documented in audit/GATE0_REPORT.md section 2.
- Holdout: everything at or after 2026-06-21 17:00 UTC, quarantined per
  HOLDOUT_DO_NOT_TOUCH.md. Untouched until the final holdout test, which
  requires the trader's separate explicit go.
- Known hole: 2025-03-01 through 2025-06-30 absent from the studied set.

## Costs (every fill, both variants)

- Commission: 0.04% per side, 0.08% per round trip (verified against
  Breakout published fees).
- Slippage: 1 bp (0.01%) per fill baseline: entries, stops, targets.
  Agreed after auditor refused the trader's zero-slippage proposal.
- Swap: Breakout terminal model, 0.0055% of position notional charged at
  each 4h UTC boundary (00/04/08/12/16/20) crossed while the position is
  open.
- Phase 1 sweeps slippage over {0, 1, 2, 3, 5, 10} bp per fill and reports
  the breakeven level.

## Sizing and trade rules

- SPEC AMENDMENT 1 (blind, logged 2026-07-08): risk per trade is 0.5% of
  current equity (supersedes the 1% in FROZEN_SPEC.md section 5). All other
  section 5 rules unchanged: SL from ATR14-RMA band extremes over t-5..t-1,
  skip if stop distance < 0.6% of entry, fixed 2:1 R take profit, market
  orders only.
- Concurrency: every signal opens an INDEPENDENT position at 0.5% risk,
  same direction or opposite, each running to its own SL/TP. Both-stops-hit
  chop scenarios are counted.
- Dedup rule (stack shared legs): when a signal fires, both of its legs are
  consumed for that variant and direction; any later pair re-using a
  consumed leg is not a trade. First completion wins.
- Variant B semantics as confirmed by the trader: front-run completes only
  at bar t >= leg 1's confirmation bar with t - leg1_pivot <= 11; pre-div
  raw condition per the coded logic with preDivMaxAge 50, swing buffer 5;
  current-turn zero-line filter per the coded defaults (bull turn requires
  the oscillator below 0, bear above 0); one-bar tick in the reversal
  direction; entry at bar t+1 open. Variant A: confirmation-bar gap <= 11,
  entry at the bar after the later confirmation.

## Walk-forward window scheme

Ten consecutive calendar half-year windows, 2021H1 through 2026H1 (2021H1,
2025H1, 2025H2, 2026H1 partial per data coverage). No parameter is fit in
Phase 1; windows are evaluation segments and every number is in-sample by
construction. Regime labels, pre-committed:

- Trend, per day from the 1D series: bull if close > SMA200 and SMA200 is
  above its own value 20 days earlier; bear if close < SMA200 and SMA200 is
  below its value 20 days earlier; chop otherwise.
- Volatility, per day: 30-day realized vol of daily log returns; high if
  above the studied-span median, low otherwise.
- A trade inherits the labels of its entry day.

## Kill thresholds (per variant; K1-K4 failure of both variants = system dead)

- K1 Expectancy: pooled net expectancy per trade <= 0 after all costs: KILL.
- K2 Consistency: more than half of the windows negative: KILL.
- K3 Cost headroom: breakeven slippage below 3 bp per fill: KILL.
- K4 Concentration: pooled net expectancy <= 0 after removing the single
  best window: KILL.
- K5 Venue survivability: bootstrap the observed trade sequence at 0.5%
  risk sizing against the agreed account, Breakout 1-Step Classic $10k
  (max daily loss 3% of balance recalculated 00:30 UTC; static max drawdown
  6% of starting balance; both on equity including floating PnL; one touch
  forfeits). If the estimated probability of breaching either limit within
  one year of trading exceeds 50%, the system as specified is untradeable
  at this venue regardless of K1-K4.

A kill is a kill. Optimization is not a resurrection tool. If Phase 1 kills
a variant, it stays dead on studied data. Surviving means "not yet
falsified", nothing more.
