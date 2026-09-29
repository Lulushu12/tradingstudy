"""Stage-3b: exit optimisation with a PROP-FIRM objective.

For each exit config we pool all symbols' IS trades and compute:
- msr: monthly Sharpe of the R stream = mean(R)/std(R) * sqrt(trades per month)
  (with fixed risk per trade, expected monthly return / monthly volatility; this is what decides how
   much you can risk without breaching a 6% static drawdown)
- robust sum: sum R after removing the best 1% of trades (must stay positive)
- long and short averages separately
- win rate
Selection uses IS only; OOS is reported alongside for verification.
"""
import numpy as np
import pandas as pd

from data import SYMBOLS, IS_END
from engine import simulate, FEE, SLIP
from lab import ctx
from stage3 import get_signal, exit_grid

IS_MONTHS, OOS_MONTHS = 48.0, 21.0


def metrics(r, d, months):
    if len(r) < 20:
        return dict(n=len(r), avg=np.nan, msr=np.nan, rob=np.nan, wr=np.nan, L=np.nan, S=np.nan, tpm=0)
    srt = np.sort(r)[::-1]
    k = max(1, len(r) // 100)
    tpm = len(r) / months
    sd = r.std()
    return dict(n=len(r), avg=r.mean(), msr=r.mean() / sd * np.sqrt(tpm) if sd > 0 else np.nan,
                rob=srt[k:].sum(), wr=(r > 0).mean(), L=r[d == 1].mean() if (d == 1).any() else np.nan,
                S=r[d == -1].mean() if (d == -1).any() else np.nan, tpm=tpm)


def eval_exits_robust(family, variant, htf, bias, tf="15m", syms=SYMBOLS, grid=None, sig_fn=None):
    """sig_fn(cx) -> (sig, sl) overrides the library lookup (for custom / baseline signals)."""
    per = {}
    for sym in syms:
        cx = ctx(sym, tf)
        if sig_fn is None:
            s, sl = get_signal(cx, family, variant, htf, bias)
        else:
            s, sl = sig_fn(cx)
        cut = np.searchsorted(cx.df.index.values, IS_END.to_datetime64())
        for j, ex in enumerate(grid or exit_grid()):
            if sl is not None and ex["sl_atr"] != 1.0:
                continue
            sd = np.maximum(sl, 0.5 * cx.atr) if sl is not None else ex["sl_atr"] * cx.atr
            tr = simulate(cx.o, cx.h, cx.l, cx.c, cx.h1, cx.l1, cx.mm, s, sd, cx.atr, cx.c,
                          ex["tp_r"], ex["be_r"], ex["trail"], ex["trail_mult"], ex["max_bars"], False,
                          0.0, 0.0, FEE, SLIP)
            eb = tr[:, 0].astype(int) + 1
            per.setdefault(j, (ex, []))[1].append((eb < cut, tr[:, 6], tr[:, 2]))
    rows = []
    for j, (ex, parts) in per.items():
        isb = np.concatenate([p[0] for p in parts]); r = np.concatenate([p[1] for p in parts])
        d = np.concatenate([p[2] for p in parts])
        mi = metrics(r[isb], d[isb], IS_MONTHS)
        mo = metrics(r[~isb], d[~isb], OOS_MONTHS)
        rows.append({**ex, **{f"is_{k}": v for k, v in mi.items()}, **{f"oos_{k}": v for k, v in mo.items()}})
    return pd.DataFrame(rows).sort_values("is_msr", ascending=False)
