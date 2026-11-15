"""Volume, funding and context features (brief 5.4, 5.5). All causal."""
from __future__ import annotations

import numpy as np
import pandas as pd

from tradingstudy.features import ta
from tradingstudy.features.htf import align_htf

MIN = pd.Timedelta(minutes=1)


def cmf(bars: pd.DataFrame, length: int = 20) -> pd.Series:
    """Chaikin Money Flow (real, volume-based)."""
    h, l, c, v = (bars[k].to_numpy(np.float64) for k in ("high", "low", "close", "volume"))
    mfm = ta.safe_div((c - l) - (h - c), h - l)
    mfm = np.where(np.isnan(mfm), 0.0, mfm)
    num = pd.Series(mfm * v).rolling(length).sum().to_numpy()
    den = pd.Series(v).rolling(length).sum().to_numpy()
    return pd.Series(ta.safe_div(num, den), index=bars.index, name=f"cmf{length}")


def funding_features(funding: pd.DataFrame, chart_index: pd.DatetimeIndex, chart_minutes: int, z_window: int = 90) -> pd.DataFrame:
    """Last PUBLISHED funding rate at each chart bar's close (calc_time <= bar close). 8h-equivalent and z-score."""
    f = funding.copy()
    f["funding_8h"] = f["funding_rate"] * 8.0 / f["interval_hours"]
    m = f["funding_8h"].rolling(z_window, min_periods=z_window // 2).mean()
    s = f["funding_8h"].rolling(z_window, min_periods=z_window // 2).std()
    f["funding_z"] = (f["funding_8h"] - m) / s
    t = f.index.as_unit("ns").asi8
    closes = (chart_index + chart_minutes * MIN).as_unit("ns").asi8
    pos = np.searchsorted(t, closes, side="right") - 1
    out = f[["funding_8h", "funding_z"]].iloc[np.clip(pos, 0, None)].copy()
    out.index = chart_index
    out.loc[pos < 0] = np.nan
    return out


def adx(bars: pd.DataFrame, length: int = 14) -> pd.DataFrame:
    h, l, c = (bars[k].to_numpy(np.float64) for k in ("high", "low", "close"))
    up = np.r_[np.nan, np.diff(h)]
    dn = np.r_[np.nan, -np.diff(l)]
    plus_dm = np.where((up > dn) & (up > 0), up, 0.0)
    minus_dm = np.where((dn > up) & (dn > 0), dn, 0.0)
    tr = ta.true_range(h, l, c)
    atr_ = ta.rma(tr, length)
    pdi = 100 * ta.safe_div(ta.rma(plus_dm, length), atr_)
    mdi = 100 * ta.safe_div(ta.rma(minus_dm, length), atr_)
    dx = 100 * ta.safe_div(np.abs(pdi - mdi), pdi + mdi)
    return pd.DataFrame({"adx": ta.rma(dx, length), "pdi": pdi, "mdi": mdi}, index=bars.index)


def trend_regimes(h4: pd.DataFrame, d1: pd.DataFrame, chart_index: pd.DatetimeIndex, chart_minutes: int) -> pd.DataFrame:
    """Candidate trend-regime definitions (brief 5.5). One or two get picked at Gate 1.
    R1 price vs 4h EMA200 and its slope; R2 4h ADX bands with DI direction; R3 price vs 1D SMA50 and its slope."""
    e200 = pd.Series(ta.ema(h4["close"], 200), index=h4.index)
    r1 = pd.DataFrame({"r1_above_ema200_4h": (h4["close"] > e200).astype(float),
                       "r1_ema200_4h_slope": (e200 - e200.shift(6)) / e200.shift(6)})  # 1-day slope
    r1.loc[e200.isna(), "r1_above_ema200_4h"] = np.nan
    a = adx(h4)
    r2 = pd.DataFrame({"r2_adx_4h": a["adx"], "r2_di_bull_4h": (a["pdi"] > a["mdi"]).astype(float)})
    s50 = pd.Series(ta.sma(d1["close"], 50), index=d1.index)
    r3 = pd.DataFrame({"r3_above_sma50_1d": (d1["close"] > s50).astype(float),
                       "r3_sma50_1d_slope": (s50 - s50.shift(5)) / s50.shift(5)})
    r3.loc[s50.isna(), "r3_above_sma50_1d"] = np.nan
    out = pd.concat([align_htf(pd.concat([r1, r2], axis=1), 240, chart_index, chart_minutes),
                     align_htf(r3, 1440, chart_index, chart_minutes)], axis=1)
    # categorical labels (+1 up, -1 down, 0 neutral/range)
    out["r1_trend"] = np.select([(out.r1_above_ema200_4h == 1) & (out.r1_ema200_4h_slope > 0),
                                 (out.r1_above_ema200_4h == 0) & (out.r1_ema200_4h_slope < 0)], [1, -1], 0)
    out["r2_trend"] = np.select([(out.r2_adx_4h >= 25) & (out.r2_di_bull_4h == 1),
                                 (out.r2_adx_4h >= 25) & (out.r2_di_bull_4h == 0)], [1, -1], 0)
    out["r3_trend"] = np.select([(out.r3_above_sma50_1d == 1) & (out.r3_sma50_1d_slope > 0),
                                 (out.r3_above_sma50_1d == 0) & (out.r3_sma50_1d_slope < 0)], [1, -1], 0)
    for r, col in (("r1_trend", "r1_ema200_4h_slope"), ("r2_trend", "r2_adx_4h"), ("r3_trend", "r3_sma50_1d_slope")):
        out.loc[out[col].isna(), r] = np.nan
    return out


def atr_regime(bars: pd.DataFrame, chart_minutes: int, window_days: int = 30) -> pd.DataFrame:
    a = pd.Series(ta.atr(bars["high"], bars["low"], bars["close"], 14), index=bars.index)
    pct = a / bars["close"]
    n = int(window_days * 1440 / chart_minutes)
    rank = pct.rolling(n, min_periods=n // 2).rank(pct=True)
    return pd.DataFrame({"atr14": a, "atr_pct": pct, "atr_pctile_30d": rank}, index=bars.index)


def session(chart_index: pd.DatetimeIndex, chart_minutes: int) -> pd.DataFrame:
    """Time features at the decision moment (bar close)."""
    t = chart_index + chart_minutes * MIN
    h = t.hour
    return pd.DataFrame({"hour_utc": h, "weekday": t.day_of_week,
                         "session": np.select([h < 8, h < 13, h < 21], ["asia", "europe", "us"], "late")},
                        index=chart_index)
