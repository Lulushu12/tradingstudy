"""Univariate conditional-expectancy scan with a family-wise permutation null.

The trap this is built to avoid: scanning ~1400 (feature, bin, side) cells and
reporting the best one. The best of 1400 pure-noise cells looks excellent. So
the same scan is re-run many times on block-shuffled labels, and the
distribution of the BEST-OF-SCAN statistic under that null is what a candidate
must beat. A cell that clears the 95th percentile of the shuffled maximum is
interesting; anything less is scenery.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data as D          # noqa: E402
import features as F      # noqa: E402
import labels as L        # noqa: E402


def prep(symbol="BTCUSDT", tf="30min", block="TRAIN", atr_mult=2.0, rr=2.0,
         hold=96, unlock=None):
    bars, m1 = D.load(symbol, tf, block, unlock=unlock)
    f = F.build(bars, m1, tf)
    lb = L.make(symbol, tf, block, atr_mult=atr_mult, rr=rr,
                max_hold_bars=hold, unlock=unlock)
    f = f[f["tradeable"]].copy()
    key_f = f["dt"].astype("int64").values
    key_l = lb["dt"].astype("int64").values
    common = np.intersect1d(key_f, key_l)
    f = f[np.isin(key_f, common)].reset_index(drop=True)
    lb = lb[np.isin(key_l, common)].reset_index(drop=True)
    assert (f["dt"].values == lb["dt"].values).all()
    return f, lb


def _bins(x, edges):
    return np.digitize(x, edges, right=False)


def scan(f, lb, cols=None, nq=10, min_n=250):
    cols = cols or F.feature_cols(f)
    rows = []
    for side, rcol in (("long", "r_long"), ("short", "r_short")):
        r = lb[rcol].values.astype(float)
        base = np.nanmean(r)
        for c in cols:
            x = f[c].values.astype(float)
            ok = np.isfinite(x) & np.isfinite(r)
            if ok.sum() < min_n * 3:
                continue
            xv = x[ok]
            uniq = np.unique(xv)
            if len(uniq) <= 12:
                edges = uniq[1:]
            else:
                qs = np.linspace(0, 1, nq + 1)[1:-1]
                edges = np.unique(np.quantile(xv, qs))
            if len(edges) == 0:
                continue
            b = _bins(x, edges)
            for k in np.unique(b[ok]):
                m = ok & (b == k)
                n = int(m.sum())
                if n < min_n:
                    continue
                mu = float(np.nanmean(r[m]))
                rows.append({
                    "feature": c, "side": side, "bin": int(k),
                    "lo": float(edges[k - 1]) if k > 0 else -np.inf,
                    "hi": float(edges[k]) if k < len(edges) else np.inf,
                    "n": n, "exp_r": mu, "lift": mu - base,
                    "wr": float(np.nanmean(lb[f"out_{side}"].values[m] == 1)),
                })
    return pd.DataFrame(rows)


def perm_null(f, lb, cols=None, n_perm=60, block=96, nq=10, min_n=250, seed=0):
    """Distribution of the best-in-scan expectancy under block-shuffled labels."""
    cols = cols or F.feature_cols(f)
    rng = np.random.default_rng(seed)
    n = len(lb)
    nb = int(np.ceil(n / block))
    best = []
    for i in range(n_perm):
        order = rng.permutation(nb)
        idx = np.concatenate([np.arange(o * block, min((o + 1) * block, n))
                              for o in order])[:n]
        lb2 = lb.iloc[idx].reset_index(drop=True)
        s = scan(f, lb2, cols=cols, nq=nq, min_n=min_n)
        if len(s):
            best.append(s["exp_r"].max())
    return np.array(best)


def run(symbol="BTCUSDT", tf="30min", atr_mult=2.0, rr=2.0, hold=96,
        n_perm=40, out=None):
    ftr, lbr = prep(symbol, tf, "TRAIN", atr_mult, rr, hold)
    fte, lbte = prep(symbol, tf, "TEST", atr_mult, rr, hold)

    base_tr = np.nanmean(lbr[["r_long", "r_short"]].values)
    s = scan(ftr, lbr)
    s = s.sort_values("exp_r", ascending=False).reset_index(drop=True)

    # apply the SAME cell definition to TEST
    te = []
    for _, row in s.iterrows():
        x = fte[row["feature"]].values.astype(float)
        r = lbte[f"r_{row['side']}"].values.astype(float)
        m = np.isfinite(x) & np.isfinite(r) & (x >= row["lo"]) & (x < row["hi"])
        te.append({"n_test": int(m.sum()),
                   "exp_r_test": float(np.nanmean(r[m])) if m.sum() >= 40 else np.nan})
    s = pd.concat([s, pd.DataFrame(te)], axis=1)

    null = perm_null(ftr, lbr, n_perm=n_perm)
    thr95 = float(np.percentile(null, 95)) if len(null) else np.nan
    thr99 = float(np.percentile(null, 99)) if len(null) else np.nan

    print(f"\n=== {symbol} {tf} atr{atr_mult} rr{rr} hold{hold} ===")
    print(f"baseline expR (all bars, both sides): {base_tr:+.4f}")
    print(f"permutation null: best-of-scan expR  mean {null.mean():+.4f}  "
          f"p95 {thr95:+.4f}  p99 {thr99:+.4f}   ({len(null)} shuffles)")
    print(f"cells scanned: {len(s)}")
    print(f"\ncells beating the p95 family-wise null: "
          f"{int((s.exp_r > thr95).sum())}")
    show = s.head(25)
    print(f"\n{'feature':<18}{'side':<6}{'n':>6}{'expR':>9}{'wr':>7}"
          f"{'n_te':>7}{'expR_te':>9}  range")
    for _, r_ in show.iterrows():
        print(f"{r_.feature:<18}{r_.side:<6}{r_.n:>6}{r_.exp_r:>9.3f}{r_.wr:>7.3f}"
              f"{r_.n_test:>7}{r_.exp_r_test:>9.3f}  "
              f"[{r_.lo:.3g},{r_.hi:.3g})")
    if out:
        s.to_csv(out, index=False)
        np.save(out.replace(".csv", "_null.npy"), null)
    return s, null


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--tf", default="30min")
    p.add_argument("--symbol", default="BTCUSDT")
    p.add_argument("--atr", type=float, default=2.0)
    p.add_argument("--rr", type=float, default=2.0)
    p.add_argument("--hold", type=int, default=96)
    p.add_argument("--perm", type=int, default=40)
    a = p.parse_args()
    rep = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reports")
    os.makedirs(rep, exist_ok=True)
    run(a.symbol, a.tf, a.atr, a.rr, a.hold, a.perm,
        out=os.path.join(rep, f"scan_{a.symbol}_{a.tf}_a{a.atr}_rr{a.rr}_h{a.hold}.csv"))
