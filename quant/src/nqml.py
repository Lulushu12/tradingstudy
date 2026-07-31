"""NQ futures, 1h bars, same machinery as the crypto study.

This is the venue where the cost argument is strongest. A round turn on NQ is
roughly $4 commission on ~$500k notional plus a 0.25pt spread, about 0.005%,
against 0.12% on crypto perps. Cost drag killed every crypto edge, so if cheap
execution is the missing ingredient it should show up here.

Data is thin: Yahoo serves ~2.4 years of hourly futures. That is a real limit and
it is stated with the result rather than papered over.
"""
import os
import sys

import numpy as np
import pandas as pd
import lightgbm as lgb

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "equity")
REP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reports")

COST = 0.00005          # 0.005% per side, all-in for NQ
PARAMS = dict(objective="regression", learning_rate=0.03, num_leaves=8,
              max_depth=3, min_data_in_leaf=200, feature_fraction=0.7,
              bagging_fraction=0.8, bagging_freq=1, lambda_l2=20.0,
              verbosity=-1, num_threads=4)


def build():
    d = pd.read_parquet(os.path.join(DATA, "nq_1h.parquet")).sort_values("dt")
    d = d.reset_index(drop=True)
    c, h, l, o, v = d.close, d.high, d.low, d.open, d.volume
    f = pd.DataFrame({"dt": d.dt, "close": c})
    ret = np.log(c).diff()
    f["ret"] = ret
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()],
                   axis=1).max(axis=1)
    atr = tr.ewm(alpha=1 / 14, adjust=False).mean()
    f["atr_pct"] = atr / c
    f["atr_rank"] = f.atr_pct.rolling(480).rank(pct=True)
    rng_ = (h - l).replace(0, np.nan)

    # VOLUME BLOCK
    f["vol_ratio24"] = v / v.rolling(24).mean().replace(0, np.nan)
    f["vol_ratio120"] = v / v.rolling(120).mean().replace(0, np.nan)
    f["vol_z"] = (v - v.rolling(120).mean()) / v.rolling(120).std().replace(0, np.nan)
    sgn = np.sign(ret) * v
    for n in (6, 24, 120):
        f[f"obv{n}"] = sgn.rolling(n).sum() / v.rolling(n).sum().replace(0, np.nan)
    f["amihud"] = ret.abs() / (v * c).replace(0, np.nan)
    f["amihud_z"] = (f.amihud - f.amihud.rolling(120).mean()) / \
        f.amihud.rolling(120).std().replace(0, np.nan)
    f["range_per_vol"] = (rng_ / c) / v.replace(0, np.nan)
    f["rpv_z"] = (f.range_per_vol - f.range_per_vol.rolling(120).mean()) / \
        f.range_per_vol.rolling(120).std().replace(0, np.nan)
    f["absorb"] = f.vol_z / (ret.abs() / f.atr_pct).replace(0, np.nan)

    # geometry
    f["body"] = (c - o) / rng_
    f["up_wick"] = (h - np.maximum(c, o)) / rng_
    f["dn_wick"] = (np.minimum(c, o) - l) / rng_
    f["close_loc"] = (c - l) / rng_
    f["range_z"] = ((rng_ / c) - (rng_ / c).rolling(120).mean()) / \
        (rng_ / c).rolling(120).std().replace(0, np.nan)
    f["gap"] = (o - c.shift()) / atr

    # displacement / persistence
    for n in (6, 24, 120):
        f[f"disp{n}"] = (c - c.shift(n)) / atr
        f[f"persist{n}"] = ret.rolling(n).sum().abs() / \
            ret.abs().rolling(n).sum().replace(0, np.nan)
    for n in (24, 120):
        hh, ll = h.rolling(n).max(), l.rolling(n).min()
        f[f"pos{n}"] = (c - ll) / (hh - ll).replace(0, np.nan)
        f[f"to_hi{n}"] = (hh - c) / atr
        f[f"to_lo{n}"] = (c - ll) / atr

    dt = pd.DatetimeIndex(d.dt)
    f["hour"] = dt.hour
    f["dow"] = dt.dayofweek
    f["atr"] = atr
    f["hi_px"] = h
    f["lo_px"] = l
    f["open_next"] = o.shift(-1)
    return f.dropna().reset_index(drop=True)


FEATS_EX = {"dt", "close", "ret", "atr", "open_next", "hi_px", "lo_px"}


def label(f, atr_mult=2.0, rr=2.0, max_bars=48):
    """Resolve a 2:1 trade from each bar on the hourly path (no finer data)."""
    n = len(f)
    entry = f.open_next.values
    stopd = atr_mult * f.atr.values
    out = {}
    for side in (1, -1):
        r = np.full(n, np.nan)
        stop = entry - side * stopd
        tgt = entry + side * rr * stopd
        for i in range(n - 1):
            e = entry[i]
            if not np.isfinite(e) or stopd[i] <= 0:
                continue
            j_end = min(i + max_bars, n - 1)
            res = 0.0
            hit = False
            H = f.hi_px.values
            L = f.lo_px.values
            for j in range(i + 1, j_end + 1):
                hh, ll = H[j], L[j]
                if side > 0:
                    if ll <= stop[i]:
                        res, hit = -1.0, True
                        break
                    if hh >= tgt[i]:
                        res, hit = rr, True
                        break
                else:
                    if hh >= stop[i]:
                        res, hit = -1.0, True
                        break
                    if ll <= tgt[i]:
                        res, hit = rr, True
                        break
            if not hit:
                res = side * (f.close.values[j_end] - e) / stopd[i]
            cost_r = 2 * COST * e / stopd[i]
            r[i] = res - cost_r
        out[side] = r
    return out["1" if False else 1], out[-1]


def walkforward(X, y, dt, train_frac=0.4, step=500):
    pred = np.full(len(y), np.nan)
    start = int(len(y) * train_frac)
    i = start
    while i < len(y):
        j = min(i + step, len(y))
        trm = np.zeros(len(y), bool)
        trm[:max(i - 48, 0)] = True
        trm &= np.isfinite(y)
        if trm.sum() > 1500:
            b = lgb.train(PARAMS, lgb.Dataset(X[trm], label=y[trm]), 200)
            pred[i:j] = b.predict(X[i:j])
        i = j
    return pred


def main():
    f = build()
    feats = [c for c in f.columns if c not in FEATS_EX]
    print(f"NQ 1h: {len(f):,} bars  {f.dt.min()} -> {f.dt.max()}  "
          f"{len(feats)} features "
          f"({sum(1 for c in feats if any(k in c for k in ('vol','obv','amihud','rpv','absorb')))} volume-derived)")
    rl, rs = label(f)
    print(f"unconditional expR: long {np.nanmean(rl):+.4f}  short {np.nanmean(rs):+.4f}")
    X = np.nan_to_num(f[feats].values.astype(np.float32), nan=0.0)
    months = (f.dt.max() - f.dt.min()).days / 30.44

    res = []
    for mode in ("IS", "WF"):
        if mode == "IS":
            pl = lgb.train(PARAMS, lgb.Dataset(X[np.isfinite(rl)],
                           label=rl[np.isfinite(rl)]), 200).predict(X)
            ps = lgb.train(PARAMS, lgb.Dataset(X[np.isfinite(rs)],
                           label=rs[np.isfinite(rs)]), 200).predict(X)
        else:
            pl = walkforward(X, rl, f.dt)
            ps = walkforward(X, rs, f.dt)
        score = np.where(pl >= ps, pl, ps)
        side = np.where(pl >= ps, 1, -1)
        r = np.where(side > 0, rl, rs)
        for thr in (0.0, 0.1, 0.2, 0.3):
            m = np.isfinite(score) & (score >= thr) & np.isfinite(r)
            if m.sum() < 100:
                continue
            sel = r[m]
            cum = np.cumsum(sel)
            dd = float(np.max(np.maximum.accumulate(cum) - cum))
            moR = sel.sum() / months
            res.append({"mode": mode, "thr": thr, "n": int(m.sum()),
                        "expR": float(sel.mean()), "moR": moR, "ddR": dd,
                        "ratio": moR / dd if dd > 0 else np.nan})
            print(f"  {mode} thr={thr:.1f}  n={m.sum():<6} expR {sel.mean():+.4f}  "
                  f"monthly {moR:+6.2f}R  maxDD {dd:6.1f}R  "
                  f"ratio {moR/dd if dd>0 else float('nan'):.3f}  "
                  f"-> at 6% floor: risk {100*min(0.06/dd,0.02) if dd>0 else 0:.3f}% "
                  f"= {100*min(0.06/dd,0.02)*moR if dd>0 else 0:+.2f}%/mo")
    pd.DataFrame(res).to_csv(os.path.join(REP, "nqml.csv"), index=False)


if __name__ == "__main__":
    main()
