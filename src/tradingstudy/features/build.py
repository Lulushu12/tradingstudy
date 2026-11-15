"""Assemble the feature frame for one coin and one execution timeframe (dev scope by default).

Every column is known at the CLOSE of its bar. Event columns (divergences, dots, signals) are stamped on the bar
where they become known. Market-structure features (brief 5.6) are added by features.structure when available.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from tradingstudy.data.guard import clip_scope, load_bars, load_funding
from tradingstudy.data.resample import resample_1m
from tradingstudy.features import context, divergence, htf, mcb

EXEC_TFS = {"6m": 6, "15m": 15, "24m": 24, "1h": 60}
HTF_MULT = 10  # brief 5.2 HTF layer multiplier


def bars_any(sym: str, minutes: int, scope: str, m1: pd.DataFrame | None = None) -> pd.DataFrame:
    """Bars for any timeframe; project timeframes come from disk, others are resampled from 1m."""
    from tradingstudy.config import TIMEFRAMES
    for tf, m in TIMEFRAMES.items():
        if m == minutes:
            return load_bars(sym, tf, scope)
    m1 = load_bars(sym, "1m", scope) if m1 is None else m1
    return clip_scope(resample_1m(m1, minutes), f"{minutes}m", scope)


def build_features(sym: str, tf: str, scope: str = "dev", mf_div_kwargs: dict | None = None,
                   wt_div_kwargs: dict | None = None, warmup: bool = True) -> pd.DataFrame:
    """warmup=True (PROTOCOL section 1): compute on 'dev_warmup' data, return only dev rows."""
    out_scope = scope
    if scope == "dev" and warmup:
        scope = "dev_warmup"
    cm = EXEC_TFS[tf]
    bars = load_bars(sym, tf, scope)
    idx = bars.index
    wt = mcb.wavetrend(bars)
    mf = pd.Series(mcb.mf_pine_ha(bars, smooth=1), index=idx, name="mf")
    parts = [
        bars[["open", "high", "low", "close", "volume", "n_1m", "complete"]],
        wt, mcb.wt_signals(wt), mf.to_frame(),
        divergence.wt_dot_divergences(wt, bars, **(wt_div_kwargs or {})),
        divergence.pivot_divergences(mf.to_numpy(), bars, **(mf_div_kwargs or {})),
        context.cmf(bars).to_frame("cmf"),
        context.atr_regime(bars, cm),
        context.session(idx, cm),
    ]
    h10 = bars_any(sym, cm * HTF_MULT, scope)
    parts.append(htf.htf_layer(h10, cm * HTF_MULT, idx, cm))
    h1, h4, d1 = load_bars(sym, "1h", scope), load_bars(sym, "4h", scope), load_bars(sym, "1D", scope)
    for name, b, m in (("1h", h1, 60), ("4h", h4, 240), ("1d", d1, 1440)):
        if m > cm:
            parts.append(htf.align_htf(context.cmf(b).to_frame(f"cmf_{name}"), m, idx, cm))
    parts.append(context.trend_regimes(h4, d1, idx, cm))
    parts.append(context.funding_features(load_funding(sym, scope), idx, cm))
    out = pd.concat(parts, axis=1)
    # divergence references: convert bar positions to timestamps so trimming warm-up rows cannot misalign them
    for c in [c for c in out.columns if c.endswith("_ref")]:
        r = out[c].to_numpy()
        out[c] = pd.Series(pd.NaT, index=idx, dtype=idx.dtype).where(r < 0, idx[np.clip(r, 0, None)])
    if out_scope != scope:
        out = clip_scope(out, tf, out_scope)
    out.attrs.update(symbol=sym, tf=tf, chart_minutes=cm, scope=out_scope)
    return out
