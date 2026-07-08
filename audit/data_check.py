"""Gate 0 step 2: map, merge, and integrity-check the 15m studied data.

Reads the TradingView 15m export chunks in 15/, merges them, and reports:
chunk spans, duplicates, gaps, timezone alignment, bad bars.
Never touches any holdout path (none exists yet; created later in Gate 0).
"""
import glob
import os
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HOLDOUT_DOC = os.path.join(ROOT, "HOLDOUT_DO_NOT_TOUCH.md")


def assert_not_holdout(path: str) -> None:
    """Refuse to load anything under a quarantined holdout path."""
    if not os.path.exists(HOLDOUT_DOC):
        return
    with open(HOLDOUT_DOC) as f:
        for line in f:
            if line.startswith("PATH:"):
                quarantined = line.split("PATH:", 1)[1].strip()
                if quarantined and os.path.abspath(path).startswith(os.path.abspath(quarantined)):
                    raise RuntimeError(f"HOLDOUT QUARANTINE: refusing to load {path}")


def load_15m() -> pd.DataFrame:
    files = sorted(glob.glob(os.path.join(ROOT, "15", "*.csv"))
                   + glob.glob(os.path.join(ROOT, "New export", "15m", "*.csv")))
    frames = []
    print(f"{len(files)} chunk files found")
    for f in files:
        assert_not_holdout(f)
        df = pd.read_csv(f)
        df["src_file"] = os.path.basename(f)
        frames.append(df)
        t0 = pd.to_datetime(df["time"].iloc[0], unit="s", utc=True)
        t1 = pd.to_datetime(df["time"].iloc[-1], unit="s", utc=True)
        print(f"  {os.path.basename(f):40s} {len(df):6d} rows  {t0}  ->  {t1}")
    merged = pd.concat(frames, ignore_index=True)
    return merged


def main() -> None:
    df = load_15m()
    df["dt"] = pd.to_datetime(df["time"], unit="s", utc=True)

    print("\n=== MERGE ===")
    n_raw = len(df)
    dup_mask = df.duplicated(subset="time", keep=False)
    n_dup_rows = int(dup_mask.sum())
    # check whether duplicated timestamps agree on OHLC
    conflicts = 0
    if n_dup_rows:
        g = df[dup_mask].groupby("time")[["open", "high", "low", "close"]].nunique()
        conflicts = int((g > 1).any(axis=1).sum())
    # On duplicate timestamps prefer the completed bar: TV exports can capture the
    # newest bar mid-formation, and a partial bar always has less volume.
    df = (df.sort_values(["time", "Volume"], ascending=[True, False])
            .drop_duplicates(subset="time", keep="first").reset_index(drop=True))
    print(f"raw rows {n_raw}, duplicated-timestamp rows {n_dup_rows} "
          f"(OHLC-conflicting timestamps: {conflicts}), unique bars {len(df)}")

    print("\n=== SPAN ===")
    print(f"first bar {df['dt'].iloc[0]}  last bar {df['dt'].iloc[-1]}")
    print(f"UTC alignment: all timestamps divisible by 900s: {(df['time'] % 900 == 0).all()}")

    print("\n=== GAPS ===")
    diff = df["time"].diff()
    gaps = df[diff > 900]
    print(f"gaps (delta > 900s): {len(gaps)}")
    for _, row in gaps.iterrows():
        prev_t = row["time"] - diff.loc[row.name]
        missing = int(diff.loc[row.name] // 900) - 1
        print(f"  gap after {pd.to_datetime(prev_t, unit='s', utc=True)}: "
              f"{missing} bars missing (next bar {row['dt']})")
    expected = int((df["time"].iloc[-1] - df["time"].iloc[0]) // 900) + 1
    print(f"expected bars if continuous: {expected}, actual: {len(df)}, "
          f"missing total: {expected - len(df)}")

    print("\n=== BAD BARS ===")
    bad_hl = df[(df["high"] < df["low"]) | (df["high"] < df["open"]) | (df["high"] < df["close"])
                | (df["low"] > df["open"]) | (df["low"] > df["close"])]
    print(f"OHLC-inconsistent bars: {len(bad_hl)}")
    print(f"non-positive prices: {int((df[['open','high','low','close']] <= 0).any(axis=1).sum())}")
    print(f"NaN in OHLC: {int(df[['open','high','low','close']].isna().any(axis=1).sum())}")
    zero_range = df[(df["high"] == df["low"])]
    print(f"zero-range bars (high==low): {len(zero_range)}")
    zero_vol = df[df["Volume"] == 0] if "Volume" in df else pd.DataFrame()
    print(f"zero-volume bars: {len(zero_vol)}")

    print("\n=== INDICATOR COLUMNS (for port validation) ===")
    for col in ["Lt Blue Wave", "Blue Wave", "VWAP", "Mny Flow"]:
        if col in df:
            nn = df[col].notna().sum()
            print(f"  {col}: {nn} non-null of {len(df)}")

    # The very last studied bar (open 2026-06-21 16:45 UTC) was exported from
    # TV mid-formation (vol 19.453 vs 366.936). Patch it with the completed
    # bar from the Binance USDT-M archive, verified 2026-07-08. The two prior
    # bars match the archive exactly, so the feeds are interchangeable here.
    fix = df["time"] == 1782060300
    if fix.any():
        df.loc[fix, ["open", "high", "low", "close", "Volume"]] = \
            [64084.0, 64188.0, 64078.4, 64122.3, 366.936]
        print("\npatched partial final bar 1782060300 with completed Binance bar")

    out = os.path.join(ROOT, "audit", "studied_15m.parquet")
    df.to_parquet(out)
    print(f"\nsaved merged studied 15m data to {out}")

    # compare with prior study parquet coverage, metadata only
    prior = os.path.join(ROOT, "study", "data", "15m.parquet")
    if os.path.exists(prior):
        p = pd.read_parquet(prior)
        tcol = None
        for c in ["time", "timestamp", "ts", "open_time"]:
            if c in p.columns:
                tcol = c
                break
        if tcol is None and isinstance(p.index, pd.DatetimeIndex):
            print(f"prior study 15m.parquet: {len(p)} rows, "
                  f"{p.index.min()} -> {p.index.max()} (index)")
        elif tcol:
            t = pd.to_datetime(p[tcol], unit="s", utc=True, errors="coerce")
            if t.isna().all():
                t = pd.to_datetime(p[tcol], utc=True, errors="coerce")
            print(f"prior study 15m.parquet: {len(p)} rows, {t.min()} -> {t.max()}")
        else:
            print(f"prior study 15m.parquet: {len(p)} rows, columns {list(p.columns)}")


if __name__ == "__main__":
    sys.exit(main())
