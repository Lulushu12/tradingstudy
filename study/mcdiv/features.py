"""Per-signal feature extraction: trigger values, anchor-wave values, and
higher-timeframe wave context.

Conventions:
- All oscillator features are recorded raw AND as "extremity" = -direction *
  value, so bull and bear setups pool onto one scale (bigger = deeper in the
  setup's favor: an oversold trough for longs, an overbought peak for shorts).
- HTF context is taken from the last CLOSED 1h/4H bar as of the 15m signal
  bar's close (strictly causal).
- HTF "wave" = the most recent CONFIRMED 5-bar fractal pivot of the HTF
  oscillator (confirmed = pivot + 2 HTF bars closed by signal time).
"""
import numpy as np
import pandas as pd
from divergence import _fractals


def htf_context(df15, dfh, prefix):
    """For each 15m bar, index of last closed HTF bar and last confirmed
    HTF wt2/mfi fractal pivots. Returns a DataFrame aligned to df15."""
    step = int(dfh["ts"].diff().median())
    close_ts = dfh["ts"].to_numpy() + step          # HTF bar close time
    sig_close = df15["ts"].to_numpy() + 900          # 15m bar close time
    # last HTF bar whose close <= 15m close
    idx = np.searchsorted(close_ts, sig_close, side="right") - 1

    out = pd.DataFrame(index=df15.index)
    for col in ("wt1", "wt2", "mfi"):
        v = dfh[col].to_numpy(float)
        out[f"{prefix}_{col}"] = np.where(idx >= 0, v[np.clip(idx, 0, None)], np.nan)
    # HTF trend regime: last closed HTF close vs its EMA200 (+1 up / -1 down)
    ema200 = dfh["close"].ewm(span=200, adjust=False).mean().to_numpy(float)
    trend = np.sign(dfh["close"].to_numpy(float) - ema200)
    out[f"{prefix}_trend"] = np.where(idx >= 0, trend[np.clip(idx, 0, None)], np.nan)

    for osc in ("wt2", "mfi"):
        v = dfh[osc].to_numpy(float)
        top, bot = _fractals(v)
        piv = np.where(top | bot)[0]
        side = np.where(top, -1, np.where(bot, +1, 0))
        conf_ts = close_ts[np.clip(piv + 2, 0, len(dfh) - 1)]  # confirm close time
        j = np.searchsorted(conf_ts, sig_close, side="right") - 1
        val = np.full(len(df15), np.nan)
        wside = np.full(len(df15), np.nan)
        age = np.full(len(df15), np.nan)
        ok = j >= 0
        pj = piv[np.clip(j, 0, None)]
        val[ok] = v[pj[ok]]
        wside[ok] = side[pj[ok]]
        age[ok] = idx[ok] - pj[ok]
        out[f"{prefix}_{osc}_wave"] = val
        out[f"{prefix}_{osc}_wave_side"] = wside
        out[f"{prefix}_{osc}_wave_age"] = age
    return out


def build_features(df15, signals, *htf_ctxs):
    wt1 = df15["wt1"].to_numpy(float)
    wt2 = df15["wt2"].to_numpy(float)
    mfi = df15["mfi"].to_numpy(float)
    close = df15["close"].to_numpy(float)
    atrp = (df15["atr14"] / df15["close"]).to_numpy(float)
    rows = []
    for s in signals:
        t = s.signal_i
        d = s.direction
        r = dict(system=s.system, direction=d, signal_i=t, dt=df15["dt"].iloc[t],
                 leg1=s.leg1_osc, gap_bars=s.gap_bars,
                 trig_wt1=wt1[t], trig_wt2=wt2[t], trig_mfi=mfi[t],
                 atr_pct=atrp[t])
        for name, ev in (("wt", s.wt_ev), ("mfi", s.mfi_ev)):
            if ev is not None:
                r[f"{name}_pivot_osc"] = ev.pivot_osc
                r[f"{name}_anchor_osc"] = ev.ref_osc
                r[f"{name}_div_osc_delta"] = ev.pivot_osc - ev.ref_osc
                r[f"{name}_div_price_pct"] = (ev.pivot_price - ev.ref_price) / ev.ref_price * 100
                r[f"{name}_pivot_age"] = t - ev.pivot_i
                r[f"{name}_anchor_age"] = t - ev.ref_i
                if name == "wt":
                    r["wt_tier"] = ev.tier
        if s.frontrun:
            other = "mfi" if s.leg1_osc == "wt" else "wt"
            osc_now = mfi[t] if other == "mfi" else wt2[t]
            r[f"{other}_pivot_osc"] = osc_now           # front-run turn value
            r[f"{other}_anchor_osc"] = s.fr_ref_osc
            r[f"{other}_div_osc_delta"] = osc_now - s.fr_ref_osc
            r[f"{other}_anchor_age"] = t - s.fr_ref_i
        rows.append(r)
    f = pd.DataFrame(rows)
    prefixes = []
    for ctx in htf_ctxs:
        prefixes.append(ctx.columns[0].split("_")[0])
        f = f.join(ctx.iloc[f["signal_i"].to_numpy()].reset_index(drop=True))

    d = f["direction"].to_numpy()
    cols = ["trig_wt1", "trig_wt2", "trig_mfi",
            "wt_pivot_osc", "wt_anchor_osc", "mfi_pivot_osc", "mfi_anchor_osc"]
    for p in prefixes:
        cols += [f"{p}_wt2", f"{p}_mfi", f"{p}_wt2_wave", f"{p}_mfi_wave"]
    for col in cols:
        if col in f:
            f["x_" + col] = -d * f[col].to_numpy(float)
    for p in prefixes:
        # last HTF wave on the trade's side? trend regime aligned with trade?
        for osc in ("wt2", "mfi"):
            f[f"{p}_{osc}_wave_aligned"] = (f[f"{p}_{osc}_wave_side"] == d).astype(float)
        f[f"{p}_trend_aligned"] = (f[f"{p}_trend"] == d).astype(float)
    return f
