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


# =====================================================================================================================
# v2 definitions (PROTOCOL Amendment 1, Gate 2). v1 above is kept unchanged so Phase 2 results stay reproducible.
# =====================================================================================================================

@nb.njit(cache=True)
def _wt_dots_v2(wt1, wt2, low, high, green, red, lookback_dots, max_dist, os_level, ob_level, fr_age):
    """Regular divergences with the level filter on the ANCHOR dot; hidden without filter; wave extremes; front-run.
    Front-run bull at t: wt1 < wt2 (no dot yet in this wave), wt1[t] > wt1[t-1]; anchor = most recent green dot with
    level <= os_level and dot bar >= t - fr_age; min(low[t-2..t]) < anchor wave low; lowest wt1 of the current wave
    > anchor level."""
    n = wt2.shape[0]
    out = np.zeros((n, 4), dtype=np.bool_)
    ref = np.full((n, 4), -1, dtype=np.int64)
    fr = np.zeros((n, 2), dtype=np.bool_)
    wave_lo = np.full(n, np.nan)
    wave_hi = np.full(n, np.nan)
    g_bar = np.empty(n, dtype=np.int64); g_lvl = np.empty(n); g_px = np.empty(n); ng = 0
    r_bar = np.empty(n, dtype=np.int64); r_lvl = np.empty(n); r_px = np.empty(n); nr = 0
    wave_low = np.inf; wave_high = -np.inf
    wt1_min = np.inf; wt1_max = -np.inf  # extreme wt1 of the current down-wave / up-wave
    for t in range(n):
        wave_low = min(wave_low, low[t]); wave_high = max(wave_high, high[t])
        if not np.isnan(wt1[t]):
            wt1_min = min(wt1_min, wt1[t]); wt1_max = max(wt1_max, wt1[t])
        wave_lo[t] = wave_low; wave_hi[t] = wave_high
        if np.isnan(wt2[t]):
            continue
        if green[t]:
            lvl = wt2[t]
            for j in range(ng - 1, max(ng - lookback_dots, 0) - 1, -1):
                if t - g_bar[j] > max_dist:
                    break
                if ref[t, 0] < 0 and wave_low < g_px[j] and lvl > g_lvl[j] and g_lvl[j] <= os_level:
                    out[t, 0] = True; ref[t, 0] = g_bar[j]
                if ref[t, 1] < 0 and wave_low > g_px[j] and lvl < g_lvl[j]:
                    out[t, 1] = True; ref[t, 1] = g_bar[j]
            g_bar[ng] = t; g_lvl[ng] = lvl; g_px[ng] = wave_low; ng += 1
            wave_high = high[t]; wt1_max = wt1[t]
        elif red[t]:
            lvl = wt2[t]
            for j in range(nr - 1, max(nr - lookback_dots, 0) - 1, -1):
                if t - r_bar[j] > max_dist:
                    break
                if ref[t, 2] < 0 and wave_high > r_px[j] and lvl < r_lvl[j] and r_lvl[j] >= ob_level:
                    out[t, 2] = True; ref[t, 2] = r_bar[j]
                if ref[t, 3] < 0 and wave_high < r_px[j] and lvl > r_lvl[j]:
                    out[t, 3] = True; ref[t, 3] = r_bar[j]
            r_bar[nr] = t; r_lvl[nr] = lvl; r_px[nr] = wave_high; nr += 1
            wave_low = low[t]; wt1_min = wt1[t]
        elif t >= 2 and not np.isnan(wt1[t - 1]):
            recent_lo = min(low[t], min(low[t - 1], low[t - 2]))
            recent_hi = max(high[t], max(high[t - 1], high[t - 2]))
            if wt1[t] < wt2[t] and wt1[t] > wt1[t - 1]:
                for j in range(ng - 1, -1, -1):
                    if t - g_bar[j] > fr_age:
                        break
                    if g_lvl[j] <= os_level:
                        if recent_lo < g_px[j] and wt1_min > g_lvl[j]:
                            fr[t, 0] = True
                        break
            if wt1[t] > wt2[t] and wt1[t] < wt1[t - 1]:
                for j in range(nr - 1, -1, -1):
                    if t - r_bar[j] > fr_age:
                        break
                    if r_lvl[j] >= ob_level:
                        if recent_hi > r_px[j] and wt1_max < r_lvl[j]:
                            fr[t, 1] = True
                        break
    return out, ref, fr, wave_lo, wave_hi


def wt_dot_divergences_v2(wt: pd.DataFrame, bars: pd.DataFrame, lookback_dots: int = 5, max_dist: int = 300,
                          os_level: float = -53, ob_level: float = 53, fr_age: int = 50) -> pd.DataFrame:
    out, ref, fr, wlo, whi = _wt_dots_v2(wt["wt1"].to_numpy(np.float64), wt["wt2"].to_numpy(np.float64),
                                         bars["low"].to_numpy(np.float64), bars["high"].to_numpy(np.float64),
                                         wt["dot_green"].to_numpy(np.bool_), wt["dot_red"].to_numpy(np.bool_),
                                         lookback_dots, max_dist, float(os_level), float(ob_level), fr_age)
    df = pd.DataFrame(out, index=wt.index, columns=[f"wtdiv_{c}" for c in EVENT_COLS])
    for k, c in enumerate(EVENT_COLS):
        df[f"wtdiv_{c}_ref"] = ref[:, k]
    df["wtdiv_fr_bull"], df["wtdiv_fr_bear"] = fr[:, 0], fr[:, 1]
    df["wave_low"], df["wave_high"] = wlo, whi
    return df


@nb.njit(cache=True)
def _mf_fractal_v2(mf, low, high, bot_limit, top_limit, fr_age):
    """Old FROZEN_SPEC / MCB_Clone_v1 f_findDivs logic. Pivot at p known at c = p + 2 (5-bar fractal, strict).
    Counting pivots pass the level filter; each is compared with the previous counting pivot only.
    Price at pivot = lowest low (highest high) over p-2..p. Front-run bull at t: reference = previous counting pivot
    low, known (p_ref + 2 <= t) and p_ref >= t - fr_age, p_ref < t - 1; min(low[t-2..t]) < lowest low over
    p_ref-4..p_ref; mf[t-1] > mf[p_ref]; mf[t] > mf[t-1]."""
    n = mf.shape[0]
    out = np.zeros((n, 4), dtype=np.bool_)
    piv = np.full((n, 4), -1, dtype=np.int64)   # pivot bar of the signal (for leg timing)
    fr = np.zeros((n, 2), dtype=np.bool_)
    lo_p = -1; lo_v = 0.0; lo_px = 0.0; lo_ext = 0.0
    hi_p = -1; hi_v = 0.0; hi_px = 0.0; hi_ext = 0.0
    for c in range(n):
        # ---- front-run at bar c against the last known counting pivot ----
        if c >= 2 and not np.isnan(mf[c]) and not np.isnan(mf[c - 1]):
            rlo = min(low[c], min(low[c - 1], low[c - 2]))
            rhi = max(high[c], max(high[c - 1], high[c - 2]))
            if lo_p >= 0 and lo_p >= c - fr_age and lo_p < c - 1 and mf[c] > mf[c - 1] and mf[c - 1] > lo_v and rlo < lo_ext:
                fr[c, 0] = True
            if hi_p >= 0 and hi_p >= c - fr_age and hi_p < c - 1 and mf[c] < mf[c - 1] and mf[c - 1] < hi_v and rhi > hi_ext:
                fr[c, 1] = True
        # ---- confirmed pivot at p = c - 2 ----
        p = c - 2
        if p < 2:
            continue
        a, b, x, d, e = mf[p - 2], mf[p - 1], mf[p], mf[p + 1], mf[c]
        if np.isnan(a) or np.isnan(b) or np.isnan(x) or np.isnan(d) or np.isnan(e):
            continue
        if a > x and b > x and d > x and e > x and x <= bot_limit:
            px = min(low[p], min(low[p - 1], low[p - 2]))
            if lo_p >= 0:
                if px < lo_px and x > lo_v:
                    out[c, 0] = True; piv[c, 0] = p
                if px > lo_px and x < lo_v:
                    out[c, 1] = True; piv[c, 1] = p
            ext = px
            for k in range(max(p - 4, 0), p + 1):
                ext = min(ext, low[k])
            lo_p = p; lo_v = x; lo_px = px; lo_ext = ext
        if a < x and b < x and d < x and e < x and x >= top_limit:
            px = max(high[p], max(high[p - 1], high[p - 2]))
            if hi_p >= 0:
                if px > hi_px and x < hi_v:
                    out[c, 2] = True; piv[c, 2] = p
                if px < hi_px and x > hi_v:
                    out[c, 3] = True; piv[c, 3] = p
            ext = px
            for k in range(max(p - 4, 0), p + 1):
                ext = max(ext, high[k])
            hi_p = p; hi_v = x; hi_px = px; hi_ext = ext
    return out, piv, fr


def mf_fractal_divergences_v2(mf, bars: pd.DataFrame, bot_limit: float = -2.5, top_limit: float = 2.5,
                              fr_age: int = 50) -> pd.DataFrame:
    out, piv, fr = _mf_fractal_v2(np.asarray(mf, dtype=np.float64), bars["low"].to_numpy(np.float64),
                                  bars["high"].to_numpy(np.float64), float(bot_limit), float(top_limit), fr_age)
    df = pd.DataFrame(out, index=bars.index, columns=[f"mfdiv_{c}" for c in EVENT_COLS])
    for k, c in enumerate(EVENT_COLS):
        df[f"mfdiv_{c}_pivot"] = piv[:, k]
    df["mfdiv_fr_bull"], df["mfdiv_fr_bear"] = fr[:, 0], fr[:, 1]
    return df


@nb.njit(cache=True)
def _stack_b(wt_fr, mf_fr, wt_reg, mf_reg, mf_piv, window):
    """Frozen-spec front-run stack for one side. Fires at t when leg 2 front-runs and leg 1 (the other oscillator's
    confirmed regular divergence) has its pivot bar within `window` bars before t and is known by t.
    One entry per leg-1 event."""
    n = wt_fr.shape[0]
    out = np.zeros(n, dtype=np.bool_)
    last_wt = -10**9; last_mf_piv = -10**9  # most recent confirmed leg-1 events (WT dot bar, MF pivot bar)
    used_wt = -1; used_mf = -1
    for t in range(n):
        if wt_reg[t]:
            last_wt = t
        if mf_reg[t]:
            last_mf_piv = mf_piv[t]
        if mf_fr[t] and t - last_wt <= window and last_wt != used_wt:
            out[t] = True; used_wt = last_wt
            continue
        if wt_fr[t] and t - last_mf_piv <= window and last_mf_piv != used_mf:
            out[t] = True; used_mf = last_mf_piv
    return out


def stack_b_v2(df: pd.DataFrame, side: str, window: int = 11) -> np.ndarray:
    return _stack_b(df[f"wtdiv_fr_{side}"].to_numpy(np.bool_), df[f"mfdiv_fr_{side}"].to_numpy(np.bool_),
                    df[f"wtdiv_{side}_reg"].to_numpy(np.bool_), df[f"mfdiv_{side}_reg"].to_numpy(np.bool_),
                    df[f"mfdiv_{side}_reg_pivot"].to_numpy(np.int64), window)
