"""H2 - liquidation-wick continuation. See PREREGISTRATION_H2.md.

Bar identification is imported unchanged from H1 so the two hypotheses provably
trade the SAME bars. Only the direction and the stop side differ.

Thresholds must not be edited after results have been seen. H2 is judged
against a 97.5% interval, not 95%, because it is the second test on the same
primary window and was selected on the basis of H1's failure.
"""

import json
import os

import numpy as np

import limit_entry
import run_backtest
from hypothesis_h1 import (SYMBOLS, WINDOWS, prep, signal,
                           STOP_BUFFER_ATR, STOP_CAP_ATR, STOP_FLOOR_ATR,
                           TARGET_R, TIME_STOP)

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# Bonferroni-adjusted for this being the second test on the same data.
CI_LO_PCT, CI_HI_PCT = 1.25, 98.75      # 97.5% interval
CI95_LO_PCT, CI95_HI_PCT = 2.5, 97.5    # reported alongside, not the criterion

rng = np.random.default_rng(11)


def book(symbol, suffix, mode):
    """Same bars as H1, opposite direction, stop beyond the opposite extreme."""
    o, h, l, c, f = prep(symbol, suffix)
    n = len(c)
    rows, signals = [], 0

    for i in range(run_backtest.WARMUP, n - 1):
        s = signal(i, o, h, l, c, f)
        if s == 0:
            continue
        signals += 1
        d = -s                       # <-- the inversion, and the only one
        atr = f["atr"][i]
        ref = c[i]

        # Stop beyond the extreme OPPOSITE to the wick: a short after a lower
        # wick is wrong if price breaks the bar's high.
        opposite = h[i] if d == -1 else l[i]
        dist = abs(ref - (opposite + (-d) * STOP_BUFFER_ATR * atr))
        dist = min(dist, STOP_CAP_ATR * atr)
        dist = max(dist, STOP_FLOOR_ATR * atr)

        res = limit_entry.simulate(i, d, mode, ref, dist, TARGET_R, TIME_STOP,
                                   0.25, 6, atr, o, h, l, c, n)
        if res is None:
            continue
        rows.append({"symbol": symbol, "bar_index": i,
                     "direction": "LONG" if d == 1 else "SHORT", **res})
    return rows, signals


def stats(rows, block, signals=None):
    if not rows:
        return None
    rs = np.array([r["r_multiple"] for r in rows])
    w = rs[rs > 0]
    losses = rs[rs <= 0]
    gl = abs(losses.sum())
    aw = w.mean() if len(w) else 0.0
    al = abs(losses.mean()) if len(losses) else 0.0

    bars = np.array([r["bar_index"] for r in rows])
    b = bars // block
    ub = np.unique(b)
    by = {q: np.flatnonzero(b == q) for q in ub}
    m = np.empty(8000)
    for i in range(8000):
        sel = np.concatenate([by[p] for p in rng.choice(ub, size=len(ub), replace=True)])
        m[i] = rs[sel].mean()

    gross = np.array([r["gross_pct"] for r in rows])
    stop_pct = np.array([abs(r["entry_px"] - r["stop"]) / r["entry_px"] for r in rows])
    return {
        "n": len(rs), "signals": signals or len(rs),
        "fill": 100.0 * len(rs) / (signals or len(rs)),
        "win": 100 * len(w) / len(rs),
        "be": 100 * al / (aw + al) if (aw + al) > 0 else float("nan"),
        "avg": float(rs.mean()), "gross_R": float((gross / stop_pct).mean()),
        "tot": float(rs.sum()),
        "pf": float(w.sum() / gl) if gl > 0 else float("nan"),
        "cost": 100 * float(np.mean([r["cost_share"] for r in rows])),
        "stop_atr": float(np.mean(stop_pct)) * 100,
        "lo975": float(np.percentile(m, CI_LO_PCT)),
        "hi975": float(np.percentile(m, CI_HI_PCT)),
        "lo95": float(np.percentile(m, CI95_LO_PCT)),
        "hi95": float(np.percentile(m, CI95_HI_PCT)),
        "p_pos": 100 * float((m > 0).mean()),
    }


HDR = (f"{'book':<32}{'n':>6}{'win%':>7}{'BE%':>7}{'stop%':>7}{'cost%R':>8}"
       f"{'grossR':>8}{'avgR':>8}{'totR':>8}{'PF':>6}{'97.5% CI':>21}{'P(>0)':>7}")


def show(tag, s):
    if not s:
        print(f"{tag:<32} (no trades)")
        return
    ci = f"[{s['lo975']:+.3f}, {s['hi975']:+.3f}]"
    star = " *" if (s["lo975"] > 0 or s["hi975"] < 0) else ""
    print(f"{tag:<32}{s['n']:>6}{s['win']:>7.1f}{s['be']:>7.1f}{s['stop_atr']:>7.2f}"
          f"{s['cost']:>8.1f}{s['gross_R']:>8.3f}{s['avg']:>8.3f}{s['tot']:>8.1f}"
          f"{s['pf']:>6.2f}{ci:>21}{s['p_pos']:>6.1f}{star}")


def main():
    report = {}
    for suffix, label, block in WINDOWS:
        print("\n" + "=" * 128)
        print(label.replace("PRIMARY TEST", "PRIMARY TEST  (97.5% CI is the criterion)"))
        print("=" * 128)
        print(HDR)
        report[suffix] = {}

        for mode, tag in [("MARKET", "H2 market entry (PRIMARY)"),
                          ("LIMIT", "H2 limit entry (secondary)")]:
            rows, sig = [], 0
            for sym in SYMBOLS:
                r, g = book(sym, suffix, mode)
                rows += r
                sig += g
            s = stats(rows, block, sig)
            report[suffix][mode] = s
            show(tag, s)

        print("  per symbol, market entry:")
        for sym in SYMBOLS:
            r, g = book(sym, suffix, "MARKET")
            s = stats(r, block, g)
            report[suffix][f"market_{sym}"] = s
            show(f"    {sym[:-4]}", s)

    print("\n" + "=" * 128)
    print("VERDICT against the pre-registered H2 criteria")
    print("=" * 128)
    p = report["1h_prior"]["MARKET"]
    syms = [report["1h_prior"].get(f"market_{s}") for s in SYMBOLS]
    reps = [report[w]["MARKET"] for w, _, _ in WINDOWS[1:]]

    if not p or p["n"] < 100:
        print(f"  INCONCLUSIVE - pooled n = {p['n'] if p else 0}, below the floor of 100.")
    elif p["avg"] > 0 and p["lo975"] > 0:
        print(f"  SUPPORTED - mean {p['avg']:+.3f} R, 97.5% CI "
              f"[{p['lo975']:+.3f}, {p['hi975']:+.3f}] excludes zero.")
    elif (p["avg"] > 0 and p["lo95"] > 0
          and all(x and x["avg"] > 0 for x in syms)
          and all(x and x["avg"] > 0 for x in reps)):
        print(f"  SUGGESTIVE - mean {p['avg']:+.3f} R, 95% CI excludes zero but 97.5% does not, "
              f"and signs are consistent across symbols and replications.")
    else:
        why = []
        if p["avg"] <= 0:
            why.append("point estimate not positive")
        if p["lo975"] <= 0:
            why.append("97.5% CI includes zero")
        if not all(x and x["avg"] > 0 for x in syms):
            why.append("per-symbol signs inconsistent")
        if not all(x and x["avg"] > 0 for x in reps):
            why.append("does not replicate on both other datasets")
        print(f"  NOT SUPPORTED - mean {p['avg']:+.3f} R, 97.5% CI "
              f"[{p['lo975']:+.3f}, {p['hi975']:+.3f}]; " + "; ".join(why) + ".")

    with open(os.path.join(DATA, "hypothesis_h2.json"), "w") as fh:
        json.dump(report, fh, indent=2, default=float)
    print("\nwrote hypothesis_h2.json")


if __name__ == "__main__":
    main()
