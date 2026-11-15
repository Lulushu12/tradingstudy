"""Volume profiles from 1m bars (brief 5.6). Each 1m bar's volume is spread over the price bins its [low, high]
range overlaps, in proportion to the overlap (standard approximation; Binance perp volume only).

Outputs: POC (highest-volume bin centre), value area high/low (70% of volume, grown from the POC towards the
heavier neighbouring bin), and low-volume nodes (local minima below lvn_frac x POC volume, inside the value area).
"""
from __future__ import annotations

import numba as nb
import numpy as np
import pandas as pd

VA_SHARE = 0.70
LVN_FRAC = 0.25


@nb.njit(cache=True)
def _profile(low, high, vol, lo, bin_w, nbins):
    hist = np.zeros(nbins)
    for i in range(low.shape[0]):
        a, b, v = low[i], high[i], vol[i]
        if v <= 0:
            continue
        ia = int((a - lo) / bin_w)
        ib = int((b - lo) / bin_w)
        ia = min(max(ia, 0), nbins - 1)
        ib = min(max(ib, 0), nbins - 1)
        if ia == ib or b <= a:
            hist[ia] += v
            continue
        span = b - a
        for k in range(ia, ib + 1):
            x0 = max(a, lo + k * bin_w)
            x1 = min(b, lo + (k + 1) * bin_w)
            if x1 > x0:
                hist[k] += v * (x1 - x0) / span
    return hist


@nb.njit(cache=True)
def _value_area(hist, share):
    poc = int(np.argmax(hist))
    total = hist.sum()
    lo_i = poc; hi_i = poc
    acc = hist[poc]
    n = hist.shape[0]
    while acc < share * total and (lo_i > 0 or hi_i < n - 1):
        up = hist[hi_i + 1] if hi_i < n - 1 else -1.0
        dn = hist[lo_i - 1] if lo_i > 0 else -1.0
        if up >= dn:
            hi_i += 1; acc += up
        else:
            lo_i -= 1; acc += dn
    return poc, lo_i, hi_i


def volume_profile(m1: pd.DataFrame, bin_w: float) -> dict:
    """m1: 1m bars covering exactly the anchored window. bin_w: price bin width."""
    if len(m1) == 0 or not np.isfinite(bin_w) or bin_w <= 0:
        return {"poc": np.nan, "vah": np.nan, "val": np.nan, "lvns": np.array([])}
    low = m1["low"].to_numpy(np.float64); high = m1["high"].to_numpy(np.float64); vol = m1["volume"].to_numpy(np.float64)
    lo = low.min()
    nbins = max(int(np.ceil((high.max() - lo) / bin_w)) + 1, 1)
    hist = _profile(low, high, vol, lo, bin_w, nbins)
    if hist.sum() <= 0:
        return {"poc": np.nan, "vah": np.nan, "val": np.nan, "lvns": np.array([])}
    poc, a, b = _value_area(hist, VA_SHARE)
    centre = lambda k: lo + (k + 0.5) * bin_w
    lvns = [centre(k) for k in range(max(a, 1), min(b, nbins - 2) + 1)
            if hist[k] < LVN_FRAC * hist[poc] and hist[k] <= hist[k - 1] and hist[k] <= hist[k + 1]]
    return {"poc": centre(poc), "vah": lo + (b + 1) * bin_w, "val": lo + a * bin_w, "lvns": np.array(lvns)}


def prev_day_profiles(m1: pd.DataFrame, atr_1d: pd.Series, bin_frac: float = 0.05) -> pd.DataFrame:
    """Profile of each UTC day, labelled by the day it describes. Usable from the NEXT day's 00:00 UTC.
    Bin width = bin_frac x the 1D ATR known at the end of that day."""
    rows = []
    for day, g in m1.groupby(m1.index.floor("1D")):
        a = atr_1d.get(day, np.nan)
        p = volume_profile(g, bin_frac * a)
        rows.append({"day": day, "poc": p["poc"], "vah": p["vah"], "val": p["val"]})
    out = pd.DataFrame(rows).set_index("day")
    return out
