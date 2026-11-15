"""Market Cipher B components: WaveTrend and Money Flow variants. All causal (bar t uses data up to t's close).

WaveTrend (brief 5.1, matches MCB_Clone_v1.pine f_wt_core):
    ap = hlc3; esa = EMA(ap, ch); d = EMA(|ap - esa|, ch); ci = (ap - esa) / (0.015 d)
    wt1 = EMA(ci, avg); wt2 = SMA(wt1, ma); hist ("VWAP") = wt1 - wt2

Money Flow candidates:
- mf_pine:  EMA( SMA( (close - open) / stdev(close, 7) * 150, 60 ) - 2.5, 4 )   (MCB_Clone_v1.pine)
- mf_clone: SMA( (close - open) / (high - low) * 150, 60 ) - 2.5                 (brief 5.1 "clone formula")
- mf_htf:   reverse-engineered: body ratio of an HTF candle, SMA over HTF bars, EMA on the chart TF,
            times a multiplier, minus 2.5. Two HTF hypotheses (3 x chart TF, fixed 3H) and two update modes:
              "developing": the HTF candle is built from chart bars printed so far (the brief's description);
              "step":       the HTF value updates only when an HTF bar closes (TradingView request.security on
                            historical bars with lookahead off).
"""
from __future__ import annotations

import numba as nb
import numpy as np
import pandas as pd

from tradingstudy.data.resample import bucket_starts
from tradingstudy.features.ta import ema, safe_div, sma, stdev

MIN_NS = 60 * 10**9


def wavetrend(df: pd.DataFrame, ch: int = 9, avg: int = 12, ma: int = 3) -> pd.DataFrame:
    ap = ((df["high"] + df["low"] + df["close"]) / 3.0).to_numpy()
    esa = ema(ap, ch)
    d = ema(np.abs(ap - esa), ch)
    ci = safe_div(ap - esa, 0.015 * d)
    wt1 = ema(ci, avg)
    wt2 = sma(wt1, ma)
    out = pd.DataFrame({"wt1": wt1, "wt2": wt2, "wt_hist": wt1 - wt2}, index=df.index)
    # Pine: crossover = a > b and a[1] <= b[1]; crossunder = a < b and a[1] >= b[1]; dot colour from wt2 - wt1
    diff = out["wt1"] - out["wt2"]
    prev = diff.shift(1)
    out["dot_green"] = (diff > 0) & (prev <= 0)
    out["dot_red"] = (diff < 0) & (prev >= 0)
    return out


def wt_signals(wt: pd.DataFrame, ob: float = 53, os_: float = -53) -> pd.DataFrame:
    return pd.DataFrame({"wt_buy": wt["dot_green"] & (wt["wt2"] <= os_),
                         "wt_sell": wt["dot_red"] & (wt["wt2"] >= ob)}, index=wt.index)


def mf_pine(df: pd.DataFrame, period: int = 60, mult: float = 150.0, pos_y: float = 2.5, sd_len: int = 7, smooth: int = 4) -> np.ndarray:
    c, o = df["close"].to_numpy(), df["open"].to_numpy()
    raw = safe_div(c - o, stdev(c, sd_len)) * mult
    return ema(sma(raw, period) - pos_y, smooth)


def heikin_ashi(df: pd.DataFrame) -> pd.DataFrame:
    """Standard Heikin-Ashi candles (causal): close = ohlc4, open = (prev HA open + prev HA close) / 2."""
    return pd.DataFrame(_heikin_ashi(*(df[k].to_numpy(np.float64) for k in ("open", "high", "low", "close"))),
                        index=df.index, columns=["open", "high", "low", "close"])


@nb.njit(cache=True)
def _heikin_ashi(o, h, l, c):
    n = o.shape[0]
    out = np.empty((n, 4))
    hc = (o + h + l + c) / 4.0
    ho = np.empty(n)
    ho[0] = (o[0] + c[0]) / 2.0
    for i in range(1, n):
        ho[i] = (ho[i - 1] + hc[i - 1]) / 2.0
    for i in range(n):
        out[i, 0] = ho[i]
        out[i, 1] = max(h[i], ho[i], hc[i])
        out[i, 2] = min(l[i], ho[i], hc[i])
        out[i, 3] = hc[i]
    return out


def mf_pine_ha(df: pd.DataFrame, period: int = 60, mult: float = 150.0, pos_y: float = 2.5, sd_len: int = 7, smooth: int = 2) -> np.ndarray:
    """MCB_Clone_v1 Money Flow computed on Heikin-Ashi candles. Best match to real MCB found in Phase 1."""
    return mf_pine(heikin_ashi(df), period, mult, pos_y, sd_len, smooth)


def body_ratio(o, h, l, c) -> np.ndarray:
    r = safe_div(np.asarray(c) - np.asarray(o), np.asarray(h) - np.asarray(l))
    return np.where(np.isnan(r) & ~np.isnan(np.asarray(c, dtype=float)), 0.0, r)  # high == low -> 0 (guard)


def mf_clone(df: pd.DataFrame, period: int = 60, mult: float = 150.0, pos_y: float = 2.5) -> np.ndarray:
    r = body_ratio(df["open"], df["high"], df["low"], df["close"])
    return sma(r * mult, period) - pos_y


@nb.njit(cache=True)
def _htf_ratio_core(bucket, o, h, l, c, is_last, sma_len, developing):
    """Returns per chart bar the SMA of HTF body ratios (unscaled)."""
    n = bucket.shape[0]
    out = np.full(n, np.nan)
    completed = np.zeros(n)  # completed HTF ratios, in order
    nc = 0
    cur_b = -1
    dev_o = dev_h = dev_l = dev_c = 0.0
    was_closed = True
    last_step_val = np.nan
    for i in range(n):
        if bucket[i] != cur_b:
            if cur_b != -1 and not was_closed:
                # previous bucket ended without a bar at its exact close time (gap): close it now
                rng = dev_h - dev_l
                completed[nc] = (dev_c - dev_o) / rng if rng != 0 else 0.0
                nc += 1
            cur_b = bucket[i]
            dev_o, dev_h, dev_l = o[i], h[i], l[i]
            was_closed = False
        else:
            dev_h = max(dev_h, h[i])
            dev_l = min(dev_l, l[i])
        dev_c = c[i]
        rng = dev_h - dev_l
        r_dev = (dev_c - dev_o) / rng if rng != 0 else 0.0
        if developing:
            if nc >= sma_len - 1:
                s = r_dev
                for j in range(nc - (sma_len - 1), nc):
                    s += completed[j]
                out[i] = s / sma_len
        if is_last[i]:
            completed[nc] = r_dev
            nc += 1
            was_closed = True
            if nc >= sma_len:
                s = 0.0
                for j in range(nc - sma_len, nc):
                    s += completed[j]
                last_step_val = s / sma_len
        if not developing:
            out[i] = last_step_val
    return out


def mf_htf(df: pd.DataFrame, chart_min: int, htf_min: int, sma_len: int = 20, ema_len: int = 5,
           mult: float = 200.0, pos_y: float = 2.5, developing: bool = True) -> np.ndarray:
    ts = pd.DatetimeIndex(df.index).as_unit("ns").asi8
    b = bucket_starts(ts, htf_min) if (htf_min <= 1440 and 1440 % htf_min == 0) or htf_min == 10080 else (ts // (htf_min * MIN_NS)) * (htf_min * MIN_NS)
    is_last = (ts + chart_min * MIN_NS) == (b + htf_min * MIN_NS)
    raw = _htf_ratio_core(b, *(df[c].to_numpy(np.float64) for c in ("open", "high", "low", "close")), is_last, sma_len, developing)
    return ema(raw, ema_len) * mult - pos_y
