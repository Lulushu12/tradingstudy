"""Signal, level placement and thesis generation.

The system is regime-conditional rather than directionally biased. At each
hourly close it classifies the tape into one of five states and trades the
setup that state implies:

  TREND_PULLBACK  - stacked EMAs, ADX confirming, price resting back into the
                    21 EMA. Buy the dip inside an intact trend.
  BREAKOUT        - stacked EMAs, ADX strong, close taking out the prior 48h
                    extreme on above-average volume. Join the expansion.
  EXHAUSTION      - price stretched >3.2 ATR from the 21 EMA with RSI at an
                    extreme while ADX is NOT strong. Fade the blow-off.
  RANGE_FADE      - ADX flat, price pinned at the edge of the Donchian
                    channel. Sell the top / buy the bottom of the range.
  DEFAULT         - nothing clean. Required anyway, because the mandate is to
                    enter on every close. Direction comes from a weighted
                    composite; conviction is scored low and the target is
                    deliberately modest.

Stops are ATR-scaled and then pushed *beyond* the last confirmed swing pivot,
so they sit past the obvious liquidity pool rather than on top of it. Targets
are an R-multiple of the resulting stop distance, sized to the setup: trends
get room to run, fades get taken quickly.
"""

import numpy as np

# setup -> (atr stop multiple, reward multiple, time stop in bars, base conviction)
SETUP_PARAMS = {
    "TREND_PULLBACK": (1.6, 2.5, 96, 5.0),
    "BREAKOUT": (1.5, 3.0, 120, 4.5),
    "RANGE_FADE": (1.3, 1.3, 36, 4.0),
    "EXHAUSTION": (1.1, 1.5, 24, 3.0),
    "DEFAULT": (1.5, 1.5, 48, 1.0),
}

MAX_STOP_ATR = 2.6
MIN_STOP_ATR = 0.6
MIN_STOP_PCT = 0.0015
SELECTIVE_THRESHOLD = 6.0

# ---------------------------------------------------------------------------
# System v2: the two changes the study actually supports.
#
# 1. Conviction is capped at 8.0, not just floored at 6.0. The 8-10 bucket was
#    negative on all three symbols (-0.124 R pooled, PF 0.84) while 6-8 was
#    positive on all three. The score is not monotonic with outcome, so the
#    most confident-looking setups get dropped rather than sized up.
#
# 2. RANGE_FADE is removed entirely. Both directions have a breakeven win rate
#    ABOVE their achieved win rate (48.6% vs 43.8% long, 49.5% vs 45.8% short):
#    a 1.3R target cannot pay for the losses at any hit rate those setups
#    reach. They lose by construction, not by variance - the only combinations
#    in the study of which that is true.
#
# Both are negative findings - things to stop doing. Nothing here adds a
# positive edge, and the v2 book still does not clear the bootstrap bar.
# ---------------------------------------------------------------------------
V2_CONVICTION_MIN = 6.0
V2_CONVICTION_MAX = 8.0
V2_EXCLUDED_SETUPS = frozenset({"RANGE_FADE"})

# Geometry: the sweep's average-R optimum, moderately wider than shipped.
V2_STOP_SCALE = 1.6
V2_TARGET_R = 4.0


def qualifies_v2(setup, conviction):
    """Does this signal belong in the v2 book?"""
    return (setup not in V2_EXCLUDED_SETUPS
            and V2_CONVICTION_MIN <= conviction < V2_CONVICTION_MAX)

# Structure-aware targeting: look for the wall before the target, not just an
# R multiple of the stop.
STRUCT_LOOKBACK = 240      # bars of history searched for opposing levels
STRUCT_MIN_R = 1.2         # a level closer than this is not worth trading toward
STRUCT_MAX_R = 6.0         # cap, so an empty chart does not produce a fantasy target
STRUCT_BUFFER_ATR = 0.15   # fill in FRONT of the level, not at it


def structure_target(direction, entry, stop, i, f, pivots, fallback_r):
    """Target the nearest opposing level that is far enough to be worth it.

    For a long that means the nearest confirmed swing HIGH above entry; for a
    short, the nearest confirmed swing LOW below it. Only pivots whose
    confirmation bar has already passed are eligible - filtering on the pivot
    bar itself would target levels that had not formed yet.

    Falls back to the setup's fixed R multiple when the chart is empty in that
    direction. Returns (target, r_multiple, basis).
    """
    risk = abs(entry - stop)
    a = f["atr"][i]
    side = pivots["highs"] if direction == 1 else pivots["lows"]

    if len(side["confirm"]):
        cut = int(np.searchsorted(side["confirm"], i, side="right"))
        if cut:
            pivot_idx = side["pivot"][:cut]
            price = side["price"][:cut]
            recent = pivot_idx >= i - STRUCT_LOOKBACK
            buf = STRUCT_BUFFER_ATR * a
            if direction == 1:
                ok = recent & (price - buf - entry >= STRUCT_MIN_R * risk)
                levels = price[ok]
                if len(levels):
                    lvl = float(levels.min())      # nearest overhead resistance
                    target = lvl - buf
                    r = (target - entry) / risk
                    if r > STRUCT_MAX_R:
                        return entry + STRUCT_MAX_R * risk, STRUCT_MAX_R, "6R cap (level far above)"
                    return target, r, f"swing high {lvl:.4f}"
            else:
                ok = recent & (entry - (price + buf) >= STRUCT_MIN_R * risk)
                levels = price[ok]
                if len(levels):
                    lvl = float(levels.max())      # nearest support below
                    target = lvl + buf
                    r = (entry - target) / risk
                    if r > STRUCT_MAX_R:
                        return entry - STRUCT_MAX_R * risk, STRUCT_MAX_R, "6R cap (level far below)"
                    return target, r, f"swing low {lvl:.4f}"

    return (entry + direction * fallback_r * risk, fallback_r,
            "no level in range - fixed R fallback")


def classify(i, f, close, prev_donch_hi, prev_donch_lo):
    """Return (setup, direction) for the close of bar i. direction is +1/-1."""
    c = close[i]
    e21, e55, e200 = f["ema21"][i], f["ema55"][i], f["ema200"][i]
    a = f["atr"][i]
    adx_v = f["adx"][i]
    rsi_v = f["rsi"][i]
    stretch = f["stretch"][i]
    dpos = f["donch_pos"][i]
    vz = f["vol_z"][i]

    stack_up = e21 > e55 > e200
    stack_dn = e21 < e55 < e200
    trend_up = stack_up and c > e200
    trend_dn = stack_dn and c < e200

    # 1. Pullback inside an intact trend.
    if trend_up and adx_v >= 22 and -2.2 < stretch < -0.25 and 35 <= rsi_v <= 58 and c > e55 - 0.5 * a:
        return "TREND_PULLBACK", 1
    if trend_dn and adx_v >= 22 and 0.25 < stretch < 2.2 and 42 <= rsi_v <= 65 and c < e55 + 0.5 * a:
        return "TREND_PULLBACK", -1

    # 2. Expansion out of the prior 48h range, with participation.
    if trend_up and adx_v >= 25 and c >= prev_donch_hi and vz >= 0.4 and stretch > 0.5:
        return "BREAKOUT", 1
    if trend_dn and adx_v >= 25 and c <= prev_donch_lo and vz >= 0.4 and stretch < -0.5:
        return "BREAKOUT", -1

    # 3. Blow-off fade - only where the trend is not strong enough to run us over.
    if adx_v < 30 and stretch >= 3.2 and rsi_v >= 78:
        return "EXHAUSTION", -1
    if adx_v < 30 and stretch <= -3.2 and rsi_v <= 22:
        return "EXHAUSTION", 1

    # 4. Range edge.
    if adx_v < 20 and stretch >= 1.6 and rsi_v >= 66 and dpos >= 0.82:
        return "RANGE_FADE", -1
    if adx_v < 20 and stretch <= -1.6 and rsi_v <= 34 and dpos <= 0.18:
        return "RANGE_FADE", 1

    # 5. No clean setup: weighted composite, with a mild fade tilt.
    score = 0.0
    score += 1.5 if stack_up else (-1.5 if stack_dn else 0.0)
    score += 1.0 if c > e200 else -1.0
    slope = f["ema200_slope"][i]
    if not np.isnan(slope):
        score += 0.8 * float(np.clip(slope, -1.0, 1.0))
    score += 0.6 if f["plus_di"][i] > f["minus_di"][i] else -0.6
    score += -0.7 * float(np.clip(stretch, -1.5, 1.5)) / 1.5
    score += 0.5 * (rsi_v - 50.0) / 50.0
    return "DEFAULT", (1 if score > 0 else -1)


def conviction(setup, direction, i, f, close):
    """0-10 confidence score. Drives the selective (high-conviction) book."""
    base = SETUP_PARAMS[setup][3]
    adx_v = f["adx"][i]
    rsi_v = f["rsi"][i]
    slope = f["ema200_slope"][i]
    vz = f["vol_z"][i]
    vr = f["vol_regime"][i]
    score = base

    if setup in ("TREND_PULLBACK", "BREAKOUT"):
        if adx_v >= 28:
            score += 1.5
        elif adx_v >= 24:
            score += 0.7
        if not np.isnan(slope) and slope * direction >= 0.5:
            score += 1.0
        if setup == "BREAKOUT" and vz >= 1.0:
            score += 1.0
        if setup == "TREND_PULLBACK" and 38 <= rsi_v <= 52:
            score += 0.5
    elif setup in ("RANGE_FADE", "EXHAUSTION"):
        if adx_v <= 16:
            score += 1.0
        if (direction == -1 and rsi_v >= 72) or (direction == 1 and rsi_v <= 28):
            score += 1.0
        if not np.isnan(slope) and abs(slope) < 0.3:
            score += 0.5  # flat macro trend: fades behave
    else:
        if not np.isnan(slope) and slope * direction >= 0.4:
            score += 0.8
        if adx_v >= 25:
            score += 0.4

    # Penalise the volatility extremes: the top decile is where stops get run
    # and the bottom decile is where targets never fill.
    if not np.isnan(vr):
        if 0.2 <= vr <= 0.8:
            score += 1.0
        elif vr > 0.92 or vr < 0.05:
            score -= 1.0

    return float(np.clip(score, 0.0, 10.0))


def levels(setup, direction, entry, i, f, pivots=None, target_mode="fixed_r"):
    """Place stop and target.

    target_mode "fixed_r" multiplies the stop distance by the setup's R value.
    "structure" instead targets the nearest confirmed opposing swing level,
    falling back to the fixed R when no level is in range.

    Returns (stop, target, time_stop, stop_note, r_multiple, target_note).
    """
    k_atr, r_mult, tstop, _ = SETUP_PARAMS[setup]
    a = f["atr"][i]
    atr_stop = entry - direction * k_atr * a
    note = f"{k_atr:.1f}x ATR"

    pivot = f["swing_lo"][i] if direction == 1 else f["swing_hi"][i]
    if not np.isnan(pivot):
        struct = pivot - direction * 0.25 * a
        # Only ever widen: the point is to sit past the pivot, never in front of it.
        if direction == 1 and struct < atr_stop:
            atr_stop, note = struct, f"beyond swing low {pivot:.4f}"
        elif direction == -1 and struct > atr_stop:
            atr_stop, note = struct, f"beyond swing high {pivot:.4f}"

    # Clamp the stop distance into a sane band.
    dist = abs(entry - atr_stop)
    max_d = MAX_STOP_ATR * a
    min_d = max(MIN_STOP_ATR * a, MIN_STOP_PCT * entry)
    if dist > max_d:
        dist, note = max_d, f"{MAX_STOP_ATR}x ATR cap"
    elif dist < min_d:
        dist, note = min_d, "min stop floor"

    stop = entry - direction * dist
    if target_mode in ("structure", "structure_extend") and pivots is not None:
        s_target, s_r, tnote = structure_target(direction, entry, stop, i, f, pivots, r_mult)
        if target_mode == "structure" or s_r > r_mult:
            target, r_mult = s_target, s_r
        else:
            # structure_extend: the wall is nearer than the setup's R multiple,
            # so ignore it and keep the original target.
            target = entry + direction * r_mult * dist
            tnote = f"{r_mult:.1f}R (nearer level ignored)"
    else:
        target = entry + direction * r_mult * dist
        tnote = f"{r_mult:.1f}R of stop distance"
    return stop, target, tstop, note, r_mult, tnote


_SETUP_PROSE = {
    "TREND_PULLBACK": "Trend pullback",
    "BREAKOUT": "Range expansion",
    "RANGE_FADE": "Range-edge fade",
    "EXHAUSTION": "Exhaustion fade",
    "DEFAULT": "Mandated fill",
}


def _ordinal(n):
    n = int(round(n))
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def thesis(setup, direction, i, f, close, entry, stop, target, r_mult, stop_note, conv,
           target_note="fixed R multiple"):
    """Compose the trade's reasoning from the actual state of the bar."""
    side = "long" if direction == 1 else "short"
    e21, e55, e200 = f["ema21"][i], f["ema55"][i], f["ema200"][i]
    adx_v, rsi_v = f["adx"][i], f["rsi"][i]
    stretch = f["stretch"][i]
    vr = f["vol_regime"][i]
    stack = "21>55>200" if e21 > e55 > e200 else ("21<55<200" if e21 < e55 < e200 else "EMAs tangled")

    head = f"{_SETUP_PROSE[setup]} {side}."

    if setup == "TREND_PULLBACK":
        body = (
            f"EMA stack {stack} with ADX {adx_v:.0f} confirming the trend still has force. "
            f"Price has eased {abs(stretch):.1f} ATR {'below' if direction == 1 else 'above'} the 21 EMA "
            f"and RSI has reset to {rsi_v:.0f} without the {'55 EMA breaking' if direction == 1 else 'trend turning'}, "
            f"so this is a pause rather than a reversal."
        )
        inval = f"a close {'below' if direction == 1 else 'above'} the 55 EMA ({e55:.4f}) breaks the premise"
    elif setup == "BREAKOUT":
        body = (
            f"Close has taken out the prior 48h {'high' if direction == 1 else 'low'} with volume "
            f"{f['vol_z'][i]:+.1f} sigma above normal, ADX {adx_v:.0f}, stack {stack}. "
            f"Participation confirms the break rather than a wick through an empty book."
        )
        inval = f"a return inside the broken level ({e21:.4f} area) marks it a failed break"
    elif setup == "RANGE_FADE":
        body = (
            f"ADX {adx_v:.0f} says no trend is in control. Price is pinned at the "
            f"{'top' if direction == -1 else 'bottom'} of the 48h range, {abs(stretch):.1f} ATR from the 21 EMA "
            f"with RSI {rsi_v:.0f}. Fading the edge back toward the mean at {e21:.4f}."
        )
        inval = "a sustained close outside the channel turns this into a breakout and kills the fade"
    elif setup == "EXHAUSTION":
        body = (
            f"Price is {abs(stretch):.1f} ATR from the 21 EMA with RSI {rsi_v:.0f} - a statistical extreme - "
            f"while ADX {adx_v:.0f} shows no trend strong enough to sustain it. Fading the blow-off, "
            f"small size and a tight leash."
        )
        inval = "any acceptance beyond the extreme means the move is real, not exhaustion"
    else:
        body = (
            f"Nothing here worth trading: ADX {adx_v:.0f}, RSI {rsi_v:.0f}, {stack}, "
            f"price {stretch:+.1f} ATR from the 21 EMA. "
            f"The mandate is to be in on every close, so direction comes from the weighted composite "
            f"(trend alignment, DI balance, and a fade tilt on stretch) and the target is kept modest. "
            f"This is a low-conviction fill, not a trade I would take standalone."
        )
        inval = "no structural thesis to break - the stop and the 48h time limit are the whole risk plan"

    vol_txt = (
        "" if np.isnan(vr)
        else f" Volatility sits in the {_ordinal(vr * 100)} percentile of the last 500h."
    )

    levels_txt = (
        f" Entry {entry:.4f}, stop {stop:.4f} ({stop_note}, {abs(entry - stop) / entry * 100:.2f}% away), "
        f"target {target:.4f} at {r_mult:.1f}R ({target_note}). "
        f"Invalidation: {inval}. Conviction {conv:.1f}/10."
    )
    return head + " " + body + vol_txt + levels_txt
