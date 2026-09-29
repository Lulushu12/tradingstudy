"""POST-HOC diagnostic (holdout already spent): did the whole Asia-fade plateau decay in the holdout,
or only the chosen config? NOT used for selecting anything."""
import itertools
import numpy as np, pandas as pd
from data import SYMBOLS, OOS_END
from engine import simulate, FEE, SLIP
from lab import ctx
import features as fx
from asia_lab import asia_fade_signal, OR_MIN, WIN_H, TRENDS, SLS, BES, HOLD_H

rows = []
for sym in SYMBOLS:
    cx = ctx(sym, "15m")
    cut = np.searchsorted(cx.df.index.values, OOS_END.to_datetime64())
    for om, wh in itertools.product(OR_MIN, WIN_H):
        base = asia_fade_signal(cx, om, wh, include_holdout=True)
        base[:cut] = 0
        for htf, kind in TRENDS:
            s = base if htf == "none" else np.where(fx.htf_bias(cx, htf, kind).astype(np.int64) == base, base, 0)
            for sl, be, hh in itertools.product(SLS, BES, HOLD_H):
                tr = simulate(cx.o, cx.h, cx.l, cx.c, cx.h1, cx.l1, cx.mm, s, sl * cx.atr, cx.atr, cx.c,
                              0.0, be, 0, 0.0, hh * 4, False, 0.0, 0.0, FEE, SLIP)
                rows.append((sym, om, wh, htf, kind, sl, be, hh, len(tr), tr[:, 6].sum()))
    print("done", sym, flush=True)
d = pd.DataFrame(rows, columns=["sym", "or_min", "win_h", "htf", "bias", "sl_atr", "be_r", "hold_h", "n", "sumR"])
a = d.groupby(["or_min", "win_h", "htf", "bias", "sl_atr", "be_r", "hold_h"])[["n", "sumR"]].sum().reset_index()
a["avgR"] = a.sumR / a.n
a.to_parquet("../results/holdout_diag_asia.parquet")
print("configs:", len(a), " share with positive HOLDOUT avgR:", round((a.avgR > 0).mean(), 3), " median avgR:", round(a.avgR.median(), 3))
for k in ["or_min", "htf", "sl_atr", "be_r", "hold_h"]:
    print(a.groupby(k).avgR.mean().round(3).to_string()); print()
