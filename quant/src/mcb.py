"""MCB Clone v1: WaveTrend + MFI clone, fractals, regular divergences.

Ported from FROZEN_SPEC.md sections 2-3. Used here NOT as a standalone system
(the original audit never validated it) but as a lower-timeframe precision
TRIGGER: the higher timeframe decides direction, this decides the moment.

  WaveTrend  channel 9, average 12, source hlc3, signal SMA 3.
             All divergence logic runs on wt2, per spec.
  MFI clone  EMA( SMA( (close-open)/stdev(close,7) * 150, 60 ) - 2.5, 4 )
  Fractals   5-bar. A pivot at bar p is CONFIRMED at p+2, so it may not be
             acted on before then. Enforced by construction here.
  Divergence Regular only. Hidden divergences are excluded, per spec.
  Levels     WT bull pivot wt2 <= -65 primary / <= -40 secondary
             WT bear pivot wt2 >= 45 primary / >= 15 secondary
             MFI bull <= -2.5, MFI bear >= 2.5

Everything returns values indexed to the bar at which the information became
usable, not the bar the pivot occurred on. That two-bar lag is the whole reason
divergence systems look better in hindsight than they trade.
"""
import numpy as np
import pandas as pd


# --------------------------------------------------------------- oscillators
def wavetrend(df, n1=9, n2=12, sig=3):
    ap = (df["high"] + df["low"] + df["close"]) / 3.0
    esa = ap.ewm(span=n1, adjust=False).mean()
    d = (ap - esa).abs().ewm(span=n1, adjust=False).mean()
    ci = (ap - esa) / (0.015 * d.replace(0, np.nan))
    wt1 = ci.ewm(span=n2, adjust=False).mean()
    wt2 = wt1.rolling(sig).mean()
    return wt1, wt2


def mfi_clone(df, period=60, mult=150.0, y_off=2.5, stdev_len=7, smooth=4):
    sd = df["close"].rolling(stdev_len).std(ddof=0)
    raw = (df["close"] - df["open"]) / sd.replace(0, np.nan) * mult
    return (raw.rolling(period).mean() - y_off).ewm(span=smooth, adjust=False).mean()


def atr_rma(df, n=14):
    tr = pd.concat([df["high"] - df["low"],
                    (df["high"] - df["close"].shift()).abs(),
                    (df["low"] - df["close"].shift()).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


# ------------------------------------------------------------------- fractals
def fractals(series):
    """5-bar fractal. Returns two boolean arrays flagged at the CONFIRMATION
    bar (p+2), not the pivot bar, plus the pivot index each confirmation refers
    to."""
    v = np.asarray(series, float)
    n = len(v)
    top = np.zeros(n, bool)
    bot = np.zeros(n, bool)
    pidx = np.full(n, -1, np.int64)
    for p in range(2, n - 2):
        w = v[p - 2:p + 3]
        if np.isnan(w).any():
            continue
        c = v[p]
        if c == w.max() and (w[:2] < c).all() and (w[3:] < c).all():
            top[p + 2] = True
            pidx[p + 2] = p
        if c == w.min() and (w[:2] > c).all() and (w[3:] > c).all():
            bot[p + 2] = True
            pidx[p + 2] = p
    return top, bot, pidx


# ---------------------------------------------------------------- divergences
def regular_divergences(df, osc, kind, lvl_primary, lvl_secondary,
                        max_gap=60):
    """Regular divergence on `osc`, flagged at the confirmation bar.

    kind='bull': price lower low, oscillator higher low, pivot below level.
    kind='bear': price higher high, oscillator lower high, pivot above level.

    Compares each newly confirmed pivot against the previous confirmed pivot of
    the same type, which is exactly what the coded valuewhen chain does.
    """
    top, bot, pidx = fractals(osc)
    o = np.asarray(osc, float)
    hi = df["high"].to_numpy(float)
    lo = df["low"].to_numpy(float)
    n = len(o)
    out = np.zeros(n, bool)
    strength = np.zeros(n)
    level = np.full(n, np.nan)      # price of the pivot that formed the div

    conf = bot if kind == "bull" else top
    prev_p = -1
    for i in range(n):
        if not conf[i]:
            continue
        p = pidx[i]
        if prev_p >= 0 and (p - prev_p) <= max_gap:
            if kind == "bull":
                price_ll = lo[p] < lo[prev_p]
                osc_hl = o[p] > o[prev_p]
                lvl_ok = o[p] <= lvl_secondary
                if price_ll and osc_hl and lvl_ok:
                    out[i] = True
                    strength[i] = 2.0 if o[p] <= lvl_primary else 1.0
                    level[i] = lo[p]
            else:
                price_hh = hi[p] > hi[prev_p]
                osc_lh = o[p] < o[prev_p]
                lvl_ok = o[p] >= lvl_secondary
                if price_hh and osc_lh and lvl_ok:
                    out[i] = True
                    strength[i] = 2.0 if o[p] >= lvl_primary else 1.0
                    level[i] = hi[p]
        prev_p = p
    return out, strength, level


def build(df):
    """Full MCB state for a bar frame. All columns usable at that bar's close."""
    wt1, wt2 = wavetrend(df)
    mfi = mfi_clone(df)
    atr = atr_rma(df)
    f = pd.DataFrame(index=df.index)
    f["wt1"], f["wt2"], f["mfi"], f["atr"] = wt1, wt2, mfi, atr

    wt_bull, wt_bull_s, wt_bull_lvl = regular_divergences(df, wt2, "bull", -65, -40)
    wt_bear, wt_bear_s, wt_bear_lvl = regular_divergences(df, wt2, "bear", 45, 15)
    mfi_bull, _, mfi_bull_lvl = regular_divergences(df, mfi, "bull", -2.5, -2.5)
    mfi_bear, _, mfi_bear_lvl = regular_divergences(df, mfi, "bear", 2.5, 2.5)
    f["div_bull_level"] = np.where(np.isfinite(wt_bull_lvl), wt_bull_lvl, mfi_bull_lvl)
    f["div_bear_level"] = np.where(np.isfinite(wt_bear_lvl), wt_bear_lvl, mfi_bear_lvl)
    f["wt_div_bull"] = wt_bull
    f["wt_div_bear"] = wt_bear
    f["mfi_div_bull"] = mfi_bull
    f["mfi_div_bear"] = mfi_bear
    f["div_bull_strength"] = wt_bull_s
    f["div_bear_strength"] = wt_bear_s

    # stack per spec section 4: exactly one WT div plus one MFI div, same
    # direction, within an 11-bar window. WT+WT and MFI+MFI are invalid.
    for d, tag in ((("wt_div_bull", "mfi_div_bull"), "bull"),
                   (("wt_div_bear", "mfi_div_bear"), "bear")):
        a = f[d[0]].rolling(11, min_periods=1).max().astype(bool)
        b = f[d[1]].rolling(11, min_periods=1).max().astype(bool)
        f[f"stack_{tag}"] = (a & b) & (f[d[0]] | f[d[1]])

    # trigger-wave cross: wt1 crossing wt2, the classic MCB entry cue
    cross_up = (wt1 > wt2) & (wt1.shift() <= wt2.shift())
    cross_dn = (wt1 < wt2) & (wt1.shift() >= wt2.shift())
    f["wt_cross_up"] = cross_up
    f["wt_cross_dn"] = cross_dn
    f["wt_cross_up_os"] = cross_up & (wt2 <= -40)
    f["wt_cross_dn_ob"] = cross_dn & (wt2 >= 45)
    return f


def trigger(f, side, mode="stack"):
    """Boolean trigger series for a given side and trigger definition."""
    if mode == "stack":
        return f["stack_bull"] if side > 0 else f["stack_bear"]
    if mode == "div":
        return ((f["wt_div_bull"] | f["mfi_div_bull"]) if side > 0
                else (f["wt_div_bear"] | f["mfi_div_bear"]))
    if mode == "cross":
        return f["wt_cross_up"] if side > 0 else f["wt_cross_dn"]
    if mode == "cross_ext":
        return f["wt_cross_up_os"] if side > 0 else f["wt_cross_dn_ob"]
    raise ValueError(mode)
