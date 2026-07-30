"""Build and honestly evaluate the best surviving system.

Candidate set is PRE-REGISTERED and deliberately tiny, because after the wide
search above, every extra hypothesis tested here is a fresh chance to fool
myself. Six rules, fixed in advance, no per-asset tuning, no threshold search:
each rule is either a plain sign condition or a fixed quantile of its own
trailing distribution.

Selection happens on BTC TRAIN only. TEST and the other four assets are the
out-of-sample check. HOLDOUT stays sealed.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data as D          # noqa: E402
import engine as E        # noqa: E402
import features as F      # noqa: E402
import labels as L        # noqa: E402

SYMS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT"]


# ------------------------------------------------------------------ candidates
def rules(f):
    """dict name -> (long_mask, short_mask). Pre-registered, no free parameters
    beyond the fixed quantiles stated here."""
    out = {}

    # R1 sustained aggressor imbalance (the one cell that ever beat a null)
    out["flow_persist"] = (f.tbi_ma96 > 0, f.tbi_ma96 < 0)

    # R2 volume-spike trend continuation (the prior study's finding, re-tested
    # independently here with a stricter engine)
    vspike = f.trade_intensity > 1.8
    out["vol_spike_cont"] = (vspike & (f.disp96 > 0) & (f.ret > 0),
                             vspike & (f.disp96 < 0) & (f.ret < 0))

    # R3 range position extremes
    out["range_pos"] = (f.pos480 > 0.8, f.pos480 < 0.2)

    # R4 momentum displacement
    out["displacement"] = (f.disp96 > 2, f.disp96 < -2)

    # R5 low-volatility regime continuation
    lowvol = f.atr_rank < 0.4
    out["lowvol_cont"] = (lowvol & (f.disp96 > 0), lowvol & (f.disp96 < 0))

    # R6 absorption reversal: heavy one-sided flow that failed to move price
    out["absorption_rev"] = (f.absorb_z < -1.5, f.absorb_z > 1.5)
    return out


def prep(symbol, tf, block, atr_mult, rr, hold, unlock=None):
    bars, m1 = D.load(symbol, tf, block, unlock=unlock)
    f = F.build(bars, m1, tf)
    lb = L.make(symbol, tf, block, atr_mult=atr_mult, rr=rr,
                max_hold_bars=hold, unlock=unlock)
    f = f[f["tradeable"]].reset_index(drop=True)
    kf = f["dt"].astype("int64").values
    kl = lb["dt"].astype("int64").values
    common = np.intersect1d(kf, kl)
    f = f[np.isin(kf, common)].reset_index(drop=True)
    lb = lb[np.isin(kl, common)].reset_index(drop=True)
    return f, lb


def eval_rule(f, lb, lm, sm):
    lm = np.asarray(lm.fillna(False), bool)
    sm = np.asarray(sm.fillna(False), bool)
    rl = lb["r_long"].values.astype(float)
    rs = lb["r_short"].values.astype(float)
    r = np.concatenate([rl[lm & np.isfinite(rl)], rs[sm & np.isfinite(rs)]])
    if len(r) < 40:
        return {"n": len(r), "exp_r": np.nan, "sh": np.nan}
    return {"n": len(r), "exp_r": float(r.mean()),
            "sh": float(r.mean() / r.std(ddof=0)) if r.std(ddof=0) > 0 else np.nan}


def trades_for(f, lb, lm, sm):
    """Materialise the trade list for a rule so it can go through the account sim."""
    lm = np.asarray(lm.fillna(False), bool)
    sm = np.asarray(sm.fillna(False), bool)
    rows = []
    for mask, side, rc, oc, hc, sc, ec in (
            (lm, 1, "r_long", "out_long", "hold_long", "stoppct_long", "exit_long"),
            (sm, -1, "r_short", "out_short", "hold_short", "stoppct_short", "exit_short")):
        sel = mask & np.isfinite(lb[rc].values.astype(float))
        if sel.sum() == 0:
            continue
        rows.append(pd.DataFrame({
            "entry_dt": lb["dt"].values[sel],
            "exit_dt": lb[ec].values[sel],
            "side": side,
            "r": lb[rc].values[sel],
            "outcome": lb[oc].values[sel],
            "stop_pct": lb[sc].values[sel],
        }))
    if not rows:
        return pd.DataFrame()
    return pd.concat(rows).sort_values("entry_dt").reset_index(drop=True)


def main(tf="4h", atr_mult=2.0, rr=2.0, hold=60):
    print(f"### candidate evaluation  tf={tf} atr={atr_mult} rr={rr} hold={hold}")
    print("\n--- STEP 1: rule selection on BTC TRAIN only ---")
    f, lb = prep("BTCUSDT", tf, "TRAIN", atr_mult, rr, hold)
    R = rules(f)
    base = np.nanmean(np.concatenate([lb.r_long.values, lb.r_short.values]))
    print(f"baseline expR = {base:+.4f}")
    sel = {}
    for name, (lm, sm) in R.items():
        s = eval_rule(f, lb, lm, sm)
        print(f"  {name:<18} n={s['n']:>6}  expR {s['exp_r']:+.4f}  "
              f"per-trade Sharpe {s['sh']:+.3f}")
        sel[name] = s

    print("\n--- STEP 2: same rules, BTC TEST (out-of-sample in time) ---")
    f2, lb2 = prep("BTCUSDT", tf, "TEST", atr_mult, rr, hold)
    R2 = rules(f2)
    for name, (lm, sm) in R2.items():
        s = eval_rule(f2, lb2, lm, sm)
        print(f"  {name:<18} n={s['n']:>6}  expR {s['exp_r']:+.4f}")

    print("\n--- STEP 3: same rules, OTHER 4 ASSETS (structural out-of-sample) ---")
    print(f"{'rule':<18}" + "".join(f"{s.replace('USDT',''):>12}" for s in SYMS[1:])
          + f"{'pooled':>12}")
    pooled = {}
    for name in R:
        cells, allr = [], []
        for sym in SYMS[1:]:
            try:
                fs, ls_ = prep(sym, tf, "DESIGN", atr_mult, rr, hold)
            except Exception:
                cells.append(np.nan)
                continue
            Rs = rules(fs)
            lm, sm = Rs[name]
            s = eval_rule(fs, ls_, lm, sm)
            cells.append(s["exp_r"])
            lmb = np.asarray(lm.fillna(False), bool)
            smb = np.asarray(sm.fillna(False), bool)
            rl = ls_["r_long"].values.astype(float)
            rs_ = ls_["r_short"].values.astype(float)
            allr.append(np.concatenate([rl[lmb & np.isfinite(rl)],
                                        rs_[smb & np.isfinite(rs_)]]))
        p = float(np.concatenate(allr).mean()) if allr else np.nan
        pooled[name] = p
        print(f"{name:<18}" + "".join(f"{c:>12.4f}" for c in cells) + f"{p:>12.4f}")

    print("\n--- STEP 4: Breakout account simulation, best rule, 5-asset portfolio ---")
    ranked = sorted(pooled.items(), key=lambda kv: (-kv[1] if np.isfinite(kv[1]) else 1))
    for name, p in ranked[:3]:
        if not np.isfinite(p) or p <= 0:
            print(f"  {name}: pooled expR {p:+.4f} -> not viable, skipped")
            continue
        allt = []
        for sym in SYMS:
            fs, ls_ = prep(sym, tf, "DESIGN", atr_mult, rr, hold)
            lm, sm = rules(fs)[name]
            t = trades_for(fs, ls_, lm, sm)
            if len(t):
                t["symbol"] = sym
                allt.append(t)
        T = pd.concat(allt).sort_values("entry_dt").reset_index(drop=True)
        print(f"\n  rule={name}  pooled expR {p:+.4f}  total signals {len(T)}  "
              f"({len(T)/66:.1f}/month across 5 assets)")
        for risk in (0.005, 0.01, 0.02):
            for conc in (3, 5):
                stats, curve = E.simulate(T, risk_pct=risk, max_concurrent=conc,
                                          symbol="BTCUSDT")
                if stats["n"] == 0:
                    continue
                mo = E.monthly(curve)
                print(f"    risk {100*risk:>4.1f}%  slots {conc}: "
                      f"n={stats['n']:>5}  expR {stats['exp_r']:+.3f}  "
                      f"total {100*stats['total_ret']:>+8.1f}%  "
                      f"maxDD {100*stats['max_dd']:>5.1f}%  "
                      f"mean/mo {100*mo.mean():>+6.2f}%  "
                      f"months>=10% {100*(mo>=0.10).mean():>4.0f}%  "
                      f"breach={stats['breached']}")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--tf", default="4h")
    p.add_argument("--atr", type=float, default=2.0)
    p.add_argument("--rr", type=float, default=2.0)
    p.add_argument("--hold", type=int, default=60)
    a = p.parse_args()
    main(a.tf, a.atr, a.rr, a.hold)
