"""The two questions that remain, answered on the same signals.

Q1. With FULL hindsight, what is the maximum monthly return achievable while
    surviving every Breakout rule for the whole span? Fine risk sweep until the
    account first fails to survive. This isolates how much of the ceiling is
    imposed by the rules rather than by the edge.

Q2. Own money, no prop rules: no 3% daily limit, no 6% floor, ruin only at
    total loss. What leverage delivers 100% every 2-4 months, and what
    drawdown and ruin probability comes with it?

Both are reported for the in-sample-optimised signal (the retrospective that was
asked for) and for the honest walk-forward signal, side by side.
"""
import os
import sys
import json

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dataset as DS      # noqa: E402
import hifreq as HF       # noqa: E402
import hifreq2 as H2      # noqa: E402
import validate as V      # noqa: E402


def breakout_frontier(T, label, lo=0.0005, hi=0.03, heats=(0.01, 0.02, 0.03)):
    """Largest risk that survives all Breakout rules, and its monthly return."""
    rows = []
    for heat in heats:
        best = None
        for risk in np.geomspace(lo, hi, 26):
            if risk > heat:
                continue
            curve, breach, mo = V.account_run(T, risk, heat)
            if len(mo) < 12:
                continue
            if breach is None:
                if best is None or mo.mean() > best["mean_mo"]:
                    best = {"risk": risk, "heat": heat, "mean_mo": float(mo.mean()),
                            "med_mo": float(mo.median()), "worst_mo": float(mo.min()),
                            "pos": float((mo > 0).mean()),
                            "ge10": float((mo >= 0.10).mean()),
                            "ge10_2mo": float((mo.rolling(2).sum() >= 0.10).mean()),
                            "total": float(curve.equity.iloc[-1] / 1e5 - 1)}
        if best:
            rows.append({"label": label, **best})
    return pd.DataFrame(rows)


def own_money(T, label, risks=(0.01, 0.02, 0.03, 0.05, 0.075, 0.10, 0.15),
              heat=0.30, start=100_000.0):
    """No daily limit, no static floor. Compounding, ruin only at wipeout."""
    out = []
    for risk in risks:
        eq = start
        live = []
        curve = []
        ruined = None
        for _, t in T.iterrows():
            ts = t.entry_dt
            live.sort(key=lambda x: x[0])
            while live and live[0][0] <= ts:
                xd, ra, r, sc = live.pop(0)
                eq += ra * r * sc
                curve.append((xd, eq))
                if eq <= start * 0.01:
                    ruined = xd
                    break
            if ruined:
                break
            live = [x for x in live if x[0] > ts]
            if sum(x[1] for x in live) / max(eq, 1e-9) + risk > heat:
                continue
            lev = 5.0 if t.symbol in ("BTCUSDT", "ETHUSDT") else 2.0
            ra = eq * risk
            notional = ra / max(t.stop_pct, 1e-9)
            live.append((t.exit_dt, ra, t.r, min(1.0, (eq * lev) / notional)))
        if not ruined:
            live.sort(key=lambda x: x[0])
            for xd, ra, r, sc in live:
                eq += ra * r * sc
                curve.append((xd, eq))
        if len(curve) < 20:
            continue
        c = pd.DataFrame(curve, columns=["dt", "eq"]).set_index("dt")["eq"]
        peak = c.cummax()
        dd = float(((peak - c) / peak).max())
        mo = c.resample("ME").last().pct_change().dropna()
        yrs = (c.index[-1] - c.index[0]).days / 365.25
        tot = c.iloc[-1] / start - 1
        # months to first double, and how often a rolling 3-month window doubles
        roll3 = c.resample("ME").last().pct_change(3).dropna()
        out.append({"label": label, "risk": risk, "ruined": ruined is not None,
                    "total": tot, "final_mult": c.iloc[-1] / start,
                    "cagr": (1 + tot) ** (1 / yrs) - 1 if tot > -1 and yrs > 0 else np.nan,
                    "maxDD": dd, "mean_mo": float(mo.mean()),
                    "med_mo": float(mo.median()), "worst_mo": float(mo.min()),
                    "p_3mo_double": float((roll3 >= 1.0).mean()),
                    "med_3mo": float(roll3.median())})
    return pd.DataFrame(out)


def get_signals(tf="30min", hold=96, k=16):
    d = DS.build(tf=tf, hold=hold)
    feats = DS.feature_list(d)
    sig = {}
    for mode in ("IS", "WF"):
        pl, _ = HF.fit_predict(d, feats, "r_long", mode=mode)
        ps, _ = HF.fit_predict(d, feats, "r_short", mode=mode)
        score = np.where(pl >= ps, pl, ps)
        side = np.where(pl >= ps, 1, -1)
        keep = HF.select_daily_topk(d, score, side, k)
        sig[mode] = H2.to_trades(d, keep, side, tf)
    return sig, d


def main():
    sig, d = get_signals()
    print("=" * 90)
    print("Q1  Maximum monthly return that SURVIVES every Breakout rule")
    print("=" * 90)
    for mode, T in sig.items():
        if len(T) < 200:
            continue
        f = breakout_frontier(T, f"30m {mode}")
        if not len(f):
            print(f"  30m {mode}: no risk level survived the whole span")
            continue
        b = f.loc[f.mean_mo.idxmax()]
        print(f"  30m {mode:<3} expR {T.r.mean():+.3f} -> max surviving "
              f"risk {100*b.risk:.3f}% heat {100*b.heat:.0f}%  "
              f"mean {100*b.mean_mo:+.2f}%/mo  median {100*b.med_mo:+.2f}%  "
              f"worst {100*b.worst_mo:+.2f}%  pos {100*b.pos:.0f}%  "
              f">=10% in {100*b.ge10:.0f}% of months, "
              f"{100*b.ge10_2mo:.0f}% of 2-month windows")

    print("\n" + "=" * 90)
    print("Q2  Own money: no daily limit, no static floor, ruin only at wipeout")
    print("=" * 90)
    for mode, T in sig.items():
        if len(T) < 200:
            continue
        o = own_money(T, f"30m {mode}")
        if not len(o):
            continue
        print(f"\n  --- 30m {mode} (expR {T.r.mean():+.3f}) ---")
        print(f"  {'risk':>6}{'ruined':>8}{'final x':>11}{'CAGR':>9}{'maxDD':>8}"
              f"{'mean/mo':>9}{'worst/mo':>10}{'med 3mo':>9}{'P(3mo 2x)':>11}")
        for _, r in o.iterrows():
            print(f"{100*r.risk:>5.1f}%{str(r.ruined):>8}{r.final_mult:>11.2f}"
                  f"{100*r.cagr:>8.0f}%{100*r.maxDD:>7.0f}%{100*r.mean_mo:>8.2f}%"
                  f"{100*r.worst_mo:>9.2f}%{100*r.med_3mo:>8.0f}%"
                  f"{100*r.p_3mo_double:>10.0f}%")

    rep = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reports")
    for mode, T in sig.items():
        T.to_parquet(os.path.join(rep, f"trades_30m_{mode}.parquet"), index=False)


if __name__ == "__main__":
    main()
