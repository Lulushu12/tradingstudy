# Pre-registration — 4H per-symbol cap on the multi-asset universe

**Committed before the test was run.** No 4h strategy code has been executed against any of
the 25 universe assets at the time of writing. The 4h numbers that motivated this exist only
for ETH, LINK and SOL.

---

## What is being tested and why

The Exposure Caps tab produced the strongest per-trade numbers anywhere in this study:

| Timeframe | Regime | Trades | Avg R | PF | Equity × | Max DD |
|---|---|---|---|---|---|---|
| 4h | one per symbol | 468 | +0.109 | 1.16 | 1.47× | 21.2% |
| 4h | portfolio cap 3 | 639 | +0.149 | 1.23 | 2.07× | 26.4% |

Those came from **three assets, examined through five concurrency regimes at once** — twenty
cells. This study has twice shown what a first look like that is worth: v2b showed +0.269 R
and delivered −0.178 out of sample; H3 showed +0.050 R and delivered +0.007 across 25 assets.

So this is the same test that killed H3, pointed at the last live hypothesis.

## Why the prior is better this time — a mechanical reason, not an aesthetic one

Friction has been the dominant term in *every* result in this study. It scales inversely with
stop distance, and stop distance scales with ATR, which grows with the square root of bar
duration. Measured cost as a share of one R:

| Timeframe | Typical cost / 1R |
|---|---|
| 15m | ~42% |
| 1h | ~6–7% |
| 4h | ~3–4% (expected) |

4h is structurally the least friction-dominated timeframe available. That is a reason to
expect it to do better, independent of having observed that it did. It is the same class of
argument that made H1 the best-founded of the three wick hypotheses.

I still put this at roughly **25–30%**. The session is 0-for-3 on first looks.

## The configuration — fixed now

**One position per symbol at a time.** Chosen over the portfolio cap of 3 deliberately, even
though portfolio-3 scored higher (+0.149 vs +0.109). Portfolio-3 was the best of five regimes
tested on three assets; per-symbol is the simpler rule with one fewer free parameter, and is
therefore less likely to be the cell that won by chance. **Picking the higher-scoring variant
here would be exactly the error this registration exists to prevent.**

- Signals: the selective book, conviction ≥ 6.0, `RANGE_FADE` disabled (deleted earlier after
  out-of-sample confirmation).
- Entry: market at the close of the signal bar.
- Levels: unchanged v1 geometry — ATR stop pushed beyond the last confirmed swing pivot,
  per-setup R target, per-setup time stop.
- Concurrency: at most one open position per symbol. No portfolio-level cap in the primary.
- Sizing for the account simulation: 1% of equity at entry, equity updating on close.

Nothing above is re-tuned. All of it is imported from the existing modules.

## The universe

The same 25 assets used for H3-Multi, selected mechanically and listed in
`PREREGISTRATION_H3M.md`. **None has ever been run on 4h data.** ETH, LINK and SOL are
excluded from the primary and reported separately as context, since the 4h configuration was
chosen by looking at them.

Span is roughly 4.6 years per asset (10,000 4h bars), covering the 2022 bear, the 2023
recovery, the 2024 bull and the 2025–26 decline. Expected sample: on the order of
**3,000–4,000 trades**.

## Statistics

Cross-sectional block bootstrap, resampling **calendar-week blocks spanning the whole
universe**, 8,000 resamples — identical to H3-Multi. Crypto majors are heavily correlated;
per-trade resampling would overstate significance badly. The naive interval will be reported
alongside solely to show the size of that overstatement, and is **not** the criterion.

## Success criteria — fixed in advance

- **SUPPORTED:** pooled mean R > 0, the **95%** cross-sectional CI excludes zero, **and**
  ≥ 60% of individual assets positive.
- **SUGGESTIVE:** pooled mean R > 0 and ≥ 60% of assets positive, but the CI includes zero.
- **NOT SUPPORTED:** anything else.
- **UNDERPOWERED:** pooled n < 1,500.

## Not allowed after seeing results

- Switching to the portfolio-cap-3 regime, or any other cap, because it scores better.
- Changing the conviction threshold, the levels, or the timeframe.
- Dropping assets that perform badly.
- Substituting the naive bootstrap for the cross-sectional one.
- Reporting the account-simulation figures as the headline if the per-trade primary fails.

## What a pass would mean

That the effect survives on 25 assets it was never selected from, across 4.6 years and four
regimes, under a bootstrap respecting cross-asset correlation. That would be the first
positive result in this entire study, and it would still require forward testing before
deployment — one exchange, spot candles proxying perp execution, funding as a constant, no
order-book depth.
