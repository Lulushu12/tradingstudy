"""Independent replication of the open-interest headline, per instrument.

Written from scratch rather than reusing lowrr/openinterest.py, because two
things need separating and the original run could not do it:

  1. Is the effect real code or a bug? An independent implementation of the merge,
     the rolling percentiles and the conditions either reproduces the numbers or
     it does not.
  2. Does it hold on an instrument it was not selected on? The conditions were
     found by searching BTC. ETH and SOL were never searched. That is the check
     that has killed every previous candidate in this study, and it is reported
     PER SYMBOL here rather than pooled, because a pooled number can be carried
     entirely by the symbol the search ran on.

Only the headline conditions are re-tested, not all 360 cells. This is a
confirmation test of specific claims, so the hypothesis count is small and fixed
in advance.
"""
import sys, os, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd
import indicators as ind
from lowrr import core
from lowrr.multiasset import load_path_file, BN, MAJORS, SLIP_MAJOR, SLIP_ALT
from lowrr.finalists_lowrr import nonoverlap
from lowrr.pooled_test import day_cluster_ci

HERE = os.path.dirname(os.path.abspath(__file__))
FLOW = os.path.join(HERE, "flow")
SYMS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
RR = [0.25, 0.5, 0.75, 1.0, 2.0]
CUT = pd.Timestamp("2025-01-01", tz="UTC")
AM = 1.5

def build(sym):
    df = ind.enrich(pd.read_parquet(os.path.join(BN, f"{sym}_4h.parquet")))
    m = pd.read_parquet(os.path.join(FLOW, f"{sym}_metrics.parquet"))

    # metrics may only be used at or after their own timestamp; a 4H bar's signal
    # is read at its CLOSE, which is open_time + 4h.
    df["close_dt"] = df["dt"] + pd.Timedelta(hours=4)
    df["close_dt"] = df["close_dt"].astype("datetime64[ns, UTC]")
    m["dt"] = m["dt"].astype("datetime64[ns, UTC]")
    m = m.sort_values("dt").reset_index(drop=True)

    mi = m.set_index("dt")
    feats = pd.DataFrame(index=mi.index)
    for col, tag in [("sum_open_interest", "oi"),
                     ("sum_toptrader_long_short_ratio", "tt_sum"),
                     ("count_toptrader_long_short_ratio", "tt_cnt"),
                     ("count_long_short_ratio", "glob"),
                     ("sum_taker_long_short_vol_ratio", "taker")]:
        s = mi[col]
        feats[f"{tag}_p30"] = s.rolling("30D", min_periods=500).rank(pct=True)
        feats[f"{tag}_p90"] = s.rolling("90D", min_periods=1500).rank(pct=True)
    feats["oi_chg6h"] = mi["sum_open_interest"].pct_change(72)   # 72 x 5min = 6h
    feats = feats.reset_index()

    merged = pd.merge_asof(df.sort_values("close_dt"), feats.sort_values("dt"),
                           left_on="close_dt", right_on="dt", direction="backward",
                           suffixes=("", "_m"))
    viol = (merged["dt_m"] > merged["close_dt"]).sum()
    assert viol == 0, f"{sym}: {viol} rows use a metric from the future"
    return merged

def conditions(d):
    """Short-side conditions only, matching the reported headline family."""
    px_dn = d["close"] < d["close"].shift(6)
    c = {
        "h2_oi_top_p30":   d["oi_p30"] >= 0.9,
        "h2_oi_top_p90":   d["oi_p90"] >= 0.9,
        "h4_ttsum_top_p30": d["tt_sum_p30"] >= 0.9,
        "h4_ttsum_top_p90": d["tt_sum_p90"] >= 0.9,
        "h4b_glob_top_p30": d["glob_p30"] >= 0.9,
        "h4b_glob_top_p90": d["glob_p90"] >= 0.9,
        "h1_unwind_dn_6h": (d["oi_chg6h"] < 0) & px_dn,
    }
    return {k: v.fillna(False).values for k, v in c.items()}

def main():
    print("independent replication, per instrument, short side, stop 1.5 x ATR14")
    print("BTC is the instrument the conditions were SEARCHED on. ETH and SOL are not.\n")
    rows = []
    for sym in SYMS:
        if not os.path.exists(os.path.join(FLOW, f"{sym}_metrics.parquet")):
            print(f"{sym}: no metrics"); continue
        d = build(sym)
        print(f"{sym}: {len(d)} bars, causality assert passed", flush=True)
        path = load_path_file(os.path.join(BN, f"{sym}_15m.parquet"))
        slip = SLIP_MAJOR if sym in MAJORS else SLIP_ALT
        bb = (d["close"] < d["bb_lo"]).fillna(False).values
        vs = ((d["close"] < d["ema200"]) & (d["vol_ratio"] > 1.8)
              & (d["close"] < d["open"])).fillna(False).values
        conds = conditions(d)
        bases = {"S_bb_break_dn": bb, "S_volspike18_dn": vs, "standalone": np.ones(len(d), bool)}
        for bname, bmask in bases.items():
            for cname, cmask in conds.items():
                mask = bmask & cmask
                idx = np.where(mask)[0]
                idx = idx[idx < len(d) - 1]
                if len(idx) < 30:
                    continue
                tr = core.trades_for_signals(d, idx, -np.ones(len(idx)), AM, RR,
                                             path, max_hold_days=50)
                if len(tr) == 0:
                    continue
                tr["cost_R"] = core.cost_R(tr["stop_frac"].values, tr["nights"].values,
                                           slip_rt=2 * slip)
                tr["net_R"] = tr["gross_R"] - tr["cost_R"]
                for rr in RR:
                    t = nonoverlap(tr[tr["rr"] == rr].copy())
                    res = (t["res"] != 0).sum()
                    if res < 30:
                        continue
                    wr = (t["res"] == 1).sum() / res
                    be = core.breakeven_wr(rr, t["stop_frac"].mean(), t["nights"].mean())
                    trn = t[t["dt"] < CUT]; tst = t[t["dt"] >= CUT]
                    rows.append(dict(sym=sym, base=bname, cond=cname, rr=rr,
                                     n=len(t), ndays=t["dt"].dt.date.nunique(),
                                     wr=wr, be=be, lift=wr - be,
                                     expR=t["net_R"].mean(),
                                     e_tr=trn["net_R"].mean() if len(trn) else np.nan,
                                     e_te=tst["net_R"].mean() if len(tst) else np.nan))
    r = pd.DataFrame(rows)
    r.to_csv(os.path.join(HERE, "oi_verify_results.csv"), index=False)

    piv = r.pivot_table(index=["base", "cond", "rr"], columns="sym", values="expR")
    piv["n_BTC"] = r[r.sym == "BTCUSDT"].set_index(["base", "cond", "rr"])["n"]
    print("\n" + "=" * 96)
    print("net expectancy per trade, BY INSTRUMENT (BTC was searched, ETH and SOL were not)")
    print("=" * 96)
    print(piv.round(3).to_string())

    for other in ["ETHUSDT", "SOLUSDT"]:
        if other not in piv.columns or "BTCUSDT" not in piv.columns:
            continue
        both = piv[["BTCUSDT", other]].dropna()
        pos_btc = both[both["BTCUSDT"] > 0]
        print(f"\n--- {other} vs BTCUSDT ---")
        print(f"  cells positive on BTC: {len(pos_btc)}/{len(both)}")
        print(f"  of those, also positive on {other}: {(pos_btc[other] > 0).sum()}"
              f"/{len(pos_btc)}")
        print(f"  median expR on BTC {pos_btc['BTCUSDT'].median():+.3f}  "
              f"-> on {other} {pos_btc[other].median():+.3f}")
        print(f"  correlation of cell expR across the two: "
              f"{both['BTCUSDT'].corr(both[other]):+.2f}")

if __name__ == "__main__":
    main()
