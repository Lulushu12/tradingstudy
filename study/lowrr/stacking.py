"""Should overlapping signals be stacked, or collapsed to one position?

Fair challenge: each signal IS a separate event, so why throw any away? Two
different questions hide inside that, and they have different answers.

  MEASUREMENT: overlapping trades are not independent observations. Five entries
  fired on five consecutive bars that all resolve inside the same 12 hours share
  one price path. They win together and lose together. Counting them as n=5
  shrinks the standard error by sqrt(5) for free, which is not a real gain in
  evidence. This is why every expectancy figure in this study is computed on the
  de-overlapped sequence.

  TRADING: stacking is a real technique and might well be correct. Staggered
  entries average your price and each later entry carries its own ATR stop. The
  question is empirical: does the Nth overlapping entry carry its own weight
  after costs, and what does stacking do to drawdown once you hold total risk
  constant rather than per-trade risk?

This script measures both. Nothing is de-overlapped here; stack depth is tagged
and everything is kept.
"""
import sys, os, pickle, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd
import indicators as ind
from lowrr import core
from lowrr.multiasset import (load_path_file, BN, RULES, RR_GRID, symbols,
                              MAJORS, SLIP_MAJOR, SLIP_ALT)
from lowrr.pooled_test import day_cluster_ci

HERE = os.path.dirname(os.path.abspath(__file__))
KEEP = ["S_bb_break_dn", "S_volspike18_dn"]

def build_raw(sym, am=1.5, start="2021-05-24"):
    """Every signal, nothing dropped, tagged with the stack depth at entry."""
    df = ind.enrich(pd.read_parquet(os.path.join(BN, f"{sym}_4h.parquet")))
    df = df[df["dt"] >= pd.Timestamp(start, tz="UTC")].reset_index(drop=True)
    path = load_path_file(os.path.join(BN, f"{sym}_15m.parquet"))
    slip = SLIP_MAJOR if sym in MAJORS else SLIP_ALT
    out = {}
    for name in KEEP:
        mask, side = RULES[name](df)
        mask = mask.fillna(False).values
        idx = np.where(mask)[0]
        idx = idx[idx < len(df) - 1]
        if len(idx) < 40:
            continue
        tr = core.trades_for_signals(df, idx, np.full(len(idx), side), am,
                                     RR_GRID, path, max_hold_days=50)
        if len(tr) == 0:
            continue
        tr["cost_R"] = core.cost_R(tr["stop_frac"].values, tr["nights"].values,
                                   slip_rt=2 * slip)
        tr["net_R"] = tr["gross_R"] - tr["cost_R"]
        tr["sym"] = sym
        for rr in RR_GRID:
            s = tr[tr["rr"] == rr].sort_values("entry_time").reset_index(drop=True)
            # stack depth: how many same-symbol trades are still open at entry
            depth = np.zeros(len(s), dtype=int)
            ex = s["exit_time"].values; en = s["entry_time"].values
            for i in range(len(s)):
                depth[i] = int(np.sum(ex[:i] > en[i]))
            s["depth"] = depth
            # group id: a fresh entry (depth 0) starts a new cluster
            s["cluster"] = (s["depth"] == 0).cumsum()
            out[(name, rr)] = s
    return out

def depth_table(store, rule, rr):
    tr = pd.concat([d[(rule, rr)] for d in store.values() if (rule, rr) in d],
                   ignore_index=True)
    print(f"\n--- {rule} rr={rr}: does the Nth overlapping entry pay? ---")
    print(f"{'depth':>6}{'n':>7}{'share':>7}{'WR':>7}{'expR':>8}{'grossR':>8}"
          f"{'costR':>7}{'cum expR':>10}")
    for d in range(0, 6):
        s = tr[tr["depth"] == d] if d < 5 else tr[tr["depth"] >= 5]
        if len(s) < 30:
            continue
        cum = tr[tr["depth"] <= d]
        lab = f"{d}" if d < 5 else "5+"
        print(f"{lab:>6}{len(s):>7}{len(s)/len(tr):>7.1%}"
              f"{(s['res']==1).sum()/max((s['res']!=0).sum(),1):>7.1%}"
              f"{s['net_R'].mean():>+8.3f}{s['gross_R'].mean():>+8.3f}"
              f"{s['cost_R'].mean():>7.3f}{cum['net_R'].mean():>+10.3f}")
    return tr

def cluster_correlation(tr):
    """How alike are the outcomes of trades stacked on the same instrument?"""
    g = tr.groupby(["sym", "cluster"])["res"]
    sizes = g.size()
    multi = sizes[sizes > 1]
    if len(multi) == 0:
        return np.nan, np.nan, 0
    # fraction of multi-trade clusters where every trade agreed (all win/all lose)
    agree = g.apply(lambda x: (x == x.iloc[0]).all())
    agree = agree[sizes > 1]
    return agree.mean(), multi.mean(), len(multi)

def stacked_portfolio(store, rule, rr, risk, max_per_sym, max_conc=4):
    frames = [d[(rule, rr)] for d in store.values() if (rule, rr) in d]
    tr = pd.concat(frames, ignore_index=True).sort_values("entry_time")
    tr = tr.reset_index(drop=True)
    open_pos = []
    taken = []
    for r in tr.itertuples():
        open_pos = [p for p in open_pos if p[0] > r.entry_time]
        if len(open_pos) >= max_conc:
            continue
        if sum(1 for p in open_pos if p[1] == r.sym) >= max_per_sym:
            continue
        open_pos.append((r.exit_time, r.sym))
        taken.append(r)
    u = pd.DataFrame(taken).sort_values("exit_time").reset_index(drop=True)
    eq = 1.0; peak = 1.0; mdd = 0.0
    for x in u["net_R"].values:
        eq += risk * eq * x
        peak = max(peak, eq); mdd = min(mdd, (eq - peak) / peak)
    yrs = (u["exit_time"].iloc[-1] - u["exit_time"].iloc[0]) / (365.25 * 86400)
    daily = u.groupby(u["exit_time"] // 86400)["net_R"].sum() * risk
    return dict(n=len(u), tpm=len(u) / (yrs * 12), expR=u["net_R"].mean(),
                Rmo=u["net_R"].sum() / (yrs * 12), maxdd=mdd,
                cagr=eq ** (1 / yrs) - 1, worst_day=daily.min(),
                cdd=(eq ** (1 / yrs) - 1) / abs(mdd) if mdd else np.nan), u

def main():
    syms = symbols()
    store = {}
    for s in syms:
        store[s] = build_raw(s)
        print(f"  built {s}", flush=True)
    with open(os.path.join(HERE, "stack_store.pkl"), "wb") as f:
        pickle.dump(store, f)

    print("\n" + "=" * 78)
    print("1. MARGINAL VALUE OF A STACKED ENTRY")
    print("=" * 78)
    for rule in KEEP:
        for rr in [0.5, 1.0, 2.0]:
            tr = depth_table(store, rule, rr)
            a, sz, nc = cluster_correlation(tr)
            print(f"       overlapping clusters: {nc}, mean size {sz:.1f}, "
                  f"all trades in the cluster agreed (all win or all lose): {a:.1%}")

    print("\n" + "=" * 78)
    print("2. EVIDENCE INFLATION: what stacking does to the standard error")
    print("=" * 78)
    print(f"{'rule':<18}{'rr':>5}{'stacking':>10}{'n':>7}{'expR':>8}{'naiveSE':>9}"
          f"{'5day CI':>18}{'ratio':>7}")
    for rule in KEEP:
        for rr in [0.5, 1.0]:
            for mps, lab in [(99, "all"), (1, "de-overlap")]:
                frames = [d[(rule, rr)] for d in store.values() if (rule, rr) in d]
                tr = pd.concat(frames, ignore_index=True)
                if mps == 1:
                    tr = tr[tr["depth"] == 0]
                naive = tr["net_R"].std() / np.sqrt(len(tr))
                lo, hi, p = day_cluster_ci(tr, block_days=5)
                print(f"{rule:<18}{rr:>5.2f}{lab:>10}{len(tr):>7}"
                      f"{tr['net_R'].mean():>+8.3f}{naive:>9.4f}"
                      f"{f'{lo:+.3f} {hi:+.3f}':>18}{((hi-lo)/2)/naive:>7.1f}x",
                      flush=True)
    print("  ratio = clustered half-width / naive SE. How much the naive number")
    print("  overstates the evidence.")

    print("\n" + "=" * 78)
    print("3. TRADING IT: stacking at FIXED PER-TRADE risk (total risk floats up)")
    print("=" * 78)
    print(f"{'rule':<18}{'rr':>5}{'max/sym':>8}{'n':>6}{'t/mo':>6}{'expR':>8}"
          f"{'R/mo':>7}{'CAGR':>7}{'maxDD':>8}{'worstDay':>9}{'CAGR/DD':>8}")
    for rule in KEEP:
        for rr in [0.5, 1.0, 2.0]:
            for mps in [1, 2, 3, 99]:
                m, _ = stacked_portfolio(store, rule, rr, 0.0025, mps)
                lab = "unlimited" if mps == 99 else str(mps)
                print(f"{rule:<18}{rr:>5.2f}{lab:>8}{m['n']:>6}{m['tpm']:>6.1f}"
                      f"{m['expR']:>+8.3f}{m['Rmo']:>+7.2f}{m['cagr']:>+7.1%}"
                      f"{m['maxdd']:>8.1%}{m['worst_day']:>+9.2%}{m['cdd']:>8.2f}")
            print()

    print("=" * 78)
    print("4. TRADING IT: stacking at FIXED TOTAL risk (per-trade risk divided)")
    print("=" * 78)
    print("   the honest comparison. A 3-deep stack at 0.25% each is not three 1R")
    print("   bets, it is one 3R bet with staggered entries, so it is compared")
    print("   against a single position of the same total size.")
    print(f"{'rule':<18}{'rr':>5}{'max/sym':>8}{'risk/trade':>11}{'n':>6}"
          f"{'CAGR':>7}{'maxDD':>8}{'worstDay':>9}{'CAGR/DD':>8}")
    for rule in KEEP:
        for rr in [0.5, 1.0, 2.0]:
            for mps in [1, 2, 3]:
                m, _ = stacked_portfolio(store, rule, rr, 0.0025 / mps, mps)
                print(f"{rule:<18}{rr:>5.2f}{mps:>8}{0.0025/mps:>11.3%}{m['n']:>6}"
                      f"{m['cagr']:>+7.1%}{m['maxdd']:>8.1%}{m['worst_day']:>+9.2%}"
                      f"{m['cdd']:>8.2f}")
            print()

if __name__ == "__main__":
    main()
