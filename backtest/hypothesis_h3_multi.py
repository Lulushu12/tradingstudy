"""H3-Multi - H3 replicated on 25 untouched assets. See PREREGISTRATION_H3M.md.

Every parameter is imported from hypothesis_h3, which imports the bar
identification from hypothesis_h1. Nothing is redefined here, so a diff proves
no rule changed.

The bootstrap resamples CALENDAR-WEEK blocks spanning the whole universe rather
than individual trades. Crypto majors are highly cross-correlated, so 25 assets
do not carry 25x the independent information; per-trade resampling would badly
overstate significance at this sample size.
"""

import json
import os

import numpy as np

import run_backtest
from hypothesis_h1 import prep, signal
from hypothesis_h3 import GAP_GUARD, STOP_ATR, TARGET_R, TIME_STOP, gap_indices
import limit_entry

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DERIVED_ON = {"ETHUSDT", "LINKUSDT", "SOLUSDT"}
WINDOWS = [("1h_early", "EARLY"), ("1h_prior", "PRIOR"), ("1h", "MAIN")]
WEEK_MS = 7 * 24 * 3600 * 1000

rng = np.random.default_rng(11)


def book(symbol, suffix, mode="MARKET"):
    """H3, unchanged, with a wall-clock timestamp attached to each trade."""
    run_backtest.SUFFIX = suffix
    ts, *_ = run_backtest.load(symbol)
    o, h, l, c, f = prep(symbol, suffix)
    n = len(c)
    gaps = gap_indices(symbol, suffix)
    rows = []

    for i in range(run_backtest.WARMUP, n - 1):
        s = signal(i, o, h, l, c, f)
        if s == 0 or any(abs(i - g) <= GAP_GUARD for g in gaps):
            continue
        atr = f["atr"][i]
        res = limit_entry.simulate(i, -s, mode, c[i], STOP_ATR * atr, TARGET_R,
                                   TIME_STOP, 0.25, 6, atr, o, h, l, c, n)
        if res is None:
            continue
        rows.append({"symbol": symbol, "window": suffix, "t": int(ts[i]),
                     "r": res["r_multiple"], "cost_share": res["cost_share"],
                     "exit": res["exit_reason"]})
    return rows


def cross_sectional_bootstrap(rows, draws=8000):
    """Resample calendar weeks, taking every asset's trades in that week together."""
    r = np.array([x["r"] for x in rows])
    week = np.array([x["t"] // WEEK_MS for x in rows])
    ub = np.unique(week)
    by = {w: np.flatnonzero(week == w) for w in ub}
    m = np.empty(draws)
    for i in range(draws):
        sel = np.concatenate([by[w] for w in rng.choice(ub, size=len(ub), replace=True)])
        m[i] = r[sel].mean()
    return {"lo": float(np.percentile(m, 2.5)), "hi": float(np.percentile(m, 97.5)),
            "p_pos": 100 * float((m > 0).mean()), "n_weeks": len(ub)}


def naive_bootstrap(rows, draws=8000):
    """Per-trade resampling - reported ONLY to show how much it overstates."""
    r = np.array([x["r"] for x in rows])
    m = np.empty(draws)
    for i in range(draws):
        m[i] = r[rng.integers(0, len(r), len(r))].mean()
    return {"lo": float(np.percentile(m, 2.5)), "hi": float(np.percentile(m, 97.5)),
            "p_pos": 100 * float((m > 0).mean())}


def summarize(rows):
    r = np.array([x["r"] for x in rows])
    w = r[r > 0]
    losses = r[r <= 0]
    gl = abs(losses.sum())
    aw = w.mean() if len(w) else 0.0
    al = abs(losses.mean()) if len(losses) else 0.0
    return {"n": len(r), "win": 100 * len(w) / len(r),
            "be": 100 * al / (aw + al) if (aw + al) > 0 else float("nan"),
            "avg": float(r.mean()), "tot": float(r.sum()),
            "pf": float(w.sum() / gl) if gl > 0 else float("nan"),
            "cost": 100 * float(np.mean([x["cost_share"] for x in rows]))}


def main():
    universe = [s for s in json.load(open(os.path.join(DATA, "_universe.json")))
                if s not in DERIVED_ON]
    print(f"universe: {len(universe)} assets never touched by this study\n")

    all_rows, per_asset, per_window, dropped = [], {}, {}, []
    for sym in universe:
        rows = []
        for suffix, _ in WINDOWS:
            if not os.path.exists(os.path.join(DATA, f"{sym}_{suffix}.csv")):
                dropped.append(f"{sym}/{suffix}")
                continue
            rows += book(sym, suffix)
        if not rows:
            dropped.append(sym)
            continue
        per_asset[sym] = summarize(rows)
        all_rows += rows

    for suffix, lab in WINDOWS:
        sel = [x for x in all_rows if x["window"] == suffix]
        if sel:
            per_window[lab] = {**summarize(sel), **cross_sectional_bootstrap(sel)}

    pooled = summarize(all_rows)
    xs = cross_sectional_bootstrap(all_rows)
    naive = naive_bootstrap(all_rows)

    print("=" * 112)
    print("PER ASSET (all three windows pooled)")
    print("=" * 112)
    print(f"{'asset':<12}{'n':>7}{'win%':>8}{'BE%':>8}{'avgR':>9}{'totR':>9}{'PF':>7}")
    for s in sorted(per_asset, key=lambda k: -per_asset[k]["avg"]):
        a = per_asset[s]
        print(f"{s[:-4]:<12}{a['n']:>7}{a['win']:>8.1f}{a['be']:>8.1f}"
              f"{a['avg']:>9.3f}{a['tot']:>9.1f}{a['pf']:>7.2f}")

    npos = sum(1 for a in per_asset.values() if a["avg"] > 0)
    print(f"\n  {npos}/{len(per_asset)} assets positive "
          f"({100 * npos / len(per_asset):.0f}%)")

    print("\n" + "=" * 112)
    print("BY WINDOW")
    print("=" * 112)
    print(f"{'window':<12}{'n':>7}{'win%':>8}{'BE%':>8}{'avgR':>9}{'PF':>7}{'95% CI':>22}{'P(>0)':>8}")
    for lab, a in per_window.items():
        print(f"{lab:<12}{a['n']:>7}{a['win']:>8.1f}{a['be']:>8.1f}{a['avg']:>9.3f}"
              f"{a['pf']:>7.2f}   [{a['lo']:+.3f}, {a['hi']:+.3f}]{a['p_pos']:>8.1f}")

    print("\n" + "=" * 112)
    print("POOLED - THE PRE-REGISTERED PRIMARY TEST")
    print("=" * 112)
    print(f"  trades {pooled['n']:,}   weeks {xs['n_weeks']}   win {pooled['win']:.1f}% "
          f"vs breakeven {pooled['be']:.1f}%   PF {pooled['pf']:.3f}   "
          f"cost {pooled['cost']:.1f}% of 1R")
    print(f"  mean R {pooled['avg']:+.4f}   total {pooled['tot']:+,.0f} R")
    print(f"  cross-sectional block bootstrap  95% CI [{xs['lo']:+.4f}, {xs['hi']:+.4f}]   "
          f"P(>0) = {xs['p_pos']:.1f}%")
    print(f"  (naive per-trade bootstrap would say [{naive['lo']:+.4f}, {naive['hi']:+.4f}], "
          f"P(>0) = {naive['p_pos']:.1f}% - overstated, not the criterion)")

    print("\n" + "=" * 112)
    print("VERDICT against the pre-registered H3-Multi criteria")
    print("=" * 112)
    frac = npos / len(per_asset)
    all_win_pos = all(a["avg"] > 0 for a in per_window.values())
    if pooled["n"] < 3000:
        print(f"  UNDERPOWERED - {pooled['n']} trades, below the floor of 3,000.")
    elif pooled["avg"] > 0 and xs["lo"] > 0 and frac >= 0.60 and all_win_pos:
        print(f"  SUPPORTED - mean {pooled['avg']:+.4f} R, 95% CI excludes zero, "
              f"{frac * 100:.0f}% of assets positive, all three windows positive.")
    elif pooled["avg"] > 0 and frac >= 0.60:
        print(f"  SUGGESTIVE - mean {pooled['avg']:+.4f} R, {frac * 100:.0f}% of assets "
              f"positive, but the 95% CI [{xs['lo']:+.4f}, {xs['hi']:+.4f}] includes zero.")
    else:
        why = []
        if pooled["avg"] <= 0:
            why.append("pooled mean not positive")
        if xs["lo"] <= 0:
            why.append("95% CI includes zero")
        if frac < 0.60:
            why.append(f"only {frac * 100:.0f}% of assets positive")
        if not all_win_pos:
            why.append("not positive in all three windows")
        print(f"  NOT SUPPORTED - " + "; ".join(why) + ".")

    if dropped:
        print(f"\n  dropped for incomplete data: {dropped}")

    json.dump({"pooled": {**pooled, **xs}, "naive": naive, "per_asset": per_asset,
               "per_window": per_window, "assets_positive": npos,
               "assets_total": len(per_asset), "dropped": dropped},
              open(os.path.join(DATA, "hypothesis_h3_multi.json"), "w"),
              indent=2, default=float)
    print("\nwrote hypothesis_h3_multi.json")


if __name__ == "__main__":
    main()
