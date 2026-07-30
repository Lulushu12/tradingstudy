"""Compact-rule optimiser: search conjunctions of feature thresholds that
maximise the implied monthly return under a 6% static drawdown.

Why rules and not a model: the boosted model reaches absurd in-sample numbers by
memorising each bar's outcome. That is not a system - there is nothing to state,
nothing to execute, and no transfer. A conjunction of feature thresholds IS a
system: you can write it down, and you could have traded it mechanically across
the whole span had you known the constants in advance.

Objective. The target reduces to a single ratio:
    implied monthly return = 0.06 * (monthly_R / maxDrawdown_R)
because risk per trade is set by sizing the worst drawdown to exactly the 6%
floor. Maximising that ratio IS maximising the achievable monthly return.

Everything here is fitted with full hindsight on the whole span. That is what
was asked for. The honest walk-forward counterpart is measured separately.
"""
import os
import sys
from itertools import product

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dataset as DS      # noqa: E402

N_Q = 9        # threshold quantiles per feature
MIN_TRADES = 300


class Book:
    """Precomputed arrays so a rule evaluation is a few vectorised passes."""

    def __init__(self, d, feats, min_trades=MIN_TRADES):
        self.d = d
        self.feats = feats
        self.min_trades = min_trades
        dt = pd.DatetimeIndex(d.dt)
        self.months_idx = ((dt.year - dt.year.min()) * 12 + dt.month - 1).values
        self.n_months = int(self.months_idx.max()) + 1
        self.span_months = (dt.max() - dt.min()).days / 30.44
        self.r = {1: d.r_long.values.astype(np.float64),
                  -1: d.r_short.values.astype(np.float64)}
        self.valid = {s: np.isfinite(self.r[s]) for s in (1, -1)}
        # atomic conditions
        self.conds = []
        for c in feats:
            x = d[c].values.astype(np.float64)
            fin = np.isfinite(x)
            if fin.sum() < len(x) * 0.5:
                continue
            qs = np.unique(np.nanquantile(x[fin], np.linspace(0.1, 0.9, N_Q)))
            for q in qs:
                self.conds.append((c, float(q), 1, (x >= q) & fin))
                self.conds.append((c, float(q), -1, (x <= q) & fin))

    def evaluate(self, mask, side):
        """Return metrics for taking `side` on every bar where mask is True."""
        m = mask & self.valid[side]
        n = int(m.sum())
        if n < self.min_trades:
            return None
        rr = np.where(m, self.r[side], 0.0)
        mon = np.bincount(self.months_idx, weights=rr, minlength=self.n_months)
        return self._metrics(mon, n)

    def evaluate_multi(self, parts):
        """parts: list of (mask, side). Union of several rules."""
        rr = np.zeros(len(self.d))
        n = 0
        for mask, side in parts:
            m = mask & self.valid[side]
            rr += np.where(m, self.r[side], 0.0)
            n += int(m.sum())
        if n < self.min_trades:
            return None
        mon = np.bincount(self.months_idx, weights=rr, minlength=self.n_months)
        return self._metrics(mon, n)

    def _metrics(self, mon, n):
        cum = np.cumsum(mon)
        dd = float(np.max(np.maximum.accumulate(cum) - cum))
        total = float(cum[-1])
        mo_R = total / self.span_months
        if dd <= 1e-9:
            dd = 1e-9
        ratio = mo_R / dd
        risk = min(0.06 / dd, 0.05)            # cap risk at 5% per trade
        return {"n": n, "mo_R": mo_R, "maxDD_R": dd, "ratio": ratio,
                "risk_pct": risk, "monthly_ret": risk * mo_R,
                "pos_months": float((mon[mon != 0] > 0).mean()) if (mon != 0).any() else 0.0,
                "worst_month_R": float(mon.min()),
                "months_traded": int((mon != 0).sum())}


def beam_search(book, side, depth=4, beam=24, verbose=True):
    """Greedy beam over conjunctions, scored by implied monthly return."""
    base = np.ones(len(book.d), dtype=bool)
    frontier = [([], base)]
    best_overall = []
    for lvl in range(depth):
        scored = []
        for path, mask in frontier:
            used = {p[0] for p in path}
            for (c, q, sgn, cm) in book.conds:
                if c in used:
                    continue
                nm = mask & cm
                met = book.evaluate(nm, side)
                if met is None:
                    continue
                scored.append((met["monthly_ret"], path + [(c, q, sgn)], nm, met))
        if not scored:
            break
        scored.sort(key=lambda z: -z[0])
        # dedupe by rule signature
        seen, keep = set(), []
        for s in scored:
            sig = tuple(sorted((a, round(b, 6), c) for a, b, c in s[1]))
            if sig in seen:
                continue
            seen.add(sig)
            keep.append(s)
            if len(keep) >= beam:
                break
        frontier = [(k[1], k[2]) for k in keep]
        best_overall.extend([(k[0], k[1], k[3]) for k in keep])
        if verbose:
            b = keep[0]
            rule = " & ".join("%s%s%.4g" % (a, ">=" if c > 0 else "<=", q)
                              for a, q, c in b[1])
            print(f"    depth {lvl+1}: best {100*b[0]:.2f}%/mo  n={b[3]['n']}  "
                  f"ratio {b[3]['ratio']:.2f}  [{rule}]")
    best_overall.sort(key=lambda z: -z[0])
    return best_overall


def assemble_portfolio(book, cands, max_rules=8, verbose=True):
    """Greedily union rules; diversification raises frequency and can cut the
    drawdown that any single rule suffers."""
    chosen = []
    cur = None
    for _ in range(max_rules):
        best = None
        for score, path, met, mask, side in cands:
            trial = chosen + [(mask, side)]
            m = book.evaluate_multi(trial)
            if m is None:
                continue
            if best is None or m["monthly_ret"] > best[0]:
                best = (m["monthly_ret"], (mask, side), path, m)
        if best is None:
            break
        if cur is not None and best[0] <= cur["monthly_ret"] + 1e-6:
            break
        chosen.append(best[1])
        cur = best[3]
        if verbose:
            print(f"  + rule {len(chosen)}: {100*cur['monthly_ret']:.2f}%/mo  "
                  f"n={cur['n']}  ratio {cur['ratio']:.2f}  "
                  f"risk {100*cur['risk_pct']:.2f}%  "
                  f"posmo {100*cur['pos_months']:.0f}%")
    return chosen, cur


def run(tf="4h", hold=60, depth=4, beam=24, min_trades=MIN_TRADES):
    d = DS.build(tf=tf, hold=hold)
    feats = DS.feature_list(d)
    book = Book(d, feats, min_trades=min_trades)
    print(f"=== {tf}: rows {len(d):,}  atomic conditions {len(book.conds)}  "
          f"span {book.span_months:.1f} months ===")

    allc = []
    for side, nm in ((1, "LONG"), (-1, "SHORT")):
        print(f"\n  beam search, {nm}")
        res = beam_search(book, side, depth=depth, beam=beam)
        for score, path, met in res[:60]:
            mask = np.ones(len(d), dtype=bool)
            for (c, q, sgn) in path:
                x = d[c].values.astype(np.float64)
                mask &= ((x >= q) if sgn > 0 else (x <= q)) & np.isfinite(x)
            allc.append((score, path, met, mask, side))

    allc.sort(key=lambda z: -z[0])
    print(f"\n  best single rules:")
    for score, path, met, _, side in allc[:8]:
        rule = " & ".join(f"{a}{'>=' if c>0 else '<='}{b:.4g}" for a, b, c in path)
        print(f"    {100*score:6.2f}%/mo  {'LONG ' if side>0 else 'SHORT'}  "
              f"n={met['n']:<6} ratio {met['ratio']:.2f}  "
              f"risk {100*met['risk_pct']:.2f}%  {rule}")

    print(f"\n  assembling portfolio")
    chosen, final = assemble_portfolio(book, allc[:120])
    return d, book, allc, chosen, final


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--tf", default="4h")
    p.add_argument("--hold", type=int, default=60)
    p.add_argument("--depth", type=int, default=4)
    p.add_argument("--beam", type=int, default=24)
    p.add_argument("--min-trades", type=int, default=300)
    a = p.parse_args()
    d, book, allc, chosen, final = run(a.tf, a.hold, a.depth, a.beam, a.min_trades)
    print("\n=== FINAL (in-sample, full hindsight) ===")
    if final:
        for k, v in final.items():
            print(f"  {k:<16} {v}")
