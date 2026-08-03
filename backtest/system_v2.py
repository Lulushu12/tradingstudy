"""Build and evaluate System v2 against the books it is meant to improve on.

v2 applies the two changes the study supports, both of them subtractive:
drop the 8-10 conviction bucket, and delete RANGE_FADE. Optionally it also
adopts the sweep's average-R geometry (stop x1.6, 4R target).

Everything is reported against v1 so the size of each change is visible, with
a time split and a block bootstrap, because the whole point of the exercise is
that plausible-looking improvements have repeatedly failed those two tests.
"""

import csv
import json
import os
import sys

import numpy as np

import indicators
import run_backtest
import simulate
import strategy

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
SYMBOLS = ["ETHUSDT", "LINKUSDT", "SOLUSDT"]

rng = np.random.default_rng(11)
_cache = {}


def prep(symbol, suffix):
    key = (symbol, suffix)
    if key not in _cache:
        run_backtest.SUFFIX = suffix
        ts, o, h, l, c, v = run_backtest.load(symbol)
        _cache[key] = (ts, o, h, l, c, indicators.build(o, h, l, c, v),
                       indicators.pivot_lists(h, l))
    return _cache[key]


def build(symbol, suffix, rule, scale=1.0, target_r=None):
    """rule(setup, conviction) -> bool. target_r None keeps the setup's own R."""
    ts, o, h, l, c, f, piv = prep(symbol, suffix)
    n = len(c)
    rows = []
    for i in range(run_backtest.WARMUP, n - 1):
        if np.isnan(f["atr"][i]) or f["atr"][i] <= 0 or np.isnan(f["adx"][i]):
            continue
        setup, direction = strategy.classify(i, f, c, f["donch_hi"][i - 1], f["donch_lo"][i - 1])
        conv = strategy.conviction(setup, direction, i, f, c)
        if not rule(setup, conv):
            continue

        entry = c[i] * (1 + direction * simulate.SLIPPAGE)
        stop, _, tstop, stop_note, rm, _ = strategy.levels(setup, direction, entry, i, f)
        use_r = rm if target_r is None else target_r
        dist = abs(entry - stop) * scale
        stop = entry - direction * dist
        target = entry + direction * use_r * dist

        res = simulate.simulate(i, direction, entry, stop, target, tstop, o, h, l, c, n)
        if not res or res["status"] != "CLOSED":
            continue
        rows.append({
            "symbol": symbol, "bar_index": i, "time": run_backtest.iso(ts[i]),
            "setup": setup, "direction": "LONG" if direction == 1 else "SHORT",
            "conviction": round(conv, 2), "entry": entry, "stop": stop, "target": target,
            "r_multiple": res["r_multiple"], "exit_reason": res["exit_reason"],
            "bars_held": res["bars_held"],
            "cost_share": res["cost_pct"] / (dist / entry),
            "planned_rr": use_r, "stop_pct": dist / entry * 100,
        })
    return rows


def summarize(rows):
    if not rows:
        return None
    rs = np.array([r["r_multiple"] for r in rows])
    w = rs[rs > 0]
    losses = rs[rs <= 0]
    gl = abs(losses.sum())
    aw = w.mean() if len(w) else 0.0
    al = abs(losses.mean()) if len(losses) else 0.0
    return {
        "n": len(rs), "win": 100 * len(w) / len(rs),
        "be": 100 * al / (aw + al) if (aw + al) > 0 else float("nan"),
        "avg": float(rs.mean()), "tot": float(rs.sum()),
        "pf": float(w.sum() / gl) if gl > 0 else float("nan"),
        "cost": 100 * float(np.mean([r["cost_share"] for r in rows])),
    }


def bootstrap(rows, block):
    rs = np.array([r["r_multiple"] for r in rows])
    bars = np.array([r["bar_index"] for r in rows])
    b = bars // block
    ub = np.unique(b)
    by = {q: np.flatnonzero(b == q) for q in ub}
    means = np.empty(4000)
    for i in range(4000):
        sel = np.concatenate([by[p] for p in rng.choice(ub, size=len(ub), replace=True)])
        means[i] = rs[sel].mean()
    return {
        "lo": float(np.percentile(means, 2.5)),
        "hi": float(np.percentile(means, 97.5)),
        "p_pos": 100 * float((means > 0).mean()),
    }


HDR = (f"{'book':<40}{'n':>6}{'win%':>7}{'BE%':>7}{'cost%R':>8}{'avgR':>8}"
       f"{'totR':>9}{'PF':>6}{'95% CI':>20}{'P(>0)':>7}")


def line(tag, rows, block):
    s = summarize(rows)
    if not s:
        print(f"{tag:<40} (no trades)")
        return None
    b = bootstrap(rows, block)
    ci = f"[{b['lo']:+.3f}, {b['hi']:+.3f}]"
    print(f"{tag:<40}{s['n']:>6}{s['win']:>7.1f}{s['be']:>7.1f}{s['cost']:>8.1f}"
          f"{s['avg']:>8.3f}{s['tot']:>9.1f}{s['pf']:>6.2f}{ci:>20}{b['p_pos']:>7.1f}")
    return {**s, **b}


V1_SELECTIVE = lambda st, cv: cv >= 6.0
V1_BAND = lambda st, cv: 6.0 <= cv < 8.0
V2 = strategy.qualifies_v2


def main():
    suffix = sys.argv[1] if len(sys.argv) > 1 else "1h"
    block = 168 if suffix.startswith("1h") else 672
    out = {}

    configs = [
        ("v1  selective (conv >= 6, all setups)", V1_SELECTIVE, 1.0, None),
        ("v1  6-8 band (all setups)", V1_BAND, 1.0, None),
        ("v2  6-8, no RANGE_FADE, shipped geom", V2, 1.0, None),
        ("v2b 6-8, no RANGE_FADE, x1.6 / 4R", V2, strategy.V2_STOP_SCALE, strategy.V2_TARGET_R),
    ]

    print("=" * 118)
    print(f"POOLED across ETH + LINK + SOL   ({suffix} candles)")
    print("=" * 118)
    print(HDR)
    pooled = {}
    for label, rule, scale, tr in configs:
        rows = []
        for s in SYMBOLS:
            rows += build(s, suffix, rule, scale, tr)
        pooled[label] = rows
        out[label] = line(label, rows, block)

    print("\n" + "=" * 118)
    print("PER SYMBOL")
    print("=" * 118)
    print(HDR)
    for s in SYMBOLS:
        for label, rule, scale, tr in configs[1:]:
            rows = build(s, suffix, rule, scale, tr)
            line(f"{s[:-4]:<5} {label}", rows, block)
        print()

    print("=" * 118)
    print("TIME SPLIT (does v2 hold in both halves?)")
    print("=" * 118)
    print(HDR)
    for label in [c[0] for c in configs[1:]]:
        rows = pooled[label]
        idx = [r["bar_index"] for r in rows]
        mid = (min(idx) + max(idx)) // 2
        line(f"{label} - H1", [r for r in rows if r["bar_index"] <= mid], block)
        line(f"{label} - H2", [r for r in rows if r["bar_index"] > mid], block)
        print()

    # What the exclusions actually removed.
    print("=" * 118)
    print("WHAT WAS CUT")
    print("=" * 118)
    print(HDR)
    hi_band = [r for r in build_all(suffix, lambda st, cv: cv >= 8.0)]
    line("dropped: conviction 8-10 (all setups)", hi_band, block)
    rf = [r for r in build_all(suffix, lambda st, cv: st == "RANGE_FADE" and 6.0 <= cv < 8.0)]
    line("dropped: RANGE_FADE in 6-8 band", rf, block)

    v2rows = pooled["v2  6-8, no RANGE_FADE, shipped geom"]

    # Full structured dump so the workbook builder never has to re-simulate.
    def pack(rows):
        s = summarize(rows)
        return None if not s else {**s, **bootstrap(rows, block)}

    report = {"pooled": out, "per_symbol": {}, "time_split": {}, "cut": {}}
    for s in SYMBOLS:
        report["per_symbol"][s] = {
            label: pack(build(s, suffix, rule, scale, tr))
            for label, rule, scale, tr in configs
        }
    for label in [c[0] for c in configs[1:]]:
        rows = pooled[label]
        idx = [r["bar_index"] for r in rows]
        mid = (min(idx) + max(idx)) // 2
        report["time_split"][label] = {
            "H1": pack([r for r in rows if r["bar_index"] <= mid]),
            "H2": pack([r for r in rows if r["bar_index"] > mid]),
        }
    report["cut"] = {
        "conviction 8-10 (all setups)": pack(hi_band),
        "RANGE_FADE inside 6-8 band": pack(rf),
    }
    report["n_trades"] = len(v2rows)

    with open(os.path.join(DATA, f"system_v2_{suffix}.json"), "w") as fh:
        json.dump(report, fh, indent=2, default=float)
    with open(os.path.join(DATA, f"system_v2_{suffix}_trades.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(v2rows[0].keys()))
        w.writeheader()
        w.writerows(v2rows)
    print(f"\nwrote system_v2_{suffix}.json and system_v2_{suffix}_trades.csv")


def build_all(suffix, rule, scale=1.0, tr=None):
    rows = []
    for s in SYMBOLS:
        rows += build(s, suffix, rule, scale, tr)
    return rows


if __name__ == "__main__":
    main()
