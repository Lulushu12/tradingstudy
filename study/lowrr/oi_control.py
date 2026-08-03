"""Is elevated open interest just a proxy for elevated volatility?

The obvious mundane explanation for the OI filter is that high OI periods are
high-volatility periods, and the study already knows a volatility filter helps a
little. If the OI filter is a worse-measured ATR filter, it is not new
information, it is a detour.

Three controls:
  1. how correlated is the OI percentile with the ATR percentile
  2. an ATR-percentile filter matched to the SAME selectivity (same share of bars
     kept), so the comparison is like for like rather than a filter that simply
     trades less
  3. the OI filter applied WITHIN volatility buckets. If it survives inside both
     the high-vol and low-vol halves, it is carrying information the ATR does not.

Also attaches a day-clustered CI to the DIFFERENCE (filtered minus unfiltered),
which is what actually needs to exclude zero, rather than to the level.
"""
import sys, os, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd
from lowrr import core
from lowrr.multiasset import load_path_file, BN, MAJORS, SLIP_MAJOR, SLIP_ALT
from lowrr.finalists_lowrr import nonoverlap
from lowrr.oi_verify import build, SYMS, RR, AM

HERE = os.path.dirname(os.path.abspath(__file__))
RNG = np.random.default_rng(7)

def day_ci_diff(a, b, block_days=5, n_boot=1500):
    """Day-clustered bootstrap CI on mean(a) - mean(b), resampling whole day blocks
    from each series independently."""
    def blocks(t):
        d = (t["exit_time"].values // 86400).astype(np.int64)
        d0 = d.min()
        blk = (d - d0) // block_days
        g = pd.Series(t["net_R"].values).groupby(blk)
        return [v.values for _, v in g]
    A, B = blocks(a), blocks(b)
    if len(A) < 8 or len(B) < 8:
        return np.nan, np.nan
    out = np.empty(n_boot)
    for i in range(n_boot):
        ia = RNG.integers(0, len(A), len(A))
        ib = RNG.integers(0, len(B), len(B))
        out[i] = (np.concatenate([A[j] for j in ia]).mean()
                  - np.concatenate([B[j] for j in ib]).mean())
    return np.percentile(out, 2.5), np.percentile(out, 97.5)

def trades(d, path, slip, mask):
    idx = np.where(mask)[0]; idx = idx[idx < len(d) - 1]
    if len(idx) < 25: return None
    tr = core.trades_for_signals(d, idx, -np.ones(len(idx)), AM, RR, path,
                                 max_hold_days=50)
    if len(tr) == 0: return None
    tr["cost_R"] = core.cost_R(tr["stop_frac"].values, tr["nights"].values,
                               slip_rt=2 * slip)
    tr["net_R"] = tr["gross_R"] - tr["cost_R"]
    return tr

def main():
    pooled = {}
    print("=== control 1: correlation of OI percentile with ATR percentile ===")
    built = {}
    for sym in SYMS:
        if not os.path.exists(os.path.join(HERE, "flow", f"{sym}_metrics.parquet")):
            continue
        d = build(sym)
        d["atr_p90"] = d["atr_pct"].rolling(540, min_periods=200).rank(pct=True)
        built[sym] = d
        c = d[["oi_p90", "atr_p90"]].dropna().corr().iloc[0, 1]
        print(f"  {sym}: corr(oi_p90, atr_p90) = {c:+.3f}  "
              f"(overlap of the two top deciles: "
              f"{((d.oi_p90>=0.9)&(d.atr_p90>=0.9)).sum()/max((d.oi_p90>=0.9).sum(),1):.1%})")

    print("\n=== controls 2 and 3: OI filter vs a selectivity-matched ATR filter ===")
    print(f"{'sym':>8}{'rr':>6}{'base_n':>8}{'exp_base':>10}{'exp_OI':>9}{'exp_ATR':>9}"
          f"{'OI-base':>9}{'ATR-base':>10}{'OI in hiVol':>12}{'OI in loVol':>12}")
    rows = []
    for sym, d in built.items():
        path = load_path_file(os.path.join(BN, f"{sym}_15m.parquet"))
        slip = SLIP_MAJOR if sym in MAJORS else SLIP_ALT
        base = (((d["close"] < d["bb_lo"])
                 | ((d["close"] < d["ema200"]) & (d["vol_ratio"] > 1.8)
                    & (d["close"] < d["open"])))).fillna(False).values
        oi = (d["oi_p90"] >= 0.9).fillna(False).values
        # match selectivity: keep the same share of BASE bars
        share = (base & oi).sum() / max(base.sum(), 1)
        thr = d.loc[base, "atr_p90"].quantile(1 - share)
        atrf = (d["atr_p90"] >= thr).fillna(False).values
        hv = (d["atr_p90"] >= 0.5).fillna(False).values
        t_base = trades(d, path, slip, base)
        t_oi = trades(d, path, slip, base & oi)
        t_atr = trades(d, path, slip, base & atrf)
        t_oi_hv = trades(d, path, slip, base & oi & hv)
        t_bs_hv = trades(d, path, slip, base & hv)
        t_oi_lv = trades(d, path, slip, base & oi & ~hv)
        t_bs_lv = trades(d, path, slip, base & ~hv)
        for rr in RR:
            def g(t):
                if t is None: return None
                x = nonoverlap(t[t["rr"] == rr].copy())
                return x if len(x) >= 30 else None
            a, o, at = g(t_base), g(t_oi), g(t_atr)
            ohv, bhv, olv, blv = g(t_oi_hv), g(t_bs_hv), g(t_oi_lv), g(t_bs_lv)
            if a is None or o is None or at is None: continue
            d_hv = (ohv["net_R"].mean() - bhv["net_R"].mean()) if (ohv is not None and bhv is not None) else np.nan
            d_lv = (olv["net_R"].mean() - blv["net_R"].mean()) if (olv is not None and blv is not None) else np.nan
            print(f"{sym.replace('USDT',''):>8}{rr:>6.2f}{len(a):>8}{a['net_R'].mean():>+10.3f}"
                  f"{o['net_R'].mean():>+9.3f}{at['net_R'].mean():>+9.3f}"
                  f"{o['net_R'].mean()-a['net_R'].mean():>+9.3f}"
                  f"{at['net_R'].mean()-a['net_R'].mean():>+10.3f}"
                  f"{d_hv:>+12.3f}{d_lv:>+12.3f}", flush=True)
            rows.append(dict(sym=sym, rr=rr, e_base=a["net_R"].mean(),
                             e_oi=o["net_R"].mean(), e_atr=at["net_R"].mean(),
                             d_oi=o["net_R"].mean()-a["net_R"].mean(),
                             d_atr=at["net_R"].mean()-a["net_R"].mean(),
                             d_hv=d_hv, d_lv=d_lv))
            pooled.setdefault(rr, {"base": [], "oi": []})
            pooled[rr]["base"].append(a); pooled[rr]["oi"].append(o)
    res = pd.DataFrame(rows)
    res.to_csv(os.path.join(HERE, "oi_control_results.csv"), index=False)

    print("\n=== pooled over the 3 instruments, day-clustered CI on the DIFFERENCE ===")
    print(f"{'rr':>6}{'n_base':>8}{'n_oi':>7}{'exp_base':>10}{'exp_OI':>9}"
          f"{'delta':>8}{'95% CI on delta':>22}")
    for rr in RR:
        if rr not in pooled: continue
        b = pd.concat(pooled[rr]["base"], ignore_index=True)
        o = pd.concat(pooled[rr]["oi"], ignore_index=True)
        lo, hi = day_ci_diff(o, b)
        print(f"{rr:>6.2f}{len(b):>8}{len(o):>7}{b['net_R'].mean():>+10.3f}"
              f"{o['net_R'].mean():>+9.3f}{o['net_R'].mean()-b['net_R'].mean():>+8.3f}"
              f"{f'{lo:+.3f} to {hi:+.3f}':>22}")

    print("\n=== summary ===")
    print(f"  OI filter beats base in {(res.d_oi>0).sum()}/{len(res)} cells, "
          f"median {res.d_oi.median():+.3f}")
    print(f"  ATR filter beats base in {(res.d_atr>0).sum()}/{len(res)} cells, "
          f"median {res.d_atr.median():+.3f}")
    print(f"  OI edge inside HIGH vol: median {res.d_hv.median():+.3f}  "
          f"positive in {(res.d_hv>0).sum()}/{res.d_hv.notna().sum()}")
    print(f"  OI edge inside LOW vol:  median {res.d_lv.median():+.3f}  "
          f"positive in {(res.d_lv>0).sum()}/{res.d_lv.notna().sum()}")

if __name__ == "__main__":
    main()
