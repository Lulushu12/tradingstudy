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

## E001 (descriptive, counts: no)
- Date: 2026-11-15
- Hypothesis: none. Indicator matching to choose the Money Flow formula (user approved choosing by agreement with
  the TradingView exports). No trade outcomes involved.
- Configuration: candidates vs real MCB BTC exports: MCB_Clone_v1 formula; brief clone formula; HTF formula grid
  (440 settings: 3x TF and fixed 3H, developing and step, SMA 10-30, EMA 1-10); PineScript-family grid (126 settings);
  4 structural variants; Heikin-Ashi grid (45 settings). Fitted on BTC 15m 2022-01..2023-12 only.
- Split: dev rows of the exports only.
- Results: chosen = MCB_Clone_v1 formula on Heikin-Ashi candles, no outer EMA: corr 0.989-0.995, 94-96% sign
  agreement on 5m..1D including unseen years. Full table: reports/phase1/MCB_VALIDATION.md.
- Verdict: n/a (feature selection by indicator agreement).

## E002 (descriptive, counts: no)
- Date: 2026-11-15
- Hypothesis: none. Census for Gate 1 proposals: tick sizes, 1m ranges, fee in R, event counts per day, range-flip
  counts across k / tolerance / height, regime shares. No outcomes after any event were computed.
- Split: dev only.
- Results: reports/phase1/gate1_facts.json and GATE1_REPORT.md section 2. Range tolerance and height proposals were
  chosen from event counts only.
- Verdict: n/a.
