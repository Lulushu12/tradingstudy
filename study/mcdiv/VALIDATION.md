# Indicator Port Validation

Validates `mc_indicators.py` (WaveTrend, MFI-clone) against the TradingView-exported columns (`exp_wta`, `exp_wtb`, `exp_mfi`) on the cleaned 15m and 4h parquet files.

## 15m timeframe

Rows: 182187. Warmup skipped: first 1000 bars.

### Column mapping (wt1/wt2 vs exp_wta/exp_wtb)

- Combo A (wt1->exp_wta, wt2->exp_wtb) summed MAE: 0.034378
- Combo B (wt1->exp_wtb, wt2->exp_wta) summed MAE: 15.051276
- **Winning mapping: wt1 -> exp_wta, wt2 -> exp_wtb**

### Error stats, all bars after warmup

- wt1 vs exp_wta: n=180809, MAE=0.017594, median AE=0.000000, p99 AE=0.000000, max AE=92.925507, corr=0.999800
- wt2 vs exp_wtb: n=180781, MAE=0.016784, median AE=0.000000, p99 AE=0.000000, max AE=90.744784, corr=0.999798
- mfi (ddof=0) vs exp_mfi: n=180249, MAE=4.236366, median AE=3.592046, p99 AE=13.361288, max AE=29.088483, corr=0.960927
- mfi (ddof=1) vs exp_mfi: n=180249, MAE=4.268910, median AE=3.632969, p99 AE=13.444789, max AE=27.213942, corr=0.960927

### Decomposing tail error: real gaps vs file-boundary re-warm artifacts

- Timestamp gaps (>3600s): 1 found (see prep_data.py gap report). 100 bars flagged after each.
- 15m export file boundaries (excluding the earliest file, already inside warmup): 16 boundaries found at ['2021-07-01 00:00:00+00:00', '2021-11-01 00:00:00+00:00', '2022-03-01 00:00:00+00:00', '2022-07-01 00:00:00+00:00', '2022-11-01 00:00:00+00:00', '2023-03-01 00:00:00+00:00', '2023-07-01 00:00:00+00:00', '2023-11-01 00:00:00+00:00', '2024-03-01 00:00:00+00:00', '2024-07-01 00:00:00+00:00', '2024-11-01 00:00:00+00:00', '2025-03-01 00:00:00+00:00', '2025-07-01 00:00:00+00:00', '2025-11-01 00:00:00+00:00', '2026-01-01 00:00:00+00:00', '2026-06-16 03:45:00+00:00']. 100 bars flagged after each start -- each new export file's indicator state is recomputed from that file's own (short) chart history, so its first ~dozens of bars have not fully converged even though the underlying timestamps are contiguous (no time gap).
- Total bars flagged as gap/boundary-adjacent (post-warmup): 1600 of 181187

| series | subset | n | MAE | median AE | p99 AE | max AE | corr |
|---|---|---|---|---|---|---|---|
| wt2 | all | 180781 | 0.016784 | 0.000000 | 0.000000 | 90.744784 | 0.999798 |
| wt2 | clean (excl gap/boundary) | 179587 | 0.000000 | 0.000000 | 0.000000 | 0.000216 | 1.000000 |
| wt2 | gap/boundary-adjacent only | 1194 | 2.541220 | 0.013699 | 75.484699 | 90.744784 | 0.969097 |
| mfi (ddof=0) | all | 180249 | 4.236366 | 3.592046 | 13.361288 | 29.088483 | 0.960927 |
| mfi (ddof=0) | clean (excl gap/boundary) | 179587 | 4.233522 | 3.593528 | 13.331665 | 22.454623 | 0.961200 |
| mfi (ddof=0) | gap/boundary-adjacent only | 662 | 5.007856 | 3.042320 | 26.475521 | 29.088483 | 0.860673 |

**Interpretation**: WT (wt1/wt2) matches the export almost exactly in clean regions (MAE 4.53e-08, correlation 1.000000) -- essentially floating point-level agreement. The visible tail error in the unconditioned 'all bars' stats is concentrated almost entirely in the gap/boundary-adjacent bars, where TradingView's own export re-warms its EMA state from a short chart history at each new export file's start (or after the one large 15m data gap). This is a data-hygiene artifact of the source exports, not a port bug: the port's continuous, single-pass computation is *more* correct across these boundaries than what any individual TradingView export shows at its own start.

### MFI mismatch investigation

Base MFI MAE (4.236 for ddof=0, 4.269 for ddof=1) is far above the 0.5 threshold, and unlike WT this persists even in the gap/boundary-clean subset, so it is investigated below.

| variant | n | MAE | median AE | p99 AE | max AE | corr |
|---|---|---|---|---|---|---|
| stdev ddof=0 (population, shipped) | 179587 | 4.233522 | 3.593528 | 13.331665 | 22.454623 | 0.961200 |
| stdev ddof=1 (sample) | 179587 | 4.266714 | 3.635215 | 13.400815 | 23.806927 | 0.961200 |
| outer EMA alpha=1/4 instead of span=4 | 179587 | 4.468881 | 3.801351 | 14.035564 | 22.485349 | 0.954917 |
| best of close-open/stdev(close) grid search (stdev_len=7, sma_len=60, ema_len=4, ddof=0) | 179587 | 4.233522 | 3.593528 | 13.331665 | 22.454623 | 0.961200 |
| exploratory OFF-SPEC: (hlc3-hlc3[1])/stdev(hlc3,7)*150 numerator | 179587 | 3.901025 | 3.395586 | 11.993350 | 19.194994 | 0.977464 |
| exploratory OFF-SPEC: classic (close-open)/(high-low)*150 SMA60-2.5 EMA4 | 179587 | 8.617680 | 7.320287 | 27.455415 | 43.062246 | 0.856600 |

WT with SMA(wt1,4) instead of SMA(wt1,3) (clean subset, vs exp_wtb): n=179587, MAE=3.497121, median AE=2.989689, p99 AE=10.733899, max AE=17.351537, corr=0.995023  -- confirms SMA period 3 (shipped, MAE 4.53e-08) is correct; period 4 is dramatically worse.

**ddof winner (15m, clean subset): ddof=0** (ddof=0 MAE=4.233522 vs ddof=1 MAE=4.266714). The difference between ddof choices is small relative to the total error (<0.05 MAE) -- it is not the source of the mismatch.

**Conclusion on MFI**: none of the tested variants (ddof choice, EMA span-vs-alpha convention, stdev/SMA/EMA window grid search, or even off-spec numerator substitutions) bring MAE below roughly 3.5-4.3, while WT matches to floating-point precision under the identical methodology. Correlation stays high (~0.96-0.98), so the *shape* of the oscillator is right, but the exact FROZEN_SPEC MFI formula (`EMA(SMA((close-open)/stdev(close,7)*150,60)-2.5,4)`) does not reproduce TradingView's `Mny Flow` plot to the precision WT achieves. FROZEN_SPEC was 'written from memory... before any data exploration' -- this is consistent with the MFI formula being mis-remembered (most likely in the exact numerator/denominator terms) rather than a porting bug. **This should be flagged for spec review; it was not silently accepted.** The shipped `mc_indicators.mfi_clone` still implements the FROZEN_SPEC formula exactly (with ddof=0, the marginally better and Pine-consistent choice) since no better variant staying faithful to the spec was found.

## 4h timeframe

Rows: 11987. Warmup skipped: first 1000 bars. Single continuous export file (no dedup, no gaps) -- a clean check unaffected by the file-boundary re-warm artifact seen in 15m.

### Column mapping

- Combo A (wt1->exp_wta, wt2->exp_wtb) summed MAE: 3.878385e-12
- Combo B (wt1->exp_wtb, wt2->exp_wta) summed MAE: 1.456019e+01
- **Winning mapping: wt1 -> exp_wta, wt2 -> exp_wtb** (same as 15m: CONSISTENT)

### Error stats, all bars after warmup (no gap/boundary exclusion needed)

- wt1 vs exp_wta: n=10987, MAE=0.000000, median AE=0.000000, p99 AE=0.000000, max AE=0.000000, corr=1.000000
- wt2 vs exp_wtb: n=10987, MAE=0.000000, median AE=0.000000, p99 AE=0.000000, max AE=0.000000, corr=1.000000
- mfi (ddof=0) vs exp_mfi: n=10987, MAE=4.270710, median AE=3.560441, p99 AE=13.228553, max AE=18.509358, corr=0.965367
- mfi (ddof=1) vs exp_mfi: n=10987, MAE=4.233945, median AE=3.579721, p99 AE=13.420918, max AE=19.429704, corr=0.965367

**ddof winner (4h): ddof=1** (ddof=0 MAE=4.270710 vs ddof=1 MAE=4.233945); again a near-tie, confirming ddof is not the driver of the MFI mismatch.

**Cross-timeframe confirmation**: on the 4h file (a single continuous export, no dedup/gap issues at all), WT still matches to 1.93e-12 MAE (essentially float precision, corr 1.0000000000) while MFI is still off by MAE~4.27 (corr ~0.965). This rules out the 15m dedup/segmentation process as the cause of the MFI mismatch -- it is a property of the formula itself, reproduced independently on a completely different, artifact-free file.

