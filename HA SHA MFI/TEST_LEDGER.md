# TEST LEDGER, XRP HA/SHA/MFI STUDY

Every executed run on this data, counted. Spec frozen in
FROZEN_SPEC_XRPHA.md before run 1.

| # | date | phase | runs | verdict |
|---|------|-------|------|---------|
| 1 | 2026-07-09 | Gate 0 (integrity + port validation, no P&L) | 1 | PASS: HA and SHA to machine epsilon, Mny Flow bounded 1.9e-6 abs, zero sign flips; 63 bars missing of 228,125; column names inverted (documented) |
| 2 | 2026-07-09 | Sandbox (2020-01-06 through 2023-12-31, frozen rule, full cost stack) | 1 | DEAD: pooled net expectancy -0.1391R (n=2245), 7/8 half-year windows negative, breakeven slippage below 0bp. Pass bar not met; K1/K2/K3/K4 all KILL. |
| 3 | 2026-07-09 | Sandbox, CANDIDATE 2 convergence rule (2020-01-06 through 2023-12-31, full cost stack) | 1 | DEAD: pooled net expectancy -0.1340R (n=2572, path_old n=1757 exp -0.1056R, path_new n=815 exp -0.1951R), 7/8 half-year windows negative, breakeven slippage below 0bp. Pass bar not met; K1/K2/K3/K4 all KILL. Sanity check (d): 13 candidate 1 entries missing from candidate 2's entry set, all explained by an earlier candidate-2 new-path completion consuming the window first; 0 unexplained. |
