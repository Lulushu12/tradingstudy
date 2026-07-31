"""Answer the two RELAXED targets directly, on their own terms.

(a) 10% every one-to-two months. Not the same as 'mean 10%/month'. The right
    statistic is the rolling 2-month return: how often it clears 10%, and what
    its WORST value is. Optimising mean monthly return does not optimise this.

(b) 100% every 2-4 months on a venue with no daily-loss rule and no static
    floor. Only real leverage and actual ruin apply.

Every candidate signal is evaluated for both, in-sample and walk-forward.
"""
import os
import sys
import json

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dataset as DS      # noqa: E402
import validate as V      # noqa: E402

REP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reports")


def trades_from_ruleset(path, tf, hold):
    with open(path) as fh:
        spec = json.load(fh)
    d = DS.build(tf=tf, hold=hold)
    rules = [([tuple(c) for c in r["conds"]], r["side"]) for r in spec["rules"]]
    T, _ = V.rules_to_trades(d, rules, tf=tf)
    return T


def unlimited_run(T, risk, heat, start=100_000.0, ruin_at=0.02):
    """No daily limit, no static floor. Ruin only at near-total loss."""
    eq, live, curve, ruined = start, [], [], None
    for _, t in T.iterrows():
        ts = t.entry_dt
        live.sort(key=lambda x: x[0])
        while live and live[0][0] <= ts:
            xd, ra, r, sc = live.pop(0)
            eq += ra * r * sc
            curve.append((xd, eq))
            if eq <= start * ruin_at:
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
            if eq <= start * ruin_at:
                ruined = xd
                break
    if len(curve) < 20:
        return None
    c = pd.DataFrame(curve, columns=["dt", "eq"]).set_index("dt")["eq"]
    return c, ruined


def window_stats(c, start=100_000.0):
    """Rolling multi-month statistics from a (possibly irregular) equity curve."""
    m = c.resample("ME").last().ffill()
    out = {}
    for w in (1, 2, 3, 4):
        rr = m.pct_change(w).dropna()
        if len(rr) == 0:
            continue
        out[w] = {"n": len(rr), "median": float(rr.median()),
                  "mean": float(rr.mean()), "worst": float(rr.min()),
                  "p_ge10": float((rr >= 0.10).mean()),
                  "p_ge100": float((rr >= 1.00).mean())}
    return out


def report_a(T, label):
    """Target (a): 10% per one-to-two months, under full Breakout rules."""
    best = None
    for heat in (0.01, 0.02, 0.03):
        for risk in np.geomspace(0.0005, 0.02, 22):
            if risk > heat:
                continue
            curve, breach, mo = V.account_run(T, risk, heat)
            if breach is not None or len(mo) < 24:
                continue
            c = curve.set_index(pd.DatetimeIndex(curve.dt))["equity"]
            w = window_stats(c)
            if 2 not in w:
                continue
            score = w[2]["p_ge10"]
            if best is None or score > best[0]:
                best = (score, risk, heat, w, mo)
    if best is None:
        print(f"  {label:<22} no config survived Breakout rules")
        return None
    score, risk, heat, w, mo = best
    print(f"  {label:<22} risk {100*risk:.3f}% heat {100*heat:.0f}%  "
          f"mean/mo {100*mo.mean():+5.2f}%")
    print(f"    {'window':>8}{'median':>9}{'worst':>9}{'P(>=10%)':>10}")
    for k in (1, 2, 3):
        if k in w:
            print(f"    {k:>7}mo{100*w[k]['median']:>8.1f}%"
                  f"{100*w[k]['worst']:>8.1f}%{100*w[k]['p_ge10']:>9.0f}%")
    return best


def report_b(T, label):
    """Target (b): 100% every 2-4 months, no venue limits."""
    print(f"\n  --- {label} ---")
    print(f"  {'risk':>6}{'heat':>6}{'ruined':>8}{'final x':>10}{'maxDD':>8}"
          f"{'med 2mo':>9}{'med 3mo':>9}{'med 4mo':>9}{'P(3mo>=100%)':>14}")
    any_ok = False
    for risk in (0.02, 0.05, 0.10, 0.20):
        for heat in (0.10, 0.30):
            res = unlimited_run(T, risk, heat)
            if res is None:
                continue
            c, ruined = res
            w = window_stats(c)
            peak = c.cummax()
            dd = float(((peak - c) / peak).max())
            ok3 = w.get(3, {}).get("p_ge100", 0.0)
            print(f"{100*risk:>5.0f}%{100*heat:>5.0f}%{str(bool(ruined)):>8}"
                  f"{c.iloc[-1]/1e5:>10.2f}{100*dd:>7.0f}%"
                  f"{100*w.get(2,{}).get('median',float('nan')):>8.0f}%"
                  f"{100*w.get(3,{}).get('median',float('nan')):>8.0f}%"
                  f"{100*w.get(4,{}).get('median',float('nan')):>8.0f}%"
                  f"{100*ok3:>13.0f}%")
            if not ruined and dd < 0.60 and ok3 >= 0.5:
                any_ok = True
    return any_ok


def main():
    cands = {}
    p30is = os.path.join(REP, "trades_30m_IS.parquet")
    p30wf = os.path.join(REP, "trades_30m_WF.parquet")
    if os.path.exists(p30is):
        cands["30m IS"] = pd.read_parquet(p30is)
    if os.path.exists(p30wf):
        cands["30m WF"] = pd.read_parquet(p30wf)
    for tag, tf, hold in (("1h", "1h", 96), ("4h_daily", "4h", 60)):
        f = os.path.join(REP, f"ruleset_{tag}.json")
        if os.path.exists(f):
            try:
                cands[f"{tag} rules IS"] = trades_from_ruleset(f, tf, hold)
            except Exception as e:
                print(f"skip {tag}: {e}")

    for k, T in cands.items():
        T["entry_dt"] = pd.to_datetime(T["entry_dt"], utc=True)
        T["exit_dt"] = pd.to_datetime(T["exit_dt"], utc=True)

    print("=" * 84)
    print("TARGET (a)  10% per one-to-two months, under full Breakout rules")
    print("            config chosen to MAXIMISE P(2-month return >= 10%)")
    print("=" * 84)
    for k, T in cands.items():
        report_a(T, k)

    print("\n" + "=" * 84)
    print("TARGET (b)  100% every 2-4 months, no daily limit, no static floor")
    print("=" * 84)
    ok = False
    for k, T in cands.items():
        ok |= bool(report_b(T, k))
    print(f"\n  any config meeting (b) without ruin and with maxDD < 60%: {ok}")


if __name__ == "__main__":
    main()
