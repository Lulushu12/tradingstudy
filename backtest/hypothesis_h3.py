"""H3 - wick continuation with a cost-derived stop. See PREREGISTRATION_H3.md.

Bar identification is imported unchanged from H1, so H1, H2 and H3 provably
fire on an identical signal list. H3 differs from H2 in exactly one substantive
parameter - the stop - plus the time stop that is coupled to it.

Primary dataset is the EARLY window, which no part of this study has touched.
"""

import json
import os

import numpy as np

import limit_entry
import run_backtest
from hypothesis_h1 import SYMBOLS, prep, signal

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---- Pre-registered parameters. Do not tune. ----
# Entry thresholds live in hypothesis_h1 and are imported via signal().
STOP_ATR = 2.5        # derived from the cost model on burned windows only
TARGET_R = 2.0        # unchanged from H1/H2
TIME_STOP = 96        # coupled to the stop widening (48 x ~2.1)
GAP_GUARD = 24        # skip signals within this many bars of a data discontinuity
# ------------------------------------------------

WINDOWS = [("1h_early", "EARLY 1h  (2023-03 to 2024-04)  PRIMARY - fresh data", 168),
           ("1h_prior", "PRIOR 1h  (2024-04 to 2025-06)  context", 168),
           ("1h", "MAIN 1h   (2025-06 to 2026-08)  context", 168)]

rng = np.random.default_rng(11)


def gap_indices(symbol, suffix):
    """Bar indices adjacent to a timestamp discontinuity."""
    run_backtest.SUFFIX = suffix
    ts, *_ = run_backtest.load(symbol)
    step = int(np.median(np.diff(ts)))
    return {i for i in range(1, len(ts)) if ts[i] - ts[i - 1] != step}


def book(symbol, suffix, mode):
    o, h, l, c, f = prep(symbol, suffix)
    n = len(c)
    gaps = gap_indices(symbol, suffix)
    rows, signals, skipped = [], 0, 0

    for i in range(run_backtest.WARMUP, n - 1):
        s = signal(i, o, h, l, c, f)
        if s == 0:
            continue
        if any(abs(i - g) <= GAP_GUARD for g in gaps):
            skipped += 1
            continue
        signals += 1
        d = -s                       # continuation direction, same as H2
        atr = f["atr"][i]
        dist = STOP_ATR * atr        # <-- the one substantive change from H2

        res = limit_entry.simulate(i, d, mode, c[i], dist, TARGET_R, TIME_STOP,
                                   0.25, 6, atr, o, h, l, c, n)
        if res is None:
            continue
        rows.append({"symbol": symbol, "bar_index": i,
                     "direction": "LONG" if d == 1 else "SHORT", **res})
    return rows, signals, skipped


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
    exits = {}
    for r in rows:
        k = r["exit_reason"].replace("_GAP", "")
        exits[k] = exits.get(k, 0) + 1
    return {
        "n": len(rs), "signals": signals or len(rs),
        "fill": 100.0 * len(rs) / (signals or len(rs)),
        "win": 100 * len(w) / len(rs),
        "be": 100 * al / (aw + al) if (aw + al) > 0 else float("nan"),
        "avg": float(rs.mean()), "gross_R": float((gross / stop_pct).mean()),
        "tot": float(rs.sum()),
        "pf": float(w.sum() / gl) if gl > 0 else float("nan"),
        "cost": 100 * float(np.mean([r["cost_share"] for r in rows])),
        "stop_pct": float(np.mean(stop_pct)) * 100,
        "exits": {k: round(100 * v / len(rs), 1) for k, v in sorted(exits.items())},
        "lo": float(np.percentile(m, 2.5)), "hi": float(np.percentile(m, 97.5)),
        "p_pos": 100 * float((m > 0).mean()),
    }


HDR = (f"{'book':<32}{'n':>6}{'win%':>7}{'BE%':>7}{'stop%':>7}{'cost%R':>8}"
       f"{'grossR':>8}{'avgR':>8}{'totR':>8}{'PF':>6}{'95% CI':>21}{'P(>0)':>7}")


def show(tag, s):
    if not s:
        print(f"{tag:<32} (no trades)")
        return
    ci = f"[{s['lo']:+.3f}, {s['hi']:+.3f}]"
    star = " *" if (s["lo"] > 0 or s["hi"] < 0) else ""
    print(f"{tag:<32}{s['n']:>6}{s['win']:>7.1f}{s['be']:>7.1f}{s['stop_pct']:>7.2f}"
          f"{s['cost']:>8.1f}{s['gross_R']:>8.3f}{s['avg']:>8.3f}{s['tot']:>8.1f}"
          f"{s['pf']:>6.2f}{ci:>21}{s['p_pos']:>6.1f}{star}")


def main():
    report = {}
    for suffix, label, block in WINDOWS:
        print("\n" + "=" * 128)
        print(label)
        print("=" * 128)
        print(HDR)
        report[suffix] = {}

        for mode, tag in [("MARKET", "H3 market entry (PRIMARY)"),
                          ("LIMIT", "H3 limit entry (secondary)")]:
            rows, sig, skip = [], 0, 0
            for sym in SYMBOLS:
                r, g, k = book(sym, suffix, mode)
                rows += r
                sig += g
                skip += k
            s = stats(rows, block, sig)
            report[suffix][mode] = s
            show(tag, s)
            if mode == "MARKET" and skip:
                print(f"    ({skip} signals skipped by the gap guard)")

        print("  per symbol, market entry:")
        for sym in SYMBOLS:
            r, g, _ = book(sym, suffix, "MARKET")
            s = stats(r, block, g)
            report[suffix][f"market_{sym}"] = s
            show(f"    {sym[:-4]}", s)

        m = report[suffix]["MARKET"]
        if m:
            print(f"    exit mix: {m['exits']}")

    print("\n" + "=" * 128)
    print("VERDICT against the pre-registered H3 criteria")
    print("=" * 128)
    p = report["1h_early"]["MARKET"]
    syms = [report["1h_early"].get(f"market_{s}") for s in SYMBOLS]
    all_pos = all(x and x["avg"] > 0 for x in syms)

    if not p or p["n"] < 100:
        print(f"  INCONCLUSIVE - pooled n = {p['n'] if p else 0}, below the floor of 100.")
    elif p["avg"] > 0 and p["lo"] > 0 and all_pos:
        print(f"  SUPPORTED - mean {p['avg']:+.3f} R, 95% CI [{p['lo']:+.3f}, {p['hi']:+.3f}] "
              f"excludes zero, and all three symbols are positive.")
    elif p["avg"] > 0 and all_pos:
        print(f"  SUGGESTIVE - mean {p['avg']:+.3f} R, positive on all three symbols, but the "
              f"95% CI [{p['lo']:+.3f}, {p['hi']:+.3f}] includes zero.")
    else:
        why = []
        if p["avg"] <= 0:
            why.append("point estimate not positive")
        if p["lo"] <= 0:
            why.append("95% CI includes zero")
        if not all_pos:
            detail = ", ".join("%s %+.3f" % (s[:-4], x["avg"])
                               for s, x in zip(SYMBOLS, syms) if x)
            why.append("not positive on all three symbols (" + detail + ")")
        print(f"  NOT SUPPORTED - mean {p['avg']:+.3f} R, 95% CI "
              f"[{p['lo']:+.3f}, {p['hi']:+.3f}]; " + "; ".join(why) + ".")

    print("\n  Reminder: H3 is the last variant of this bar shape to be tested, whatever the")
    print("  result. A pass is a candidate for forward testing, not a finding.")

    with open(os.path.join(DATA, "hypothesis_h3.json"), "w") as fh:
        json.dump(report, fh, indent=2, default=float)
    print("\nwrote hypothesis_h3.json")


if __name__ == "__main__":
    main()
