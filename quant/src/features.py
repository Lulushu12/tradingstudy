"""Causal feature construction.

Deliberately avoids the standard oscillator/MA vocabulary. The premise is that
anything computable from close prices alone has been arbitraged flat (the
costmap confirms it: raw hit rates sit exactly on the martingale null). The
features here lean on things that are NOT recoverable from a close series:

  - aggressor imbalance (taker_buy_base vs total volume) - who crossed the spread
  - trade-size structure (quote_volume / trades) - participant composition
  - intrabar path shape measured from real 1m data - how the move was made
  - liquidity texture (range delivered per trade) - how thin the book was

Every column is computed from information available at or before the CLOSE of
bar t. Any column that peeks is a bug; `verify_causality` tries to catch it.
"""
import numpy as np
import pandas as pd


def _z(s, n):
    m = s.rolling(n).mean()
    sd = s.rolling(n).std(ddof=0)
    return (s - m) / sd.replace(0, np.nan)


def _rank(s, n):
    return s.rolling(n).rank(pct=True)


def intrabar(m1, bars, tf):
    """Path statistics for each bar, built from its constituent 1m bars."""
    step = pd.Timedelta(tf)
    g = m1.set_index("dt")
    r1 = np.log(g["close"]).diff()
    agg = pd.DataFrame({
        "absmove": r1.abs().resample(tf, label="left", closed="left").sum(),
        "rv": (r1 ** 2).resample(tf, label="left", closed="left").sum(),
        "m1_max_up": r1.resample(tf, label="left", closed="left").max(),
        "m1_max_dn": r1.resample(tf, label="left", closed="left").min(),
        "n_up": (r1 > 0).resample(tf, label="left", closed="left").sum(),
        "n_dn": (r1 < 0).resample(tf, label="left", closed="left").sum(),
    })
    # where in the bar did the extreme occur? (0 = start, 1 = end)
    def _argpos(x, fn):
        if len(x) == 0:
            return np.nan
        return float(fn(x.values)) / max(len(x) - 1, 1)
    hi_pos = g["high"].resample(tf, label="left", closed="left").apply(
        lambda x: _argpos(x, np.argmax))
    lo_pos = g["low"].resample(tf, label="left", closed="left").apply(
        lambda x: _argpos(x, np.argmin))
    agg["hi_pos"] = hi_pos
    agg["lo_pos"] = lo_pos
    return bars.merge(agg.reset_index(), on="dt", how="left")


def build(bars, m1=None, tf="30min", with_path=True):
    b = bars.copy()
    if with_path and m1 is not None:
        b = intrabar(m1, b, tf)

    c, o, h, l = b["close"], b["open"], b["high"], b["low"]
    v, qv, ntr = b["volume"], b["quote_volume"], b["trades"]
    tbb, tbq = b["taker_buy_base"], b["taker_buy_quote"]

    rng_ = (h - l).replace(0, np.nan)
    body = (c - o)
    ret = np.log(c).diff()

    f = pd.DataFrame(index=b.index)
    f["dt"] = b["dt"]
    f["close"] = c
    f["ret"] = ret

    # ---- true range / ATR in percent, the risk unit everything is scaled by
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()],
                   axis=1).max(axis=1)
    atr = tr.ewm(alpha=1 / 14, adjust=False).mean()
    f["atr"] = atr
    f["atr_pct"] = atr / c
    f["atr_rank"] = _rank(f["atr_pct"], 480)
    f["vol_of_vol"] = _z(f["atr_pct"].rolling(24).std(), 480)

    # ---- AGGRESSOR IMBALANCE. taker_buy_base is the volume that lifted the
    # offer. This is order flow, not a price transform.
    tbi = (tbb / v.replace(0, np.nan)) - 0.5
    f["tbi"] = tbi
    for n in (8, 24, 96):
        f[f"tbi_ma{n}"] = tbi.rolling(n).mean()
        f[f"tbi_z{n}"] = _z(tbi, n)
    # signed notional imbalance (buy quote minus sell quote), normalised
    sell_q = qv - tbq
    f["dq"] = (tbq - sell_q) / qv.replace(0, np.nan)
    f["dq_z96"] = _z(f["dq"], 96)
    f["dq_cum24"] = f["dq"].rolling(24).sum()

    # ---- ABSORPTION: heavy one-sided flow that fails to move price.
    # large |imbalance| with small |return| = someone is soaking it up.
    f["absorb"] = f["tbi"] / (ret.abs() / atr.div(c)).replace(0, np.nan)
    f["absorb_z"] = _z(f["absorb"], 96)
    # flow/price divergence sign: flow says buy, price went down (or vice versa)
    f["flow_div"] = np.sign(f["tbi"]) * -np.sign(ret)
    f["flow_eff"] = ret / f["tbi"].replace(0, np.nan)   # price moved per unit flow

    # ---- PARTICIPANT COMPOSITION
    ats = qv / ntr.replace(0, np.nan)
    f["avg_trade_usd"] = ats
    f["ats_z96"] = _z(ats, 96)
    f["ats_rank480"] = _rank(ats, 480)
    f["trade_intensity"] = ntr / ntr.rolling(96).mean()
    f["vol_per_trade_z"] = _z(v / ntr.replace(0, np.nan), 96)

    # ---- LIQUIDITY TEXTURE: how much range did each trade buy?
    f["range_per_trade"] = (rng_ / c) / ntr.replace(0, np.nan)
    f["rpt_z"] = _z(f["range_per_trade"], 96)
    f["rpt_rank"] = _rank(f["range_per_trade"], 480)
    f["kyle"] = (rng_ / c) / (qv.replace(0, np.nan) ** 0.5)   # impact per sqrt notional
    f["kyle_z"] = _z(f["kyle"], 96)

    # ---- BAR GEOMETRY
    f["body_frac"] = body / rng_
    f["up_wick"] = (h - np.maximum(c, o)) / rng_
    f["dn_wick"] = (np.minimum(c, o) - l) / rng_
    f["wick_skew"] = f["up_wick"] - f["dn_wick"]
    f["close_loc"] = (c - l) / rng_          # where in the range it closed
    f["range_z"] = _z(rng_ / c, 96)
    f["range_rank"] = _rank(rng_ / c, 480)
    f["gap"] = (o - c.shift()) / atr

    # ---- PATH SHAPE (needs 1m)
    if "absmove" in b:
        f["efficiency"] = (np.log(c / o).abs()) / b["absmove"].replace(0, np.nan)
        f["rv_vs_range"] = np.sqrt(b["rv"]) / (rng_ / c).replace(0, np.nan)
        f["updn_ratio"] = b["n_up"] / (b["n_up"] + b["n_dn"]).replace(0, np.nan)
        f["hi_pos"] = b["hi_pos"]
        f["lo_pos"] = b["lo_pos"]
        f["extreme_late"] = np.where(body > 0, b["hi_pos"], b["lo_pos"])
        f["m1_jump"] = b[["m1_max_up", "m1_max_dn"]].abs().max(axis=1) / f["atr_pct"]

    # ---- DISPLACEMENT / PERSISTENCE (no moving averages: raw displacement
    # and signed-vs-absolute path ratio, which is a Hurst-like statistic)
    for n in (6, 24, 96):
        f[f"disp{n}"] = (c - c.shift(n)) / atr
        f[f"persist{n}"] = (ret.rolling(n).sum().abs() /
                            ret.abs().rolling(n).sum().replace(0, np.nan))
    f["accel"] = f["disp6"] - f["disp24"] / 4

    # ---- LEVEL STRUCTURE, measured in ATR not price
    for n in (24, 96, 480):
        hh = h.rolling(n).max()
        ll = l.rolling(n).min()
        f[f"to_hi{n}"] = (hh - c) / atr
        f[f"to_lo{n}"] = (c - ll) / atr
        f[f"pos{n}"] = (c - ll) / (hh - ll).replace(0, np.nan)
        f[f"since_hi{n}"] = n - h.rolling(n).apply(lambda x: float(np.argmax(x)), raw=True)
        f[f"since_lo{n}"] = n - l.rolling(n).apply(lambda x: float(np.argmin(x)), raw=True)

    # ---- CLOCK. Crypto has hard session structure; this is free information.
    dt = pd.DatetimeIndex(b["dt"])
    f["hour"] = dt.hour
    f["dow"] = dt.dayofweek
    f["minofday"] = dt.hour * 60 + dt.minute
    f["is_weekend"] = (dt.dayofweek >= 5).astype(int)
    # sessions in UTC
    f["sess_asia"] = ((dt.hour >= 0) & (dt.hour < 8)).astype(int)
    f["sess_eu"] = ((dt.hour >= 7) & (dt.hour < 15)).astype(int)
    f["sess_us"] = ((dt.hour >= 13) & (dt.hour < 21)).astype(int)

    f["tradeable"] = b["tradeable"] if "tradeable" in b else True
    f["open_next"] = b["open"].shift(-1)
    return f


NON_FEATURE = {"dt", "close", "tradeable", "open_next", "atr", "ret"}


def feature_cols(f):
    return [c for c in f.columns if c not in NON_FEATURE]


def verify_causality(bars, m1, tf, n_trials=6, seed=0):
    """Recompute features with the tail of the data deleted. Any feature whose
    value at an early bar CHANGES when future bars are removed is peeking."""
    rng = np.random.default_rng(seed)
    full = build(bars, m1, tf)
    bad = {}
    for _ in range(n_trials):
        cut = rng.integers(int(len(bars) * 0.4), int(len(bars) * 0.9))
        b2 = bars.iloc[:cut].copy()
        m2 = m1[m1["dt"] < bars["dt"].iloc[cut]].copy()
        f2 = build(b2, m2, tf)
        k = min(len(f2), cut) - 5
        a = full.iloc[:k]
        c = f2.iloc[:k]
        for col in feature_cols(full):
            if col not in c:
                continue
            x, y = a[col].values.astype(float), c[col].values.astype(float)
            m = np.isfinite(x) & np.isfinite(y)
            if m.sum() == 0:
                continue
            d = np.abs(x[m] - y[m])
            scale = np.maximum(np.abs(x[m]), 1e-9)
            if np.nanmax(d / scale) > 1e-6:
                bad[col] = bad.get(col, 0) + 1
    return bad
