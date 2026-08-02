"""Is the pooled multi-asset edge real, or is it 12 copies of the same day?

Twelve crypto perps are not twelve independent experiments. They stop out
together. Pooling 7,792 trades and dividing by sqrt(7792) would produce a
standard error that is simply false.

Test used: bootstrap clustered on CALENDAR DAY. Resample days with replacement
and take every trade that entered on a resampled day, so all correlated
same-day trades travel together. A block variant resamples runs of 5
consecutive days as well, which additionally absorbs serial correlation across
days (a bad week, not just a bad day).

Also reported: the per-asset unconditional barrier baseline, so the winrate lift
attributed to the signal is measured against each instrument's own geometry
rather than against BTC's or against the theoretical fair line.
"""
import sys, os, pickle, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd
import indicators as ind
from lowrr import core
from lowrr.multiasset import load_path_file, BN, RR_GRID, portfolio

HERE = os.path.dirname(os.path.abspath(__file__))
RNG = np.random.default_rng(20260802)

def day_cluster_ci(tr, n_boot=4000, block_days=1, q=(2.5, 97.5)):
    """Bootstrap the mean of net_R, resampling whole days (or runs of days)."""
    day = (tr["entry_time"].values // 86400).astype(np.int64)
    order = np.argsort(day)
    day = day[order]
    val = tr["net_R"].values[order]
    udays, starts = np.unique(day, return_index=True)
    ends = np.append(starts[1:], len(day))
    nd = len(udays)
    if nd < 30:
        return (np.nan, np.nan, np.nan)
    nblocks = int(np.ceil(nd / block_days))
    means = np.empty(n_boot)
    for b in range(n_boot):
        picks = RNG.integers(0, nd, size=nblocks)
        idx = []
        for p in picks:
            for d in range(block_days):
                k = p + d
                if k < nd:
                    idx.append(np.arange(starts[k], ends[k]))
        if not idx:
            means[b] = np.nan; continue
        sel = np.concatenate(idx)
        means[b] = val[sel].mean()
    lo, hi = np.nanpercentile(means, q)
    p_neg = np.nanmean(means <= 0)
    return lo, hi, p_neg

def unconditional_per_asset(sym, am=1.5, start="2021-05-24"):
    """Barrier ladder on every bar of one instrument, its own 15m path."""
    df = ind.enrich(pd.read_parquet(os.path.join(BN, f"{sym}_4h.parquet")))
    df = df[df["dt"] >= pd.Timestamp(start, tz="UTC")].reset_index(drop=True)
    path = load_path_file(os.path.join(BN, f"{sym}_15m.parquet"))
    idx = np.arange(len(df) - 1)
    ok = np.isfinite(df["atr14"].values[idx]) & (df["atr14"].values[idx] > 0)
    idx = idx[ok]
    tr = core.trades_for_signals(df, np.concatenate([idx, idx]),
                                 np.concatenate([np.ones(len(idx)), -np.ones(len(idx))]),
                                 am, RR_GRID, path, max_hold_days=50)
    out = {}
    for rr in RR_GRID:
        s = tr[tr["rr"] == rr]
        out[rr] = (s["res"] == 1).sum() / (s["res"] != 0).sum()
    return out

def main():
    with open(os.path.join(HERE, "multiasset_store.pkl"), "rb") as f:
        store = pickle.load(f)
    syms = sorted(store)

    print("=== per-asset unconditional barrier winrate (own 15m path, 1.5xATR) ===")
    unc = {}
    for s in syms:
        unc[s] = unconditional_per_asset(s)
        print(f"  {s:<10} " + "  ".join(f"rr{rr}:{unc[s][rr]:.1%}" for rr in RR_GRID),
              flush=True)
    fair = {rr: 1 / (1 + rr) for rr in RR_GRID}
    print("  fair     " + "  ".join(f"rr{rr}:{fair[rr]:.1%}" for rr in RR_GRID))

    print("\n=== pooled edge, day-clustered bootstrap ===")
    print(f"{'rule':<18}{'rr':>5}{'n':>7}{'days':>6}{'WR':>7}{'uncond':>8}{'lift':>7}"
          f"{'expR':>8}{'naiveSE':>9}{'day CI':>18}{'5day CI':>18}{'P(<=0)':>8}")
    for rule in ["S_bb_break_dn", "L_bb_break_up", "S_volspike18_dn", "L_volspike18_up"]:
        for rr in [0.25, 0.5, 1.0, 2.0]:
            frames = [d[(rule, rr)] for d in store.values() if (rule, rr) in d]
            if not frames:
                continue
            tr = pd.concat(frames, ignore_index=True)
            res = (tr["res"] != 0).sum()
            wr = (tr["res"] == 1).sum() / res
            # sample-weighted unconditional baseline across the assets present
            w = tr.groupby("sym").size()
            base = sum(unc[s][rr] * n for s, n in w.items()) / w.sum()
            naive = tr["net_R"].std() / np.sqrt(len(tr))
            lo1, hi1, p1 = day_cluster_ci(tr, block_days=1)
            lo5, hi5, p5 = day_cluster_ci(tr, block_days=5)
            ndays = len(np.unique(tr["entry_time"].values // 86400))
            print(f"{rule:<18}{rr:>5.2f}{len(tr):>7}{ndays:>6}{wr:>7.1%}{base:>8.1%}"
                  f"{wr-base:>+7.1%}{tr['net_R'].mean():>+8.3f}{naive:>9.4f}"
                  f"{f'{lo1:+.3f} {hi1:+.3f}':>18}{f'{lo5:+.3f} {hi5:+.3f}':>18}"
                  f"{p5:>8.1%}", flush=True)

    print("\n=== concurrency-capped portfolio (max 4 open, 1 per symbol) ===")
    print(f"{'rule':<18}{'rr':>5}{'n':>6}{'t/mo':>6}{'expR':>8}{'R/mo':>7}"
          f"{'5day CI':>18}{'P(<=0)':>8}{'maxDD@0.25%':>12}{'CAGR/DD':>9}")
    for rule in ["S_bb_break_dn", "S_volspike18_dn"]:
        for rr in [0.25, 0.5, 1.0, 2.0]:
            out = portfolio(store, rule, rr, 0.0025)
            if out is None:
                continue
            m, u = out
            lo5, hi5, p5 = day_cluster_ci(u, block_days=5)
            print(f"{rule:<18}{rr:>5.2f}{m['n']:>6}{m['tpm']:>6.1f}{m['expR']:>+8.3f}"
                  f"{m['R_per_month']:>+7.2f}{f'{lo5:+.3f} {hi5:+.3f}':>18}{p5:>8.1%}"
                  f"{m['maxdd']:>12.1%}{m['cagr']/abs(m['maxdd']):>9.2f}", flush=True)

if __name__ == "__main__":
    main()
