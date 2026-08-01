"""How much of the best result is selection?

By this point roughly a thousand configurations have been evaluated across the
project. The headline 0.68%/month was the best of many, chosen after looking.
Its own bootstrap already said the return improvement was not established
(P=0.761), and that bootstrap does not account for the searching.

This measures the search cost directly. The exit search is re-run on
block-SHUFFLED labels, so any structure linking a divergence to a subsequent
outcome is destroyed while the trade distribution, the autocorrelation and the
number of configurations tried are all preserved. The distribution of the
best-of-search statistic under that null is what a real finding must beat.
"""
import os
import sys
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exits as X         # noqa: E402
import run_exits as RE    # noqa: E402
import run_mtf as RM      # noqa: E402

REP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reports")
LTFS = ["5min", "15min", "30min", "1h"]
MODES = {"BASE": 0, "TIGHTEN": 1, "SEQ": 4, "SEQ_TIGHT": 5,
         "PARTIAL": 6, "PARTIAL_TIGHT": 7}
BUFS = [0.0, 0.05, 0.15]


def collect():
    """Real results for every (ltf, mode, buffer) cell."""
    out = {}
    for ltf in LTFS:
        for sym in RM.CORE:
            try:
                sig, m1 = RM.htf_signals(sym, "4h")
                ev = RE.ltf_events(sym, ltf)
            except Exception:                    # noqa: BLE001
                continue
            for mname, code in MODES.items():
                for buf in BUFS:
                    if code in (0,) and buf != BUFS[0]:
                        continue
                    key = (ltf, mname, buf)
                    for side in (1, -1):
                        ss = sig[sig.side == side]
                        if not len(ss):
                            continue
                        e = ev[side]
                        d = X.run(ss, m1, e["div_dt"], e["div_lvl"],
                                  e["dot_dt"], mode=code, buf_frac=buf)
                        if len(d):
                            out.setdefault(key, []).append(d)
    return {k: pd.concat(v).sort_values("close_dt").reset_index(drop=True)
            for k, v in out.items()}


def score(r, months):
    r = np.asarray(r, float)
    r = r[np.isfinite(r)]
    if len(r) < 50:
        return np.nan
    cum = np.cumsum(r)
    dd = float(np.max(np.maximum.accumulate(cum) - cum))
    if dd <= 0:
        return np.nan
    return min(0.06 / dd, 0.02) * (r.sum() / months)


def main(n_perm=200, block=40, seed=0):
    cells = collect()
    print(f"configurations evaluated: {len(cells)}")
    months = {}
    real = {}
    for k, T in cells.items():
        m = ((pd.Timestamp(T.close_dt.max())
              - pd.Timestamp(T.close_dt.min())).days / 30.44)
        months[k] = m
        real[k] = score(T["r"].values, m)
    real_s = pd.Series(real).dropna().sort_values(ascending=False)
    print(f"\nbest observed: {real_s.index[0]} -> {100*real_s.iloc[0]:.3f}%/mo")
    print(f"baseline BASE cells: "
          + ", ".join(f"{100*v:.3f}%" for k, v in real_s.items()
                      if k[1] == 'BASE'))

    rng = np.random.default_rng(seed)
    best_null = []
    for _ in range(n_perm):
        vals = []
        for k, T in cells.items():
            r = T["r"].values
            n = len(r)
            nb = int(np.ceil(n / block))
            st = rng.integers(0, max(n - block, 1), nb)
            idx = np.clip((st[:, None] + np.arange(block)).ravel()[:n], 0, n - 1)
            vals.append(score(r[idx], months[k]))
        v = np.array(vals, float)
        if np.isfinite(v).any():
            best_null.append(np.nanmax(v))
    bn = np.array(best_null)
    print(f"\npermutation null over the SAME search ({n_perm} shuffles):")
    print(f"  best-of-search under null: mean {100*bn.mean():.3f}%  "
          f"p50 {100*np.percentile(bn,50):.3f}%  "
          f"p95 {100*np.percentile(bn,95):.3f}%  "
          f"p99 {100*np.percentile(bn,99):.3f}%")
    obs = real_s.iloc[0]
    p = float((bn >= obs).mean())
    print(f"\n  observed best {100*obs:.3f}%/mo")
    print(f"  P(a search this wide produces this by chance) = {p:.3f}")
    print(f"  selection-adjusted verdict: "
          f"{'SURVIVES' if p < 0.05 else 'NOT distinguishable from search luck'}")
    pd.DataFrame({"null_best": bn}).to_csv(
        os.path.join(REP, "selection_null.csv"), index=False)
    return real_s, bn


if __name__ == "__main__":
    main()
