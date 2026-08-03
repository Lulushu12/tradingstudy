"""The four strategies, exactly as frozen in FROZEN_SPEC_TSM.md.

Each builder returns (signals_frame, engine_kwargs). Anything not stated in the source video
is marked INVENTED with the spec item it corresponds to, so the provenance of every rule is
readable in the code and not only in the spec.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from indicators import (atr, crossed_above, crossed_below, donchian, ema,
                        fractal_pivots, macd, mfi, monotonic_run)


def _blank(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({
        "entry": 0, "exit": False,
        "stop": np.nan, "stop_dist": np.nan, "target": np.nan, "trail": np.nan,
    }, index=df.index)


# --------------------------------------------------------------------------- S1
def s1_macd(df: pd.DataFrame, flip: bool) -> tuple[pd.DataFrame, dict]:
    """STATED: MACD(12,26,9); long on cross above signal, sell on cross below.
    INVENTED 1: fill at next bar open.  INVENTED 2: flat vs flip.  INVENTED 3: timeframe.
    No stop and no target are stated, so none is imposed."""
    line, sig = macd(df["close"])
    up, dn = crossed_above(line, sig), crossed_below(line, sig)

    s = _blank(df)
    s.loc[up, "entry"] = 1
    if flip:
        s.loc[dn, "entry"] = -1
    else:
        s.loc[dn, "exit"] = True
    return s, {}


# --------------------------------------------------------------------------- S2
def s2_donchian(df: pd.DataFrame, mid_exit: bool) -> tuple[pd.DataFrame, dict]:
    """STATED: close beyond the 20-period channel; 2xATR(20) stop; exit on either the
    opposite band or the 50-channel midpoint.
    INVENTED 1: channel excludes the current bar.  INVENTED 2: both exits run, declared."""
    hi20, lo20 = donchian(df, 20, exclude_current=True)
    hi50, lo50 = donchian(df, 50, exclude_current=True)
    a = atr(df, 20)

    s = _blank(df)
    s.loc[df["close"] > hi20, "entry"] = 1
    s.loc[df["close"] < lo20, "entry"] = -1
    s["stop_dist"] = 2.0 * a

    if mid_exit:
        # The 50-channel midpoint sits BELOW a long breakout entry, so "exit on a touch of
        # the midpoint" is a give-back exit that fires when price falls back to it, not a
        # profit target price rises into. Modelled as a trailing level, which is what the
        # Turtle-style rule the video describes actually is.
        s["trail"] = (hi50 + lo50) / 2.0
    else:
        # opposite-band exit: a long closes out on a close back below the 20-period low
        s.loc[df["close"] < lo20, "exit"] = True
        s.loc[df["close"] > hi20, "exit"] = True
    return s, {}


# --------------------------------------------------------------------------- S3
def s3_mfi(df: pd.DataFrame, use_stop: bool) -> tuple[pd.DataFrame, dict]:
    """STATED: MFI(50) crossing the 50 centreline, filtered by price vs the 200 EMA.
    INVENTED 1: 2xATR(14) stop (nothing is stated) and a no-stop variant.
    INVENTED 2: exit on the opposite crossover.  INVENTED 3: daily timeframe."""
    m = mfi(df, 50)
    e200 = ema(df["close"], 200)
    up, dn = crossed_above(m, pd.Series(50.0, index=df.index)), crossed_below(m, pd.Series(50.0, index=df.index))

    s = _blank(df)
    s.loc[up & (df["close"] > e200), "entry"] = 1
    s.loc[dn & (df["close"] < e200), "entry"] = -1
    # opposite cross closes the position even when the filter blocks a new entry
    s.loc[(up | dn) & (s["entry"] == 0), "exit"] = True
    if use_stop:
        s["stop_dist"] = 2.0 * atr(df, 14)
    return s, {}


# --------------------------------------------------------------------------- S4
def s4_outside_bar(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """STATED: daily; EMA20/50 aligned, sloping, price on the correct side; pullback into the
    EMA band; outside bar engulfing the prior body and breaking both extremes, closing with
    the trend; entry at that bar's close; stop beyond its opposite extreme; 50% off at 1R,
    stop to breakeven, then trail on swing structure.
    INVENTED 1: slope = both EMAs strictly monotonic over 5 bars.
    INVENTED 2: swing = confirmed 5-bar fractal pivot.
    INVENTED 3: no buffer beyond the bar extreme.
    INVENTED 4: the operational test for 'inside the zone' (spec amendment)."""
    e20, e50 = ema(df["close"], 20), ema(df["close"], 50)
    o, h, l, c = df["open"], df["high"], df["low"], df["close"]
    body_hi, body_lo = pd.concat([o, c], axis=1).max(axis=1), pd.concat([o, c], axis=1).min(axis=1)

    outside = (h > h.shift(1)) & (l < l.shift(1)) & \
              (body_hi >= body_hi.shift(1)) & (body_lo <= body_lo.shift(1))

    up_trend = (e20 > e50) & monotonic_run(e20, 5, True) & monotonic_run(e50, 5, True) & (c > e20)
    dn_trend = (e20 < e50) & monotonic_run(e20, 5, False) & monotonic_run(e50, 5, False) & (c < e20)

    in_zone_long = (l <= e20) & (h >= e50) & (c > e50)     # INVENTED 4
    in_zone_short = (h >= e20) & (l <= e50) & (c < e50)

    long_sig = up_trend & outside & (c > o) & in_zone_long
    short_sig = dn_trend & outside & (c < o) & in_zone_short

    swing_lo, swing_hi = fractal_pivots(df, 2, 2)

    s = _blank(df)
    s.loc[long_sig, "entry"] = 1
    s.loc[short_sig, "entry"] = -1
    s.loc[long_sig, "stop"] = l[long_sig]                  # INVENTED 3: exactly the extreme
    s.loc[short_sig, "stop"] = h[short_sig]
    s["trail"] = np.where(s["entry"].ffill().fillna(0) >= 0, swing_lo, swing_hi)
    return s, {"entry_on_close": True, "tiered_exit": True}


RUNS = {
    "s1_flat":    ("BTCUSDT_1D", lambda d: s1_macd(d, flip=False)),
    "s1_flip":    ("BTCUSDT_1D", lambda d: s1_macd(d, flip=True)),
    "s1_flat_4h": ("BTCUSDT_4h", lambda d: s1_macd(d, flip=False)),
    "s1_flip_4h": ("BTCUSDT_4h", lambda d: s1_macd(d, flip=True)),
    "s2_mid":     ("BTCUSDT_1D", lambda d: s2_donchian(d, mid_exit=True)),
    "s2_band":    ("BTCUSDT_1D", lambda d: s2_donchian(d, mid_exit=False)),
    "s3_atr":     ("BTCUSDT_1D", lambda d: s3_mfi(d, use_stop=True)),
    "s3_nostop":  ("BTCUSDT_1D", lambda d: s3_mfi(d, use_stop=False)),
    "s4":         ("BTCUSDT_1D", lambda d: s4_outside_bar(d)),
}
