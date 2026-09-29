"""Detailed diagnostics for one strategy's trades (IS + OOS only)."""
import numpy as np, pandas as pd
from data import SYMBOLS, OOS_END
from lab import ctx, run, Exit
from stage3 import get_signal


def trades_for(family, variant, htf, bias, ex, tf="15m", syms=SYMBOLS, holdout=False, sl_override=None):
    out = []
    for s in syms:
        cx = ctx(s, tf)
        sig, sl = get_signal(cx, family, variant, htf, bias, include_holdout=holdout)
        sl_arr = sl_override(cx, sig) if sl_override else None
        out.append(run(cx, sig, ex, sl_dist=sl_arr))
    t = pd.concat(out, ignore_index=True)
    t["time"] = pd.to_datetime(t.time, utc=True)
    if not holdout:
        t = t[t.time < OOS_END]
    return t


def describe(t, label=""):
    r = t.r
    srt = np.sort(r.values)[::-1]
    top1 = srt[: max(1, len(srt) // 100)].sum()
    print(f"== {label}  n={len(t)}  avgR={r.mean():.3f}  WR={(r>0).mean():.2%}  sumR={r.sum():.0f}  "
          f"sumR excl. top1% trades={r.sum()-top1:.0f}  median hold={((t.xbar-t.ebar).median())} bars")
    g = lambda k: t.groupby(k).r.agg(["count", "mean", "sum"]).round(3)
    print("by direction:\n", g(t.dir.map({1: "long", -1: "short"})).T.to_string())
    print("by symbol:\n", g("sym").T.to_string())
    print("by year:\n", g(t.time.dt.year).T.to_string())
    print("exit reasons:\n", t.reason.map({1: "stop", 2: "tp", 3: "time", 4: "opp", 5: "trail", 6: "end"}).value_counts().to_string())
