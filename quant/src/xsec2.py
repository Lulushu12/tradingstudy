"""Cross-sectional, done properly: risk-parity legs instead of equal dollars.

The first attempt weighted each leg by equal notional. Because SOL/XRP carry
2-3x BTC's volatility, that book was implicitly short the high-vol assets, and
that tilt dominated the signal it was meant to isolate. Here each position is
sized by inverse volatility so every leg contributes the same risk, and the
long and short legs are scaled to cancel. What is left is the rank signal.

Reported gross-vs-cost so the cost story and the alpha story stay separable.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as E        # noqa: E402
import xsec as X          # noqa: E402


def weights(sig_row, vol_row, n_side):
    """Rank by signal, size by inverse vol, scale legs to equal risk."""
    ok = sig_row.notna() & vol_row.notna() & (vol_row > 0)
    if ok.sum() < 4:
        return None
    s = sig_row[ok].rank()
    iv = 1.0 / vol_row[ok]
    w = pd.Series(0.0, index=sig_row.index)
    longs = s.nlargest(n_side).index
    shorts = s.nsmallest(n_side).index
    wl = iv[longs] / iv[longs].sum()
    ws = iv[shorts] / iv[shorts].sum()
    w[longs] = wl
    w[shorts] = -ws
    # equalise risk of the two legs, then scale to unit portfolio risk
    risk_l = float((wl * vol_row[longs]).sum())
    risk_s = float((ws * vol_row[shorts]).sum())
    if risk_l <= 0 or risk_s <= 0:
        return None
    w[shorts] *= risk_l / risk_s
    tot = float((w.abs() * vol_row.reindex(w.index)).sum())
    if tot <= 0:
        return None
    return w / tot          # unit-risk book; leverage applied later


def decompose(pan, col, h, n_side=2, sign=1.0, target_vol=None):
    close = X.xs_matrix(pan, "close")
    o = pd.DataFrame({s: pan[s]["open_next"] for s in pan})
    S = X.xs_matrix(pan, col) * sign
    V = X.xs_matrix(pan, "atr_pct")
    idx = np.arange(0, len(close) - h, h)

    g, c, dates = [], [], []
    w_prev = pd.Series(0.0, index=close.columns)
    for i in idx:
        w = weights(S.iloc[i], V.iloc[i], n_side)
        if w is None:
            continue
        pr = (o.iloc[i + h] / o.iloc[i] - 1.0)
        if pr.isna().any():
            continue
        g.append(float((w * pr).sum()))
        c.append(float((w - w_prev).abs().sum()) * (E.TAKER + E.SLIP))
        dates.append(close.index[i + h])
        w_prev = w
    if not g:
        return pd.Series(dtype=float), pd.Series(dtype=float)
    return (pd.Series(g, index=pd.DatetimeIndex(dates)),
            pd.Series(c, index=pd.DatetimeIndex(dates)))


def sharpe(r, py):
    if len(r) < 20 or r.std(ddof=0) == 0:
        return np.nan
    return float(r.mean() / r.std(ddof=0) * np.sqrt(py))


def main():
    rows = []
    for tf, bpy in [("4h", 2190), ("1h", 8760), ("30min", 17520)]:
        print(f"\n=============== {tf} (risk-parity legs) ===============")
        pan_tr, _ = X.panel(tf, "TRAIN")
        pan_te, _ = X.panel(tf, "TEST")
        ic = X.xs_ic(pan_tr)
        ic["abs"] = ic["ic"].abs()
        top = ic.sort_values("abs", ascending=False).head(10)

        print(f"{'feature':<18}{'h':>4}{'IC':>8} | "
              f"{'TRAIN gross':>12}{'net':>9}{'Sharpe':>8} | "
              f"{'TEST gross':>11}{'net':>9}{'Sharpe':>8}")
        for _, r in top.iterrows():
            h, sg = int(r.h), float(np.sign(r.ic))
            gtr, ctr = decompose(pan_tr, r.feature, h, 2, sg)
            gte, cte = decompose(pan_te, r.feature, h, 2, sg)
            if len(gtr) < 30 or len(gte) < 30:
                continue
            py = bpy / h
            ntr, nte = gtr - ctr, gte - cte
            print(f"{r.feature:<18}{h:>4}{r.ic:>8.4f} | "
                  f"{100*gtr.mean()*py:>11.1f}%{100*ntr.mean()*py:>8.1f}%"
                  f"{sharpe(ntr, py):>8.2f} | "
                  f"{100*gte.mean()*py:>10.1f}%{100*nte.mean()*py:>8.1f}%"
                  f"{sharpe(nte, py):>8.2f}")
            rows.append({"tf": tf, "feature": r.feature, "h": h, "sign": sg,
                         "ic": r.ic,
                         "train_net": ntr.mean() * py, "train_sh": sharpe(ntr, py),
                         "test_net": nte.mean() * py, "test_sh": sharpe(nte, py)})

    out = pd.DataFrame(rows)
    rep = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reports")
    out.to_csv(os.path.join(rep, "xsec_riskparity.csv"), index=False)

    print("\n=== signals with POSITIVE net Sharpe in BOTH train and test ===")
    good = out[(out.train_sh > 0) & (out.test_sh > 0)].sort_values(
        "test_sh", ascending=False)
    if len(good) == 0:
        print("  none")
    else:
        for _, r in good.iterrows():
            print(f"  {r.tf:<6}{r.feature:<18}h={r.h:<4}"
                  f"train Sh {r.train_sh:+.2f} ({100*r.train_net:+.1f}%/yr)  "
                  f"test Sh {r.test_sh:+.2f} ({100*r.test_net:+.1f}%/yr)")


if __name__ == "__main__":
    main()
