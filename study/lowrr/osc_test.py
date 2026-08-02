"""Run the divergence stacks across the R:R ladder, with emphasis on 0.5:1.

Two settings:
  4H across 12 perps, resolved on each symbol's own 15m path. This is the
     high-timeframe / low-commission setting the question is about, and the 11
     non-BTC instruments are an out-of-sample check on anything BTC throws up.
  15m on BTC, resolved on the 5m path. This is the timeframe FROZEN_SPEC
     actually specifies, included so the comparison is not rigged toward the
     answer the study already prefers.

Two stop rules, both reported:
  atr    stop = 1.5 x ATR14, matching every other rule in this study so it is
         directly comparable
  spec   FROZEN_SPEC section 5: highest (close + 1*ATR14) over t-5..t-1 for
         shorts, mirrored for longs, signal bar excluded, plus the 0.6% minimum
         stop distance entry invalidation

See the scope warning at the top of lowrr/oscillators.py. The port is not
validated against TradingView and this is not the Gate 0 audit.
"""
import sys, os, warnings, itertools
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd
from lowrr import core, oscillators as osc
from lowrr.multiasset import load_path_file, BN, MAJORS, SLIP_MAJOR, SLIP_ALT, symbols
from lowrr.finalists_lowrr import nonoverlap
from lowrr.pooled_test import day_cluster_ci

HERE = os.path.dirname(os.path.abspath(__file__))
CUT = pd.Timestamp("2025-01-01", tz="UTC")
RR = [0.25, 0.5, 0.75, 1.0, 2.0]
VARIANTS = ["WT+MFI", "WT+RSI", "MFI+RSI", "WT_only", "MFI_only", "RSI_only",
            "DIAG_any_two"]

def build_symbol(sym, tf="4h", path_tf="15m", level_mode="primary", window=11,
                 start="2021-05-24"):
    df = pd.read_parquet(os.path.join(BN, f"{sym}_{tf}.parquet"))
    df = osc.build_osc(df)
    df = df[df["dt"] >= pd.Timestamp(start, tz="UTC")].reset_index(drop=True)
    path = load_path_file(os.path.join(BN, f"{sym}_{path_tf}.parquet"))
    slip = SLIP_MAJOR if sym in MAJORS else SLIP_ALT
    sets = osc.signal_sets(df, level_mode=level_mode, window=window)
    out = {}
    for name, (bull, bear) in sets.items():
        for stop_mode in ("atr", "spec"):
            idx = np.concatenate([bull, bear]) if len(bull) + len(bear) else np.array([], int)
            if len(idx) < 25:
                continue
            side = np.concatenate([np.ones(len(bull)), -np.ones(len(bear))])
            keep = idx < len(df) - 1
            idx, side = idx[keep], side[keep]
            if len(idx) < 25:
                continue
            order = np.argsort(idx)
            idx, side = idx[order], side[order]
            if stop_mode == "spec":
                sd = osc.spec_stop(df, side, idx)
                tr = core.trades_for_signals(df, idx, side, 1.0, RR, path,
                                             max_hold_days=50, stop_dist=sd,
                                             min_stop_frac=0.006)
            else:
                tr = core.trades_for_signals(df, idx, side, 1.5, RR, path,
                                             max_hold_days=50)
            if len(tr) == 0:
                continue
            tr["cost_R"] = core.cost_R(tr["stop_frac"].values, tr["nights"].values,
                                       slip_rt=2 * slip)
            tr["net_R"] = tr["gross_R"] - tr["cost_R"]
            tr["sym"] = sym
            for rr in RR:
                out[(name, stop_mode, rr)] = nonoverlap(
                    tr[tr["rr"] == rr].copy())
    return out

def report(store, title, min_n=60, do_ci=True):
    print(f"\n{'='*104}\n{title}\n{'='*104}")
    print(f"{'variant':<14}{'stop':>6}{'rr':>6}{'n':>6}{'t/mo':>6}{'WR':>7}{'be':>7}"
          f"{'lift':>7}{'expR':>8}{'R/mo':>7}{'trE':>8}{'teE':>8}"
          f"{'5day CI':>18}{'P<=0':>7}{'hold':>6}")
    rows = []
    keys = sorted({k for d in store.values() for k in d})
    n_hyp = 0
    for name, stop_mode, rr in keys:
        frames = [d[(name, stop_mode, rr)] for d in store.values()
                  if (name, stop_mode, rr) in d]
        if not frames:
            continue
        tr = pd.concat(frames, ignore_index=True)
        res = (tr["res"] != 0).sum()
        if res < min_n:
            continue
        n_hyp += 1
        wr = (tr["res"] == 1).sum() / res
        be = core.breakeven_wr(rr, tr["stop_frac"].mean(), tr["nights"].mean())
        span = ((tr["entry_time"].max() - tr["entry_time"].min())
                / (86400 * 30.44))
        trn = tr[tr["dt"] < CUT]; tst = tr[tr["dt"] >= CUT]
        lo = hi = p = np.nan
        if do_ci:
            lo, hi, p = day_cluster_ci(tr, block_days=5)
        expR = tr["net_R"].mean()
        rows.append(dict(variant=name, stop=stop_mode, rr=rr, n=len(tr), wr=wr,
                         be=be, expR=expR, e_tr=trn["net_R"].mean(),
                         e_te=tst["net_R"].mean(), lo=lo, hi=hi, p=p,
                         tpm=len(tr) / span if span > 0 else np.nan))
        print(f"{name:<14}{stop_mode:>6}{rr:>6.2f}{len(tr):>6}"
              f"{len(tr)/span if span>0 else 0:>6.1f}{wr:>7.1%}{be:>7.1%}"
              f"{wr-be:>+7.1%}{expR:>+8.3f}"
              f"{expR*(len(tr)/span if span>0 else 0):>+7.2f}"
              f"{trn['net_R'].mean():>+8.3f}{tst['net_R'].mean():>+8.3f}"
              f"{f'{lo:+.3f} {hi:+.3f}' if do_ci else '':>18}"
              f"{p:>7.1%}" if do_ci else "", flush=True)
    print(f"\nhypotheses in this table: {n_hyp}")
    return pd.DataFrame(rows), n_hyp

def main():
    total_hyp = 0
    all_rows = []
    for level_mode in ("primary", "secondary"):
        store = {}
        for s in symbols():
            store[s] = build_symbol(s, level_mode=level_mode)
            print(f"  built {s} ({level_mode})", flush=True)
        r, nh = report(store, f"4H, 12 perps, level filter = {level_mode}, "
                              f"stack window 11 bars")
        r["level"] = level_mode; r["tf"] = "4H"
        all_rows.append(r); total_hyp += nh

    # 15m BTC, the timeframe FROZEN_SPEC actually specifies
    print("\nbuilding 15m BTC on the 5m path ...", flush=True)
    df = pd.read_parquet(os.path.join(core.DATA, "15m.parquet"))
    df = osc.build_osc(df)
    df = df[df["dt"] >= pd.Timestamp("2021-05-24", tz="UTC")].reset_index(drop=True)
    path = core.load_path("5m")
    for level_mode in ("primary", "secondary"):
        sets = osc.signal_sets(df, level_mode=level_mode, window=11)
        store = {"BTC15": {}}
        for name, (bull, bear) in sets.items():
            for stop_mode in ("atr", "spec"):
                idx = np.concatenate([bull, bear]) if len(bull) + len(bear) else np.array([], int)
                side = np.concatenate([np.ones(len(bull)), -np.ones(len(bear))])
                keep = idx < len(df) - 1
                idx, side = idx[keep], side[keep]
                if len(idx) < 25:
                    continue
                o = np.argsort(idx); idx, side = idx[o], side[o]
                if stop_mode == "spec":
                    sd = osc.spec_stop(df, side, idx)
                    tr = core.trades_for_signals(df, idx, side, 1.0, RR, path,
                                                 max_hold_days=20, stop_dist=sd,
                                                 min_stop_frac=0.006)
                else:
                    tr = core.trades_for_signals(df, idx, side, 1.5, RR, path,
                                                 max_hold_days=20)
                if len(tr) == 0:
                    continue
                tr["cost_R"] = core.cost_R(tr["stop_frac"].values,
                                           tr["nights"].values,
                                           slip_rt=2 * SLIP_MAJOR)
                tr["net_R"] = tr["gross_R"] - tr["cost_R"]
                tr["sym"] = "BTCUSDT"
                for rr in RR:
                    store["BTC15"][(name, stop_mode, rr)] = nonoverlap(
                        tr[tr["rr"] == rr].copy())
        r, nh = report(store, f"15m BTC (FROZEN_SPEC timeframe), "
                              f"level filter = {level_mode}")
        r["level"] = level_mode; r["tf"] = "15m"
        all_rows.append(r); total_hyp += nh

    out = pd.concat(all_rows, ignore_index=True)
    out.to_csv(os.path.join(HERE, "osc_results.csv"), index=False)
    print(f"\n\nTOTAL hypotheses evaluated in this file: {total_hyp}")
    print(f"at a nominal 5% level that is ~{0.05*total_hyp:.0f} expected false positives")
    surv = out[(out["e_tr"] > 0) & (out["e_te"] > 0) & (out["lo"] > 0)]
    print(f"\nsurvive train AND test AND day-clustered CI excludes zero: "
          f"{len(surv)} / {len(out)}")
    if len(surv):
        print(surv.sort_values("expR", ascending=False).to_string(index=False))
    lowrr_surv = surv[surv["rr"] < 1.0]
    print(f"\nof those, at rr < 1: {len(lowrr_surv)}")
    if len(lowrr_surv):
        print(lowrr_surv.sort_values("expR", ascending=False).to_string(index=False))

if __name__ == "__main__":
    main()
