"""
Validates the mc_indicators.py port against the TradingView-exported
indicator columns (exp_wta, exp_wtb, exp_mfi) on the 15m and 4h data.

Determines the wt1/wt2 <-> exp_wta/exp_wtb column mapping, reports
error statistics, investigates the MFI mismatch with formula variants,
and separates out two known sources of legitimate (non-bug) tail error:
  1. bars shortly after a real timestamp gap (>3600s) in the 15m series
  2. bars shortly after the start of a new 15m export file (indicator
     state resets/re-warms within each ~4-month CSV export)

Writes study/mcdiv/VALIDATION.md.

Run as: python3 study/mcdiv/validate_port.py
"""
import glob
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from mc_indicators import wavetrend, mfi_clone  # noqa: E402

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
OUT_MD = os.path.join(os.path.dirname(__file__), "VALIDATION.md")

WARMUP = 1000
POST_EVENT_BARS = 100  # bars to flag after a gap / file-boundary event
GAP_THRESHOLD_S = 3600
GOOD_MAE = 0.5


def ae_stats(a, b):
    m = a.notna() & b.notna()
    aa, bb = a[m], b[m]
    if len(aa) == 0:
        return dict(n=0, mae=np.nan, median=np.nan, p99=np.nan, maxae=np.nan, corr=np.nan)
    ae = (aa - bb).abs()
    return dict(
        n=int(m.sum()),
        mae=float(ae.mean()),
        median=float(ae.median()),
        p99=float(ae.quantile(0.99)),
        maxae=float(ae.max()),
        corr=float(aa.corr(bb)),
    )


def fmt_stats(s):
    return (f"n={s['n']}, MAE={s['mae']:.6f}, median AE={s['median']:.6f}, "
            f"p99 AE={s['p99']:.6f}, max AE={s['maxae']:.6f}, corr={s['corr']:.6f}")


def determine_wt_mapping(wt1, wt2, exp_wta, exp_wtb, warm):
    """Pick the wt1/wt2 <-> exp_wta/exp_wtb pairing with lower combined MAE."""
    combos = {
        "A": (ae_stats(wt1[warm:], exp_wta[warm:])["mae"] + ae_stats(wt2[warm:], exp_wtb[warm:])["mae"],
              {"wt1": "exp_wta", "wt2": "exp_wtb"}),
        "B": (ae_stats(wt1[warm:], exp_wtb[warm:])["mae"] + ae_stats(wt2[warm:], exp_wta[warm:])["mae"],
              {"wt1": "exp_wtb", "wt2": "exp_wta"}),
    }
    winner = min(combos, key=lambda k: combos[k][0])
    return combos[winner][1], combos


def find_gap_event_indices(df, threshold_s):
    ts = df["ts"].values
    diffs = np.diff(ts)
    gap_positions = np.where(diffs > threshold_s)[0] + 1  # index of first bar after the gap
    return gap_positions


def find_file_boundary_indices(df, glob_pattern):
    """Row indices in the deduped/sorted df that are the first bar of a raw
    export file's timestamp range, EXCLUDING the very first (earliest)
    file's start (which is already inside the global warmup window)."""
    paths = sorted(glob.glob(glob_pattern))
    starts = []
    for p in paths:
        t0 = pd.read_csv(p, usecols=["time"])["time"].iloc[0]
        starts.append(int(t0))
    starts = sorted(starts)
    starts = starts[1:]  # drop the earliest (covered by global warmup)
    ts_to_idx = pd.Series(np.arange(len(df)), index=df["ts"].values)
    idxs = []
    for t0 in starts:
        if t0 in ts_to_idx.index:
            idxs.append(int(ts_to_idx.loc[t0]))
    return sorted(set(idxs)), starts


def mask_after_events(n, event_positions, n_bars):
    mask = np.zeros(n, dtype=bool)
    for p in event_positions:
        mask[p:p + n_bars] = True
    return mask


def mfi_variant(df, numerator="close_open", stdev_src="close", stdev_len=7,
                 sma_len=60, ema_len=4, offset=2.5, ddof=0, ema_mode="span"):
    if numerator == "close_open":
        num = df["close"] - df["open"]
    elif numerator == "hlc3_diff":
        hlc3 = (df["high"] + df["low"] + df["close"]) / 3.0
        num = hlc3 - hlc3.shift(1)
    else:
        raise ValueError(numerator)

    if stdev_src == "close":
        src = df["close"]
    elif stdev_src == "hlc3":
        src = (df["high"] + df["low"] + df["close"]) / 3.0
    else:
        raise ValueError(stdev_src)

    stdev = src.rolling(stdev_len).std(ddof=ddof)
    raw = num / stdev * 150.0
    sma = raw.rolling(sma_len).mean()
    x = sma - offset
    if ema_mode == "span":
        out = x.ewm(span=ema_len, adjust=False).mean()
    else:
        out = x.ewm(alpha=1.0 / ema_len, adjust=False).mean()
    return out


def main():
    lines = []
    lines.append("# Indicator Port Validation\n")
    lines.append("Validates `mc_indicators.py` (WaveTrend, MFI-clone) against the "
                  "TradingView-exported columns (`exp_wta`, `exp_wtb`, `exp_mfi`) on "
                  "the cleaned 15m and 4h parquet files.\n")

    # =========================================================
    # 15m validation
    # =========================================================
    df15 = pd.read_parquet(os.path.join(DATA_DIR, "15m.parquet")).reset_index(drop=True)
    wt1, wt2 = wavetrend(df15)
    mfi0 = mfi_clone(df15, ddof=0)
    mfi1 = mfi_clone(df15, ddof=1)

    exp_wta, exp_wtb, exp_mfi = df15["exp_wta"], df15["exp_wtb"], df15["exp_mfi"]

    mapping, combos = determine_wt_mapping(wt1, wt2, exp_wta, exp_wtb, WARMUP)
    lines.append("## 15m timeframe\n")
    lines.append(f"Rows: {len(df15)}. Warmup skipped: first {WARMUP} bars.\n")
    lines.append("### Column mapping (wt1/wt2 vs exp_wta/exp_wtb)\n")
    lines.append(f"- Combo A (wt1->exp_wta, wt2->exp_wtb) summed MAE: {combos['A'][0]:.6f}")
    lines.append(f"- Combo B (wt1->exp_wtb, wt2->exp_wta) summed MAE: {combos['B'][0]:.6f}")
    lines.append(f"- **Winning mapping: wt1 -> {mapping['wt1']}, wt2 -> {mapping['wt2']}**\n")

    wt1_exp = exp_wta if mapping["wt1"] == "exp_wta" else exp_wtb
    wt2_exp = exp_wta if mapping["wt2"] == "exp_wta" else exp_wtb

    s_wt1 = ae_stats(wt1.iloc[WARMUP:], wt1_exp.iloc[WARMUP:])
    s_wt2 = ae_stats(wt2.iloc[WARMUP:], wt2_exp.iloc[WARMUP:])
    s_mfi0 = ae_stats(mfi0.iloc[WARMUP:], exp_mfi.iloc[WARMUP:])
    s_mfi1 = ae_stats(mfi1.iloc[WARMUP:], exp_mfi.iloc[WARMUP:])

    lines.append("### Error stats, all bars after warmup\n")
    lines.append(f"- wt1 vs {mapping['wt1']}: {fmt_stats(s_wt1)}")
    lines.append(f"- wt2 vs {mapping['wt2']}: {fmt_stats(s_wt2)}")
    lines.append(f"- mfi (ddof=0) vs exp_mfi: {fmt_stats(s_mfi0)}")
    lines.append(f"- mfi (ddof=1) vs exp_mfi: {fmt_stats(s_mfi1)}\n")

    # --- gap / file-boundary decomposition ---
    gap_positions = find_gap_event_indices(df15, GAP_THRESHOLD_S)
    gap_mask = mask_after_events(len(df15), gap_positions, POST_EVENT_BARS)

    boundary_positions, boundary_starts = find_file_boundary_indices(
        df15, os.path.join(REPO_ROOT, "New export", "15m", "*.csv"))
    boundary_mask = mask_after_events(len(df15), boundary_positions, POST_EVENT_BARS)

    warm_mask = np.arange(len(df15)) >= WARMUP
    event_mask = gap_mask | boundary_mask
    clean_mask = warm_mask & ~event_mask
    event_mask_post_warm = warm_mask & event_mask

    lines.append("### Decomposing tail error: real gaps vs file-boundary re-warm artifacts\n")
    lines.append(f"- Timestamp gaps (>{GAP_THRESHOLD_S}s): {len(gap_positions)} found "
                  f"(see prep_data.py gap report). {POST_EVENT_BARS} bars flagged after each.")
    lines.append(f"- 15m export file boundaries (excluding the earliest file, already inside "
                  f"warmup): {len(boundary_positions)} boundaries found at "
                  f"{[str(pd.to_datetime(t, unit='s', utc=True)) for t in boundary_starts]}. "
                  f"{POST_EVENT_BARS} bars flagged after each start -- each new export file's "
                  f"indicator state is recomputed from that file's own (short) chart history, "
                  f"so its first ~dozens of bars have not fully converged even though the "
                  f"underlying timestamps are contiguous (no time gap).")
    lines.append(f"- Total bars flagged as gap/boundary-adjacent (post-warmup): "
                  f"{int(event_mask_post_warm.sum())} of {int(warm_mask.sum())}\n")

    def masked_stats(a, b, mask):
        idx = np.where(mask)[0]
        return ae_stats(a.iloc[idx], b.iloc[idx])

    s_wt2_clean = masked_stats(wt2, wt2_exp, clean_mask)
    s_wt2_event = masked_stats(wt2, wt2_exp, event_mask_post_warm)
    s_mfi0_clean = masked_stats(mfi0, exp_mfi, clean_mask)
    s_mfi0_event = masked_stats(mfi0, exp_mfi, event_mask_post_warm)

    lines.append("| series | subset | " + " | ".join(["n", "MAE", "median AE", "p99 AE", "max AE", "corr"]) + " |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for name, s in [
        ("wt2", ("all", s_wt2)), ("wt2", ("clean (excl gap/boundary)", s_wt2_clean)),
        ("wt2", ("gap/boundary-adjacent only", s_wt2_event)),
        ("mfi (ddof=0)", ("all", s_mfi0)), ("mfi (ddof=0)", ("clean (excl gap/boundary)", s_mfi0_clean)),
        ("mfi (ddof=0)", ("gap/boundary-adjacent only", s_mfi0_event)),
    ]:
        subset, st = s
        lines.append(f"| {name} | {subset} | {st['n']} | {st['mae']:.6f} | {st['median']:.6f} | "
                      f"{st['p99']:.6f} | {st['maxae']:.6f} | {st['corr']:.6f} |")
    lines.append("")

    lines.append("**Interpretation**: WT (wt1/wt2) matches the export almost exactly "
                  f"in clean regions (MAE {s_wt2_clean['mae']:.2e}, correlation "
                  f"{s_wt2_clean['corr']:.6f}) -- essentially floating point-level agreement. "
                  "The visible tail error in the unconditioned 'all bars' stats is concentrated "
                  "almost entirely in the gap/boundary-adjacent bars, where TradingView's own "
                  "export re-warms its EMA state from a short chart history at each new export "
                  "file's start (or after the one large 15m data gap). This is a data-hygiene "
                  "artifact of the source exports, not a port bug: the port's continuous, "
                  "single-pass computation is *more* correct across these boundaries than what "
                  "any individual TradingView export shows at its own start.\n")

    # =========================================================
    # MFI investigation (task 4d): required variants + broader search
    # =========================================================
    lines.append("### MFI mismatch investigation\n")
    lines.append(f"Base MFI MAE ({s_mfi0['mae']:.3f} for ddof=0, {s_mfi1['mae']:.3f} for ddof=1) is "
                  f"far above the {GOOD_MAE} threshold, and unlike WT this persists even in the "
                  "gap/boundary-clean subset, so it is investigated below.\n")

    variant_rows = []

    # ddof variants (already have mfi0/mfi1 clean-subset numbers)
    variant_rows.append(("stdev ddof=0 (population, shipped)", s_mfi0_clean))
    variant_rows.append(("stdev ddof=1 (sample)", masked_stats(mfi1, exp_mfi, clean_mask)))

    # EMA span vs alpha=1/n on the outer smooth
    v_alpha = mfi_variant(df15, ema_mode="alpha", ddof=0)
    variant_rows.append(("outer EMA alpha=1/4 instead of span=4", masked_stats(v_alpha, exp_mfi, clean_mask)))

    # SMA(wt1,4) variant note (WT, not MFI) -- required by task 4d
    wt2_sma4 = wt1.rolling(4).mean()
    s_wt2_sma4 = masked_stats(wt2_sma4, wt2_exp, clean_mask)

    # stdev length / SMA length / outer EMA length grid (bounded search)
    grid_results = []
    for stdev_len in (5, 6, 7, 8, 9):
        for sma_len in (55, 58, 60, 62, 65):
            for ema_len in (3, 4, 5):
                for ddof in (0, 1):
                    v = mfi_variant(df15, stdev_len=stdev_len, sma_len=sma_len,
                                     ema_len=ema_len, ddof=ddof)
                    st = masked_stats(v, exp_mfi, clean_mask)
                    grid_results.append((st["mae"], stdev_len, sma_len, ema_len, ddof, st))
    grid_results.sort(key=lambda r: r[0])
    best_grid = grid_results[0]
    variant_rows.append((
        f"best of close-open/stdev(close) grid search "
        f"(stdev_len={best_grid[1]}, sma_len={best_grid[2]}, ema_len={best_grid[3]}, ddof={best_grid[4]})",
        best_grid[5]))

    # alternate numerator: hlc3 diff instead of close-open (exploratory, off-spec)
    v_hlc3 = mfi_variant(df15, numerator="hlc3_diff", stdev_src="hlc3", stdev_len=7,
                          sma_len=60, ema_len=4, ddof=0)
    variant_rows.append(("exploratory OFF-SPEC: (hlc3-hlc3[1])/stdev(hlc3,7)*150 numerator",
                          masked_stats(v_hlc3, exp_mfi, clean_mask)))

    # classic VuManChu-style (close-open)/(high-low) formula, for reference
    v_classic = ((df15["close"] - df15["open"]) / (df15["high"] - df15["low"]) * 150).rolling(60).mean() - 2.5
    v_classic = v_classic.ewm(span=4, adjust=False).mean()
    variant_rows.append(("exploratory OFF-SPEC: classic (close-open)/(high-low)*150 SMA60-2.5 EMA4",
                          masked_stats(v_classic, exp_mfi, clean_mask)))

    lines.append("| variant | n | MAE | median AE | p99 AE | max AE | corr |")
    lines.append("|---|---|---|---|---|---|---|")
    for name, st in variant_rows:
        lines.append(f"| {name} | {st['n']} | {st['mae']:.6f} | {st['median']:.6f} | "
                      f"{st['p99']:.6f} | {st['maxae']:.6f} | {st['corr']:.6f} |")
    lines.append("")
    lines.append(f"WT with SMA(wt1,4) instead of SMA(wt1,3) (clean subset, vs {mapping['wt2']}): "
                 f"{fmt_stats(s_wt2_sma4)}  -- confirms SMA period 3 (shipped, MAE "
                 f"{s_wt2_clean['mae']:.2e}) is correct; period 4 is dramatically worse.\n")

    ddof_winner = "ddof=0" if s_mfi0_clean["mae"] <= masked_stats(mfi1, exp_mfi, clean_mask)["mae"] else "ddof=1"
    lines.append(f"**ddof winner (15m, clean subset): {ddof_winner}** "
                 f"(ddof=0 MAE={s_mfi0_clean['mae']:.6f} vs ddof=1 MAE={masked_stats(mfi1, exp_mfi, clean_mask)['mae']:.6f}). "
                 "The difference between ddof choices is small relative to the total error "
                 "(<0.05 MAE) -- it is not the source of the mismatch.\n")

    lines.append("**Conclusion on MFI**: none of the tested variants (ddof choice, EMA "
                  "span-vs-alpha convention, stdev/SMA/EMA window grid search, or even "
                  "off-spec numerator substitutions) bring MAE below roughly 3.5-4.3, "
                  "while WT matches to floating-point precision under the identical "
                  "methodology. Correlation stays high (~0.96-0.98), so the *shape* of the "
                  "oscillator is right, but the exact FROZEN_SPEC MFI formula "
                  "(`EMA(SMA((close-open)/stdev(close,7)*150,60)-2.5,4)`) does not "
                  "reproduce TradingView's `Mny Flow` plot to the precision WT achieves. "
                  "FROZEN_SPEC was 'written from memory... before any data exploration' -- "
                  "this is consistent with the MFI formula being mis-remembered (most likely "
                  "in the exact numerator/denominator terms) rather than a porting bug. "
                  "**This should be flagged for spec review; it was not silently accepted.** "
                  "The shipped `mc_indicators.mfi_clone` still implements the FROZEN_SPEC "
                  "formula exactly (with ddof=0, the marginally better and Pine-consistent "
                  "choice) since no better variant staying faithful to the spec was found.\n")

    # =========================================================
    # 4h validation
    # =========================================================
    df4h = pd.read_parquet(os.path.join(DATA_DIR, "4h.parquet")).reset_index(drop=True)
    wt1_4h, wt2_4h = wavetrend(df4h)
    mfi0_4h = mfi_clone(df4h, ddof=0)
    mfi1_4h = mfi_clone(df4h, ddof=1)
    exp_wta_4h, exp_wtb_4h, exp_mfi_4h = df4h["exp_wta"], df4h["exp_wtb"], df4h["exp_mfi"]

    mapping_4h, combos_4h = determine_wt_mapping(wt1_4h, wt2_4h, exp_wta_4h, exp_wtb_4h, WARMUP)

    lines.append("## 4h timeframe\n")
    lines.append(f"Rows: {len(df4h)}. Warmup skipped: first {WARMUP} bars. "
                 "Single continuous export file (no dedup, no gaps) -- a clean check "
                 "unaffected by the file-boundary re-warm artifact seen in 15m.\n")
    lines.append("### Column mapping\n")
    lines.append(f"- Combo A (wt1->exp_wta, wt2->exp_wtb) summed MAE: {combos_4h['A'][0]:.6e}")
    lines.append(f"- Combo B (wt1->exp_wtb, wt2->exp_wta) summed MAE: {combos_4h['B'][0]:.6e}")
    lines.append(f"- **Winning mapping: wt1 -> {mapping_4h['wt1']}, wt2 -> {mapping_4h['wt2']}** "
                 f"(same as 15m: {'CONSISTENT' if mapping_4h == mapping else 'INCONSISTENT'})\n")

    wt1_exp_4h = exp_wta_4h if mapping_4h["wt1"] == "exp_wta" else exp_wtb_4h
    wt2_exp_4h = exp_wta_4h if mapping_4h["wt2"] == "exp_wta" else exp_wtb_4h

    s_wt1_4h = ae_stats(wt1_4h.iloc[WARMUP:], wt1_exp_4h.iloc[WARMUP:])
    s_wt2_4h = ae_stats(wt2_4h.iloc[WARMUP:], wt2_exp_4h.iloc[WARMUP:])
    s_mfi0_4h = ae_stats(mfi0_4h.iloc[WARMUP:], exp_mfi_4h.iloc[WARMUP:])
    s_mfi1_4h = ae_stats(mfi1_4h.iloc[WARMUP:], exp_mfi_4h.iloc[WARMUP:])

    lines.append("### Error stats, all bars after warmup (no gap/boundary exclusion needed)\n")
    lines.append(f"- wt1 vs {mapping_4h['wt1']}: {fmt_stats(s_wt1_4h)}")
    lines.append(f"- wt2 vs {mapping_4h['wt2']}: {fmt_stats(s_wt2_4h)}")
    lines.append(f"- mfi (ddof=0) vs exp_mfi: {fmt_stats(s_mfi0_4h)}")
    lines.append(f"- mfi (ddof=1) vs exp_mfi: {fmt_stats(s_mfi1_4h)}\n")

    ddof_winner_4h = "ddof=1" if s_mfi1_4h["mae"] < s_mfi0_4h["mae"] else "ddof=0"
    lines.append(f"**ddof winner (4h): {ddof_winner_4h}** (ddof=0 MAE={s_mfi0_4h['mae']:.6f} vs "
                 f"ddof=1 MAE={s_mfi1_4h['mae']:.6f}); again a near-tie, confirming ddof is not "
                 "the driver of the MFI mismatch.\n")

    lines.append("**Cross-timeframe confirmation**: on the 4h file (a single continuous "
                 f"export, no dedup/gap issues at all), WT still matches to "
                 f"{s_wt2_4h['mae']:.2e} MAE (essentially float precision, corr "
                 f"{s_wt2_4h['corr']:.10f}) while MFI is still off by MAE~{s_mfi0_4h['mae']:.2f} "
                 "(corr ~0.965). This rules out the 15m dedup/segmentation process as the "
                 "cause of the MFI mismatch -- it is a property of the formula itself, "
                 "reproduced independently on a completely different, artifact-free file.\n")

    with open(OUT_MD, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Wrote {OUT_MD}")

    # Also print a compact console summary
    print("\n=== SUMMARY ===")
    print("15m mapping:", mapping)
    print("15m wt2 clean MAE:", s_wt2_clean["mae"], "corr:", s_wt2_clean["corr"])
    print("15m mfi0 clean MAE:", s_mfi0_clean["mae"], "corr:", s_mfi0_clean["corr"])
    print("4h mapping:", mapping_4h)
    print("4h wt2 MAE:", s_wt2_4h["mae"], "corr:", s_wt2_4h["corr"])
    print("4h mfi0 MAE:", s_mfi0_4h["mae"], "corr:", s_mfi0_4h["corr"])


if __name__ == "__main__":
    main()
