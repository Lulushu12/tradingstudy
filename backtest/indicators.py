"""Causal indicator set.

Every value at index i is computed only from bars 0..i. Swing pivots are the one
place where naive implementations leak the future, so they carry an explicit
right-hand confirmation lag: a pivot at bar p is only *visible* from bar
p + PIVOT_RIGHT onward, and the arrays exposed here respect that.
"""

import numpy as np

PIVOT_LEFT = 3
PIVOT_RIGHT = 3


def ema(values, span):
    alpha = 2.0 / (span + 1.0)
    out = np.empty_like(values, dtype=float)
    out[0] = values[0]
    for i in range(1, len(values)):
        out[i] = alpha * values[i] + (1 - alpha) * out[i - 1]
    return out


def wilder_rma(values, period):
    """Wilder's smoothing (the running average used by ATR/RSI/ADX)."""
    out = np.full(len(values), np.nan, dtype=float)
    if len(values) < period:
        return out
    seed = np.mean(values[:period])
    out[period - 1] = seed
    prev = seed
    for i in range(period, len(values)):
        prev = (prev * (period - 1) + values[i]) / period
        out[i] = prev
    return out


def true_range(high, low, close):
    prev_close = np.roll(close, 1)
    prev_close[0] = close[0]
    a = high - low
    b = np.abs(high - prev_close)
    c = np.abs(low - prev_close)
    return np.maximum(a, np.maximum(b, c))


def atr(high, low, close, period=14):
    return wilder_rma(true_range(high, low, close), period)


def rsi(close, period=14):
    delta = np.diff(close, prepend=close[0])
    gain = np.where(delta > 0, delta, 0.0)
    loss = np.where(delta < 0, -delta, 0.0)
    avg_gain = wilder_rma(gain, period)
    avg_loss = wilder_rma(loss, period)
    with np.errstate(divide="ignore", invalid="ignore"):
        rs = avg_gain / avg_loss
        out = 100.0 - (100.0 / (1.0 + rs))
    # avg_loss == 0 means an unbroken run of gains -> RSI 100
    out = np.where((avg_loss == 0) & ~np.isnan(avg_gain), 100.0, out)
    return out


def adx(high, low, close, period=14):
    """Returns (adx, plus_di, minus_di)."""
    n = len(close)
    up = np.diff(high, prepend=high[0])
    dn = -np.diff(low, prepend=low[0])
    plus_dm = np.where((up > dn) & (up > 0), up, 0.0)
    minus_dm = np.where((dn > up) & (dn > 0), dn, 0.0)

    tr_rma = wilder_rma(true_range(high, low, close), period)
    plus_rma = wilder_rma(plus_dm, period)
    minus_rma = wilder_rma(minus_dm, period)

    with np.errstate(divide="ignore", invalid="ignore"):
        plus_di = 100.0 * plus_rma / tr_rma
        minus_di = 100.0 * minus_rma / tr_rma
        dx = 100.0 * np.abs(plus_di - minus_di) / (plus_di + minus_di)

    dx = np.nan_to_num(dx, nan=0.0, posinf=0.0, neginf=0.0)
    adx_out = np.full(n, np.nan)
    start = 2 * period - 1
    if n > start:
        seed = np.mean(dx[period : 2 * period])
        adx_out[start] = seed
        prev = seed
        for i in range(start + 1, n):
            prev = (prev * (period - 1) + dx[i]) / period
            adx_out[i] = prev
    return adx_out, plus_di, minus_di


def rolling_max(values, window):
    out = np.full(len(values), np.nan)
    for i in range(len(values)):
        lo = max(0, i - window + 1)
        out[i] = np.max(values[lo : i + 1])
    return out


def rolling_min(values, window):
    out = np.full(len(values), np.nan)
    for i in range(len(values)):
        lo = max(0, i - window + 1)
        out[i] = np.min(values[lo : i + 1])
    return out


def rolling_mean_std(values, window):
    mean = np.full(len(values), np.nan)
    std = np.full(len(values), np.nan)
    for i in range(len(values)):
        lo = max(0, i - window + 1)
        seg = values[lo : i + 1]
        mean[i] = seg.mean()
        std[i] = seg.std()
    return mean, std


def confirmed_swings(high, low):
    """Most recent *confirmed* swing high / swing low visible at each bar.

    A bar p is a swing high if its high exceeds the highs of PIVOT_LEFT bars
    before and PIVOT_RIGHT bars after. That verdict cannot be known until bar
    p + PIVOT_RIGHT, so the value is only propagated from that bar onward. This
    is the difference between an honest backtest and one that places stops using
    information that did not exist yet.
    """
    n = len(high)
    last_sh = np.full(n, np.nan)
    last_sl = np.full(n, np.nan)

    sh_price = np.nan
    sl_price = np.nan
    for i in range(n):
        # At bar i we can finally confirm the pivot candidate at bar i-PIVOT_RIGHT.
        p = i - PIVOT_RIGHT
        if p - PIVOT_LEFT >= 0:
            seg_hi = high[p - PIVOT_LEFT : p + PIVOT_RIGHT + 1]
            seg_lo = low[p - PIVOT_LEFT : p + PIVOT_RIGHT + 1]
            if high[p] == seg_hi.max() and np.argmax(seg_hi) == PIVOT_LEFT:
                sh_price = high[p]
            if low[p] == seg_lo.min() and np.argmin(seg_lo) == PIVOT_LEFT:
                sl_price = low[p]
        last_sh[i] = sh_price
        last_sl[i] = sl_price
    return last_sh, last_sl


def pivot_lists(high, low):
    """Every confirmed pivot as (confirm_idx, pivot_idx, price), ascending.

    confirm_idx is the first bar from which the pivot could have been known
    (pivot_idx + PIVOT_RIGHT). Callers must filter on confirm_idx <= i, never on
    pivot_idx <= i, or they are reading levels that had not formed yet.
    """
    n = len(high)
    highs, lows = [], []
    for p in range(PIVOT_LEFT, n - PIVOT_RIGHT):
        seg_hi = high[p - PIVOT_LEFT : p + PIVOT_RIGHT + 1]
        seg_lo = low[p - PIVOT_LEFT : p + PIVOT_RIGHT + 1]
        if high[p] == seg_hi.max() and np.argmax(seg_hi) == PIVOT_LEFT:
            highs.append((p + PIVOT_RIGHT, p, float(high[p])))
        if low[p] == seg_lo.min() and np.argmin(seg_lo) == PIVOT_LEFT:
            lows.append((p + PIVOT_RIGHT, p, float(low[p])))

    def pack(rows):
        if not rows:
            z = np.zeros(0)
            return {"confirm": z.astype(int), "pivot": z.astype(int), "price": z}
        c, p, px = zip(*rows)
        return {"confirm": np.array(c), "pivot": np.array(p), "price": np.array(px)}

    # confirm is ascending by construction, so searchsorted works directly.
    return {"highs": pack(highs), "lows": pack(lows)}


def percentile_rank(values, window):
    """Rank of the current value inside its trailing window, in [0, 1]."""
    out = np.full(len(values), np.nan)
    for i in range(len(values)):
        lo = max(0, i - window + 1)
        seg = values[lo : i + 1]
        seg = seg[~np.isnan(seg)]
        if len(seg) < 20 or np.isnan(values[i]):
            continue
        out[i] = float(np.sum(seg <= values[i])) / len(seg)
    return out


def build(open_, high, low, close, volume):
    """Compute the full causal feature set used by the strategy."""
    f = {}
    f["ema21"] = ema(close, 21)
    f["ema55"] = ema(close, 55)
    f["ema200"] = ema(close, 200)
    f["atr"] = atr(high, low, close, 14)
    f["rsi"] = rsi(close, 14)
    adx_v, pdi, mdi = adx(high, low, close, 14)
    f["adx"] = adx_v
    f["plus_di"] = pdi
    f["minus_di"] = mdi
    f["donch_hi"] = rolling_max(high, 48)
    f["donch_lo"] = rolling_min(low, 48)
    f["swing_hi"], f["swing_lo"] = confirmed_swings(high, low)

    vmean, vstd = rolling_mean_std(volume, 100)
    with np.errstate(divide="ignore", invalid="ignore"):
        f["vol_z"] = np.where(vstd > 0, (volume - vmean) / vstd, 0.0)

    atr_pct = f["atr"] / close
    f["atr_pct"] = atr_pct
    f["vol_regime"] = percentile_rank(atr_pct, 500)

    # Distance from the 21 EMA in ATR units - the "stretch" that mean reversion
    # setups key off.
    with np.errstate(divide="ignore", invalid="ignore"):
        f["stretch"] = (close - f["ema21"]) / f["atr"]

    # Slope of the 200 EMA over the last 24 bars, normalised by ATR: the
    # macro-trend gradient.
    slope = np.full(len(close), np.nan)
    e200 = f["ema200"]
    for i in range(24, len(close)):
        slope[i] = (e200[i] - e200[i - 24]) / f["atr"][i] if f["atr"][i] > 0 else 0.0
    f["ema200_slope"] = slope

    # Position inside the 48-bar Donchian channel, 0 = bottom, 1 = top.
    rng = f["donch_hi"] - f["donch_lo"]
    with np.errstate(divide="ignore", invalid="ignore"):
        f["donch_pos"] = np.where(rng > 0, (close - f["donch_lo"]) / rng, 0.5)

    return f
