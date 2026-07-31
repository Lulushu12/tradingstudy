"""Stress the one positive walk-forward result before believing it.

Three specific threats:

  1. SURVIVORSHIP. The universe is today's Nasdaq-100 over 28 years. If the edge
     is concentrated in the early era, when the surviving-winner bias is worst,
     it is an artefact. If it is flat or stronger recently, it is more credible.
  2. COST. Daily rebalancing turns over the book constantly. Sweep the cost
     assumption upward and find where the edge dies.
  3. CALENDAR FEATURES. `dow` and `dom` topped the importance table. Retrain
     with them removed; if the edge collapses, it was a seasonality artefact
     rather than a volume/price signal.

Also answers the practical question: what leverage would the target need, and
what drawdown comes with it.
"""
import os
import sys

import numpy as np
import pandas as pd
import lightgbm as lgb

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import eqml as E          # noqa: E402

REP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reports")


def by_era(r, label):
    if len(r) == 0:
        return
    y = r.groupby(r.index.year)
    print(f"\n  {label} — annualised return by year:")
    rows = []
    for yr, g in y:
        py = 252 / max(len(g), 1) * len(g) / max(len(g), 1)
        ann = (1 + g).prod() - 1
        rows.append((yr, ann, len(g)))
    line = "   "
    for yr, ann, n in rows:
        line += f"{yr}:{100*ann:+6.1f}  "
        if len(line) > 100:
            print(line)
            line = "   "
    if line.strip():
        print(line)
    half = len(rows) // 2
    early = np.mean([a for _, a, _ in rows[:half]])
    late = np.mean([a for _, a, _ in rows[half:]])
    print(f"    first half mean {100*early:+.1f}%/yr   "
          f"second half mean {100*late:+.1f}%/yr")
    return early, late


def main():
    df = E.load()
    f = E.features(df)
    cols = E.feat_cols(f)
    fx = E.cs_normalise(f, cols)
    X_all = np.nan_to_num(fx[cols].values.astype(np.float32), nan=0.0)

    h = 5
    y = E.forward_target(f, h)

    print("=" * 78)
    print("1.  SURVIVORSHIP: is the walk-forward edge concentrated early?")
    print("=" * 78)
    p_wf = E.walkforward(X_all, y, f["dt"])
    r = E.ls_portfolio(f, np.where(np.isfinite(p_wf), p_wf, np.nan), hold=h)
    s = E.summarise(r, h, "WF full")
    print(f"  full sample: ann {100*s['ann_ret']:+.1f}%  Sharpe {s['sharpe']:+.2f}  "
          f"maxDD {100*s['maxDD']:.1f}%")
    by_era(r, "WF h=5")

    print("\n" + "=" * 78)
    print("2.  COST SENSITIVITY: where does the edge cross zero?")
    print("=" * 78)
    print(f"  {'round-trip bps':>16}{'ann ret':>10}{'Sharpe':>9}")
    for bps in (0, 5, 10, 20, 40, 80):
        rr = E.ls_portfolio(f, np.where(np.isfinite(p_wf), p_wf, np.nan),
                            hold=h, cost=bps / 10000.0)
        ss = E.summarise(rr, h, f"cost{bps}")
        if ss:
            print(f"  {bps:>16}{100*ss['ann_ret']:>9.1f}%{ss['sharpe']:>9.2f}")

    print("\n" + "=" * 78)
    print("3.  CALENDAR FEATURES REMOVED (dow, dom)")
    print("=" * 78)
    keep = [c for c in cols if c not in ("dow", "dom")]
    Xk = np.nan_to_num(fx[keep].values.astype(np.float32), nan=0.0)
    p2 = E.walkforward(Xk, y, f["dt"])
    r2 = E.ls_portfolio(f, np.where(np.isfinite(p2), p2, np.nan), hold=h)
    s2 = E.summarise(r2, h, "no-calendar")
    if s2:
        print(f"  ann {100*s2['ann_ret']:+.1f}%  Sharpe {s2['sharpe']:+.2f}  "
              f"maxDD {100*s2['maxDD']:.1f}%   "
              f"(with calendar: {100*s['ann_ret']:+.1f}%, {s['sharpe']:+.2f})")

    print("\n" + "=" * 78)
    print("4.  VOLUME FEATURES ONLY vs PRICE FEATURES ONLY")
    print("=" * 78)
    volish = [c for c in keep if any(k in c for k in
              ("dv_", "dollar_vol", "amihud", "obv", "volret", "absorb", "vol_trend"))]
    priceish = [c for c in keep if c not in volish]
    for name, sub in (("volume only", volish), ("price only", priceish)):
        Xs = np.nan_to_num(fx[sub].values.astype(np.float32), nan=0.0)
        ps = E.walkforward(Xs, y, f["dt"])
        rs = E.ls_portfolio(f, np.where(np.isfinite(ps), ps, np.nan), hold=h)
        ss = E.summarise(rs, h, name)
        if ss:
            print(f"  {name:<14} ({len(sub):>2} feats): ann {100*ss['ann_ret']:+6.1f}%  "
                  f"Sharpe {ss['sharpe']:+.2f}  maxDD {100*ss['maxDD']:.1f}%")

    print("\n" + "=" * 78)
    print("5.  WHAT LEVERAGE WOULD THE TARGET NEED")
    print("=" * 78)
    base = s
    print(f"  unlevered: {100*base['ann_ret']:+.1f}%/yr, vol {100*base['ann_vol']:.1f}%, "
          f"maxDD {100*base['maxDD']:.1f}%")
    for target_mo in (0.02, 0.05, 0.10):
        need = ((1 + target_mo) ** 12 - 1) / max(base["ann_ret"], 1e-9)
        print(f"  for {100*target_mo:.0f}%/month ({100*((1+target_mo)**12-1):.0f}%/yr): "
              f"leverage {need:.1f}x -> implied maxDD "
              f"{100*min(base['maxDD']*need, 1.0):.0f}%"
              + ("  (RUIN)" if base["maxDD"] * need >= 1.0 else ""))


if __name__ == "__main__":
    main()
