# Divergence MC Systems: Winners vs Losers Study

Data: BINANCE BTCUSDT.P 15m, 2021-03 to 2026-06 (182,187 bars after dedup; one real
data hole 2026-05-06 to 2026-06-16). All indicators computed causally, signal on bar
close, entry next bar open, fees 0.08% round trip. All data pooled (exploratory mode,
per the trader's instruction). Full pipeline in `study/mcdiv/`.

## What was measured

Four trigger sets, all from the FROZEN_SPEC divergence logic (5-bar fractals on the
oscillator, confirmed pivot+2, regular divergences only, level filters at the pivot):

| System | Definition | Trades (resolved) | WR 1:1 | WR 2:1 | netR 1:1 | netR 2:1 |
|---|---|---|---|---|---|---|
| A | Confirmed WT-div + MFI-div stack, 11-bar window | 721 | 51.5% | 35.9% | -0.052 | -0.004 |
| B | Front-run stack (leg 2 pre-div entry) | 511 | 52.3% | 33.5% | -0.038 | -0.079 |
| WTdiv | Every WT regular divergence alone | 2,123 | 51.3% | 33.9% | -0.054 | -0.065 |
| MFIdiv | Every MFI regular divergence alone | 1,706 | 49.5% | 32.4% | -0.094 | -0.112 |

Stops per spec (ATR-band extreme of bars t-5..t-1, skip if < 0.6%), both-touched-in-one-bar
counted as a loss (conservative). Roughly a third of raw signals are skipped by the 0.6%
minimum-stop rule.

Baseline verdict: every system is slightly NEGATIVE net of fees on the pooled sample.
The only mildly positive cell is Variant A shorts (54.8% @1:1, +0.01R; 36.7% @2:1, +0.02R).

For each trade the study recorded WT1/WT2/MFI at the trigger bar, at the divergence leg
pivot, at the anchor (reference) pivot, and the 1h/4H WaveTrend and MFI state (last
closed bar and last completed wave extreme). The full winners-vs-losers averages, per
system and per direction, are in `out/averages_tables.md`. Per-feature significance
tests are in `out/stats_*.csv`, quintile winrates in `out/quintiles_*.csv`, robustness
checks in `out/robustness.md`.

## Headline answer: winners and losers look almost identical

Averaging the WT and MFI values across all trade triggers, anchors, and HTF waves,
winners and losers are separated by only fractions of an oscillator unit in almost
every slot. Examples (Variant A longs, 1:1): trigger WT2 -46.7 (win) vs -46.1 (loss);
WT anchor pivot -74.5 vs -75.1; MFI anchor -24.1 vs -23.4. Largest effect size found
anywhere in the study: |Cliff's delta| = 0.14 (small). Most are under 0.07 (negligible).

The formal model confirms it. A logistic regression over all 27 trigger/anchor/HTF
features, evaluated with time-ordered cross-validation, produces AUC 0.47-0.53 across
all eight system x target combinations - indistinguishable from coin-flipping. A
depth-3 decision tree finds no leaf that is both large and clean. After
Benjamini-Hochberg correction across each table, exactly ONE feature in the whole
study survives at q < 0.10: `atr_pct` for MFIdiv @2:1 (lower volatility slightly
better, d = -0.09). No WT or MFI level survives anywhere.

Conclusion: THE DEPTH OF THE WAVES DOES NOT SEPARATE WINNERS FROM LOSERS. Whether the
trigger, anchor, or HTF wave sat at -50 or -80 on WT, or 15 vs 25 on MFI, carries
essentially no information about whether the trade wins.

## The in-sample tilts (not significant after correction, but consistent)

Three directional tendencies recur across systems and targets. They are hypotheses,
not findings:

1. LESS extreme trigger WT is slightly better, not worse. In Variant B @1:1 winners
   trigger at WT2 extremity 48.7 vs losers 52.9 (p=0.007 raw, the smallest p in the
   study). The same negative sign on trigger extremity shows up in most tables. Deeper
   into overbought/oversold at entry is, if anything, mildly bad.
2. A LARGER MFI divergence delta (pivot minus anchor, i.e. a stronger money-flow
   divergence) leans toward winning (B @1:1: 5.9 vs 4.6, p=0.013 raw).
3. The last completed 4H MFI wave being on the trade's side leans toward winning
   (recurs in A, B and WTdiv tables; never significant after correction).

## The one candidate filter worth forward-testing

Combining tilts 1 and 2 on Variant B @1:1 (both thresholds fixed at pooled medians:
trigger WT2 extremity < 53.0 AND direction-normalized MFI div delta > 3.8):

| Year | n | winrate | avg netR1 |
|---|---|---|---|
| 2021 | 34 | 55.9% | +0.045 |
| 2022 | 37 | 56.8% | +0.058 |
| 2023 | 18 | 55.6% | +0.028 |
| 2024 | 27 | 66.7% | +0.254 |
| 2025 | 29 | 58.6% | +0.085 |
| 2026 | 3 | 66.7% | +0.238 |
| pooled | 148 | 58.8% | +0.096 |

Fee-adjusted breakeven at 1:1 for this subset is 54.0%; the filter clears it in every
year. Honesty caveats, in order of importance:
- The filter was CHOSEN by looking at the same data it is evaluated on (2 features
  picked from 27 after seeing p-values). This is textbook selection bias.
- n = 148 over 5.5 years is ~2.2 trades/month; the standard error on 58.8% is ~4%, so
  the true winrate could plausibly be low-50s, i.e. breakeven.
- It contradicts nothing in the baseline: unfiltered Variant B remains net negative.
Treat it as the single hypothesis this study nominates for a forward test, nothing more.

## Honesty flags

- MFI formula: the FROZEN_SPEC clone `EMA(SMA((close-open)/stdev(close,7)*150,60)-2.5,4)`
  does NOT reproduce TradingView's exported `Mny Flow` (corr ~0.96, MAE ~4.2), while the
  WT port matches to float precision. The spec formula is likely mis-remembered. Per the
  trader's explicit instruction this study uses the clone as canonical; every MFI-side
  number above would shift somewhat under the true Market Cipher money flow.
- The WT port (channel 9, average 12, wt2=SMA3) matches the export exactly, and the
  export's "Lt Blue Wave" is wt1, "Blue Wave" is wt2.
- Variant B ambiguities resolved by declared assumption: reference extreme = price
  extreme of the 5-bar window centered on the anchor pivot; anchor level filter uses the
  looser (secondary) WT tier.
- All results are in-sample on studied data. Per the audit charter: in-sample results
  can only falsify, never confirm. Here they mostly falsify - the divergence systems as
  specified show no positive expectancy and no wave-depth pattern that predicts outcomes.
