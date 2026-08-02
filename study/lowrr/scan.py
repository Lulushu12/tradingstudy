"""Hunt for a low R:R / high-winrate edge on high timeframes.

Method: barrier.py already resolved a long AND a short for EVERY bar, on the 5m
path, across the R:R ladder. That table is the outcome universe. Here we slice it
by causal conditions and ask, at each rr, whether any condition lifts the winrate
above the Breakout-cost breakeven on BOTH train and test.

Honesty rules baked in:
  - train = pre-2025, test = 2025-01 onward. Same split as the earlier study.
  - every condition is evaluated at bar close; the outcome it is joined to was
    entered at the next bar open. No look-ahead.
  - the number of hypotheses tested is printed. With H hypotheses at a 5% level
    you expect 0.05*H false positives, so a "winner" is only interesting if it
    survives test AND its train/test gap is small AND the sample is not tiny.
"""
import sys, os, warnings, itertools
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd
import indicators as ind
from lowrr import core

HERE = os.path.dirname(os.path.abspath(__file__))
CUT = pd.Timestamp("2025-01-01", tz="UTC")

def build_frame(tf):
    df = ind.enrich(pd.read_parquet(os.path.join(core.DATA, f"{tf}.parquet")))
    df = df[df["dt"] >= pd.Timestamp("2021-05-24", tz="UTC")].reset_index(drop=True)
    # daily trend context merged onto the lower TF using only CLOSED daily bars
    d1 = ind.enrich(pd.read_parquet(os.path.join(core.DATA, "1D.parquet")))
    d1 = d1[["dt", "close", "ema50", "ema200", "rsi14", "atr14"]].copy()
    d1.columns = ["dt", "d_close", "d_ema50", "d_ema200", "d_rsi", "d_atr"]
    d1["dt"] = d1["dt"] + pd.Timedelta(days=1)   # only usable after the daily bar closes
    df["dt"] = df["dt"].astype("datetime64[ns, UTC]")
    d1["dt"] = d1["dt"].astype("datetime64[ns, UTC]")
    df = pd.merge_asof(df.sort_values("dt"), d1.sort_values("dt"), on="dt", direction="backward")
    return df

def conditions(df):
    """Dict of name -> (mask, side). side +1 long, -1 short, 0 = both directions
    evaluated separately."""
    c = {}
    up = df["close"] > df["ema200"]
    up50 = df["ema50"] > df["ema200"]
    d_up = df["d_close"] > df["d_ema200"]
    upbar = df["close"] > df["open"]
    vol = df.get("vol_ratio", pd.Series(np.nan, index=df.index))
    atrq = df["atr_pct"].rolling(500).rank(pct=True)
    ext = (df["close"] - df["ema200"]) / df["atr14"]
    macd_up = (df["macd"] > 0) & (df["macd_hist"] > df["macd_hist"].shift(1))
    macd_dn = (df["macd"] < 0) & (df["macd_hist"] < df["macd_hist"].shift(1))
    up1 = upbar.shift(1).fillna(False).astype(bool)
    up2 = upbar.shift(2).fillna(False).astype(bool)
    run_up = upbar & up1 & up2
    run_dn = (~upbar) & (~up1) & (~up2)

    base = {
        "all": pd.Series(True, index=df.index),
        "trend": up, "trend+50": up & up50, "trend+d1": up & d_up,
        "trend+macd": up & macd_up,
        "volspike1.8+bar": up & (vol > 1.8) & upbar,
        "volspike2.5+bar": up & (vol > 2.5) & upbar,
        "trend+run3": up & run_up,
        "trend+pullback_ema20": up & (df["close"] < df["ema20"]),
        "trend+rsi<40": up & (df["rsi14"] < 40),
        "trend+rsi<30": up & (df["rsi14"] < 30),
        "trend+bb_lo": up & (df["close"] < df["bb_lo"]),
        "trend+hammer": up & (df["c_hammer"] == 1),
        "trend+bull_engulf": up & (df["c_bull_engulf"] == 1),
        "trend+marubozu": up & (df["c_marubozu_bull"] == 1),
        "trend+lowvol": up & (atrq < 0.33),
        "trend+hivol": up & (atrq > 0.67),
        "trend+near_ema200": up & (ext.abs() < 1.0),
        "trend+far_ema200": up & (ext > 4.0),
        "rsi>70": df["rsi14"] > 70,
        "rsi<30": df["rsi14"] < 30,
        "bb_break_up": df["close"] > df["bb_up"],
        "div_bull": df["div_bull"] == 1,
        "d1_trend": d_up,
    }
    # mirrored short versions
    mirror = {
        "all": pd.Series(True, index=df.index),
        "trend": ~up, "trend+50": (~up) & (~up50), "trend+d1": (~up) & (~d_up),
        "trend+macd": (~up) & macd_dn,
        "volspike1.8+bar": (~up) & (vol > 1.8) & (~upbar),
        "volspike2.5+bar": (~up) & (vol > 2.5) & (~upbar),
        "trend+run3": (~up) & run_dn,
        "trend+pullback_ema20": (~up) & (df["close"] > df["ema20"]),
        "trend+rsi<40": (~up) & (df["rsi14"] > 60),
        "trend+rsi<30": (~up) & (df["rsi14"] > 70),
        "trend+bb_lo": (~up) & (df["close"] > df["bb_up"]),
        "trend+hammer": (~up) & (df["c_shooting_star"] == 1),
        "trend+bull_engulf": (~up) & (df["c_bear_engulf"] == 1),
        "trend+marubozu": (~up) & (df["c_marubozu_bear"] == 1),
        "trend+lowvol": (~up) & (atrq < 0.33),
        "trend+hivol": (~up) & (atrq > 0.67),
        "trend+near_ema200": (~up) & (ext.abs() < 1.0),
        "trend+far_ema200": (~up) & (ext < -4.0),
        "rsi>70": df["rsi14"] < 30,
        "rsi<30": df["rsi14"] > 70,
        "bb_break_up": df["close"] < df["bb_lo"],
        "div_bull": df["div_bear"] == 1,
        "d1_trend": ~d_up,
    }
    for k, v in base.items():
        c[(k, +1)] = v.fillna(False).values
    for k, v in mirror.items():
        c[(k, -1)] = v.fillna(False).values
    return c

def evaluate(tr, df, conds, rr_list):
    rows = []
    n_hyp = 0
    for rr in rr_list:
        s = tr[tr["rr"] == rr]
        for (name, side), mask in conds.items():
            sub = s[(s["side"] == side) & (s["sig_i"].map(lambda i: mask[i]))]
            res = (sub["res"] != 0).sum()
            if res < 40:
                continue
            n_hyp += 1
            trn = sub[sub["dt"] < CUT]; tst = sub[sub["dt"] >= CUT]
            def blk(x):
                r = (x["res"] != 0).sum()
                if r == 0: return np.nan, np.nan, 0, np.nan
                wr = (x["res"] == 1).sum() / r
                be = core.breakeven_wr(rr, x["stop_frac"].mean(), x["nights"].mean())
                return wr, be, len(x), x["net_R"].mean()
            wr_a, be_a, n_a, e_a = blk(sub)
            wr_1, be_1, n_1, e_1 = blk(trn)
            wr_2, be_2, n_2, e_2 = blk(tst)
            rows.append(dict(rr=rr, name=name, side=side,
                             n=n_a, wr=wr_a, be=be_a, expR=e_a,
                             n_tr=n_1, wr_tr=wr_1, e_tr=e_1,
                             n_te=n_2, wr_te=wr_2, e_te=e_2,
                             se=np.sqrt(wr_a * (1 - wr_a) / max(res, 1)),
                             hold=sub["hold_h"].mean(), nights=sub["nights"].mean(),
                             costR=sub["cost_R"].mean()))
    return pd.DataFrame(rows), n_hyp

def main():
    rr_list = [0.25, 0.33, 0.5, 0.75, 1.0, 2.0]
    all_rows = []
    total_hyp = 0
    for tf in ["4H", "1D"]:
        p = os.path.join(HERE, f"barrier_{tf}.parquet")
        if not os.path.exists(p):
            print(f"missing {p}; run barrier.py first"); continue
        tr = pd.read_parquet(p)
        df = build_frame(tf)
        conds = conditions(df)
        r, nh = evaluate(tr, df, conds, rr_list)
        r["tf"] = tf
        all_rows.append(r); total_hyp += nh
    res = pd.concat(all_rows, ignore_index=True)
    res.to_csv(os.path.join(HERE, "scan_results.csv"), index=False)

    print(f"\nhypotheses evaluated (>=40 resolved trades): {total_hyp}")
    print(f"at a nominal 5% level you expect ~{0.05*total_hyp:.0f} false positives\n")

    surv = res[(res["e_tr"] > 0) & (res["e_te"] > 0)].copy()
    surv["worst"] = surv[["e_tr", "e_te"]].min(axis=1)
    print(f"conditions with POSITIVE net expectancy in BOTH train and test: "
          f"{len(surv)} / {len(res)}")
    print(f"\n{'tf':>3} {'rr':>5} {'side':>4} {'name':<22} {'n':>5} {'WR':>6} {'be':>6} "
          f"{'expR':>7} | {'ntr':>5} {'WRtr':>6} {'Etr':>7} | {'nte':>4} {'WRte':>6} {'Ete':>7} "
          f"{'hold_h':>7}")
    for _, r in surv.sort_values("worst", ascending=False).head(30).iterrows():
        print(f"{r['tf']:>3} {r['rr']:>5.2f} {int(r['side']):>4} {r['name']:<22} "
              f"{int(r['n']):>5} {r['wr']:>5.1%} {r['be']:>5.1%} {r['expR']:>+7.3f} | "
              f"{int(r['n_tr']):>5} {r['wr_tr']:>5.1%} {r['e_tr']:>+7.3f} | "
              f"{int(r['n_te']):>4} {r['wr_te']:>5.1%} {r['e_te']:>+7.3f} {r['hold']:>7.1f}")

    print("\n--- restricted to rr < 1 (the question actually asked) ---")
    low = surv[surv["rr"] < 1.0].sort_values("worst", ascending=False)
    if len(low) == 0:
        print("NOTHING survives train and test at rr < 1.")
    else:
        for _, r in low.head(25).iterrows():
            print(f"{r['tf']:>3} {r['rr']:>5.2f} {int(r['side']):>4} {r['name']:<22} "
                  f"{int(r['n']):>5} WR={r['wr']:>5.1%} be={r['be']:>5.1%} "
                  f"expR={r['expR']:>+6.3f} | tr {r['wr_tr']:>5.1%}/{r['e_tr']:>+6.3f} "
                  f"te {r['wr_te']:>5.1%}/{r['e_te']:>+6.3f} n_te={int(r['n_te'])} "
                  f"hold={r['hold']:>5.1f}h")

if __name__ == "__main__":
    main()
