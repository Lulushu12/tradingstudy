"""Unconditional barrier baseline: what does cutting R:R actually buy you?

For EVERY bar on a timeframe we resolve a hypothetical long and a hypothetical
short (stop = atr_mult * ATR14, target = rr * stop) on the true 5-minute path,
across an R:R ladder. No signal, no filter, no edge. Just the geometry.

What this measures:
  - realised winrate vs the driftless fair line 1/(1+rr)
  - the Breakout cost in R at each rr, including the 5 bps overnight fee
  - the winrate you would need (breakeven) vs the winrate the market hands you
  - the EDGE GAP: how many winrate points of genuine skill you must add at each
    rr just to reach zero.
"""
import sys, os, time, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd
import indicators as ind
from lowrr import core

RR_GRID = [0.25, 0.33, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0]

def run(tf="4H", atr_mult=1.5, path_tf="5m", max_hold_days=50, start="2021-05-24"):
    df = ind.enrich(pd.read_parquet(os.path.join(core.DATA, f"{tf}.parquet")))
    df = df[df["dt"] >= pd.Timestamp(start, tz="UTC")].reset_index(drop=True)
    path = core.load_path(path_tf)
    idx = np.arange(len(df) - 1)
    ok = np.isfinite(df["atr14"].values[idx]) & (df["atr14"].values[idx] > 0)
    idx = idx[ok]
    sig_idx = np.concatenate([idx, idx])
    sig_side = np.concatenate([np.ones(len(idx)), -np.ones(len(idx))])
    t0 = time.time()
    tr = core.trades_for_signals(df, sig_idx, sig_side, atr_mult, RR_GRID, path,
                                 max_hold_days=max_hold_days)
    print(f"# {tf}: {len(idx)} bars x 2 sides x {len(RR_GRID)} rr "
          f"= {len(tr)} resolutions in {time.time()-t0:.0f}s "
          f"({df['dt'].iloc[0].date()} -> {df['dt'].iloc[-1].date()})")
    return tr

def table(tr, tf):
    print(f"\n===== {tf} unconditional barrier ladder (stop = 1.5*ATR14, 5m path) =====")
    print(f"{'rr':>5} {'WR':>7} {'fair':>7} {'diff':>7} | {'stop%':>6} {'nights':>6} "
          f"{'commR':>6} {'carryR':>6} {'costR':>6} | {'be_WR':>7} {'gap':>7} "
          f"{'grossR':>7} {'netR':>7} {'hold_h':>7} {'t/o':>5}")
    rows = []
    for rr in RR_GRID:
        s = tr[tr["rr"] == rr]
        res = (s["res"] != 0).sum()
        wr = (s["res"] == 1).sum() / res
        sf = s["stop_frac"].mean(); ni = s["nights"].mean()
        commR = (core.COMM_RT + core.SLIP_RT) / sf
        carryR = core.OVERNIGHT * ni / sf
        be = core.breakeven_wr(rr, sf, ni)
        fair = core.fair_wr(rr)
        rows.append(dict(rr=rr, wr=wr, fair=fair, be=be, gap=be - wr,
                         grossR=s["gross_R"].mean(), netR=s["net_R"].mean(),
                         costR=s["cost_R"].mean(), nights=ni, stop_frac=sf,
                         hold=s["hold_h"].mean(), to=(s["res"] == 0).mean()))
        print(f"{rr:>5.2f} {wr:>6.1%} {fair:>6.1%} {wr-fair:>+6.1%} | {sf:>5.2%} {ni:>6.2f} "
              f"{commR:>6.3f} {carryR:>6.3f} {s['cost_R'].mean():>6.3f} | "
              f"{be:>6.1%} {be-wr:>+6.1%} {s['gross_R'].mean():>+7.3f} "
              f"{s['net_R'].mean():>+7.3f} {s['hold_h'].mean():>7.1f} {(s['res']==0).mean():>5.1%}")
    print("  WR   = realised unconditional winrate (long and short pooled)")
    print("  fair = 1/(1+rr), the driftless barrier odds")
    print("  be   = winrate needed for zero net expectancy after Breakout costs")
    print("  gap  = edge in winrate POINTS a signal must supply to break even")
    return pd.DataFrame(rows)

if __name__ == "__main__":
    out = {}
    for tf in ["4H", "1D"]:
        tr = run(tf)
        out[tf] = table(tr, tf)
        tr.to_parquet(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   f"barrier_{tf}.parquet"))
