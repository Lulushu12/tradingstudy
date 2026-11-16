# Phase 3: discovery results

Walk-forward rule search (<= 2 conditions, fixed feature list, thresholds from each fold's training data, 7-day embargo and purge). Out-of-sample = the 6 test folds 2023-01-01 to 2025-11-14, full engine and portfolio rules. Deflated Sharpe uses N = 390 (all configurations so far).

## 1. Procedures (structure stop, 2R)

| id | Family | TF | Var | OOS trades | Per day | Win | Gross R | Net exp R | PF | Folds + | Coins + | DSR | Rule stability | Final rule |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P3-001 | stack | 15m | A | 444 | 0.42 | 31% | -0.153 | -0.301 | 0.65 | 1/6 | 1/9 | 0.00 | 1/6 | r2_rel == 1.0 AND fib_exec_in_0618_zone == 1.0 |
| P3-002 | stack | 15m | B | 251 | 0.24 | 31% | -0.166 | -0.278 | 0.65 | 0/6 | 2/9 | 0.00 | 1/6 | r2_rel == 1.0 AND fib_exec_in_0618_zone == 1.0 |
| P3-003 | stack | 24m | A | 264 | 0.25 | 37% | -0.047 | -0.148 | 0.79 | 2/6 | 2/9 | 0.00 | 3/6 | r1_rel == 1.0 AND htf_near_cross_rel == 1.0 |
| P3-004 | stack | 24m | B | 269 | 0.26 | 38% | +0.018 | -0.085 | 0.88 | 3/6 | 1/9 | 0.00 | 4/6 | r1_rel == 1.0 AND htf_near_cross_rel == 1.0 |
| P3-005 | stack | 1h | A | 192 | 0.18 | 39% | -0.062 | -0.113 | 0.81 | 2/6 | 3/9 | 0.00 | 1/6 | htf_near_cross_rel == 1.0 AND session == asia |
| P3-006 | stack | 1h | B | 203 | 0.19 | 33% | -0.097 | -0.163 | 0.76 | 1/6 | 4/9 | 0.00 | 0/6 | cmf4h_rel <= -0.137 AND htf_near_cross_rel == 1.0 |
| P3-007 | flips | 15m | A | 185 | 0.18 | 31% | -0.135 | -0.279 | 0.66 | 2/6 | 1/9 | 0.00 | 0/6 | atr_pctile_30d > 0.705 AND cmf_rel <= -0.0909 |
| P3-008 | flips | 15m | B | 210 | 0.20 | 31% | -0.203 | -0.360 | 0.59 | 1/6 | 0/9 | 0.00 | 0/6 | cmf4h_rel <= -0.0163 AND r2_rel == 0.0 |
| P3-009 | flips | 24m | A | 179 | 0.17 | 35% | -0.054 | -0.152 | 0.80 | 3/6 | 4/9 | 0.00 | 3/6 | funding_z_rel <= -0.117 AND confluence_types <= 1 |
| P3-010 | flips | 24m | B | 214 | 0.20 | 34% | -0.110 | -0.245 | 0.70 | 1/6 | 2/9 | 0.00 | 2/6 | atr_pctile_30d > 0.746 AND cmf4h_rel <= 0.0889 |
| P3-011 | flips | 1h | A | 147 | 0.14 | 31% | -0.155 | -0.228 | 0.69 | 2/6 | 2/9 | 0.00 | 0/6 | confluence_types <= 1 AND sr_dist <= 1.14 |
| P3-012 | flips | 1h | B | 149 | 0.14 | 31% | -0.188 | -0.264 | 0.65 | 2/6 | 2/9 | 0.00 | 0/6 | atr_pctile_30d > 0.486 AND cmf_rel <= 0.0269 |

## 2. Rule chosen in each fold (training data only)

**P3-001 stack 15m A**

| Fold | Rule | Train trades | Train exp R | Test signals | Selected | Test exp R |
|---|---|---|---|---|---|---|
| 2023H1 | htf_mf_rel == 1.0 AND session == europe | 251 | +0.225 | 2421 | 121 | -0.289 |
| 2023H2 | htf_mf_rel == 1.0 AND session == europe | 364 | +0.113 | 2691 | 122 | -0.174 |
| 2024H1 | funding_z_rel > 0.285 AND fib_exec_in_0618_zone == 1.0 | 106 | +0.058 | 3062 | 29 | -0.414 |
| 2024H2 | atr_pctile_30d <= 0.359 AND session == europe | 1021 | -0.000 | 3066 | 231 | -0.444 |
| 2025H1 | r2_rel == 1.0 AND session == late | 303 | +0.017 | 3271 | 71 | -0.108 |
| 2025H2 | r2_rel == 1.0 AND fib_exec_in_0618_zone == 1.0 | 101 | +0.198 | 2577 | 11 | +0.102 |

**P3-002 stack 15m B**

| Fold | Rule | Train trades | Train exp R | Test signals | Selected | Test exp R |
|---|---|---|---|---|---|---|
| 2023H1 | cmf_rel > 0.0321 AND htf_near_cross_rel == 1.0 | 190 | +0.083 | 3257 | 99 | -0.185 |
| 2023H2 | cmf4h_rel > 0.00751 AND fib_exec_in_0618_zone == 1.0 | 109 | +0.045 | 3669 | 49 | -0.184 |
| 2024H1 | session == asia AND fib_exec_in_0618_zone == 1.0 | 109 | +0.182 | 4107 | 41 | -0.119 |
| 2024H2 | session == asia AND fib_exec_in_0618_zone == 1.0 | 142 | +0.097 | 4227 | 40 | -0.315 |
| 2025H1 | session == asia AND fib_exec_in_0618_zone == 1.0 | 180 | +0.053 | 4439 | 43 | -0.670 |
| 2025H2 | r2_rel == 1.0 AND fib_exec_in_0618_zone == 1.0 | 130 | -0.000 | 3439 | 12 | -0.327 |

**P3-003 stack 24m A**

| Fold | Rule | Train trades | Train exp R | Test signals | Selected | Test exp R |
|---|---|---|---|---|---|---|
| 2023H1 | r2_rel == 1.0 AND session == asia | 114 | +0.248 | 1472 | 56 | -0.489 |
| 2023H2 | r1_rel == 1.0 AND session == asia | 481 | +0.099 | 1664 | 171 | +0.024 |
| 2024H1 | r1_rel == 1.0 AND htf_near_cross_rel == 1.0 | 101 | +0.282 | 1746 | 26 | -0.175 |
| 2024H2 | r1_rel == 1.0 AND htf_near_cross_rel == 1.0 | 126 | +0.173 | 1933 | 31 | -0.360 |
| 2025H1 | session == us AND fib_exec_in_0618_zone == 1.0 | 103 | +0.124 | 1952 | 22 | -0.400 |
| 2025H2 | r1_rel == 1.0 AND htf_near_cross_rel == 1.0 | 193 | +0.111 | 1537 | 30 | +0.023 |

**P3-004 stack 24m B**

| Fold | Rule | Train trades | Train exp R | Test signals | Selected | Test exp R |
|---|---|---|---|---|---|---|
| 2023H1 | r2_rel == 1.0 AND session == asia | 155 | +0.187 | 1989 | 84 | -0.264 |
| 2023H2 | funding_z_rel <= -0.597 AND r2_rel == 1.0 | 100 | +0.283 | 2193 | 43 | -0.089 |
| 2024H1 | r1_rel == 1.0 AND htf_near_cross_rel == 1.0 | 147 | +0.242 | 2417 | 50 | +0.020 |
| 2024H2 | r1_rel == 1.0 AND htf_near_cross_rel == 1.0 | 196 | +0.155 | 2612 | 55 | +0.169 |
| 2025H1 | r1_rel == 1.0 AND htf_near_cross_rel == 1.0 | 244 | +0.157 | 2688 | 57 | +0.039 |
| 2025H2 | r1_rel == 1.0 AND htf_near_cross_rel == 1.0 | 298 | +0.153 | 2108 | 46 | -0.330 |

**P3-005 stack 1h A**

| Fold | Rule | Train trades | Train exp R | Test signals | Selected | Test exp R |
|---|---|---|---|---|---|---|
| 2023H1 | sr_dist > 0.96 AND session == late | 115 | +0.241 | 617 | 61 | +0.023 |
| 2023H2 | r1_rel == -1.0 AND htf_near_cross_rel == 1.0 | 106 | +0.198 | 667 | 42 | -0.079 |
| 2024H1 | atr_pctile_30d <= 0.739 AND htf_near_cross_rel == 1.0 | 127 | +0.307 | 763 | 45 | +0.029 |
| 2024H2 | atr_pctile_30d <= 0.718 AND htf_near_cross_rel == 1.0 | 162 | +0.287 | 948 | 60 | -0.386 |
| 2025H1 | cmf4h_rel > -0.0422 AND htf_near_cross_rel == 1.0 | 121 | +0.176 | 697 | 14 | -0.227 |
| 2025H2 | htf_near_cross_rel == 1.0 AND session == asia | 138 | +0.242 | 568 | 17 | -0.021 |

**P3-006 stack 1h B**

| Fold | Rule | Train trades | Train exp R | Test signals | Selected | Test exp R |
|---|---|---|---|---|---|---|
| 2023H1 | atr_pctile_30d <= 0.369 AND session == europe | 113 | +0.139 | 804 | 44 | -0.004 |
| 2023H2 | htf_mf_rel == 1.0 AND session == europe | 128 | +0.196 | 903 | 50 | -0.007 |
| 2024H1 | funding_z_rel <= -0.672 AND session == late | 123 | +0.166 | 982 | 27 | +0.103 |
| 2024H2 | htf_near_cross_rel == 1.0 AND session == us | 116 | +0.192 | 1204 | 43 | -0.295 |
| 2025H1 | funding_z_rel <= -0.691 AND session == late | 194 | +0.098 | 1061 | 48 | -0.353 |
| 2025H2 | funding_z_rel <= -0.705 AND htf_near_cross_rel == 1.0 | 145 | +0.143 | 831 | 22 | -0.459 |

**P3-007 flips 15m A**

| Fold | Rule | Train trades | Train exp R | Test signals | Selected | Test exp R |
|---|---|---|---|---|---|---|
| 2023H1 | atr_pctile_30d > 0.326 AND sr_dist > 0.589 | 100 | -0.004 | 151 | 67 | -0.467 |
| 2023H2 | funding_z_rel <= -0.191 | 121 | -0.098 | 138 | 50 | -0.340 |
| 2024H1 | atr_pctile_30d > 0.366 AND sr_dist > 1.18 | 100 | +0.008 | 133 | 25 | +0.113 |
| 2024H2 | atr_pctile_30d > 0.703 AND htf_mf_rel == 1.0 | 109 | +0.083 | 124 | 31 | -0.414 |
| 2025H1 | cmf_rel <= -0.0905 AND cmf4h_rel > -0.0281 | 144 | -0.001 | 136 | 30 | +0.065 |
| 2025H2 | sr_dist > 1.19 AND r1_rel == -1.0 | 128 | +0.102 | 99 | 8 | -0.311 |

**P3-008 flips 15m B**

| Fold | Rule | Train trades | Train exp R | Test signals | Selected | Test exp R |
|---|---|---|---|---|---|---|
| 2023H1 | cmf_rel <= 0.00239 AND confluence_types <= 2 | 128 | -0.032 | 187 | 89 | -0.702 |
| 2023H2 | atr_pctile_30d > 0.368 AND sr_dist > 0.36 | 145 | -0.163 | 172 | 77 | -0.192 |
| 2024H1 | atr_pctile_30d > 0.397 AND cmf4h_rel <= -0.0163 | 101 | +0.093 | 159 | 30 | +0.088 |
| 2024H2 | atr_pctile_30d > 0.39 AND cmf4h_rel <= -0.0151 | 125 | +0.089 | 161 | 43 | -0.389 |
| 2025H1 | atr_pctile_30d > 0.406 AND cmf4h_rel <= -0.0151 | 150 | +0.022 | 174 | 41 | -0.306 |
| 2025H2 | atr_pctile_30d > 0.406 AND cmf4h_rel <= -0.0166 | 174 | -0.021 | 130 | 25 | -0.377 |

**P3-009 flips 24m A**

| Fold | Rule | Train trades | Train exp R | Test signals | Selected | Test exp R |
|---|---|---|---|---|---|---|
| 2023H1 | atr_pctile_30d > 0.361 AND htf_near_cross_rel == 0.0 | 102 | +0.031 | 102 | 62 | -0.313 |
| 2023H2 | atr_pctile_30d > 0.333 AND cmf4h_rel <= 0.0728 | 108 | +0.137 | 109 | 53 | -0.198 |
| 2024H1 | funding_z_rel <= -0.126 AND htf_near_cross_rel == 0.0 | 108 | +0.135 | 101 | 38 | +0.003 |
| 2024H2 | funding_z_rel <= -0.137 AND confluence_types <= 1 | 104 | +0.238 | 96 | 24 | +0.107 |
| 2025H1 | funding_z_rel <= -0.141 AND confluence_types <= 1 | 126 | +0.226 | 89 | 17 | -0.572 |
| 2025H2 | funding_z_rel <= -0.12 AND confluence_types <= 1 | 146 | +0.121 | 65 | 14 | +0.263 |

**P3-010 flips 24m B**

| Fold | Rule | Train trades | Train exp R | Test signals | Selected | Test exp R |
|---|---|---|---|---|---|---|
| 2023H1 | htf_near_cross_rel == 0.0 | 135 | -0.250 | 145 | 133 | -0.288 |
| 2023H2 | atr_pctile_30d > 0.33 AND cmf4h_rel <= 0.0731 | 107 | -0.152 | 133 | 59 | -0.261 |
| 2024H1 | funding_z_rel <= 0.00647 AND htf_near_cross_rel == 0.0 | 104 | -0.105 | 135 | 56 | -0.214 |
| 2024H2 | funding_z_rel <= -0.0729 AND cmf4h_rel <= 0.085 | 106 | +0.040 | 126 | 25 | +0.500 |
| 2025H1 | funding_z_rel <= -0.0528 AND cmf4h_rel <= 0.086 | 124 | +0.107 | 124 | 26 | -0.630 |
| 2025H2 | atr_pctile_30d > 0.762 AND cmf4h_rel <= 0.0886 | 124 | +0.087 | 90 | 17 | -0.503 |

**P3-011 flips 1h A**

| Fold | Rule | Train trades | Train exp R | Test signals | Selected | Test exp R |
|---|---|---|---|---|---|---|
| 2023H1 | no filter | 49 | +0.093 | 39 | 39 | -0.020 |
| 2023H2 | no filter | 86 | +0.054 | 38 | 38 | -0.535 |
| 2024H1 | htf_near_cross_rel == 0.0 | 118 | -0.088 | 30 | 30 | -0.187 |
| 2024H2 | sr_dist <= 1.19 AND fib_exec_in_0618_zone == 0.0 | 100 | +0.050 | 22 | 18 | -0.625 |
| 2025H1 | sr_dist <= 1.14 AND htf_near_cross_rel == 0.0 | 112 | -0.007 | 31 | 18 | +0.004 |
| 2025H2 | sr_dist <= 1.14 AND htf_near_cross_rel == 0.0 | 131 | -0.014 | 19 | 13 | +0.094 |

**P3-012 flips 1h B**

| Fold | Rule | Train trades | Train exp R | Test signals | Selected | Test exp R |
|---|---|---|---|---|---|---|
| 2023H1 | no filter | 56 | -0.233 | 52 | 52 | -0.560 |
| 2023H2 | no filter | 94 | -0.350 | 52 | 52 | +0.093 |
| 2024H1 | htf_near_cross_rel == 0.0 AND fib_exec_in_0618_zone == 0.0 | 118 | -0.245 | 38 | 38 | -0.416 |
| 2024H2 | atr_pctile_30d > 0.478 AND htf_near_cross_rel == 0.0 | 101 | -0.106 | 33 | 24 | -0.507 |
| 2025H1 | atr_pctile_30d > 0.483 AND htf_near_cross_rel == 0.0 | 118 | -0.164 | 43 | 25 | -0.155 |
| 2025H2 | atr_pctile_30d > 0.486 AND fib_exec_in_0618_zone == 0.0 | 136 | -0.146 | 23 | 14 | +0.189 |

## 3. Protocol criteria

- P3-001: fails S1, S2, S3, S4, S5, S7, S8, S9, S10
- P3-002: fails S1, S2, S3, S4, S5, S7, S8, S9, S10
- P3-003: fails S1, S2, S3, S4, S5, S7, S8, S9, S10
- P3-004: fails S1, S2, S3, S4, S5, S7, S8, S9
- P3-005: fails S1, S2, S3, S4, S5, S7, S9, S10
- P3-006: fails S1, S2, S3, S4, S5, S7, S9, S10
- P3-007: fails S1, S2, S3, S4, S5, S7, S8, S9, S10
- P3-008: fails S1, S2, S3, S4, S5, S7, S8, S9, S10
- P3-009: fails S1, S2, S3, S4, S5, S7, S9, S10
- P3-010: fails S1, S2, S3, S4, S5, S7, S8, S9, S10
- P3-011: fails S1, S2, S3, S4, S5, S7, S9, S10
- P3-012: fails S1, S2, S3, S4, S5, S7, S9, S10
