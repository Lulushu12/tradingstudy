"""WaveTrend / MFI-clone oscillator suite and divergence stacks.

=============================================================================
SCOPE WARNING, READ BEFORE QUOTING ANY NUMBER FROM THIS FILE
=============================================================================
This is EXPLORATORY work inside the low R:R study. It is NOT the FROZEN_SPEC
audit and must never be presented as one.

  - The port is written from the formulas in FROZEN_SPEC.md. There is no
    PineScript in this repo to port line by line, and the port has NOT been
    validated against TradingView indicator values. Gate 0 of the audit
    requires that validation before any backtest is trusted. An unvalidated
    port produces fake results, so treat everything here as a direction
    indicator, not as evidence.
  - No holdout is touched, and nothing here may be used to select between
    Variant A and Variant B. That selection is committed to the locked
    holdout.
  - Only Variant A (standard stack) is implemented. Variant B (the front-run)
    depends on pre-div raw conditions whose exact coded form is not in this
    repo, and guessing at them would manufacture a system that was never
    specified. It is left out rather than approximated.
=============================================================================

Indicators per FROZEN_SPEC.md section 2:
  WaveTrend  channel 9, average 12, source hlc3, MA length 3, wt2 = SMA(wt1,3)
  MFI clone  EMA( SMA( (close-open)/stdev(close,7) * 150, 60 ) - 2.5, 4 )
  fractals   5-bar, a pivot at bar p is CONFIRMED at p+2
  levels     WT bull pivot wt2 <= -65 primary / <= -40 secondary
             WT bear pivot wt2 >= +45 primary / >= +15 secondary
             MFI bull pivot <= -2.5, MFI bear pivot >= +2.5
  stack      exactly one WT div + one MFI div, same direction, within 11 bars
             measured between fractal confirmation bars (Variant A)

Also tested here beyond the spec, clearly labelled:
  - WT+RSI and MFI+RSI stacks (other oscillator pairs)
  - single-oscillator divergences with no stack partner
  - the "any two same-direction divergences" variant, which FROZEN_SPEC calls a
    known bug, run ONLY as a labelled diagnostic and never as a candidate
"""
import sys, os, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd

# ------------------------------------------------------------------ indicators
def ema(s, n):
    return s.ewm(span=n, adjust=False).mean()

def sma(s, n):
    return s.rolling(n).mean()

def rma(s, n):
    return s.ewm(alpha=1 / n, adjust=False).mean()

def wavetrend_mcb(df, chlen=9, avg=12, malen=3):
    """MCB-style WaveTrend. Divergence logic runs on wt2 per the spec."""
    hlc3 = (df["high"] + df["low"] + df["close"]) / 3
    esa = ema(hlc3, chlen)
    de = ema((hlc3 - esa).abs(), chlen)
    ci = (hlc3 - esa) / (0.015 * de.replace(0, np.nan))
    wt1 = ema(ci, avg)
    wt2 = sma(wt1, malen)
    return wt1, wt2

def mfi_clone(df, period=60, mult=150.0, yoff=2.5, sdlen=7, smooth=4):
    """EMA( SMA( (close-open)/stdev(close,sdlen) * mult, period ) - yoff, smooth ).

    Pine's stdev is the population standard deviation, so ddof=0.
    """
    sd = df["close"].rolling(sdlen).std(ddof=0)
    raw = (df["close"] - df["open"]) / sd.replace(0, np.nan) * mult
    return ema(sma(raw, period) - yoff, smooth)

def atr_rma(df, n=14):
    h, l, c = df["high"], df["low"], df["close"]
    pc = c.shift(1)
    tr = pd.concat([(h - l), (h - pc).abs(), (l - pc).abs()], axis=1).max(axis=1)
    return rma(tr, n)

# -------------------------------------------------------------------- fractals
def fractals(df):
    """5-bar fractal. Pivot at bar p uses bars p-2..p+2 and CONFIRMS at p+2.

    Returns two int arrays of pivot bar indices (tops, bottoms). The caller is
    responsible for only using a pivot from bar p+2 onward, which is what makes
    this causal.
    """
    h = df["high"].values
    l = df["low"].values
    n = len(df)
    tops, bots = [], []
    for p in range(2, n - 2):
        w = h[p - 2:p + 3]
        if h[p] == w.max() and w.argmax() == 2:
            tops.append(p)
        w = l[p - 2:p + 3]
        if l[p] == w.min() and w.argmin() == 2:
            bots.append(p)
    return np.array(tops, dtype=int), np.array(bots, dtype=int)

# ---------------------------------------------------------------- divergences
def regular_divs(df, osc, tops, bots, lvl_bear=None, lvl_bull=None,
                 max_gap=100):
    """Regular divergences between CONSECUTIVE confirmed pivots.

    bull: price makes a lower pivot low, oscillator makes a higher low
    bear: price makes a higher pivot high, oscillator makes a lower high

    Level filter is applied at the CURRENT pivot, per the spec's
    "tested at the pivot" wording.

    Returns (bull_conf_bars, bear_conf_bars) as arrays of CONFIRMATION bar
    indices (pivot bar + 2), which is the earliest bar the signal can be acted
    on without look-ahead.
    """
    o = np.asarray(osc, dtype=float)
    lo = df["low"].values
    hi = df["high"].values
    bull, bear = [], []
    for k in range(1, len(bots)):
        p, q = bots[k], bots[k - 1]          # p current, q previous
        if p - q > max_gap:
            continue
        if not (np.isfinite(o[p]) and np.isfinite(o[q])):
            continue
        if lvl_bull is not None and not (o[p] <= lvl_bull):
            continue
        if lo[p] < lo[q] and o[p] > o[q]:
            bull.append(p + 2)
    for k in range(1, len(tops)):
        p, q = tops[k], tops[k - 1]
        if p - q > max_gap:
            continue
        if not (np.isfinite(o[p]) and np.isfinite(o[q])):
            continue
        if lvl_bear is not None and not (o[p] >= lvl_bear):
            continue
        if hi[p] > hi[q] and o[p] < o[q]:
            bear.append(p + 2)
    return np.array(bull, dtype=int), np.array(bear, dtype=int)

def stack(a_bars, b_bars, window=11, n=None):
    """Signal bars where a divergence from set A and one from set B land within
    `window` bars of each other. Gap 0 (same bar) is valid per the spec.

    The signal fires on the LATER of the two confirmation bars, which is the
    first bar at which both legs are known.
    """
    if len(a_bars) == 0 or len(b_bars) == 0:
        return np.array([], dtype=int)
    out = set()
    b_sorted = np.sort(b_bars)
    for x in a_bars:
        lo = np.searchsorted(b_sorted, x - window, side="left")
        hi = np.searchsorted(b_sorted, x + window, side="right")
        for y in b_sorted[lo:hi]:
            out.add(int(max(x, y)))
    return np.array(sorted(out), dtype=int)

# --------------------------------------------------------------- signal build
def build_osc(df):
    """Attach the oscillator suite to a frame that already has OHLC."""
    df = df.copy()
    wt1, wt2 = wavetrend_mcb(df)
    df["wt1"], df["wt2"] = wt1, wt2
    df["mfic"] = mfi_clone(df)
    d = df["close"].diff()
    up = d.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
    df["rsi14"] = 100 - 100 / (1 + up / dn)
    df["atr14"] = atr_rma(df, 14)
    return df

def spec_stop(df, side_arr, sig_bars, atr_mult=1.0, lookback=5):
    """FROZEN_SPEC section 5 stop.

    short: highest (close + 1*ATR14) over bars t-5..t-1, signal bar EXCLUDED
    long:  lowest  (close - 1*ATR14) over the same window
    Returns stop DISTANCE in price from the entry (next bar open).
    """
    c = df["close"].values
    a = df["atr14"].values
    o = df["open"].values
    up_band = c + atr_mult * a
    dn_band = c - atr_mult * a
    dist = np.full(len(sig_bars), np.nan)
    for i, t in enumerate(sig_bars):
        lo = max(0, t - lookback)
        if lo >= t:
            continue
        entry = o[t + 1] if t + 1 < len(o) else np.nan
        if not np.isfinite(entry):
            continue
        if side_arr[i] < 0:
            lvl = np.nanmax(up_band[lo:t])
            dist[i] = lvl - entry
        else:
            lvl = np.nanmin(dn_band[lo:t])
            dist[i] = entry - lvl
    return dist

def signal_sets(df, level_mode="primary", window=11, max_gap=100):
    """Every divergence-stack variant, as arrays of signal bars per direction."""
    if level_mode == "primary":
        wt_bull, wt_bear = -65.0, 45.0
    elif level_mode == "secondary":
        wt_bull, wt_bear = -40.0, 15.0
    else:
        wt_bull, wt_bear = None, None
    mfi_bull, mfi_bear = (-2.5, 2.5) if level_mode != "none" else (None, None)

    tops, bots = fractals(df)
    wtb, wtr = regular_divs(df, df["wt2"].values, tops, bots,
                            lvl_bear=wt_bear, lvl_bull=wt_bull, max_gap=max_gap)
    mfb, mfr = regular_divs(df, df["mfic"].values, tops, bots,
                            lvl_bear=mfi_bear, lvl_bull=mfi_bull, max_gap=max_gap)
    rsb, rsr = regular_divs(df, df["rsi14"].values, tops, bots,
                            lvl_bear=None, lvl_bull=None, max_gap=max_gap)
    s = {}
    s["WT+MFI"] = (stack(wtb, mfb, window), stack(wtr, mfr, window))
    s["WT+RSI"] = (stack(wtb, rsb, window), stack(wtr, rsr, window))
    s["MFI+RSI"] = (stack(mfb, rsb, window), stack(mfr, rsr, window))
    s["WT_only"] = (wtb, wtr)
    s["MFI_only"] = (mfb, mfr)
    s["RSI_only"] = (rsb, rsr)
    # DIAGNOSTIC ONLY: the spec calls this a known bug. Never a candidate.
    anyb = np.unique(np.concatenate([wtb, mfb])) if len(wtb) + len(mfb) else np.array([], int)
    anyr = np.unique(np.concatenate([wtr, mfr])) if len(wtr) + len(mfr) else np.array([], int)
    s["DIAG_any_two"] = (stack(anyb, anyb, window), stack(anyr, anyr, window))
    return s
