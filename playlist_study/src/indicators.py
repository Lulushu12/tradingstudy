"""
Indicator library for the playlist strategies.

Everything here is causal: the value at bar t uses only bars up to and including
t. Anything that needs future bars to be known (swing pivots, fair value gap
confirmation) returns the value on the bar where it becomes KNOWABLE, not the
bar it refers to, and says so in its docstring. Getting this wrong is the single
most common way a video strategy backtests beautifully and loses money live.
"""

import numpy as np
import pandas as pd


# ---------------------------------------------------------------- moving averages

def sma(s, n):
    return s.rolling(n, min_periods=n).mean()


def ema(s, n):
    return s.ewm(span=n, adjust=False, min_periods=n).mean()


def rma(s, n):
    """Wilder smoothing, as used inside RSI and ATR."""
    return s.ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean()


def wma(s, n):
    w = np.arange(1, n + 1, dtype=float)
    return s.rolling(n, min_periods=n).apply(lambda x: np.dot(x, w) / w.sum(), raw=True)


def hma(s, n):
    half = wma(s, max(1, n // 2))
    full = wma(s, n)
    return wma(2 * half - full, max(1, int(np.sqrt(n))))


# ---------------------------------------------------------------- oscillators

def rsi(close, n=14):
    d = close.diff()
    gain = rma(d.clip(lower=0), n)
    loss = rma((-d).clip(lower=0), n)
    rs = gain / loss.replace(0, np.nan)
    out = 100 - 100 / (1 + rs)
    return out.fillna(100 * (gain > 0))


def stoch_rsi(close, n=14, k=3, d=3):
    r = rsi(close, n)
    lo = r.rolling(n, min_periods=n).min()
    hi = r.rolling(n, min_periods=n).max()
    raw = 100 * (r - lo) / (hi - lo).replace(0, np.nan)
    kk = raw.rolling(k, min_periods=k).mean()
    return kk, kk.rolling(d, min_periods=d).mean()


def stochastic(high, low, close, n=14, k=3, d=3):
    lo = low.rolling(n, min_periods=n).min()
    hi = high.rolling(n, min_periods=n).max()
    raw = 100 * (close - lo) / (hi - lo).replace(0, np.nan)
    kk = raw.rolling(k, min_periods=k).mean()
    return kk, kk.rolling(d, min_periods=d).mean()


def macd(close, fast=12, slow=26, signal=9):
    line = ema(close, fast) - ema(close, slow)
    sig = ema(line, signal)
    return line, sig, line - sig


def cci(high, low, close, n=20):
    tp = (high + low + close) / 3
    ma = sma(tp, n)
    md = (tp - ma).abs().rolling(n, min_periods=n).mean()
    return (tp - ma) / (0.015 * md.replace(0, np.nan))


def mfi(high, low, close, volume, n=14):
    """Classic Money Flow Index. Requires real volume."""
    tp = (high + low + close) / 3
    raw = tp * volume
    up = raw.where(tp > tp.shift(1), 0.0)
    dn = raw.where(tp < tp.shift(1), 0.0)
    pos = up.rolling(n, min_periods=n).sum()
    neg = dn.rolling(n, min_periods=n).sum()
    return 100 - 100 / (1 + pos / neg.replace(0, np.nan))


# ---------------------------------------------------------------- volatility

def true_range(high, low, close):
    pc = close.shift(1)
    return pd.concat([high - low, (high - pc).abs(), (low - pc).abs()], axis=1).max(axis=1)


def atr(high, low, close, n=14):
    return rma(true_range(high, low, close), n)


def bollinger(close, n=20, k=2.0):
    mid = sma(close, n)
    sd = close.rolling(n, min_periods=n).std(ddof=0)
    return mid - k * sd, mid, mid + k * sd


def keltner(high, low, close, n=20, k=1.5):
    mid = ema(close, n)
    a = atr(high, low, close, n)
    return mid - k * a, mid, mid + k * a


def supertrend(high, low, close, n=10, mult=3.0):
    """Returns (trend_direction, trend_line). Direction is +1 long, -1 short."""
    a = atr(high, low, close, n)
    hl2 = (high + low) / 2
    upper = (hl2 + mult * a).to_numpy()
    lower = (hl2 - mult * a).to_numpy()
    c = close.to_numpy()

    fu = np.full(len(c), np.nan)
    fl = np.full(len(c), np.nan)
    dirn = np.ones(len(c), dtype=int)
    for i in range(1, len(c)):
        if np.isnan(upper[i]):
            continue
        fu[i] = upper[i] if (np.isnan(fu[i - 1]) or upper[i] < fu[i - 1] or c[i - 1] > fu[i - 1]) else fu[i - 1]
        fl[i] = lower[i] if (np.isnan(fl[i - 1]) or lower[i] > fl[i - 1] or c[i - 1] < fl[i - 1]) else fl[i - 1]
        if c[i] > fu[i]:
            dirn[i] = 1
        elif c[i] < fl[i]:
            dirn[i] = -1
        else:
            dirn[i] = dirn[i - 1]
    line = np.where(dirn == 1, fl, fu)
    return pd.Series(dirn, index=close.index), pd.Series(line, index=close.index)


def adx(high, low, close, n=14):
    up = high.diff()
    dn = -low.diff()
    plus = ((up > dn) & (up > 0)) * up
    minus = ((dn > up) & (dn > 0)) * dn
    tr = rma(true_range(high, low, close), n)
    pdi = 100 * rma(plus, n) / tr.replace(0, np.nan)
    mdi = 100 * rma(minus, n) / tr.replace(0, np.nan)
    dx = 100 * (pdi - mdi).abs() / (pdi + mdi).replace(0, np.nan)
    return rma(dx, n), pdi, mdi


# ---------------------------------------------------------------- volume

def vwap_session(df, freq="D"):
    """Session anchored VWAP, reset each period. Needs real volume."""
    tp = (df["high"] + df["low"] + df["close"]) / 3
    g = df.index.to_period(freq)
    pv = (tp * df["volume"]).groupby(g).cumsum()
    v = df["volume"].groupby(g).cumsum()
    return pv / v.replace(0, np.nan)


def rolling_vwap(df, n=20):
    tp = (df["high"] + df["low"] + df["close"]) / 3
    pv = (tp * df["volume"]).rolling(n, min_periods=n).sum()
    v = df["volume"].rolling(n, min_periods=n).sum()
    return pv / v.replace(0, np.nan)


def relative_volume(volume, n=20):
    return volume / sma(volume, n)


# ---------------------------------------------------------------- structure

def pivots(high, low, left=2, right=2):
    """Fractal swing points.

    Returns (pivot_high, pivot_low): each is a Series holding the pivot PRICE on
    the bar the pivot is CONFIRMED, which is `right` bars after the extreme
    itself. Reading them on the extreme's own bar would be look-ahead.
    """
    n = len(high)
    h = high.to_numpy()
    l = low.to_numpy()
    ph = np.full(n, np.nan)
    pl = np.full(n, np.nan)
    for i in range(left, n - right):
        w = h[i - left:i + right + 1]
        if h[i] == w.max() and (w == h[i]).sum() == 1:
            ph[i + right] = h[i]
        w = l[i - left:i + right + 1]
        if l[i] == w.min() and (w == l[i]).sum() == 1:
            pl[i + right] = l[i]
    return pd.Series(ph, index=high.index), pd.Series(pl, index=low.index)


def last_pivot_levels(high, low, left=2, right=2):
    """Most recent confirmed swing high / swing low price, forward filled.

    Safe to read on any bar: the value present at bar t was confirmed at or
    before t.
    """
    ph, pl = pivots(high, low, left, right)
    return ph.ffill(), pl.ffill()


def fair_value_gaps(df, min_size_pct=0.0):
    """Three bar imbalance (ICT style fair value gap).

    A bullish FVG exists when low[t] > high[t-2]; bearish when high[t] < low[t-2].
    The gap is only knowable at bar t, so both edges are reported on bar t.
    Returns a frame with bull/bear flags and the gap edges.
    """
    hi2 = df["high"].shift(2)
    lo2 = df["low"].shift(2)
    bull = df["low"] > hi2
    bear = df["high"] < lo2
    bull_sz = (df["low"] - hi2) / df["close"] * 100
    bear_sz = (lo2 - df["high"]) / df["close"] * 100
    if min_size_pct > 0:
        bull &= bull_sz >= min_size_pct
        bear &= bear_sz >= min_size_pct
    return pd.DataFrame(
        {
            "bull_fvg": bull.fillna(False),
            "bear_fvg": bear.fillna(False),
            "bull_bottom": hi2.where(bull),
            "bull_top": df["low"].where(bull),
            "bear_bottom": df["high"].where(bear),
            "bear_top": lo2.where(bear),
            "bull_size_pct": bull_sz.where(bull),
            "bear_size_pct": bear_sz.where(bear),
        },
        index=df.index,
    )


def swing_structure(high, low, left=2, right=2):
    """Break of structure / change of character, evaluated causally.

    Emits +1 on a bar that closes through the most recent confirmed swing high,
    -1 on a bar breaking the most recent confirmed swing low, 0 otherwise.
    """
    ph, pl = last_pivot_levels(high, low, left, right)
    up = (high > ph.shift(1)) & ph.shift(1).notna()
    dn = (low < pl.shift(1)) & pl.shift(1).notna()
    return (up.astype(int) - dn.astype(int)).rename("bos")


def donchian(high, low, n=20):
    return low.rolling(n, min_periods=n).min(), high.rolling(n, min_periods=n).max()


def fib_levels(swing_low, swing_high, ratios=(0.236, 0.382, 0.5, 0.618, 0.705, 0.786)):
    """Retracement prices for a low->high leg. Works elementwise on Series."""
    rng = swing_high - swing_low
    return {r: swing_high - rng * r for r in ratios}


def zigzag(df, left=3, right=3, min_pct=0.0):
    """Alternating confirmed swing legs, the closest mechanical stand-in for
    the "find a large trend" instruction that price action videos open with.

    Returns a list of dicts, each an impulse leg:
        start_i / end_i   integer bar positions of the leg's two extremes
        confirm_i         bar position where the leg became KNOWN (end_i + right)
        direction         +1 for a low->high leg, -1 for a high->low leg
        start_px / end_px the two extreme prices
        size_pct          leg size as a percent of the starting price

    A leg is only usable from confirm_i onward. Any strategy that anchors a
    Fibonacci to a leg must not act before that bar, otherwise it is drawing the
    tool with knowledge of where the swing ended.
    """
    ph, pl = pivots(df["high"], df["low"], left, right)
    events = []
    for i, v in enumerate(ph.to_numpy()):
        if not np.isnan(v):
            events.append((i, i - right, v, 1))
    for i, v in enumerate(pl.to_numpy()):
        if not np.isnan(v):
            events.append((i, i - right, v, -1))
    events.sort(key=lambda e: (e[1], e[0]))

    # collapse consecutive same-type pivots, keeping the more extreme one
    chain = []
    for conf_i, ext_i, px, kind in events:
        if chain and chain[-1][3] == kind:
            better = px > chain[-1][2] if kind == 1 else px < chain[-1][2]
            if better:
                chain[-1] = (conf_i, ext_i, px, kind)
            continue
        chain.append((conf_i, ext_i, px, kind))

    legs = []
    for (c0, i0, p0, k0), (c1, i1, p1, k1) in zip(chain, chain[1:]):
        direction = 1 if k1 == 1 else -1
        size = abs(p1 - p0) / p0 * 100
        if size < min_pct:
            continue
        legs.append({
            "start_i": i0, "end_i": i1, "confirm_i": c1,
            "direction": direction, "start_px": p0, "end_px": p1,
            "size_pct": size,
        })
    return legs


# ---------------------------------------------------------------- candlesticks

def candle_stats(df):
    body = (df["close"] - df["open"]).abs()
    rng = (df["high"] - df["low"]).replace(0, np.nan)
    upper = df["high"] - df[["open", "close"]].max(axis=1)
    lower = df[["open", "close"]].min(axis=1) - df["low"]
    return pd.DataFrame(
        {
            "body": body,
            "range": rng,
            "body_pct": body / rng,
            "upper_wick": upper,
            "lower_wick": lower,
            "upper_pct": upper / rng,
            "lower_pct": lower / rng,
            "bull": df["close"] > df["open"],
            "bear": df["close"] < df["open"],
        },
        index=df.index,
    )


def hammer(df, body_max=0.34, lower_min=0.5, upper_max=0.15):
    c = candle_stats(df)
    return (c["body_pct"] <= body_max) & (c["lower_pct"] >= lower_min) & (c["upper_pct"] <= upper_max)


def shooting_star(df, body_max=0.34, upper_min=0.5, lower_max=0.15):
    c = candle_stats(df)
    return (c["body_pct"] <= body_max) & (c["upper_pct"] >= upper_min) & (c["lower_pct"] <= lower_max)


def engulfing(df):
    """Returns +1 bullish engulfing, -1 bearish engulfing, 0 none."""
    po, pc = df["open"].shift(1), df["close"].shift(1)
    bull = (df["close"] > df["open"]) & (pc < po) & (df["close"] >= po) & (df["open"] <= pc)
    bear = (df["close"] < df["open"]) & (pc > po) & (df["close"] <= po) & (df["open"] >= pc)
    return (bull.astype(int) - bear.astype(int)).rename("engulf")


def heikin_ashi(df):
    ha_c = (df["open"] + df["high"] + df["low"] + df["close"]) / 4
    ha_o = np.full(len(df), np.nan)
    o = df["open"].to_numpy()
    c = ha_c.to_numpy()
    ha_o[0] = o[0]
    for i in range(1, len(df)):
        ha_o[i] = (ha_o[i - 1] + c[i - 1]) / 2
    ha_o = pd.Series(ha_o, index=df.index)
    return pd.DataFrame(
        {
            "open": ha_o,
            "high": pd.concat([df["high"], ha_o, ha_c], axis=1).max(axis=1),
            "low": pd.concat([df["low"], ha_o, ha_c], axis=1).min(axis=1),
            "close": ha_c,
        },
        index=df.index,
    )


# ---------------------------------------------------------------- divergence

def regular_divergence(price_high, price_low, osc, left=2, right=2, max_lookback=60):
    """Regular bullish / bearish divergence against an oscillator.

    Compares consecutive confirmed pivots. Flags land on the confirmation bar of
    the second pivot, so they are tradable on the next bar open.
    Returns (bull, bear) boolean Series.
    """
    ph, pl = pivots(price_high, price_low, left, right)
    n = len(osc)
    bull = np.zeros(n, dtype=bool)
    bear = np.zeros(n, dtype=bool)

    def scan(piv, price, cmp_price, cmp_osc, out):
        idx = np.flatnonzero(piv.notna().to_numpy())
        pv = piv.to_numpy()
        ov = osc.to_numpy()
        for a, b in zip(idx, idx[1:]):
            if b - a > max_lookback:
                continue
            # the extreme sat `right` bars before its confirmation bar
            oa, ob = ov[a - right], ov[b - right]
            if np.isnan(oa) or np.isnan(ob):
                continue
            if cmp_price(pv[b], pv[a]) and cmp_osc(ob, oa):
                out[b] = True

    scan(pl, price_low, lambda x, y: x < y, lambda x, y: x > y, bull)
    scan(ph, price_high, lambda x, y: x > y, lambda x, y: x < y, bear)
    return pd.Series(bull, index=osc.index), pd.Series(bear, index=osc.index)


# ---------------------------------------------------------------- reconstructions
# Indicators the videos name but do not define. Each is rebuilt from its
# published formula. Where a video's wording leaves a choice open, the choice is
# stated in the docstring rather than buried in the code, because a
# reconstruction that quietly picks one reading is indistinguishable from a
# faithful port in the results table.

def smma(s, n):
    """Wilder/SMMA as used by LazyBear's Impulse MACD."""
    return s.ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean()


def zlema(s, n):
    e1 = ema(s, n)
    e2 = ema(e1, n)
    return e1 + (e1 - e2)


def impulse_macd(df, length=34, signal=9):
    """LazyBear's Impulse MACD (video 034).

    md is zero whenever the zero-lag mean sits inside the smoothed high/low
    band, which is the "skip consolidation" behaviour the video describes.
    Returns (md, signal_line, histogram).
    """
    hi = smma(df["high"], length)
    lo = smma(df["low"], length)
    mi = zlema((df["high"] + df["low"] + df["close"]) / 3, length)
    md = np.where(mi > hi, mi - hi, np.where(mi < lo, mi - lo, 0.0))
    md = pd.Series(md, index=df.index)
    sb = sma(md, signal)
    return md, sb, md - sb


def lwti(df, period=25, smooth=20):
    """Larry Williams Trade Index (videos 053/054).

    out = (close - close[period]) / ATR(period) * 50 + 50, smoothed by an SMA.

    The videos say only "LWTI is green". The published indicator colours green
    when the raw line is above its own smoothed line, so that is the reading
    used here. The alternative reading, green above the 50 midline, is exposed
    as `above_mid` so the runner can test both.
    """
    diff = df["close"] - df["close"].shift(period)
    rng = atr(df["high"], df["low"], df["close"], period)
    out = diff / rng.replace(0, np.nan) * 50 + 50
    sig = sma(out, smooth)
    return pd.DataFrame(
        {"lwti": out, "signal": sig, "green": out > sig, "above_mid": out > 50},
        index=df.index,
    )


def smi(df, k=10, d=3, ema_len=3):
    """Stochastic Momentum Index (video 087). Returns (smi_line, signal)."""
    hh = df["high"].rolling(k, min_periods=k).max()
    ll = df["low"].rolling(k, min_periods=k).min()
    rel = df["close"] - (hh + ll) / 2
    diff = hh - ll
    num = ema(ema(rel, d), d)
    den = ema(ema(diff / 2, d), d)
    line = 100 * num / den.replace(0, np.nan)
    return line, ema(line, ema_len)


def mcginley(s, n):
    """McGinley Dynamic, the baseline type named in video 064's SSL Hybrid."""
    v = s.to_numpy(float)
    out = np.full(len(v), np.nan)
    seed = sma(s, n).to_numpy(float)
    for i in range(len(v)):
        if np.isnan(seed[i]):
            continue
        if np.isnan(out[i - 1]) if i else True:
            out[i] = seed[i]
        else:
            prev = out[i - 1]
            ratio = v[i] / prev if prev else 1.0
            out[i] = prev + (v[i] - prev) / max(n * (ratio ** 4), 1e-9)
    return pd.Series(out, index=s.index)


def ssl_hybrid(df, length=200, baseline="mcginley"):
    """SSL Hybrid baseline channel (video 064).

    Colour is blue when close is above the baseline of highs, red when below the
    baseline of lows. Only the baseline half of the indicator is rebuilt; the
    video's entry also needs the proprietary "Next Pivot" projection, which is
    why 064 stays untestable as a whole.
    """
    f = mcginley if baseline == "mcginley" else (lambda s, n: ema(s, n))
    hi = f(df["high"], length)
    lo = f(df["low"], length)
    up = df["close"] > hi
    dn = df["close"] < lo
    return pd.DataFrame({"hi": hi, "lo": lo, "blue": up, "red": dn}, index=df.index)


def ut_bot(df, key=2.0, period=1):
    """UT Bot ATR trailing stop (video 063).

    Standard published logic: an ATR band that ratchets in the direction of the
    trend and flips when close crosses it. Returns a frame with the stop level
    and the flip signals.
    """
    a = key * atr(df["high"], df["low"], df["close"], period)
    c = df["close"].to_numpy(float)
    av = a.to_numpy(float)
    stop = np.full(len(c), np.nan)
    for i in range(1, len(c)):
        if np.isnan(av[i]):
            continue
        prev = stop[i - 1]
        if np.isnan(prev):
            stop[i] = c[i] - av[i]
            continue
        if c[i] > prev and c[i - 1] > prev:
            stop[i] = max(prev, c[i] - av[i])
        elif c[i] < prev and c[i - 1] < prev:
            stop[i] = min(prev, c[i] + av[i])
        else:
            stop[i] = c[i] - av[i] if c[i] > prev else c[i] + av[i]
    st = pd.Series(stop, index=df.index)
    above = df["close"] > st
    return pd.DataFrame(
        {"stop": st, "buy": above & ~above.shift(1).fillna(False),
         "sell": ~above & above.shift(1).fillna(False)},
        index=df.index,
    )


def smoothed_heikin_ashi(df, pre=10, post=10):
    """Smoothed Heikin Ashi (video 061): EMA the OHLC, build HA, EMA again."""
    pre_df = pd.DataFrame({c: ema(df[c], pre) for c in ["open", "high", "low", "close"]})
    ha = heikin_ashi(pre_df.dropna())
    out = pd.DataFrame({c: ema(ha[c], post) for c in ha.columns})
    return out.reindex(df.index)
