"""H1 - liquidation-wick reversion. See PREREGISTRATION.md.

Thresholds below are the pre-registered ones and must not be edited after
results have been seen. They are named as constants precisely so that any
change shows up in a diff.
"""

import json
import os
import sys

import numpy as np

import indicators
import limit_entry
import run_backtest

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
SYMBOLS = ["ETHUSDT", "LINKUSDT", "SOLUSDT"]

# ---- Pre-registered parameters. Do not tune. ----
WICK_ATR = 1.0        # wick must be at least this many ATR
WICK_FRAC = 0.50      # wick as a share of the bar's full range
CLOSE_POS = 0.50      # close must recover to at least this share of the range
VOL_Z = 1.0           # volume z-score over 100 bars
STOP_BUFFER_ATR = 0.25
STOP_CAP_ATR = 2.5
STOP_FLOOR_ATR = 0.6
TARGET_R = 2.0
TIME_STOP = 48
# ------------------------------------------------

WINDOWS = [("1h_prior", "PRIOR 1h  (2024-04 to 2025-06)  PRIMARY TEST", 168),
           ("1h", "MAIN 1h   (2025-06 to 2026-08)  replication", 168),
           ("15m", "15m       (2026-04 to 2026-08)  replication", 672)]

rng = np.random.default_rng(11)
_cache = {}


def prep(symbol, suffix):
    key = (symbol, suffix)
    if key not in _cache:
        run_backtest.SUFFIX = suffix
        ts, o, h, l, c, v = run_backtest.load(symbol)
        _cache[key] = (o, h, l, c, indicators.build(o, h, l, c, v))
    return _cache[key]


def signal(i, o, h, l, c, f):
    """Return +1 (long), -1 (short) or 0. Uses only data through bar i."""
    rng_bar = h[i] - l[i]
    if rng_bar <= 0:
        return 0
    atr = f["atr"][i]
    if np.isnan(atr) or atr <= 0:
        return 0
    if f["vol_z"][i] < VOL_Z:
        return 0

    body_lo = min(o[i], c[i])
    body_hi = max(o[i], c[i])
    lower_wick = body_lo - l[i]
    upper_wick = h[i] - body_hi

    # Long: a lower wick was absorbed and the close recovered.
    if (lower_wick >= WICK_ATR * atr
            and lower_wick / rng_bar >= WICK_FRAC
            and (c[i] - l[i]) / rng_bar >= CLOSE_POS):
        return 1
    # Short: mirror.
    if (upper_wick >= WICK_ATR * atr
            and upper_wick / rng_bar >= WICK_FRAC
            and (h[i] - c[i]) / rng_bar >= CLOSE_POS):
        return -1
    return 0


def book(symbol, suffix, mode):
    o, h, l, c, f = prep(symbol, suffix)
    n = len(c)
    rows, signals = [], 0

    for i in range(run_backtest.WARMUP, n - 1):
        d = signal(i, o, h, l, c, f)
        if d == 0:
            continue
        signals += 1
        atr = f["atr"][i]
        ref = c[i]

        extreme = l[i] if d == 1 else h[i]
        dist = abs(ref - (extreme - d * STOP_BUFFER_ATR * atr))
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
        "lo": float(np.percentile(m, 2.5)), "hi": float(np.percentile(m, 97.5)),
        "p_pos": 100 * float((m > 0).mean()),
    }


HDR = (f"{'book':<34}{'n':>6}{'fill%':>7}{'win%':>7}{'BE%':>7}{'cost%R':>8}"
       f"{'grossR':>8}{'avgR':>8}{'totR':>8}{'PF':>6}{'95% CI':>21}{'P(>0)':>7}")


def show(tag, s):
    if not s:
        print(f"{tag:<34} (no trades)")
        return
    ci = f"[{s['lo']:+.3f}, {s['hi']:+.3f}]"
    star = " *" if (s["lo"] > 0 or s["hi"] < 0) else ""
    print(f"{tag:<34}{s['n']:>6}{s['fill']:>7.1f}{s['win']:>7.1f}{s['be']:>7.1f}"
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

        for mode, tag in [("MARKET", "H1 market entry (PRIMARY)"),
                          ("LIMIT", "H1 limit entry (secondary)")]:
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

        for d in ("LONG", "SHORT"):
            rows, sig = [], 0
            for sym in SYMBOLS:
                r, g = book(sym, suffix, "MARKET")
                rows += [x for x in r if x["direction"] == d]
            s = stats(rows, block)
            report[suffix][f"market_{d}"] = s
            show(f"    {d.lower()}s only", s)

    print("\n" + "=" * 128)
    print("VERDICT against the pre-registered criteria")
    print("=" * 128)
    p = report["1h_prior"]["MARKET"]
    if not p or p["n"] < 100:
        print(f"  INCONCLUSIVE - pooled n = {p['n'] if p else 0} on the primary window, "
              f"below the pre-registered floor of 100.")
    elif p["lo"] > 0:
        print(f"  SUPPORTED - mean {p['avg']:+.3f} R, 95% CI [{p['lo']:+.3f}, {p['hi']:+.3f}] "
              f"excludes zero on the primary out-of-sample window.")
    else:
        syms = [report["1h_prior"].get(f"market_{s}") for s in SYMBOLS]
        all_pos = all(x and x["avg"] > 0 for x in syms)
        reps = [report[w]["MARKET"] for w, _, _ in WINDOWS[1:]]
        all_rep = all(x and x["avg"] > 0 for x in reps)
        if p["avg"] > 0 and all_pos and all_rep:
            print(f"  SUGGESTIVE - mean {p['avg']:+.3f} R, CI includes zero, but the sign is "
                  f"consistent across all three symbols and both replication datasets.")
        else:
            print(f"  NOT SUPPORTED - mean {p['avg']:+.3f} R, 95% CI "
                  f"[{p['lo']:+.3f}, {p['hi']:+.3f}] includes zero"
                  + ("" if p["avg"] > 0 else " and the point estimate is negative")
                  + (f"; per-symbol signs consistent: {all_pos}; replicates: {all_rep}."))

    with open(os.path.join(DATA, "hypothesis_h1.json"), "w") as fh:
        json.dump(report, fh, indent=2, default=float)
    print("\nwrote hypothesis_h1.json")


if __name__ == "__main__":
    main()
