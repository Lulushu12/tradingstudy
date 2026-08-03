"""
The playlist strategies, coded.

Each function takes an OHLCV frame and a config, and returns a backtest.Signals.
Signals land on the bar whose CLOSE completes the setup; the engine fills at the
next bar's open.

Every interpretation the videos left open is marked with an ASSUMPTION comment.
Those are the places where a different reading would produce different numbers,
and they are the honest answer to "did you test what the video said".
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd

import backtest as bt
import conventions as cv
import indicators as ta


@dataclass
class Cfg:
    stop_conv: str = "swing"
    expiry: int = cv.EXPIRY_BARS
    target_r: float = 2.0
    nbar: int = 10
    atr_mult: float = 1.5
    variant: str = ""          # per strategy switch, documented at each use


def _stops(df, cfg):
    return cv.stop_levels(df, cfg.stop_conv, cfg.nbar, cfg.atr_mult)


def _rr_target(entry_ref, stop, side, r):
    return entry_ref + side * (entry_ref - stop).abs() * r


# ------------------------------------------------------------------ S1: Fib ABCD

def s1_fib_abcd(df, cfg):
    """Video 010: the 0.88 retracement entry, claimed 62% win rate over 77 trades.

    Fib is anchored to a confirmed impulse leg. 0 sits at the leg's extreme and 1
    at its origin. The setup needs three further steps: a rejection out of the
    0.5-0.618 band, a return into the 0.382-0 band, then a push to 0.88 where the
    entry sits. Target is the leg extreme, stop beyond the leg origin, both as
    the video states them, so this strategy does NOT use the stop convention
    sweep.

    ASSUMPTION: "rejects without crossing" is read as trading into the band while
    never exceeding its far edge. Exceeding the far edge kills the setup.
    """
    long_s, short_s, stop_s, tgt_s = cv.empty_signals(df)
    lim_s = pd.Series(np.nan, index=df.index)
    lo = df["low"].to_numpy(float)
    hi = df["high"].to_numpy(float)

    for leg in cv.legs(df, min_atr=cv.MIN_LEG_ATR):
        side = -1 if leg["dir"] == 1 else 1   # up leg sets up a long, per the video
        origin, extreme = leg["start_px"], leg["end_px"]
        rng = abs(extreme - origin)
        if rng <= 0:
            continue

        # level(r): 0 at the extreme, 1 at the origin
        sgn = 1.0 if leg["dir"] == 1 else -1.0
        def lvl(r):
            return extreme - sgn * rng * r

        state, step_bar = "B", leg["known_at"]
        for i in range(leg["known_at"] + 1, len(df)):
            if i - step_bar > cfg.expiry:
                break
            if state == "B":
                # kill if it blows through 0.618 before rejecting
                past = lo[i] < lvl(0.618) if leg["dir"] == 1 else hi[i] > lvl(0.618)
                inband = (lo[i] <= lvl(0.5)) if leg["dir"] == 1 else (hi[i] >= lvl(0.5))
                if past:
                    break
                if inband:
                    state, step_bar = "C", i
            elif state == "C":
                past = hi[i] > lvl(0.0) if leg["dir"] == 1 else lo[i] < lvl(0.0)
                inband = (hi[i] >= lvl(0.382)) if leg["dir"] == 1 else (lo[i] <= lvl(0.382))
                if past:
                    break
                if inband:
                    state, step_bar = "D", i
            else:
                past = lo[i] < lvl(1.0) if leg["dir"] == 1 else hi[i] > lvl(1.0)
                if past:
                    break
                hit = (lo[i] <= lvl(0.88)) if leg["dir"] == 1 else (hi[i] >= lvl(0.88))
                if hit:
                    long_s.iloc[i] = leg["dir"] == 1
                    short_s.iloc[i] = leg["dir"] != 1
                    stop_s.iloc[i] = lvl(1.0)
                    tgt_s.iloc[i] = lvl(0.0)
                    lim_s.iloc[i] = lvl(0.88)   # the entry is a resting limit
                    break
    return bt.Signals(long_s, short_s, stop_s, tgt_s, limit=lim_s)


# ------------------------------------------------- S2: Donchian + LWTI + volume

def s2_donchian_lwti(df, cfg):
    """Videos 053/054: Donchian(96) touch, LWTI green, volume above its MA(30).

    Stop at the Donchian midline, target 2R, both as stated.
    ASSUMPTION: cfg.variant "mid" switches LWTI green from "above its own
    smoothed line" (the published colouring) to "above the 50 midline".
    """
    dlo, dhi = ta.donchian(df["high"], df["low"], 96)
    dlo, dhi = dlo.shift(1), dhi.shift(1)          # prior bars only
    mid = (dlo + dhi) / 2
    lw = ta.lwti(df, 25, 20)
    green = lw["above_mid"] if cfg.variant == "mid" else lw["green"]
    volok = df["volume"] > ta.sma(df["volume"], 30)

    long_sig = (df["high"] >= dhi) & green & volok
    short_sig = (df["low"] <= dlo) & ~green & volok

    stop = pd.Series(np.nan, index=df.index)
    stop[long_sig] = mid[long_sig]
    stop[short_sig] = mid[short_sig]
    ref = df["close"]
    tgt = pd.Series(np.nan, index=df.index)
    tgt[long_sig] = _rr_target(ref, stop, 1, cfg.target_r)[long_sig]
    tgt[short_sig] = _rr_target(ref, stop, -1, cfg.target_r)[short_sig]
    return bt.Signals(long_sig.fillna(False), short_sig.fillna(False), stop, tgt)


# ---------------------------------------------------------- S3: Raschke 3/10

def s3_raschke_310(df, cfg):
    """Video 067: MACD(3,10,16) with simple averages, the "Anti" pullback trade.

    The oscillator makes an extreme, pulls back against it while the signal line
    still leans the original way, then crosses back. Entry on that recross.

    ASSUMPTION: "makes a new high" is read as a new 20 bar extreme in the
    oscillator, and the pullback must recross within cfg.expiry bars.
    """
    osc = ta.sma(df["close"], 3) - ta.sma(df["close"], 10)
    sig = ta.sma(osc, 16)
    ls, ss = _stops(df, cfg)

    new_hi = osc >= osc.rolling(20, min_periods=20).max()
    new_lo = osc <= osc.rolling(20, min_periods=20).min()
    cross_up = (osc > sig) & (osc.shift(1) <= sig.shift(1))
    cross_dn = (osc < sig) & (osc.shift(1) >= sig.shift(1))

    # armed if a new extreme happened within the expiry window
    armed_long = new_hi.rolling(cfg.expiry, min_periods=1).max().astype(bool).shift(1)
    armed_short = new_lo.rolling(cfg.expiry, min_periods=1).max().astype(bool).shift(1)

    long_sig = (cross_up & armed_long).fillna(False)
    short_sig = (cross_dn & armed_short).fillna(False)

    stop = pd.Series(np.nan, index=df.index)
    stop[long_sig] = ls[long_sig]
    stop[short_sig] = ss[short_sig]
    tgt = pd.Series(np.nan, index=df.index)
    tgt[long_sig] = _rr_target(df["close"], stop, 1, cfg.target_r)[long_sig]
    tgt[short_sig] = _rr_target(df["close"], stop, -1, cfg.target_r)[short_sig]
    return bt.Signals(long_sig, short_sig, stop, tgt)


# ------------------------------------------------------- S4: RSI 80/20 + VWAP

def s4_rsi_vwap(df, cfg):
    """Video 065: RSI banded at 80/20 rather than 70/30, target the session VWAP.

    Only the mean reversion method is coded. The video's second method, entering
    on a pullback to the RSI midline during a trend, never defines "strong trend"
    or the exit, so it is not mechanisable as stated.

    ASSUMPTION: "double bar break" is read as two consecutive closes back in the
    direction of the reversal after RSI has been beyond the band.
    """
    r = ta.rsi(df["close"], 14)
    vwap = ta.vwap_session(df, "D")
    ls, ss = _stops(df, cfg)

    was_os = (r < 20).rolling(cfg.expiry, min_periods=1).max().astype(bool)
    was_ob = (r > 80).rolling(cfg.expiry, min_periods=1).max().astype(bool)
    two_up = (df["close"] > df["close"].shift(1)) & (df["close"].shift(1) > df["close"].shift(2))
    two_dn = (df["close"] < df["close"].shift(1)) & (df["close"].shift(1) < df["close"].shift(2))

    long_sig = (was_os & two_up & (r > 20)).fillna(False)
    short_sig = (was_ob & two_dn & (r < 80)).fillna(False)
    # one entry per excursion: drop repeats while still armed
    long_sig &= ~long_sig.shift(1).fillna(False)
    short_sig &= ~short_sig.shift(1).fillna(False)

    stop = pd.Series(np.nan, index=df.index)
    stop[long_sig] = ls[long_sig]
    stop[short_sig] = ss[short_sig]
    # target is the session VWAP, but only when it sits the right side of entry
    tgt = pd.Series(np.nan, index=df.index)
    good_l = long_sig & (vwap > df["close"])
    good_s = short_sig & (vwap < df["close"])
    tgt[good_l] = vwap[good_l]
    tgt[good_s] = vwap[good_s]
    fb_l = long_sig & ~good_l
    fb_s = short_sig & ~good_s
    tgt[fb_l] = _rr_target(df["close"], stop, 1, cfg.target_r)[fb_l]
    tgt[fb_s] = _rr_target(df["close"], stop, -1, cfg.target_r)[fb_s]
    return bt.Signals(long_sig, short_sig, stop, tgt)


# -------------------------------------------------- S5: EMA trend meter + SMI

def s5_ema_meter_smi(df, cfg):
    """Video 087: EMA 13/21/34/55 stacked, plus an SMI cross in the same direction."""
    e13, e21 = ta.ema(df["close"], 13), ta.ema(df["close"], 21)
    e34, e55 = ta.ema(df["close"], 34), ta.ema(df["close"], 55)
    up = (e13 > e21) & (e21 > e34) & (e34 > e55)
    dn = (e13 < e21) & (e21 < e34) & (e34 < e55)

    line, sg = ta.smi(df)
    x_up = (line > sg) & (line.shift(1) <= sg.shift(1))
    x_dn = (line < sg) & (line.shift(1) >= sg.shift(1))
    ls, ss = _stops(df, cfg)

    long_sig = (up & x_up).fillna(False)
    short_sig = (dn & x_dn).fillna(False)
    stop = pd.Series(np.nan, index=df.index)
    stop[long_sig] = ls[long_sig]
    stop[short_sig] = ss[short_sig]
    tgt = pd.Series(np.nan, index=df.index)
    tgt[long_sig] = _rr_target(df["close"], stop, 1, cfg.target_r)[long_sig]
    tgt[short_sig] = _rr_target(df["close"], stop, -1, cfg.target_r)[short_sig]
    return bt.Signals(long_sig, short_sig, stop, tgt)


# ------------------------------------------------------------ S6: Impulse MACD

def s6_impulse_macd(df, cfg):
    """Video 034: LazyBear Impulse MACD cross, skipping the flat zone.

    md is zero by construction while the zero lag mean sits inside the smoothed
    high/low band, which is exactly the consolidation the video says to avoid,
    so requiring md off zero implements "skip weak signals" without inventing a
    threshold. Exit is the opposite cross, as stated, so there is no fixed target.
    """
    md, sb, _ = ta.impulse_macd(df)
    ls, ss = _stops(df, cfg)

    x_up = (md > sb) & (md.shift(1) <= sb.shift(1)) & (md != 0)
    x_dn = (md < sb) & (md.shift(1) >= sb.shift(1)) & (md != 0)

    stop = pd.Series(np.nan, index=df.index)
    stop[x_up] = ls[x_up]
    stop[x_dn] = ss[x_dn]
    return bt.Signals(x_up.fillna(False), x_dn.fillna(False), stop,
                      pd.Series(np.nan, index=df.index),
                      exit_long=x_dn.fillna(False), exit_short=x_up.fillna(False))


# ------------------------------------------------------ S7: Smoothed Heikin Ashi

def s7_smoothed_ha(df, cfg):
    """Video 061: smoothed Heikin Ashi (10,10) colour flip after a run.

    ASSUMPTION: "strong downtrend" is read as at least 5 consecutive red smoothed
    HA bars before the flip. cfg.variant "flip" exits on the opposite colour
    (the video's second half); default exits at 1.5R (the video's first half).
    The video actually says to do both with half the position each, which this
    engine cannot express, so the two halves are tested separately.
    """
    ha = ta.smoothed_heikin_ashi(df, 10, 10)
    green = ha["close"] > ha["open"]
    red = ~green

    run_red = red.rolling(5, min_periods=5).sum() == 5
    run_green = green.rolling(5, min_periods=5).sum() == 5
    flip_up = green & red.shift(1).fillna(False) & run_red.shift(1).fillna(False)
    flip_dn = red & green.shift(1).fillna(False) & run_green.shift(1).fillna(False)
    ls, ss = _stops(df, cfg)

    stop = pd.Series(np.nan, index=df.index)
    stop[flip_up] = ls[flip_up]
    stop[flip_dn] = ss[flip_dn]

    if cfg.variant == "flip":
        tgt = pd.Series(np.nan, index=df.index)
        xl, xs = flip_dn.fillna(False), flip_up.fillna(False)
    else:
        tgt = pd.Series(np.nan, index=df.index)
        tgt[flip_up] = _rr_target(df["close"], stop, 1, 1.5)[flip_up]
        tgt[flip_dn] = _rr_target(df["close"], stop, -1, 1.5)[flip_dn]
        xl = xs = None
    return bt.Signals(flip_up.fillna(False), flip_dn.fillna(False), stop, tgt,
                      exit_long=xl, exit_short=xs)


# ------------------------------------------------------------- S8: ABC + RSI

def s8_abc_rsi(df, cfg):
    """Video 026: A low, B high, C pullback holding above A, enter on the B break.

    Stop below C, target 2R, RSI above 50 at B for longs. Mirrored for shorts.
    """
    long_s, short_s, stop_s, tgt_s = cv.empty_signals(df)
    r = ta.rsi(df["close"], 14)
    hi = df["high"].to_numpy(float)
    lo = df["low"].to_numpy(float)
    rv = r.to_numpy(float)

    ll = cv.legs(df, min_atr=cv.MIN_LEG_ATR)
    for a_, b_ in zip(ll, ll[1:]):
        if a_["dir"] == b_["dir"]:
            continue
        if a_["dir"] == 1:                      # A low -> B high -> C pullback
            A, B, C = a_["start_px"], a_["end_px"], b_["end_px"]
            if not (C > A) or np.isnan(rv[a_["end_i"]]) or rv[a_["end_i"]] <= 50:
                continue
            start = b_["known_at"]
            for i in range(start + 1, min(start + cfg.expiry + 1, len(df))):
                if lo[i] < C:                    # C broken, pattern dead
                    break
                if hi[i] > B:
                    long_s.iloc[i] = True
                    stop_s.iloc[i] = C
                    tgt_s.iloc[i] = B + (B - C) * cfg.target_r
                    break
        else:                                    # A high -> B low -> C rally
            A, B, C = a_["start_px"], a_["end_px"], b_["end_px"]
            if not (C < A) or np.isnan(rv[a_["end_i"]]) or rv[a_["end_i"]] >= 50:
                continue
            start = b_["known_at"]
            for i in range(start + 1, min(start + cfg.expiry + 1, len(df))):
                if hi[i] > C:
                    break
                if lo[i] < B:
                    short_s.iloc[i] = True
                    stop_s.iloc[i] = C
                    tgt_s.iloc[i] = B - (C - B) * cfg.target_r
                    break
    return bt.Signals(long_s, short_s, stop_s, tgt_s)


# ---------------------------------------------- S9: the SMC sweep -> BOS -> FVG

def s9_smc(df, cfg):
    """The liquidity sweep into fair value gap family, 21 videos collapsed to one.

    Long sequence: price sweeps a confirmed swing low and closes back above it,
    then closes above the last confirmed swing high (break of structure), leaving
    a bullish fair value gap somewhere in that displacement; entry when price
    trades back into that gap. Stop beyond the sweep extreme.

    cfg.variant is a plus separated switch list:
      nosweep  drop the liquidity sweep requirement
      nobos    drop the break of structure requirement
      mid      enter at the gap midpoint instead of its near edge
      liq      target the opposing swing level instead of a fixed R multiple
    """
    sw = set(cfg.variant.split("+")) if cfg.variant else set()
    long_s, short_s, stop_s, tgt_s = cv.empty_signals(df)
    lim_s = pd.Series(np.nan, index=df.index)

    ph, pl = ta.pivots(df["high"], df["low"], cv.PIVOT_LEFT, cv.PIVOT_RIGHT)
    ph_f, pl_f = ph.ffill(), pl.ffill()
    fvg = ta.fair_value_gaps(df)

    hi, lo, cl = (df["high"].to_numpy(float), df["low"].to_numpy(float),
                  df["close"].to_numpy(float))
    phv, plv = ph_f.to_numpy(float), pl_f.to_numpy(float)
    bull_fvg = fvg["bull_fvg"].to_numpy(bool)
    bear_fvg = fvg["bear_fvg"].to_numpy(bool)
    bull_bot = fvg["bull_bottom"].to_numpy(float)
    bull_top = fvg["bull_top"].to_numpy(float)
    bear_bot = fvg["bear_bottom"].to_numpy(float)
    bear_top = fvg["bear_top"].to_numpy(float)

    n = len(df)
    for side in (1, -1):
        i = cv.PIVOT_LEFT + cv.PIVOT_RIGHT + 3
        while i < n - 1:
            # --- step 1: sweep of a confirmed level
            if "nosweep" in sw:
                swept_i, swept_px = i, (plv[i] if side == 1 else phv[i])
                if np.isnan(swept_px):
                    i += 1
                    continue
            else:
                lvl = plv[i - 1] if side == 1 else phv[i - 1]
                if np.isnan(lvl):
                    i += 1
                    continue
                took = (lo[i] < lvl and cl[i] > lvl) if side == 1 else (hi[i] > lvl and cl[i] < lvl)
                if not took:
                    i += 1
                    continue
                swept_i, swept_px = i, (lo[i] if side == 1 else hi[i])

            # --- step 2: break of structure within the expiry window
            bos_i = None
            if "nobos" in sw:
                bos_i = swept_i
            else:
                for j in range(swept_i + 1, min(swept_i + cfg.expiry + 1, n)):
                    ref = phv[j - 1] if side == 1 else plv[j - 1]
                    if np.isnan(ref):
                        continue
                    if (cl[j] > ref) if side == 1 else (cl[j] < ref):
                        bos_i = j
                        break
            if bos_i is None:
                i = swept_i + 1
                continue

            # --- step 3: a gap left by the displacement
            gap = None
            for j in range(swept_i + 1, min(bos_i + cfg.expiry + 1, n)):
                if side == 1 and bull_fvg[j]:
                    gap = (j, bull_bot[j], bull_top[j])
                elif side == -1 and bear_fvg[j]:
                    gap = (j, bear_bot[j], bear_top[j])
            if gap is None:
                i = bos_i + 1
                continue
            gj, gbot, gtop = gap

            # --- step 4: return into the gap
            entry_ref = (gtop if side == 1 else gbot)
            if "mid" in sw:
                entry_ref = (gbot + gtop) / 2
            hit = None
            for j in range(max(gj, bos_i) + 1, min(max(gj, bos_i) + cfg.expiry + 1, n - 1)):
                touched = (lo[j] <= entry_ref) if side == 1 else (hi[j] >= entry_ref)
                blown = (lo[j] < swept_px) if side == 1 else (hi[j] > swept_px)
                if blown:
                    break
                if touched:
                    hit = j
                    break
            if hit is None:
                i = bos_i + 1
                continue

            stop = swept_px
            # entry is a limit resting at the gap edge, so price is measured
            # from that level rather than from the touching bar's close
            if "liq" in sw:
                opp = phv[hit] if side == 1 else plv[hit]
                tgt = opp if not np.isnan(opp) else np.nan
                if not np.isnan(tgt) and ((side == 1 and tgt <= entry_ref) or
                                          (side == -1 and tgt >= entry_ref)):
                    tgt = entry_ref + side * abs(entry_ref - stop) * cfg.target_r
            else:
                tgt = entry_ref + side * abs(entry_ref - stop) * cfg.target_r

            (long_s if side == 1 else short_s).iloc[hit] = True
            stop_s.iloc[hit] = stop
            tgt_s.iloc[hit] = tgt
            lim_s.iloc[hit] = entry_ref
            i = hit + 1

    return bt.Signals(long_s, short_s, stop_s, tgt_s, limit=lim_s)


# ------------------------------------------------------------------- registry

REGISTRY = {
    "S1 Fib ABCD 0.88":        (s1_fib_abcd, "30m", False),
    "S2 Donchian+LWTI+vol":    (s2_donchian_lwti, "5m", True),
    "S3 Raschke 3/10":         (s3_raschke_310, "1h", True),
    "S4 RSI 80/20 + VWAP":     (s4_rsi_vwap, "15m", True),
    "S5 EMA meter + SMI":      (s5_ema_meter_smi, "4h", True),
    "S6 Impulse MACD":         (s6_impulse_macd, "4h", True),
    "S7 Smoothed HA":          (s7_smoothed_ha, "1h", True),
    "S8 ABC + RSI":            (s8_abc_rsi, "4h", False),
    "S9 SMC sweep->FVG":       (s9_smc, "15m", False),
}
# third field: whether the video leaves the stop vague, so the three stop
# conventions get swept. S1, S8 and S9 state their own stop explicitly.
