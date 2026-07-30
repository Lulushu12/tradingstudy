"""Take a rule set from the optimiser and run it through the REAL account sim.

The optimiser scores rules with a ratio proxy that assumes every signal can be
taken at full size. The actual Breakout account cannot do that: there is a 3%
daily loss limit, a static floor that ends the account permanently, leverage
caps, and finite portfolio heat. This re-runs the finalists under those rules
and reports what the account would actually have done, month by month.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dataset as DS      # noqa: E402
import engine as E        # noqa: E402

TF_DELTA = {"4h": "4h", "1h": "1h", "30min": "30min", "15min": "15min"}


def rules_to_trades(d, rulespecs, tf="4h"):
    """rulespecs: list of (path, side) where path is [(feature, thr, sign), ...]"""
    step = pd.Timedelta(TF_DELTA[tf])
    sel = {1: np.zeros(len(d), bool), -1: np.zeros(len(d), bool)}
    for path, side in rulespecs:
        m = np.ones(len(d), bool)
        for (c, q, sgn) in path:
            x = d[c].values.astype(float)
            m &= ((x >= q) if sgn > 0 else (x <= q)) & np.isfinite(x)
        sel[side] |= m

    parts = []
    for side, rc, oc, ec, sc in ((1, "r_long", "out_long", "exit_long", "stoppct_long"),
                                 (-1, "r_short", "out_short", "exit_short", "stoppct_short")):
        m = sel[side] & np.isfinite(d[rc].values)
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
    T = pd.concat(parts).sort_values("entry_dt").reset_index(drop=True)
    T = T[T.exit_dt > T.entry_dt].reset_index(drop=True)
    return T, sel


def account_run(T, risk, heat, start_eq=100_000.0, max_dd=0.06, daily=0.03,
                enforce=True):
    """Full Breakout simulation. Returns (equity curve, breach, monthly returns)."""
    eq = start_eq
    floor = start_eq * (1 - max_dd)
    live = []
    day_anchor, day_eq = None, start_eq
    rows, breach = [], None

    for _, t in T.iterrows():
        ts = t.entry_dt
        live.sort(key=lambda x: x[0])
        while live and live[0][0] <= ts:
            xd, ra, r, sc = live.pop(0)
            eq += ra * r * sc
            rows.append({"dt": xd, "equity": eq})
            if enforce:
                if eq <= floor:
                    breach = ("static_dd", xd)
                    break
                if eq <= day_eq * (1 - daily):
                    breach = ("daily_loss", xd)
                    break
        if breach:
            break
        anchor = pd.Timestamp(ts).normalize() + pd.Timedelta(minutes=30)
        if pd.Timestamp(ts) < anchor:
            anchor -= pd.Timedelta(days=1)
        if day_anchor is None or anchor > day_anchor:
            day_anchor, day_eq = anchor, eq

        live = [x for x in live if x[0] > ts]
        if sum(x[1] for x in live) / eq + risk > heat:
            continue
        lev = E.MAX_LEV.get(t.symbol, E.DEFAULT_LEV)
        ra = eq * risk
        notional = ra / max(t.stop_pct, 1e-9)
        live.append((t.exit_dt, ra, t.r, min(1.0, (eq * lev) / notional)))

    if not breach:
        live.sort(key=lambda x: x[0])
        for xd, ra, r, sc in live:
            eq += ra * r * sc
            rows.append({"dt": xd, "equity": eq})
            if enforce and eq <= floor:
                breach = ("static_dd", xd)
                break

    curve = pd.DataFrame(rows)
    if len(curve) == 0:
        return curve, breach, pd.Series(dtype=float)
    c = curve.set_index(pd.DatetimeIndex(curve.dt))["equity"]
    m = c.resample("ME").last().ffill()
    prev = m.shift(1).fillna(start_eq)
    return curve, breach, (m / prev - 1)


def report(T, name, risks=(0.0025, 0.005, 0.0075, 0.01, 0.015), heats=(0.02, 0.04, 0.06)):
    print(f"\n=== {name}: {len(T)} trades, "
          f"{T.entry_dt.min().date()} -> {T.entry_dt.max().date()} ===")
    print(f"raw expR {T.r.mean():+.4f}  win rate {float((T.outcome==1).mean()):.3f}")
    print(f"{'risk':>7}{'heat':>7}{'taken':>7}{'final%':>9}{'CAGR%':>8}"
          f"{'maxDD%':>8}{'mean/mo':>9}{'worst mo':>10}{'>=10%':>7}{'breach':>16}")
    best = None
    for risk in risks:
        for heat in heats:
            if heat < risk:
                continue
            curve, breach, mo = account_run(T, risk, heat)
            if len(curve) == 0:
                continue
            eqs = curve.equity.values
            peak = np.maximum.accumulate(eqs)
            dd = float(((peak - eqs) / peak).max())
            total = eqs[-1] / 100_000 - 1
            yrs = (curve.dt.iloc[-1] - curve.dt.iloc[0]).days / 365.25
            cagr = (1 + total) ** (1 / yrs) - 1 if yrs > 0 and total > -1 else np.nan
            print(f"{100*risk:>6.2f}%{100*heat:>6.1f}%{len(curve):>7}"
                  f"{100*total:>8.1f}%{100*cagr:>7.1f}%{100*dd:>7.1f}%"
                  f"{100*mo.mean():>8.2f}%{100*mo.min():>9.2f}%"
                  f"{100*float((mo>=0.10).mean()):>6.0f}%"
                  f"{str(breach[0]) if breach else '-':>16}")
            if breach is None and (best is None or mo.mean() > best[0]):
                best = (mo.mean(), risk, heat, mo, curve)
    if best:
        mo = best[3]
        print(f"\nbest surviving config: risk {100*best[1]:.2f}% heat {100*best[2]:.1f}%")
        print(f"  mean {100*mo.mean():.2f}%/mo  median {100*mo.median():.2f}%  "
              f"positive {100*float((mo>0).mean()):.0f}%  "
              f">=10% in {100*float((mo>=0.10).mean()):.0f}% of months")
        print("  monthly returns by year:")
        by = mo.groupby(mo.index.year)
        for y, g in by:
            print(f"    {y}: " + " ".join(f"{100*v:+6.1f}" for v in g.values))
    return best


if __name__ == "__main__":
    print("run via findbest.py")
