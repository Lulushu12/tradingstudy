# Pre-registration — Entry Hypothesis H3

**Committed before the test was run.** The commit adding this file contains no H3 results.
No strategy code has been executed against the H3 dataset at the time of writing.

---

## The dataset — fresh, and a different regime

`*_1h_early.csv`: **2023-03-02 13:00 → 2024-04-22 05:00 UTC**, 10,000 hourly bars per symbol,
ending exactly where the PRIOR window begins. Neither H1, H2, nor any part of the earlier
system design has ever touched it.

It also fixes the single biggest limitation of everything before it. Both existing windows
were net-down; this one is a **sustained bull market**:

| Symbol | EARLY (new) | PRIOR | MAIN |
|---|---|---|---|
| ETH | **+98.2%** | −18.2% | −29.6% |
| LINK | **+119.3%** | −12.0% | −40.7% |
| SOL | **+602.3%** | −1.7% | −52.0% |

Finding 5 of this study says no directional conclusion transfers because the sample contained
no sustained bull phase. This window is that phase.

**Known data defect:** one hourly bar is missing across all three symbols simultaneously —
`2023-03-24 13:00 UTC`, an exchange-wide outage, not a fetch error. Both other windows had
zero gaps. **Pre-registered handling:** any signal whose bar index is within **24 bars** of
the discontinuity is skipped, so no trade's indicators or entry can be contaminated. That
discards ~0.25% of bars. This rule is fixed now, before seeing any result.

## What H3 is

H1 and H2 established two things on the same 393 bars:

- The bar shape carries **real directional information**, and it runs in the **continuation**
  direction. H2's gross R was +0.141 (PRIOR) and +0.062 (MAIN); H1's, the opposite side, was
  −0.024 and −0.160.
- That information was **worth less than the stop its own structure dictated**. H2's stop sat
  just beyond the opposite extreme of a bar that closed near it — 1.1–1.3% on hourly — so
  friction consumed 12–14% of one R and turned a gross +0.141 into a net +0.019.

H3 keeps H2's direction and replaces the structural stop with one sized so friction cannot
dominate.

> A large, absorbed wick on abnormal volume marks revealed supply or demand that reasserts.
> Traded in the continuation direction with a stop wide enough that friction is a minor term,
> the signal is net profitable.

### Entry conditions — unchanged from H1 and H2

The identification function is **imported**, not reimplemented, so all three hypotheses
provably fire on an identical bar list.

| # | Condition | Value |
|---|---|---|
| 1 | Wick ≥ | **1.0 × ATR(14)** |
| 2 | Wick / bar range ≥ | **0.50** |
| 3 | Close recovered into ≥ | **0.50** of range |
| 4 | Volume z-score (100 bars) ≥ | **1.0** |

### Direction — H2's

Large **lower** wick → **SHORT**. Large **upper** wick → **LONG**.

### The stop — derived from the cost model, not from performance

This is the only substantive change, and it is derived arithmetically using **only the
already-burned MAIN and PRIOR windows**. No property of the EARLY dataset was consulted.

```
round-trip friction, market in and market out, ~20h funding
    = 2 × (0.045% taker + 0.020% slippage) + 0.010%/8h × 20h
    = 0.155% of price
target: friction ≤ 6% of one R   (the level at which this study's books
                                  were not friction-dominated)
required stop ≥ 0.155% / 0.06    = 2.58% of price
median hourly ATR, MAIN + PRIOR  = 1.018% of price
required stop in ATR             = 2.58 / 1.018 = 2.54 ATR
```

**Registered value: stop = 2.5 × ATR(14).** Not rounded up to a nicer number; 2.5 is what the
derivation gives.

### Target and time stop

- **Target: 2.0R** — unchanged from H1 and H2.
- **Time stop: 96 bars**, raised from 48. This is a *coupled consequence* of the stop change,
  not an independent knob: H3's stop is ~2.1× H2's (2.5% vs 1.2% of price), so a 2R target is
  a proportionally larger move and needs proportionally more time to resolve. Holding it at
  48 would guarantee that most trades expire before the hypothesis could be right or wrong,
  which would make this a weak test rather than a conservative one. 48 × 2.1 ≈ 100, rounded
  to 96 (four days).

Both values are fixed now.

### Execution

- **Primary:** market entry at the close of the signal bar.
- **Secondary:** the v3 resting limit (0.25 ATR better, 6-bar expiry).

## Success criteria — fixed in advance

Primary test on the **EARLY window**.

- **SUPPORTED:** mean R > 0, the **95%** block-bootstrap CI excludes zero, **and** the sign is
  positive on all three symbols individually.
- **SUGGESTIVE:** mean R > 0 and positive on all three symbols, but the 95% CI includes zero.
- **NOT SUPPORTED:** anything else.
- **UNDERPOWERED:** pooled n < 100, reported as inconclusive regardless of point estimate.

**Why 95% and not a stricter bar.** H2 was penalised to 97.5% because it re-used the same
data H1 had already spent. H3 does not: it is tested on a dataset that has never been
touched, and selecting a hypothesis on one sample does not inflate the false-positive rate on
an independent one. The extra per-symbol sign requirement is the guard against the hypothesis
family having been iterated three times.

## Not allowed after seeing results

- Changing the stop multiple, the target, the time stop, the four entry thresholds, or the
  gap-guard.
- Adding any regime, session, symbol or volatility filter.
- Reporting the limit-entry variant as the headline if the market-entry primary fails.
- Testing H4 on this dataset. **This window gets one hypothesis.**

## Standing commitment

**H3 is the last variant of this bar shape that will be tested, whatever the result.** Three
hypotheses on one idea is already at the edge of what the data can support. If H3 passes it
is a candidate for forward testing on unseen future data, not a finding and not a system. If
it fails, the conclusion is that this bar shape is not tradeable in these assets and the idea
is closed.

## Limitations acknowledged in advance

- Hourly bars hide the intrabar path; a wick is a proxy for forced flow, not evidence of it.
- The signal fires more often in high-volatility regimes and this is not corrected for.
- A bull-market window tests the direction question the other two could not, but it is still
  one regime, three correlated assets, and one exchange.
- Funding is modelled as a constant drag in both directions. In a strong bull market real
  funding is persistently positive, which would penalise the long side more than modelled
  here and flatter the short side. H3 trades both, but the asymmetry is not captured.
