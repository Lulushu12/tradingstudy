"""
House conventions for the ambiguities the videos never resolve.

Three of the four gaps recorded in STRATEGY_CATALOG.md are settled here so that
every strategy answers them the same way and the results stay comparable:

  1. "Stop below the recent low" has three readings, all tested.
  2. Multi step setups expire after EXPIRY_BARS between consecutive steps.
  3. "A strong trend" / "a large move" is a minimum leg size in ATR units.

The fourth gap, "target the previous high", is resolved per strategy because the
videos do give a usable reference in each case.
"""

import numpy as np
import pandas as pd

import indicators as ta

EXPIRY_BARS = 20          # max bars between consecutive steps of a setup
MIN_LEG_ATR = 3.0         # a move must span this many ATR to count as a leg
PIVOT_LEFT = 2
PIVOT_RIGHT = 2

STOP_CONVENTIONS = ("swing", "nbar", "atr")


def stop_levels(df, conv, nbar=10, atr_mult=1.5):
    """Candidate stop prices for a long and for a short, per convention.

    swing : most recent CONFIRMED fractal pivot. Closest to what the videos draw
            on charts, and it moves with structure.
    nbar  : lowest low / highest high of the last `nbar` bars. Purely mechanical.
    atr   : a fixed ATR multiple from the close. Volatility normalised.

    All three are causal. The swing reading uses confirmed pivots only, so the
    level present on bar t was already knowable at t.
    """
    if conv == "swing":
        ph, pl = ta.last_pivot_levels(df["high"], df["low"], PIVOT_LEFT, PIVOT_RIGHT)
        return pl, ph
    if conv == "nbar":
        return (df["low"].rolling(nbar, min_periods=nbar).min(),
                df["high"].rolling(nbar, min_periods=nbar).max())
    if conv == "atr":
        a = ta.atr(df["high"], df["low"], df["close"], 14)
        return df["close"] - atr_mult * a, df["close"] + atr_mult * a
    raise ValueError(f"unknown stop convention {conv}")


def legs(df, left=PIVOT_LEFT, right=PIVOT_RIGHT, min_atr=MIN_LEG_ATR):
    """Alternating swing legs, each usable only from its confirmation bar on.

    Returns a list of dicts with the leg's start and end index and price, its
    direction, and `known_at`: the bar index from which a strategy may reference
    the leg without looking ahead. Legs shorter than `min_atr` ATR are dropped,
    which is how "a large move" gets a definition.
    """
    ph, pl = ta.pivots(df["high"], df["low"], left, right)
    a = ta.atr(df["high"], df["low"], df["close"], 14).to_numpy(float)

    events = []
    phv, plv = ph.to_numpy(), pl.to_numpy()
    for i in range(len(df)):
        if not np.isnan(phv[i]):
            events.append((i - right, phv[i], 1, i))     # extreme_i, price, is_high, confirm_i
        if not np.isnan(plv[i]):
            events.append((i - right, plv[i], 0, i))
    events.sort(key=lambda e: (e[0], e[3]))

    # keep an alternating high/low chain, taking the more extreme of any run
    chain = []
    for e in events:
        if chain and chain[-1][2] == e[2]:
            better = e[1] > chain[-1][1] if e[2] == 1 else e[1] < chain[-1][1]
            if better:
                chain[-1] = e
            continue
        chain.append(e)

    out = []
    for a_, b_ in zip(chain, chain[1:]):
        si, sp, s_is_high, s_conf = a_
        ei, ep, e_is_high, e_conf = b_
        size = abs(ep - sp)
        ref = a[ei] if ei < len(a) and not np.isnan(a[ei]) else np.nan
        if np.isnan(ref) or ref <= 0 or size < min_atr * ref:
            continue
        out.append({
            "start_i": si, "start_px": float(sp),
            "end_i": ei, "end_px": float(ep),
            "dir": 1 if e_is_high else -1,      # +1 = up leg (low -> high)
            "known_at": e_conf,                 # leg is confirmed here
            "size": float(size),
        })
    return out


def empty_signals(df):
    f = pd.Series(False, index=df.index)
    n = pd.Series(np.nan, index=df.index)
    return f.copy(), f.copy(), n.copy(), n.copy()


def fill(series, i, value):
    series.iloc[i] = value
