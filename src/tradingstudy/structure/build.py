"""Market-structure features for one coin and execution timeframe (brief 5.6).

Structure timeframes used for an execution TF X: X itself plus every structure TF above X
(6m, 24m, 30m, 1h, 4h, 1D, 1W). An execution bar sees a structure TF only as of that TF's last fully closed bar.
Distances are in ATR(14) of the timeframe the level comes from, except the confluence band, which is
band x ATR(14) of the execution TF around the execution close.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from tradingstudy.data.guard import clip_scope, load_bars
from tradingstudy.features import ta
from tradingstudy.features.build import EXEC_TFS, bars_any
from tradingstudy.structure import levels as lv
from tradingstudy.structure.profile import prev_day_profiles, volume_profile
from tradingstudy.structure.ranges import ranges_and_flips
from tradingstudy.structure.swings import zigzag

STRUCTURE_TFS = {"6m": 6, "15m": 15, "24m": 24, "30m": 30, "1h": 60, "4h": 240, "1D": 1440, "1W": 10080}
STRUCT_DEFAULTS = dict(k=3.0, confluence_band=0.25, frvp_bin_frac=0.1, va_touch=0.5)  # PROTOCOL section 6
MIN = pd.Timedelta(minutes=1)


def _align_pos(struct_index: pd.DatetimeIndex, struct_min: int, exec_index: pd.DatetimeIndex, exec_min: int) -> np.ndarray:
    ends = (struct_index + struct_min * MIN).as_unit("ns").asi8
    closes = (exec_index + exec_min * MIN).as_unit("ns").asi8
    return np.searchsorted(ends, closes, side="right") - 1


def _take(arr: np.ndarray, pos: np.ndarray) -> np.ndarray:
    out = arr[np.clip(pos, 0, None)].astype(float)
    out[pos < 0] = np.nan
    return out


def structure_tf(sym: str, tf: str, m1: pd.DataFrame, scope: str, k: float, range_kw: dict, level_kw: dict, frvp_bin_frac: float):
    minutes = STRUCTURE_TFS[tf]
    bars = bars_any(sym, minutes, scope, m1=m1)
    atr = ta.atr(bars["high"], bars["low"], bars["close"], 14)
    sw = zigzag(bars, k)
    state, events, ranges = ranges_and_flips(bars, sw, **range_kw)
    held = lv.held_levels(bars, sw, atr, minutes, **level_kw)
    legs = lv.fib_legs(sw, len(bars))
    n = len(bars)
    # last broken range per bar (known from its break bar) and its FRVP
    lb = np.full((n, 5), np.nan)  # high, low, poc, vah, val
    broken = ranges[ranges.outcome != 0].sort_values("end")
    prof_cache = {}
    for r in broken.itertuples(index=False):
        r_start, r_end = int(r.start), int(r.end)
        t0, t1 = bars.index[r_start], bars.index[r_end] + minutes * MIN
        p = volume_profile(m1.loc[(m1.index >= t0) & (m1.index < t1)], frvp_bin_frac * r.atr)
        prof_cache[(r_start, r_end)] = p
        lb[r_end:, :] = (r.high, r.low, p["poc"], p["vah"], p["val"])
    # FRVP features for flip events of this TF
    if len(events):
        ev_rows = []
        for e in events.itertuples(index=False):
            p = prof_cache.get((int(e.range_start), int(e.break_bar)))
            if p is None:
                t0, t1 = bars.index[int(e.range_start)], bars.index[int(e.break_bar)] + minutes * MIN
                p = volume_profile(m1.loc[(m1.index >= t0) & (m1.index < t1)], frvp_bin_frac * e.atr_at_break)
            level = e.range_low if e.direction == -1 else e.range_high
            edge = p["val"] if e.direction == -1 else p["vah"]
            ev_rows.append({"frvp_poc": p["poc"], "frvp_vah": p["vah"], "frvp_val": p["val"],
                            "retest_dist_va_edge_atr": (level - edge) / e.atr_at_break,
                            "retest_dist_poc_atr": (level - p["poc"]) / e.atr_at_break,
                            "retest_near_lvn": bool(len(p["lvns"]) and np.min(np.abs(p["lvns"] - level)) <= 0.5 * e.atr_at_break)})
        events = pd.concat([events.reset_index(drop=True), pd.DataFrame(ev_rows)], axis=1)
    events["tf"] = tf
    events["known_at"] = events["time"] + minutes * MIN if len(events) else pd.Series(dtype="datetime64[ns, UTC]")
    return {"bars": bars, "minutes": minutes, "atr": atr, "swings": sw, "state": state, "events": events,
            "ranges": ranges, "held": held, "legs": legs, "last_broken": lb}


def build_structure(sym: str, tf: str, scope: str = "dev", k: float | None = None, range_kw: dict | None = None,
                    level_kw: dict | None = None, confluence_band: float | None = None, warmup: bool = True):
    """warmup=True (PROTOCOL section 1): compute on 'dev_warmup' data, return only dev rows and dev events."""
    out_scope = scope
    if scope == "dev" and warmup:
        scope = "dev_warmup"
    p = dict(STRUCT_DEFAULTS)
    if k is not None:
        p["k"] = k
    if confluence_band is not None:
        p["confluence_band"] = confluence_band
    cm = EXEC_TFS[tf]
    ex = load_bars(sym, tf, scope)
    idx = ex.index
    close = ex["close"].to_numpy(np.float64)
    ex_atr = ta.atr(ex["high"], ex["low"], ex["close"], 14)
    band = p["confluence_band"] * ex_atr
    m1 = load_bars(sym, "1m", scope)
    tfs = [tf] + [t for t, m in STRUCTURE_TFS.items() if m > cm]
    feats = {}
    conf_count = np.zeros(len(ex))
    conf_top_tf = np.zeros(len(ex))
    near_fib = np.full(len(ex), np.inf)
    near_fib_lvl = np.full(len(ex), np.nan)
    near_fib_tf = np.full(len(ex), np.nan)
    type_hit = {t: np.zeros(len(ex), dtype=bool) for t in ("fib", "sr", "range", "profile")}
    lvl_above = np.full(len(ex), np.inf)
    lvl_below = np.full(len(ex), -np.inf)
    all_events = []
    for rank, stf in enumerate(tfs):
        S = structure_tf(sym, stf, m1, scope, p["k"], range_kw or {}, level_kw or {}, p["frvp_bin_frac"])
        pos = _align_pos(S["bars"].index, S["minutes"], idx, cm)
        a = _take(S["atr"], pos)
        levels = []  # (n_exec, K) blocks of level prices
        # held S/R
        hp = S["held"]["price"][np.clip(pos, 0, None)].copy(); hp[pos < 0] = np.nan
        hs = S["held"]["strength"][np.clip(pos, 0, None)].copy()
        hr = S["held"]["role"][np.clip(pos, 0, None)].astype(float)
        hf = S["held"]["flipped"][np.clip(pos, 0, None)].astype(float)
        levels.append(hp)
        d = np.abs(hp - close[:, None])
        j = np.nanargmin(np.where(np.isnan(d), np.inf, d), axis=1)
        rows = np.arange(len(ex))
        feats[f"sr_{stf}_dist_atr"] = (hp[rows, j] - close) / a
        feats[f"sr_{stf}_strength"] = hs[rows, j]
        feats[f"sr_{stf}_role"] = hr[rows, j]
        feats[f"sr_{stf}_flipped"] = hf[rows, j]
        # ranges: active bounds and last broken range bounds plus its FRVP
        st = S["state"]
        rh, rl = _take(st["range_high"].to_numpy(), pos), _take(st["range_low"].to_numpy(), pos)
        feats[f"range_{stf}_active"] = _take(st["range_active"].to_numpy().astype(float), pos)
        feats[f"range_{stf}_pos"] = (close - rl) / (rh - rl)
        lb = S["last_broken"][np.clip(pos, 0, None)].copy(); lb[pos < 0] = np.nan
        levels += [np.c_[rh, rl], lb]
        within = lambda X: (np.abs(X - close[:, None]) <= band[:, None]).any(axis=1)
        type_hit["sr"] |= within(hp)
        type_hit["range"] |= within(np.c_[rh, rl, lb[:, 0], lb[:, 1]])
        type_hit["profile"] |= within(lb[:, 2:5])
        # next opposing level candidates (PROTOCOL section 4): held S/R, active range bounds, last broken range bounds
        cand = np.c_[hp, rh, rl, lb[:, 0], lb[:, 1]]
        above = np.where(cand > close[:, None], cand, np.inf).min(axis=1)
        below = np.where(cand < close[:, None], cand, -np.inf).max(axis=1)
        lvl_above = np.minimum(lvl_above, above)
        lvl_below = np.maximum(lvl_below, below)
        feats[f"lastrange_{stf}_dist_high_atr"] = (lb[:, 0] - close) / a
        feats[f"lastrange_{stf}_dist_low_atr"] = (lb[:, 1] - close) / a
        feats[f"lastrange_{stf}_dist_poc_atr"] = (lb[:, 2] - close) / a
        feats[f"lastrange_{stf}_in_value"] = ((close >= lb[:, 4]) & (close <= lb[:, 3])).astype(float)
        # Fibonacci: exec TF only 0.618 (zone 0.618-0.65); higher TFs 0.382/0.5/0.618/0.786; last 3 legs (stacking)
        legs = S["legs"][np.clip(pos, 0, None)].copy(); legs[pos < 0] = np.nan
        ratios = lv.FIB_EXEC if stf == tf else lv.FIB_HTF
        fl = np.stack([lv.fib_retrace(legs[:, g, 0], legs[:, g, 1], r) for g in range(legs.shape[1]) for r in ratios], axis=1)
        levels.append(fl)
        type_hit["fib"] |= within(fl)
        last_leg = [lv.fib_retrace(legs[:, 0, 0], legs[:, 0, 1], r) for r in ratios]
        dl = np.stack([np.abs(x - close) / a for x in last_leg], axis=1)
        dl_f = np.where(np.isnan(dl), np.inf, dl)
        jj = dl_f.argmin(axis=1)
        dmin = dl_f[rows, jj]
        better = dmin < near_fib
        near_fib = np.where(better, dmin, near_fib)
        near_fib_lvl = np.where(better, np.array(ratios)[jj], near_fib_lvl)
        near_fib_tf = np.where(better, STRUCTURE_TFS[stf], near_fib_tf)
        if stf == tf:
            z0 = lv.fib_retrace(legs[:, 0, 0], legs[:, 0, 1], lv.FIB_EXEC_ZONE[0])
            z1 = lv.fib_retrace(legs[:, 0, 0], legs[:, 0, 1], lv.FIB_EXEC_ZONE[1])
            feats["fib_exec_in_0618_zone"] = ((close >= np.fmin(z0, z1)) & (close <= np.fmax(z0, z1))).astype(float)
            feats["leg_a"], feats["leg_b"] = legs[:, 0, 0], legs[:, 0, 1]
            feats["leg_dir"] = np.sign(legs[:, 0, 1] - legs[:, 0, 0])
            # most recent confirmed up-leg and down-leg (swings alternate, so they are legs 0 and 1 in some order)
            up0 = legs[:, 0, 1] > legs[:, 0, 0]
            for nm, sel in (("up", up0), ("down", ~up0)):
                feats[f"{nm}leg_a"] = np.where(sel, legs[:, 0, 0], legs[:, 1, 0])
                feats[f"{nm}leg_b"] = np.where(sel, legs[:, 0, 1], legs[:, 1, 1])
        # confluence: levels of this TF within band of the execution close
        L = np.concatenate(levels, axis=1)
        hit = (np.abs(L - close[:, None]) <= band[:, None]).sum(axis=1)
        conf_count += hit
        conf_top_tf = np.where(hit > 0, STRUCTURE_TFS[stf], conf_top_tf)
        # flip events of this TF, mapped to the first execution bar whose close is at or after the event's close
        ev = S["events"]
        if len(ev):
            ev = ev.copy()
            ev["exec_bar"] = np.searchsorted((idx + cm * MIN).as_unit("ns").asi8, ev["known_at"].dt.as_unit("ns").astype("int64").to_numpy(), side="left")
            ev = ev[ev["exec_bar"] < len(idx)]
            ev["exec_time"] = idx[ev["exec_bar"].to_numpy()]
            all_events.append(ev)
    # previous UTC day profile (usable from the next day's open) and previous day/week high-low
    d1 = load_bars(sym, "1D", scope)
    a1d = pd.Series(ta.atr(d1["high"], d1["low"], d1["close"], 14), index=d1.index)
    pdp = prev_day_profiles(m1, a1d)
    pos_d = _align_pos(pdp.index, 1440, idx, cm)
    pd_atr = _take(a1d.reindex(pdp.index).to_numpy(), pos_d)
    for c in ("poc", "vah", "val"):
        v = _take(pdp[c].to_numpy(), pos_d)
        feats[f"pdp_{c}_dist_atr"] = (v - close) / pd_atr
        conf_count += (np.abs(v - close) <= band)
        type_hit["profile"] |= (np.abs(v - close) <= band)
        conf_top_tf = np.where((np.abs(v - close) <= band) & (conf_top_tf < 1440), 1440, conf_top_tf)
    vah, val = _take(pdp["vah"].to_numpy(), pos_d), _take(pdp["val"].to_numpy(), pos_d)
    feats["pdp_in_value"] = ((close >= val) & (close <= vah)).astype(float)
    w1 = load_bars(sym, "1W", scope)
    for name, b, m in (("pd", d1, 1440), ("pw", w1, 10080)):
        ps = _align_pos(b.index, m, idx, cm)
        ab = _take(ta.atr(b["high"], b["low"], b["close"], 14), ps)
        feats[f"{name}_high_dist_atr"] = (_take(b["high"].to_numpy(), ps) - close) / ab
        feats[f"{name}_low_dist_atr"] = (_take(b["low"].to_numpy(), ps) - close) / ab
    feats["confluence_count"] = conf_count
    feats["confluence_types"] = sum(type_hit[t].astype(float) for t in type_hit)
    feats["next_level_above"] = np.where(np.isinf(lvl_above), np.nan, lvl_above)
    feats["next_level_below"] = np.where(np.isinf(lvl_below), np.nan, lvl_below)
    feats["confluence_top_tf_min"] = conf_top_tf
    feats["fib_nearest_dist_atr"] = np.where(np.isinf(near_fib), np.nan, near_fib)
    feats["fib_nearest_level"] = near_fib_lvl
    feats["fib_nearest_tf_min"] = near_fib_tf
    out = pd.DataFrame(feats, index=idx)
    events = pd.concat(all_events, ignore_index=True) if all_events else pd.DataFrame()
    if out_scope != scope:
        out = clip_scope(out, tf, out_scope)
        if len(events):
            events = events[events["exec_time"].isin(out.index)].copy()
            events["exec_bar"] = out.index.get_indexer(events["exec_time"])
    return out, events
