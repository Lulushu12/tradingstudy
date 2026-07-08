"""Line-by-line Python port of MCB Clone v1 (MCB_Clone_v1.pine).

Scope: only the components FROZEN_SPEC.md declares part of the system:
WaveTrend, MFI clone, fractals, regular divergences with level filters,
pre-div raw conditions, ATR14 RMA. RSI/StochRSI/gold dots/buy-sell dots are
excluded per spec section 2.

Pine semantics reproduced:
- ta.ema:   alpha = 2/(n+1), recursive, seeded with the first source value.
            Warm-up differs from TradingView (which had pre-series history),
            so validation must skip a burn-in prefix.
- ta.sma:   plain rolling mean, NaN until n values.
- ta.stdev: population stdev (biased = true, Pine default).
- ta.rma:   alpha = 1/n, seeded with SMA(n) per Pine docs (used for ATR).
- ta.valuewhen(cond, src, 0): value of src at the most recent bar where cond
            was true, including the current bar.
- Fractals: f_top_fractal/f_bot_fractal, strict comparisons, pivot at bar
            t-2 confirmed at bar t (2-bar lag).

All series are computed causally: values at bar t use bars <= t only.
"""
from dataclasses import dataclass, field

import numpy as np


# ── Pine building blocks ─────────────────────────────────────────────────────

def pine_ema(x: np.ndarray, n: int) -> np.ndarray:
    alpha = 2.0 / (n + 1.0)
    out = np.full(len(x), np.nan)
    prev = np.nan
    for i, v in enumerate(x):
        if np.isnan(v):
            out[i] = prev
            continue
        prev = v if np.isnan(prev) else alpha * v + (1 - alpha) * prev
        out[i] = prev
    return out


def pine_sma(x: np.ndarray, n: int) -> np.ndarray:
    """Rolling mean; NaN whenever the window contains any NaN (matches Pine,
    where ta.sma is na until `n` non-na values exist)."""
    out = np.full(len(x), np.nan)
    csum = np.cumsum(np.nan_to_num(x))
    out[n - 1:] = (csum[n - 1:] - np.concatenate(([0.0], csum[:-n]))) / n
    bad = np.isnan(x).astype(np.int64).cumsum()
    nan_in_win = np.zeros(len(x), dtype=bool)
    nan_in_win[n - 1:] = (bad[n - 1:] - np.concatenate(([0], bad[:-n]))) > 0
    out[nan_in_win] = np.nan
    return out


def pine_stdev(x: np.ndarray, n: int) -> np.ndarray:
    """Population stdev, matching Pine ta.stdev default (biased = true)."""
    out = np.full(len(x), np.nan)
    for i in range(n - 1, len(x)):
        out[i] = np.std(x[i - n + 1:i + 1])
    return out


def pine_rma(x: np.ndarray, n: int) -> np.ndarray:
    """Wilder smoothing, seeded with SMA(n) per Pine ta.rma docs."""
    out = np.full(len(x), np.nan)
    alpha = 1.0 / n
    prev = np.nan
    count = 0
    acc = 0.0
    for i, v in enumerate(x):
        if np.isnan(v):
            continue
        if np.isnan(prev):
            acc += v
            count += 1
            if count == n:
                prev = acc / n
                out[i] = prev
            continue
        prev = alpha * v + (1 - alpha) * prev
        out[i] = prev
    return out


# ── Indicators ───────────────────────────────────────────────────────────────

def wavetrend(high, low, close, chlen=9, avg=12, malen=3):
    """f_wavetrend with source hlc3, single timeframe (request.security is
    identity when tf equals the chart timeframe)."""
    tfsrc = (high + low + close) / 3.0
    esa = pine_ema(tfsrc, chlen)
    de = pine_ema(np.abs(tfsrc - esa), chlen)
    ci = (tfsrc - esa) / (0.015 * de)
    wt1 = pine_ema(ci, avg)
    wt2 = pine_sma(wt1, malen)
    return wt1, wt2


def mfi_clone(open_, close, period=60, mult=150.0, pos_y=2.5, stdev_len=7, smooth=4):
    """f_mfi: EMA(SMA((close-open)/stdev(close,stdevLen)*mult, period) - posY, smooth)."""
    raw = (close - open_) / pine_stdev(close, stdev_len) * mult
    return pine_ema(pine_sma(raw, period) - pos_y, smooth)


def atr_rma(high, low, close, n=14):
    prev_close = np.concatenate(([np.nan], close[:-1]))
    tr = np.maximum(high - low,
                    np.maximum(np.abs(high - prev_close), np.abs(low - prev_close)))
    tr[0] = high[0] - low[0]
    return pine_rma(tr, n)


# ── Fractals ─────────────────────────────────────────────────────────────────

def top_fractal(src: np.ndarray) -> np.ndarray:
    """True at bar t when the pivot at t-2 is a top: src[4]<src[2] and
    src[3]<src[2] and src[2]>src[1] and src[2]>src[0] (Pine indexing,
    src[0] = current bar)."""
    out = np.zeros(len(src), dtype=bool)
    s = src
    out[4:] = ((s[:-4] < s[2:-2]) & (s[1:-3] < s[2:-2])
               & (s[2:-2] > s[3:-1]) & (s[2:-2] > s[4:]))
    return out & ~np.isnan(src)


def bot_fractal(src: np.ndarray) -> np.ndarray:
    out = np.zeros(len(src), dtype=bool)
    s = src
    out[4:] = ((s[:-4] > s[2:-2]) & (s[1:-3] > s[2:-2])
               & (s[2:-2] < s[3:-1]) & (s[2:-2] < s[4:]))
    return out & ~np.isnan(src)


# ── Divergences (f_findDivs / f_findDivs_mfi are identical in the source) ────

@dataclass
class DivChain:
    """Per-bar output of one f_findDivs call (one oscillator, one level pair)."""
    is_top: np.ndarray
    is_bot: np.ndarray
    bear_div: np.ndarray
    bull_div: np.ndarray
    # reference (previous pivot) identity for every div event, NaN/-1 elsewhere
    bear_ref_bar: np.ndarray
    bull_ref_bar: np.ndarray


def find_divs(osc: np.ndarray, high: np.ndarray, low: np.ndarray,
              top_limit: float, bot_limit: float) -> DivChain:
    """Port of f_findDivs(src, topLimit, botLimit, true), regular divs only.

    Evaluated at confirmation bar t (pivot at t-2):
      isTop      = fractal and osc[t-2] >= topLimit
      highPrev   = osc pivot value at the most recent isTop bar as of t-2
      highPrice  = high at that pivot bar
      bearSignal = isTop and high[t-2] > highPrice and osc[t-2] < highPrev
    The [2] offset on the valuewhen chain means the reference is always the
    PREVIOUS pivot in the same filtered chain, never the current one.
    """
    n = len(osc)
    is_top = top_fractal(osc)
    is_bot = bot_fractal(osc)
    with np.errstate(invalid="ignore"):
        osc_p = np.concatenate(([np.nan, np.nan], osc[:-2]))          # osc[2]
        is_top &= osc_p >= top_limit
        is_bot &= osc_p <= bot_limit

    bear = np.zeros(n, dtype=bool)
    bull = np.zeros(n, dtype=bool)
    bear_ref = np.full(n, -1, dtype=np.int64)
    bull_ref = np.full(n, -1, dtype=np.int64)

    # walk forward maintaining valuewhen state as of 2 bars ago
    last_top = -1   # most recent isTop bar index
    last_bot = -1
    hist_top = []   # all isTop bar indices, to query "as of t-2"
    hist_bot = []
    for t in range(n):
        # state "as of bar t-2": most recent event bar <= t-2
        def as_of(hist, cutoff):
            for b in reversed(hist):
                if b <= cutoff:
                    return b
            return -1
        if is_top[t]:
            ref = as_of(hist_top, t - 2)
            if ref >= 0:
                ref_pivot = ref - 2
                cur_pivot = t - 2
                if high[cur_pivot] > high[ref_pivot] and osc[cur_pivot] < osc[ref_pivot]:
                    bear[t] = True
                    bear_ref[t] = ref_pivot
            hist_top.append(t)
        if is_bot[t]:
            ref = as_of(hist_bot, t - 2)
            if ref >= 0:
                ref_pivot = ref - 2
                cur_pivot = t - 2
                if low[cur_pivot] < low[ref_pivot] and osc[cur_pivot] > osc[ref_pivot]:
                    bull[t] = True
                    bull_ref[t] = ref_pivot
            hist_bot.append(t)
    return DivChain(is_top, is_bot, bear, bull, bear_ref, bull_ref)


# ── Pre-divergence raw conditions ────────────────────────────────────────────

@dataclass
class PreDiv:
    """Per-bar pre-div raw conditions plus reference identity."""
    pre_bull: np.ndarray
    pre_bear: np.ndarray
    bull_ref_bar: np.ndarray   # confirmation bar of the reference bot pivot
    bear_ref_bar: np.ndarray


def prediv_raw(osc: np.ndarray, high: np.ndarray, low: np.ndarray,
               is_top: np.ndarray, is_bot: np.ndarray,
               max_age: int, swing_buf: int,
               os_filter: float, ob_filter: float) -> PreDiv:
    """Port of the preBull/preBear *_raw logic.

    At bar t:
      refBot*   = valuewhen(isBot, ., 0): most recent isBot bar u <= t
                  (the CURRENT bar counts, no [2] shift here).
      refBotWT2 = osc[u-2]  (pivot value)
      refBotLow = min(low[u-6 .. u-2])  (lowest(low, swing_buf)[2] at u)
      preBull   = (t - u) <= max_age and low[t] < refBotLow
                  and osc[t] > refBotWT2 and osc[t] < os_filter
    max_age is measured against the CONFIRMATION bar u (bar_index - refBotBar
    in the source), not the pivot bar.
    """
    n = len(osc)
    pre_bull = np.zeros(n, dtype=bool)
    pre_bear = np.zeros(n, dtype=bool)
    bull_ref = np.full(n, -1, dtype=np.int64)
    bear_ref = np.full(n, -1, dtype=np.int64)

    last_bot = -1
    last_top = -1
    for t in range(n):
        if is_bot[t]:
            last_bot = t
        if is_top[t]:
            last_top = t
        if last_bot >= 0 and (t - last_bot) <= max_age:
            u = last_bot
            pivot = u - 2
            ref_low = low[max(0, pivot - swing_buf + 1):pivot + 1].min()
            if (low[t] < ref_low and osc[t] > osc[pivot] and osc[t] < os_filter):
                pre_bull[t] = True
                bull_ref[t] = u
        if last_top >= 0 and (t - last_top) <= max_age:
            u = last_top
            pivot = u - 2
            ref_high = high[max(0, pivot - swing_buf + 1):pivot + 1].max()
            if (high[t] > ref_high and osc[t] < osc[pivot] and osc[t] > ob_filter):
                pre_bear[t] = True
                bear_ref[t] = u
        # NOTE: Pine evaluates valuewhen on the current bar BEFORE the rest of
        # the expression, so a bar where is_bot fires can reference itself.
        # That is reproduced here because last_bot/last_top update first.
    return PreDiv(pre_bull, pre_bear, bull_ref, bear_ref)
