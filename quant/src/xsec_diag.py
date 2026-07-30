"""Diagnostic: is the cross-sectional loss alpha or is it cost?

Decompose the long/short result into gross return and cost, and check the
gross number against what the measured IC predicts. If gross alpha is positive
but smaller than turnover cost, the finding is 'real but untradeable'. If gross
alpha is negative while IC is strongly positive, there is a bug and every
cross-sectional number must be thrown out.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as E        # noqa: E402
import xsec as X          # noqa: E402


def decompose(pan, col, h, n_side=2, sign=1.0, gross_notional=1.0):
    """Same portfolio as xsec.ls_backtest but reporting gross and cost apart,
    and normalising so that sum|w| == gross_notional (no accidental leverage)."""
    close = X.xs_matrix(pan, "close")
    o = pd.DataFrame({s: pan[s]["open_next"] for s in pan})
    Xm = X.xs_matrix(pan, col) * sign
    idx = np.arange(0, len(close) - h, h)

    g, c, dates = [], [], []
    w_prev = pd.Series(0.0, index=close.columns)
    for i in idx:
        x = Xm.iloc[i]
        if x.notna().sum() < 4:
            continue
        r = x.rank()
        w = pd.Series(0.0, index=close.columns)
        w[r.nlargest(n_side).index] = 1.0
        w[r.nsmallest(n_side).index] = -1.0
        w = w / w.abs().sum() * gross_notional      # sum|w| = gross_notional
        pr = (o.iloc[i + h] / o.iloc[i] - 1.0)
        g.append(float((w * pr).sum()))
        c.append(float((w - w_prev).abs().sum()) * (E.TAKER + E.SLIP))
        dates.append(close.index[i + h])
        w_prev = w
    return (pd.Series(g, index=pd.DatetimeIndex(dates)),
            pd.Series(c, index=pd.DatetimeIndex(dates)))


def main():
    for tf, bars_per_year in [("4h", 2190), ("1h", 8760), ("30min", 17520)]:
        print(f"\n=============== {tf} ===============")
        pan_tr, _ = X.panel(tf, "TRAIN")
        pan_te, _ = X.panel(tf, "TEST")
        ic = X.xs_ic(pan_tr)
        ic["abs"] = ic["ic"].abs()
        top = ic.sort_values("abs", ascending=False).head(8)

        print(f"{'feature':<18}{'h':>4}{'IC':>8} | "
              f"{'gross/reb':>10}{'cost/reb':>10}{'net/reb':>9}{'grossSh':>9} | "
              f"{'TEST gross':>11}{'TEST net':>10}{'TESTgrSh':>9}")
        for _, r in top.iterrows():
            h, sg = int(r.h), float(np.sign(r.ic))
            gtr, ctr = decompose(pan_tr, r.feature, h, n_side=2, sign=sg)
            gte, cte = decompose(pan_te, r.feature, h, n_side=2, sign=sg)
            if len(gtr) < 20 or len(gte) < 20:
                continue
            py = bars_per_year / h
            gsh = gtr.mean() / gtr.std(ddof=0) * np.sqrt(py) if gtr.std() > 0 else np.nan
            gshte = gte.mean() / gte.std(ddof=0) * np.sqrt(py) if gte.std() > 0 else np.nan
            print(f"{r.feature:<18}{h:>4}{r.ic:>8.4f} | "
                  f"{100*gtr.mean():>9.4f}%{100*ctr.mean():>9.4f}%"
                  f"{100*(gtr-ctr).mean():>8.4f}%{gsh:>9.2f} | "
                  f"{100*gte.mean():>10.4f}%{100*(gte-cte).mean():>9.4f}%"
                  f"{gshte:>9.2f}")

        # Rebalance-frequency sweep on the single best signal: cost scales with
        # turnover, gross alpha decays with horizon. Find the crossover, if any.
        best = top.iloc[0]
        sg = float(np.sign(best.ic))
        print(f"\nholding-period sweep for {best.feature} (sign {sg:+.0f}), "
              f"gross vs cost per rebalance:")
        for h in [4, 8, 24, 48, 96, 192, 384]:
            if h >= len(X.xs_matrix(pan_te, 'close')) // 4:
                continue
            gtr, ctr = decompose(pan_tr, best.feature, h, n_side=2, sign=sg)
            gte, cte = decompose(pan_te, best.feature, h, n_side=2, sign=sg)
            if len(gtr) < 20 or len(gte) < 20:
                continue
            py = bars_per_year / h
            ann_g = gtr.mean() * py
            ann_n = (gtr - ctr).mean() * py
            ann_gte = gte.mean() * py
            ann_nte = (gte - cte).mean() * py
            print(f"  h={h:>4}  TRAIN gross {100*ann_g:>+7.1f}%/yr  "
                  f"net {100*ann_n:>+7.1f}%/yr   |   "
                  f"TEST gross {100*ann_gte:>+7.1f}%/yr  net {100*ann_nte:>+7.1f}%/yr")


if __name__ == "__main__":
    main()
