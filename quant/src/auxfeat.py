"""Merge the auxiliary series into the bar dataset and derive features.

Everything here is causal: an auxiliary observation is only attached to a bar if
its timestamp is at or before that bar's CLOSE. Funding is the sharpest trap —
`calc_time` is when the rate is settled, so a rate stamped 08:00 must not be
visible to a bar closing at 07:45. Enforced with merge_asof(direction=backward)
against the bar's close instant, then verified.

Feature families and the hypothesis each encodes:

  FUNDING  - what longs pay shorts. High positive funding means crowded longs
             paying to stay, which is both a carry cost and a squeeze setup.
  OPEN INT - position build-up vs unwind. OI rising with price is new money;
             OI falling with price is covering. Same price move, opposite
             meaning, and OHLCV cannot tell them apart.
  POSITIONING - top-trader long/short by SIZE vs by COUNT. When the two diverge,
             big accounts are positioned against the crowd, which is the
             cleanest smart-vs-dumb-money proxy that exists in public data.
  BASIS    - perp premium over index. Term-structure stress.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

AUX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "aux")


def _load(symbol, kind):
    p = os.path.join(AUX, f"{symbol}_{kind}.parquet")
    return pd.read_parquet(p) if os.path.exists(p) else None


def attach(bars, symbol, tf):
    """bars: frame with `dt` = bar OPEN. A bar stamped t closes at t+tf, so the
    information cutoff for that bar is t+tf. Merge on that instant."""
    step = pd.Timedelta(tf)
    b = bars.copy()
    b["_cut"] = (b["dt"] + step).astype("datetime64[ns, UTC]")
    b = b.sort_values("_cut")

    out = b
    for kind in ("funding", "metrics", "premium"):
        a = _load(symbol, kind)
        if a is None or not len(a):
            continue
        a = a.copy()
        a["dt"] = a["dt"].astype("datetime64[ns, UTC]")
        a = a.sort_values("dt").rename(columns={"dt": "_aux_dt"})
        out = pd.merge_asof(out, a, left_on="_cut", right_on="_aux_dt",
                            direction="backward",
                            suffixes=("", f"_{kind}"))
        # age of the auxiliary observation, in hours - large values mean stale
        out[f"age_{kind}"] = (out["_cut"] - out["_aux_dt"]).dt.total_seconds() / 3600
        out = out.drop(columns=["_aux_dt"])
    return out.sort_values("dt").reset_index(drop=True)


def features(d):
    """Derive the aux feature block. `d` is the output of attach()."""
    f = pd.DataFrame(index=d.index)
    c = d["close"]

    # ---------------- FUNDING
    if "funding" in d:
        fr = d["funding"]
        f["funding"] = fr
        f["funding_ann"] = fr * 3 * 365                    # annualised carry
        for n in (3, 9, 21):                               # ~1d, 3d, 7d of 8h prints
            f[f"funding_ma{n}"] = fr.rolling(n).mean()
        f["funding_z"] = ((fr - fr.rolling(90).mean())
                          / fr.rolling(90).std().replace(0, np.nan))
        f["funding_flip"] = np.sign(fr) * (np.sign(fr) != np.sign(fr.shift())).astype(float)
        f["funding_extreme"] = (fr.abs() > fr.abs().rolling(90).quantile(0.9)).astype(float)
        f["funding_x_ret"] = f["funding_z"] * np.sign(np.log(c).diff())

    # ---------------- OPEN INTEREST
    if "sum_open_interest" in d:
        oi = d["sum_open_interest"]
        oiv = d["sum_open_interest_value"]
        f["oi"] = oi
        f["oi_usd"] = oiv
        for n in (6, 24, 96):
            f[f"oi_chg{n}"] = oi.pct_change(n)
        f["oi_z96"] = ((oi - oi.rolling(96).mean())
                       / oi.rolling(96).std().replace(0, np.nan))
        ret = np.log(c).diff()
        # the key interaction: price direction vs OI direction
        f["oi_price_agree"] = np.sign(f["oi_chg6"]) * np.sign(ret)
        f["oi_up_price_up"] = ((f["oi_chg6"] > 0) & (ret > 0)).astype(float)
        f["oi_dn_price_up"] = ((f["oi_chg6"] < 0) & (ret > 0)).astype(float)
        # notional per unit of OI: leverage intensity proxy
        f["oi_notional_ratio"] = oiv / (oi * c).replace(0, np.nan)
        f["oi_vs_vol"] = oi / d["volume"].replace(0, np.nan) if "volume" in d else np.nan

    # ---------------- POSITIONING
    if "sum_toptrader_long_short_ratio" in d:
        tt_size = d["sum_toptrader_long_short_ratio"]
        tt_cnt = d["count_toptrader_long_short_ratio"]
        acct = d["count_long_short_ratio"]
        taker = d["sum_taker_long_short_vol_ratio"]
        f["tt_size"] = tt_size
        f["tt_count"] = tt_cnt
        f["acct_ratio"] = acct
        f["taker_ratio"] = taker
        for n in (24, 96):
            f[f"tt_size_z{n}"] = ((tt_size - tt_size.rolling(n).mean())
                                  / tt_size.rolling(n).std().replace(0, np.nan))
            f[f"acct_z{n}"] = ((acct - acct.rolling(n).mean())
                               / acct.rolling(n).std().replace(0, np.nan))
        # smart vs crowd: big accounts positioned against retail
        f["smart_vs_crowd"] = np.log(tt_size.replace(0, np.nan)) - np.log(acct.replace(0, np.nan))
        f["svc_z"] = ((f["smart_vs_crowd"] - f["smart_vs_crowd"].rolling(96).mean())
                      / f["smart_vs_crowd"].rolling(96).std().replace(0, np.nan))
        # size vs count among top traders: few big longs vs many small longs
        f["tt_size_vs_count"] = np.log(tt_size.replace(0, np.nan)) - np.log(tt_cnt.replace(0, np.nan))
        f["taker_z"] = ((taker - taker.rolling(96).mean())
                        / taker.rolling(96).std().replace(0, np.nan))

    # ---------------- BASIS
    if "premium" in d:
        pr = d["premium"]
        f["premium"] = pr
        f["premium_z"] = ((pr - pr.rolling(168).mean())
                          / pr.rolling(168).std().replace(0, np.nan))
        f["premium_ma24"] = pr.rolling(24).mean()

    # ---------------- COMBINATIONS across families
    if "funding_z" in f and "oi_chg24" in f:
        # crowded and growing = squeeze fuel; crowded and shrinking = unwind
        f["squeeze_fuel"] = f["funding_z"] * np.sign(f["oi_chg24"])
    if "funding_z" in f and "svc_z" in f:
        f["carry_vs_smart"] = f["funding_z"] * f["svc_z"]

    for cname in ("age_funding", "age_metrics", "age_premium"):
        if cname in d:
            f[cname] = d[cname]
    return f


AUX_RAW = {"funding", "funding_interval_hours", "sum_open_interest",
           "sum_open_interest_value", "count_toptrader_long_short_ratio",
           "sum_toptrader_long_short_ratio", "count_long_short_ratio",
           "sum_taker_long_short_vol_ratio", "premium", "_cut"}


def verify_causality(bars, symbol, tf, n=2000):
    """Every attached auxiliary observation must predate the bar's close."""
    d = attach(bars.head(n), symbol, tf)
    step = pd.Timedelta(tf)
    bad = {}
    for kind in ("funding", "metrics", "premium"):
        col = f"age_{kind}"
        if col not in d:
            continue
        neg = (d[col] < 0).sum()
        bad[kind] = {"negative_age": int(neg),
                     "median_age_h": float(d[col].median()),
                     "max_age_h": float(d[col].max())}
    return bad


if __name__ == "__main__":
    import data as D
    bars, _ = D.load("BTCUSDT", "1h", "DESIGN", pad_bars=0)
    print("causality audit (age must never be negative):")
    for k, v in verify_causality(bars, "BTCUSDT", "1h").items():
        print(f"  {k:9} {v}")
    d = attach(bars, "BTCUSDT", "1h")
    f = features(d)
    print(f"\naux features: {len(f.columns)}")
    print(f"coverage (non-null share, last 10k bars):")
    cov = f.tail(10000).notna().mean().sort_values()
    print(f"  worst: {dict(cov.head(4).round(3))}")
    print(f"  best:  {dict(cov.tail(3).round(3))}")
