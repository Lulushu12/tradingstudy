"""Does the open-interest filter ADD anything, or just select a subset?

The filtered cells look strong, but the base rules they filter are already the
two best rules in the study. A filter that merely retains a favourable slice of
an already-positive rule is not a discovery, it is a smaller sample of the same
edge. The question is incremental value:

    expR(base AND filter)  vs  expR(base)  on the SAME instrument
    and expR(base AND NOT filter), because if the complement is also positive the
    filter is not separating anything

Reported per instrument and pooled with a day-clustered CI on the DIFFERENCE,
not on the level.
"""
import sys, os, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd
import indicators as ind
from lowrr import core
from lowrr.multiasset import load_path_file, BN, MAJORS, SLIP_MAJOR, SLIP_ALT
from lowrr.finalists_lowrr import nonoverlap
from lowrr.pooled_test import day_cluster_ci
from lowrr.oi_verify import build, conditions, SYMS, RR, AM, CUT

HERE = os.path.dirname(os.path.abspath(__file__))
FILTERS = ["h4b_glob_top_p30", "h4b_glob_top_p90", "h2_oi_top_p90"]

def trades(d, path, slip, mask, rr_grid=RR):
    idx = np.where(mask)[0]
    idx = idx[idx < len(d) - 1]
    if len(idx) < 25:
        return None
    tr = core.trades_for_signals(d, idx, -np.ones(len(idx)), AM, rr_grid, path,
                                 max_hold_days=50)
    if len(tr) == 0:
        return None
    tr["cost_R"] = core.cost_R(tr["stop_frac"].values, tr["nights"].values,
                               slip_rt=2 * slip)
    tr["net_R"] = tr["gross_R"] - tr["cost_R"]
    return tr

def main():
    store = {}
    for sym in SYMS:
        if not os.path.exists(os.path.join(HERE, "flow", f"{sym}_metrics.parquet")):
            continue
        d = build(sym)
        path = load_path_file(os.path.join(BN, f"{sym}_15m.parquet"))
        slip = SLIP_MAJOR if sym in MAJORS else SLIP_ALT
        conds = conditions(d)
        bases = {
            "S_bb_break_dn": (d["close"] < d["bb_lo"]).fillna(False).values,
            "S_volspike18_dn": ((d["close"] < d["ema200"]) & (d["vol_ratio"] > 1.8)
                                & (d["close"] < d["open"])).fillna(False).values,
        }
        store[sym] = (d, path, slip, conds, bases)
        print(f"built {sym}", flush=True)

    print("\n" + "=" * 108)
    print("INCREMENTAL VALUE OF THE OI FILTER over the unfiltered base rule")
    print("BTC was searched. ETH and SOL were not.")
    print("=" * 108)
    print(f"{'base':<17}{'filter':<19}{'rr':>5}{'sym':>9}{'n_all':>7}{'n_f':>6}"
          f"{'exp_all':>9}{'exp_filt':>9}{'exp_NOTf':>9}{'delta':>8}")
    rows = []
    for bname in ["S_bb_break_dn", "S_volspike18_dn"]:
        for fname in FILTERS:
            for rr in RR:
                for sym, (d, path, slip, conds, bases) in store.items():
                    b = bases[bname]
                    f = conds[fname]
                    t_all = trades(d, path, slip, b)
                    t_f = trades(d, path, slip, b & f)
                    t_n = trades(d, path, slip, b & ~f)
                    if t_all is None or t_f is None or t_n is None:
                        continue
                    a = nonoverlap(t_all[t_all["rr"] == rr].copy())
                    ff = nonoverlap(t_f[t_f["rr"] == rr].copy())
                    nn = nonoverlap(t_n[t_n["rr"] == rr].copy())
                    if min(len(a), len(ff), len(nn)) < 30:
                        continue
                    rows.append(dict(base=bname, filt=fname, rr=rr, sym=sym,
                                     n_all=len(a), n_f=len(ff),
                                     e_all=a["net_R"].mean(),
                                     e_f=ff["net_R"].mean(),
                                     e_n=nn["net_R"].mean(),
                                     delta=ff["net_R"].mean() - a["net_R"].mean()))
                    r = rows[-1]
                    print(f"{bname:<17}{fname:<19}{rr:>5.2f}{sym.replace('USDT',''):>9}"
                          f"{r['n_all']:>7}{r['n_f']:>6}{r['e_all']:>+9.3f}"
                          f"{r['e_f']:>+9.3f}{r['e_n']:>+9.3f}{r['delta']:>+8.3f}",
                          flush=True)
    res = pd.DataFrame(rows)
    res.to_csv(os.path.join(HERE, "oi_incremental_results.csv"), index=False)

    print("\n" + "=" * 108)
    print("SUMMARY: is the filtered slice better than the whole rule?")
    print("=" * 108)
    for fname in FILTERS:
        s = res[res.filt == fname]
        if len(s) == 0:
            continue
        print(f"\n{fname}:")
        print(f"  cells where filter beats unfiltered: {(s.delta>0).sum()}/{len(s)}")
        print(f"  median delta {s.delta.median():+.3f}   "
              f"BTC {s[s.sym=='BTCUSDT'].delta.median():+.3f}   "
              f"ETH {s[s.sym=='ETHUSDT'].delta.median():+.3f}   "
              f"SOL {s[s.sym=='SOLUSDT'].delta.median():+.3f}")
        print(f"  complement (base AND NOT filter) positive in "
              f"{(s.e_n>0).sum()}/{len(s)} cells, median {s.e_n.median():+.3f}")
        for rr in RR:
            q = s[s.rr == rr]
            if len(q) == 0: continue
            print(f"    rr={rr:<5} delta median {q.delta.median():+.3f}  "
                  f"filt {q.e_f.median():+.3f} vs all {q.e_all.median():+.3f} "
                  f"vs complement {q.e_n.median():+.3f}")

if __name__ == "__main__":
    main()
