# Phase 1: Categorical Fade v1 walk-forward

Rules per CATEGORICAL_SPEC.md, costs and kill thresholds per AUDIT_COMMITMENTS_CATEGORICAL.md. Causal ER threshold, both-touched resolves to the stop, one position at a time, 1% equity risk, 0.04%/side commission, 0.02%/fill slippage.

## 1. Pooled result

| metric | value |
|---|---|
| trades | 220 |
| signals skipped (already in a position) | 254 |
| win rate | 63.18% |
| net expectancy per trade | **-0.0497 R** |
| 95% block-bootstrap CI | [-0.1456, +0.0188] |
| median trade | +0.2394 R |
| profit factor | 0.871 |
| total return on 1% risk sizing | -11.0% |
| max drawdown | -17.11% |
| longest losing streak | 5 trades / 25 days |
| mean hold | 6.0 bars |

## 2. Per year

| year | n | win rate | net exp (R) | profit factor | return |
|---|---|---|---|---|---|
| 2021 | 3 | 100.0% | +0.7348 | inf | +2.2% |
| 2022 | 47 | 57.4% | -0.1445 | 0.672 | -6.7% |
| 2023 | 42 | 71.4% | -0.0226 | 0.925 | -1.0% |
| 2024 | 45 | 55.6% | -0.1552 | 0.663 | -6.9% |
| 2025 | 60 | 66.7% | +0.0148 | 1.042 | +0.7% |
| 2026 | 23 | 60.9% | +0.0300 | 1.073 | +0.6% |

## 3. Per regime

| regime | n | win rate | net exp (R) | profit factor |
|---|---|---|---|---|
| bull (200-bar up) | 117 | 68.4% | -0.0070 | 0.979 |
| bear (200-bar down) | 103 | 57.3% | -0.0982 | 0.779 |
| high vol | 42 | 57.1% | -0.0572 | 0.870 |
| low vol | 178 | 64.6% | -0.0480 | 0.871 |
| long side | 103 | 61.2% | -0.0998 | 0.754 |
| short side | 117 | 65.0% | -0.0057 | 0.985 |

## 4. Exit reason mix

| reason | n | share | mean R |
|---|---|---|---|
| stop | 81 | 36.8% | -1.0433 |
| target | 139 | 63.2% | +0.5293 |

## 5. Cost sweep: where does expectancy cross zero

| cost multiple | comm/side | slip/fill | trades | net exp (R) | profit factor |
|---|---|---|---|---|---|
| 0.0x | 0.000% | 0.000% | 220 | -0.0005 | 0.999 |
| 0.5x | 0.020% | 0.010% | 220 | -0.0252 | 0.933 |
| 1.0x | 0.040% | 0.020% | 220 | -0.0497 | 0.871 |
| 1.5x | 0.060% | 0.030% | 220 | -0.0740 | 0.811 |
| 2.0x | 0.080% | 0.040% | 220 | -0.0980 | 0.755 |
| 2.5x | 0.100% | 0.050% | 220 | -0.1218 | 0.701 |
| 3.0x | 0.120% | 0.060% | 220 | -0.1453 | 0.650 |
| 4.0x | 0.160% | 0.080% | 220 | -0.1918 | 0.555 |
| 5.0x | 0.200% | 0.100% | 220 | -0.2374 | 0.470 |

Expectancy is **negative at ZERO cost** (-0.0005 R). There is no cost headroom to measure because there is no gross edge to erode. This is the single most important number in the report: the system did not die of friction, it died of having nothing to spend.

## 6. Kill thresholds applied

| # | threshold | observed | verdict |
|---|---|---|---|
| K1 | pooled net expectancy > 0 | -0.0497 R | **FAIL** |
| K2 | trade count >= 300 | 220 trades | **FAIL** |
| K3 | profit factor >= 1.10 | 0.871 | **FAIL** |
| K4 | positive in >= 4 of 6 years | 3 of 6 | **FAIL** |
| K5 | cost headroom >= 1.5x | 0.0x | **FAIL** |
| K6 | max drawdown <= 35% | -17.11% | PASS |

### Verdict: **DEAD**
