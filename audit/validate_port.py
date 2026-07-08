"""Gate 0 step 1: validate the Python port against TradingView-exported values.

The 15m chunk exports carry the indicator columns computed by TradingView:
  Lt Blue Wave = wt1, Blue Wave = wt2, VWAP = wt1 - wt2, Mny Flow = mfi.
We recompute all of them with the port on the merged continuous series and
compare bar by bar. The first BURN_IN bars are excluded: TradingView had
pre-2021 history loaded, the port starts cold on 2021-01-07.

Also checks cross-export consistency: ~73k timestamps exist in two different
TV exports; their indicator values should agree with each other.
"""
import glob
import os

import numpy as np
import pandas as pd

from mcb_port import wavetrend, mfi_clone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BURN_IN = 3000


def cross_export_consistency() -> None:
    frames = []
    for f in glob.glob(os.path.join(ROOT, "15", "*.csv")) + \
             glob.glob(os.path.join(ROOT, "New export", "15m", "*.csv")):
        frames.append(pd.read_csv(f, usecols=lambda c: c in
                                  ["time", "Lt Blue Wave", "Blue Wave", "Mny Flow"]))
    df = pd.concat(frames, ignore_index=True)
    dup = df[df.duplicated("time", keep=False)]
    print(f"cross-export: {dup['time'].nunique()} timestamps present in 2+ exports")
    for col in ["Lt Blue Wave", "Blue Wave", "Mny Flow"]:
        spread = dup.groupby("time")[col].agg(lambda s: s.max() - s.min())
        n_mismatch = int((spread > 1e-9).sum())
        print(f"  {col:14s} max spread {spread.max():.3e}, "
              f"timestamps disagreeing beyond 1e-9: {n_mismatch}")
        if n_mismatch:
            worst = spread.sort_values(ascending=False).head(5)
            for t, v in worst.items():
                print(f"    {pd.to_datetime(t, unit='s', utc=True)}  spread {v:.6g}")


def main() -> None:
    df = pd.read_parquet(os.path.join(ROOT, "audit", "studied_15m.parquet"))
    o = df["open"].to_numpy(float)
    h = df["high"].to_numpy(float)
    l = df["low"].to_numpy(float)
    c = df["close"].to_numpy(float)

    wt1, wt2 = wavetrend(h, l, c)
    mfi = mfi_clone(o, c)

    ref = {
        "wt1 (Lt Blue Wave)": (wt1, df["Lt Blue Wave"].to_numpy(float)),
        "wt2 (Blue Wave)":    (wt2, df["Blue Wave"].to_numpy(float)),
        "vwap (wt1-wt2)":     (wt1 - wt2, df["VWAP"].to_numpy(float)),
        "mfi (Mny Flow)":     (mfi, df["Mny Flow"].to_numpy(float)),
    }
    print(f"bars: {len(df)}, comparing from bar {BURN_IN} "
          f"({df['dt'].iloc[BURN_IN]}) onward\n")
    for name, (mine, tv) in ref.items():
        m = mine[BURN_IN:]
        t = tv[BURN_IN:]
        ok = ~np.isnan(m) & ~np.isnan(t)
        d = np.abs(m[ok] - t[ok])
        scale = np.maximum(np.abs(t[ok]), 1.0)
        rel = d / scale
        print(f"{name:20s} n={ok.sum():6d}  max_abs={d.max():.3e}  "
              f"p999_abs={np.quantile(d, 0.999):.3e}  max_rel={rel.max():.3e}  "
              f"frac_within_1e-6_rel={np.mean(rel < 1e-6):.6f}")
        worst_i = np.argsort(d)[-3:]
        idx = np.where(ok)[0][worst_i] + BURN_IN
        for i in idx:
            print(f"    worst: {df['dt'].iloc[i]}  mine={mine[i]:.8f} tv={tv[i]:.8f} "
                  f"src={df['src_file'].iloc[i]}")
    print()
    cross_export_consistency()


if __name__ == "__main__":
    main()
