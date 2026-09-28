"""Signal library. Each family is a generator yielding (family, variant, sig, sl_dist or None).
sig: +1 long / -1 short / 0 none, decided on the CLOSE of the bar.
sl_dist: optional structural stop distance (price units); if None the exit template's ATR stop is used.
"""
import numpy as np
import pandas as pd

import ind
import features as fx
from features import cross_up, cross_dn, shift


def _sig(long_mask, short_mask):
    s = np.zeros(long_mask.size, np.int64)
    s[np.asarray(long_mask, bool)] = 1
    s[np.asarray(short_mask, bool)] = -1
    s[np.asarray(long_mask, bool) & np.asarray(short_mask, bool)] = 0
    return s


def _nz(x):
    return np.nan_to_num(np.asarray(x, dtype=np.float64), nan=0.0)


def struct_sl(cx, sig, pad=0.25, look=1):
    """Stop beyond the extreme of the last `look` bars, plus pad*ATR."""
    lo = ind.rolling_min(cx.l, look)
    hi = ind.rolling_max(cx.h, look)
    a = cx.atr
    d = np.where(sig == 1, cx.c - lo + pad * a, np.where(sig == -1, hi - cx.c + pad * a, np.nan))
    return np.where(d > 0, d, np.nan)


# =============================================================== TREND / MOMENTUM
def fam_ema_cross(cx):
    for f, s in [(5, 13), (9, 21), (20, 50), (50, 200)]:
        a, b = fx.ema(cx, f), fx.ema(cx, s)
        yield "ema_cross", f"{f}/{s}", _sig(cross_up(a, b), cross_dn(a, b)), None


def fam_ema_pullback(cx):
    for n in (9, 20, 50):
        e = fx.ema(cx, n)
        e200 = fx.ema(cx, 200) if n < 200 else e
        # trend on the execution TF: ema above slower ema; pullback touches ema, closes back beyond
        up = (e > fx.ema(cx, n * 2 + 1)) if n < 100 else np.ones_like(e, bool)
        dn = (e < fx.ema(cx, n * 2 + 1)) if n < 100 else np.ones_like(e, bool)
        L = up & (cx.l <= e) & (cx.c > e) & (cx.c > cx.o)
        S = dn & (cx.h >= e) & (cx.c < e) & (cx.c < cx.o)
        yield "ema_pullback", f"{n}", _sig(L, S), None
        sig = _sig(L, S)
        yield "ema_pullback", f"{n}_structsl", sig, struct_sl(cx, sig, 0.25, 3)


def fam_macd(cx):
    m, s, hst = fx.macd(cx)
    yield "macd_cross", "any", _sig(cross_up(m, s), cross_dn(m, s)), None
    yield "macd_cross", "below0", _sig(cross_up(m, s) & (m < 0), cross_dn(m, s) & (m > 0)), None
    yield "macd_zero", "", _sig(cross_up(m, 0), cross_dn(m, 0)), None


def fam_supertrend(cx):
    for n, m in [(10, 2.0), (10, 3.0), (7, 2.0), (14, 4.0)]:
        _, d = fx.st(cx, n, m)
        yield "st_flip", f"{n}_{m}", _sig(cross_dn(d, 0), cross_up(d, 0)), None


def fam_rsi_pullback(cx):
    # Connors-style: trend by ema200, RSI(2/3) dip
    e = fx.ema(cx, 200)
    for n, lo in [(2, 10), (2, 5), (3, 15), (7, 25)]:
        r = fx.rsi(cx, n)
        L = (cx.c > e) & (r < lo)
        S = (cx.c < e) & (r > 100 - lo)
        yield "rsi_pullback", f"{n}_{lo}", _sig(L, S), None
        # entry on the hook back
        L2 = (cx.c > e) & cross_up(r, lo)
        S2 = (cx.c < e) & cross_dn(r, 100 - lo)
        yield "rsi_pullback_hook", f"{n}_{lo}", _sig(L2, S2), None


def fam_stoch(cx):
    k, d = fx.stoch(cx, 14)
    for lo in (20, 10):
        yield "stoch_cross", f"{lo}", _sig(cross_up(k, d) & (k < lo + 5), cross_dn(k, d) & (k > 95 - lo)), None


def fam_ha(cx):
    ho, _, _, hc = F_ha(cx)
    g = hc > ho
    for n in (2, 3, 5):
        prev_red = np.ones(g.size, bool)
        prev_green = np.ones(g.size, bool)
        for k in range(1, n + 1):
            prev_red &= ~shift(g, k, 1).astype(bool)
            prev_green &= shift(g, k, 0).astype(bool)
        yield "ha_flip", f"{n}", _sig(g & prev_red, ~g & prev_green), None


def F_ha(cx):
    return fx.F(cx, "ha", lambda: ind.heikin_ashi(cx.o, cx.h, cx.l, cx.c))


def fam_momentum_bar(cx):
    rng = cx.h - cx.l
    body = np.abs(cx.c - cx.o)
    for k in (1.5, 2.0, 3.0):
        big = (rng > k * shift(cx.atr, 1)) & (body > 0.7 * rng)
        yield "wide_bar_cont", f"{k}", _sig(big & (cx.c > cx.o), big & (cx.c < cx.o)), None
        yield "wide_bar_fade", f"{k}", _sig(big & (cx.c < cx.o), big & (cx.c > cx.o)), None


def fam_consecutive(cx):
    up = cx.c > cx.o
    dn = cx.c < cx.o
    for n in (3, 4, 5, 6):
        allup = np.ones(up.size, bool)
        alldn = np.ones(up.size, bool)
        for k in range(n):
            allup &= shift(up, k, 0).astype(bool)
            alldn &= shift(dn, k, 0).astype(bool)
        yield "consec_fade", f"{n}", _sig(alldn, allup), None
        yield "consec_cont", f"{n}", _sig(allup, alldn), None


# =============================================================== BREAKOUT
def fam_donchian(cx):
    for n in (12, 24, 48, 96, 288):
        hh = shift(ind.rolling_max(cx.h, n), 1)
        ll = shift(ind.rolling_min(cx.l, n), 1)
        L = cross_up(cx.c, hh)
        S = cross_dn(cx.c, ll)
        yield "donchian_bo", f"{n}", _sig(L, S), None
        vs = fx.vol_sma(cx, 20)
        yield "donchian_bo_vol", f"{n}", _sig(L & (cx.v > 2 * shift(vs, 1)), S & (cx.v > 2 * shift(vs, 1))), None
        # failed breakout: pokes beyond prior range, closes back inside
        yield "donchian_fail", f"{n}", _sig((cx.l < ll) & (cx.c > ll), (cx.h > hh) & (cx.c < hh)), None


def fam_squeeze(cx):
    mid, bu, bl = fx.bb(cx, 20, 2.0)
    _, ku, kl = fx.kc(cx, 20, 1.5)
    sq = (bu < ku) & (bl > kl)
    fired = shift(sq, 1, 0).astype(bool) & ~sq
    mom = cx.c - (ind.rolling_max(cx.h, 20) + ind.rolling_min(cx.l, 20)) / 4 - ind.sma(cx.c, 20) / 2
    yield "ttm_squeeze", "fire", _sig(fired & (mom > 0), fired & (mom < 0)), None
    width = (bu - bl) / mid
    for n in (50, 100):
        low_w = width <= shift(ind.rolling_min(_nz(width), n), 1) * 1.1
        prior_low = shift(low_w, 1, 0).astype(bool)
        yield "bb_squeeze_bo", f"{n}", _sig(prior_low & (cx.c > bu), prior_low & (cx.c < bl)), None


def fam_inside_nr(cx):
    ib = (cx.h < shift(cx.h, 1)) & (cx.l > shift(cx.l, 1))
    ib_prev = shift(ib, 1, 0).astype(bool)
    L = ib_prev & (cx.c > shift(cx.h, 1))
    S = ib_prev & (cx.c < shift(cx.l, 1))
    yield "inside_bar_bo", "", _sig(L, S), None
    rng = cx.h - cx.l
    for n in (4, 7):
        nr = rng <= ind.rolling_min(rng, n)
        nrp = shift(nr, 1, 0).astype(bool)
        yield "nr_bo", f"{n}", _sig(nrp & (cx.c > shift(cx.h, 1)), nrp & (cx.c < shift(cx.l, 1))), None


def _session_or(cx, tz, start_min, length):
    """Opening range for a session starting at local start_min, lasting `length` minutes.
    Returns (or_high, or_low, active_mask, window_id) where active_mask marks bars after OR completes
    (for 4h) on the same local day."""
    lm, lday = fx.local_minute(cx, tz)
    in_or = (lm >= start_min) & (lm < start_min + length)
    after = (lm >= start_min + length) & (lm < start_min + length + 240)
    df = pd.DataFrame({"h": np.where(in_or, cx.h, np.nan), "l": np.where(in_or, cx.l, np.nan), "d": lday})
    g = df.groupby("d")
    orh = g.h.transform("max").values
    orl = g.l.transform("min").values
    return orh, orl, after, lday


def fam_opening_range(cx):
    sessions = [("UTC", 0, "asia"), ("Europe/London", 8 * 60, "london"), ("America/New_York", 9 * 60 + 30, "ny")]
    for tz, st, nm in sessions:
        for ln in (15, 30, 60):
            orh, orl, after, lday = _session_or(cx, tz, st, ln)
            L = after & cross_up(cx.c, orh)
            S = after & cross_dn(cx.c, orl)
            # only first breakout per session
            first = _first_per_group(L | S, lday)
            sig = _sig(L & first, S & first)
            sl = np.where(sig != 0, (orh - orl) * 0.5 + 0.1 * cx.atr, np.nan)  # stop at OR mid
            yield "orb", f"{nm}_{ln}", sig, None
            yield "orb", f"{nm}_{ln}_midsl", sig, sl
            # fade: breaks out then closes back inside
            Lf = after & (shift(cx.c, 1) < orl) & (cx.c > orl)
            Sf = after & (shift(cx.c, 1) > orh) & (cx.c < orh)
            firstf = _first_per_group(Lf | Sf, lday)
            yield "orb_fade", f"{nm}_{ln}", _sig(Lf & firstf, Sf & firstf), None


def _first_per_group(mask, grp):
    s = pd.Series(mask.astype(int))
    c = s.groupby(grp).cumsum().values
    return mask & (c == 1)


def fam_prev_day(cx):
    pdh, pdl, pdc = fx.prev_day_hl(cx)
    day = fx.day_id(cx)
    L = cross_up(cx.c, pdh)
    S = cross_dn(cx.c, pdl)
    yield "pdhl_bo", "", _sig(L & _first_per_group(L, day), S & _first_per_group(S, day)), None
    # sweep & reclaim
    Ls = (cx.l < pdl) & (cx.c > pdl)
    Ss = (cx.h > pdh) & (cx.c < pdh)
    sig = _sig(Ls & _first_per_group(Ls, day), Ss & _first_per_group(Ss, day))
    yield "pdhl_sweep", "", sig, None
    yield "pdhl_sweep", "structsl", sig, struct_sl(cx, sig, 0.2, 1)


def fam_asia_sweep(cx):
    lm, lday = fx.local_minute(cx, "UTC")
    in_asia = lm < 7 * 60
    df = pd.DataFrame({"h": np.where(in_asia, cx.h, np.nan), "l": np.where(in_asia, cx.l, np.nan), "d": lday})
    ah = df.groupby("d").h.transform("max").values
    al = df.groupby("d").l.transform("min").values
    win = (lm >= 7 * 60) & (lm < 16 * 60)
    Ls = win & (cx.l < al) & (cx.c > al)
    Ss = win & (cx.h > ah) & (cx.c < ah)
    sig = _sig(Ls & _first_per_group(Ls, lday), Ss & _first_per_group(Ss, lday))
    yield "asia_sweep", "", sig, None
    yield "asia_sweep", "structsl", sig, struct_sl(cx, sig, 0.2, 1)
    Lb = win & cross_up(cx.c, ah)
    Sb = win & cross_dn(cx.c, al)
    yield "asia_bo", "", _sig(Lb & _first_per_group(Lb, lday), Sb & _first_per_group(Sb, lday)), None


# =============================================================== MEAN REVERSION
def fam_bb_revert(cx):
    for n, k in [(20, 2.0), (20, 2.5), (20, 3.0)]:
        mid, u, lo = fx.bb(cx, n, k)
        yield "bb_reenter", f"{n}_{k}", _sig(cross_up(cx.c, lo), cross_dn(cx.c, u)), None
        yield "bb_outside", f"{n}_{k}", _sig(cross_dn(cx.c, lo), cross_up(cx.c, u)), None


def fam_rsi_extreme(cx):
    for n, lo in [(14, 30), (14, 25), (14, 20), (7, 20)]:
        r = fx.rsi(cx, n)
        yield "rsi_ext_hook", f"{n}_{lo}", _sig(cross_up(r, lo), cross_dn(r, 100 - lo)), None


def fam_vwap(cx):
    vw, sd = fx.vwap(cx)
    lm = fx.minute_of_day(cx)
    ok = lm >= 60  # need some session to build
    for k in (1.0, 2.0, 3.0):
        lo, up = vw - k * sd, vw + k * sd
        yield "vwap_band_revert", f"{k}", _sig(ok & cross_up(cx.c, lo), ok & cross_dn(cx.c, up)), None
    L = ok & (cx.l <= vw) & (cx.c > vw) & (shift(cx.c, 1) > shift(vw, 1))
    S = ok & (cx.h >= vw) & (cx.c < vw) & (shift(cx.c, 1) < shift(vw, 1))
    yield "vwap_bounce", "", _sig(L, S), None
    yield "vwap_cross", "", _sig(ok & cross_up(cx.c, vw), ok & cross_dn(cx.c, vw)), None


def fam_zscore(cx):
    for n in (20, 50):
        z = ind.zscore(cx.c, n)
        for k in (2.0, 2.5, 3.0):
            yield "zscore_revert", f"{n}_{k}", _sig(cross_up(z, -k), cross_dn(z, k)), None


def fam_keltner(cx):
    for k in (2.0, 2.5, 3.0):
        _, u, lo = fx.kc(cx, 20, k)
        yield "kc_reenter", f"{k}", _sig(cross_up(cx.c, lo), cross_dn(cx.c, u)), None


def fam_cci_mfi(cx):
    c = fx.F(cx, "cci20", lambda: ind.cci(cx.h, cx.l, cx.c, 20))
    for k in (100, 200):
        yield "cci_hook", f"{k}", _sig(cross_up(c, -k), cross_dn(c, k)), None
    m = fx.F(cx, "mfi14", lambda: ind.mfi(cx.h, cx.l, cx.c, cx.v, 14))
    for lo in (20, 10):
        yield "mfi_hook", f"{lo}", _sig(cross_up(m, lo), cross_dn(m, 100 - lo)), None


# =============================================================== CANDLESTICKS
def candles(cx):
    o, h, l, c = cx.o, cx.h, cx.l, cx.c
    body = np.abs(c - o)
    rng = np.maximum(h - l, 1e-12)
    up_w = h - np.maximum(o, c)
    lo_w = np.minimum(o, c) - l
    a = cx.atr
    po, pc, ph, pl = shift(o, 1), shift(c, 1), shift(h, 1), shift(l, 1)
    p2o, p2c = shift(o, 2), shift(c, 2)
    pbody = np.abs(pc - po)
    P = {}
    P["engulf"] = ((c > o) & (pc < po) & (c >= po) & (o <= pc) & (body > pbody),
                   (c < o) & (pc > po) & (c <= po) & (o >= pc) & (body > pbody))
    P["pinbar"] = ((lo_w > 2 * body) & (lo_w > 0.6 * rng) & (rng > 0.8 * a),
                   (up_w > 2 * body) & (up_w > 0.6 * rng) & (rng > 0.8 * a))
    P["hammer_strict"] = ((lo_w > 3 * body) & (up_w < 0.15 * rng) & (rng > a),
                          (up_w > 3 * body) & (lo_w < 0.15 * rng) & (rng > a))
    P["morning_star"] = ((p2c < p2o) & (np.abs(p2c - p2o) > 0.6 * a) & (pbody < 0.3 * a) & (c > o) & (c > (p2o + p2c) / 2),
                         (p2c > p2o) & (np.abs(p2c - p2o) > 0.6 * a) & (pbody < 0.3 * a) & (c < o) & (c < (p2o + p2c) / 2))
    P["piercing"] = ((pc < po) & (pbody > 0.6 * a) & (o < pc) & (c > (po + pc) / 2) & (c < po),
                     (pc > po) & (pbody > 0.6 * a) & (o > pc) & (c < (po + pc) / 2) & (c > po))
    P["three_soldiers"] = ((c > o) & (pc > po) & (p2c > p2o) & (c > pc) & (pc > p2c) & (body > 0.5 * a) & (pbody > 0.5 * a),
                           (c < o) & (pc < po) & (p2c < p2o) & (c < pc) & (pc < p2c) & (body > 0.5 * a) & (pbody > 0.5 * a))
    P["outside_rev"] = ((h > ph) & (l < pl) & (c > ph), (h > ph) & (l < pl) & (c < pl))
    P["marubozu"] = ((c > o) & (body > 0.9 * rng) & (rng > 1.2 * a), (c < o) & (body > 0.9 * rng) & (rng > 1.2 * a))
    P["tweezer"] = ((np.abs(l - pl) < 0.05 * a) & (pc < po) & (c > o), (np.abs(h - ph) < 0.05 * a) & (pc > po) & (c < o))
    P["three_bar_rev"] = ((shift(l, 1) < shift(l, 2)) & (shift(l, 1) < l) & (c > ph),
                          (shift(h, 1) > shift(h, 2)) & (shift(h, 1) > h) & (c < pl))
    return P


def fam_candles(cx):
    P = fx.F(cx, "candles", lambda: candles(cx))
    for look in (0, 20, 50):
        if look:
            at_low = cx.l <= ind.rolling_min(cx.l, look) * 1.0005
            at_high = cx.h >= ind.rolling_max(cx.h, look) * 0.9995
            # for multi-bar patterns check the extreme within last 3 bars
            at_low3 = ind.rolling_min(cx.l, 3) <= ind.rolling_min(cx.l, look) * 1.0005
            at_high3 = ind.rolling_max(cx.h, 3) >= ind.rolling_max(cx.h, look) * 0.9995
        for name, (L, S) in P.items():
            if look:
                cont = name in ("marubozu", "three_soldiers")
                if cont:
                    L2, S2 = L & at_high3, S & at_low3  # continuation at breakout
                else:
                    L2, S2 = L & at_low3, S & at_high3
            else:
                L2, S2 = L, S
            sig = _sig(_nz(L2).astype(bool), _nz(S2).astype(bool))
            yield "candle", f"{name}_ctx{look}", sig, None
            yield "candle", f"{name}_ctx{look}_structsl", sig, struct_sl(cx, sig, 0.2, 3)


# =============================================================== SWING STRUCTURE / SFP
def fam_sfp(cx):
    for left, right in [(5, 5), (10, 5), (20, 10)]:
        ph, pl, _, _ = fx.piv(cx, left, right)
        lph = pd.Series(ph).ffill().values
        lpl = pd.Series(pl).ffill().values
        Ss = (cx.h > lph) & (cx.c < lph)
        Ls = (cx.l < lpl) & (cx.c > lpl)
        sig = _sig(Ls, Ss)
        yield "sfp", f"{left}_{right}", sig, None
        yield "sfp", f"{left}_{right}_structsl", sig, struct_sl(cx, sig, 0.2, 1)
        # break of structure (close beyond last swing) = momentum
        yield "bos", f"{left}_{right}", _sig(cross_up(cx.c, lph), cross_dn(cx.c, lpl)), None


def fam_pivot_points(cx):
    pdh, pdl, pdc = fx.prev_day_hl(cx)
    p = (pdh + pdl + pdc) / 3
    r1, s1 = 2 * p - pdl, 2 * p - pdh
    r2, s2 = p + (pdh - pdl), p - (pdh - pdl)
    for nm, lvl_lo, lvl_hi in [("s1r1", s1, r1), ("s2r2", s2, r2), ("p", p, p)]:
        L = (cx.l <= lvl_lo) & (cx.c > lvl_lo)
        S = (cx.h >= lvl_hi) & (cx.c < lvl_hi)
        yield "floor_pivot_bounce", nm, _sig(L, S), None
        yield "floor_pivot_break", nm, _sig(cross_up(cx.c, lvl_hi), cross_dn(cx.c, lvl_lo)), None
    # camarilla H3/L3 fade, H4/L4 breakout
    rng = pdh - pdl
    h3, l3 = pdc + rng * 1.1 / 4, pdc - rng * 1.1 / 4
    h4, l4 = pdc + rng * 1.1 / 2, pdc - rng * 1.1 / 2
    yield "camarilla_fade", "h3l3", _sig(cross_up(cx.c, l3), cross_dn(cx.c, h3)), None
    yield "camarilla_bo", "h4l4", _sig(cross_up(cx.c, h4), cross_dn(cx.c, l4)), None


# =============================================================== DIVERGENCES
def _divergence(cx, osc, left, right, min_gap=5, max_gap=60, hidden=False):
    ph, pl, phi, pli = fx.piv(cx, left, right)
    n = cx.c.size
    L = np.zeros(n, bool)
    S = np.zeros(n, bool)
    last_l = last_h = -1
    for i in range(n):
        if pli[i] >= 0:
            p = pli[i]
            if last_l >= 0 and min_gap <= p - last_l <= max_gap and not np.isnan(osc[p]) and not np.isnan(osc[last_l]):
                if not hidden and cx.l[p] < cx.l[last_l] and osc[p] > osc[last_l]:
                    L[i] = True
                if hidden and cx.l[p] > cx.l[last_l] and osc[p] < osc[last_l]:
                    L[i] = True
            last_l = p
        if phi[i] >= 0:
            p = phi[i]
            if last_h >= 0 and min_gap <= p - last_h <= max_gap and not np.isnan(osc[p]) and not np.isnan(osc[last_h]):
                if not hidden and cx.h[p] > cx.h[last_h] and osc[p] < osc[last_h]:
                    S[i] = True
                if hidden and cx.h[p] < cx.h[last_h] and osc[p] > osc[last_h]:
                    S[i] = True
            last_h = p
    return _sig(L, S)


def fam_divergence(cx):
    m, _, hst = fx.macd(cx)
    k, _ = fx.stoch(cx, 14)
    obv = fx.F(cx, "obv", lambda: np.cumsum(np.sign(np.diff(cx.c, prepend=cx.c[0])) * cx.v))
    # replicable volume delta: up-volume minus down-volume, classified by the bar's direction
    cvd = fx.F(cx, "cvd", lambda: np.cumsum(np.where(cx.c >= cx.o, cx.v, -cx.v)))
    oscs = {"rsi14": fx.rsi(cx, 14), "macd": m, "hist": hst, "stoch": k, "obv": obv, "cvd": cvd,
            "mfi": fx.F(cx, "mfi14", lambda: ind.mfi(cx.h, cx.l, cx.c, cx.v, 14))}
    for (left, right) in [(5, 2), (5, 5), (10, 3)]:
        for on, osc in oscs.items():
            for hid in (False, True):
                sig = _divergence(cx, osc, left, right, hidden=hid)
                nm = f"{on}_{left}_{right}"
                yield ("hdiv" if hid else "div"), nm, sig, None
                yield ("hdiv" if hid else "div"), nm + "_structsl", sig, struct_sl(cx, sig, 0.2, right + 1)


# =============================================================== VOLUME
def fam_volume(cx):
    vs = shift(fx.vol_sma(cx, 20), 1)
    rng = cx.h - cx.l
    for k in (2.0, 3.0, 5.0):
        spike = cx.v > k * vs
        # climax: huge volume, close off the extreme -> reversal
        yield "vol_climax", f"{k}", _sig(spike & (cx.c < cx.o) & ((cx.c - cx.l) > 0.4 * rng),
                                          spike & (cx.c > cx.o) & ((cx.h - cx.c) > 0.4 * rng)), None
        yield "vol_thrust", f"{k}", _sig(spike & (cx.c > cx.o) & ((cx.h - cx.c) < 0.2 * rng),
                                          spike & (cx.c < cx.o) & ((cx.c - cx.l) < 0.2 * rng)), None
    # taker imbalance (Binance taker buy volume; TradingView equivalent needs lower-TF delta)
    tb = cx.df.taker_buy_volume.values
    ratio = np.where(cx.v > 0, tb / np.maximum(cx.v, 1e-12), 0.5)
    r_s = ind.sma(ratio, 12)
    for th in (0.56, 0.6):
        yield "taker_ratio_mom", f"{th}", _sig(cross_up(r_s, th), cross_dn(r_s, 1 - th)), None
        yield "taker_ratio_fade", f"{th}", _sig(cross_dn(r_s, 1 - th), cross_up(r_s, th)), None


# =============================================================== VOLUME PROFILE
def _vp_levels(cx, bins=50, va=0.70):
    """Previous UTC day's volume profile from execution-TF bars: POC, VAH, VAL.
    Each bar's volume is spread uniformly over the bins its high-low range covers."""
    day = fx.day_id(cx)
    uniq, start = np.unique(day, return_index=True)
    end = np.append(start[1:], day.size)
    poc = np.full(uniq.size, np.nan); vah = poc.copy(); val = poc.copy()
    for k in range(uniq.size):
        s, e = start[k], end[k]
        hi, lo = cx.h[s:e].max(), cx.l[s:e].min()
        if hi <= lo:
            continue
        edges = np.linspace(lo, hi, bins + 1)
        width = edges[1] - edges[0]
        prof = np.zeros(bins)
        for j in range(s, e):
            b0 = int(min((cx.l[j] - lo) / width, bins - 1))
            b1 = int(min((cx.h[j] - lo) / width, bins - 1))
            prof[b0:b1 + 1] += cx.v[j] / (b1 - b0 + 1)
        pi = int(prof.argmax())
        tot = prof.sum()
        a, b = pi, pi
        acc = prof[pi]
        while acc < va * tot:
            up = prof[b + 1] if b + 1 < bins else -1
            dn = prof[a - 1] if a - 1 >= 0 else -1
            if up >= dn:
                b += 1; acc += up
            else:
                a -= 1; acc += dn
        poc[k] = (edges[pi] + edges[pi + 1]) / 2
        vah[k] = edges[b + 1]
        val[k] = edges[a]
    # shift by one day: today's bars see yesterday's profile
    idx = np.searchsorted(uniq, day)
    prev = idx - 1
    ok = prev >= 0
    P = np.where(ok, poc[np.maximum(prev, 0)], np.nan)
    H = np.where(ok, vah[np.maximum(prev, 0)], np.nan)
    Lo = np.where(ok, val[np.maximum(prev, 0)], np.nan)
    return P, H, Lo


def fam_volume_profile(cx):
    P, H, Lo = fx.F(cx, "vp", lambda: _vp_levels(cx))
    day = fx.day_id(cx)
    # 1) rejection at yesterday's value edges
    L = (cx.l <= Lo) & (cx.c > Lo)
    S = (cx.h >= H) & (cx.c < H)
    sig = _sig(L, S)
    yield "vp_edge_reject", "", sig, None
    yield "vp_edge_reject", "structsl", sig, struct_sl(cx, sig, 0.2, 2)
    # 2) 80% rule: day opened outside value, price re-enters value -> trade toward other edge
    first_open = pd.Series(cx.o).groupby(day).transform("first").values
    Lr = (first_open < Lo) & cross_up(cx.c, Lo)
    Sr = (first_open > H) & cross_dn(cx.c, H)
    sig = _sig(Lr & _first_per_group(Lr, day), Sr & _first_per_group(Sr, day))
    yield "vp_80rule", "", sig, None
    # dedicated target: other value-area edge handled by the R-based exits; also give structural stop
    yield "vp_80rule", "structsl", sig, struct_sl(cx, sig, 0.3, 6)
    # 3) acceptance breakout of value
    yield "vp_break", "", _sig(cross_up(cx.c, H), cross_dn(cx.c, Lo)), None
    # 4) POC test from the trend side
    Lp = (shift(cx.c, 1) > shift(P, 1)) & (cx.l <= P) & (cx.c > P)
    Sp = (shift(cx.c, 1) < shift(P, 1)) & (cx.h >= P) & (cx.c < P)
    yield "vp_poc_bounce", "", _sig(Lp, Sp), None


# =============================================================== FIBONACCI
def fam_fib(cx):
    """Objective fib retracements: swings from confirmed pivots (so no hindsight anchoring).
    Up-swing = confirmed pivot low followed by a confirmed pivot high that is >= min_atr ATR above it.
    Signal: price trades into the retracement zone and closes back out of it (rejection),
    before breaking the swing origin. Stop beyond the 0.786 level (or swing origin)."""
    for left, right, min_atr in [(10, 5, 4.0), (20, 10, 6.0), (5, 3, 3.0)]:
        ph, pl, phi, pli = fx.piv(cx, left, right)
        for lvl, stop_lvl in [(0.5, 0.786), (0.618, 0.786), (0.618, 1.0), (0.786, 1.0)]:
            sig, sl = _fib_scan(cx.h, cx.l, cx.c, cx.o, cx.atr, phi, pli, lvl, stop_lvl, min_atr)
            yield "fib_retrace", f"{left}_{right}_{lvl}_{stop_lvl}", sig, sl
            yield "fib_retrace", f"{left}_{right}_{lvl}_atrsl", sig, None


def _fib_scan(h, l, c, o, a, phi, pli, lvl, stop_lvl, min_atr):
    n = c.size
    sig = np.zeros(n, np.int64)
    sl = np.full(n, np.nan)
    last_h_idx = last_l_idx = -1
    swing = 0  # +1 up-swing active, -1 down-swing active
    s_lo = s_hi = np.nan
    used = False
    for i in range(n):
        if pli[i] >= 0:
            last_l_idx = pli[i]
            if last_h_idx >= 0 and last_h_idx < last_l_idx and h[last_h_idx] - l[last_l_idx] >= min_atr * a[i]:
                swing, s_hi, s_lo, used = -1, h[last_h_idx], l[last_l_idx], False
        if phi[i] >= 0:
            last_h_idx = phi[i]
            if last_l_idx >= 0 and last_l_idx < last_h_idx and h[last_h_idx] - l[last_l_idx] >= min_atr * a[i]:
                swing, s_hi, s_lo, used = 1, h[last_h_idx], l[last_l_idx], False
        if swing == 0 or used or np.isnan(a[i]):
            continue
        rngs = s_hi - s_lo
        if swing == 1:
            level = s_hi - lvl * rngs
            stop = s_hi - stop_lvl * rngs
            if l[i] < s_lo:  # invalidated
                swing = 0
                continue
            if h[i] > s_hi:  # new high, swing extends; wait for new pivot
                swing = 0
                continue
            if l[i] <= level and c[i] > level and c[i] > o[i]:
                sig[i] = 1
                sl[i] = c[i] - stop + 0.1 * a[i]
                used = True
        else:
            level = s_lo + lvl * rngs
            stop = s_lo + stop_lvl * rngs
            if h[i] > s_hi or l[i] < s_lo:
                swing = 0
                continue
            if h[i] >= level and c[i] < level and c[i] < o[i]:
                sig[i] = -1
                sl[i] = stop - c[i] + 0.1 * a[i]
                used = True
    sl = np.where(sl > 0, sl, np.nan)
    return sig, sl


# =============================================================== TIME
def fam_time(cx):
    """Pure time-of-day drift probe: enter at the start of each UTC hour in the HTF bias direction.
    (Only meaningful combined with a bias; tells us whether any hour carries directional drift.)"""
    lm = fx.minute_of_day(cx)
    for hr in range(24):
        m = lm == hr * 60 + (60 - 5)  # close of the bar before the hour -> enter at the hour open
        yield "hour_drift", f"{(hr + 1) % 24:02d}", _sig(m, np.zeros_like(m)), None
        yield "hour_drift_short", f"{(hr + 1) % 24:02d}", _sig(np.zeros_like(m), m), None


FAMILIES = [fam_ema_cross, fam_ema_pullback, fam_macd, fam_supertrend, fam_rsi_pullback, fam_stoch, fam_ha,
            fam_momentum_bar, fam_consecutive, fam_donchian, fam_squeeze, fam_inside_nr, fam_opening_range,
            fam_prev_day, fam_asia_sweep, fam_bb_revert, fam_rsi_extreme, fam_vwap, fam_zscore, fam_keltner,
            fam_cci_mfi, fam_candles, fam_sfp, fam_pivot_points, fam_divergence, fam_volume,
            fam_volume_profile, fam_fib, fam_time]


# =============================================================== WAVE 2
def fam_btc_leadlag(cx):
    """BTC leads alts: BTC bar return large (in its own ATR units) while the alt lagged."""
    if cx.sym == "BTCUSDT":
        return
    from data import bars
    b = bars("BTCUSDT", cx.tf).reindex(cx.df.index)
    bc, bo = b.close.values, b.open.values
    batr = ind.atr(b.high.values, b.low.values, bc, 14)
    bmove = (bc - bo) / batr
    amove = (cx.c - cx.o) / cx.atr
    for k in (1.0, 1.5, 2.0):
        for lag in (0.25, 0.5):
            L = (bmove > k) & (amove < lag * bmove)
            S = (bmove < -k) & (amove > lag * bmove)
            yield "btc_leadlag", f"{k}_{lag}", _sig(_nz(L).astype(bool), _nz(S).astype(bool)), None
    # 3-bar version
    b3 = (bc - shift(bc, 3)) / batr
    a3 = (cx.c - shift(cx.c, 3)) / cx.atr
    for k in (2.0, 3.0):
        L = (b3 > k) & (a3 < 0.5 * b3)
        S = (b3 < -k) & (a3 > 0.5 * b3)
        yield "btc_leadlag3", f"{k}", _sig(_nz(L).astype(bool), _nz(S).astype(bool)), None


WAVE2 = [fam_btc_leadlag]
