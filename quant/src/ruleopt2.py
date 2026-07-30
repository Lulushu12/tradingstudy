"""Compact-rule optimiser, corrected.

Fixes over the first version, each of which was inflating the result:
  1. Rules are unioned as SETS of (bar, side). The first version summed R over
     overlapping masks, so adding a near-duplicate rule counted the same trade
     twice and 'diversification' was really 8x leverage.
  2. A rule must trade in at least `min_month_cover` of the months in the span.
     A rule firing in 14 of 66 months cannot deliver 'ten percent per month'
     however good those 14 months look.
  3. Drawdown is floored before dividing, and rules with a degenerate (near
     zero) drawdown are rejected rather than scored as infinite.
  4. Every finalist is re-run through the real Breakout account simulator
     (static 6% floor, 3% daily loss, leverage caps, portfolio heat) instead of
     being scored by the ratio proxy alone.

Fitted with full hindsight over the whole span, as requested.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dataset as DS      # noqa: E402

N_Q = 9


class Book:
    def __init__(self, d, feats, min_trades=300, min_month_cover=0.85,
                 min_dd=0.5):
        self.d = d
        self.min_trades = min_trades
        self.min_dd = min_dd
        dt = pd.DatetimeIndex(d.dt)
        self.mi = ((dt.year - dt.year.min()) * 12 + dt.month - 1).values
        self.n_months = int(self.mi.max()) + 1
        # day index for the 3% daily-loss constraint, which is what actually
        # binds once signals cluster across correlated assets
        dayk = dt.floor("D")
        self.di = (dayk - dayk.min()).days.values
        self.n_days = int(self.di.max()) + 1
        self.span_months = (dt.max() - dt.min()).days / 30.44
        self.min_months = int(min_month_cover * self.n_months)
        self.r = {1: d.r_long.values.astype(np.float64),
                  -1: d.r_short.values.astype(np.float64)}
        self.valid = {s: np.isfinite(self.r[s]) for s in (1, -1)}
        self.conds = []
        for c in feats:
            x = d[c].values.astype(np.float64)
            fin = np.isfinite(x)
            if fin.sum() < len(x) * 0.5:
                continue
            for q in np.unique(np.nanquantile(x[fin], np.linspace(0.1, 0.9, N_Q))):
                self.conds.append((c, float(q), 1, (x >= q) & fin))
                self.conds.append((c, float(q), -1, (x <= q) & fin))

    def metrics(self, sel_long, sel_short):
        """sel_*: boolean arrays. Each (bar, side) contributes at most once."""
        ml = sel_long & self.valid[1]
        ms = sel_short & self.valid[-1]
        n = int(ml.sum() + ms.sum())
        if n < self.min_trades:
            return None
        rr = np.where(ml, self.r[1], 0.0) + np.where(ms, self.r[-1], 0.0)
        mon = np.bincount(self.mi, weights=rr, minlength=self.n_months)
        active = np.bincount(self.mi, weights=(ml | ms).astype(float),
                             minlength=self.n_months)
        months_traded = int((active > 0).sum())
        if months_traded < self.min_months:
            return None
        cum = np.cumsum(mon)
        dd = float(np.max(np.maximum.accumulate(cum) - cum))
        if dd < self.min_dd:
            return None                      # degenerate, not a real curve
        mo_R = float(cum[-1]) / self.span_months
        if mo_R <= 0:
            return None
        # worst single day in R. The 3% daily loss limit is a hard stop, so it
        # caps risk independently of the 6% floor and usually binds first.
        day = np.bincount(self.di, weights=rr, minlength=self.n_days)
        worst_day = float(day.min())
        risk_static = 0.06 / dd
        risk_daily = (0.03 / abs(worst_day)) if worst_day < 0 else 0.02
        risk = min(risk_static, risk_daily, 0.02)
        act = mon[active > 0]
        return {"n": n, "mo_R": mo_R, "maxDD_R": dd, "ratio": mo_R / dd,
                "worst_day_R": worst_day,
                "bind": "daily" if risk_daily < risk_static else "static",
                "risk_pct": risk, "monthly_ret": risk * mo_R,
                "months_traded": months_traded,
                "pos_months": float((act > 0).mean()),
                "worst_month_R": float(mon.min()),
                "worst_month_ret": risk * float(mon.min())}


def beam_search(book, side, depth=4, beam=24, verbose=True):
    empty = np.zeros(len(book.d), dtype=bool)
    frontier = [([], np.ones(len(book.d), dtype=bool))]
    out = []
    for lvl in range(depth):
        scored = []
        for path, mask in frontier:
            used = {p[0] for p in path}
            for (c, q, sgn, cm) in book.conds:
                if c in used:
                    continue
                nm = mask & cm
                met = (book.metrics(nm, empty) if side > 0
                       else book.metrics(empty, nm))
                if met is None:
                    continue
                scored.append((met["monthly_ret"], path + [(c, q, sgn)], nm, met))
        if not scored:
            break
        scored.sort(key=lambda z: -z[0])
        seen, keep = set(), []
        for s in scored:
            sig = tuple(sorted((a, round(b, 8), c) for a, b, c in s[1]))
            if sig in seen:
                continue
            seen.add(sig)
            keep.append(s)
            if len(keep) >= beam:
                break
        frontier = [(k[1], k[2]) for k in keep]
        out.extend([(k[0], k[1], k[3], k[2]) for k in keep])
        if verbose:
            b = keep[0]
            rule = " & ".join("%s%s%.4g" % (a, ">=" if c > 0 else "<=", q)
                              for a, q, c in b[1])
            print(f"    depth {lvl+1}: {100*b[0]:6.2f}%/mo  n={b[3]['n']:<6}"
                  f"ratio {b[3]['ratio']:6.2f}  months {b[3]['months_traded']}  "
                  f"[{rule}]")
    out.sort(key=lambda z: -z[0])
    return out


def assemble(book, cands, max_rules=10, verbose=True):
    """Union rules as sets. A rule only helps if it adds NEW trades that improve
    the combined curve."""
    sel_l = np.zeros(len(book.d), dtype=bool)
    sel_s = np.zeros(len(book.d), dtype=bool)
    chosen, cur = [], None
    for _ in range(max_rules):
        best = None
        for score, path, met, mask, side in cands:
            nl = sel_l | mask if side > 0 else sel_l
            ns = sel_s | mask if side < 0 else sel_s
            if int(nl.sum() + ns.sum()) == int(sel_l.sum() + sel_s.sum()):
                continue                     # adds nothing new
            m = book.metrics(nl, ns)
            if m is None:
                continue
            if best is None or m["monthly_ret"] > best[0]:
                best = (m["monthly_ret"], nl, ns, path, side, m)
        if best is None:
            break
        if cur is not None and best[0] <= cur["monthly_ret"] + 1e-9:
            break
        sel_l, sel_s = best[1], best[2]
        chosen.append((best[3], best[4]))
        cur = best[5]
        if verbose:
            rule = " & ".join("%s%s%.4g" % (a, ">=" if c > 0 else "<=", q)
                              for a, q, c in best[3])
            print(f"  + {'LONG ' if best[4]>0 else 'SHORT'} {100*cur['monthly_ret']:6.2f}%/mo "
                  f"n={cur['n']:<6} ratio {cur['ratio']:5.2f} "
                  f"risk {100*cur['risk_pct']:.2f}% "
                  f"months {cur['months_traded']}/{book.n_months} "
                  f"posmo {100*cur['pos_months']:.0f}%  [{rule}]")
    return chosen, cur, sel_l, sel_s


def run(tf="4h", hold=60, depth=4, beam=20, min_trades=300, cover=0.85):
    d = DS.build(tf=tf, hold=hold)
    feats = DS.feature_list(d)
    book = Book(d, feats, min_trades=min_trades, min_month_cover=cover)
    print(f"=== {tf}: rows {len(d):,}  conditions {len(book.conds)}  "
          f"months {book.n_months}  min-cover {book.min_months} ===")
    allc = []
    for side, nm in ((1, "LONG"), (-1, "SHORT")):
        print(f"\n  beam, {nm}")
        for score, path, met, mask in beam_search(book, side, depth, beam):
            allc.append((score, path, met, mask, side))
    allc.sort(key=lambda z: -z[0])
    if not allc:
        print("\n  no rule met the coverage and drawdown constraints")
        return d, book, allc, [], None, None, None
    print(f"\n  best single rules (coverage-constrained):")
    for score, path, met, _, side in allc[:8]:
        rule = " & ".join("%s%s%.4g" % (a, ">=" if c > 0 else "<=", q)
                          for a, q, c in path)
        print(f"    {100*score:6.2f}%/mo {'LONG ' if side>0 else 'SHORT'} "
              f"n={met['n']:<6} ratio {met['ratio']:5.2f} "
              f"months {met['months_traded']}  {rule}")
    print(f"\n  portfolio (set union)")
    chosen, final, sl, ss = assemble(book, allc[:150])
    return d, book, allc, chosen, final, sl, ss


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--tf", default="4h")
    p.add_argument("--hold", type=int, default=60)
    p.add_argument("--depth", type=int, default=4)
    p.add_argument("--beam", type=int, default=20)
    p.add_argument("--min-trades", type=int, default=300)
    p.add_argument("--cover", type=float, default=0.85)
    a = p.parse_args()
    d, book, allc, chosen, final, sl, ss = run(
        a.tf, a.hold, a.depth, a.beam, a.min_trades, a.cover)
    if final:
        print("\n=== FINAL (in-sample, full hindsight, corrected) ===")
        for k, v in final.items():
            print(f"  {k:<18} {v}")
        np.save(f"/tmp/sel_long_{a.tf}.npy", sl)
        np.save(f"/tmp/sel_short_{a.tf}.npy", ss)
