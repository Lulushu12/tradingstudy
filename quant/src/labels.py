"""Precompute the outcome of a trade opened at EVERY bar.

Once R_long[t] and R_short[t] exist for a given (atr_mult, rr, max_hold), any
candidate strategy collapses to a boolean mask over bars and its expectancy is
just a masked mean. That turns the search from 'minutes per hypothesis' into
'microseconds per hypothesis', which is what makes real brute force possible.

Trades overlap heavily, so the effective sample is far smaller than the row
count. Significance is therefore done by BLOCK bootstrap, never by a naive
t-stat on overlapping observations.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data as D          # noqa: E402
import engine as E        # noqa: E402

CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "labels")


def make(symbol, tf, block, atr_mult=2.0, rr=2.0, max_hold_bars=48,
         delay_min=1, unlock=None, force=False):
    os.makedirs(CACHE, exist_ok=True)
    key = f"{symbol}_{tf}_{block}_a{atr_mult}_rr{rr}_h{max_hold_bars}_d{delay_min}"
    path = os.path.join(CACHE, key + ".parquet")
    if os.path.exists(path) and not force:
        return pd.read_parquet(path)

    bars, m1 = D.load(symbol, tf, block, unlock=unlock)
    step = pd.Timedelta(tf)
    tr = pd.concat([bars.high - bars.low,
                    (bars.high - bars.close.shift()).abs(),
                    (bars.low - bars.close.shift()).abs()], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1 / 14, adjust=False).mean()

    b = bars.copy()
    b["atr"] = atr
    b = b[b["tradeable"] & b["atr"].notna() & (b["atr"] > 0)].reset_index(drop=True)

    sd = atr_mult * b["atr"].values
    hold_min = int(max_hold_bars * pd.Timedelta(tf).total_seconds() / 60)

    frames = {}
    for side in (1, -1):
        sig = pd.DataFrame({
            "close_dt": b["dt"] + step,
            "side": side,
            "stop_px": b["close"].values - side * sd,
            "target_px": b["close"].values + side * rr * sd,
            "bar_key": b["dt"].astype("int64"),
        })
        t = E.resolve(sig, m1, delay_min=delay_min, max_hold_min=hold_min)
        frames[side] = t.set_index("bar_key")

    out = pd.DataFrame({"dt": b["dt"]})
    out.index = b["dt"].astype("int64")
    for side, nm in ((1, "long"), (-1, "short")):
        t = frames[side]
        out[f"r_{nm}"] = t["r"]
        out[f"out_{nm}"] = t["outcome"]
        out[f"hold_{nm}"] = t["hold_min"]
        out[f"exit_{nm}"] = t["exit_dt"]
        out[f"stoppct_{nm}"] = t["stop_pct"]
    out = out.reset_index(drop=True)
    out.to_parquet(path, index=False, compression="zstd")
    return out


# ------------------------------------------------------------------ statistics

def block_bootstrap(r, n_boot=2000, block=48, seed=0):
    """CI for the mean of an overlapping-trade R series. Blocks of `block` bars
    keep the overlap structure intact instead of pretending it away."""
    r = np.asarray(r, float)
    r = r[np.isfinite(r)]
    n = len(r)
    if n < block * 3:
        return np.nan, np.nan, np.nan
    rng = np.random.default_rng(seed)
    nb = int(np.ceil(n / block))
    starts = rng.integers(0, n - block, size=(n_boot, nb))
    idx = (starts[:, :, None] + np.arange(block)[None, None, :]).reshape(n_boot, -1)[:, :n]
    means = r[idx].mean(axis=1)
    return float(means.mean()), float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def eval_mask(mask, r, block=48, n_boot=800, seed=0):
    """Expectancy of a strategy defined by a boolean mask, with block-bootstrap CI."""
    m = np.asarray(mask, bool) & np.isfinite(r)
    n = int(m.sum())
    if n < 30:
        return {"n": n, "exp_r": np.nan, "lo": np.nan, "hi": np.nan, "p_pos": np.nan}
    sel = np.asarray(r, float)[m]
    mu = float(sel.mean())
    # bootstrap over the SELECTED trades in time order, block-resampled
    rng = np.random.default_rng(seed)
    bl = max(4, min(block, n // 6))
    nb = int(np.ceil(n / bl))
    starts = rng.integers(0, max(n - bl, 1), size=(n_boot, nb))
    idx = (starts[:, :, None] + np.arange(bl)[None, None, :]).reshape(n_boot, -1)[:, :n]
    idx = np.clip(idx, 0, n - 1)
    means = sel[idx].mean(axis=1)
    return {"n": n, "exp_r": mu,
            "lo": float(np.percentile(means, 2.5)),
            "hi": float(np.percentile(means, 97.5)),
            "p_pos": float((means > 0).mean())}


if __name__ == "__main__":
    import itertools
    syms = ["BTCUSDT"]
    for sym, tf, am, rr in itertools.product(syms, ["30min"], [2.0], [2.0]):
        for blk in ["TRAIN", "TEST"]:
            lb = make(sym, tf, blk, atr_mult=am, rr=rr, max_hold_bars=48)
            print(f"{sym} {tf} {blk} a{am} rr{rr}: {len(lb):,} bars  "
                  f"long expR {lb.r_long.mean():+.4f}  short expR {lb.r_short.mean():+.4f}  "
                  f"long WR {(lb.out_long==1).mean():.3f}  short WR {(lb.out_short==1).mean():.3f}")
