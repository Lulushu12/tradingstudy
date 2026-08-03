# Pre-registration — Entry Hypothesis H2

**Committed before the test was run.** The commit adding this file contains no H2 results.

---

## Honest statement of epistemic position

H2 is **not** as clean a test as H1 was, and pretending otherwise would defeat the purpose
of writing this down.

- H1 was chosen from market-structure reasoning, before its data was touched.
- H2 is being tested **because H1 failed**, on the **same primary window**, using the **same
  bars**. That is data-dependent hypothesis selection, and it is the second look at that
  dataset.
- The mechanism below is genuinely plausible, but I articulated it *after* seeing H1's
  result. Post-hoc rationalisation is exactly the failure mode this whole exercise exists to
  avoid, and I cannot fully rule it out here.

Two things partly compensate, and neither fully:

1. **A stricter bar.** H2 must clear a **97.5% confidence interval** excluding zero, not
   95% — a Bonferroni adjustment for this being the second test on the same data.
2. **H2 is not simply "1 − H1".** Reversing direction changes which bars hit the stop before
   the target, and the stop moves to the opposite side of the signal bar, so the geometry is
   materially different. The result is new information, not an arithmetic complement.

Even if H2 clears the bar, it should be treated as a candidate for a genuinely fresh test on
data neither hypothesis has touched — not as a finding.

## The mechanism

H1 assumed a violent wick was forced flow being absorbed, and that the absorption held. It
lost, and lost *gross*, which says the bar carries information rather than being noise.

The competing reading: a large wick on abnormal volume **reveals** where size actually sits.
A flush that drops 1+ ATR and gets bought back within the hour has shown that real supply
exists below and that leveraged longs there have been cleared out. The same-bar recovery is
thin — short-covering and passive fills into a vacuum — rather than genuine accumulation.
Once revealed, that level tends to be revisited: the wick is a liquidity marker, not a floor.

Under that reading the correct trade is **with** the wick's excursion, not against it.

## H2 — liquidation-wick continuation

> The bar identification is **identical to H1**. Only the direction and the stop side change.

### Entry conditions

Unchanged from H1, at the close of bar *i*, using only data through bar *i*:

| # | Condition | Value |
|---|---|---|
| 1 | Wick size: `min(open,close) − low` (or `high − max(open,close)`) | ≥ **1.0 × ATR(14)** |
| 2 | Wick dominates the bar: `wick / (high − low)` | ≥ **0.50** |
| 3 | Close recovered: `(close − low) / (high − low)` (or mirror) | ≥ **0.50** |
| 4 | Volume z-score over 100 bars | ≥ **1.0** |

### Direction — inverted

- Large **lower** wick, close recovered up → **SHORT** (H1 went long)
- Large **upper** wick, close recovered down → **LONG** (H1 went short)

### Levels — structurally mirrored, not distance-mirrored

The stop goes where the thesis is wrong. H2's thesis is that price returns through the wick,
so it is wrong if price breaks decisively **beyond the opposite extreme** of the signal bar.

- **Stop:** for a short, `high + 0.25 × ATR`; for a long, `low − 0.25 × ATR`.
  Capped at 2.5 ATR, floored at 0.6 ATR.
- **Target:** **2.0R** (unchanged from H1).
- **Time stop:** **48 bars** (unchanged from H1).

Note this makes H2's stop *tighter* than H1's, because the signal bar closes near the
extreme the stop now sits beyond. Tighter stops mean friction consumes a larger share of one
R, and that is a known headwind going in, not an excuse afterwards.

### Execution

- **Primary:** market entry at the close of the signal bar.
- **Secondary:** the v3 resting limit (0.25 ATR better, 6-bar expiry).

## Success criteria — fixed in advance

Primary test on the **PRIOR window (2024-04-22 → 2025-06-12)**.

- **SUPPORTED:** mean R > 0 **and** the **97.5%** block-bootstrap CI excludes zero.
- **SUGGESTIVE:** mean R > 0, the 95% CI excludes zero but the 97.5% does not, **and** the
  sign is consistent across all three symbols **and** both replication datasets.
- **NOT SUPPORTED:** anything else.
- **UNDERPOWERED:** pooled n < 100, reported as inconclusive regardless of point estimate.

## Not allowed after seeing results

- Changing any threshold, the stop rule, the target, or the time stop.
- Adding a regime, session, symbol or volatility filter.
- Testing a third direction variant and reporting the best of the three.
- Quietly relaxing the 97.5% bar back to 95%.

If H2 fails, the honest conclusion is that this bar shape carries no tradeable edge in either
direction in these assets, and the next idea needs new data, not another variant.
