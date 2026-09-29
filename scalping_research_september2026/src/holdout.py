"""One-time holdout evaluation of the frozen spec (FINAL_SPEC.md)."""
import numpy as np
import pandas as pd

from data import SYMBOLS, TF_MIN
from engine import simulate, FEE, SLIP
from lab import ctx
import features as fx
from asia_lab import asia_fade_signal
from portfolio import account, period, monthly_report, challenge_stats

SPEC = dict(or_min=45, win_h=4, htf="1d", bias="ema200", sl_atr=4.0, be_r=1.0, hold_bars=288)


def final_trades():
    out = []
    for sym in SYMBOLS:
        cx = ctx(sym, "15m")
        base = asia_fade_signal(cx, SPEC["or_min"], SPEC["win_h"], include_holdout=True)
        b = fx.htf_bias(cx, SPEC["htf"], SPEC["bias"]).astype(np.int64)
        s = np.where(b == base, base, 0)
        tr = simulate(cx.o, cx.h, cx.l, cx.c, cx.h1, cx.l1, cx.mm, s, SPEC["sl_atr"] * cx.atr, cx.atr, cx.c,
                      0.0, SPEC["be_r"], 0, 0.0, SPEC["hold_bars"], False, 0.0, 0.0, FEE, SLIP)
        t = pd.DataFrame(tr, columns=["ebar", "xbar", "dir", "entry", "exit", "sl_pct", "r", "reason"])
        t["time"] = cx.df.index[t.ebar.astype(int) + 1]
        t["xtime"] = cx.df.index[t.xbar.astype(int)] + pd.Timedelta(minutes=15)
        t["sym"] = sym
        t["strat"] = "AORF"
        out.append(t)
    return pd.concat(out, ignore_index=True)


if __name__ == "__main__":
    pd.set_option("display.width", 250, "display.max_columns", 30)
    t = final_trades()
    t["per"] = period(t)
    t.to_parquet("../results/final_trades_all_periods.parquet")
    print("=== Per-trade stats by period (R, after costs) ===")
    g = t.groupby("per").r
    print(pd.DataFrame({"n": g.size(), "avgR": g.mean(), "WR": g.apply(lambda x: (x > 0).mean()), "sumR": g.sum(),
                        "long_avg": t[t.dir == 1].groupby("per").r.mean(),
                        "short_avg": t[t.dir == -1].groupby("per").r.mean()}).round(3).loc[["IS", "OOS", "HOLDOUT"]].to_string())
    h = t[t.per == "HOLDOUT"]
    print("\n=== HOLDOUT by coin ===")
    print(h.groupby("sym").r.agg(["count", "mean", "sum"]).round(3).T.to_string())
    print("\n=== HOLDOUT exit reasons ===")
    print(h.reason.map({1: "stop", 2: "tp", 3: "time", 6: "end of data"}).value_counts().to_string())
    for risk in (0.002, 0.0025, 0.003, 0.005):
        a = account(t, risk=risk)
        a["per"] = period(a)
        print(f"\n=== Account sim, risk {risk:.2%}/trade ===")
        for p in ("IS", "OOS", "HOLDOUT"):
            s = a[a.per == p]
            m, dd = monthly_report(s)
            print(f"{p:8s} months {len(m):3d}  avg {m.mean():+.2%}  median {m.median():+.2%}  worst {m.min():+.2%}  "
                  f"best {m.max():+.2%}  positive {(m > 0).mean():.0%}  maxDD {dd:.2%}  total {m.sum():+.2%}")
        if risk == 0.0025:
            s = a[a.per == "HOLDOUT"]
            m, _ = monthly_report(s)
            print("HOLDOUT monthly returns:", " ".join(f"{k}:{v:+.2%}" for k, v in m.items()))
            print("HOLDOUT challenge (start weekly, +10% before -6%, until data ends):",
                  challenge_stats(s, horizon_days=150))
