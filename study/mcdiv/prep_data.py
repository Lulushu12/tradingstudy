"""
Data preparation for MC-B divergence study.

Loads raw TradingView CSV exports of BINANCE BTCUSDT.P (with Market Cipher B
columns), cleans/dedupes them, and writes clean parquet files:

  study/mcdiv/data/15m.parquet
  study/mcdiv/data/4h.parquet
  study/mcdiv/data/1d.parquet
  study/mcdiv/data/1h.parquet   (resampled from cleaned 15m OHLCV, no indicators)

Run as: python3 study/mcdiv/prep_data.py
"""
import glob
import os
import sys

import numpy as np
import pandas as pd

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

KEEP_COLS = [
    "time", "open", "high", "low", "close", "Volume",
    "Lt Blue Wave", "Blue Wave", "Mny Flow", "Buy",
]

RENAME = {
    "time": "ts",
    "open": "open",
    "high": "high",
    "low": "low",
    "close": "close",
    "Volume": "volume",
    "Lt Blue Wave": "exp_wta",
    "Blue Wave": "exp_wtb",
    "Mny Flow": "exp_mfi",
    "Buy": "exp_buy",
}

IND_COLS = ["exp_wta", "exp_wtb", "exp_mfi"]  # for duplicate-agreement checks


def load_and_clean(paths, label):
    """Load one or more CSVs with the shared schema, concat, sort, dedupe."""
    frames = []
    for p in paths:
        df = pd.read_csv(p, usecols=KEEP_COLS)
        frames.append(df)
    raw = pd.concat(frames, ignore_index=True)
    raw = raw.rename(columns=RENAME)
    n_raw = len(raw)

    raw = raw.sort_values("ts", kind="mergesort").reset_index(drop=True)

    # Identify duplicate timestamps and check agreement between duplicates on
    # indicator columns before collapsing.
    dup_mask = raw["ts"].duplicated(keep=False)
    max_discrepancy = 0.0
    max_discrepancy_col = None
    max_discrepancy_ts = None
    n_dup_ts = raw.loc[dup_mask, "ts"].nunique()

    # Secondary, stricter check: discrepancy only among duplicate rows that
    # are FULLY populated across all indicator columns (excludes the "still
    # forming last bar of an export" artifact, where a row can have one
    # indicator column populated with a preliminary/unconverged value while
    # the other columns are still NaN).
    max_full_discrepancy = 0.0
    max_full_discrepancy_col = None
    max_full_discrepancy_ts = None
    n_full_dup_groups = 0
    partial_row_groups = 0

    if n_dup_ts > 0:
        for ts, grp in raw.loc[dup_mask].groupby("ts"):
            if len(grp) < 2:
                continue
            any_partial = grp[IND_COLS].isna().any(axis=1).any()
            if any_partial:
                partial_row_groups += 1
            for col in IND_COLS:
                vals = grp[col].dropna().values
                if len(vals) >= 2:
                    spread = float(np.max(vals) - np.min(vals))
                    if spread > max_discrepancy:
                        max_discrepancy = spread
                        max_discrepancy_col = col
                        max_discrepancy_ts = int(ts)
            full = grp.dropna(subset=IND_COLS)
            if len(full) >= 2:
                n_full_dup_groups += 1
                for col in IND_COLS:
                    vals = full[col].values
                    spread = float(np.max(vals) - np.min(vals))
                    if spread > max_full_discrepancy:
                        max_full_discrepancy = spread
                        max_full_discrepancy_col = col
                        max_full_discrepancy_ts = int(ts)

    # Dedupe: prefer the row with the most non-null indicator values; among
    # ties, prefer the row with a non-null exp_buy too; then keep first.
    raw["_nn"] = raw[IND_COLS].notna().sum(axis=1)
    raw = raw.sort_values(["ts", "_nn"], ascending=[True, False], kind="mergesort")
    deduped = raw.drop_duplicates(subset="ts", keep="first").drop(columns="_nn")
    deduped = deduped.sort_values("ts").reset_index(drop=True)

    deduped["dt"] = pd.to_datetime(deduped["ts"], unit="s", utc=True)

    print(f"--- {label} ---")
    print(f"  files: {len(paths)}")
    print(f"  raw rows (concatenated): {n_raw}")
    print(f"  duplicate timestamps found: {n_dup_ts}")
    print(f"  duplicate groups containing a partially-null row (still-forming "
          f"last bar of an export): {partial_row_groups}")
    print(f"  max discrepancy among duplicate rows on indicator cols "
          f"(any pairwise non-null overlap, incl. partial rows): "
          f"{max_discrepancy!r} (col={max_discrepancy_col}, ts={max_discrepancy_ts})")
    print(f"  max discrepancy among duplicate rows where BOTH rows are fully "
          f"populated across all 3 indicator cols ({n_full_dup_groups} such groups): "
          f"{max_full_discrepancy!r} (col={max_full_discrepancy_col}, ts={max_full_discrepancy_ts})")
    print(f"  deduped rows: {len(deduped)}")
    if len(deduped):
        print(f"  span: {deduped['dt'].iloc[0]}  ->  {deduped['dt'].iloc[-1]}")

    return deduped, {
        "label": label,
        "n_raw": n_raw,
        "n_dup_ts": int(n_dup_ts),
        "partial_row_groups": partial_row_groups,
        "max_discrepancy": max_discrepancy,
        "max_discrepancy_col": max_discrepancy_col,
        "max_discrepancy_ts": max_discrepancy_ts,
        "max_full_discrepancy": max_full_discrepancy,
        "max_full_discrepancy_col": max_full_discrepancy_col,
        "max_full_discrepancy_ts": max_full_discrepancy_ts,
        "n_full_dup_groups": n_full_dup_groups,
        "n_deduped": len(deduped),
    }


def report_gaps(df, expected_spacing, label):
    ts = df["ts"].values
    diffs = np.diff(ts)
    gap_mask = diffs > expected_spacing
    n_gaps = int(gap_mask.sum())
    print(f"\n--- {label} gap structure (expected spacing {expected_spacing}s) ---")
    print(f"  total bar-to-bar intervals: {len(diffs)}")
    print(f"  intervals > expected spacing (gaps): {n_gaps}")
    if n_gaps == 0:
        return {"label": label, "n_gaps": 0, "top_gaps": []}

    gap_idx = np.where(gap_mask)[0]
    gap_sizes = diffs[gap_idx]
    order = np.argsort(-gap_sizes)
    top_n = min(10, len(order))
    top_gaps = []
    print(f"  top {top_n} largest gaps:")
    for k in order[:top_n]:
        i = gap_idx[k]
        start_ts = int(ts[i])
        end_ts = int(ts[i + 1])
        start_dt = pd.to_datetime(start_ts, unit="s", utc=True)
        end_dt = pd.to_datetime(end_ts, unit="s", utc=True)
        gap_s = int(diffs[i])
        n_missing = gap_s // expected_spacing - 1
        print(f"    {start_dt}  ->  {end_dt}   gap={gap_s}s (~{n_missing} bars missing)")
        top_gaps.append({
            "start": str(start_dt), "end": str(end_dt),
            "gap_seconds": gap_s, "missing_bars": int(n_missing),
        })
    return {"label": label, "n_gaps": n_gaps, "top_gaps": top_gaps}


def resample_1h(df15):
    d = df15.set_index("dt")[["ts", "open", "high", "low", "close", "volume"]].copy()
    agg = d.resample("1h", closed="left", label="left").agg({
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
    })
    agg = agg.dropna(subset=["open", "high", "low", "close"])
    agg = agg.reset_index()
    agg["ts"] = (agg["dt"].astype("int64") // 10**9).astype("int64")
    agg = agg[["ts", "dt", "open", "high", "low", "close", "volume"]]
    return agg


def main():
    summaries = []

    # --- 15m ---
    fifteen_paths = sorted(glob.glob(os.path.join(REPO_ROOT, "New export", "15m", "*.csv")))
    print(f"Found {len(fifteen_paths)} 15m CSV files")
    assert len(fifteen_paths) == 17, f"expected 17 15m files, found {len(fifteen_paths)}"
    df15, summary15 = load_and_clean(fifteen_paths, "15m")
    summaries.append(summary15)
    gaps15 = report_gaps(df15, 900, "15m")

    out15 = os.path.join(DATA_DIR, "15m.parquet")
    df15.to_parquet(out15, index=False)
    print(f"  wrote {out15}  ({len(df15)} rows)")

    # --- 4h ---
    fourh_path = os.path.join(REPO_ROOT, "BINANCE_BTCUSDT.P, 240.csv")
    df4h, summary4h = load_and_clean([fourh_path], "4h")
    summaries.append(summary4h)
    gaps4h = report_gaps(df4h, 4 * 3600, "4h")
    out4h = os.path.join(DATA_DIR, "4h.parquet")
    df4h.to_parquet(out4h, index=False)
    print(f"  wrote {out4h}  ({len(df4h)} rows)")

    # --- 1D ---
    oned_path = os.path.join(REPO_ROOT, "BINANCE_BTCUSDT.P, 1D.csv")
    df1d, summary1d = load_and_clean([oned_path], "1D")
    summaries.append(summary1d)
    gaps1d = report_gaps(df1d, 24 * 3600, "1D")
    out1d = os.path.join(DATA_DIR, "1d.parquet")
    df1d.to_parquet(out1d, index=False)
    print(f"  wrote {out1d}  ({len(df1d)} rows)")

    # --- 1h resample from cleaned 15m ---
    df1h = resample_1h(df15)
    out1h = os.path.join(DATA_DIR, "1h.parquet")
    df1h.to_parquet(out1h, index=False)
    print(f"\n--- 1h (resampled from 15m) ---")
    print(f"  rows: {len(df1h)}")
    print(f"  span: {df1h['dt'].iloc[0]}  ->  {df1h['dt'].iloc[-1]}")
    print(f"  wrote {out1h}")

    print("\n=== SUMMARY ===")
    for s in summaries:
        print(s)
    for g in (gaps15, gaps4h, gaps1d):
        print({"label": g["label"], "n_gaps": g["n_gaps"]})


if __name__ == "__main__":
    main()
