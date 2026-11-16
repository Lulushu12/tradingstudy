"""Replica of the user's "Macro View" (MCB_Clone_v1.pine on branch claude/practical-galileo-wyubia, f_macro_core).
PROTOCOL Amendment 2.

On the source TF (10 x chart TF): over the last `length` closed source candles, the share (%) of candles with
wt2 > 0 / < 0 and with MF > 0 / < 0 (MF = the clone's stdev formula, as on the user's chart).
State +2 / +1 / 0 / -1 / -2 as in the indicator. Timing: the indicator uses request.security(lookahead_on) on
values shifted by [1], so a chart bar sees the state of the last source candle that CLOSED AT OR BEFORE THE CHART
BAR'S OPEN.
"""
from __future__ import annotations

import numba as nb
import numpy as np
import pandas as pd

from tradingstudy.features import mcb

MIN = pd.Timedelta(minutes=1)


def macro_state_htf(htf: pd.DataFrame, length: int = 50, thresh: float = 60.0) -> pd.DataFrame:
    wt = mcb.wavetrend(htf)
    mf = pd.Series(mcb.mf_pine(htf), index=htf.index)  # clone formula, as on the user's chart
    w2 = wt["wt2"]

    def share(cond):  # Pine: na compares false -> 0; math.sum needs `length` bars
        return cond.astype(float).rolling(length, min_periods=length).sum() / length * 100

    out = pd.DataFrame({"wt_bull": share(w2 > 0), "wt_bear": share(w2 < 0),
                        "mf_bull": share(mf > 0), "mf_bear": share(mf < 0)}, index=htf.index)
    wt_is_bull = (out.wt_bull >= thresh) & (out.wt_bull > out.wt_bear)
    wt_is_bear = (out.wt_bear >= thresh) & (out.wt_bear > out.wt_bull)
    mf_is_bull = (out.mf_bull >= thresh) & (out.mf_bull > out.mf_bear)
    mf_is_bear = (out.mf_bear >= thresh) & (out.mf_bear > out.mf_bull)
    state = np.select([wt_is_bull & mf_is_bull, wt_is_bull, wt_is_bear & mf_is_bear, wt_is_bear], [2, 1, -2, -1], 0).astype(float)
    state[out.wt_bull.isna().to_numpy()] = np.nan
    out["state"] = state
    out["lean"] = lean_bias(state)
    return out


@nb.njit(cache=True)
def _lean(state):
    n = state.shape[0]
    out = np.full(n, np.nan)
    last = 0.0
    for k in range(n):
        s = state[k]
        if np.isnan(s):
            continue
        if s > 0:
            out[k] = 1.0; last = 1.0
        elif s < 0:
            out[k] = -1.0; last = -1.0
        else:
            out[k] = -last if last != 0 else 0.0  # neutral after red = bullish lean, after green = bearish lean
    return out


def lean_bias(state) -> np.ndarray:
    return _lean(np.asarray(state, dtype=np.float64))


def align_on_open(htf_vals: pd.DataFrame, htf_minutes: int, chart_index: pd.DatetimeIndex) -> pd.DataFrame:
    """Value of the last source candle whose close is at or before each chart bar's OPEN (indicator timing)."""
    ends = (htf_vals.index + htf_minutes * MIN).as_unit("ns").asi8
    opens = chart_index.as_unit("ns").asi8
    pos = np.searchsorted(ends, opens, side="right") - 1
    out = htf_vals.iloc[np.clip(pos, 0, None)].copy()
    out.index = chart_index
    out.loc[pos < 0] = np.nan
    return out


def macro_bias(htf: pd.DataFrame, htf_minutes: int, chart_index: pd.DatetimeIndex, length: int = 50,
               thresh: float = 60.0) -> pd.DataFrame:
    m = macro_state_htf(htf, length, thresh)
    a = align_on_open(m[["state", "lean"]], htf_minutes, chart_index)
    st = a["state"]
    a["bias_lean"] = a["lean"]
    a["bias_any"] = np.where(st >= 1, 1.0, np.where(st <= -1, -1.0, 0.0))
    a["bias_strong"] = np.where(st == 2, 1.0, np.where(st == -2, -1.0, 0.0))
    a.loc[st.isna(), ["bias_any", "bias_strong"]] = np.nan
    return a
