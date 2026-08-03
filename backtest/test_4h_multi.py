"""4h per-symbol cap on the 25-asset universe. See PREREGISTRATION_4H.md.

Signal generation and cap logic are imported from portfolio.py so nothing can
drift between the three-asset run that motivated this and the multi-asset test.
"""

import json
import os

import numpy as np

import portfolio

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DERIVED_ON = {"ETHUSDT", "LINKUSDT", "SOLUSDT"}
WEEK_MS = 7 * 24 * 3600 * 1000
TF = "4h"

rng = np.random.default_rng(11)


def collect(symbols):
    sigs, missing = [], []
    for sym in symbols:
        if not os.path.exists(os.path.join(DATA, f"{sym}_{TF}.csv")):
            missing.append(sym)
            continue
        try:
            s = portfolio.signals(sym, TF)
        except Exception as exc:  # noqa: BLE001
            missing.append(f"{sym} ({exc})")
            continue
        for x in s:
            x["bar_ms"] = portfolio.BAR_MS[TF]
        sigs += s
    return sigs, missing


def xs_bootstrap(trades, draws=8000):
    r = np.array([t["r"] for t in trades])
    wk = np.array([t["t"] // WEEK_MS for t in trades])
    ub = np.unique(wk)
    by = {w: np.flatnonzero(wk == w) for w in ub}
    m = np.empty(draws)
    for i in range(draws):
        sel = np.concatenate([by[w] for w in rng.choice(ub, size=len(ub), replace=True)])
        m[i] = r[sel].mean()
    return {"lo": float(np.percentile(m, 2.5)), "hi": float(np.percentile(m, 97.5)),
            "p_pos": 100 * float((m > 0).mean()), "weeks": len(ub)}


def naive_bootstrap(trades, draws=8000):
    r = np.array([t["r"] for t in trades])
    m = np.empty(draws)
    for i in range(draws):
        m[i] = r[rng.integers(0, len(r), len(r))].mean()
    return {"lo": float(np.percentile(m, 2.5)), "hi": float(np.percentile(m, 97.5)),
            "p_pos": 100 * float((m > 0).mean())}


def main():
    universe = json.load(open(os.path.join(DATA, "_universe.json")))
    new = [s for s in universe if s not in DERIVED_ON]

    sigs, missing = collect(new)
    print(f"universe: {len(new)} assets, {len(sigs)} raw 4h selective signals")
    if missing:
        print(f"  missing/failed: {missing}")

    kept = portfolio.apply_cap(sigs, "per_symbol")
    st = portfolio.stats(kept, len(sigs))
    ac = portfolio.simulate_account(kept)
    xs = xs_bootstrap(kept)
    nv = naive_bootstrap(kept)

    per_asset = {}
    for sym in new:
        rows = [t for t in kept if t["symbol"] == sym]
        if len(rows) >= 20:
            r = np.array([t["r"] for t in rows])
            w = r[r > 0]
            gl = abs(r[r <= 0].sum())
            per_asset[sym] = {"n": len(r), "win": 100 * len(w) / len(r),
                              "avg": float(r.mean()), "tot": float(r.sum()),
                              "pf": float(w.sum() / gl) if gl > 0 else float("nan")}
    npos = sum(1 for a in per_asset.values() if a["avg"] > 0)

    print("\n" + "=" * 96)
    print("PER ASSET - 4h, one position per symbol")
    print("=" * 96)
    print(f"{'asset':<12}{'n':>7}{'win%':>8}{'avgR':>9}{'totR':>9}{'PF':>7}")
    for s in sorted(per_asset, key=lambda k: -per_asset[k]["avg"]):
        a = per_asset[s]
        print(f"{s[:-4]:<12}{a['n']:>7}{a['win']:>8.1f}{a['avg']:>9.3f}"
              f"{a['tot']:>9.1f}{a['pf']:>7.2f}")
    print(f"\n  {npos}/{len(per_asset)} assets positive "
          f"({100 * npos / max(len(per_asset), 1):.0f}%)")

    print("\n" + "=" * 96)
    print("POOLED - PRE-REGISTERED PRIMARY TEST")
    print("=" * 96)
    print(f"  trades {st['n']:,} of {len(sigs):,} signals ({st['taken_pct']:.1f}% taken)   "
          f"weeks {xs['weeks']}")
    print(f"  win {st['win']:.1f}%   avg R {st['avg']:+.4f}   total {st['tot']:+.1f} R   "
          f"PF {st['pf']:.3f}")
    print(f"  cross-sectional 95% CI [{xs['lo']:+.4f}, {xs['hi']:+.4f}]   "
          f"P(>0) = {xs['p_pos']:.1f}%")
    print(f"  (naive per-trade CI [{nv['lo']:+.4f}, {nv['hi']:+.4f}], "
          f"P(>0) = {nv['p_pos']:.1f}% - overstated, not the criterion)")
    if ac:
        print(f"  account sim: equity {ac['equity']:.2f}x over {ac['years']:.1f}y, "
              f"CAGR {ac['cagr'] * 100:+.1f}%, max DD {ac['max_dd'] * 100:.1f}%, "
              f"peak concurrent {ac['max_conc']}")

    frac = npos / max(len(per_asset), 1)
    print("\n" + "=" * 96)
    print("VERDICT against the pre-registered criteria")
    print("=" * 96)
    if st["n"] < 1500:
        print(f"  UNDERPOWERED - {st['n']} trades, below the floor of 1,500.")
    elif st["avg"] > 0 and xs["lo"] > 0 and frac >= 0.60:
        print(f"  SUPPORTED - mean {st['avg']:+.4f} R, 95% CI excludes zero, "
              f"{frac * 100:.0f}% of assets positive.")
    elif st["avg"] > 0 and frac >= 0.60:
        print(f"  SUGGESTIVE - mean {st['avg']:+.4f} R, {frac * 100:.0f}% of assets positive, "
              f"but the 95% CI [{xs['lo']:+.4f}, {xs['hi']:+.4f}] includes zero.")
    else:
        why = []
        if st["avg"] <= 0:
            why.append("pooled mean not positive")
        if xs["lo"] <= 0:
            why.append("95% CI includes zero")
        if frac < 0.60:
            why.append(f"only {frac * 100:.0f}% of assets positive")
        print("  NOT SUPPORTED - " + "; ".join(why) + ".")

    json.dump({"pooled": {**st, **xs, **(ac or {})}, "naive": nv,
               "per_asset": per_asset, "assets_positive": npos,
               "assets_total": len(per_asset), "missing": missing},
              open(os.path.join(DATA, "test_4h_multi.json"), "w"), indent=2, default=float)
    print("\nwrote test_4h_multi.json")


if __name__ == "__main__":
    main()
