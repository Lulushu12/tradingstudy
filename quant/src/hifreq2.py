"""High-frequency system, evaluated through the REAL account simulator.

Correction to hifreq.py: that version capped ENTRIES per day and sized 3%/k,
claiming the daily loss limit could not be breached. That was wrong. Trades
entered on different days can exit on the SAME day, and the 3% limit applies to
realised equity change, i.e. to exits. The bound never held, and every config
did in fact breach.

Here the selected signals are turned into a real trade list with entry and exit
timestamps and pushed through validate.account_run, which applies the static
floor, the daily limit on realised P&L, leverage caps and portfolio heat in the
correct order.

IS and WF are always reported together.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dataset as DS      # noqa: E402
import hifreq as HF       # noqa: E402
import validate as V      # noqa: E402

STEP = {"30min": "30min", "1h": "1h", "4h": "4h", "15min": "15min"}


def to_trades(d, keep, side_arr, tf):
    step = pd.Timedelta(STEP[tf])
    parts = []
    for side, rc, oc, ec, sc in ((1, "r_long", "out_long", "exit_long", "stoppct_long"),
                                 (-1, "r_short", "out_short", "exit_short", "stoppct_short")):
        m = keep & (side_arr == side) & np.isfinite(d[rc].values)
        if m.sum() == 0:
            continue
        parts.append(pd.DataFrame({
            "entry_dt": pd.to_datetime(d.loc[m, "dt"].values, utc=True) + step,
            "exit_dt": pd.to_datetime(d.loc[m, ec].values, utc=True),
            "symbol": d.loc[m, "symbol"].values,
            "side": side,
            "r": d.loc[m, rc].values,
            "outcome": d.loc[m, oc].values,
            "stop_pct": d.loc[m, sc].values,
        }))
    if not parts:
        return pd.DataFrame()
    T = pd.concat(parts).sort_values("entry_dt").reset_index(drop=True)
    return T[T.exit_dt > T.entry_dt].reset_index(drop=True)


def sweep(T, label, risks=(0.001, 0.002, 0.0035, 0.005, 0.0075, 0.01),
          heats=(0.01, 0.02, 0.03, 0.06)):
    rows = []
    for risk in risks:
        for heat in heats:
            if heat < risk:
                continue
            curve, breach, mo = V.account_run(T, risk, heat)
            if len(curve) < 20:
                continue
            eqs = curve.equity.values
            peak = np.maximum.accumulate(eqs)
            dd = float(((peak - eqs) / peak).max())
            total = eqs[-1] / 100_000 - 1
            yrs = (curve.dt.iloc[-1] - curve.dt.iloc[0]).days / 365.25
            rows.append({
                "label": label, "risk": risk, "heat": heat, "fills": len(curve),
                "total": total, "cagr": (1 + total) ** (1 / yrs) - 1 if total > -1 and yrs > 0 else np.nan,
                "maxDD": dd, "mean_mo": float(mo.mean()), "med_mo": float(mo.median()),
                "worst_mo": float(mo.min()), "pos_mo": float((mo > 0).mean()),
                "ge10": float((mo >= 0.10).mean()), "n_mo": len(mo),
                "breach": breach[0] if breach else None,
                "breach_dt": str(breach[1]) if breach else None,
                "survived": breach is None})
    return pd.DataFrame(rows)


def run(tf="30min", hold=96, ks=(8, 16, 24, 40)):
    d = DS.build(tf=tf, hold=hold)
    feats = DS.feature_list(d)
    print(f"=== {tf}: rows {len(d):,} ===")
    allres = []
    for mode in ("IS", "WF"):
        print(f"\n--- {mode} ---")
        pl, _ = HF.fit_predict(d, feats, "r_long", mode=mode)
        ps, _ = HF.fit_predict(d, feats, "r_short", mode=mode)
        score = np.where(pl >= ps, pl, ps)
        side = np.where(pl >= ps, 1, -1)
        for k in ks:
            keep = HF.select_daily_topk(d, score, side, k)
            T = to_trades(d, keep, side, tf)
            if len(T) < 200:
                continue
            res = sweep(T, f"{mode}_k{k}")
            if not len(res):
                continue
            allres.append(res)
            surv = res[res.survived]
            if len(surv):
                b = surv.loc[surv.mean_mo.idxmax()]
                print(f"  k={k:<3} n={len(T):<6} expR {T.r.mean():+.3f}  "
                      f"BEST SURVIVING: risk {100*b.risk:.2f}% heat {100*b.heat:.0f}%  "
                      f"mean/mo {100*b.mean_mo:+6.2f}%  worst {100*b.worst_mo:+6.2f}%  "
                      f"pos {100*b.pos_mo:.0f}%  >=10% {100*b.ge10:.0f}%  "
                      f"CAGR {100*b.cagr:.0f}%  maxDD {100*b.maxDD:.0f}%")
            else:
                b = res.loc[res.mean_mo.idxmax()]
                print(f"  k={k:<3} n={len(T):<6} expR {T.r.mean():+.3f}  "
                      f"NONE SURVIVED (all breach). best-before-breach "
                      f"risk {100*b.risk:.2f}%: mean/mo {100*b.mean_mo:+.2f}% "
                      f"breach={b.breach} @ {b.breach_dt}")
    return pd.concat(allres) if allres else pd.DataFrame(), d


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--tf", default="30min")
    p.add_argument("--hold", type=int, default=96)
    a = p.parse_args()
    res, d = run(a.tf, a.hold)
    rep = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reports")
    if len(res):
        res.to_csv(os.path.join(rep, f"hifreq2_{a.tf}.csv"), index=False)
        print("\n=== all surviving configs, ranked by mean monthly ===")
        s = res[res.survived].sort_values("mean_mo", ascending=False).head(15)
        for _, r in s.iterrows():
            print(f"  {r.label:<10} risk {100*r.risk:.2f}% heat {100*r.heat:.0f}%  "
                  f"mean/mo {100*r.mean_mo:+6.2f}%  worst {100*r.worst_mo:+6.2f}%  "
                  f"pos {100*r.pos_mo:.0f}%  >=10% {100*r.ge10:.0f}%  "
                  f"CAGR {100*r.cagr:>6.0f}%  maxDD {100*r.maxDD:.0f}%")
