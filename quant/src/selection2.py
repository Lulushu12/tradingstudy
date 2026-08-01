"""Correctly specified null for the divergence-exit search.

selection.py block-shuffled the R series. That is the wrong null here: shuffling
destroys loss clustering, real markets cluster losses, and the score depends on
1/maxDrawdown - so a shuffled path has an artificially small drawdown and an
artificially high score. It produced a null mean of 1.58%/mo against an observed
0.685%, which says the SCORE is dominated by drawdown-path luck, not that the
rule is worthless.

The right null leaves the market, the trades and the drawdown structure exactly
as they are, and destroys only the thing under test: the alignment between
divergence timing and trade outcome. Divergence and red-dot event timestamps are
shifted by a random offset of weeks. Everything else is identical, including the
number of configurations searched.

If the real search beats this null, the divergence rule carries information. If
not, the timing of the divergences is irrelevant and any tightening rule with
similar statistics would do as well.
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
LTFS = ["5min", "15min", "30min"]
MODES = {"TIGHTEN": 1, "SEQ_TIGHT": 5, "PARTIAL_TIGHT": 7}
BUFS = [0.0, 0.05, 0.15]


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


def run_search(shift_days=0.0, rng=None):
    """Full (ltf, mode, buffer) search. shift_days != 0 displaces the MCB event
    timestamps, breaking their alignment with price while preserving everything
    else."""
    cells = {}
    for ltf in LTFS:
        for sym in RM.CORE:
            try:
                sig, m1 = RM.htf_signals(sym, "4h")
                ev = RE.ltf_events(sym, ltf)
            except Exception:                    # noqa: BLE001
                continue
            for side in (1, -1):
                ss = sig[sig.side == side]
                if not len(ss):
                    continue
                e = ev[side]
                dd_, dl_, dot_ = e["div_dt"], e["div_lvl"], e["dot_dt"]
                if shift_days:
                    off = pd.Timedelta(days=float(rng.uniform(7, shift_days)))
                    sgn = 1 if rng.random() < 0.5 else -1
                    dd_ = dd_ + sgn * off
                    dot_ = dot_ + sgn * off
                for mname, code in MODES.items():
                    for buf in BUFS:
                        d = X.run(ss, m1, dd_, dl_, dot_, mode=code,
                                  buf_frac=buf)
                        if len(d):
                            cells.setdefault((ltf, mname, buf), []).append(d)
    out = {}
    for k, v in cells.items():
        T = pd.concat(v).sort_values("close_dt").reset_index(drop=True)
        m = ((pd.Timestamp(T.close_dt.max())
              - pd.Timestamp(T.close_dt.min())).days / 30.44)
        out[k] = (score(T["r"].values, m), float(T["r"].mean()),
                  float(T.loc[T.r < 0, "r"].mean()) if (T.r < 0).any() else np.nan)
    return out


def main(n_perm=60, seed=1):
    real = run_search()
    rs = pd.Series({k: v[0] for k, v in real.items()}).dropna().sort_values(
        ascending=False)
    best_key = rs.index[0]
    print(f"configurations: {len(rs)}")
    print(f"best observed: {best_key} -> {100*rs.iloc[0]:.3f}%/mo  "
          f"(expR {real[best_key][1]:+.4f}, avg loss {real[best_key][2]:+.3f})")

    rng = np.random.default_rng(seed)
    best_null, loss_null = [], []
    for i in range(n_perm):
        r = run_search(shift_days=90.0, rng=rng)
        v = pd.Series({k: x[0] for k, x in r.items()}).dropna()
        if len(v):
            best_null.append(v.max())
            k2 = v.idxmax()
            loss_null.append(r[k2][2])
    bn = np.array(best_null)
    print(f"\nnull: MCB event times shifted 7-90 days ({n_perm} draws)")
    print(f"  best-of-search under null: mean {100*bn.mean():.3f}%  "
          f"p95 {100*np.percentile(bn,95):.3f}%  max {100*bn.max():.3f}%")
    print(f"  avg loss of the null winners: {np.nanmean(loss_null):+.3f} "
          f"(real: {real[best_key][2]:+.3f})")
    obs = rs.iloc[0]
    p = float((bn >= obs).mean())
    print(f"\n  observed {100*obs:.3f}%/mo   p = {p:.3f}")
    print(f"  verdict: {'divergence timing CARRIES information' if p < 0.05 else 'divergence timing adds nothing beyond a generic tighter stop'}")
    pd.DataFrame({"null_best": bn}).to_csv(
        os.path.join(REP, "selection2_null.csv"), index=False)


if __name__ == "__main__":
    main()
