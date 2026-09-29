"""Walk-forward step 2: quarterly re-selection using ONLY past months.

For each test quarter starting Jan 2022, rank all configs on the trailing `window` months and
equal-weight the top K (at most one config per signal family), then record the NEXT quarter's
monthly R. Stitching the quarters gives a fully out-of-sample monthly track record 2022-01 .. 2026-09.
"""
import sys
import itertools

import numpy as np
import pandas as pd

N_MONTHS = 81
FIRST_TEST = 24  # 2022-01
MONTHS = pd.period_range("2020-01", periods=N_MONTHS, freq="M")


def load(tfs):
    Ms, Ns = [], []
    for tf in tfs:
        M = pd.read_parquet(f"../results/wf_monthly_R_{tf}.parquet")
        N = pd.read_parquet(f"../results/wf_monthly_n_{tf}.parquet")
        M.index = pd.MultiIndex.from_tuples([(tf,) + k for k in M.index], names=["tf"] + list(M.index.names))
        N.index = M.index
        Ms.append(M); Ns.append(N)
    M = pd.concat(Ms); N = pd.concat(Ns)
    return M, N


def walk_forward(M, N, window=24, K=5, score="msr", min_tpm=6, one_per_family=True, rng=None):
    R = M.values.astype(np.float64)
    C = N.values.astype(np.float64)
    fam = M.index.get_level_values("family").values
    out = np.full(N_MONTHS, np.nan)
    picks = []
    for t in range(FIRST_TEST, N_MONTHS, 3):
        lo = max(0, t - window)
        tr = R[:, lo:t]
        n = C[:, lo:t].sum(axis=1)
        ok = n / (t - lo) >= min_tpm
        mu = tr.mean(axis=1)
        sd = tr.std(axis=1) + 1e-9
        half = (t - lo) // 2
        both = (tr[:, :half].sum(axis=1) > 0) & (tr[:, half:].sum(axis=1) > 0)
        if rng is not None:
            s = rng.random(len(mu))
            ok = ok
        elif score == "msr":
            s = mu / sd
        else:
            s = mu
        s = np.where(ok & (both | (rng is not None)), s, -np.inf)
        order = np.argsort(-s)
        chosen, seen = [], set()
        for i in order:
            if not np.isfinite(s[i]):
                break
            if one_per_family and fam[i] in seen:
                continue
            chosen.append(i); seen.add(fam[i])
            if len(chosen) == K:
                break
        te = slice(t, min(t + 3, N_MONTHS))
        if chosen:
            out[te] = R[chosen, te].mean(axis=0)
            picks.append((str(MONTHS[t]), [M.index[i] for i in chosen]))
        else:
            out[te] = 0.0
    return pd.Series(out[FIRST_TEST:], index=MONTHS[FIRST_TEST:]), picks


def summarize(s):
    last12 = s.iloc[-12:]
    yearly = s.groupby(s.index.year).sum()
    return dict(avg_m=s.mean(), msr=s.mean() / s.std() if s.std() > 0 else np.nan, pos=(s > 0).mean(),
                worst=s.min(), last12_sum=last12.sum(), last12_pos=(last12 > 0).mean(),
                **{f"y{y}": v for y, v in yearly.items()})


if __name__ == "__main__":
    tfs = sys.argv[1].split(",")
    M, N = load(tfs)
    print("universe:", len(M), "configs on", tfs, flush=True)
    rows = []
    for window, K, score in itertools.product([12, 24, 36], [1, 3, 5, 10], ["msr", "mean"]):
        s, _ = walk_forward(M, N, window, K, score)
        rows.append(dict(window=window, K=K, score=score, **summarize(s)))
    res = pd.DataFrame(rows)
    pd.set_option("display.width", 250, "display.max_columns", 30)
    print(res.round(2).to_string(index=False))
    rnd = [summarize(walk_forward(M, N, 24, 5, "msr", rng=np.random.default_rng(i))[0]) for i in range(20)]
    rnd = pd.DataFrame(rnd)
    print("\nRANDOM-pick baseline (24m window, K=5, 20 seeds): median avg_m %.2f, median msr %.2f, median last12 %.2f"
          % (rnd.avg_m.median(), rnd.msr.median(), rnd.last12_sum.median()))
    res.to_parquet(f"../results/wf_summary_{'_'.join(tfs)}.parquet")
