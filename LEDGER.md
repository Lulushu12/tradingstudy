# LEDGER

Every experiment, in order. Never delete or overwrite an entry. Failed experiments stay.
Fields: id, date, hypothesis, configuration, split, results, verdict.
The experiment budget (frozen at Gate 1) counts entries marked `counts: yes`.

---

## E000 (descriptive, counts: no)
- Date: 2026-11-15
- Hypothesis: none. Descriptive data statistic to inform the Gate 1 grid, not a strategy test. No signal, entry or
  outcome was evaluated.
- Configuration: round-trip fee 0.08% divided by stop distance (1.0, 1.5, 2.0 x ATR14 Wilder), BTC only, using the
  repo's TradingView OHLC (5m as proxy for 6m, 30m as proxy for 24m).
- Split: 2022-01-01 to 2025-10-31 (dev only).
- Results (median fee in R, 1.0 / 1.5 / 2.0 x ATR): 5m 0.48 / 0.32 / 0.24; 15m 0.25 / 0.17 / 0.13;
  30m 0.17 / 0.12 / 0.09; 1h 0.12 / 0.08 / 0.06.
- Verdict: n/a. Recompute on Binance data for all coins and the real 6m/24m bars in Phase 1.
