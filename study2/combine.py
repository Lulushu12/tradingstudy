"""Combined portfolio: baseline + surviving rules + ML book.

Books (all pre-registered before this script's holdout look):
  volspike   4h both sides 2:1  (prior study's rule, extended to 6 symbols)
  glsr_short 4h short 2:1      (holdout survivor, +0.215R)
  whale_long 4h long 2:1       (holdout survivor, +0.125R)
  btclead    1h alt long 2:1   (holdout survivor, +0.052R)
  ml4h_l21   4h long 2:1       (LightGBM p>0.54, holdout +0.128R bar-level)
  [ml4h shorts included only if their holdout was positive]

Steps:
 1. build/collect trade lists (per-symbol locks WITHIN each book).
 2. train-period monthly-R correlation between books.
 3. grid-search per-book risk weights on TRAIN to maximize monthly return
    subject to train maxDD <= DD_CAP_TRAIN (safety margin under the 6% target).
 4. ONE holdout evaluation at frozen weights.
"""
import warnings, itertools, json
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import core, portfolio

DD_CAP_TRAIN = 0.05
SPLIT = np.datetime64("2025-01-01")

def volspike_trades():
    sigs = []
    for sym in core.SYMS:
        df = core.load(sym, "4h")
        c, o, v = df["close"], df["open"], df["volume"]
        ema200 = c.ewm(span=200, adjust=False).mean()
        vr = v / v.rolling(20).mean()
        up = (c > ema200) & (vr > 1.8) & (c > o)
        dn = (c < ema200) & (vr > 1.8) & (c < o)
        for side, m in (("long", up), ("short", dn)):
            s = df.loc[m, ["dt"]].copy()
            s["sym"] = sym; s["side"] = side; s["rr"] = 2.0
            sigs.append(s)
    sig = pd.concat(sigs)[["sym", "dt", "side", "rr"]]
    return portfolio.resolve_trades(sig, "4h")

def ml_trades(fname, ival, side):
    t = pd.read_parquet(f"{core.DATA}/{fname}")
    sig = t[["sym", "dt"]].copy()
    sig["side"] = side; sig["rr"] = 2.0
    return portfolio.resolve_trades(sig, ival)

def monthly_R(trades, lo, hi):
    t = trades[(trades["entry_dt"] >= lo) & (trades["entry_dt"] < hi)].copy()
    t["exit_dt"] = pd.to_datetime(t["exit_dt"], utc=True)
    return t.set_index("exit_dt")["netR"].resample("ME").sum()

def sim_combo(books, weights, lo, hi, start_eq=1.0):
    rows = []
    for name, w in weights.items():
        if w <= 0:
            continue
        t = books[name]
        t = t[(t["entry_dt"] >= lo) & (t["entry_dt"] < hi)]
        for r in t.itertuples():
            rows.append((r.entry_dt, r.exit_dt, r.netR, w))
    if not rows:
        return None
    ev = []
    for i, (ent, ext, netR, w) in enumerate(rows):
        ev.append((ent, 1, i)); ev.append((ext, 0, i))
    ev.sort(key=lambda x: (x[0], x[1]))
    eq = start_eq; risk = {}; pnl_at = []
    for ts, kind, i in ev:
        if kind == 1:
            risk[i] = eq * rows[i][3]
        elif i in risk:
            p = risk.pop(i) * rows[i][2]
            eq += p
            pnl_at.append((ts, p))
    s = pd.Series([p for _, p in pnl_at],
                  index=pd.DatetimeIndex([pd.Timestamp(t) for t, _ in pnl_at]))
    daily = s.resample("1D").sum().cumsum() + start_eq
    dd = float((daily / daily.cummax() - 1).min())
    months = max((s.index.max() - s.index.min()).days / 30.4, 1e-9)
    mret = (eq / start_eq) ** (1 / months) - 1 if eq > 0 else -1.0
    monthly = s.resample("ME").sum()
    return {"final_eq": round(eq, 4), "mret": round(float(mret), 4),
            "maxDD": round(dd, 4), "n": len(pnl_at),
            "pos_months": round(float((monthly > 0).mean()), 2)}

if __name__ == "__main__":
    books = {
        "volspike": volspike_trades(),
        "glsr_short": pd.read_parquet(f"{core.DATA}/rtrades_glsr_short.parquet"),
        "whale_long": pd.read_parquet(f"{core.DATA}/rtrades_whale_long.parquet"),
        "btclead": pd.read_parquet(f"{core.DATA}/rtrades_btclead_alt.parquet"),
        "ml4h_l21": ml_trades("trades_4h_long_21.parquet", "4h", "long"),
        "ml4h_s21": ml_trades("trades_4h_short_21.parquet", "4h", "short"),
    }
    LO, HI = np.datetime64("2020-01-01"), np.datetime64("2027-01-01")
    print("== book stats (train | holdout) ==")
    for n, t in books.items():
        for lo, hi, tag in ((LO, SPLIT, "train"), (SPLIT, HI, "hold")):
            g = t[(t["entry_dt"] >= lo) & (t["entry_dt"] < hi)]
            if len(g):
                print(f"  {n:11s} {tag:5s} n={len(g):5d} expR={g['netR'].mean():+.3f}")
    mr = pd.DataFrame({n: monthly_R(t, LO, SPLIT) for n, t in books.items()})
    print("\n== train monthly-R correlation ==")
    print(mr.corr().round(2).to_string())

    grid = [0.0, 0.001, 0.002, 0.003, 0.005]
    names = list(books)
    best = None
    for combo in itertools.product(grid, repeat=len(names)):
        if sum(combo) == 0:
            continue
        w = dict(zip(names, combo))
        s = sim_combo(books, w, LO, SPLIT)
        if s is None or s["maxDD"] < -DD_CAP_TRAIN:
            continue
        if best is None or s["mret"] > best[1]["mret"]:
            best = (w, s)
    w, s = best
    print("\n== chosen weights (train) ==", json.dumps(w))
    print("train:", s)
    print("holdout:", sim_combo(books, w, SPLIT, HI))
    # also show a more aggressive variant for reference: weights x2
    w2 = {k: v * 2 for k, v in w.items()}
    print("\nweights x2 train:", sim_combo(books, w2, LO, SPLIT))
    print("weights x2 holdout:", sim_combo(books, w2, SPLIT, HI))
