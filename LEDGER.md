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

## Phase 2 baselines (counts: yes, 212 configurations)
- Date: 2026-11-15. Split: walk-forward test period 2023-01-01..2025-11-14, fixed rules (no fitting), all 9 coins.
- Columns: n = filled trades; exp = net expectancy R; folds+ = positive folds of 6; coins+ = positive coins of 9; verdict = protocol criteria failed (S6/S10 n/a for fixed baselines).

| id | hypothesis | configuration | n | exp R | PF | fee R | folds+ | coins+ | DSR | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| P2-001 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 6m A stop 2.0xATR tgt 1R | 12471 | -0.226 | 0.65 | 0.141 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-002 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 6m A stop 2.0xATR tgt 1.5R | 11097 | -0.238 | 0.69 | 0.140 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-003 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 6m A stop 2.0xATR tgt 2R | 9896 | -0.241 | 0.71 | 0.140 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-004 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 6m A stop 2.0xATR tgt 3R | 8615 | -0.245 | 0.73 | 0.137 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-005 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 6m A stop 2.0xATR tgt fib1.272 | 8562 | -0.232 | 0.74 | 0.137 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-006 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 6m A stop 2.0xATR tgt fib1.618 | 7905 | -0.244 | 0.74 | 0.136 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-007 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 6m A stop 2.0xATR tgt next_level | 6245 | -0.240 | 0.69 | 0.147 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-008 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 6m B stop 2.0xATR tgt 1R | 11712 | -0.240 | 0.63 | 0.141 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-009 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 6m B stop 2.0xATR tgt 1.5R | 10501 | -0.254 | 0.67 | 0.142 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-010 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 6m B stop 2.0xATR tgt 2R | 9574 | -0.246 | 0.71 | 0.140 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-011 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 6m B stop 2.0xATR tgt 3R | 8639 | -0.240 | 0.74 | 0.138 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-012 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 6m B stop 2.0xATR tgt fib1.272 | 8401 | -0.211 | 0.77 | 0.138 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-013 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 6m B stop 2.0xATR tgt fib1.618 | 7804 | -0.240 | 0.75 | 0.137 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-014 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 6m B stop 2.0xATR tgt next_level | 5648 | -0.264 | 0.67 | 0.148 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-015 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 15m A stop 1.5xATR tgt 1R | 7340 | -0.141 | 0.76 | 0.104 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-016 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 15m A stop 1.5xATR tgt 1.5R | 6415 | -0.176 | 0.75 | 0.105 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-017 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 15m A stop 1.5xATR tgt 2R | 5890 | -0.172 | 0.78 | 0.105 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-018 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 15m A stop 1.5xATR tgt 3R | 5324 | -0.151 | 0.82 | 0.105 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-019 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 15m A stop 1.5xATR tgt fib1.272 | 5085 | -0.159 | 0.82 | 0.105 | 0/6 | 1/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-020 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 15m A stop 1.5xATR tgt fib1.618 | 4913 | -0.172 | 0.81 | 0.105 | 1/6 | 1/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-021 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 15m A stop 1.5xATR tgt next_level | 3645 | -0.157 | 0.79 | 0.107 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-022 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 15m A stop 2.0xATR tgt 1R | 6501 | -0.131 | 0.77 | 0.079 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-023 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 15m A stop 2.0xATR tgt 1.5R | 5670 | -0.131 | 0.81 | 0.079 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-024 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 15m A stop 2.0xATR tgt 2R | 5205 | -0.138 | 0.81 | 0.079 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-025 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 15m A stop 2.0xATR tgt 3R | 4716 | -0.120 | 0.85 | 0.078 | 1/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-026 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 15m A stop 2.0xATR tgt fib1.272 | 4759 | -0.115 | 0.85 | 0.079 | 1/6 | 1/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-027 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 15m A stop 2.0xATR tgt fib1.618 | 4576 | -0.112 | 0.86 | 0.078 | 1/6 | 1/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-028 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 15m A stop 2.0xATR tgt next_level | 2768 | -0.133 | 0.81 | 0.082 | 0/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-029 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 15m B stop 1.5xATR tgt 1R | 6770 | -0.161 | 0.73 | 0.106 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-030 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 15m B stop 1.5xATR tgt 1.5R | 6075 | -0.168 | 0.76 | 0.106 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-031 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 15m B stop 1.5xATR tgt 2R | 5727 | -0.174 | 0.78 | 0.107 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-032 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 15m B stop 1.5xATR tgt 3R | 5192 | -0.165 | 0.81 | 0.106 | 0/6 | 1/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-033 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 15m B stop 1.5xATR tgt fib1.272 | 4927 | -0.187 | 0.79 | 0.106 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-034 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 15m B stop 1.5xATR tgt fib1.618 | 4767 | -0.184 | 0.80 | 0.106 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-035 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 15m B stop 1.5xATR tgt next_level | 3346 | -0.162 | 0.79 | 0.110 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-036 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 15m B stop 2.0xATR tgt 1R | 6108 | -0.126 | 0.78 | 0.080 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-037 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 15m B stop 2.0xATR tgt 1.5R | 5483 | -0.128 | 0.81 | 0.080 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-038 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 15m B stop 2.0xATR tgt 2R | 5068 | -0.123 | 0.83 | 0.080 | 1/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-039 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 15m B stop 2.0xATR tgt 3R | 4611 | -0.139 | 0.83 | 0.080 | 1/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-040 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 15m B stop 2.0xATR tgt fib1.272 | 4616 | -0.147 | 0.81 | 0.080 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-041 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 15m B stop 2.0xATR tgt fib1.618 | 4478 | -0.143 | 0.82 | 0.080 | 1/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-042 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 15m B stop 2.0xATR tgt next_level | 2534 | -0.133 | 0.81 | 0.085 | 0/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-043 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 24m A stop 1.5xATR tgt 1R | 4887 | -0.154 | 0.74 | 0.083 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-044 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 24m A stop 1.5xATR tgt 1.5R | 4354 | -0.168 | 0.76 | 0.082 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-045 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 24m A stop 1.5xATR tgt 2R | 4143 | -0.162 | 0.79 | 0.083 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-046 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 24m A stop 1.5xATR tgt 3R | 3859 | -0.154 | 0.81 | 0.083 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-047 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 24m A stop 1.5xATR tgt fib1.272 | 3743 | -0.161 | 0.81 | 0.083 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-048 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 24m A stop 1.5xATR tgt fib1.618 | 3656 | -0.173 | 0.80 | 0.082 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-049 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 24m A stop 1.5xATR tgt next_level | 2433 | -0.180 | 0.76 | 0.085 | 1/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-050 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 24m A stop 2.0xATR tgt 1R | 4308 | -0.128 | 0.78 | 0.062 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-051 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 24m A stop 2.0xATR tgt 1.5R | 3886 | -0.129 | 0.80 | 0.062 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-052 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 24m A stop 2.0xATR tgt 2R | 3661 | -0.129 | 0.82 | 0.062 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-053 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 24m A stop 2.0xATR tgt 3R | 3457 | -0.134 | 0.82 | 0.062 | 1/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-054 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 24m A stop 2.0xATR tgt fib1.272 | 3448 | -0.135 | 0.81 | 0.062 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-055 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 24m A stop 2.0xATR tgt fib1.618 | 3391 | -0.137 | 0.82 | 0.062 | 1/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-056 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 24m A stop 2.0xATR tgt next_level | 1855 | -0.169 | 0.75 | 0.065 | 0/6 | 1/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-057 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 24m B stop 1.5xATR tgt 1R | 4474 | -0.157 | 0.74 | 0.082 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-058 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 24m B stop 1.5xATR tgt 1.5R | 4042 | -0.166 | 0.76 | 0.082 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-059 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 24m B stop 1.5xATR tgt 2R | 3861 | -0.169 | 0.78 | 0.083 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-060 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 24m B stop 1.5xATR tgt 3R | 3621 | -0.141 | 0.83 | 0.082 | 1/6 | 1/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-061 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 24m B stop 1.5xATR tgt fib1.272 | 3513 | -0.178 | 0.79 | 0.082 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-062 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 24m B stop 1.5xATR tgt fib1.618 | 3456 | -0.173 | 0.80 | 0.082 | 1/6 | 1/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-063 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 24m B stop 1.5xATR tgt next_level | 2250 | -0.152 | 0.79 | 0.086 | 1/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-064 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 24m B stop 2.0xATR tgt 1R | 3999 | -0.127 | 0.78 | 0.062 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-065 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 24m B stop 2.0xATR tgt 1.5R | 3646 | -0.123 | 0.81 | 0.062 | 1/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-066 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 24m B stop 2.0xATR tgt 2R | 3468 | -0.112 | 0.84 | 0.062 | 1/6 | 1/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-067 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 24m B stop 2.0xATR tgt 3R | 3291 | -0.133 | 0.82 | 0.062 | 1/6 | 1/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-068 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 24m B stop 2.0xATR tgt fib1.272 | 3293 | -0.139 | 0.81 | 0.062 | 1/6 | 1/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-069 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 24m B stop 2.0xATR tgt fib1.618 | 3259 | -0.129 | 0.83 | 0.062 | 1/6 | 2/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-070 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 24m B stop 2.0xATR tgt next_level | 1672 | -0.169 | 0.75 | 0.066 | 1/6 | 2/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-071 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 1h A stop 1.5xATR tgt 1R | 2272 | -0.049 | 0.91 | 0.048 | 2/6 | 2/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-072 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 1h A stop 1.5xATR tgt 1.5R | 2079 | -0.057 | 0.90 | 0.048 | 2/6 | 2/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-073 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 1h A stop 1.5xATR tgt 2R | 2000 | -0.060 | 0.90 | 0.048 | 2/6 | 3/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-074 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 1h A stop 1.5xATR tgt 3R | 1952 | -0.062 | 0.90 | 0.048 | 0/6 | 4/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-075 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 1h A stop 1.5xATR tgt fib1.272 | 1933 | -0.076 | 0.88 | 0.048 | 1/6 | 3/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-076 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 1h A stop 1.5xATR tgt fib1.618 | 1934 | -0.074 | 0.89 | 0.048 | 1/6 | 3/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-077 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 1h A stop 1.5xATR tgt next_level | 1230 | -0.081 | 0.87 | 0.048 | 0/6 | 2/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-078 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 1h A stop 2.0xATR tgt 1R | 1996 | -0.040 | 0.92 | 0.036 | 2/6 | 2/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-079 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 1h A stop 2.0xATR tgt 1.5R | 1868 | -0.046 | 0.91 | 0.036 | 2/6 | 2/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-080 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 1h A stop 2.0xATR tgt 2R | 1831 | -0.050 | 0.91 | 0.036 | 0/6 | 2/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-081 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 1h A stop 2.0xATR tgt 3R | 1802 | -0.044 | 0.92 | 0.036 | 2/6 | 4/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-082 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 1h A stop 2.0xATR tgt fib1.272 | 1783 | -0.056 | 0.90 | 0.036 | 1/6 | 1/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-083 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 1h A stop 2.0xATR tgt fib1.618 | 1795 | -0.054 | 0.90 | 0.036 | 2/6 | 2/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-084 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 1h A stop 2.0xATR tgt next_level | 953 | -0.087 | 0.84 | 0.036 | 0/6 | 2/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-085 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 1h B stop 1.5xATR tgt 1R | 2087 | -0.079 | 0.85 | 0.048 | 1/6 | 1/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-086 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 1h B stop 1.5xATR tgt 1.5R | 1944 | -0.090 | 0.85 | 0.048 | 0/6 | 2/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-087 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 1h B stop 1.5xATR tgt 2R | 1875 | -0.081 | 0.87 | 0.048 | 0/6 | 2/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-088 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 1h B stop 1.5xATR tgt 3R | 1825 | -0.080 | 0.88 | 0.048 | 1/6 | 1/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-089 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 1h B stop 1.5xATR tgt fib1.272 | 1801 | -0.077 | 0.88 | 0.048 | 1/6 | 1/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-090 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 1h B stop 1.5xATR tgt fib1.618 | 1807 | -0.076 | 0.88 | 0.048 | 1/6 | 1/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-091 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 1h B stop 1.5xATR tgt next_level | 1134 | -0.109 | 0.83 | 0.049 | 0/6 | 2/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-092 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 1h B stop 2.0xATR tgt 1R | 1874 | -0.069 | 0.86 | 0.036 | 0/6 | 1/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-093 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 1h B stop 2.0xATR tgt 1.5R | 1774 | -0.070 | 0.87 | 0.036 | 0/6 | 2/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-094 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 1h B stop 2.0xATR tgt 2R | 1729 | -0.078 | 0.86 | 0.036 | 0/6 | 2/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-095 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 1h B stop 2.0xATR tgt 3R | 1707 | -0.075 | 0.87 | 0.036 | 1/6 | 2/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-096 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 1h B stop 2.0xATR tgt fib1.272 | 1678 | -0.080 | 0.86 | 0.036 | 0/6 | 2/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-097 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 1h B stop 2.0xATR tgt fib1.618 | 1696 | -0.077 | 0.86 | 0.036 | 0/6 | 1/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-098 | Baseline 1 (user's WT + MF regular divergence stack) has positive net expectancy | B1 1h B stop 2.0xATR tgt next_level | 866 | -0.130 | 0.78 | 0.037 | 0/6 | 1/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-099 | Baseline 2 (plain range flip) has positive net expectancy | B2 6m A stop 2.0xATR tgt 1R | 1493 | -0.260 | 0.61 | 0.144 | 0/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-100 | Baseline 2 (plain range flip) has positive net expectancy | B2 6m A stop 2.0xATR tgt 1.5R | 1483 | -0.275 | 0.65 | 0.144 | 0/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-101 | Baseline 2 (plain range flip) has positive net expectancy | B2 6m A stop 2.0xATR tgt 2R | 1478 | -0.297 | 0.65 | 0.144 | 0/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-102 | Baseline 2 (plain range flip) has positive net expectancy | B2 6m A stop 2.0xATR tgt 3R | 1467 | -0.342 | 0.64 | 0.144 | 0/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-103 | Baseline 2 (plain range flip) has positive net expectancy | B2 6m A stop 2.0xATR tgt fib1.272 | 1465 | -0.324 | 0.65 | 0.144 | 0/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-104 | Baseline 2 (plain range flip) has positive net expectancy | B2 6m A stop 2.0xATR tgt fib1.618 | 1456 | -0.365 | 0.63 | 0.145 | 0/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-105 | Baseline 2 (plain range flip) has positive net expectancy | B2 6m A stop 2.0xATR tgt next_level | 625 | -0.315 | 0.61 | 0.149 | 0/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-106 | Baseline 2 (plain range flip) has positive net expectancy | B2 6m B stop 2.0xATR tgt 1R | 2168 | -0.216 | 0.66 | 0.144 | 0/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-107 | Baseline 2 (plain range flip) has positive net expectancy | B2 6m B stop 2.0xATR tgt 1.5R | 2145 | -0.255 | 0.67 | 0.145 | 0/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-108 | Baseline 2 (plain range flip) has positive net expectancy | B2 6m B stop 2.0xATR tgt 2R | 2133 | -0.280 | 0.67 | 0.144 | 0/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-109 | Baseline 2 (plain range flip) has positive net expectancy | B2 6m B stop 2.0xATR tgt 3R | 2099 | -0.307 | 0.68 | 0.144 | 0/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-110 | Baseline 2 (plain range flip) has positive net expectancy | B2 6m B stop 2.0xATR tgt fib1.272 | 2106 | -0.278 | 0.70 | 0.144 | 0/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-111 | Baseline 2 (plain range flip) has positive net expectancy | B2 6m B stop 2.0xATR tgt fib1.618 | 2069 | -0.347 | 0.65 | 0.145 | 0/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-112 | Baseline 2 (plain range flip) has positive net expectancy | B2 6m B stop 2.0xATR tgt next_level | 662 | -0.270 | 0.66 | 0.154 | 0/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-113 | Baseline 2 (plain range flip) has positive net expectancy | B2 15m A stop 1.5xATR tgt 1R | 622 | -0.177 | 0.71 | 0.111 | 0/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-114 | Baseline 2 (plain range flip) has positive net expectancy | B2 15m A stop 1.5xATR tgt 1.5R | 621 | -0.108 | 0.84 | 0.111 | 2/6 | 3/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-115 | Baseline 2 (plain range flip) has positive net expectancy | B2 15m A stop 1.5xATR tgt 2R | 621 | -0.098 | 0.87 | 0.110 | 0/6 | 4/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-116 | Baseline 2 (plain range flip) has positive net expectancy | B2 15m A stop 1.5xATR tgt 3R | 620 | -0.130 | 0.85 | 0.111 | 1/6 | 2/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-117 | Baseline 2 (plain range flip) has positive net expectancy | B2 15m A stop 1.5xATR tgt fib1.272 | 618 | -0.132 | 0.85 | 0.111 | 2/6 | 2/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-118 | Baseline 2 (plain range flip) has positive net expectancy | B2 15m A stop 1.5xATR tgt fib1.618 | 617 | -0.208 | 0.78 | 0.111 | 1/6 | 1/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-119 | Baseline 2 (plain range flip) has positive net expectancy | B2 15m A stop 1.5xATR tgt next_level | 339 | -0.168 | 0.78 | 0.113 | 0/6 | 1/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-120 | Baseline 2 (plain range flip) has positive net expectancy | B2 15m A stop 2.0xATR tgt 1R | 627 | -0.068 | 0.88 | 0.083 | 2/6 | 2/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-121 | Baseline 2 (plain range flip) has positive net expectancy | B2 15m A stop 2.0xATR tgt 1.5R | 626 | -0.042 | 0.93 | 0.083 | 2/6 | 4/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-122 | Baseline 2 (plain range flip) has positive net expectancy | B2 15m A stop 2.0xATR tgt 2R | 623 | -0.058 | 0.92 | 0.083 | 2/6 | 4/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-123 | Baseline 2 (plain range flip) has positive net expectancy | B2 15m A stop 2.0xATR tgt 3R | 622 | -0.074 | 0.91 | 0.083 | 2/6 | 3/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-124 | Baseline 2 (plain range flip) has positive net expectancy | B2 15m A stop 2.0xATR tgt fib1.272 | 620 | -0.050 | 0.93 | 0.083 | 3/6 | 3/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-125 | Baseline 2 (plain range flip) has positive net expectancy | B2 15m A stop 2.0xATR tgt fib1.618 | 620 | -0.098 | 0.88 | 0.083 | 2/6 | 4/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-126 | Baseline 2 (plain range flip) has positive net expectancy | B2 15m A stop 2.0xATR tgt next_level | 271 | -0.078 | 0.88 | 0.085 | 3/6 | 2/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-127 | Baseline 2 (plain range flip) has positive net expectancy | B2 15m B stop 1.5xATR tgt 1R | 870 | -0.162 | 0.73 | 0.110 | 0/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-128 | Baseline 2 (plain range flip) has positive net expectancy | B2 15m B stop 1.5xATR tgt 1.5R | 870 | -0.141 | 0.80 | 0.110 | 0/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-129 | Baseline 2 (plain range flip) has positive net expectancy | B2 15m B stop 1.5xATR tgt 2R | 869 | -0.145 | 0.81 | 0.110 | 0/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-130 | Baseline 2 (plain range flip) has positive net expectancy | B2 15m B stop 1.5xATR tgt 3R | 866 | -0.109 | 0.87 | 0.110 | 1/6 | 2/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-131 | Baseline 2 (plain range flip) has positive net expectancy | B2 15m B stop 1.5xATR tgt fib1.272 | 864 | -0.102 | 0.88 | 0.110 | 1/6 | 3/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-132 | Baseline 2 (plain range flip) has positive net expectancy | B2 15m B stop 1.5xATR tgt fib1.618 | 862 | -0.157 | 0.83 | 0.110 | 1/6 | 2/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-133 | Baseline 2 (plain range flip) has positive net expectancy | B2 15m B stop 1.5xATR tgt next_level | 319 | -0.225 | 0.71 | 0.116 | 0/6 | 1/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-134 | Baseline 2 (plain range flip) has positive net expectancy | B2 15m B stop 2.0xATR tgt 1R | 872 | -0.103 | 0.82 | 0.083 | 0/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-135 | Baseline 2 (plain range flip) has positive net expectancy | B2 15m B stop 2.0xATR tgt 1.5R | 871 | -0.112 | 0.83 | 0.083 | 0/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-136 | Baseline 2 (plain range flip) has positive net expectancy | B2 15m B stop 2.0xATR tgt 2R | 869 | -0.093 | 0.87 | 0.083 | 1/6 | 1/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-137 | Baseline 2 (plain range flip) has positive net expectancy | B2 15m B stop 2.0xATR tgt 3R | 865 | -0.109 | 0.86 | 0.083 | 1/6 | 1/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-138 | Baseline 2 (plain range flip) has positive net expectancy | B2 15m B stop 2.0xATR tgt fib1.272 | 866 | -0.085 | 0.89 | 0.083 | 2/6 | 2/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-139 | Baseline 2 (plain range flip) has positive net expectancy | B2 15m B stop 2.0xATR tgt fib1.618 | 862 | -0.138 | 0.84 | 0.083 | 1/6 | 1/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-140 | Baseline 2 (plain range flip) has positive net expectancy | B2 15m B stop 2.0xATR tgt next_level | 260 | -0.099 | 0.85 | 0.087 | 1/6 | 3/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-141 | Baseline 2 (plain range flip) has positive net expectancy | B2 24m A stop 1.5xATR tgt 1R | 412 | -0.132 | 0.77 | 0.083 | 1/6 | 2/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-142 | Baseline 2 (plain range flip) has positive net expectancy | B2 24m A stop 1.5xATR tgt 1.5R | 411 | -0.182 | 0.74 | 0.083 | 0/6 | 3/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-143 | Baseline 2 (plain range flip) has positive net expectancy | B2 24m A stop 1.5xATR tgt 2R | 411 | -0.118 | 0.84 | 0.083 | 1/6 | 3/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-144 | Baseline 2 (plain range flip) has positive net expectancy | B2 24m A stop 1.5xATR tgt 3R | 411 | -0.121 | 0.85 | 0.083 | 1/6 | 2/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-145 | Baseline 2 (plain range flip) has positive net expectancy | B2 24m A stop 1.5xATR tgt fib1.272 | 411 | -0.209 | 0.75 | 0.083 | 1/6 | 1/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-146 | Baseline 2 (plain range flip) has positive net expectancy | B2 24m A stop 1.5xATR tgt fib1.618 | 410 | -0.176 | 0.79 | 0.083 | 1/6 | 3/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-147 | Baseline 2 (plain range flip) has positive net expectancy | B2 24m A stop 1.5xATR tgt next_level | 243 | -0.098 | 0.86 | 0.084 | 1/6 | 4/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-148 | Baseline 2 (plain range flip) has positive net expectancy | B2 24m A stop 2.0xATR tgt 1R | 414 | -0.108 | 0.81 | 0.063 | 1/6 | 3/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-149 | Baseline 2 (plain range flip) has positive net expectancy | B2 24m A stop 2.0xATR tgt 1.5R | 413 | -0.084 | 0.87 | 0.063 | 3/6 | 4/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-150 | Baseline 2 (plain range flip) has positive net expectancy | B2 24m A stop 2.0xATR tgt 2R | 413 | -0.088 | 0.87 | 0.063 | 1/6 | 4/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-151 | Baseline 2 (plain range flip) has positive net expectancy | B2 24m A stop 2.0xATR tgt 3R | 412 | -0.129 | 0.82 | 0.063 | 2/6 | 2/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-152 | Baseline 2 (plain range flip) has positive net expectancy | B2 24m A stop 2.0xATR tgt fib1.272 | 411 | -0.178 | 0.75 | 0.063 | 1/6 | 1/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-153 | Baseline 2 (plain range flip) has positive net expectancy | B2 24m A stop 2.0xATR tgt fib1.618 | 412 | -0.159 | 0.79 | 0.063 | 2/6 | 2/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-154 | Baseline 2 (plain range flip) has positive net expectancy | B2 24m A stop 2.0xATR tgt next_level | 201 | -0.037 | 0.94 | 0.064 | 2/6 | 2/9 | 0.01 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-155 | Baseline 2 (plain range flip) has positive net expectancy | B2 24m B stop 1.5xATR tgt 1R | 584 | -0.103 | 0.82 | 0.085 | 1/6 | 2/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-156 | Baseline 2 (plain range flip) has positive net expectancy | B2 24m B stop 1.5xATR tgt 1.5R | 583 | -0.140 | 0.80 | 0.085 | 1/6 | 3/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-157 | Baseline 2 (plain range flip) has positive net expectancy | B2 24m B stop 1.5xATR tgt 2R | 582 | -0.100 | 0.86 | 0.085 | 2/6 | 4/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-158 | Baseline 2 (plain range flip) has positive net expectancy | B2 24m B stop 1.5xATR tgt 3R | 581 | -0.099 | 0.88 | 0.085 | 1/6 | 3/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-159 | Baseline 2 (plain range flip) has positive net expectancy | B2 24m B stop 1.5xATR tgt fib1.272 | 580 | -0.178 | 0.79 | 0.085 | 1/6 | 3/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-160 | Baseline 2 (plain range flip) has positive net expectancy | B2 24m B stop 1.5xATR tgt fib1.618 | 579 | -0.187 | 0.78 | 0.085 | 1/6 | 2/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-161 | Baseline 2 (plain range flip) has positive net expectancy | B2 24m B stop 1.5xATR tgt next_level | 219 | -0.041 | 0.94 | 0.085 | 3/6 | 2/9 | 0.01 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-162 | Baseline 2 (plain range flip) has positive net expectancy | B2 24m B stop 2.0xATR tgt 1R | 585 | -0.102 | 0.82 | 0.064 | 1/6 | 2/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-163 | Baseline 2 (plain range flip) has positive net expectancy | B2 24m B stop 2.0xATR tgt 1.5R | 581 | -0.108 | 0.83 | 0.064 | 2/6 | 3/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-164 | Baseline 2 (plain range flip) has positive net expectancy | B2 24m B stop 2.0xATR tgt 2R | 580 | -0.135 | 0.81 | 0.064 | 1/6 | 2/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-165 | Baseline 2 (plain range flip) has positive net expectancy | B2 24m B stop 2.0xATR tgt 3R | 580 | -0.130 | 0.83 | 0.064 | 2/6 | 1/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-166 | Baseline 2 (plain range flip) has positive net expectancy | B2 24m B stop 2.0xATR tgt fib1.272 | 580 | -0.167 | 0.77 | 0.064 | 1/6 | 3/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-167 | Baseline 2 (plain range flip) has positive net expectancy | B2 24m B stop 2.0xATR tgt fib1.618 | 579 | -0.178 | 0.77 | 0.064 | 1/6 | 1/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-168 | Baseline 2 (plain range flip) has positive net expectancy | B2 24m B stop 2.0xATR tgt next_level | 173 | -0.055 | 0.91 | 0.062 | 1/6 | 2/9 | 0.01 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-169 | Baseline 2 (plain range flip) has positive net expectancy | B2 1h A stop 1.5xATR tgt 1R | 155 | -0.072 | 0.86 | 0.050 | 3/6 | 5/9 | 0.01 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-170 | Baseline 2 (plain range flip) has positive net expectancy | B2 1h A stop 1.5xATR tgt 1.5R | 155 | -0.103 | 0.83 | 0.050 | 2/6 | 3/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-171 | Baseline 2 (plain range flip) has positive net expectancy | B2 1h A stop 1.5xATR tgt 2R | 155 | -0.116 | 0.82 | 0.050 | 1/6 | 3/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-172 | Baseline 2 (plain range flip) has positive net expectancy | B2 1h A stop 1.5xATR tgt 3R | 155 | -0.142 | 0.80 | 0.050 | 1/6 | 2/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-173 | Baseline 2 (plain range flip) has positive net expectancy | B2 1h A stop 1.5xATR tgt fib1.272 | 155 | -0.139 | 0.80 | 0.050 | 2/6 | 3/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-174 | Baseline 2 (plain range flip) has positive net expectancy | B2 1h A stop 1.5xATR tgt fib1.618 | 155 | -0.102 | 0.85 | 0.050 | 2/6 | 3/9 | 0.01 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-175 | Baseline 2 (plain range flip) has positive net expectancy | B2 1h A stop 1.5xATR tgt next_level | 101 | -0.089 | 0.86 | 0.052 | 1/6 | 2/9 | 0.02 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-176 | Baseline 2 (plain range flip) has positive net expectancy | B2 1h A stop 2.0xATR tgt 1R | 157 | -0.130 | 0.75 | 0.038 | 1/6 | 2/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-177 | Baseline 2 (plain range flip) has positive net expectancy | B2 1h A stop 2.0xATR tgt 1.5R | 157 | -0.128 | 0.77 | 0.038 | 1/6 | 2/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-178 | Baseline 2 (plain range flip) has positive net expectancy | B2 1h A stop 2.0xATR tgt 2R | 157 | -0.124 | 0.79 | 0.038 | 1/6 | 1/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-179 | Baseline 2 (plain range flip) has positive net expectancy | B2 1h A stop 2.0xATR tgt 3R | 157 | -0.165 | 0.73 | 0.038 | 1/6 | 1/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-180 | Baseline 2 (plain range flip) has positive net expectancy | B2 1h A stop 2.0xATR tgt fib1.272 | 157 | -0.126 | 0.78 | 0.038 | 1/6 | 2/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-181 | Baseline 2 (plain range flip) has positive net expectancy | B2 1h A stop 2.0xATR tgt fib1.618 | 157 | -0.137 | 0.77 | 0.038 | 1/6 | 2/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-182 | Baseline 2 (plain range flip) has positive net expectancy | B2 1h A stop 2.0xATR tgt next_level | 76 | -0.088 | 0.84 | 0.040 | 2/6 | 4/9 | 0.04 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-183 | Baseline 2 (plain range flip) has positive net expectancy | B2 1h B stop 1.5xATR tgt 1R | 225 | -0.033 | 0.93 | 0.050 | 3/6 | 5/9 | 0.01 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-184 | Baseline 2 (plain range flip) has positive net expectancy | B2 1h B stop 1.5xATR tgt 1.5R | 225 | -0.073 | 0.88 | 0.050 | 3/6 | 3/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-185 | Baseline 2 (plain range flip) has positive net expectancy | B2 1h B stop 1.5xATR tgt 2R | 225 | -0.109 | 0.83 | 0.050 | 2/6 | 3/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-186 | Baseline 2 (plain range flip) has positive net expectancy | B2 1h B stop 1.5xATR tgt 3R | 225 | -0.133 | 0.80 | 0.050 | 2/6 | 3/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-187 | Baseline 2 (plain range flip) has positive net expectancy | B2 1h B stop 1.5xATR tgt fib1.272 | 225 | -0.112 | 0.83 | 0.050 | 2/6 | 3/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-188 | Baseline 2 (plain range flip) has positive net expectancy | B2 1h B stop 1.5xATR tgt fib1.618 | 225 | -0.092 | 0.86 | 0.050 | 2/6 | 4/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-189 | Baseline 2 (plain range flip) has positive net expectancy | B2 1h B stop 1.5xATR tgt next_level | 94 | +0.052 | 1.09 | 0.052 | 3/6 | 4/9 | 0.18 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-190 | Baseline 2 (plain range flip) has positive net expectancy | B2 1h B stop 2.0xATR tgt 1R | 225 | -0.049 | 0.90 | 0.037 | 3/6 | 4/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-191 | Baseline 2 (plain range flip) has positive net expectancy | B2 1h B stop 2.0xATR tgt 1.5R | 225 | -0.094 | 0.83 | 0.037 | 2/6 | 3/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-192 | Baseline 2 (plain range flip) has positive net expectancy | B2 1h B stop 2.0xATR tgt 2R | 225 | -0.115 | 0.79 | 0.037 | 2/6 | 4/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-193 | Baseline 2 (plain range flip) has positive net expectancy | B2 1h B stop 2.0xATR tgt 3R | 225 | -0.101 | 0.82 | 0.037 | 2/6 | 4/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-194 | Baseline 2 (plain range flip) has positive net expectancy | B2 1h B stop 2.0xATR tgt fib1.272 | 225 | -0.095 | 0.83 | 0.037 | 2/6 | 3/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-195 | Baseline 2 (plain range flip) has positive net expectancy | B2 1h B stop 2.0xATR tgt fib1.618 | 225 | -0.067 | 0.88 | 0.037 | 2/6 | 3/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-196 | Baseline 2 (plain range flip) has positive net expectancy | B2 1h B stop 2.0xATR tgt next_level | 72 | +0.046 | 1.09 | 0.040 | 1/6 | 4/9 | 0.21 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-197 | HTF layer filter improves Baseline 1 | B3 6m A +HTF near_cross stop 2.0xATR tgt 2R | 1825 | -0.222 | 0.73 | 0.131 | 0/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-198 | HTF layer filter improves Baseline 1 | B3 6m A +HTF mf_dir stop 2.0xATR tgt 2R | 3852 | -0.258 | 0.69 | 0.142 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-199 | HTF layer filter improves Baseline 1 | B3 6m B +HTF near_cross stop 2.0xATR tgt 2R | 1611 | -0.201 | 0.75 | 0.130 | 0/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-200 | HTF layer filter improves Baseline 1 | B3 6m B +HTF mf_dir stop 2.0xATR tgt 2R | 3658 | -0.243 | 0.71 | 0.141 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-201 | HTF layer filter improves Baseline 1 | B3 15m A +HTF near_cross stop 1.5xATR tgt 2R | 761 | -0.088 | 0.88 | 0.098 | 1/6 | 2/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-202 | HTF layer filter improves Baseline 1 | B3 15m A +HTF mf_dir stop 1.5xATR tgt 2R | 1765 | -0.148 | 0.81 | 0.107 | 0/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-203 | HTF layer filter improves Baseline 1 | B3 15m B +HTF near_cross stop 1.5xATR tgt 2R | 703 | -0.073 | 0.90 | 0.095 | 2/6 | 2/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-204 | HTF layer filter improves Baseline 1 | B3 15m B +HTF mf_dir stop 1.5xATR tgt 2R | 1645 | -0.175 | 0.78 | 0.108 | 1/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-205 | HTF layer filter improves Baseline 1 | B3 24m A +HTF near_cross stop 1.5xATR tgt 2R | 502 | -0.112 | 0.85 | 0.078 | 2/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-206 | HTF layer filter improves Baseline 1 | B3 24m A +HTF mf_dir stop 1.5xATR tgt 2R | 1116 | -0.143 | 0.81 | 0.084 | 1/6 | 1/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-207 | HTF layer filter improves Baseline 1 | B3 24m B +HTF near_cross stop 1.5xATR tgt 2R | 429 | -0.077 | 0.89 | 0.077 | 2/6 | 2/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-208 | HTF layer filter improves Baseline 1 | B3 24m B +HTF mf_dir stop 1.5xATR tgt 2R | 1008 | -0.104 | 0.86 | 0.084 | 2/6 | 2/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-209 | HTF layer filter improves Baseline 1 | B3 1h A +HTF near_cross stop 1.5xATR tgt 2R | 195 | -0.022 | 0.97 | 0.047 | 3/6 | 5/9 | 0.02 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-210 | HTF layer filter improves Baseline 1 | B3 1h A +HTF mf_dir stop 1.5xATR tgt 2R | 438 | -0.021 | 0.96 | 0.048 | 2/6 | 4/9 | 0.00 | fails S1,S2,S4,S5,S7,S8 |
| P2-211 | HTF layer filter improves Baseline 1 | B3 1h B +HTF near_cross stop 1.5xATR tgt 2R | 182 | -0.053 | 0.92 | 0.048 | 2/6 | 2/9 | 0.01 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-212 | HTF layer filter improves Baseline 1 | B3 1h B +HTF mf_dir stop 1.5xATR tgt 2R | 417 | -0.084 | 0.87 | 0.048 | 3/6 | 3/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
