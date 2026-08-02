"""Take the low R:R candidates seriously and then try hard to kill them.

The scan slices overlapping bar-by-bar outcomes, which inflates the sample and
flatters stability. Everything here works on a NON-OVERLAPPING trade sequence
(one position at a time), which is what a Breakout account can actually hold.

For each candidate:
  - non-overlapping trade sequence, Breakout costs incl. the 5 bps overnight fee
  - train (pre-2025) / test (2025+) split
  - stationary block bootstrap CI on net expectancy (blocks preserve the clustering
    that makes naive standard errors a lie)
  - cost headroom: how much extra per-side slippage kills it
  - per-year expectancy
"""
import sys, os, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd
import indicators as ind
from lowrr import core
from lowrr.scan import build_frame, CUT

HERE = os.path.dirname(os.path.abspath(__file__))
RNG = np.random.default_rng(20260802)

# ------------------------------------------------------------------ candidates
def rule_masks(df):
    up = df["close"] > df["ema200"]
    ext = (df["close"] - df["ema200"]) / df["atr14"]
    vol = df.get("vol_ratio", pd.Series(np.nan, index=df.index))
    upbar = df["close"] > df["open"]
    up1 = upbar.shift(1).fillna(False).astype(bool)
    up2 = upbar.shift(2).fillna(False).astype(bool)
    r = {
        # name: (mask, side)
        "S_bb_break_dn":     ((df["close"] < df["bb_lo"]), -1),
        "S_dntrend_rsi60":   ((~up) & (df["rsi14"] > 60), -1),
        "S_dntrend_at_200":  ((~up) & (ext.abs() < 1.0), -1),
        "S_volspike25_dn":   ((~up) & (vol > 2.5) & (~upbar), -1),
        "S_volspike18_dn":   ((~up) & (vol > 1.8) & (~upbar), -1),
        "L_uptrend_run3":    (up & upbar & up1 & up2, +1),
        "L_bb_break_up":     ((df["close"] > df["bb_up"]), +1),
        "L_volspike18_up":   (up & (vol > 1.8) & upbar, +1),
        "L_uptrend_at_200":  (up & (ext.abs() < 1.0), +1),
    }
    return {k: (v[0].fillna(False).values, v[1]) for k, v in r.items()}

# ------------------------------------------------------------------- machinery
def nonoverlap(tr):
    """Keep only trades that could actually be held one at a time."""
    tr = tr.sort_values("entry_time").reset_index(drop=True)
    keep = []
    busy = -1
    for r in tr.itertuples():
        if r.entry_time < busy:
            continue
        keep.append(r.Index)
        busy = r.exit_time
    return tr.loc[keep].reset_index(drop=True)

def block_bootstrap_ci(x, n_boot=4000, block=10, q=(2.5, 97.5)):
    """Stationary block bootstrap on the mean. Blocks keep the streakiness."""
    x = np.asarray(x, dtype=float)
    n = len(x)
    if n < block * 2:
        return (np.nan, np.nan)
    nb = int(np.ceil(n / block))
    starts = RNG.integers(0, n, size=(n_boot, nb))
    offs = np.arange(block)
    idx = (starts[:, :, None] + offs[None, None, :]) % n
    means = x[idx.reshape(n_boot, -1)[:, :n]].mean(axis=1)
    return tuple(np.percentile(means, q))

def recost(tr, extra_slip_per_side=0.0):
    c = core.cost_R(tr["stop_frac"].values, tr["nights"].values,
                    slip_rt=core.SLIP_RT + 2 * extra_slip_per_side)
    return tr["gross_R"].values - c

def evaluate(name, tr, rr):
    tr = nonoverlap(tr)
    if len(tr) < 30:
        return None
    res = (tr["res"] != 0).sum()
    wr = (tr["res"] == 1).sum() / res
    lo, hi = block_bootstrap_ci(tr["net_R"].values)
    trn = tr[tr["dt"] < CUT]; tst = tr[tr["dt"] >= CUT]
    span_m = (tr["entry_time"].iloc[-1] - tr["entry_time"].iloc[0]) / (86400 * 30.44)
    # cost headroom: extra per-side slippage at which expectancy hits zero
    head = np.nan
    for s in np.arange(0.0, 0.0030, 0.00002):
        if recost(tr, s).mean() <= 0:
            head = s; break
    streak = mx = 0
    for w in (tr["net_R"] > 0).values:
        if w: streak = 0
        else: streak += 1; mx = max(mx, streak)
    yrs = tr.groupby(tr["dt"].dt.year)["net_R"].agg(["mean", "size"])
    return dict(
        rule=name, rr=rr, n=len(tr), wr=wr,
        be=core.breakeven_wr(rr, tr["stop_frac"].mean(), tr["nights"].mean()),
        expR=tr["net_R"].mean(), ci_lo=lo, ci_hi=hi,
        R_per_month=tr["net_R"].mean() * len(tr) / span_m,
        tpm=len(tr) / span_m,
        n_tr=len(trn), e_tr=trn["net_R"].mean() if len(trn) else np.nan,
        wr_tr=(trn["res"] == 1).sum() / max((trn["res"] != 0).sum(), 1),
        n_te=len(tst), e_te=tst["net_R"].mean() if len(tst) else np.nan,
        wr_te=(tst["res"] == 1).sum() / max((tst["res"] != 0).sum(), 1),
        hold_h=tr["hold_h"].mean(), nights=tr["nights"].mean(),
        costR=tr["cost_R"].mean(), stop_frac=tr["stop_frac"].mean(),
        slip_headroom_bps=head * 1e4 if np.isfinite(head) else np.inf,
        lose_streak=mx,
        years="  ".join(f"{y}:{r['mean']:+.3f}({int(r['size'])})" for y, r in yrs.iterrows()),
    ), tr

def main():
    tf = "4H"
    rr_grid = [0.25, 0.33, 0.5, 0.75, 1.0, 1.5, 2.0]
    atr_mults = [1.0, 1.5, 2.5]
    df = build_frame(tf)
    path = core.load_path("5m")
    masks = rule_masks(df)
    rows = []
    store = {}
    for am in atr_mults:
        for name, (mask, side) in masks.items():
            idx = np.where(mask)[0]
            idx = idx[idx < len(df) - 1]
            if len(idx) < 40:
                continue
            tr_all = core.trades_for_signals(df, idx, np.full(len(idx), side),
                                             am, rr_grid, path, max_hold_days=50)
            for rr in rr_grid:
                out = evaluate(name, tr_all[tr_all["rr"] == rr].copy(), rr)
                if out is None:
                    continue
                d, trades = out
                d["atr_mult"] = am
                rows.append(d)
                store[(name, am, rr)] = trades
        print(f"# atr_mult={am} done", flush=True)
    res = pd.DataFrame(rows)
    res.to_csv(os.path.join(HERE, "finalists_lowrr.csv"), index=False)

    def show(sub, title):
        print(f"\n===== {title} =====")
        print(f"{'rule':<19}{'am':>4}{'rr':>6}{'n':>5}{'t/mo':>6}{'WR':>7}{'be':>7}"
              f"{'expR':>8}{'ci_lo':>8}{'ci_hi':>8}{'R/mo':>7}{'trE':>7}{'teE':>7}"
              f"{'hold':>6}{'slipHR':>8}{'strk':>5}")
        for _, r in sub.iterrows():
            print(f"{r['rule']:<19}{r['atr_mult']:>4.1f}{r['rr']:>6.2f}{int(r['n']):>5}"
                  f"{r['tpm']:>6.1f}{r['wr']:>7.1%}{r['be']:>7.1%}{r['expR']:>+8.3f}"
                  f"{r['ci_lo']:>+8.3f}{r['ci_hi']:>+8.3f}{r['R_per_month']:>+7.2f}"
                  f"{r['e_tr']:>+7.3f}{r['e_te']:>+7.3f}{r['hold_h']:>6.0f}"
                  f"{r['slip_headroom_bps']:>8.1f}{int(r['lose_streak']):>5}")

    surv = res[(res["e_tr"] > 0) & (res["e_te"] > 0) & (res["ci_lo"] > 0)]
    show(surv[surv["rr"] < 1].sort_values("R_per_month", ascending=False).head(25),
         "rr < 1, positive in train AND test AND bootstrap CI excludes zero")
    show(surv[surv["rr"] >= 1].sort_values("R_per_month", ascending=False).head(15),
         "rr >= 1 comparison set (same filter)")

    print("\n--- per-year detail for the top rr<1 rows ---")
    for _, r in surv[surv["rr"] < 1].sort_values("R_per_month", ascending=False).head(6).iterrows():
        print(f"{r['rule']} am={r['atr_mult']} rr={r['rr']}: {r['years']}")

    import pickle
    with open(os.path.join(HERE, "trades_store.pkl"), "wb") as f:
        pickle.dump(store, f)
    print(f"\nsaved {len(store)} trade sets to trades_store.pkl")

if __name__ == "__main__":
    main()
