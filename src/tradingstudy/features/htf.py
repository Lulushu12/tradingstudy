"""Higher-timeframe alignment and the HTF layer (brief 5.3).

Rule (brief 5.8): a chart bar may only see the LAST FULLY CLOSED HTF bar. An HTF bar opened at s with length W
closes at s + W. A chart bar opened at t with length c closes at t + c and may use HTF bars with s + W <= t + c.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from tradingstudy.features import mcb

MIN = pd.Timedelta(minutes=1)


def align_htf(htf: pd.DataFrame, htf_minutes: int, chart_index: pd.DatetimeIndex, chart_minutes: int) -> pd.DataFrame:
    """Values of the last fully closed HTF bar as seen at each chart bar's close."""
    ends = (htf.index + htf_minutes * MIN).as_unit("ns").asi8
    closes = (chart_index + chart_minutes * MIN).as_unit("ns").asi8
    pos = np.searchsorted(ends, closes, side="right") - 1
    out = htf.iloc[np.clip(pos, 0, None)].copy()
    out.index = chart_index
    out.loc[pos < 0] = np.nan
    return out


def htf_layer(htf_bars: pd.DataFrame, htf_minutes: int, chart_index: pd.DatetimeIndex, chart_minutes: int,
              near_cross: float = 2.0) -> pd.DataFrame:
    """HTF WaveTrend near-cross and HTF Money Flow direction, computed on HTF bars then aligned (last closed)."""
    wt = mcb.wavetrend(htf_bars)
    mf = pd.Series(mcb.mf_pine_ha(htf_bars, smooth=1), index=htf_bars.index)
    gap = wt["wt1"] - wt["wt2"]
    prev_gap = gap.shift(1)
    h = pd.DataFrame({
        "htf_wt1": wt["wt1"], "htf_wt2": wt["wt2"], "htf_gap": gap,
        # wt2 above wt1 by less than the threshold and closing in = bullish cross imminent (mirrored for bearish)
        "htf_near_cross_bull": (gap < 0) & (-gap < near_cross) & (gap.abs() < prev_gap.abs()),
        "htf_near_cross_bear": (gap > 0) & (gap < near_cross) & (gap.abs() < prev_gap.abs()),
        "htf_dot_green": wt["dot_green"], "htf_dot_red": wt["dot_red"],
        "htf_mf": mf, "htf_mf_rising": mf > mf.shift(1),
    })
    a = align_htf(h.astype(float), htf_minutes, chart_index, chart_minutes)
    for c in ["htf_near_cross_bull", "htf_near_cross_bear", "htf_dot_green", "htf_dot_red", "htf_mf_rising"]:
        a[c] = a[c] == 1.0
    return a
