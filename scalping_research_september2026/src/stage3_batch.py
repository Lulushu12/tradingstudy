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


def _suff(r, d):
    k = max(1, int(np.ceil(len(r) * 0.06)))
    return dict(n=len(r), s=r.sum(), q=(r ** 2).sum(), w=int((r > 0).sum()),
                nl=int((d == 1).sum()), sl=r[d == 1].sum(), ns=int((d == -1).sum()), ss=r[d == -1].sum(),
                top=np.sort(r)[::-1][:k])


def sym_task(args):
    sym, tf, cands = args
    from engine import simulate, FEE, SLIP
    from lab import ctx
    from stage3 import get_signal, exit_grid
    from data import IS_END
    cx = ctx(sym, tf)
    cut = np.searchsorted(cx.df.index.values, IS_END.to_datetime64())
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
            isb = (tr[:, 0].astype(int) + 1) < cut
            r, d = tr[:, 6], tr[:, 2]
            out.append((ci, tuple(ex.items()), _suff(r[isb], d[isb]), _suff(r[~isb], d[~isb])))
        # free the cached signal to keep memory flat
        cx.cache.pop(("sig", family, variant, htf, bias), None)
    print("symbol done", sym, tf, flush=True)
    return sym, out


def pool_stats(parts, months):
    n = sum(p["n"] for p in parts)
    if n < 20:
        return dict(n=n)
    s = sum(p["s"] for p in parts); q = sum(p["q"] for p in parts)
    m = s / n; sd = np.sqrt(max(q / n - m * m, 1e-12)); tpm = n / months
    top = np.sort(np.concatenate([p["top"] for p in parts]))[::-1][:max(1, n // 100)]
    nl = sum(p["nl"] for p in parts); ns = sum(p["ns"] for p in parts)
    return dict(n=n, avg=m, msr=m / sd * np.sqrt(tpm), rob=s - top.sum(), wr=sum(p["w"] for p in parts) / n,
                L=sum(p["sl"] for p in parts) / max(nl, 1), S=sum(p["ss"] for p in parts) / max(ns, 1), tpm=tpm,
                pos=sum(1 for p in parts if p["s"] > 0))


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
