"""Template-free predictability test.

Trade templates (ATR stops, fixed RR) impose path dependence that can hide or
manufacture apparent edge. This strips that away and asks the blunt question:
do these features carry ANY information about forward returns?

Two measurements:
  1. Univariate rank IC per feature per horizon, TRAIN vs TEST, with the
     sign-stability check that matters (an IC that flips sign OOS is noise).
  2. Multivariate out-of-sample R2 from a purged, embargoed walk-forward ridge.
     Purging matters: overlapping forward windows leak across a naive split.

If OOS R2 is <= 0 and ICs do not hold sign, the asset is a martingale at this
horizon and the search should move on rather than grind harder.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data as D          # noqa: E402
import features as F      # noqa: E402

HORIZONS = [1, 2, 4, 8, 24, 48, 96]


def fwd_returns(f, horizons=HORIZONS):
    c = f["close"].values.astype(float)
    out = {}
    for h in horizons:
        fr = np.full(len(c), np.nan)
        fr[:-h] = np.log(c[h:] / c[:-h])
        # normalise by prevailing vol so horizons are comparable
        out[h] = fr / f["atr_pct"].values
    return out


def rank_ic(x, y):
    m = np.isfinite(x) & np.isfinite(y)
    if m.sum() < 200:
        return np.nan
    a = pd.Series(x[m]).rank().values
    b = pd.Series(y[m]).rank().values
    a = a - a.mean()
    b = b - b.mean()
    d = np.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / d) if d > 0 else np.nan


def univariate(symbol="BTCUSDT", tf="30min"):
    rows = []
    ftr, _ = _prep(symbol, tf, "TRAIN")
    fte, _ = _prep(symbol, tf, "TEST")
    ytr = fwd_returns(ftr)
    yte = fwd_returns(fte)
    cols = F.feature_cols(ftr)
    for c in cols:
        for h in HORIZONS:
            ic_tr = rank_ic(ftr[c].values.astype(float), ytr[h])
            ic_te = rank_ic(fte[c].values.astype(float), yte[h])
            rows.append({"feature": c, "h": h, "ic_train": ic_tr,
                         "ic_test": ic_te,
                         "same_sign": bool(np.isfinite(ic_tr) and np.isfinite(ic_te)
                                           and np.sign(ic_tr) == np.sign(ic_te))})
    return pd.DataFrame(rows)


def _prep(symbol, tf, block):
    bars, m1 = D.load(symbol, tf, block)
    f = F.build(bars, m1, tf)
    f = f[f["tradeable"]].reset_index(drop=True)
    return f, bars


def walkforward_ridge(symbol="BTCUSDT", tf="30min", h=24, n_folds=8,
                      embargo=None, alphas=(1, 10, 100, 1000, 10000)):
    """Purged+embargoed expanding walk-forward. Returns OOS R2 and OOS IC."""
    f, _ = _prep(symbol, tf, "DESIGN")
    y = fwd_returns(f, [h])[h]
    cols = F.feature_cols(f)
    X = f[cols].values.astype(float)
    ok = np.isfinite(X).all(axis=1) & np.isfinite(y)
    X, y = X[ok], y[ok]
    dt = f["dt"].values[ok]
    embargo = embargo or h * 3

    n = len(y)
    fold = n // (n_folds + 1)
    oos_pred, oos_true = [], []
    for k in range(1, n_folds + 1):
        tr_end = fold * k
        te_start = tr_end + embargo          # purge the overlap window
        te_end = min(te_start + fold, n)
        if te_end - te_start < 200:
            continue
        Xtr, ytr = X[:tr_end - embargo], y[:tr_end - embargo]
        Xte, yte = X[te_start:te_end], y[te_start:te_end]
        mu, sd = Xtr.mean(0), Xtr.std(0)
        sd[sd == 0] = 1
        Xtr_s = (Xtr - mu) / sd
        Xte_s = (Xte - mu) / sd
        ym = ytr.mean()
        # inner split to pick alpha, still purged
        cut = int(len(Xtr_s) * 0.8)
        best_a, best_s = alphas[0], -np.inf
        for a in alphas:
            A = Xtr_s[:cut]
            b = ytr[:cut] - ytr[:cut].mean()
            w = np.linalg.solve(A.T @ A + a * np.eye(A.shape[1]), A.T @ b)
            p = Xtr_s[cut + embargo:] @ w
            t = ytr[cut + embargo:]
            if len(t) < 100:
                continue
            s = rank_ic(p, t)
            if np.isfinite(s) and s > best_s:
                best_s, best_a = s, a
        A = Xtr_s
        b = ytr - ym
        w = np.linalg.solve(A.T @ A + best_a * np.eye(A.shape[1]), A.T @ b)
        oos_pred.append(Xte_s @ w + ym)
        oos_true.append(yte)

    p = np.concatenate(oos_pred)
    t = np.concatenate(oos_true)
    ss_res = ((t - p) ** 2).sum()
    ss_tot = ((t - t.mean()) ** 2).sum()
    return {"h": h, "n_oos": len(t), "oos_r2": float(1 - ss_res / ss_tot),
            "oos_ic": rank_ic(p, t),
            "oos_ic_top_decile": _decile_spread(p, t)}


def _decile_spread(p, t):
    """Mean forward return of the top prediction decile minus the bottom."""
    m = np.isfinite(p) & np.isfinite(t)
    p, t = p[m], t[m]
    if len(p) < 1000:
        return np.nan
    q = np.quantile(p, [0.1, 0.9])
    return float(t[p >= q[1]].mean() - t[p <= q[0]].mean())


def main():
    for tf in ["15min", "30min", "1h", "4h"]:
        print(f"\n================ {tf} ================")
        u = univariate("BTCUSDT", tf)
        u["absic"] = u["ic_train"].abs()
        top = u.sort_values("absic", ascending=False).head(12)
        print(f"{'feature':<18}{'h':>4}{'IC_train':>10}{'IC_test':>10}  sign_holds")
        for _, r in top.iterrows():
            print(f"{r.feature:<18}{r.h:>4}{r.ic_train:>10.4f}{r.ic_test:>10.4f}"
                  f"  {'YES' if r.same_sign else 'no'}")
        strong = u[(u.absic > 0.03)]
        print(f"\nfeatures with |IC_train| > 0.03: {len(strong)} / {len(u)}")
        if len(strong):
            print(f"  of those, sign holds OOS: {int(strong.same_sign.sum())} "
                  f"({100*strong.same_sign.mean():.0f}%)  "
                  f"[coin flip = 50%]")
        print(f"  mean |IC_test| among them: {strong.ic_test.abs().mean():.4f}")

        for h in (8, 24, 96):
            r = walkforward_ridge("BTCUSDT", tf, h=h, n_folds=8)
            print(f"  ridge WF h={h:>3}: OOS R2 {r['oos_r2']:+.5f}  "
                  f"OOS IC {r['oos_ic']:+.4f}  top-bot decile spread "
                  f"{r['oos_ic_top_decile']:+.4f} ATR")


if __name__ == "__main__":
    main()
