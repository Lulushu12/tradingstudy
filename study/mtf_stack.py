"""Multi-timeframe rescue attempt for the lower-TF SFP divergence entries.

The SFP-timed divergence shorts have big samples on 1h/30m/15m (236/709/1395 star
trades) but die to fees out-of-sample. Here we try to buy back edge with harder
filters, at the cost of sample:

  HTF bias:   4H trend (close<EMA200 on the last CLOSED 4H bar), and/or an ACTIVE
              4H divergence (4H SFP bear fired within the last 6 closed 4H bars).
  LTF stack:  a divergence on the timeframe below fired just before the signal
              (1h <- 15m within 2h; 30m <- 15m within 1h; 15m <- 5m within 30min).

All HTF/LTF context is merged as-of by BAR CLOSE time (only closed bars), fully
causal. Short side only (the edge family). Exits: fixed 1R, fixed 2R, and the
winning partial scheme (half@1R -> breakeven + 3-ATR trail). Train<2025 / Test.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import indicators as ind
from engine import FEE_RT
from research import breakeven_wr
from trend_runner import run_fixed
from sfp_divergence import sfp_divergence, make_30m
from sfp_exits import run_half1R_trail

SEC = {"4H": 14400, "1h": 3600, "30m": 1800, "15m": 900, "5m": 300}
STACK_SRC = {"1h": ("15m", 8), "30m": ("15m", 4), "15m": ("5m", 6)}  # (src, K bars)
HTF_DIV_K = 6                     # 4H divergence considered active for 6 closed bars

def asof_flag(src_close_t, src_flag, dst_close_t):
    """Value of src_flag on the last CLOSED source bar at each dst bar close."""
    idx = np.searchsorted(src_close_t, dst_close_t, side="right") - 1
    out = np.zeros(len(dst_close_t), bool)
    ok = idx >= 0
    out[ok] = src_flag[idx[ok]]
    return out

def recent(flag, k):
    return pd.Series(flag.astype(float)).rolling(k, min_periods=1).max().values > 0

_cache = {}
def load(tf):
    if tf not in _cache:
        if tf == "30m":
            make_30m()
        df = ind.enrich(pd.read_parquet(f"data/{tf}.parquet"))
        m = sfp_divergence(df)
        _cache[tf] = (df, m)
    return _cache[tf]

def report(tag, tr, p_be=None):
    cut = pd.Timestamp("2024-12-31", tz="UTC").timestamp()
    out = []
    for lab, sub in [("TR", tr[tr.entry_time < cut]), ("TE", tr[tr.entry_time >= cut])]:
        if not len(sub):
            out.append(f"{lab}: (none)"); continue
        R = sub["net_R"].values
        out.append(f"{lab}: n={len(sub):4d} WR={(R>0).mean():5.1%} expR={R.mean():+.3f}")
    a = tr[tr.entry_time < cut]; b = tr[tr.entry_time >= cut]
    ok = len(a) >= 20 and len(b) >= 20 and a["net_R"].mean() > 0 and b["net_R"].mean() > 0
    be = f"(be {p_be:.0%})" if p_be else ""
    print(f"    {tag:34}{be:10} | " + " | ".join(out) + ("   <<<" if ok else ""))

def run_tf(tf):
    df, m = load(tf)
    n = len(df)
    close_t = df["time"].values + SEC[tf]
    bear = m["bear0"] | m["bear1"]
    dn_loc = (df["close"] < df["ema200"]).values

    # 4H context
    df4, m4 = load("4H")
    close4 = df4["time"].values + SEC["4H"]
    dn4 = asof_flag(close4, (df4["close"] < df4["ema200"]).values, close_t)
    div4 = asof_flag(close4, recent((m4["bear0"] | m4["bear1"]), HTF_DIV_K), close_t)

    # lower-TF divergence stack
    src, K = STACK_SRC[tf]
    dfs, ms = load(src)
    closes = dfs["time"].values + SEC[src]
    stack = asof_flag(closes, recent((ms["bear0"] | ms["bear1"]), K), close_t)

    star = bear & dn_loc
    F = {
        "star (local dn)  [ref]":      star,
        "bear & 4H dn":                bear & dn4,
        "star & 4H dn":                star & dn4,
        "star & 4H dn & 4H div":       star & dn4 & div4,
        f"star & {src}-div stack":     star & stack,
        f"star & 4H dn & {src} stack": star & dn4 & stack,
        "full stack (all filters)":    star & dn4 & div4 & stack,
    }
    sfmean = (1.5*df["atr14"]/df["open"].shift(-1)).mean()
    print(f"\n################ TF={tf}  feeR~{FEE_RT/sfmean:.2f}  "
          f"(signals: star={int(star.sum())}) ################")
    for fname, mask in F.items():
        Lz = np.zeros(n, bool)
        print(f"  -- {fname}  (n={int(mask.sum())})")
        for rr in [1.0, 2.0]:
            report(f"fixed {rr:.0f}R", run_fixed(df, Lz, mask, rr=rr),
                   breakeven_wr(rr, sfmean))
        report("half@1R->BE + 3ATRtrail", run_half1R_trail(df, Lz, mask, k=3.0))

if __name__ == "__main__":
    import sys
    for tf in (sys.argv[1:] or ["1h", "30m", "15m"]):
        run_tf(tf)
