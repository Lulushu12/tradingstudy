# TEST LEDGER, RESEARCH CYCLE 1

Every executed test on any data, counted. Rules frozen in
RESEARCH_PROTOCOL.md before test 1.

| # | date | candidate | segment | runs | verdict |
|---|------|-----------|---------|------|---------|
| 1 | 2026-07-09 | C1 funding extreme fade | sandbox | 1 | SURVIVES (+0.196R, n=130, 5/6 windows) |
| 2 | 2026-07-09 | C2 OI flush reversion | sandbox | 1 | DEAD (-0.211R, n=26) |
| 3 | 2026-07-09 | C3 premium extreme fade | sandbox | 1 | DEAD (+0.015R, n=404) |
| 4 | 2026-07-09 | C4 weekend move fade | sandbox | 1 | DEAD (+0.075R, n=89) |
| 5 | 2026-07-09 | C5 compression breakout | sandbox | 1 | DEAD (-0.033R, n=21) |

| 6 | 2026-07-09 | C1 funding extreme fade | validation (one-shot) | 1 | DEAD (-0.071R, n=110, 0/5 windows nonneg) |

Validation runs used: 1 of 1 permitted. CYCLE 1 CLOSED: all five candidates
dead. Per protocol this verdict stands; no re-thresholding, no reruns.
