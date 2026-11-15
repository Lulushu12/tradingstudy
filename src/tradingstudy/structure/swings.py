"""ATR zigzag swing detector (brief 5.6). The only searched structure parameter is k.

Rules (causal):
- ATR = ATR(14), Wilder, of the timeframe the swings come from.
- In an up-leg we track the running high. If a bar makes a new high, the extreme moves (no reversal check that bar,
  because the order of high and low inside one bar is unknown). Otherwise, if the bar's low is at least k x ATR below
  the extreme, the swing HIGH is confirmed on this bar and a down-leg starts with the extreme at this bar's low.
  Down-legs mirror this.
- Before the first reversal both a running high and a running low are tracked; whichever reverses first sets the
  initial direction.
- A swing EXISTS only from its confirmation bar's close. Its pivot bar is earlier. Never use the forming leg.
"""
from __future__ import annotations

import numba as nb
import numpy as np
import pandas as pd

from tradingstudy.features import ta


@nb.njit(cache=True)
def _zigzag(high, low, atr, k):
    n = high.shape[0]
    piv_bar = np.empty(n, dtype=np.int64)
    piv_px = np.empty(n)
    piv_type = np.empty(n, dtype=np.int64)  # +1 swing high, -1 swing low
    conf_bar = np.empty(n, dtype=np.int64)
    ns = 0
    direction = 0
    hi = -np.inf; hi_bar = -1
    lo = np.inf; lo_bar = -1
    for t in range(n):
        a = atr[t]
        if np.isnan(a):
            continue
        if direction == 0:
            new_hi = high[t] > hi
            new_lo = low[t] < lo
            if new_hi:
                hi = high[t]; hi_bar = t
            if new_lo:
                lo = low[t]; lo_bar = t
            if hi_bar >= 0 and not new_hi and low[t] <= hi - k * a:
                piv_bar[ns] = hi_bar; piv_px[ns] = hi; piv_type[ns] = 1; conf_bar[ns] = t; ns += 1
                direction = -1; lo = low[t]; lo_bar = t
            elif lo_bar >= 0 and not new_lo and high[t] >= lo + k * a:
                piv_bar[ns] = lo_bar; piv_px[ns] = lo; piv_type[ns] = -1; conf_bar[ns] = t; ns += 1
                direction = 1; hi = high[t]; hi_bar = t
        elif direction == 1:
            if high[t] > hi:
                hi = high[t]; hi_bar = t
            elif low[t] <= hi - k * a:
                piv_bar[ns] = hi_bar; piv_px[ns] = hi; piv_type[ns] = 1; conf_bar[ns] = t; ns += 1
                direction = -1; lo = low[t]; lo_bar = t
        else:
            if low[t] < lo:
                lo = low[t]; lo_bar = t
            elif high[t] >= lo + k * a:
                piv_bar[ns] = lo_bar; piv_px[ns] = lo; piv_type[ns] = -1; conf_bar[ns] = t; ns += 1
                direction = 1; hi = high[t]; hi_bar = t
    return piv_bar[:ns], piv_px[:ns], piv_type[:ns], conf_bar[:ns]


def zigzag(bars: pd.DataFrame, k: float = 3.0, atr_len: int = 14) -> pd.DataFrame:
    """Confirmed swings, one row per swing, in confirmation order.
    Columns: pivot_time, pivot_bar, price, type (+1 high / -1 low), confirm_bar, known_at (confirm bar close time),
    atr (ATR at the confirmation bar)."""
    a = ta.atr(bars["high"], bars["low"], bars["close"], atr_len)
    pb, px, ty, cb = _zigzag(bars["high"].to_numpy(np.float64), bars["low"].to_numpy(np.float64), a, float(k))
    minutes = bars.attrs.get("minutes")
    idx = bars.index
    out = pd.DataFrame({"pivot_time": idx[pb], "pivot_bar": pb, "price": px, "type": ty,
                        "confirm_bar": cb, "confirm_time": idx[cb], "atr": a[cb]})
    if minutes is not None:
        out["known_at"] = out["confirm_time"] + pd.Timedelta(minutes=minutes)
    return out
