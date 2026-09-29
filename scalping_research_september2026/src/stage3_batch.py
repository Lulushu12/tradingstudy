"""Batch stage-3: IS-only candidate selection from the gross-edge scan, robust exit optimisation,
OOS reported for verification only.

Memory-safe layout: one task per SYMBOL (a worker only ever holds one symbol), returning per
(candidate, exit) sufficient statistics that are pooled in the parent. The robust "sum minus best 1%"
is exact because each symbol ships its top 6% trades (the pooled top 1% can't need more)."""
import sys
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp

import numpy as np
import pandas as pd

from data import SYMBOLS

MAX_H = {"5m": 96, "15m": 96}
IS_MONTHS, OOS_MONTHS = 48.0, 21.0


def select_candidates(tf, top=60):
    from edge_agg import pooled
    a = pooled(tf)
    a = a[(a.H <= MAX_H[tf]) & (a.is_mean > 0.12) & (a.is_t > 3) & (a.is_pos >= a.n_sym - 1) & (a.n_sym >= 6)]
    a = a.sort_values("is_t", ascending=False)
    a = a.drop_duplicates(["family", "variant", "htf", "bias"])
    a = a.groupby(["family", "variant"]).head(3)
    hd = a[a.family.str.startswith("hour_drift")].head(6)
    a = pd.concat([a[~a.family.str.startswith("hour_drift")], hd]).sort_values("is_t", ascending=False)
    return a.head(top)


N_MONTHS = 12 * 7  # 2020-01 .. 2026-12
TOPK = 96
# compact layout: [n, s, q, w, nl, sl, ns, ss] + top[TOPK] + mon[N_MONTHS]
VLEN = 8 + TOPK + N_MONTHS


def bar_months(cx):
    idx = cx.df.index
    return ((idx.year - 2020) * 12 + idx.month - 1).values.astype(np.int64)


def _suff(r, d, mon=None):
    """Compact sufficient stats as one float32 vector. `mon` = month index of each trade's entry so
    the pooled result can compute a TRUE monthly Sharpe (correlated trades land in the same month).
    The pooled "sum minus best 1%" is exact as long as the pooled top-1% count <= TOPK per symbol."""
    v = np.full(VLEN, np.nan, np.float32)
    v[0] = len(r); v[1] = r.sum(); v[2] = (r ** 2).sum(); v[3] = (r > 0).sum()
    v[4] = (d == 1).sum(); v[5] = r[d == 1].sum(); v[6] = (d == -1).sum(); v[7] = r[d == -1].sum()
    top = np.sort(r)[::-1][:TOPK]
    v[8:8 + len(top)] = top
    v[8 + TOPK:] = 0.0
    if mon is not None and len(r):
        v[8 + TOPK:] = np.bincount(mon, weights=r, minlength=N_MONTHS)[:N_MONTHS]
    return v


def pool_stats(parts, months):
    P = np.vstack(parts).astype(np.float64)
    n = P[:, 0].sum()
    if n < 20:
        return dict(n=n)
    s, q = P[:, 1].sum(), P[:, 2].sum()
    m = s / n; sd = np.sqrt(max(q / n - m * m, 1e-12)); tpm = n / months
    top = P[:, 8:8 + TOPK].ravel()
    top = np.sort(top[~np.isnan(top)])[::-1][:max(1, int(n) // 100)]
    nl, ns = P[:, 4].sum(), P[:, 6].sum()
    mm = P[:, 8 + TOPK:].sum(axis=0)
    nz = np.nonzero(mm)[0]
    mm = mm[nz.min():nz.max() + 1] if len(nz) else mm
    return dict(n=n, avg=m, msr=m / sd * np.sqrt(tpm), rob=s - top.sum(), wr=P[:, 3].sum() / n,
                L=P[:, 5].sum() / max(nl, 1), S=P[:, 7].sum() / max(ns, 1), tpm=tpm,
                pos=int((P[:, 1] > 0).sum()), true_msr=mm.mean() / mm.std() if mm.std() > 0 else np.nan,
                worst_m=mm.min(), pos_m=(mm > 0).mean(), avg_m=mm.mean())


def sym_task(args):
    sym, tf, cands = args
    from engine import simulate, FEE, SLIP
    from lab import ctx
    from stage3 import get_signal, exit_grid
    from data import IS_END
    cx = ctx(sym, tf)
    cut = np.searchsorted(cx.df.index.values, IS_END.to_datetime64())
    bm = bar_months(cx)
    out = []
    for ci, (family, variant, htf, bias) in enumerate(cands):
        try:
            s, sl = get_signal(cx, family, variant, htf, bias)
        except Exception as e:
            print("signal error", sym, family, variant, e, flush=True)
            continue
        for ex in exit_grid():
            if sl is not None and ex["sl_atr"] != 1.0:
                continue
            sd = np.maximum(sl, 0.5 * cx.atr) if sl is not None else ex["sl_atr"] * cx.atr
            tr = simulate(cx.o, cx.h, cx.l, cx.c, cx.h1, cx.l1, cx.mm, s, sd, cx.atr, cx.c,
                          ex["tp_r"], ex["be_r"], ex["trail"], ex["trail_mult"], ex["max_bars"], False,
                          0.0, 0.0, FEE, SLIP)
            eb = tr[:, 0].astype(int) + 1
            isb = eb < cut
            r, d, mo = tr[:, 6], tr[:, 2], bm[eb]
            out.append((ci, tuple(ex.items()), _suff(r[isb], d[isb], mo[isb]), _suff(r[~isb], d[~isb], mo[~isb])))
        cx.cache.pop(("sig", family, variant, htf, bias), None)
    print("symbol done", sym, tf, flush=True)
    return sym, out


def run_batch(tf, cands_df, workers=3, tag=""):
    cands = [(r.family, r.variant, r.htf, r.bias) for r in cands_df.itertuples()]
    acc = {}
    with ProcessPoolExecutor(workers, mp_context=mp.get_context("spawn")) as ex:
        for sym, out in ex.map(sym_task, [(s, tf, cands) for s in SYMBOLS]):
            for ci, exk, a, b in out:
                acc.setdefault((ci, exk), ([], []))
                acc[(ci, exk)][0].append(a)
                acc[(ci, exk)][1].append(b)
    rows = []
    for (ci, exk), (a, b) in acc.items():
        fam, var, htf, bias = cands[ci]
        pi, po = pool_stats(a, IS_MONTHS), pool_stats(b, OOS_MONTHS)
        rows.append(dict(tf=tf, family=fam, variant=var, htf=htf, bias=bias, **dict(exk),
                         **{f"is_{k}": v for k, v in pi.items()}, **{f"oos_{k}": v for k, v in po.items()}))
    res = pd.DataFrame(rows)
    res.to_parquet(f"../results/stage3_batch_{tf}{tag}.parquet")
    return res


if __name__ == "__main__":
    tf = sys.argv[1]
    cands = select_candidates(tf)
    print(f"{tf}: {len(cands)} candidates", flush=True)
    res = run_batch(tf, cands)
    print("saved", len(res), flush=True)
