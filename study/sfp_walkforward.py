"""Year-by-year walk-forward of the 4H star (SFP bearish divergence + downtrend).

No fitting anywhere — the rules are fixed (entry: SFP bear0|1 & close<EMA200 on 4H,
next-bar-open entry, 1.5*ATR stop) and simply evaluated per calendar year, the same
protocol used to validate the volume-spike strategy in fourh_deep.py. Exits: fixed
1R, 2R, 3R, and half@1R->breakeven + 3-ATR trail. Also shown for the deduped
(first-signal-per-swing) entries and, as a reference, the bull-side mirror.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import indicators as ind
from research import breakeven_wr
from trend_runner import run_fixed
from sfp_divergence import sfp_divergence
from sfp_exits import run_half1R_trail

def yearly(tag, trades):
    t = trades.copy()
    t["year"] = pd.to_datetime(t["entry_time"], unit="s", utc=True).dt.year
    print(f"\n--- {tag} ---")
    print(f"  {'year':6} {'n':>4} {'WR':>7} {'expR':>8} {'sumR':>8}")
    for y, sub in t.groupby("year"):
        R = sub["net_R"].values
        print(f"  {y:<6} {len(sub):>4} {(R>0).mean():>6.1%} {R.mean():>+8.3f} {R.sum():>+8.1f}")
    R = t["net_R"].values
    pos_years = sum((sub['net_R'].sum() > 0) for _, sub in t.groupby('year'))
    n_years = t['year'].nunique()
    print(f"  {'ALL':<6} {len(t):>4} {(R>0).mean():>6.1%} {R.mean():>+8.3f} {R.sum():>+8.1f}"
          f"   positive years: {pos_years}/{n_years}")

def main():
    df = ind.enrich(pd.read_parquet("data/4H.parquet"))
    n = len(df)
    m = sfp_divergence(df)
    dn = (df["close"] < df["ema200"]).values
    up = ~dn
    star = (m["bear0"] | m["bear1"]) & dn
    dedup = star & ~np.roll(star, 1); dedup[0] = star[0]
    bull = (m["bull0"] | m["bull1"]) & up
    Lz = np.zeros(n, bool)
    sfmean = (1.5*df["atr14"]/df["open"].shift(-1)).mean()
    print(f"4H star walk-forward  (breakeven WR: {breakeven_wr(1.0, sfmean):.1%} @1R, "
          f"{breakeven_wr(2.0, sfmean):.1%} @2R, {breakeven_wr(3.0, sfmean):.1%} @3R)")
    for rr in [1.0, 2.0, 3.0]:
        yearly(f"star  fixed {rr:.0f}R", run_fixed(df, Lz, star, rr=rr))
    yearly("star  half@1R->BE + 3ATRtrail", run_half1R_trail(df, Lz, star, k=3.0))
    yearly("star DEDUP  half@1R->BE + 3ATRtrail", run_half1R_trail(df, Lz, dedup, k=3.0))
    yearly("star DEDUP  fixed 3R", run_fixed(df, Lz, dedup, rr=3.0))
    yearly("bull mirror  half@1R->BE + 3ATRtrail (ref)", run_half1R_trail(df, bull, Lz, k=3.0))

if __name__ == "__main__":
    main()
