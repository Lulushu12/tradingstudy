"""Support/resistance levels that held, with role flips (brief 5.6), plus Fibonacci legs.

Held levels (per timeframe, causal):
  - Each confirmed zigzag swing is a reversal of at least k x ATR from its extreme. At its confirmation bar the swing
    price either adds a HOLD to an existing level within tol x ATR, or creates a new level.
    Swing highs create resistance, swing lows support.
  - Strength = sum of holds, each decayed by exp(-age / half_life_bars) (recent holds weigh more).
  - Break: a close beyond the level by more than brk x ATR. A broken level FLIPS role once (support becomes
    resistance and vice versa). A flipped level that is broken again is retired.
  - Snapshot per bar: the M levels nearest to the close (price, strength, role, flipped flag).
Fibonacci: the last confirmed leg A -> B (two most recent swings) and the two legs before it. Retracement level r
  of leg A -> B is B - r (B - A). Extension e is A + e (B - A).
"""
from __future__ import annotations

import numba as nb
import numpy as np
import pandas as pd

LEVEL_DEFAULTS = dict(tol=0.5, brk=0.25, half_life_days=30.0, max_levels=64, snapshot=12)


@nb.njit(cache=True)
def _held_levels(c, atr, sw_px, sw_type, sw_conf, tol, brk, hl_bars, max_levels, M):
    n = c.shape[0]
    ns = sw_px.shape[0]
    px = np.zeros(max_levels); s = np.zeros(max_levels); last = np.zeros(max_levels, dtype=np.int64)
    role = np.zeros(max_levels, dtype=np.int64)  # +1 resistance, -1 support
    flipped = np.zeros(max_levels, dtype=np.bool_); holds = np.zeros(max_levels, dtype=np.int64)
    alive = np.zeros(max_levels, dtype=np.bool_)
    out_px = np.full((n, M), np.nan); out_str = np.full((n, M), np.nan)
    out_role = np.zeros((n, M), dtype=np.int8); out_flip = np.zeros((n, M), dtype=np.bool_)
    out_holds = np.zeros((n, M), dtype=np.int16)
    si = 0
    dist = np.empty(max_levels)
    for t in range(n):
        a = atr[t]
        # breaks on this bar's close
        if not np.isnan(a):
            for j in range(max_levels):
                if not alive[j]:
                    continue
                if role[j] == -1 and c[t] < px[j] - brk * a:
                    if flipped[j]:
                        alive[j] = False
                    else:
                        role[j] = 1; flipped[j] = True
                elif role[j] == 1 and c[t] > px[j] + brk * a:
                    if flipped[j]:
                        alive[j] = False
                    else:
                        role[j] = -1; flipped[j] = True
        # swings confirmed on this bar
        while si < ns and sw_conf[si] == t:
            p = sw_px[si]
            best = -1; bd = np.inf
            for j in range(max_levels):
                if alive[j] and abs(px[j] - p) <= tol * a and abs(px[j] - p) < bd:
                    best = j; bd = abs(px[j] - p)
            if best >= 0:
                s[best] = s[best] * np.exp(-(t - last[best]) / hl_bars) + 1.0
                last[best] = t; holds[best] += 1
            else:
                # free slot, else replace the weakest
                slot = -1; weakest = np.inf
                for j in range(max_levels):
                    if not alive[j]:
                        slot = j
                        break
                    cur = s[j] * np.exp(-(t - last[j]) / hl_bars)
                    if cur < weakest:
                        weakest = cur; slot = j
                px[slot] = p; s[slot] = 1.0; last[slot] = t; holds[slot] = 1
                role[slot] = 1 if sw_type[si] == 1 else -1; flipped[slot] = False; alive[slot] = True
            si += 1
        # snapshot: M nearest alive levels
        for j in range(max_levels):
            dist[j] = abs(px[j] - c[t]) if alive[j] else np.inf
        order = np.argsort(dist)
        for m in range(M):
            j = order[m]
            if not alive[j]:
                break
            out_px[t, m] = px[j]; out_str[t, m] = s[j] * np.exp(-(t - last[j]) / hl_bars)
            out_role[t, m] = role[j]; out_flip[t, m] = flipped[j]; out_holds[t, m] = holds[j]
    return out_px, out_str, out_role, out_flip, out_holds


def held_levels(bars: pd.DataFrame, swings: pd.DataFrame, atr: np.ndarray, minutes: int, **params) -> dict:
    p = {**LEVEL_DEFAULTS, **params}
    hl_bars = p["half_life_days"] * 1440 / minutes
    px, st, ro, fl, ho = _held_levels(bars["close"].to_numpy(np.float64), atr, swings["price"].to_numpy(np.float64),
                                      swings["type"].to_numpy(np.int64), swings["confirm_bar"].to_numpy(np.int64),
                                      float(p["tol"]), float(p["brk"]), float(hl_bars), int(p["max_levels"]), int(p["snapshot"]))
    return {"price": px, "strength": st, "role": ro, "flipped": fl, "holds": ho}


def fib_legs(swings: pd.DataFrame, n_bars: int, legs: int = 3) -> np.ndarray:
    """Per bar of the swing timeframe: (A, B) of the last `legs` confirmed legs, newest first. Shape (n_bars, legs, 2).
    A leg is known from the confirmation bar of its later swing B."""
    out = np.full((n_bars, legs, 2), np.nan)
    px = swings["price"].to_numpy()
    cb = swings["confirm_bar"].to_numpy()
    for i in range(1, len(swings)):
        start = cb[i]
        end = cb[i + 1] if i + 1 < len(swings) else n_bars
        for g in range(legs):
            j = i - g
            if j >= 1:
                out[start:end, g, 0] = px[j - 1]
                out[start:end, g, 1] = px[j]
    return out


FIB_HTF = (0.382, 0.5, 0.618, 0.786)
FIB_EXEC = (0.618,)
FIB_EXEC_ZONE = (0.618, 0.65)


def fib_retrace(a, b, r):
    return b - r * (b - a)


def fib_extend(a, b, e):
    return a + e * (b - a)
