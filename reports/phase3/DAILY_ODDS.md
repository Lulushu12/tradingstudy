# E006: next-day odds from the daily timeframe (descriptive, declared before running)

1413 days x 9 coins = 12217 coin-days in the dev period (SUI from 2023-05). Unconditional rates: T1 up first (0.25 ATR) 48.8%, T1 up first (0.5 ATR) 48.6%, T2 bigger up-extension 49.1%.

Difference = P(up | second bin) - P(up | first bin). z from a day-clustered bootstrap. Halves: 2022-2023 / 2024-2025.

## P1_close_loc

| Target | Bin | Days | P(up) full | P(up) 2022-23 | P(up) 2024-25 |
|---|---|---|---|---|---|
| T1 up first (0.25 ATR) | high | 4021 | 51.0% | 50.8% | 51.2% |
| T1 up first (0.25 ATR) | mid | 3947 | 47.6% | 45.7% | 49.5% |
| T1 up first (0.25 ATR) | low | 3670 | 47.7% | 48.0% | 47.5% |
| T1 up first (0.5 ATR) | high | 2868 | 52.7% | 51.3% | 54.0% |
| T1 up first (0.5 ATR) | mid | 2753 | 47.3% | 44.6% | 49.8% |
| T1 up first (0.5 ATR) | low | 2524 | 45.4% | 49.0% | 42.1% |
| T2 bigger up-extension | high | 4189 | 50.6% | 49.2% | 52.0% |
| T2 bigger up-extension | mid | 4198 | 49.0% | 46.5% | 51.6% |
| T2 bigger up-extension | low | 3830 | 47.6% | 50.3% | 44.9% |

| Target | Difference (high minus low) full | 2022-23 | 2024-25 | z | Promising? |
|---|---|---|---|---|---|
| T1 up first (0.25 ATR) | +3.3 pts | +2.8 | +3.8 | +1.55 | no |
| T1 up first (0.5 ATR) | +7.4 pts | +2.3 | +12.0 | +2.87 | no |
| T2 bigger up-extension | +3.0 pts | -1.2 | +7.1 | +1.47 | no |

## P2_wick_imbalance

| Target | Bin | Days | P(up) full | P(up) 2022-23 | P(up) 2024-25 |
|---|---|---|---|---|---|
| T1 up first (0.25 ATR) | balanced | 5801 | 49.7% | 49.1% | 50.3% |
| T1 up first (0.25 ATR) | lower wick bigger | 3120 | 48.9% | 48.8% | 49.0% |
| T1 up first (0.25 ATR) | upper wick bigger | 2717 | 46.9% | 45.3% | 48.4% |
| T1 up first (0.5 ATR) | balanced | 4122 | 49.2% | 48.9% | 49.5% |
| T1 up first (0.5 ATR) | lower wick bigger | 2149 | 49.7% | 50.0% | 49.4% |
| T1 up first (0.5 ATR) | upper wick bigger | 1874 | 46.0% | 45.2% | 46.7% |
| T2 bigger up-extension | balanced | 6080 | 49.2% | 48.7% | 49.6% |
| T2 bigger up-extension | lower wick bigger | 3283 | 50.7% | 50.1% | 51.2% |
| T2 bigger up-extension | upper wick bigger | 2854 | 47.1% | 46.3% | 47.9% |

| Target | Difference (upper wick bigger minus lower wick bigger) full | 2022-23 | 2024-25 | z | Promising? |
|---|---|---|---|---|---|
| T1 up first (0.25 ATR) | -2.0 pts | -3.5 | -0.6 | -0.86 | no |
| T1 up first (0.5 ATR) | -3.7 pts | -4.8 | -2.7 | -1.34 | no |
| T2 bigger up-extension | -3.5 pts | -3.8 | -3.3 | -1.53 | no |

## P3_day_dir

| Target | Bin | Days | P(up) full | P(up) 2022-23 | P(up) 2024-25 |
|---|---|---|---|---|---|
| T1 up first (0.25 ATR) | up day | 5789 | 49.6% | 48.4% | 50.7% |
| T1 up first (0.25 ATR) | down day | 5849 | 48.1% | 47.9% | 48.3% |
| T1 up first (0.5 ATR) | up day | 4113 | 50.0% | 48.4% | 51.6% |
| T1 up first (0.5 ATR) | down day | 4032 | 47.1% | 48.3% | 46.1% |
| T2 bigger up-extension | up day | 6061 | 49.2% | 47.2% | 51.1% |
| T2 bigger up-extension | down day | 6156 | 49.1% | 50.0% | 48.2% |

| Target | Difference (up day minus down day) full | 2022-23 | 2024-25 | z | Promising? |
|---|---|---|---|---|---|
| T1 up first (0.25 ATR) | +1.5 pts | +0.5 | +2.4 | +0.89 | no |
| T1 up first (0.5 ATR) | +2.9 pts | +0.1 | +5.5 | +1.44 | no |
| T2 bigger up-extension | +0.1 pts | -2.8 | +2.9 | +0.06 | no |

## P4_next_weekend

| Target | Bin | Days | P(up) full | P(up) 2022-23 | P(up) 2024-25 |
|---|---|---|---|---|---|
| T1 up first (0.25 ATR) | weekend | 3048 | 51.6% | 52.5% | 50.7% |
| T1 up first (0.25 ATR) | weekday | 8590 | 47.8% | 46.6% | 49.0% |
| T1 up first (0.5 ATR) | weekend | 1685 | 51.2% | 50.7% | 51.7% |
| T1 up first (0.5 ATR) | weekday | 6460 | 47.9% | 47.7% | 48.1% |
| T2 bigger up-extension | weekend | 3484 | 51.2% | 50.9% | 51.5% |
| T2 bigger up-extension | weekday | 8733 | 48.3% | 47.6% | 48.9% |

| Target | Difference (weekend minus weekday) full | 2022-23 | 2024-25 | z | Promising? |
|---|---|---|---|---|---|
| T1 up first (0.25 ATR) | +3.8 pts | +5.9 | +1.7 | +1.73 | no |
| T1 up first (0.5 ATR) | +3.3 pts | +3.0 | +3.6 | +1.14 | no |
| T2 bigger up-extension | +2.9 pts | +3.3 | +2.6 | +1.38 | no |

## P5_funding

| Target | Bin | Days | P(up) full | P(up) 2022-23 | P(up) 2024-25 |
|---|---|---|---|---|---|
| T1 up first (0.25 ATR) | middle | 10244 | 49.0% | 48.3% | 49.6% |
| T1 up first (0.25 ATR) | z < -1.5 | 994 | 48.3% | 47.4% | 49.3% |
| T1 up first (0.25 ATR) | z > +1.5 | 398 | 46.7% | 45.0% | 47.7% |
| T1 up first (0.5 ATR) | middle | 7119 | 48.9% | 48.5% | 49.2% |
| T1 up first (0.5 ATR) | z < -1.5 | 709 | 45.3% | 45.5% | 45.0% |
| T1 up first (0.5 ATR) | z > +1.5 | 316 | 50.3% | 53.0% | 48.8% |
| T2 bigger up-extension | middle | 10758 | 49.3% | 48.8% | 49.8% |
| T2 bigger up-extension | z < -1.5 | 1048 | 47.0% | 47.4% | 46.7% |
| T2 bigger up-extension | z > +1.5 | 409 | 49.6% | 47.2% | 50.9% |

| Target | Difference (z > +1.5 minus z < -1.5) full | 2022-23 | 2024-25 | z | Promising? |
|---|---|---|---|---|---|
| T1 up first (0.25 ATR) | -1.6 pts | -2.4 | -1.6 | -0.35 | no |
| T1 up first (0.5 ATR) | +5.0 pts | +7.5 | +3.7 | +1.04 | no |
| T2 bigger up-extension | +2.6 pts | -0.1 | +4.3 | +0.63 | no |

## Verdict against the declared rule

Predictor/target pairs meeting the rule: 0 of 15.
