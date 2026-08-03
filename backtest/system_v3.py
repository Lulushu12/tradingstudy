"""System v3: RANGE_FADE deleted, plus optional resting-limit entries.

Run order matters here, and is fixed in advance to avoid burning the only
clean dataset left:

  1. v3 (RANGE_FADE deleted, market entries) is evaluated on BOTH windows.
  2. The limit-entry parameters are chosen a priori - 0.25 ATR offset, 6-bar
     expiry - as the natural middle of a plausible range, NOT by picking the
     best cell of a grid. The grid is printed for context, but the headline
     number is the a-priori setting on the PRIOR window, which no design
     decision in this study was fitted to.

Anything else would recycle the out-of-sample set into a training set, which
is the exact error the previous round of this study got caught making.
"""

import json
import os
import sys

import numpy as np

import indicators
import limit_entry
import run_backtest
import strategy

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
SYMBOLS = ["ETHUSDT", "LINKUSDT", "SOLUSDT"]

WINDOWS = [("1h_prior", "PRIOR 1h (2024-04 to 2025-06)", 168),
           ("1h", "MAIN 1h (2025-06 to 2026-08)", 168)]

# Chosen before looking at any limit-entry result.
DEFAULT_OFFSET = 0.25
DEFAULT_EXPIRY = 6

rng = np.random.default_rng(11)
_cache = {}


def prep(symbol, suffix):
    key = (symbol, suffix)
    if key not in _cache:
        run_backtest.SUFFIX = suffix
        ts, o, h, l, c, v = run_backtest.load(symbol)
        _cache[key] = (o, h, l, c, indicators.build(o, h, l, c, v))
    return _cache[key]


def book(symbol, suffix, use_limit, offset=DEFAULT_OFFSET, expiry=DEFAULT_EXPIRY,
         conv_min=6.0, conv_max=10.001, scale=1.0, target_r=None):
    o, h, l, c, f = prep(symbol, suffix)
    n = len(c)
    rows, signals, unfilled = [], 0, 0

    for i in range(run_backtest.WARMUP, n - 1):
        if np.isnan(f["atr"][i]) or f["atr"][i] <= 0 or np.isnan(f["adx"][i]):
            continue
        setup, direction = strategy.classify(i, f, c, f["donch_hi"][i - 1], f["donch_lo"][i - 1])
        conv = strategy.conviction(setup, direction, i, f, c)
        if not (conv_min <= conv < conv_max):
            continue
        signals += 1

        # Stop distance is fixed at signal time and applied to the actual fill.
        ref = c[i]
        stop, _, tstop, _, rm, _ = strategy.levels(setup, direction, ref, i, f)
        stop_dist = abs(ref - stop) * scale
        use_r = rm if target_r is None else target_r

        mode = "LIMIT" if (use_limit and setup in limit_entry.LIMIT_SETUPS) else "MARKET"
        res = limit_entry.simulate(i, direction, mode, ref, stop_dist, use_r, tstop,
                                   offset, expiry, f["atr"][i], o, h, l, c, n)
        if res is None:
            unfilled += 1
            continue
        rows.append({"symbol": symbol, "bar_index": i, "setup": setup,
                     "direction": "LONG" if direction == 1 else "SHORT",
                     "conviction": round(conv, 2), **res})
    return rows, signals, unfilled


def stats(rows, block, signals=None, unfilled=None):
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
    means = np.empty(4000)
    for i in range(4000):
        sel = np.concatenate([by[p] for p in rng.choice(ub, size=len(ub), replace=True)])
        means[i] = rs[sel].mean()

    return {
        "n": len(rs), "win": 100 * len(w) / len(rs),
        "be": 100 * al / (aw + al) if (aw + al) > 0 else float("nan"),
        "avg": float(rs.mean()), "tot": float(rs.sum()),
        "pf": float(w.sum() / gl) if gl > 0 else float("nan"),
        "cost": 100 * float(np.mean([r["cost_share"] for r in rows])),
        "fill_rate": (100.0 * len(rows) / signals) if signals else 100.0,
        "lo": float(np.percentile(means, 2.5)),
        "hi": float(np.percentile(means, 97.5)),
        "p_pos": 100 * float((means > 0).mean()),
    }


HDR = (f"{'configuration':<38}{'n':>6}{'fill%':>7}{'win%':>7}{'BE%':>7}{'cost%R':>8}"
       f"{'avgR':>8}{'totR':>9}{'PF':>6}{'95% CI':>20}{'P(>0)':>7}")


def show(tag, s):
    if not s:
        print(f"{tag:<38} (no trades)")
        return
    ci = f"[{s['lo']:+.3f}, {s['hi']:+.3f}]"
    star = " *" if (s["lo"] > 0 or s["hi"] < 0) else ""
    print(f"{tag:<38}{s['n']:>6}{s['fill_rate']:>7.1f}{s['win']:>7.1f}{s['be']:>7.1f}"
          f"{s['cost']:>8.1f}{s['avg']:>8.3f}{s['tot']:>9.1f}{s['pf']:>6.2f}{ci:>20}"
          f"{s['p_pos']:>6.1f}{star}")


def pooled(suffix, block, **kw):
    rows, sig, unf = [], 0, 0
    for s in SYMBOLS:
        r, g, u = book(s, suffix, **kw)
        rows += r
        sig += g
        unf += u
    return rows, stats(rows, block, sig, unf)


def main():
    report = {}
    for suffix, label, block in WINDOWS:
        print("\n" + "=" * 126)
        print(label)
        print("=" * 126)
        print(HDR)
        report[suffix] = {}

        for tag, kw in [
            ("v3 market, conv >= 6", dict(use_limit=False)),
            ("v3 market, conv 6-8", dict(use_limit=False, conv_max=8.0)),
            ("v3 LIMIT, conv >= 6", dict(use_limit=True)),
            ("v3 LIMIT, conv 6-8", dict(use_limit=True, conv_max=8.0)),
        ]:
            rows, s = pooled(suffix, block, **kw)
            report[suffix][tag] = s
            show(tag, s)

        print("\n  per symbol, v3 LIMIT conv >= 6:")
        for sym in SYMBOLS:
            r, g, u = book(sym, suffix, use_limit=True)
            show(f"    {sym[:-4]}", stats(r, block, g, u))

    print("\n" + "=" * 126)
    print("LIMIT PARAMETER GRID - context only. The headline uses the a-priori 0.25 / 6.")
    print("=" * 126)
    grid = {}
    for suffix, label, block in WINDOWS:
        print(f"\n  {label}   avg R (fill rate %)")
        print(f"  {'offset':<10}" + "".join(f"{'exp=' + str(e):>18}" for e in (3, 6, 12)))
        grid[suffix] = {}
        for off in (0.15, 0.25, 0.40, 0.60):
            cells = []
            for exp in (3, 6, 12):
                _, s = pooled(suffix, block, use_limit=True, offset=off, expiry=exp)
                grid[suffix][f"{off}|{exp}"] = s
                cells.append(f"{s['avg']:+.3f} ({s['fill_rate']:.0f}%)" if s else "-")
            print(f"  {off:<10}" + "".join(f"{c:>18}" for c in cells))

    paired = paired_test()

    with open(os.path.join(DATA, "system_v3.json"), "w") as fh:
        json.dump({"books": report, "grid": grid, "paired": paired,
                   "a_priori": {"offset": DEFAULT_OFFSET, "expiry": DEFAULT_EXPIRY}},
                  fh, indent=2, default=float)
    print("\nwrote system_v3.json")


def paired_pairs(suffix, tag, limit_all=False):
    """Market and limit outcome for the SAME signal. Unfilled limit scores 0."""
    out = []
    for sym in SYMBOLS:
        o, h, l, c, f = prep(sym, suffix)
        n = len(c)
        for i in range(run_backtest.WARMUP, n - 1):
            if np.isnan(f["atr"][i]) or f["atr"][i] <= 0 or np.isnan(f["adx"][i]):
                continue
            st, d = strategy.classify(i, f, c, f["donch_hi"][i - 1], f["donch_lo"][i - 1])
            if strategy.conviction(st, d, i, f, c) < 6.0:
                continue
            ref = c[i]
            sl, _, ts, _, rm, _ = strategy.levels(st, d, ref, i, f)
            dist = abs(ref - sl)
            m = limit_entry.simulate(i, d, "MARKET", ref, dist, rm, ts, DEFAULT_OFFSET,
                                     DEFAULT_EXPIRY, f["atr"][i], o, h, l, c, n)
            if m is None:
                continue
            mode = "LIMIT" if (limit_all or st in limit_entry.LIMIT_SETUPS) else "MARKET"
            lm = limit_entry.simulate(i, d, mode, ref, dist, rm, ts, DEFAULT_OFFSET,
                                      DEFAULT_EXPIRY, f["atr"][i], o, h, l, c, n)
            # Offset the bar index per window so bootstrap blocks never collide.
            out.append((tag * 100000 + i, m["r_multiple"],
                        lm["r_multiple"] if lm else 0.0, lm is None))
    return out


def _boot_mean(vals, bars, draws=8000, block=168):
    v = np.asarray(vals)
    b = np.asarray(bars) // block
    ub = np.unique(b)
    by = {q: np.flatnonzero(b == q) for q in ub}
    m = np.empty(draws)
    for i in range(draws):
        sel = np.concatenate([by[p] for p in rng.choice(ub, size=len(ub), replace=True)])
        m[i] = v[sel].mean()
    return {"mean": float(v.mean()), "lo": float(np.percentile(m, 2.5)),
            "hi": float(np.percentile(m, 97.5)), "p_pos": 100 * float((m > 0).mean())}


def paired_test():
    """Market vs limit on identical signals - far more powerful than two means."""
    print("\n" + "=" * 126)
    print("PAIRED TEST - same signals, both entry methods. Unfilled limit orders score 0.")
    print("=" * 126)
    print(f"{'window':<14}{'design':<24}{'signals':>9}{'unfilled':>10}{'mktR':>9}"
          f"{'limR':>9}{'gain':>9}{'95% CI on gain':>24}{'P(>0)':>8}")

    res = {}
    for suffix, label in [("1h_prior", "PRIOR (OOS)"), ("1h", "MAIN")]:
        for la, dl in [(False, "limit: pullbacks only"), (True, "limit: all setups")]:
            rows = paired_pairs(suffix, 0 if suffix == "1h_prior" else 1, la)
            bars = [r[0] for r in rows]
            mk = np.array([r[1] for r in rows])
            lm = np.array([r[2] for r in rows])
            g = _boot_mean(lm - mk, bars)
            res[f"{suffix}|{'all' if la else 'pullbacks'}"] = {
                "signals": len(rows), "unfilled": sum(1 for r in rows if r[3]),
                "market_avg": float(mk.mean()), "limit_avg": float(lm.mean()), **g}
            print(f"{label:<14}{dl:<24}{len(rows):>9}{sum(1 for r in rows if r[3]):>10}"
                  f"{mk.mean():>+9.3f}{lm.mean():>+9.3f}{g['mean']:>+9.3f}"
                  f"   [{g['lo']:+.4f}, {g['hi']:+.4f}]{g['p_pos']:>8.1f}")

    both = paired_pairs("1h_prior", 0) + paired_pairs("1h", 1)
    bars = [r[0] for r in both]
    mk = np.array([r[1] for r in both])
    lm = np.array([r[2] for r in both])
    gain = _boot_mean(lm - mk, bars)
    level = _boot_mean(lm, bars)
    res["combined"] = {"signals": len(both), "gain": gain, "level": level,
                       "market_avg": float(mk.mean()), "limit_avg": float(lm.mean())}

    print(f"\n  BOTH WINDOWS COMBINED - 20,000 hours, {len(both)} signals")
    print(f"    does limit BEAT market?   gain {gain['mean']:+.4f} R  "
          f"CI [{gain['lo']:+.4f}, {gain['hi']:+.4f}]  P(>0) = {gain['p_pos']:.1f}%  "
          f"-> {'SIGNIFICANT' if gain['lo'] > 0 else 'not significant at 95%'}")
    print(f"    is the limit book PROFITABLE?  avg R {level['mean']:+.4f}  "
          f"CI [{level['lo']:+.4f}, {level['hi']:+.4f}]  P(>0) = {level['p_pos']:.1f}%  "
          f"-> {'SIGNIFICANT' if level['lo'] > 0 else 'not significant at 95%'}")
    return res


if __name__ == "__main__":
    main()
