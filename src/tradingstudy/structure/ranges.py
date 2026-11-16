"""Ranges and the range-flip setup (brief 5.6). Runs on the bars of ONE timeframe using that timeframe's zigzag swings.

Range (confirmed, causal; defaults frozen in PROTOCOL section 6): evaluated each time a swing is confirmed, on the last four confirmed swings (two highs and
two lows, since swings alternate):
  - |high1 - high2| <= tol x ATR and |low1 - low2| <= tol x ATR
  - range high = max(highs), range low = min(lows); height (high - low) between h_min and h_max ATR
  - duration (first to last pivot bar) >= min_bars
  ATR is the ATR(14) at the confirming bar. The range exists from that bar's close. While a range is active, a new swing
  within tol of a boundary adds a touch.
Breakdown: a close below range low - brk x ATR (breakout mirrored). The range then ends and a bearish flip setup starts.
Bearish range flip (bullish mirrored):
  1. range confirmed  2. breakdown close  3. a lower swing low confirmed after the breakdown bar
  4. retest: a bar's high reaches the zone [range_low - ztol x ATR, ...]
  5. rejection (Variant A, confirmed): a bar that touched the zone closes below the range low with a bearish body.
     Variant B (front-run): the first touch bar itself, if it does not invalidate.
  Invalidation: a close above range_low + inval x ATR. Expiry: more than `expiry` bars after the breakdown.
  One event per variant per breakdown. Events are stamped on the bar whose close confirms them.
"""
from __future__ import annotations

import numba as nb
import numpy as np
import pandas as pd

from tradingstudy.features import ta

DEFAULTS = dict(tol=1.0, h_min=2.0, h_max=12.0, min_bars=10, brk=0.25, ztol=0.25, inval=0.5, expiry=200)
EV_COLS = ["bar", "direction", "variant", "range_high", "range_low", "range_start", "range_confirm", "break_bar",
           "new_swing_px", "atr_at_break", "touches"]
RANGE_COLS = ["start", "confirm", "end", "high", "low", "atr", "touches", "outcome"]  # outcome +1 breakout, -1 breakdown, 0 active


@nb.njit(cache=True)
def _ranges_flips(o, h, l, c, atr, sw_px, sw_type, sw_piv, sw_conf, tol, h_min, h_max, min_bars, brk, ztol, inval, expiry):
    n = c.shape[0]
    ns = sw_px.shape[0]
    # per-bar state
    st_active = np.zeros(n, dtype=np.bool_)
    st_hi = np.full(n, np.nan)
    st_lo = np.full(n, np.nan)
    # events (max 2 per breakdown) and ranges
    ev = np.full((2 * ns + 2, 11), np.nan)
    ne = 0
    rg = np.full((ns + 1, 8), np.nan)
    nr = 0
    active = False
    r_hi = r_lo = r_atr = 0.0
    r_start = r_conf = -1
    r_touch = 0
    # flip setups: index 0 bearish (after breakdown), 1 bullish (after breakout)
    f_alive = np.zeros(2, dtype=np.bool_)
    f_level = np.zeros(2); f_atr = np.zeros(2); f_break = np.zeros(2, dtype=np.int64)
    f_newswing = np.zeros(2, dtype=np.bool_); f_newpx = np.zeros(2)
    f_touched = np.zeros(2, dtype=np.bool_); f_doneA = np.zeros(2, dtype=np.bool_); f_doneB = np.zeros(2, dtype=np.bool_)
    f_rhi = np.zeros(2); f_rlo = np.zeros(2); f_rstart = np.zeros(2); f_rconf = np.zeros(2); f_touches = np.zeros(2)
    si = 0  # next swing to process
    for t in range(n):
        a = atr[t]
        # ---- flip setups progress on this bar (before new swings so a swing confirmed this bar counts for step 3) ----
        while si < ns and sw_conf[si] == t:
            # step 3: lower low / higher high swing after breakdown / breakout
            for d in range(2):
                if f_alive[d] and not f_newswing[d] and sw_conf[si] > f_break[d]:
                    if d == 0 and sw_type[si] == -1 and sw_px[si] < f_level[d]:
                        f_newswing[d] = True; f_newpx[d] = sw_px[si]
                    if d == 1 and sw_type[si] == 1 and sw_px[si] > f_level[d]:
                        f_newswing[d] = True; f_newpx[d] = sw_px[si]
            # range detection / extension
            if active:
                p = sw_px[si]
                if (sw_type[si] == 1 and abs(p - r_hi) <= tol * a) or (sw_type[si] == -1 and abs(p - r_lo) <= tol * a):
                    r_touch += 1
            elif si >= 3 and not np.isnan(a):
                hs = np.empty(2); ls = np.empty(2); nh = 0; nl = 0
                for j in range(si - 3, si + 1):
                    if sw_type[j] == 1:
                        if nh < 2:
                            hs[nh] = sw_px[j]
                        nh += 1
                    else:
                        if nl < 2:
                            ls[nl] = sw_px[j]
                        nl += 1
                if nh == 2 and nl == 2:
                    hi_ = max(hs[0], hs[1]); lo_ = min(ls[0], ls[1])
                    height = hi_ - lo_
                    dur = sw_piv[si] - sw_piv[si - 3]
                    if (abs(hs[0] - hs[1]) <= tol * a and abs(ls[0] - ls[1]) <= tol * a and height >= h_min * a
                            and height <= h_max * a and dur >= min_bars and c[t] < hi_ + brk * a and c[t] > lo_ - brk * a):
                        active = True; r_hi = hi_; r_lo = lo_; r_atr = a; r_start = sw_piv[si - 3]; r_conf = t; r_touch = 4
            si += 1
        if np.isnan(a):
            continue
        # ---- breakout / breakdown of the active range ----
        if active and t > r_conf:
            d = -1
            if c[t] < r_lo - brk * a:
                d = 0
            elif c[t] > r_hi + brk * a:
                d = 1
            if d >= 0:
                rg[nr, 0] = r_start; rg[nr, 1] = r_conf; rg[nr, 2] = t; rg[nr, 3] = r_hi; rg[nr, 4] = r_lo
                rg[nr, 5] = r_atr; rg[nr, 6] = r_touch; rg[nr, 7] = -1 if d == 0 else 1
                nr += 1
                active = False
                f_alive[d] = True; f_level[d] = r_lo if d == 0 else r_hi; f_atr[d] = a; f_break[d] = t
                f_newswing[d] = False; f_touched[d] = False; f_doneA[d] = False; f_doneB[d] = False
                f_rhi[d] = r_hi; f_rlo[d] = r_lo; f_rstart[d] = r_start; f_rconf[d] = r_conf; f_touches[d] = r_touch
        # ---- flip setup steps 4-5 ----
        for d in range(2):
            if not f_alive[d] or t <= f_break[d]:
                continue
            lvl = f_level[d]
            if t - f_break[d] > expiry:
                f_alive[d] = False
                continue
            if d == 0:
                invalid = c[t] > lvl + inval * a
                touch = h[t] >= lvl - ztol * a
                reject = touch and c[t] < lvl and c[t] < o[t]
            else:
                invalid = c[t] < lvl - inval * a
                touch = l[t] <= lvl + ztol * a
                reject = touch and c[t] > lvl and c[t] > o[t]
            if invalid:
                f_alive[d] = False
                continue
            if not f_newswing[d]:
                continue
            for variant in range(2):
                fire = False
                if variant == 0 and not f_doneA[d] and reject:
                    fire = True; f_doneA[d] = True
                if variant == 1 and not f_doneB[d] and touch:
                    fire = True; f_doneB[d] = True
                if fire:
                    ev[ne, 0] = t; ev[ne, 1] = -1 if d == 0 else 1; ev[ne, 2] = variant
                    ev[ne, 3] = f_rhi[d]; ev[ne, 4] = f_rlo[d]; ev[ne, 5] = f_rstart[d]; ev[ne, 6] = f_rconf[d]
                    ev[ne, 7] = f_break[d]; ev[ne, 8] = f_newpx[d]; ev[ne, 9] = f_atr[d]; ev[ne, 10] = f_touches[d]
                    ne += 1
            if f_doneA[d] and f_doneB[d]:
                f_alive[d] = False
        st_active[t] = active
        if active:
            st_hi[t] = r_hi; st_lo[t] = r_lo
    if active:
        rg[nr, 0] = r_start; rg[nr, 1] = r_conf; rg[nr, 2] = n - 1; rg[nr, 3] = r_hi; rg[nr, 4] = r_lo
        rg[nr, 5] = r_atr; rg[nr, 6] = r_touch; rg[nr, 7] = 0
        nr += 1
    return st_active, st_hi, st_lo, ev[:ne], rg[:nr]


def ranges_and_flips(bars: pd.DataFrame, swings: pd.DataFrame, **params):
    p = {**DEFAULTS, **params}
    o, h, l, c = (bars[k].to_numpy(np.float64) for k in ("open", "high", "low", "close"))
    atr = ta.atr(h, l, c, 14)
    st_active, st_hi, st_lo, ev, rg = _ranges_flips(
        o, h, l, c, atr, swings["price"].to_numpy(np.float64), swings["type"].to_numpy(np.int64),
        swings["pivot_bar"].to_numpy(np.int64), swings["confirm_bar"].to_numpy(np.int64),
        float(p["tol"]), float(p["h_min"]), float(p["h_max"]), int(p["min_bars"]), float(p["brk"]),
        float(p["ztol"]), float(p["inval"]), int(p["expiry"]))
    state = pd.DataFrame({"range_active": st_active, "range_high": st_hi, "range_low": st_lo, "atr14": atr}, index=bars.index)
    events = pd.DataFrame(ev, columns=EV_COLS)
    for col in ["bar", "direction", "variant", "range_start", "range_confirm", "break_bar", "touches"]:
        events[col] = events[col].astype("int64")
    events["time"] = bars.index[events["bar"].to_numpy()]
    ranges = pd.DataFrame(rg, columns=RANGE_COLS)
    for col in ["start", "confirm", "end", "touches", "outcome"]:
        ranges[col] = ranges[col].astype("int64")
    return state, events, ranges


# =====================================================================================================================
# v2 (PROTOCOL Amendment 1): setups are ARMED on the range TF (steps 1-3), the retest (steps 4-5) is scanned on any
# execution TF with the "respect" rule. v1 above is kept unchanged so Phase 2 results stay reproducible.
# =====================================================================================================================
SETUP_COLS = ["direction", "level", "atr_brk", "break_bar", "armed_bar", "range_high", "range_low", "range_start",
              "range_confirm", "new_swing_px", "touches"]


@nb.njit(cache=True)
def _range_setups(c, atr, sw_px, sw_type, sw_piv, sw_conf, tol, h_min, h_max, min_bars, brk, inval, expiry):
    n = c.shape[0]
    ns = sw_px.shape[0]
    st_active = np.zeros(n, dtype=np.bool_); st_hi = np.full(n, np.nan); st_lo = np.full(n, np.nan)
    setups = np.full((ns + 2, 11), np.nan); nsu = 0
    rg = np.full((ns + 1, 8), np.nan); nr = 0
    active = False
    r_hi = r_lo = r_atr = 0.0
    r_start = r_conf = -1; r_touch = 0
    f_alive = np.zeros(2, dtype=np.bool_); f_level = np.zeros(2); f_atr = np.zeros(2); f_break = np.zeros(2, dtype=np.int64)
    f_rhi = np.zeros(2); f_rlo = np.zeros(2); f_rstart = np.zeros(2); f_rconf = np.zeros(2); f_touches = np.zeros(2)
    si = 0
    for t in range(n):
        a = atr[t]
        # pre-arming invalidation / expiry on the range TF
        for d in range(2):
            if f_alive[d] and t > f_break[d] and not np.isnan(a):
                if t - f_break[d] > expiry or (d == 0 and c[t] > f_level[d] + inval * a) or (d == 1 and c[t] < f_level[d] - inval * a):
                    f_alive[d] = False
        while si < ns and sw_conf[si] == t:
            for d in range(2):
                if f_alive[d] and sw_conf[si] > f_break[d]:
                    ok = (d == 0 and sw_type[si] == -1 and sw_px[si] < f_level[d]) or (d == 1 and sw_type[si] == 1 and sw_px[si] > f_level[d])
                    if ok:
                        setups[nsu, 0] = -1 if d == 0 else 1; setups[nsu, 1] = f_level[d]; setups[nsu, 2] = f_atr[d]
                        setups[nsu, 3] = f_break[d]; setups[nsu, 4] = t; setups[nsu, 5] = f_rhi[d]; setups[nsu, 6] = f_rlo[d]
                        setups[nsu, 7] = f_rstart[d]; setups[nsu, 8] = f_rconf[d]; setups[nsu, 9] = sw_px[si]; setups[nsu, 10] = f_touches[d]
                        nsu += 1
                        f_alive[d] = False
            if active:
                p = sw_px[si]
                if (sw_type[si] == 1 and abs(p - r_hi) <= tol * a) or (sw_type[si] == -1 and abs(p - r_lo) <= tol * a):
                    r_touch += 1
            elif si >= 3 and not np.isnan(a):
                hs = np.empty(2); ls = np.empty(2); nh = 0; nl = 0
                for j in range(si - 3, si + 1):
                    if sw_type[j] == 1:
                        if nh < 2:
                            hs[nh] = sw_px[j]
                        nh += 1
                    else:
                        if nl < 2:
                            ls[nl] = sw_px[j]
                        nl += 1
                if nh == 2 and nl == 2:
                    hi_ = max(hs[0], hs[1]); lo_ = min(ls[0], ls[1]); height = hi_ - lo_
                    dur = sw_piv[si] - sw_piv[si - 3]
                    if (abs(hs[0] - hs[1]) <= tol * a and abs(ls[0] - ls[1]) <= tol * a and height >= h_min * a
                            and height <= h_max * a and dur >= min_bars and c[t] < hi_ + brk * a and c[t] > lo_ - brk * a):
                        active = True; r_hi = hi_; r_lo = lo_; r_atr = a; r_start = sw_piv[si - 3]; r_conf = t; r_touch = 4
            si += 1
        if np.isnan(a):
            continue
        if active and t > r_conf:
            d = -1
            if c[t] < r_lo - brk * a:
                d = 0
            elif c[t] > r_hi + brk * a:
                d = 1
            if d >= 0:
                rg[nr, 0] = r_start; rg[nr, 1] = r_conf; rg[nr, 2] = t; rg[nr, 3] = r_hi; rg[nr, 4] = r_lo
                rg[nr, 5] = r_atr; rg[nr, 6] = r_touch; rg[nr, 7] = -1 if d == 0 else 1
                nr += 1
                active = False
                f_alive[d] = True; f_level[d] = r_lo if d == 0 else r_hi; f_atr[d] = a; f_break[d] = t
                f_rhi[d] = r_hi; f_rlo[d] = r_lo; f_rstart[d] = r_start; f_rconf[d] = r_conf; f_touches[d] = r_touch
        st_active[t] = active
        if active:
            st_hi[t] = r_hi; st_lo[t] = r_lo
    if active:
        rg[nr, 0] = r_start; rg[nr, 1] = r_conf; rg[nr, 2] = n - 1; rg[nr, 3] = r_hi; rg[nr, 4] = r_lo
        rg[nr, 5] = r_atr; rg[nr, 6] = r_touch; rg[nr, 7] = 0
        nr += 1
    return st_active, st_hi, st_lo, setups[:nsu], rg[:nr]


@nb.njit(cache=True)
def _retest_scan(o, h, l, c, open_ns, s_dir, s_level, s_atr, s_start_ns, s_expiry_ns, ztol, inval):
    """Scan execution bars for each armed setup. Bearish: touch = high >= level - ztol*atr; respect = open <= level
    and close < level. Variant B = first touch bar that respects; Variant A = touch + respect + bearish body.
    Dead on a close above level + inval*atr or at expiry. Retest extreme = highest high from the first touch bar
    (respecting or not) to the firing bar. Output rows: setup, bar, variant, retest_extreme."""
    n = c.shape[0]
    ns = s_dir.shape[0]
    out = np.full((2 * ns, 4), np.nan)
    k = 0
    for s in range(ns):
        d = s_dir[s]; lvl = s_level[s]; a = s_atr[s]
        i0 = np.searchsorted(open_ns, s_start_ns[s])
        first = -1; doneA = False; doneB = False; ext = np.nan
        for i in range(i0, n):
            if open_ns[i] >= s_expiry_ns[s]:
                break
            if d == -1:
                if c[i] > lvl + inval * a:
                    break
                touch = h[i] >= lvl - ztol * a
                respect = o[i] <= lvl and c[i] < lvl
                body = c[i] < o[i]
            else:
                if c[i] < lvl - inval * a:
                    break
                touch = l[i] <= lvl + ztol * a
                respect = o[i] >= lvl and c[i] > lvl
                body = c[i] > o[i]
            if touch and first < 0:
                first = i
                ext = h[i] if d == -1 else l[i]
            elif first >= 0:
                ext = max(ext, h[i]) if d == -1 else min(ext, l[i])
            if touch and respect:
                if not doneB:
                    out[k, 0] = s; out[k, 1] = i; out[k, 2] = 1; out[k, 3] = ext; k += 1; doneB = True
                if body and not doneA:
                    out[k, 0] = s; out[k, 1] = i; out[k, 2] = 0; out[k, 3] = ext; k += 1; doneA = True
            if doneA and doneB:
                break
    return out[:k]


def range_setups_v2(bars: pd.DataFrame, swings: pd.DataFrame, **params):
    p = {**DEFAULTS, **params}
    o, h, l, c = (bars[k].to_numpy(np.float64) for k in ("open", "high", "low", "close"))
    atr = ta.atr(h, l, c, 14)
    st_active, st_hi, st_lo, su, rg = _range_setups(
        c, atr, swings["price"].to_numpy(np.float64), swings["type"].to_numpy(np.int64),
        swings["pivot_bar"].to_numpy(np.int64), swings["confirm_bar"].to_numpy(np.int64),
        float(p["tol"]), float(p["h_min"]), float(p["h_max"]), int(p["min_bars"]), float(p["brk"]),
        float(p["inval"]), int(p["expiry"]))
    state = pd.DataFrame({"range_active": st_active, "range_high": st_hi, "range_low": st_lo, "atr14": atr}, index=bars.index)
    setups = pd.DataFrame(su, columns=SETUP_COLS)
    for col in ["direction", "break_bar", "armed_bar", "range_start", "range_confirm", "touches"]:
        setups[col] = setups[col].astype("int64")
    ranges = pd.DataFrame(rg, columns=RANGE_COLS)
    for col in ["start", "confirm", "end", "touches", "outcome"]:
        ranges[col] = ranges[col].astype("int64")
    return state, setups, ranges


def scan_retests(setups: pd.DataFrame, range_bars: pd.DataFrame, range_minutes: int, exec_bars: pd.DataFrame,
                 exec_minutes: int, same_tf: bool, **params) -> pd.DataFrame:
    """Retest events on the execution bars. Same TF: scanning starts AT the armed bar (as in v1). Higher-TF range:
    scanning starts at the first execution bar opening at or after the armed range-TF bar's close."""
    p = {**DEFAULTS, **params}
    if setups.empty:
        return pd.DataFrame(columns=["setup", "bar", "variant", "retest_extreme"])
    ri = range_bars.index.as_unit("ns")
    armed_open = ri[setups["armed_bar"].to_numpy()].asi8
    start = armed_open if same_tf else armed_open + range_minutes * 60 * 10**9
    brk_open = ri[setups["break_bar"].to_numpy()].asi8
    expiry = brk_open + (int(p["expiry"]) + 1) * range_minutes * 60 * 10**9
    o, h, l, c = (exec_bars[k].to_numpy(np.float64) for k in ("open", "high", "low", "close"))
    ev = _retest_scan(o, h, l, c, exec_bars.index.as_unit("ns").asi8, setups["direction"].to_numpy(np.int64),
                      setups["level"].to_numpy(np.float64), setups["atr_brk"].to_numpy(np.float64),
                      start.astype(np.int64), expiry.astype(np.int64), float(p["ztol"]), float(p["inval"]))
    out = pd.DataFrame(ev, columns=["setup", "bar", "variant", "retest_extreme"])
    for col in ["setup", "bar", "variant"]:
        out[col] = out[col].astype("int64")
    out = out.join(setups.drop(columns=["break_bar", "armed_bar"]).reset_index(drop=True), on="setup")
    out["time"] = exec_bars.index[out["bar"].to_numpy()]
    return out
