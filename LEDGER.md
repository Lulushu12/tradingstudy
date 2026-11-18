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

## Phase 2 re-run with Amendment 1 definitions (counts: yes, 166 configurations)
- Date: 2026-11-16. Split: walk-forward test period 2023-01-01..2025-11-14, fixed rules, 9 coins, structure stops. DSR with N = 378.

| id | hypothesis | configuration | n | exp R | gross R | PF | fee R | folds+ | coins+ | DSR | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P2-213 | Divergence stack v2 (anchor filter, frozen-spec MF and front-run, structure stops) has positive net expectancy | B1v2 15m A target 1R | 8136 | -0.180 | -0.067 | 0.70 | 0.113 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-214 | Divergence stack v2 (anchor filter, frozen-spec MF and front-run, structure stops) has positive net expectancy | B1v2 15m A target 1.5R | 7141 | -0.180 | -0.067 | 0.75 | 0.112 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-215 | Divergence stack v2 (anchor filter, frozen-spec MF and front-run, structure stops) has positive net expectancy | B1v2 15m A target 2R | 6485 | -0.201 | -0.088 | 0.74 | 0.113 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-216 | Divergence stack v2 (anchor filter, frozen-spec MF and front-run, structure stops) has positive net expectancy | B1v2 15m A target 3R | 5780 | -0.193 | -0.081 | 0.77 | 0.112 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-217 | Divergence stack v2 (anchor filter, frozen-spec MF and front-run, structure stops) has positive net expectancy | B1v2 15m A target fib1.272 | 5600 | -0.226 | -0.109 | 0.75 | 0.117 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-218 | Divergence stack v2 (anchor filter, frozen-spec MF and front-run, structure stops) has positive net expectancy | B1v2 15m A target fib1.618 | 5348 | -0.207 | -0.092 | 0.77 | 0.115 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-219 | Divergence stack v2 (anchor filter, frozen-spec MF and front-run, structure stops) has positive net expectancy | B1v2 15m A target next_level | 4246 | -0.278 | -0.141 | 0.66 | 0.137 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-220 | Divergence stack v2 (anchor filter, frozen-spec MF and front-run, structure stops) has positive net expectancy | B1v2 15m B target 1R | 10370 | -0.199 | -0.077 | 0.68 | 0.123 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-221 | Divergence stack v2 (anchor filter, frozen-spec MF and front-run, structure stops) has positive net expectancy | B1v2 15m B target 1.5R | 8975 | -0.207 | -0.084 | 0.72 | 0.122 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-222 | Divergence stack v2 (anchor filter, frozen-spec MF and front-run, structure stops) has positive net expectancy | B1v2 15m B target 2R | 7994 | -0.233 | -0.111 | 0.71 | 0.122 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-223 | Divergence stack v2 (anchor filter, frozen-spec MF and front-run, structure stops) has positive net expectancy | B1v2 15m B target 3R | 7039 | -0.237 | -0.115 | 0.73 | 0.122 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-224 | Divergence stack v2 (anchor filter, frozen-spec MF and front-run, structure stops) has positive net expectancy | B1v2 15m B target fib1.272 | 6611 | -0.225 | -0.099 | 0.76 | 0.127 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-225 | Divergence stack v2 (anchor filter, frozen-spec MF and front-run, structure stops) has positive net expectancy | B1v2 15m B target fib1.618 | 6281 | -0.237 | -0.113 | 0.75 | 0.124 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-226 | Divergence stack v2 (anchor filter, frozen-spec MF and front-run, structure stops) has positive net expectancy | B1v2 15m B target next_level | 5790 | -0.240 | -0.096 | 0.71 | 0.143 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-227 | Divergence stack v2 (anchor filter, frozen-spec MF and front-run, structure stops) has positive net expectancy | B1v2 24m A target 1R | 5614 | -0.128 | -0.042 | 0.77 | 0.085 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-228 | Divergence stack v2 (anchor filter, frozen-spec MF and front-run, structure stops) has positive net expectancy | B1v2 24m A target 1.5R | 5039 | -0.137 | -0.052 | 0.79 | 0.085 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-229 | Divergence stack v2 (anchor filter, frozen-spec MF and front-run, structure stops) has positive net expectancy | B1v2 24m A target 2R | 4682 | -0.128 | -0.042 | 0.82 | 0.085 | 0/6 | 1/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-230 | Divergence stack v2 (anchor filter, frozen-spec MF and front-run, structure stops) has positive net expectancy | B1v2 24m A target 3R | 4329 | -0.139 | -0.052 | 0.82 | 0.086 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-231 | Divergence stack v2 (anchor filter, frozen-spec MF and front-run, structure stops) has positive net expectancy | B1v2 24m A target fib1.272 | 4177 | -0.188 | -0.096 | 0.77 | 0.091 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-232 | Divergence stack v2 (anchor filter, frozen-spec MF and front-run, structure stops) has positive net expectancy | B1v2 24m A target fib1.618 | 4125 | -0.180 | -0.091 | 0.78 | 0.089 | 0/6 | 1/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-233 | Divergence stack v2 (anchor filter, frozen-spec MF and front-run, structure stops) has positive net expectancy | B1v2 24m A target next_level | 2846 | -0.197 | -0.094 | 0.74 | 0.103 | 0/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-234 | Divergence stack v2 (anchor filter, frozen-spec MF and front-run, structure stops) has positive net expectancy | B1v2 24m B target 1R | 7298 | -0.146 | -0.053 | 0.75 | 0.094 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-235 | Divergence stack v2 (anchor filter, frozen-spec MF and front-run, structure stops) has positive net expectancy | B1v2 24m B target 1.5R | 6368 | -0.150 | -0.056 | 0.78 | 0.094 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-236 | Divergence stack v2 (anchor filter, frozen-spec MF and front-run, structure stops) has positive net expectancy | B1v2 24m B target 2R | 5798 | -0.163 | -0.069 | 0.78 | 0.094 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-237 | Divergence stack v2 (anchor filter, frozen-spec MF and front-run, structure stops) has positive net expectancy | B1v2 24m B target 3R | 5186 | -0.164 | -0.070 | 0.79 | 0.095 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-238 | Divergence stack v2 (anchor filter, frozen-spec MF and front-run, structure stops) has positive net expectancy | B1v2 24m B target fib1.272 | 5037 | -0.176 | -0.079 | 0.79 | 0.098 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-239 | Divergence stack v2 (anchor filter, frozen-spec MF and front-run, structure stops) has positive net expectancy | B1v2 24m B target fib1.618 | 4889 | -0.169 | -0.073 | 0.80 | 0.096 | 1/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-240 | Divergence stack v2 (anchor filter, frozen-spec MF and front-run, structure stops) has positive net expectancy | B1v2 24m B target next_level | 4046 | -0.211 | -0.099 | 0.73 | 0.112 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-241 | Divergence stack v2 (anchor filter, frozen-spec MF and front-run, structure stops) has positive net expectancy | B1v2 1h A target 1R | 2679 | -0.107 | -0.055 | 0.79 | 0.052 | 1/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-242 | Divergence stack v2 (anchor filter, frozen-spec MF and front-run, structure stops) has positive net expectancy | B1v2 1h A target 1.5R | 2533 | -0.093 | -0.041 | 0.84 | 0.052 | 1/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-243 | Divergence stack v2 (anchor filter, frozen-spec MF and front-run, structure stops) has positive net expectancy | B1v2 1h A target 2R | 2455 | -0.097 | -0.044 | 0.84 | 0.053 | 0/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-244 | Divergence stack v2 (anchor filter, frozen-spec MF and front-run, structure stops) has positive net expectancy | B1v2 1h A target 3R | 2386 | -0.100 | -0.048 | 0.84 | 0.053 | 1/6 | 1/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-245 | Divergence stack v2 (anchor filter, frozen-spec MF and front-run, structure stops) has positive net expectancy | B1v2 1h A target fib1.272 | 2257 | -0.108 | -0.054 | 0.83 | 0.054 | 1/6 | 1/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-246 | Divergence stack v2 (anchor filter, frozen-spec MF and front-run, structure stops) has positive net expectancy | B1v2 1h A target fib1.618 | 2283 | -0.111 | -0.058 | 0.83 | 0.054 | 1/6 | 1/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-247 | Divergence stack v2 (anchor filter, frozen-spec MF and front-run, structure stops) has positive net expectancy | B1v2 1h A target next_level | 1482 | -0.120 | -0.059 | 0.82 | 0.061 | 1/6 | 2/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-248 | Divergence stack v2 (anchor filter, frozen-spec MF and front-run, structure stops) has positive net expectancy | B1v2 1h B target 1R | 3665 | -0.098 | -0.041 | 0.81 | 0.057 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-249 | Divergence stack v2 (anchor filter, frozen-spec MF and front-run, structure stops) has positive net expectancy | B1v2 1h B target 1.5R | 3366 | -0.114 | -0.057 | 0.81 | 0.057 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-250 | Divergence stack v2 (anchor filter, frozen-spec MF and front-run, structure stops) has positive net expectancy | B1v2 1h B target 2R | 3230 | -0.134 | -0.076 | 0.79 | 0.057 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-251 | Divergence stack v2 (anchor filter, frozen-spec MF and front-run, structure stops) has positive net expectancy | B1v2 1h B target 3R | 3095 | -0.143 | -0.085 | 0.79 | 0.058 | 0/6 | 1/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-252 | Divergence stack v2 (anchor filter, frozen-spec MF and front-run, structure stops) has positive net expectancy | B1v2 1h B target fib1.272 | 2961 | -0.141 | -0.081 | 0.80 | 0.060 | 0/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-253 | Divergence stack v2 (anchor filter, frozen-spec MF and front-run, structure stops) has positive net expectancy | B1v2 1h B target fib1.618 | 2974 | -0.137 | -0.078 | 0.80 | 0.059 | 1/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-254 | Divergence stack v2 (anchor filter, frozen-spec MF and front-run, structure stops) has positive net expectancy | B1v2 1h B target next_level | 2190 | -0.160 | -0.095 | 0.77 | 0.065 | 0/6 | 2/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-255 | Same-TF range flip v2 (respect rule, structure stops) has positive net expectancy | B2v2 15m A target 1R | 507 | -0.217 | -0.055 | 0.66 | 0.162 | 0/6 | 1/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-256 | Same-TF range flip v2 (respect rule, structure stops) has positive net expectancy | B2v2 15m A target 1.5R | 507 | -0.175 | -0.013 | 0.76 | 0.162 | 0/6 | 2/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-257 | Same-TF range flip v2 (respect rule, structure stops) has positive net expectancy | B2v2 15m A target 2R | 506 | -0.190 | -0.027 | 0.77 | 0.162 | 0/6 | 1/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-258 | Same-TF range flip v2 (respect rule, structure stops) has positive net expectancy | B2v2 15m A target 3R | 504 | -0.108 | +0.055 | 0.88 | 0.162 | 1/6 | 3/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-259 | Same-TF range flip v2 (respect rule, structure stops) has positive net expectancy | B2v2 15m A target fib1.272 | 499 | -0.205 | -0.041 | 0.79 | 0.163 | 0/6 | 1/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-260 | Same-TF range flip v2 (respect rule, structure stops) has positive net expectancy | B2v2 15m A target fib1.618 | 503 | -0.293 | -0.130 | 0.72 | 0.163 | 0/6 | 1/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-261 | Same-TF range flip v2 (respect rule, structure stops) has positive net expectancy | B2v2 15m A target next_level | 301 | -0.210 | -0.031 | 0.76 | 0.179 | 1/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-262 | Same-TF range flip v2 (respect rule, structure stops) has positive net expectancy | B2v2 15m B target 1R | 472 | -0.228 | -0.050 | 0.64 | 0.177 | 0/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-263 | Same-TF range flip v2 (respect rule, structure stops) has positive net expectancy | B2v2 15m B target 1.5R | 472 | -0.212 | -0.034 | 0.72 | 0.177 | 0/6 | 1/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-264 | Same-TF range flip v2 (respect rule, structure stops) has positive net expectancy | B2v2 15m B target 2R | 472 | -0.246 | -0.068 | 0.71 | 0.177 | 0/6 | 2/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-265 | Same-TF range flip v2 (respect rule, structure stops) has positive net expectancy | B2v2 15m B target 3R | 470 | -0.203 | -0.025 | 0.78 | 0.177 | 1/6 | 1/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-266 | Same-TF range flip v2 (respect rule, structure stops) has positive net expectancy | B2v2 15m B target fib1.272 | 468 | -0.086 | +0.092 | 0.92 | 0.178 | 2/6 | 4/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-267 | Same-TF range flip v2 (respect rule, structure stops) has positive net expectancy | B2v2 15m B target fib1.618 | 468 | -0.147 | +0.030 | 0.86 | 0.177 | 2/6 | 4/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-268 | Same-TF range flip v2 (respect rule, structure stops) has positive net expectancy | B2v2 15m B target next_level | 271 | -0.263 | -0.066 | 0.72 | 0.197 | 1/6 | 1/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-269 | Same-TF range flip v2 (respect rule, structure stops) has positive net expectancy | B2v2 24m A target 1R | 345 | -0.202 | -0.086 | 0.68 | 0.116 | 0/6 | 1/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-270 | Same-TF range flip v2 (respect rule, structure stops) has positive net expectancy | B2v2 24m A target 1.5R | 345 | -0.219 | -0.103 | 0.70 | 0.116 | 0/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-271 | Same-TF range flip v2 (respect rule, structure stops) has positive net expectancy | B2v2 24m A target 2R | 345 | -0.246 | -0.130 | 0.70 | 0.116 | 1/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-272 | Same-TF range flip v2 (respect rule, structure stops) has positive net expectancy | B2v2 24m A target 3R | 345 | -0.197 | -0.081 | 0.77 | 0.116 | 1/6 | 2/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-273 | Same-TF range flip v2 (respect rule, structure stops) has positive net expectancy | B2v2 24m A target fib1.272 | 340 | -0.300 | -0.182 | 0.68 | 0.117 | 1/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-274 | Same-TF range flip v2 (respect rule, structure stops) has positive net expectancy | B2v2 24m A target fib1.618 | 342 | -0.286 | -0.170 | 0.70 | 0.116 | 1/6 | 2/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-275 | Same-TF range flip v2 (respect rule, structure stops) has positive net expectancy | B2v2 24m A target next_level | 207 | -0.219 | -0.093 | 0.73 | 0.126 | 2/6 | 2/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-276 | Same-TF range flip v2 (respect rule, structure stops) has positive net expectancy | B2v2 24m B target 1R | 357 | -0.244 | -0.108 | 0.62 | 0.136 | 0/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-277 | Same-TF range flip v2 (respect rule, structure stops) has positive net expectancy | B2v2 24m B target 1.5R | 357 | -0.279 | -0.143 | 0.64 | 0.136 | 0/6 | 1/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-278 | Same-TF range flip v2 (respect rule, structure stops) has positive net expectancy | B2v2 24m B target 2R | 357 | -0.281 | -0.145 | 0.67 | 0.136 | 0/6 | 1/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-279 | Same-TF range flip v2 (respect rule, structure stops) has positive net expectancy | B2v2 24m B target 3R | 357 | -0.226 | -0.090 | 0.75 | 0.136 | 1/6 | 1/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-280 | Same-TF range flip v2 (respect rule, structure stops) has positive net expectancy | B2v2 24m B target fib1.272 | 354 | -0.351 | -0.214 | 0.65 | 0.137 | 1/6 | 1/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-281 | Same-TF range flip v2 (respect rule, structure stops) has positive net expectancy | B2v2 24m B target fib1.618 | 356 | -0.383 | -0.246 | 0.63 | 0.137 | 1/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-282 | Same-TF range flip v2 (respect rule, structure stops) has positive net expectancy | B2v2 24m B target next_level | 232 | -0.223 | -0.084 | 0.74 | 0.139 | 1/6 | 2/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-283 | Same-TF range flip v2 (respect rule, structure stops) has positive net expectancy | B2v2 1h A target 1R | 127 | -0.149 | -0.078 | 0.74 | 0.071 | 2/6 | 2/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-284 | Same-TF range flip v2 (respect rule, structure stops) has positive net expectancy | B2v2 1h A target 1.5R | 127 | -0.166 | -0.094 | 0.75 | 0.071 | 2/6 | 3/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-285 | Same-TF range flip v2 (respect rule, structure stops) has positive net expectancy | B2v2 1h A target 2R | 127 | -0.167 | -0.096 | 0.77 | 0.071 | 2/6 | 4/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-286 | Same-TF range flip v2 (respect rule, structure stops) has positive net expectancy | B2v2 1h A target 3R | 127 | -0.067 | +0.005 | 0.91 | 0.071 | 3/6 | 4/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-287 | Same-TF range flip v2 (respect rule, structure stops) has positive net expectancy | B2v2 1h A target fib1.272 | 127 | -0.102 | -0.030 | 0.87 | 0.071 | 2/6 | 4/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-288 | Same-TF range flip v2 (respect rule, structure stops) has positive net expectancy | B2v2 1h A target fib1.618 | 127 | -0.064 | +0.008 | 0.92 | 0.071 | 3/6 | 4/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-289 | Same-TF range flip v2 (respect rule, structure stops) has positive net expectancy | B2v2 1h A target next_level | 98 | -0.012 | +0.063 | 0.98 | 0.075 | 3/6 | 3/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-290 | Same-TF range flip v2 (respect rule, structure stops) has positive net expectancy | B2v2 1h B target 1R | 133 | -0.181 | -0.102 | 0.69 | 0.079 | 1/6 | 1/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-291 | Same-TF range flip v2 (respect rule, structure stops) has positive net expectancy | B2v2 1h B target 1.5R | 133 | -0.159 | -0.080 | 0.76 | 0.079 | 2/6 | 3/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-292 | Same-TF range flip v2 (respect rule, structure stops) has positive net expectancy | B2v2 1h B target 2R | 133 | -0.233 | -0.154 | 0.69 | 0.079 | 2/6 | 3/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-293 | Same-TF range flip v2 (respect rule, structure stops) has positive net expectancy | B2v2 1h B target 3R | 133 | -0.147 | -0.068 | 0.81 | 0.079 | 2/6 | 3/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-294 | Same-TF range flip v2 (respect rule, structure stops) has positive net expectancy | B2v2 1h B target fib1.272 | 133 | -0.152 | -0.073 | 0.82 | 0.079 | 2/6 | 3/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-295 | Same-TF range flip v2 (respect rule, structure stops) has positive net expectancy | B2v2 1h B target fib1.618 | 133 | -0.099 | -0.020 | 0.88 | 0.079 | 2/6 | 3/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-296 | Same-TF range flip v2 (respect rule, structure stops) has positive net expectancy | B2v2 1h B target next_level | 93 | -0.056 | +0.031 | 0.93 | 0.088 | 2/6 | 4/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-297 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 1h>15m A target 1R | 156 | -0.141 | -0.013 | 0.76 | 0.128 | 1/6 | 3/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-298 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 1h>15m A target 1.5R | 156 | -0.282 | -0.154 | 0.63 | 0.128 | 0/6 | 2/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-299 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 1h>15m A target 2R | 156 | -0.350 | -0.223 | 0.58 | 0.128 | 1/6 | 2/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-300 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 1h>15m A target 3R | 156 | -0.340 | -0.212 | 0.63 | 0.128 | 2/6 | 3/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-301 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 1h>15m A target fib1.272 | 155 | -0.223 | -0.095 | 0.77 | 0.128 | 3/6 | 4/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-302 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 1h>15m A target fib1.618 | 156 | -0.175 | -0.048 | 0.82 | 0.128 | 3/6 | 4/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-303 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 1h>15m A target next_level | 76 | -0.332 | -0.191 | 0.63 | 0.142 | 0/6 | 2/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-304 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 1h>15m B target 1R | 152 | -0.254 | -0.118 | 0.60 | 0.136 | 1/6 | 2/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-305 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 1h>15m B target 1.5R | 152 | -0.359 | -0.223 | 0.55 | 0.136 | 1/6 | 1/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-306 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 1h>15m B target 2R | 152 | -0.373 | -0.236 | 0.56 | 0.136 | 2/6 | 2/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-307 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 1h>15m B target 3R | 152 | -0.320 | -0.184 | 0.65 | 0.136 | 2/6 | 2/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-308 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 1h>15m B target fib1.272 | 149 | -0.172 | -0.033 | 0.82 | 0.139 | 2/6 | 3/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-309 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 1h>15m B target fib1.618 | 151 | -0.132 | +0.005 | 0.86 | 0.137 | 2/6 | 3/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-310 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 1h>15m B target next_level | 69 | -0.190 | -0.034 | 0.79 | 0.156 | 2/6 | 4/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-311 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 4h>15m A target 1R | 47 | -0.086 | +0.026 | 0.84 | 0.112 | 2/6 | 4/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-312 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 4h>15m A target 1.5R | 47 | +0.030 | +0.142 | 1.05 | 0.112 | 4/6 | 5/9 | 0.00 | fails S1,S2,S3,S5,S7,S9 |
| P2-313 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 4h>15m A target 2R | 47 | -0.232 | -0.120 | 0.70 | 0.112 | 2/6 | 4/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-314 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 4h>15m A target 3R | 47 | -0.236 | -0.124 | 0.72 | 0.112 | 2/6 | 4/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-315 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 4h>15m A target fib1.272 | 45 | -0.131 | -0.016 | 0.85 | 0.115 | 2/6 | 3/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-316 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 4h>15m A target fib1.618 | 46 | -0.258 | -0.144 | 0.71 | 0.114 | 1/6 | 3/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-317 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 4h>15m A target next_level | 19 | +0.014 | +0.146 | 1.02 | 0.132 | 2/6 | 2/9 | 0.03 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-318 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 4h>15m B target 1R | 36 | +0.013 | +0.114 | 1.03 | 0.101 | 2/6 | 3/9 | 0.01 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-319 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 4h>15m B target 1.5R | 36 | -0.229 | -0.128 | 0.68 | 0.101 | 2/6 | 3/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-320 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 4h>15m B target 2R | 36 | -0.341 | -0.240 | 0.59 | 0.101 | 1/6 | 3/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-321 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 4h>15m B target 3R | 36 | -0.296 | -0.195 | 0.65 | 0.101 | 1/6 | 3/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-322 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 4h>15m B target fib1.272 | 35 | -0.435 | -0.332 | 0.51 | 0.103 | 1/6 | 1/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-323 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 4h>15m B target fib1.618 | 35 | -0.471 | -0.368 | 0.47 | 0.103 | 1/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-324 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 4h>15m B target next_level | 15 | -0.621 | -0.471 | 0.33 | 0.150 | 1/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-325 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 1h>24m A target 1R | 141 | -0.112 | -0.001 | 0.80 | 0.111 | 2/6 | 2/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-326 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 1h>24m A target 1.5R | 141 | -0.107 | +0.004 | 0.84 | 0.111 | 1/6 | 4/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-327 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 1h>24m A target 2R | 141 | -0.128 | -0.017 | 0.83 | 0.111 | 2/6 | 5/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-328 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 1h>24m A target 3R | 141 | -0.111 | -0.000 | 0.87 | 0.111 | 2/6 | 5/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-329 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 1h>24m A target fib1.272 | 140 | -0.134 | -0.023 | 0.85 | 0.111 | 2/6 | 3/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-330 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 1h>24m A target fib1.618 | 141 | -0.054 | +0.057 | 0.94 | 0.111 | 3/6 | 3/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-331 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 1h>24m A target next_level | 87 | -0.165 | -0.042 | 0.80 | 0.124 | 1/6 | 4/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-332 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 1h>24m B target 1R | 134 | -0.082 | +0.031 | 0.85 | 0.113 | 2/6 | 4/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-333 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 1h>24m B target 1.5R | 134 | -0.128 | -0.014 | 0.81 | 0.113 | 2/6 | 3/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-334 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 1h>24m B target 2R | 134 | -0.214 | -0.101 | 0.72 | 0.113 | 1/6 | 2/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-335 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 1h>24m B target 3R | 134 | -0.246 | -0.132 | 0.71 | 0.113 | 1/6 | 3/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-336 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 1h>24m B target fib1.272 | 134 | -0.341 | -0.227 | 0.64 | 0.113 | 1/6 | 3/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-337 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 1h>24m B target fib1.618 | 134 | -0.320 | -0.207 | 0.66 | 0.113 | 1/6 | 3/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-338 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 1h>24m B target next_level | 72 | -0.429 | -0.297 | 0.52 | 0.132 | 1/6 | 1/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-339 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 4h>24m A target 1R | 45 | -0.269 | -0.172 | 0.57 | 0.097 | 1/6 | 2/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-340 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 4h>24m A target 1.5R | 45 | -0.255 | -0.158 | 0.64 | 0.097 | 2/6 | 3/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-341 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 4h>24m A target 2R | 45 | -0.179 | -0.082 | 0.76 | 0.097 | 4/6 | 4/9 | 0.00 | fails S1,S2,S3,S5,S7,S9 |
| P2-342 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 4h>24m A target 3R | 45 | -0.143 | -0.046 | 0.82 | 0.097 | 2/6 | 4/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-343 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 4h>24m A target fib1.272 | 45 | -0.207 | -0.110 | 0.75 | 0.097 | 2/6 | 4/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-344 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 4h>24m A target fib1.618 | 45 | -0.350 | -0.253 | 0.61 | 0.097 | 1/6 | 2/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-345 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 4h>24m A target next_level | 20 | -0.280 | -0.171 | 0.66 | 0.109 | 2/6 | 2/9 | 0.02 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-346 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 4h>24m B target 1R | 41 | -0.223 | -0.109 | 0.62 | 0.114 | 2/6 | 3/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-347 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 4h>24m B target 1.5R | 41 | -0.214 | -0.100 | 0.70 | 0.114 | 1/6 | 2/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-348 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 4h>24m B target 2R | 41 | -0.182 | -0.068 | 0.75 | 0.114 | 2/6 | 3/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-349 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 4h>24m B target 3R | 41 | -0.317 | -0.203 | 0.62 | 0.114 | 1/6 | 4/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-350 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 4h>24m B target fib1.272 | 41 | -0.316 | -0.202 | 0.63 | 0.114 | 1/6 | 2/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-351 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 4h>24m B target fib1.618 | 41 | -0.270 | -0.156 | 0.69 | 0.114 | 2/6 | 2/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-352 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 4h>24m B target next_level | 14 | -0.633 | -0.489 | 0.28 | 0.144 | 1/6 | 2/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-353 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 4h>1h A target 1R | 45 | -0.243 | -0.172 | 0.60 | 0.071 | 2/6 | 3/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-354 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 4h>1h A target 1.5R | 45 | -0.431 | -0.360 | 0.42 | 0.071 | 1/6 | 1/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-355 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 4h>1h A target 2R | 45 | -0.515 | -0.444 | 0.35 | 0.071 | 0/6 | 1/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-356 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 4h>1h A target 3R | 45 | -0.618 | -0.547 | 0.26 | 0.071 | 0/6 | 1/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-357 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 4h>1h A target fib1.272 | 41 | -0.787 | -0.713 | 0.11 | 0.075 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-358 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 4h>1h A target fib1.618 | 45 | -0.774 | -0.703 | 0.11 | 0.071 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-359 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 4h>1h A target next_level | 28 | -0.702 | -0.613 | 0.21 | 0.089 | 0/6 | 1/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-360 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 4h>1h B target 1R | 37 | -0.554 | -0.490 | 0.27 | 0.064 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-361 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 4h>1h B target 1.5R | 37 | -0.630 | -0.565 | 0.24 | 0.064 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-362 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 4h>1h B target 2R | 37 | -0.645 | -0.580 | 0.25 | 0.064 | 1/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-363 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 4h>1h B target 3R | 37 | -0.620 | -0.555 | 0.28 | 0.064 | 1/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-364 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 4h>1h B target fib1.272 | 36 | -0.760 | -0.695 | 0.11 | 0.065 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-365 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 4h>1h B target fib1.618 | 37 | -0.767 | -0.703 | 0.11 | 0.064 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-366 | Higher-TF range flip (range on 1h/4h, retest on exec TF) has positive net expectancy | B4 4h>1h B target next_level | 22 | -0.728 | -0.643 | 0.15 | 0.085 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S9 |
| P2-367 | HTF layer filter improves divergence stack v2 | B3v2 15m A +near_cross target 2R | 1101 | -0.200 | -0.094 | 0.74 | 0.105 | 0/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-368 | HTF layer filter improves divergence stack v2 | B3v2 15m A +mf_dir target 2R | 2693 | -0.205 | -0.093 | 0.74 | 0.112 | 0/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-369 | HTF layer filter improves divergence stack v2 | B3v2 15m B +near_cross target 2R | 1434 | -0.217 | -0.098 | 0.73 | 0.119 | 0/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-370 | HTF layer filter improves divergence stack v2 | B3v2 15m B +mf_dir target 2R | 3813 | -0.201 | -0.081 | 0.75 | 0.120 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P2-371 | HTF layer filter improves divergence stack v2 | B3v2 24m A +near_cross target 2R | 669 | -0.060 | +0.018 | 0.91 | 0.079 | 3/6 | 4/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-372 | HTF layer filter improves divergence stack v2 | B3v2 24m A +mf_dir target 2R | 1814 | -0.127 | -0.042 | 0.82 | 0.084 | 0/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-373 | HTF layer filter improves divergence stack v2 | B3v2 24m B +near_cross target 2R | 903 | -0.134 | -0.048 | 0.81 | 0.086 | 1/6 | 2/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-374 | HTF layer filter improves divergence stack v2 | B3v2 24m B +mf_dir target 2R | 2552 | -0.114 | -0.023 | 0.84 | 0.090 | 0/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-375 | HTF layer filter improves divergence stack v2 | B3v2 1h A +near_cross target 2R | 290 | +0.037 | +0.088 | 1.07 | 0.051 | 3/6 | 5/9 | 0.00 | fails S1,S2,S3,S4,S5,S7 |
| P2-376 | HTF layer filter improves divergence stack v2 | B3v2 1h A +mf_dir target 2R | 708 | -0.094 | -0.043 | 0.84 | 0.052 | 1/6 | 2/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-377 | HTF layer filter improves divergence stack v2 | B3v2 1h B +near_cross target 2R | 365 | -0.131 | -0.076 | 0.79 | 0.054 | 2/6 | 1/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P2-378 | HTF layer filter improves divergence stack v2 | B3v2 1h B +mf_dir target 2R | 1088 | -0.162 | -0.106 | 0.75 | 0.057 | 0/6 | 2/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |

## Phase 3 discovery procedures (counts: yes, 12 configurations)
- Date: 2026-11-16. Split: walk-forward, rule chosen on each fold's purged training data, OOS 2023-01-01..2025-11-14. DSR with N = 390.

| id | hypothesis | configuration | n | exp R | gross R | PF | folds+ | coins+ | DSR | stability | final rule | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P3-001 | A <=2-condition context filter makes the stack events profitable out of sample | stack 15m A structure stop 2R, walk-forward rule search | 444 | -0.301 | -0.153 | 0.65 | 1/6 | 1/9 | 0.00 | 1/6 | r2_rel == 1.0 AND fib_exec_in_0618_zone == 1.0 | fails S1,S2,S3,S4,S5,S7,S8,S9,S10 |
| P3-002 | A <=2-condition context filter makes the stack events profitable out of sample | stack 15m B structure stop 2R, walk-forward rule search | 251 | -0.278 | -0.166 | 0.65 | 0/6 | 2/9 | 0.00 | 1/6 | r2_rel == 1.0 AND fib_exec_in_0618_zone == 1.0 | fails S1,S2,S3,S4,S5,S7,S8,S9,S10 |
| P3-003 | A <=2-condition context filter makes the stack events profitable out of sample | stack 24m A structure stop 2R, walk-forward rule search | 264 | -0.148 | -0.047 | 0.79 | 2/6 | 2/9 | 0.00 | 3/6 | r1_rel == 1.0 AND htf_near_cross_rel == 1.0 | fails S1,S2,S3,S4,S5,S7,S8,S9,S10 |
| P3-004 | A <=2-condition context filter makes the stack events profitable out of sample | stack 24m B structure stop 2R, walk-forward rule search | 269 | -0.085 | +0.018 | 0.88 | 3/6 | 1/9 | 0.00 | 4/6 | r1_rel == 1.0 AND htf_near_cross_rel == 1.0 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P3-005 | A <=2-condition context filter makes the stack events profitable out of sample | stack 1h A structure stop 2R, walk-forward rule search | 192 | -0.113 | -0.062 | 0.81 | 2/6 | 3/9 | 0.00 | 1/6 | htf_near_cross_rel == 1.0 AND session == asia | fails S1,S2,S3,S4,S5,S7,S9,S10 |
| P3-006 | A <=2-condition context filter makes the stack events profitable out of sample | stack 1h B structure stop 2R, walk-forward rule search | 203 | -0.163 | -0.097 | 0.76 | 1/6 | 4/9 | 0.00 | 0/6 | cmf4h_rel <= -0.137 AND htf_near_cross_rel == 1.0 | fails S1,S2,S3,S4,S5,S7,S9,S10 |
| P3-007 | A <=2-condition context filter makes the flips events profitable out of sample | flips 15m A structure stop 2R, walk-forward rule search | 185 | -0.279 | -0.135 | 0.66 | 2/6 | 1/9 | 0.00 | 0/6 | atr_pctile_30d > 0.705 AND cmf_rel <= -0.0909 | fails S1,S2,S3,S4,S5,S7,S8,S9,S10 |
| P3-008 | A <=2-condition context filter makes the flips events profitable out of sample | flips 15m B structure stop 2R, walk-forward rule search | 210 | -0.360 | -0.203 | 0.59 | 1/6 | 0/9 | 0.00 | 0/6 | cmf4h_rel <= -0.0163 AND r2_rel == 0.0 | fails S1,S2,S3,S4,S5,S7,S8,S9,S10 |
| P3-009 | A <=2-condition context filter makes the flips events profitable out of sample | flips 24m A structure stop 2R, walk-forward rule search | 179 | -0.152 | -0.054 | 0.80 | 3/6 | 4/9 | 0.00 | 3/6 | funding_z_rel <= -0.117 AND confluence_types <= 1 | fails S1,S2,S3,S4,S5,S7,S9,S10 |
| P3-010 | A <=2-condition context filter makes the flips events profitable out of sample | flips 24m B structure stop 2R, walk-forward rule search | 214 | -0.245 | -0.110 | 0.70 | 1/6 | 2/9 | 0.00 | 2/6 | atr_pctile_30d > 0.746 AND cmf4h_rel <= 0.0889 | fails S1,S2,S3,S4,S5,S7,S8,S9,S10 |
| P3-011 | A <=2-condition context filter makes the flips events profitable out of sample | flips 1h A structure stop 2R, walk-forward rule search | 147 | -0.228 | -0.155 | 0.69 | 2/6 | 2/9 | 0.00 | 0/6 | confluence_types <= 1 AND sr_dist <= 1.14 | fails S1,S2,S3,S4,S5,S7,S9,S10 |
| P3-012 | A <=2-condition context filter makes the flips events profitable out of sample | flips 1h B structure stop 2R, walk-forward rule search | 149 | -0.264 | -0.188 | 0.65 | 2/6 | 2/9 | 0.00 | 0/6 | atr_pctile_30d > 0.486 AND cmf_rel <= 0.0269 | fails S1,S2,S3,S4,S5,S7,S9,S10 |

## Hypothesis H-MV, Macro View gate (counts: yes, 27 configurations)
- Date: 2026-11-16. Declared in PROTOCOL Amendment 2. Split: walk-forward test period 2023-01-01..2025-11-14, fixed rules, 9 coins, structure stop, 2R. DSR with N = 417.

| id | hypothesis | configuration | n | exp R | gross R | PF | folds+ | coins+ | DSR | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| P3-013 | MCB entries taken only with the 10x Macro View bias are profitable | 15m stackA bias lean (len 50, thr 60.0, x10) 2R | 3878 | -0.176 | -0.058 | 0.77 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P3-014 | MCB entries taken only with the 10x Macro View bias are profitable | 15m stackA bias any (len 50, thr 60.0, x10) 2R | 3010 | -0.157 | -0.041 | 0.80 | 0/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P3-015 | MCB entries taken only with the 10x Macro View bias are profitable | 15m stackA bias strong (len 50, thr 60.0, x10) 2R | 2309 | -0.204 | -0.089 | 0.74 | 0/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P3-016 | MCB entries taken only with the 10x Macro View bias are profitable | 15m stackB bias lean (len 50, thr 60.0, x10) 2R | 5095 | -0.218 | -0.091 | 0.73 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P3-017 | MCB entries taken only with the 10x Macro View bias are profitable | 15m stackB bias any (len 50, thr 60.0, x10) 2R | 3978 | -0.231 | -0.105 | 0.71 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P3-018 | MCB entries taken only with the 10x Macro View bias are profitable | 15m stackB bias strong (len 50, thr 60.0, x10) 2R | 3117 | -0.238 | -0.116 | 0.71 | 0/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P3-019 | MCB entries taken only with the 10x Macro View bias are profitable | 15m wtdiv bias lean (len 50, thr 60.0, x10) 2R | 6601 | -0.208 | -0.094 | 0.73 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P3-020 | MCB entries taken only with the 10x Macro View bias are profitable | 15m wtdiv bias any (len 50, thr 60.0, x10) 2R | 5499 | -0.235 | -0.121 | 0.71 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P3-021 | MCB entries taken only with the 10x Macro View bias are profitable | 15m wtdiv bias strong (len 50, thr 60.0, x10) 2R | 4308 | -0.245 | -0.134 | 0.69 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P3-022 | MCB entries taken only with the 10x Macro View bias are profitable | 24m stackA bias lean (len 50, thr 60.0, x10) 2R | 2653 | -0.156 | -0.067 | 0.79 | 0/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P3-023 | MCB entries taken only with the 10x Macro View bias are profitable | 24m stackA bias any (len 50, thr 60.0, x10) 2R | 2019 | -0.191 | -0.102 | 0.74 | 0/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P3-024 | MCB entries taken only with the 10x Macro View bias are profitable | 24m stackA bias strong (len 50, thr 60.0, x10) 2R | 1525 | -0.157 | -0.069 | 0.79 | 0/6 | 1/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P3-025 | MCB entries taken only with the 10x Macro View bias are profitable | 24m stackB bias lean (len 50, thr 60.0, x10) 2R | 3522 | -0.174 | -0.078 | 0.77 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P3-026 | MCB entries taken only with the 10x Macro View bias are profitable | 24m stackB bias any (len 50, thr 60.0, x10) 2R | 2754 | -0.197 | -0.101 | 0.74 | 0/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P3-027 | MCB entries taken only with the 10x Macro View bias are profitable | 24m stackB bias strong (len 50, thr 60.0, x10) 2R | 2092 | -0.173 | -0.076 | 0.77 | 0/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P3-028 | MCB entries taken only with the 10x Macro View bias are profitable | 24m wtdiv bias lean (len 50, thr 60.0, x10) 2R | 4931 | -0.136 | -0.048 | 0.81 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P3-029 | MCB entries taken only with the 10x Macro View bias are profitable | 24m wtdiv bias any (len 50, thr 60.0, x10) 2R | 4001 | -0.172 | -0.085 | 0.77 | 0/6 | 0/9 | 0.00 | fails S1,S2,S3,S4,S5,S7,S8,S9 |
| P3-030 | MCB entries taken only with the 10x Macro View bias are profitable | 24m wtdiv bias strong (len 50, thr 60.0, x10) 2R | 3104 | -0.177 | -0.090 | 0.76 | 0/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P3-031 | MCB entries taken only with the 10x Macro View bias are profitable | 1h stackA bias lean (len 50, thr 60.0, x10) 2R | 1310 | -0.085 | -0.032 | 0.86 | 2/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P3-032 | MCB entries taken only with the 10x Macro View bias are profitable | 1h stackA bias any (len 50, thr 60.0, x10) 2R | 984 | -0.082 | -0.030 | 0.86 | 2/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P3-033 | MCB entries taken only with the 10x Macro View bias are profitable | 1h stackA bias strong (len 50, thr 60.0, x10) 2R | 762 | -0.055 | -0.004 | 0.91 | 2/6 | 2/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P3-034 | MCB entries taken only with the 10x Macro View bias are profitable | 1h stackB bias lean (len 50, thr 60.0, x10) 2R | 1870 | -0.115 | -0.057 | 0.82 | 0/6 | 1/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P3-035 | MCB entries taken only with the 10x Macro View bias are profitable | 1h stackB bias any (len 50, thr 60.0, x10) 2R | 1402 | -0.075 | -0.017 | 0.88 | 1/6 | 3/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P3-036 | MCB entries taken only with the 10x Macro View bias are profitable | 1h stackB bias strong (len 50, thr 60.0, x10) 2R | 1087 | -0.053 | +0.002 | 0.91 | 2/6 | 3/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P3-037 | MCB entries taken only with the 10x Macro View bias are profitable | 1h wtdiv bias lean (len 50, thr 60.0, x10) 2R | 2758 | -0.091 | -0.039 | 0.85 | 0/6 | 0/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P3-038 | MCB entries taken only with the 10x Macro View bias are profitable | 1h wtdiv bias any (len 50, thr 60.0, x10) 2R | 2110 | -0.090 | -0.038 | 0.85 | 0/6 | 2/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |
| P3-039 | MCB entries taken only with the 10x Macro View bias are profitable | 1h wtdiv bias strong (len 50, thr 60.0, x10) 2R | 1660 | -0.074 | -0.022 | 0.88 | 1/6 | 4/9 | 0.00 | fails S1,S2,S4,S5,S7,S8,S9 |

## E003 (descriptive, counts: no)
- Date: 2026-11-16
- Hypothesis: none chosen. Diagnostic requested by the user before considering partial exits: is there any
  favourable/adverse asymmetry after entry that some exit rule (partials, trailing, breakeven) could extract?
- Configuration: filled entries (independent simulation, no portfolio) of stack v2 A and B, pooled range flips A, and
  stack v2 A gated by Macro View lean, on 15m/24m/1h; CONTROL = random bars and directions with a 1.5 ATR stop.
  Measured on 1m bars over 24 h after the fill: MFE, MAE, and first touch of +x vs -x R (x = 0.5, 1, 2).
- Split: walk-forward test period 2023-01-01..2025-11-14.
- Results: favourable-first rates 46-51% for every entry set (control 48-50%); median MFE equals median MAE within
  about 0.1R everywhere (e.g. stack A 1h 1.18 vs 1.19 R); longs and shorts both symmetric. Full table:
  reports/phase3/EXCURSION_REPORT.md.
- Verdict: no exploitable asymmetry. No exit rule can turn these entries into an edge; partial-exit hypothesis not
  pursued.

## E004 and E005 declared before running (descriptive, counts: no), 2026-11-18
- **E004 range edges.** Ranges from the frozen v2 detector (k=3, tol 1.0 ATR, height 2-12 ATR) on 15m, 24m, 1h, 4h,
  9 coins, dev period. D1: lifetime after confirmation and share of time inside a confirmed range. D2: each first touch
  of an active range edge from inside (bar low within 0.25 ATR of the range low, previous close outside that zone;
  mirrored for the top). From the touch bar's close, on 1m bars: does price reach the range midpoint before trading
  0.25 ATR beyond the edge? Benchmark = driftless random walk (gambler's ruin) probability for the same distances.
  Implied fade-to-mid result in R (stop 0.25 ATR beyond the edge) before and after fees.
  **Promising only if** actual minus benchmark >= +5 percentage points AND implied net R >= +0.10 AND >= 300 touches.
- **E005 HTF entries with LTF structure stops.** Signals on 1h and 4h (divergence stack v2 Variant A, WT dot divergence
  alone), ungated and gated by Macro View lean (10 x the signal TF). Stop = most recent confirmed 15m zigzag swing
  (k=3) beyond the entry, plus 1 x ATR(15m). From the signal bar's close, on 1m bars over 24 h (1h signals) / 48 h
  (4h signals): first touch of +x R vs -x R for x = 0.5, 1, 2, 3. Control: random 1h/4h bars, random direction, same
  stop construction. Walk-forward test period 2023-01-01..2025-11-14.
  **Promising only if** favourable-first at 0.5R and 1R >= 55% AND >= control + 5 points AND >= 300 signals.

## E004 result (descriptive, counts: no), 2026-11-18
- Ranges (frozen v2 detector): median life after confirmation 3.8 h (15m), 6 h (24m), 17 h (1h), 72 h (4h); price is
  inside a confirmed range about 7% of the time on every TF.
- Edge touches (8,451 / 5,161 / 1,998 / 472 on 15m / 24m / 1h / 4h): price reached the midpoint first 18.1% / 17.4% /
  17.5% / 13.6% of the time vs a random-walk benchmark of 20.5% / 19.6% / 19.5% / 17.9%: edges hold 2 to 4 points WORSE
  than chance, on both bottoms and tops. Gross fade-to-mid result negative everywhere (-0.12 to -0.39 R before fees;
  the mean fee column is inflated by touches closing right at the edge, irrelevant to the verdict).
- Verdict against the declared rule: NOT promising (difference negative). Range-edge fading closed.

## E005 result (descriptive, counts: no), 2026-11-18
- 1h signals with a 15m structure stop (+1 ATR): favourable-first 49.6-51.5% at 0.5R, 48.6-49.8% at 1R; control 50.9% /
  50.5%. No reaction.
- 4h signals: favourable-first 52.2-54.6% at 0.5R and 53.2-55.0% at 1R vs control 50.6% / 48.8% (about +3 to +6 points,
  n = 447 to 2,788), falling to 45-50% at 2R and 42-47% at 3R. A small early favourable reaction that fades.
- Verdict against the declared rule (>= 55% at BOTH 0.5R and 1R, >= control + 5 points, >= 300 signals): NOT met by
  any group (best: 4h WT divergence with Macro View lean, 52.2% / 55.0%). Not promising by the frozen rule.
  Observation recorded without acting on it: the 4h early reaction is the first non-random pattern in the study; at a
  1R target its implied net result is roughly +0.03 to +0.05 R after fees, below the +0.10 R bar.

## Hypothesis H-VS, 4h volume-spike trend continuation (counts: yes, 12 configurations)
- Date: 2026-11-18. Declared in PROTOCOL Amendment 3. Walk-forward test period, 9 coins. DSR with N = 429.

| id | hypothesis | configuration | n | exp R | gross R | PF | folds+ | coins+ | DSR | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| P3-040 | 4h volume-spike trend continuation holds on 9 coins | C1 original: market entry, 50-day hold (vol x1.8, EMA200, 1.5 ATR, 2.0R) | 1192 | +0.072 | +0.098 | 1.11 | 4/6 | 8/9 | 0.00 | fails S1,S2,S5,S7,S8,S9 |
| P3-041 | 4h volume-spike trend continuation holds on 9 coins | C2 brief: limit at close, 24h timeout (vol x1.8, EMA200, 1.5 ATR, 2.0R) | 1684 | +0.037 | +0.065 | 1.08 | 4/6 | 6/9 | 0.00 | fails S1,S2,S5,S7,S8 |
| P3-042 | 4h volume-spike trend continuation holds on 9 coins | C3 limit at close, 50-day hold (vol x1.8, EMA200, 1.5 ATR, 2.0R) | 1177 | +0.073 | +0.100 | 1.11 | 4/6 | 8/9 | 0.00 | fails S1,S2,S5,S7,S8,S9 |
| P3-043 | 4h volume-spike trend continuation holds on 9 coins | C4 market entry, 24h timeout (vol x1.8, EMA200, 1.5 ATR, 2.0R) | 1711 | +0.031 | +0.059 | 1.07 | 4/6 | 6/9 | 0.00 | fails S1,S2,S5,S7,S8,S9 |
| P3-044 | 4h volume-spike trend continuation holds on 9 coins | neighbour of P3-042: vol_mult=1.5 (vol x1.5, EMA200, 1.5 ATR, 2.0R) | 1348 | +0.025 | +0.050 | 1.04 | 4/6 | 6/9 | 0.00 | fails S1,S2,S5,S7,S8 |
| P3-045 | 4h volume-spike trend continuation holds on 9 coins | neighbour of P3-042: vol_mult=2.1 (vol x2.1, EMA200, 1.5 ATR, 2.0R) | 1017 | +0.126 | +0.153 | 1.20 | 5/6 | 7/9 | 0.00 | fails S2,S5,S7,S8 |
| P3-046 | 4h volume-spike trend continuation holds on 9 coins | neighbour of P3-042: ema_len=150 (vol x1.8, EMA150, 1.5 ATR, 2.0R) | 1188 | +0.098 | +0.125 | 1.15 | 5/6 | 8/9 | 0.00 | fails S1,S2,S7,S8 |
| P3-047 | 4h volume-spike trend continuation holds on 9 coins | neighbour of P3-042: ema_len=250 (vol x1.8, EMA250, 1.5 ATR, 2.0R) | 1179 | +0.066 | +0.092 | 1.10 | 4/6 | 7/9 | 0.00 | fails S1,S2,S5,S7,S8 |
| P3-048 | 4h volume-spike trend continuation holds on 9 coins | neighbour of P3-042: stop_atr=1.0 (vol x1.8, EMA200, 1.0 ATR, 2.0R) | 1825 | +0.071 | +0.112 | 1.11 | 5/6 | 8/9 | 0.00 | fails S1,S2,S7,S8 |
| P3-049 | 4h volume-spike trend continuation holds on 9 coins | neighbour of P3-042: stop_atr=2.0 (vol x1.8, EMA200, 2.0 ATR, 2.0R) | 785 | +0.079 | +0.098 | 1.12 | 5/6 | 7/9 | 0.00 | fails S1,S2,S5,S7,S8 |
| P3-050 | 4h volume-spike trend continuation holds on 9 coins | neighbour of P3-042: target_r=1.5 (vol x1.8, EMA200, 1.5 ATR, 1.5R) | 1438 | +0.078 | +0.105 | 1.13 | 5/6 | 8/9 | 0.00 | fails S1,S2,S5,S7,S8 |
| P3-051 | 4h volume-spike trend continuation holds on 9 coins | neighbour of P3-042: target_r=3.0 (vol x1.8, EMA200, 1.5 ATR, 3.0R) | 909 | +0.071 | +0.097 | 1.09 | 4/6 | 7/9 | 0.00 | fails S1,S2,S5,S7,S8,S9 |

## E006 declared before running (descriptive, counts: no), 2026-11-18: next-day odds from the daily timeframe
- **Days:** UTC days (Binance 1D bars). Predictors use day D only (known at D's close); targets are about day D+1.
  9 coins, dev period. Split: first half 2022-01-01..2023-12-31, second half 2024-01-01..2025-11-14.
- **Targets (D+1):** T1 first touch from D+1's open on 1m bars: +x before -x, x = 0.25 and 0.5 x ATR14(1D) as of D's
  close (neither within the day = excluded; same minute = counted as neither). T2 bigger extension from the open:
  (high - open) > (open - low).
- **Predictors (5, fixed cut-offs, not fitted):** P1 D's close location (close - low)/(high - low): < 0.33 / 0.33-0.67
  / > 0.67. P2 D's wick imbalance (upper wick - lower wick)/(high - low): < -0.2 / middle / > 0.2. P3 D up day vs down
  day. P4 D+1 weekend vs weekday. P5 funding z-score at D's close (90 prints): < -1.5 / middle / > +1.5.
- **Statistics:** P(up) per bin; difference between the extreme bins; z from a day-clustered bootstrap (resampling
  whole dates across coins, 1,000 draws), because the coins move together.
- **Promising only if, for some predictor and target:** the extreme-bin difference is >= 6 percentage points with the
  SAME sign in both halves, AND |z| >= 3 on the full dev period, AND (for T1 at x = 0.5 ATR) the better bin's
  first-touch rate is >= 55% (or <= 45%), AND >= 300 days per bin. Otherwise the idea closes.
