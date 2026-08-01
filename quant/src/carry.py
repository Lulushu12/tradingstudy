"""Funding carry: the delta-neutral basis trade.

Not a directional system. Long spot, short perpetual, collect funding. The perp
tracks spot, so the position has near-zero price exposure and the return is the
funding stream itself. This is the trade institutions actually run at scale in
crypto, and it is the only strategy in this study with a mechanical reason to be
reliably positive: funding is the price leveraged longs pay to stay long, and in
a market structurally biased long it is positive most of the time.

Costs modelled: two legs to open and two to close (4 x taker), plus the spot
borrow/exchange spread. Held positions accrue funding every 8 hours.

What this cannot do is reach 10%/month. What it can do is produce a high-Sharpe
stream that composes with a directional book instead of competing with it.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import auxfeat as A       # noqa: E402
import engine as E        # noqa: E402

REP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reports")
SYMS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT"]


def carry_stats(symbol):
    f = A._load(symbol, "funding")
    if f is None or not len(f):
        return None
    fr = f.set_index("dt")["funding"].sort_index()
    ann = fr.mean() * 3 * 365
    pos_share = float((fr > 0).mean())
    monthly = fr.resample("ME").sum()
    return {"symbol": symbol, "n_prints": len(fr),
            "mean_funding": float(fr.mean()), "ann_gross": float(ann),
            "pct_positive": pos_share,
            "monthly_mean": float(monthly.mean()),
            "monthly_std": float(monthly.std()),
            "worst_month": float(monthly.min()),
            "sharpe": float(monthly.mean() / monthly.std() * np.sqrt(12))
            if monthly.std() > 0 else np.nan,
            "monthly": monthly}


def main():
    rows, curves = [], {}
    for s in SYMS:
        st = carry_stats(s)
        if st is None:
            continue
        curves[s] = st.pop("monthly")
        rows.append(st)
    df = pd.DataFrame(rows)
    print("=== funding carry, long spot / short perp, GROSS of costs ===")
    print(f"{'symbol':<10}{'ann gross':>11}{'% pos':>8}{'mo mean':>10}"
          f"{'mo std':>9}{'worst mo':>10}{'Sharpe':>8}")
    for _, r in df.iterrows():
        print(f"{r.symbol:<10}{100*r.ann_gross:>10.2f}%{100*r.pct_positive:>7.0f}%"
              f"{100*r.monthly_mean:>9.3f}%{100*r.monthly_std:>8.3f}%"
              f"{100*r.worst_month:>9.3f}%{r.sharpe:>8.2f}")

    # equal-weight basket
    M = pd.DataFrame(curves).dropna(how="all")
    bask = M.mean(axis=1)
    # costs: 4 taker legs per round trip, amortised over the holding period
    print("\n=== basket (equal weight), NET of costs at various turnover ===")
    print(f"{'rebalance':>12}{'ann net':>10}{'Sharpe':>9}{'worst mo':>10}")
    for days, label in ((30, "monthly"), (90, "quarterly"), (365, "yearly")):
        rt_cost = 4 * E.TAKER + 2 * E.SLIP
        per_year = 365 / days
        net_m = bask - (rt_cost * per_year / 12)
        ann = net_m.mean() * 12
        sh = net_m.mean() / net_m.std() * np.sqrt(12) if net_m.std() > 0 else np.nan
        print(f"{label:>12}{100*ann:>9.2f}%{sh:>9.2f}{100*net_m.min():>9.2f}%")

    print("\n=== what leverage would the targets need ===")
    rt_cost = 4 * E.TAKER + 2 * E.SLIP
    net_m = bask - (rt_cost * 12 / 12)
    ann = net_m.mean() * 12
    vol = net_m.std() * np.sqrt(12)
    print(f"  unlevered: {100*ann:.2f}%/yr, vol {100*vol:.2f}%, "
          f"Sharpe {ann/vol if vol>0 else float('nan'):.2f}")
    for tgt in (0.02, 0.05, 0.10):
        need = ((1 + tgt) ** 12 - 1) / max(ann, 1e-9)
        print(f"  {100*tgt:.0f}%/month needs {need:.1f}x leverage "
              f"-> vol {100*vol*need:.0f}%/yr"
              + ("   (liquidation risk dominates)" if need > 5 else ""))
    df.to_csv(os.path.join(REP, "carry.csv"), index=False)


if __name__ == "__main__":
    main()
