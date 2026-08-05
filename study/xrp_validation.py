"""Task 1 — cross-asset validation: the 4H star on BINANCE XRPUSDT.P.

The strongest robustness test available: NOTHING is re-fitted. The exact BTC rules
(SFP bear0|1 & close<EMA200 on 4H, entry next 4H open, 1.5*ATR(14) stop; exits
fixed 1R/2R/3R and half@1R->BE + 3-ATR trail) are evaluated on a different asset.
XRP raw data = chunked TradingView 15m exports (OHLC only, no volume — the star
uses none), resampled to UTC-aligned 4H. Same fee model (0.08% round trip).

Reports: train/test split at 2025-01 (same as BTC) + year-by-year walk-forward,
for the bear star and the bull mirror.
"""
import warnings; warnings.filterwarnings("ignore")
import glob, os
import numpy as np
import pandas as pd
import indicators as ind
from research import breakeven_wr
from trend_runner import run_fixed
from sfp_divergence import sfp_divergence
from sfp_exits import run_half1R_trail
from sfp_walkforward import yearly

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_xrp_4h():
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "xrp_4H.parquet")
    if os.path.exists(out):
        return pd.read_parquet(out)
    use = ["time", "open", "high", "low", "close"]
    frames = []
    for f in glob.glob(os.path.join(BASE, "HA SHA MFI", "BINANCE_XRPUSDT.P, 15*.csv")):
        frames.append(pd.read_csv(f, usecols=lambda c: c in use))
    df = pd.concat(frames, ignore_index=True)
    for c in use:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = (df.dropna(subset=use).drop_duplicates(subset="time", keep="last")
            .sort_values("time").reset_index(drop=True))
    df["dt"] = pd.to_datetime(df["time"], unit="s", utc=True)
    gaps = int((df["time"].diff() > 900).sum())
    print(f"XRP 15m: {len(df)} bars  {df['dt'].iloc[0]} -> {df['dt'].iloc[-1]}  gaps>{900}s={gaps}")
    r = df.set_index("dt").resample("4h").agg(
        open=("open", "first"), high=("high", "max"),
        low=("low", "min"), close=("close", "last")).dropna(subset=["open"]).reset_index()
    r["volume"] = np.nan
    r["time"] = ((r["dt"] - pd.Timestamp(0, tz="UTC")) // pd.Timedelta(seconds=1)).astype("int64")
    r.to_parquet(out)
    print(f"XRP 4H: {len(r)} bars  {r['dt'].iloc[0]} -> {r['dt'].iloc[-1]}")
    return r

def tt(tag, tr, p_be=None):
    cut = pd.Timestamp("2024-12-31", tz="UTC").timestamp()
    out = []
    for lab, sub in [("TR", tr[tr.entry_time < cut]), ("TE", tr[tr.entry_time >= cut])]:
        if not len(sub):
            out.append(f"{lab}: (none)"); continue
        R = sub["net_R"].values
        out.append(f"{lab}: n={len(sub):3d} WR={(R>0).mean():5.1%} expR={R.mean():+.3f}")
    be = f"(be {p_be:.0%})" if p_be else ""
    print(f"  {tag:30}{be:10} | " + " | ".join(out))

def main():
    df = ind.enrich(load_xrp_4h())
    n = len(df)
    m = sfp_divergence(df)
    dn = (df["close"] < df["ema200"]).values
    star = (m["bear0"] | m["bear1"]) & dn
    bull = (m["bull0"] | m["bull1"]) & ~dn
    Lz = np.zeros(n, bool)
    sfmean = (1.5*df["atr14"]/df["open"].shift(-1)).mean()
    print(f"\nXRP 4H star: n={int(star.sum())}  bull mirror: n={int(bull.sum())}  "
          f"stop~{sfmean:.3%}  feeR~{0.0008/sfmean:.3f}")
    print("\n===== train/test (cut 2025-01, same as BTC) =====")
    for rr in [1.0, 2.0, 3.0]:
        tt(f"star fixed {rr:.0f}R", run_fixed(df, Lz, star, rr=rr), breakeven_wr(rr, sfmean))
    tt("star half@1R->BE+trail", run_half1R_trail(df, Lz, star, k=3.0))
    for rr in [1.0, 2.0]:
        tt(f"bull fixed {rr:.0f}R", run_fixed(df, bull, Lz, rr=rr), breakeven_wr(rr, sfmean))
    tt("bull half@1R->BE+trail", run_half1R_trail(df, bull, Lz, k=3.0))
    print("\n===== year-by-year walk-forward =====")
    yearly("XRP star fixed 1R", run_fixed(df, Lz, star, rr=1.0))
    yearly("XRP star fixed 3R", run_fixed(df, Lz, star, rr=3.0))
    yearly("XRP star half@1R->BE+trail", run_half1R_trail(df, Lz, star, k=3.0))
    yearly("XRP bull half@1R->BE+trail", run_half1R_trail(df, bull, Lz, k=3.0))

if __name__ == "__main__":
    main()
