# Hypothesis H-VS: 4h volume-spike trend continuation (PROTOCOL Amendment 3)

Pre-existing hypothesis from the user's earlier BTC study, tested on all 9 coins. Walk-forward test period 2023-01-01 to 2025-11-14, fees, slippage, portfolio guards. Deflated Sharpe uses N = 429 (frozen rule); DSR(N=12) counts only this hypothesis's configurations and is informational.

| id | Configuration | Trades | Per day | Win | Gross R | Net exp R | PF | Folds + | Coins + | Max coin share | 2022 (info) | P(breach 90d) | Max DD (dev, 0.5% risk) | DSR | DSR(N=12) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P3-040 | C1 original: market entry, 50-day hold | 1192 | 1.14 | 37% | +0.098 | +0.072 | 1.11 | 4/6 | 8/9 | 46% | +0.076 | 32% | 24% | 0.00 | 0.75 |
| P3-041 | C2 brief: limit at close, 24h timeout | 1684 | 1.61 | 45% | +0.065 | +0.037 | 1.08 | 4/6 | 6/9 | 54% | +0.104 | 29% | 31% | 0.00 | 0.57 |
| P3-042 | C3 limit at close, 50-day hold | 1177 | 1.12 | 37% | +0.100 | +0.073 | 1.11 | 4/6 | 8/9 | 43% | +0.105 | 32% | 24% | 0.00 | 0.75 |
| P3-043 | C4 market entry, 24h timeout | 1711 | 1.63 | 44% | +0.059 | +0.031 | 1.07 | 4/6 | 6/9 | 42% | +0.089 | 32% | 33% | 0.00 | 0.47 |
| P3-044 | neighbour of P3-042: vol_mult=1.5 | 1348 | 1.29 | 35% | +0.050 | +0.025 | 1.04 | 4/6 | 6/9 | 143% | +0.114 | 41% | 31% | 0.00 | 0.31 |
| P3-045 | neighbour of P3-042: vol_mult=2.1 | 1017 | 0.97 | 39% | +0.153 | +0.126 | 1.20 | 5/6 | 7/9 | 38% | +0.216 | 21% | 25% | 0.00 | 0.96 |
| P3-046 | neighbour of P3-042: ema_len=150 | 1188 | 1.13 | 38% | +0.125 | +0.098 | 1.15 | 5/6 | 8/9 | 27% | +0.117 | 28% | 23% | 0.00 | 0.90 |
| P3-047 | neighbour of P3-042: ema_len=250 | 1179 | 1.12 | 37% | +0.092 | +0.066 | 1.10 | 4/6 | 7/9 | 46% | +0.136 | 33% | 30% | 0.00 | 0.70 |
| P3-048 | neighbour of P3-042: stop_atr=1.0 | 1825 | 1.74 | 38% | +0.112 | +0.071 | 1.11 | 5/6 | 8/9 | 35% | +0.194 | 38% | 31% | 0.00 | 0.78 |
| P3-049 | neighbour of P3-042: stop_atr=2.0 | 785 | 0.75 | 37% | +0.098 | +0.079 | 1.12 | 5/6 | 7/9 | 59% | +0.072 | 22% | 14% | 0.00 | 0.75 |
| P3-050 | neighbour of P3-042: target_r=1.5 | 1438 | 1.37 | 45% | +0.105 | +0.078 | 1.13 | 5/6 | 8/9 | 46% | +0.140 | 27% | 27% | 0.00 | 0.89 |
| P3-051 | neighbour of P3-042: target_r=3.0 | 909 | 0.87 | 28% | +0.097 | +0.071 | 1.09 | 4/6 | 7/9 | 58% | +0.196 | 35% | 23% | 0.00 | 0.61 |

## Folds (net exp R)

| id | 2023H1 | 2023H2 | 2024H1 | 2024H2 | 2025H1 | 2025H2 |
|---|---|---|---|---|---|---|
| P3-040 | -0.072 | +0.036 | -0.007 | +0.168 | +0.087 | +0.282 |
| P3-041 | -0.101 | -0.081 | +0.050 | +0.146 | +0.099 | +0.166 |
| P3-042 | -0.073 | +0.058 | -0.028 | +0.147 | +0.098 | +0.304 |
| P3-043 | -0.122 | -0.084 | +0.063 | +0.117 | +0.108 | +0.160 |

## By coin (net exp R, core configurations)

| id | BTC | ETH | SOL | ADA | XRP | DOGE | SUI | LINK | AVAX |
|---|---|---|---|---|---|---|---|---|---|
| P3-040 | +0.16 | +0.09 | +0.25 | +0.04 | -0.08 | +0.09 | +0.01 | +0.05 | +0.03 |
| P3-041 | +0.10 | -0.01 | +0.23 | -0.00 | -0.08 | +0.06 | +0.01 | +0.04 | +0.01 |
| P3-042 | +0.15 | +0.11 | +0.29 | +0.07 | -0.13 | +0.05 | +0.01 | +0.05 | +0.03 |
| P3-043 | +0.06 | -0.01 | +0.20 | -0.02 | -0.05 | +0.07 | +0.01 | +0.03 | +0.03 |

## Verdict against the frozen criteria

- All 12 configurations are positive out of sample (+0.025 to +0.126 R), and positive in 2022: a stable plateau, consistent with the earlier BTC finding.
- Not a candidate: every configuration fails S1 (+0.10 R), S7 (deflated Sharpe) and S8 (prop survival: 29-32% chance of breaching the 6% max drawdown within 90 days at 0.5% risk; 24-33% max drawdown over the dev period). Core configurations also fail S2 (PF) and S5 (SOL is 43-54% of the profit). S6 fails narrowly for the best core (volume x1.5 neighbour +0.025 R < half of +0.073 R).
- The volume x2.1 neighbour (+0.126 R) is NOT promoted: choosing it after seeing it would be selection.
- Losses concentrate in 2023 (choppy market), gains in 2022 and 2024-2025 (trending): a trend-regime dependence.
