# Phase 1 diagnostic: what destroyed the gross edge

Phase 1 returns -0.0005 R at zero cost against Gate 0's +0.1196 R. Friction is not the cause. Each row below applies one more tightening, so the drop can be attributed.

| step | configuration | signals | win rate | gross exp (R) |
|---|---|---|---|---|
| 1 | Gate 0 baseline: pooled edge on filtered set, both-hits excluded | 797 | 65.5% | **+0.0298** |
| 2 | + threshold population = all bars, not filtered | 367 | 61.9% | **-0.0240** |
| 3 | + CAUSAL expanding 10th percentile | 326 | 61.0% | **-0.0365** |
| 4 | + both-touched resolves to the stop | 328 | 60.7% | **-0.0423** |
| 5 | + one position at a time (frozen spec, zero cost) | 220 | 63.2% | **-0.0005** |
| 6 | + costs 0.12% round trip (headline Phase 1) | 220 | 63.2% | **-0.0497** |

## Threshold comparison

- Pooled 10th percentile over the filtered valid set: **0.0770**
- Pooled 10th percentile over all bars: **0.0378**
- Causal expanding threshold: mean **0.0392**, range 0.0371 to 0.0463
- Signals selected: pooled-filtered 2347, pooled-all 1197, causal 1061

## Position-cap selection effect

Of the qualifying signals, **220 were taken and 254 were skipped** because a position was already open. If the taken subset performs materially worse than the full qualifying set, the cap is not merely discarding signals, it is selecting the bad ones.

- All qualifying signals (step 4): 328 signals, -0.0423 R
- Taken subset under the cap (step 5): 220 trades, -0.0005 R
- Difference attributable to the cap: **+0.0418 R**
