"""Account-level evaluation under Breakout 1-Step Classic.

A single equity curve over 5 years answers the wrong question. A prop account
starts on one specific day and either reaches +10% or dies. So: start an account
on every candidate date, run it forward, and report the DISTRIBUTION of
outcomes. That is what 'can this make 10% in a month' actually means.

Also enforces what the earlier sim ignored: these 5 assets are highly
correlated, so simultaneous positions are one bet wearing five hats. Portfolio
heat (total risk live at once) is capped, not just the position count.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import candidate as C     # noqa: E402
import engine as E        # noqa: E402

SYMS = C.SYMS


def build_trades(rule, tf="4h", atr_mult=2.0, rr=2.0, hold=60, block="DESIGN",
                 unlock=None):
    allt = []
    for sym in SYMS:
        f, lb = C.prep(sym, tf, block, atr_mult, rr, hold, unlock=unlock)
        lm, sm = C.rules(f)[rule]
        t = C.trades_for(f, lb, lm, sm)
        if len(t):
            t["symbol"] = sym
            allt.append(t)
    T = pd.concat(allt).sort_values("entry_dt").reset_index(drop=True)
    T["entry_dt"] = pd.to_datetime(T["entry_dt"], utc=True)
    T["exit_dt"] = pd.to_datetime(T["exit_dt"], utc=True)
    return T


def run_account(T, start, days, risk_pct, max_heat, start_eq=100_000.0,
                target=0.10, max_dd=0.06, daily=0.03):
    """One account. Returns (outcome, final_return, days_taken).
    outcome in {'pass','bust_static','bust_daily','timeout'}"""
    end = start + pd.Timedelta(days=days)
    sub = T[(T.entry_dt >= start) & (T.entry_dt < end)]
    if len(sub) == 0:
        return "timeout", 0.0, days

    eq = start_eq
    floor = start_eq * (1 - max_dd)
    day_anchor = None
    day_eq = start_eq
    live = []          # (exit_dt, risk_amt, r, scale)

    events = []
    for _, t in sub.iterrows():
        events.append((t.entry_dt, "in", t))
    events.sort(key=lambda e: e[0])

    for ts, _, t in events:
        # settle exits first
        live.sort(key=lambda x: x[0])
        while live and live[0][0] <= ts:
            xd, ra, r, sc = live.pop(0)
            eq += ra * r * sc
            if eq <= floor:
                return "bust_static", eq / start_eq - 1, (xd - start).days
            if eq <= day_eq * (1 - daily):
                return "bust_daily", eq / start_eq - 1, (xd - start).days
            if eq >= start_eq * (1 + target):
                return "pass", eq / start_eq - 1, (xd - start).days

        anchor = pd.Timestamp(ts).normalize() + pd.Timedelta(minutes=30)
        if pd.Timestamp(ts) < anchor:
            anchor -= pd.Timedelta(days=1)
        if day_anchor is None or anchor > day_anchor:
            day_anchor, day_eq = anchor, eq

        live = [x for x in live if x[0] > ts]
        heat = sum(x[1] for x in live) / eq
        if heat + risk_pct > max_heat:
            continue

        lev = E.MAX_LEV.get(t.symbol, E.DEFAULT_LEV)
        ra = eq * risk_pct
        notional = ra / max(t.stop_pct, 1e-9)
        scale = min(1.0, (eq * lev) / notional)
        live.append((t.exit_dt, ra, t.r, scale))

    live.sort(key=lambda x: x[0])
    for xd, ra, r, sc in live:
        eq += ra * r * sc
        if eq <= floor:
            return "bust_static", eq / start_eq - 1, days
        if eq >= start_eq * (1 + target):
            return "pass", eq / start_eq - 1, (xd - start).days
    return "timeout", eq / start_eq - 1, days


def sweep(T, days=30, step_days=3):
    starts = pd.date_range(T.entry_dt.min(), T.entry_dt.max() - pd.Timedelta(days=days),
                           freq=f"{step_days}D", tz="UTC")
    print(f"accounts simulated per config: {len(starts)}  "
          f"(rolling {days}-day windows, every {step_days} days)")
    print(f"\n{'risk':>6}{'heat':>7}{'P(pass)':>9}{'P(bust)':>9}"
          f"{'P(time)':>9}{'mean ret':>10}{'median':>9}{'p5':>8}{'p95':>8}")
    rows = []
    for risk in (0.0025, 0.005, 0.0075, 0.01, 0.015, 0.02, 0.03):
        for heat in (0.02, 0.04, 0.06):
            if heat < risk:
                continue
            res = [run_account(T, s, days, risk, heat) for s in starts]
            oc = pd.Series([r[0] for r in res])
            rt = pd.Series([r[1] for r in res])
            row = {"risk": risk, "heat": heat,
                   "p_pass": float((oc == "pass").mean()),
                   "p_bust": float(oc.str.startswith("bust").mean()),
                   "p_time": float((oc == "timeout").mean()),
                   "mean": float(rt.mean()), "median": float(rt.median()),
                   "p5": float(rt.quantile(0.05)), "p95": float(rt.quantile(0.95))}
            rows.append(row)
            print(f"{100*risk:>5.2f}%{100*heat:>6.1f}%{100*row['p_pass']:>8.1f}%"
                  f"{100*row['p_bust']:>8.1f}%{100*row['p_time']:>8.1f}%"
                  f"{100*row['mean']:>9.2f}%{100*row['median']:>8.2f}%"
                  f"{100*row['p5']:>7.2f}%{100*row['p95']:>7.2f}%")
    return pd.DataFrame(rows)


def stability(T):
    """Per-year and per-asset expectancy with block-bootstrap CI."""
    import labels as L
    print("\n--- edge stability ---")
    T2 = T.copy()
    T2["year"] = T2.entry_dt.dt.year
    print(f"{'year':>6}{'n':>7}{'expR':>9}{'95% CI':>22}")
    for y, g in T2.groupby("year"):
        mu, lo, hi = L.block_bootstrap(g.r.values, n_boot=1500, block=20)
        print(f"{y:>6}{len(g):>7}{g.r.mean():>9.3f}   [{lo:+.3f}, {hi:+.3f}]")
    print(f"\n{'symbol':>10}{'n':>7}{'expR':>9}{'95% CI':>22}")
    for s, g in T2.groupby("symbol"):
        mu, lo, hi = L.block_bootstrap(g.r.values, n_boot=1500, block=20)
        print(f"{s:>10}{len(g):>7}{g.r.mean():>9.3f}   [{lo:+.3f}, {hi:+.3f}]")
    mu, lo, hi = L.block_bootstrap(T2.r.values, n_boot=3000, block=20)
    print(f"\npooled expR {T2.r.mean():+.4f}  95% CI [{lo:+.4f}, {hi:+.4f}]  n={len(T2)}")
    print(f"win rate {float((T2.outcome==1).mean()):.3f}  "
          f"timeouts {float((T2.outcome==0).mean()):.3f}")


def main():
    T = build_trades("vol_spike_cont")
    print(f"vol_spike_cont: {len(T)} trades, "
          f"{T.entry_dt.min()} -> {T.entry_dt.max()}")
    stability(T)
    print("\n=== 30-day account outcomes (Breakout 1-Step Classic) ===")
    r30 = sweep(T, days=30, step_days=3)
    rep = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reports")
    r30.to_csv(os.path.join(rep, "account_30d.csv"), index=False)
    print("\n=== 60-day windows (no time limit on Breakout evaluations) ===")
    r60 = sweep(T, days=60, step_days=5)
    r60.to_csv(os.path.join(rep, "account_60d.csv"), index=False)


if __name__ == "__main__":
    main()
