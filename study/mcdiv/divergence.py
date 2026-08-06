"""Divergence detection per FROZEN_SPEC.md (MCB Clone v1 logic).

All logic is causal: a 5-bar fractal pivot at bar p is CONFIRMED at bar p+2.
Divergence events are emitted at the confirmation bar and compare the current
pivot against the PREVIOUS level-qualifying pivot (valuewhen chain), price
checked at high[p]/low[p] of the pivot bars, exactly as the coded f_findDivs.

Regular divergences only. Hidden divergences excluded (spec section 3).
"""
import numpy as np
import pandas as pd
from dataclasses import dataclass


@dataclass
class DivEvent:
    osc: str          # "wt" or "mfi"
    direction: int    # +1 bull, -1 bear
    confirm_i: int    # bar index where fractal confirms (pivot_i + 2)
    pivot_i: int      # pivot bar index
    pivot_osc: float  # oscillator value at pivot bar
    pivot_price: float  # low (bull) / high (bear) at pivot bar
    ref_i: int        # reference (anchor) pivot bar index
    ref_osc: float    # oscillator value at anchor pivot
    ref_price: float  # low/high at anchor pivot
    tier: str         # "primary" or "secondary" (level filter tier)


def _fractals(osc: np.ndarray):
    """5-bar fractal tops/bottoms on the oscillator. Returns boolean arrays
    indexed by PIVOT bar p (requires strict center extreme like f_fractalize:
    src[4]<src[2] > src[0] pattern i.e. p is a top if osc[p] is the max of
    p-2..p+2 with strict inequality vs both immediate sides per the coded
    f_top_fractal: src[4]<src[2] and src[3]<src[2] and src[2]>src[1] and src[2]>src[0])."""
    n = len(osc)
    top = np.zeros(n, bool)
    bot = np.zeros(n, bool)
    s = osc
    for p in range(2, n - 2):
        if np.isnan(s[p - 2 : p + 3]).any():
            continue
        if s[p - 2] < s[p] and s[p - 1] < s[p] and s[p] > s[p + 1] and s[p] > s[p + 2]:
            top[p] = True
        if s[p - 2] > s[p] and s[p - 1] > s[p] and s[p] < s[p + 1] and s[p] < s[p + 2]:
            bot[p] = True
    return top, bot


def find_divs(osc: np.ndarray, high: np.ndarray, low: np.ndarray,
              top_limit: float, bot_limit: float, name: str, tier: str):
    """Port of f_findDivs(src, topLimit, botLimit, useLimits=true).

    A fractal only enters the valuewhen chain if it passes the level filter,
    so BOTH the current and the reference pivot are level-qualified.
    Bear: price higher high while osc lower high. Bull: price lower low while
    osc higher low. Emitted at confirmation bar (pivot+2).
    """
    top, bot = _fractals(osc)
    events = []
    prev_top = None  # (pivot_i, osc, price)
    for p in np.where(top)[0]:
        if osc[p] < top_limit:
            continue
        if prev_top is not None:
            if high[p] > prev_top[2] and osc[p] < prev_top[1]:
                events.append(DivEvent(name, -1, p + 2, p, osc[p], high[p],
                                       prev_top[0], prev_top[1], prev_top[2], tier))
        prev_top = (p, osc[p], high[p])
    prev_bot = None
    for p in np.where(bot)[0]:
        if osc[p] > bot_limit:
            continue
        if prev_bot is not None:
            if low[p] < prev_bot[2] and osc[p] > prev_bot[1]:
                events.append(DivEvent(name, +1, p + 2, p, osc[p], low[p],
                                       prev_bot[0], prev_bot[1], prev_bot[2], tier))
        prev_bot = (p, osc[p], low[p])
    return events


def all_div_events(df: pd.DataFrame):
    """All regular divergence events per spec level filters.

    WT (on wt2): bull <= -65 primary / <= -40 secondary; bear >= 45 / >= 15.
    MFI: bull <= -2.5, bear >= 2.5 (single tier, labeled primary).
    Secondary WT events that duplicate a primary event (same confirm bar &
    direction) are dropped; the primary tier label wins.
    """
    wt2 = df["wt2"].to_numpy(float)
    mfi = df["mfi"].to_numpy(float)
    high = df["high"].to_numpy(float)
    low = df["low"].to_numpy(float)

    wt_primary = find_divs(wt2, high, low, 45.0, -65.0, "wt", "primary")
    wt_secondary = find_divs(wt2, high, low, 15.0, -40.0, "wt", "secondary")
    seen = {(e.confirm_i, e.direction) for e in wt_primary}
    wt_events = wt_primary + [e for e in wt_secondary
                              if (e.confirm_i, e.direction) not in seen]
    mfi_events = find_divs(mfi, high, low, 2.5, -2.5, "mfi", "primary")
    return sorted(wt_events, key=lambda e: e.confirm_i), mfi_events


# ---------------- stacking (entry signals) ----------------

@dataclass
class Signal:
    system: str      # "A", "B", or "buggy"
    direction: int
    signal_i: int    # bar t; entry at open of t+1
    wt_ev: DivEvent | None
    mfi_ev: DivEvent | None
    leg1_osc: str    # which oscillator confirmed first
    gap_bars: int
    frontrun: bool
    # Variant B leg2 details (None for A):
    fr_ref_i: int | None = None
    fr_ref_osc: float | None = None


def stack_variant_a(wt_events, mfi_events, window=11):
    """Variant A: one WT div + one MFI div, same direction, confirmation bars
    within <=window bars (gap 0 valid). Entry next bar open. Each event is
    consumed by at most one signal (dedup rule: pair with the nearest
    unconsumed opposite-oscillator event; earliest completion fires)."""
    signals = []
    used_wt, used_mfi = set(), set()
    events = sorted(wt_events + mfi_events, key=lambda e: (e.confirm_i, e.osc))
    for k, e in enumerate(events):
        key = (e.osc, e.confirm_i, e.direction, e.pivot_i)
        if key in (used_wt | used_mfi):
            continue
        # find nearest earlier-or-equal unconsumed opposite-osc event in window
        best = None
        for e2 in events[:k + 1]:
            if e2.osc == e.osc or e2.direction != e.direction:
                continue
            k2 = (e2.osc, e2.confirm_i, e2.direction, e2.pivot_i)
            if k2 in (used_wt | used_mfi):
                continue
            if 0 <= e.confirm_i - e2.confirm_i <= window:
                if best is None or e2.confirm_i > best.confirm_i:
                    best = e2
        if best is None:
            continue
        wt_ev = e if e.osc == "wt" else best
        mfi_ev = e if e.osc == "mfi" else best
        used_wt.add((wt_ev.osc, wt_ev.confirm_i, wt_ev.direction, wt_ev.pivot_i))
        used_mfi.add((mfi_ev.osc, mfi_ev.confirm_i, mfi_ev.direction, mfi_ev.pivot_i))
        leg1 = best.osc if best.confirm_i < e.confirm_i else (
            "both" if best.confirm_i == e.confirm_i else e.osc)
        signals.append(Signal("A", e.direction, e.confirm_i, wt_ev, mfi_ev,
                              leg1, abs(e.confirm_i - best.confirm_i), False))
    return signals


def stack_buggy(wt_events, mfi_events, window=11):
    """Diagnostic only: any two same-direction div events within window,
    including WT+WT and MFI+MFI. Same consume-once dedup."""
    signals = []
    used = set()
    events = sorted(wt_events + mfi_events, key=lambda e: (e.confirm_i, e.osc))
    for k, e in enumerate(events):
        key = (e.osc, e.confirm_i, e.direction, e.pivot_i)
        if key in used:
            continue
        best = None
        for e2 in events[:k + 1]:
            if e2 is e or e2.direction != e.direction:
                continue
            k2 = (e2.osc, e2.confirm_i, e2.direction, e2.pivot_i)
            if k2 in used or k2 == key:
                continue
            if 0 <= e.confirm_i - e2.confirm_i <= window:
                if best is None or e2.confirm_i > best.confirm_i:
                    best = e2
        if best is None:
            continue
        used.add(key)
        used.add((best.osc, best.confirm_i, best.direction, best.pivot_i))
        wt_ev = e if e.osc == "wt" else (best if best.osc == "wt" else None)
        mfi_ev = e if e.osc == "mfi" else (best if best.osc == "mfi" else None)
        signals.append(Signal("buggy", e.direction, e.confirm_i, wt_ev, mfi_ev,
                              best.osc, abs(e.confirm_i - best.confirm_i), False))
    return signals


def _level_ok(osc_name, direction, ref_osc):
    if osc_name == "wt":
        return ref_osc <= -40.0 if direction > 0 else ref_osc >= 15.0
    return ref_osc <= -2.5 if direction > 0 else ref_osc >= 2.5


def stack_variant_b(df, wt_events, mfi_events, window=11, max_age=50):
    """Variant B front-run, per spec section 4.

    Leg 1: either oscillator's div, fully fractal-confirmed at bar c1.
    Leg 2: the OTHER oscillator via front-run at bar t (t >= c1):
      - reference anchor = most recent confirmed, level-qualified fractal pivot
        of the other oscillator, pivot age <= max_age bars from t
      - price exceeds the reference extreme (true extreme of the 5-bar swing
        buffer around the reference pivot bar)
      - oscillator holding on the divergent side of the reference value
      - oscillator ticked once in the reversal direction (osc[t] vs osc[t-1])
      - level filter tested on the reference anchor only
    Window: t - leg1.pivot_i <= window. Entry open of t+1. Front-run consumes
    the signal (one entry per leg1 event).
    """
    n = len(df)
    high = df["high"].to_numpy(float)
    low = df["low"].to_numpy(float)
    osc_arr = {"wt": df["wt2"].to_numpy(float), "mfi": df["mfi"].to_numpy(float)}

    # confirmed fractal pivots per oscillator (all, unfiltered), for anchors
    pivots = {}
    for name in ("wt", "mfi"):
        top, bot = _fractals(osc_arr[name])
        pivots[name] = {
            +1: [(p, osc_arr[name][p]) for p in np.where(bot)[0]],
            -1: [(p, osc_arr[name][p]) for p in np.where(top)[0]],
        }

    signals = []
    for leg1 in sorted(wt_events + mfi_events, key=lambda e: e.confirm_i):
        other = "mfi" if leg1.osc == "wt" else "wt"
        d = leg1.direction
        o = osc_arr[other]
        fired = False
        for t in range(leg1.confirm_i, min(leg1.pivot_i + window, n - 2) + 1):
            # reference anchor: most recent confirmed (pivot+2 <= t),
            # level-qualified pivot of the other oscillator, age <= max_age
            ref = None
            for (p, val) in reversed(pivots[other][d]):
                if p + 2 > t:
                    continue
                if t - p > max_age:
                    break
                if _level_ok(other, d, val):
                    ref = (p, val)
                    break
            if ref is None:
                continue
            p, ref_val = ref
            lo_w = max(0, p - 2)
            if d > 0:
                ref_ext = low[lo_w: p + 3].min()
                price_ok = low[t] < ref_ext
                side_ok = o[t] > ref_val
                tick_ok = o[t] > o[t - 1]
            else:
                ref_ext = high[lo_w: p + 3].max()
                price_ok = high[t] > ref_ext
                side_ok = o[t] < ref_val
                tick_ok = o[t] < o[t - 1]
            if price_ok and side_ok and tick_ok:
                wt_ev = leg1 if leg1.osc == "wt" else None
                mfi_ev = leg1 if leg1.osc == "mfi" else None
                signals.append(Signal("B", d, t, wt_ev, mfi_ev, leg1.osc,
                                      t - leg1.confirm_i, True,
                                      fr_ref_i=p, fr_ref_osc=ref_val))
                fired = True
                break
        if fired:
            continue
    # one signal per bar+direction (two leg1s can front-run on the same bar)
    dedup = {}
    for s in signals:
        dedup.setdefault((s.signal_i, s.direction), s)
    return sorted(dedup.values(), key=lambda s: s.signal_i)
