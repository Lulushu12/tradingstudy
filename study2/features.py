"""Feature engineering. All features are CAUSAL: value at bar i uses only
data with timestamp <= close time of bar i.

Families:
  F  funding          (funding rate level / momentum / extremes / time-to-funding)
  B  basis            (premium index klines: perp-index premium)
  M  metrics          (open interest, long-short ratios, taker vol ratio; 2021-12+)
  O  order flow       (taker-buy ratio, trade count, avg trade size from klines)
  P  path shape       (5m micro-path inside recent window: wicks, sweeps, vov)
  C  calendar         (hour, dow, funding slot, weekend, month-end)
  X  cross-asset      (BTC lead returns, relative strength, breadth, dispersion)
  T  context          (returns, vol regime, trend location -- interaction fuel)

Merging rule for slower/async series (funding events, 5m metrics): as-of join
BACKWARD onto bar close time. A bar closing at t gets the latest value with
timestamp <= t. Funding "calc_time" is the payment time; the rate is known
(and ~fixed) by then, so backward as-of is causal.
"""
import numpy as np
import pandas as pd
from core import DATA, SYMS, atr

def _ns(df):
    df["dt"] = df["dt"].astype("datetime64[ns, UTC]")
    return df

def z(s, n):
    m = s.rolling(n, min_periods=max(5, n // 4)).mean()
    sd = s.rolling(n, min_periods=max(5, n // 4)).std()
    return (s - m) / sd.replace(0, np.nan)

def pctile(s, n):
    return s.rolling(n, min_periods=max(10, n // 4)).rank(pct=True)

def bar_hours(ival):
    return {"15m": 0.25, "1h": 1.0, "4h": 4.0}[ival]

def build_features(sym, ival, kl_cache=None):
    df = pd.read_parquet(f"{DATA}/klines_{sym}_{ival}.parquet").copy()
    bh = bar_hours(ival)
    pb = lambda hours: max(1, int(round(hours / bh)))   # bars per N hours
    c, o, h, l, v = df["close"], df["open"], df["high"], df["low"], df["volume"]
    close_time = df["dt"] + pd.Timedelta(hours=bh)      # features known at bar CLOSE
    X = pd.DataFrame(index=df.index)
    X["dt"] = df["dt"]

    # ---- T: context ----
    for hrs in (1, 4, 24, 72, 168):
        if hrs >= bh:
            X[f"T_ret_{hrs}h"] = c.pct_change(pb(hrs))
    a = pd.Series(atr(df), index=df.index)
    X["T_atr_pct"] = a / c
    X["T_atr_regime"] = (a / c) / (a / c).rolling(pb(24 * 30)).median()
    ema200 = c.ewm(span=200, adjust=False).mean()
    X["T_ema200_dist"] = c / ema200 - 1
    X["T_ema200_slope"] = ema200.pct_change(pb(24))
    rng = (h.rolling(pb(24 * 14)).max() - l.rolling(pb(24 * 14)).min())
    X["T_donch_pos"] = (c - l.rolling(pb(24 * 14)).min()) / rng.replace(0, np.nan)
    r1 = c.pct_change()
    X["T_rv_ratio"] = (r1.rolling(pb(24)).std() / r1.rolling(pb(24 * 7)).std())
    X["T_vol_z"] = z(v, pb(24 * 7))

    # ---- O: order flow from klines ----
    tb = df["taker_buy_vol"] / v.replace(0, np.nan)          # taker buy ratio
    X["O_tbr"] = tb
    X["O_tbr_ma6h"] = tb.rolling(pb(6)).mean()
    X["O_tbr_z"] = z(tb.rolling(pb(6)).mean(), pb(24 * 7))
    delta = (2 * df["taker_buy_vol"] - v)                    # signed flow
    X["O_cvd_24h"] = delta.rolling(pb(24)).sum() / v.rolling(pb(24)).sum().replace(0, np.nan)
    ats = df["quote_vol"] / df["count"].replace(0, np.nan)   # avg trade size ($)
    X["O_ats_z"] = z(ats, pb(24 * 7))
    X["O_count_z"] = z(df["count"], pb(24 * 7))
    # flow-price divergence: price up while flow down (and vice versa)
    X["O_flow_div"] = z(c.pct_change(pb(4)), pb(24 * 7)) - z(delta.rolling(pb(4)).sum(), pb(24 * 7))
    # whale bar: huge avg trade size on high volume
    X["O_whale"] = ((z(ats, pb(24 * 7)) > 2) & (X["T_vol_z"] > 1)).astype(float)

    # ---- F: funding ----
    try:
        fu = _ns(pd.read_parquet(f"{DATA}/funding_{sym}.parquet"))
        fu = fu.sort_values("dt")
        m = pd.merge_asof(pd.DataFrame({"dt": close_time}), fu, on="dt",
                          direction="backward")
        fr = m["funding_rate"].values
        X["F_rate"] = fr
        frs = pd.Series(fr, index=df.index)
        X["F_rate_z30d"] = z(frs, pb(24 * 30))
        X["F_cum3d"] = frs.rolling(pb(72)).sum() * bh / 8    # approx sum of paid fundings
        X["F_extreme_pos"] = (frs > 0.0005).astype(float)
        X["F_extreme_neg"] = (frs < -0.0002).astype(float)
        X["F_x_trend"] = frs * np.sign(X["T_ema200_dist"])
        hrs_utc = close_time.dt.hour + close_time.dt.minute / 60
        X["F_tt_funding"] = (8 - (hrs_utc % 8)) % 8          # hours to next payment
    except FileNotFoundError:
        pass

    # ---- B: basis / premium index ----
    try:
        pr = _ns(pd.read_parquet(f"{DATA}/premium_{sym}.parquet")).sort_values("dt")
        pr["p_dt_close"] = pr["dt"] + pd.Timedelta(hours=1)
        m = pd.merge_asof(pd.DataFrame({"dt": close_time}),
                          pr[["p_dt_close", "p_close"]].rename(columns={"p_dt_close": "dt"}),
                          on="dt", direction="backward")
        pc = pd.Series(m["p_close"].values, index=df.index)
        X["B_prem"] = pc
        X["B_prem_z"] = z(pc, pb(24 * 30))
        X["B_prem_chg24h"] = pc - pc.shift(pb(24))
    except FileNotFoundError:
        pass

    # ---- M: metrics (OI, LSR) ----
    try:
        me = _ns(pd.read_parquet(f"{DATA}/metrics_{sym}.parquet")).sort_values("dt")
        m = pd.merge_asof(pd.DataFrame({"dt": close_time}), me, on="dt",
                          direction="backward", tolerance=pd.Timedelta("2h"))
        oi = pd.Series(m["oi"].values, index=df.index)
        X["M_oi_norm"] = oi / oi.rolling(pb(24 * 30)).mean()
        for hrs in (1, 4, 24):
            if hrs >= bh:
                X[f"M_oi_chg_{hrs}h"] = oi.pct_change(pb(hrs))
        # OI-price quadrants: +price+OI=new longs, -price+OI=new shorts,
        # +price-OI=short covering, -price-OI=long liquidation
        dp = np.sign(c.pct_change(pb(4)))
        doi = np.sign(oi.pct_change(pb(4)))
        X["M_oi_quad"] = dp * 2 + doi                        # {-3,-1,1,3}
        X["M_liq_cascade"] = ((oi.pct_change(pb(4)) < -0.03) &
                              (c.pct_change(pb(4)).abs() > 0.02)).astype(float)
        for col, name in [("top_lsr_pos", "tlsr_pos"), ("top_lsr_acct", "tlsr_acct"),
                          ("glob_lsr", "glsr"), ("taker_vol_ratio", "tvr")]:
            s = pd.Series(m[col].values, index=df.index)
            X[f"M_{name}"] = s
            X[f"M_{name}_z"] = z(s, pb(24 * 30))
            X[f"M_{name}_chg24h"] = s - s.shift(pb(24))
    except FileNotFoundError:
        pass

    # ---- P: path shape from 5m ----
    if ival in ("1h", "4h"):
        d5 = pd.read_parquet(f"{DATA}/klines_{sym}_5m.parquet")
        d5c = d5["close"]
        r5 = d5c.pct_change()
        vov = r5.rolling(72).std().rolling(72).std()         # vol-of-vol, 6h windows
        wick = ((d5["high"] - d5[["open", "close"]].max(axis=1)) +
                (d5[["open", "close"]].min(axis=1) - d5["low"]))
        wickiness = (wick / (d5["high"] - d5["low"]).replace(0, np.nan)).rolling(12).mean()
        d5f = pd.DataFrame({"dt": d5["dt"] + pd.Timedelta(minutes=5),
                            "P_vov": vov.values, "P_wickiness": wickiness.values,
                            "P_r5_autocorr": r5.rolling(144).apply(
                                lambda x: 0, raw=True) if False else np.nan})
        d5f = d5f.drop(columns=["P_r5_autocorr"])
        mm = pd.merge_asof(pd.DataFrame({"dt": close_time}), d5f, on="dt",
                           direction="backward", tolerance=pd.Timedelta("1h"))
        X["P_vov"] = z(pd.Series(mm["P_vov"].values, index=df.index), pb(24 * 30))
        X["P_wickiness"] = mm["P_wickiness"].values
    # sweep-and-reclaim on trading TF: bar broke prior 24h low but closed back above
    lo24 = l.rolling(pb(24)).min().shift(1)
    hi24 = h.rolling(pb(24)).max().shift(1)
    X["P_sweep_low"] = ((l < lo24) & (c > lo24)).astype(float)
    X["P_sweep_high"] = ((h > hi24) & (c < hi24)).astype(float)
    body = (c - o).abs()
    X["P_bar_wick_ratio"] = 1 - body / (h - l).replace(0, np.nan)
    X["P_close_pos"] = (c - l) / (h - l).replace(0, np.nan)

    # ---- C: calendar ----
    ct = close_time
    X["C_hour"] = ct.dt.hour.astype(float)
    X["C_dow"] = ct.dt.dayofweek.astype(float)
    X["C_weekend"] = (ct.dt.dayofweek >= 5).astype(float)
    X["C_funding_slot"] = (ct.dt.hour % 8).astype(float)
    X["C_dom"] = ct.dt.day.astype(float)
    X["C_us_session"] = ((ct.dt.hour >= 13) & (ct.dt.hour < 21)).astype(float)
    X["C_asia_session"] = ((ct.dt.hour >= 0) & (ct.dt.hour < 8)).astype(float)

    # ---- X: cross-asset (needs BTC + universe closes on same TF) ----
    if kl_cache is not None:
        uni = []
        for s2 in SYMS:
            kdf = kl_cache[(s2, ival)]
            uni.append(kdf.set_index("dt")["close"].rename(s2))
        U = pd.concat(uni, axis=1).sort_index()
        U = U.reindex(df["dt"]).ffill()
        Uret24 = U.pct_change(pb(24))
        btc = U["BTCUSDT"]
        X["X_btc_ret4h"] = btc.pct_change(pb(4)).values
        X["X_btc_ret24h"] = Uret24["BTCUSDT"].values
        if sym != "BTCUSDT":
            rel = c.values / btc.values
            rel_s = pd.Series(rel, index=df.index)
            X["X_rs_btc_24h"] = rel_s.pct_change(pb(24))
            X["X_rs_btc_z"] = z(rel_s.pct_change(pb(24)), pb(24 * 30))
            # lead-lag: BTC's most recent 1-4 bars (alt may lag)
            X["X_btc_lead1"] = btc.pct_change(1).values
        X["X_breadth"] = (Uret24 > 0).mean(axis=1).values
        X["X_dispersion"] = Uret24.std(axis=1).values
        X["X_rel_to_breadth"] = X.get("T_ret_24h", np.nan) - Uret24.mean(axis=1).values

    return df, X
