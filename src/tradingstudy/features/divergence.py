"""Divergence events. Every event is stamped on the bar where it becomes KNOWN (closed-bar confirmation).

WaveTrend dot divergences (brief 5.2), Variant A (confirmed):
  - Each green dot (wt1 crosses above wt2) has a level = wt2 at the cross bar and a price low = the lowest wick low
    of its wave (bars after the previous red dot up to and including the green dot). Red dots mirrored (highest high).
  - The current dot is compared with up to `lookback_dots` previous same-colour dots no more than `max_dist` bars back.
    The most recent qualifying earlier dot is the reference.
  - Regular bullish: price lower low AND dot level higher. Hidden bullish: price higher low AND dot level lower.
  - Level filter (regular): current green dot level <= os_level (red: >= ob_level). Hidden: no filter by default
    (MCB_Clone_v1.pine default "No OB/OS limit on hidden").
  - Event bar = the dot bar (a cross is known at that bar's close).
WaveTrend Variant B (front-run): within a wave that has no dot yet, the first bar where wt1 turns toward wt2
  (wt1[t] > wt1[t-1] while wt1 < wt2, for bullish) and the wave so far already satisfies the regular divergence
  conditions using wt2[t] as the provisional level. One event per wave.

Money Flow pivot divergences, Variant A:
  - Pivot low at p: mf[p] lower than the `piv` bars before it and not higher than the `piv` bars after it.
    Known at p + piv (event bar). Price at the pivot = lowest low over [p - piv, p + piv].
  - Compared with earlier pivots whose pivot bar is within `lookback` bars of p; most recent qualifying is reference.
  - Regular bullish: mf higher by more than min_delta AND price lower by more than min_price_delta. Hidden mirrored.
Money Flow Variant B (front-run): at bar t, mf turns up (mf[t] > mf[t-1]) and t-1 is a left-side-only pivot
  candidate (lower than the `piv` bars before it). Price = lowest low over [t-1-piv, t]. Same comparisons.
  The candidate may never confirm; that risk is part of the variant.
"""
from __future__ import annotations

import numba as nb
import numpy as np
import pandas as pd

EVENT_COLS = ["bull_reg", "bull_hid", "bear_reg", "bear_hid"]


@nb.njit(cache=True)
def _wt_dot_div(wt1, wt2, low, high, green, red, lookback_dots, max_dist, os_level, ob_level, filter_hidden):
    n = wt2.shape[0]
    out = np.zeros((n, 4), dtype=np.bool_)
    ref = np.full((n, 4), -1, dtype=np.int64)
    fr = np.zeros((n, 2), dtype=np.bool_)  # front-run bull, bear
    fr_ref = np.full((n, 2), -1, dtype=np.int64)
    g_bar = np.empty(n, dtype=np.int64); g_lvl = np.empty(n); g_px = np.empty(n); ng = 0
    r_bar = np.empty(n, dtype=np.int64); r_lvl = np.empty(n); r_px = np.empty(n); nr = 0
    wave_low = np.inf   # running low since the last red dot (down-wave, ends at a green dot)
    wave_high = -np.inf  # running high since the last green dot
    fired_bull = False
    fired_bear = False
    for t in range(n):
        wave_low = min(wave_low, low[t])
        wave_high = max(wave_high, high[t])
        if np.isnan(wt2[t]):
            continue
        if green[t]:
            lvl = wt2[t]
            for j in range(ng - 1, max(ng - lookback_dots, 0) - 1, -1):
                if t - g_bar[j] > max_dist:
                    break
                if ref[t, 0] < 0 and wave_low < g_px[j] and lvl > g_lvl[j] and lvl <= os_level:
                    out[t, 0] = True; ref[t, 0] = g_bar[j]
                if ref[t, 1] < 0 and wave_low > g_px[j] and lvl < g_lvl[j] and (not filter_hidden or lvl <= os_level):
                    out[t, 1] = True; ref[t, 1] = g_bar[j]
            g_bar[ng] = t; g_lvl[ng] = lvl; g_px[ng] = wave_low; ng += 1
            wave_high = high[t]  # new up-wave starts at this bar
            fired_bear = False
        elif red[t]:
            lvl = wt2[t]
            for j in range(nr - 1, max(nr - lookback_dots, 0) - 1, -1):
                if t - r_bar[j] > max_dist:
                    break
                if ref[t, 2] < 0 and wave_high > r_px[j] and lvl < r_lvl[j] and lvl >= ob_level:
                    out[t, 2] = True; ref[t, 2] = r_bar[j]
                if ref[t, 3] < 0 and wave_high < r_px[j] and lvl > r_lvl[j] and (not filter_hidden or lvl >= ob_level):
                    out[t, 3] = True; ref[t, 3] = r_bar[j]
            r_bar[nr] = t; r_lvl[nr] = lvl; r_px[nr] = wave_high; nr += 1
            wave_low = low[t]
            fired_bull = False
        else:
            if t == 0 or np.isnan(wt1[t - 1]):
                continue
            # front-run bullish: in a down-wave (wt1 < wt2), wt1 ticks up, no green dot yet in this wave
            if not fired_bull and wt1[t] < wt2[t] and wt1[t] > wt1[t - 1]:
                lvl = wt2[t]
                for j in range(ng - 1, max(ng - lookback_dots, 0) - 1, -1):
                    if t - g_bar[j] > max_dist:
                        break
                    if wave_low < g_px[j] and lvl > g_lvl[j] and lvl <= os_level:
                        fr[t, 0] = True; fr_ref[t, 0] = g_bar[j]; fired_bull = True
                        break
            if not fired_bear and wt1[t] > wt2[t] and wt1[t] < wt1[t - 1]:
                lvl = wt2[t]
                for j in range(nr - 1, max(nr - lookback_dots, 0) - 1, -1):
                    if t - r_bar[j] > max_dist:
                        break
                    if wave_high > r_px[j] and lvl < r_lvl[j] and lvl >= ob_level:
                        fr[t, 1] = True; fr_ref[t, 1] = r_bar[j]; fired_bear = True
                        break
    return out, ref, fr, fr_ref


def wt_dot_divergences(wt: pd.DataFrame, bars: pd.DataFrame, lookback_dots: int = 5, max_dist: int = 300,
                       os_level: float = -53, ob_level: float = 53, filter_hidden: bool = False) -> pd.DataFrame:
    out, ref, fr, fr_ref = _wt_dot_div(wt["wt1"].to_numpy(np.float64), wt["wt2"].to_numpy(np.float64),
                                       bars["low"].to_numpy(np.float64), bars["high"].to_numpy(np.float64),
                                       wt["dot_green"].to_numpy(np.bool_), wt["dot_red"].to_numpy(np.bool_),
                                       lookback_dots, max_dist, float(os_level), float(ob_level), filter_hidden)
    df = pd.DataFrame(out, index=wt.index, columns=[f"wtdiv_{c}" for c in EVENT_COLS])
    for k, c in enumerate(EVENT_COLS):
        df[f"wtdiv_{c}_ref"] = ref[:, k]
    df["wtdiv_fr_bull"], df["wtdiv_fr_bear"] = fr[:, 0], fr[:, 1]
    df["wtdiv_fr_bull_ref"], df["wtdiv_fr_bear_ref"] = fr_ref[:, 0], fr_ref[:, 1]
    return df


@nb.njit(cache=True)
def _pivot_div(osc, low, high, piv, lookback, min_delta, min_price_delta):
    n = osc.shape[0]
    out = np.zeros((n, 4), dtype=np.bool_)
    ref = np.full((n, 4), -1, dtype=np.int64)
    fr = np.zeros((n, 2), dtype=np.bool_)
    fr_ref = np.full((n, 2), -1, dtype=np.int64)
    lo_bar = np.empty(n, dtype=np.int64); lo_val = np.empty(n); lo_px = np.empty(n); nlo = 0
    hi_bar = np.empty(n, dtype=np.int64); hi_val = np.empty(n); hi_px = np.empty(n); nhi = 0
    for c in range(n):
        # ---- front-run candidates at bar c (pivot candidate at c-1, left side only) ----
        p = c - 1
        if p - piv >= 0 and not np.isnan(osc[c]):
            okl = True; okh = True
            for k in range(1, piv + 1):
                if np.isnan(osc[p - k]) or not (osc[p] < osc[p - k]):
                    okl = False
                if np.isnan(osc[p - k]) or not (osc[p] > osc[p - k]):
                    okh = False
            if okl and osc[c] > osc[p]:
                px = low[p - piv]
                for k in range(p - piv, c + 1):
                    px = min(px, low[k])
                for j in range(nlo - 1, -1, -1):
                    if p - lo_bar[j] > lookback:
                        break
                    if osc[p] - lo_val[j] > min_delta and lo_px[j] - px > min_price_delta:
                        fr[c, 0] = True; fr_ref[c, 0] = lo_bar[j]
                        break
            if okh and osc[c] < osc[p]:
                px = high[p - piv]
                for k in range(p - piv, c + 1):
                    px = max(px, high[k])
                for j in range(nhi - 1, -1, -1):
                    if p - hi_bar[j] > lookback:
                        break
                    if hi_val[j] - osc[p] > min_delta and px - hi_px[j] > min_price_delta:
                        fr[c, 1] = True; fr_ref[c, 1] = hi_bar[j]
                        break
        # ---- confirmed pivots: pivot bar p = c - piv ----
        p = c - piv
        if p - piv < 0 or np.isnan(osc[p]):
            continue
        is_lo = True; is_hi = True
        for k in range(1, piv + 1):
            a, b = osc[p - k], osc[p + k]
            if np.isnan(a) or np.isnan(b):
                is_lo = False; is_hi = False
                break
            if not (osc[p] < a and osc[p] <= b):
                is_lo = False
            if not (osc[p] > a and osc[p] >= b):
                is_hi = False
        if is_lo:
            px = low[p - piv]
            for k in range(p - piv, p + piv + 1):
                px = min(px, low[k])
            for j in range(nlo - 1, -1, -1):
                if p - lo_bar[j] > lookback:
                    break
                if ref[c, 0] < 0 and osc[p] - lo_val[j] > min_delta and lo_px[j] - px > min_price_delta:
                    out[c, 0] = True; ref[c, 0] = lo_bar[j]
                if ref[c, 1] < 0 and lo_val[j] - osc[p] > min_delta and px - lo_px[j] > min_price_delta:
                    out[c, 1] = True; ref[c, 1] = lo_bar[j]
            lo_bar[nlo] = p; lo_val[nlo] = osc[p]; lo_px[nlo] = px; nlo += 1
        if is_hi:
            px = high[p - piv]
            for k in range(p - piv, p + piv + 1):
                px = max(px, high[k])
            for j in range(nhi - 1, -1, -1):
                if p - hi_bar[j] > lookback:
                    break
                if ref[c, 2] < 0 and hi_val[j] - osc[p] > min_delta and px - hi_px[j] > min_price_delta:
                    out[c, 2] = True; ref[c, 2] = hi_bar[j]
                if ref[c, 3] < 0 and osc[p] - hi_val[j] > min_delta and hi_px[j] - px > min_price_delta:
                    out[c, 3] = True; ref[c, 3] = hi_bar[j]
            hi_bar[nhi] = p; hi_val[nhi] = osc[p]; hi_px[nhi] = px; nhi += 1
    return out, ref, fr, fr_ref


def pivot_divergences(osc, bars: pd.DataFrame, prefix: str = "mfdiv", piv: int = 3, lookback: int = 100,
                      min_delta: float = 0.0, min_price_delta: float = 0.0) -> pd.DataFrame:
    out, ref, fr, fr_ref = _pivot_div(np.asarray(osc, dtype=np.float64), bars["low"].to_numpy(np.float64),
                                      bars["high"].to_numpy(np.float64), piv, lookback, float(min_delta), float(min_price_delta))
    df = pd.DataFrame(out, index=bars.index, columns=[f"{prefix}_{c}" for c in EVENT_COLS])
    for k, c in enumerate(EVENT_COLS):
        df[f"{prefix}_{c}_ref"] = ref[:, k]
    df[f"{prefix}_fr_bull"], df[f"{prefix}_fr_bear"] = fr[:, 0], fr[:, 1]
    df[f"{prefix}_fr_bull_ref"], df[f"{prefix}_fr_bear_ref"] = fr_ref[:, 0], fr_ref[:, 1]
    return df
