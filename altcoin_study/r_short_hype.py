"""Stage R: the actionable form of the selection signal.

Stage O/P found the strongest launch signal points DOWN: the loudest launches (top quintile
of week-1 volume) have a median hold-to-today outcome of 0.10x. If that is real, the trade
is not to buy quiet coins -- it is to SHORT loud ones.

Tested properly: entry at the close of the observation window (day 7), ATR stop, fixed R
target, funding paid/received modelled from real history, pessimistic same-bar resolution,
and an out-of-sample split. Ranked WITHIN each listing cohort so it is not an era bet.
"""
import numpy as np, pandas as pd
from scipy import stats as st

BARS = 42                     # 7 days of 4h bars = observation window
FEE, SLIP = 0.0010, 0.0005

p = pd.read_parquet("panel_4h.parquet")
fund = pd.read_parquet("funding.parquet")
D = pd.read_parquet("launch_signals_binance.parquet")

fmap = {s: g.set_index("dt")["rate"] for s, g in fund.groupby("symbol")}

def atr(h, l, c, n=14):
    pc = np.concatenate([[c[0]], c[:-1]])
    tr = np.maximum(h-l, np.maximum(abs(h-pc), abs(l-pc)))
    return pd.Series(tr).ewm(alpha=1/n, adjust=False).mean().to_numpy()

def run(sym, side, atr_mult, rr, max_bars):
    g = p[p.symbol == sym].sort_values("dt")
    c = g["close"].to_numpy(float); o = g["open"].to_numpy(float)
    h = g["high"].to_numpy(float); l = g["low"].to_numpy(float)
    dts = g["dt"].to_numpy()
    if len(c) < BARS + 20: return None
    a = atr(h, l, c)
    i = BARS
    if not np.isfinite(a[i-1]) or a[i-1] <= 0: return None
    entry = o[i]*(1 + side*SLIP)
    rdist = atr_mult*a[i-1]; sdf = rdist/entry
    if sdf < 0.005 or sdf > 0.9: return None
    stop = entry - side*rdist; tgt = entry + side*rr*rdist
    end = min(i+max_bars, len(c))
    R = None
    for j in range(i, end):
        hs = (l[j] <= stop) if side > 0 else (h[j] >= stop)
        ht = (h[j] >= tgt) if side > 0 else (l[j] <= tgt)
        if hs:                                     # pessimistic: stop first, fill at worse
            fill = min(stop, c[j]) if side > 0 else max(stop, c[j])
            R = side*(fill-entry)/rdist; xi = j; break
        if ht: R = rr; xi = j; break
    if R is None:
        xi = end-1; R = side*(c[xi]-entry)/rdist
    ser = fmap.get(sym)
    fR = 0.0
    if ser is not None:
        seg = ser.loc[(ser.index > pd.Timestamp(dts[i])) & (ser.index <= pd.Timestamp(dts[xi]))]
        fR = seg.sum()*side/sdf
    return R - (FEE+2*SLIP)/sdf - fR, sdf, pd.Timestamp(dts[xi])

# rank loudness within each listing cohort
D["loud_rank"] = D.groupby("year")["adv_w"].rank(pct=True)
D["bucket"] = pd.cut(D.loud_rank, [0,.2,.4,.6,.8,1.0], labels=[1,2,3,4,5])

print("="*104)
print("R1. SHORT THE LOUDEST LAUNCHES  (entry at day 7 close, 2xATR stop, 2R target)")
print("="*104)
print(f"{'bucket (week-1 volume)':<28} {'n':>5} {'E net R':>9} {'WR':>7} {'t-stat':>8} {'train':>8} {'test':>8}")
print("-"*104)
store = {}
for b in [1,2,3,4,5]:
    rows = []
    for s in D[D.bucket == b].sym:
        r = run(s, -1, 2.0, 2.0, 500)
        if r: rows.append((s, r[0], r[2]))
    if len(rows) < 25: continue
    t = pd.DataFrame(rows, columns=["sym","R","exit"])
    store[b] = t
    se = t.R.std()/np.sqrt(len(t))
    yr = D.set_index("sym").year
    t["year"] = t.sym.map(yr)
    tr, te = t[t.year <= 2023], t[t.year >= 2024]
    lab = f"Q{b}" + (" loudest" if b == 5 else " quietest" if b == 1 else "")
    print(f"{lab:<28} {len(t):>5} {t.R.mean():>+8.3f} {(t.R>0).mean():>6.1%} "
          f"{t.R.mean()/se:>7.2f} {tr.R.mean():>+7.3f} {te.R.mean():>+7.3f}")

print("\n  (bucket 5 = loudest launches. Positive E means shorting them made money.)")

print("\n" + "="*104)
print("R2. PARAMETER SENSITIVITY on the loudest bucket (is it a knife edge?)")
print("="*104)
loud = D[D.bucket == 5].sym.tolist()
print(f"{'stop':>6} {'target':>8} {'n':>5} {'E net R':>9} {'WR':>7} {'t':>7} {'train':>8} {'test':>8}")
print("-"*104)
yr = D.set_index("sym").year
for am in [1.5, 2.0, 3.0]:
    for rr in [1.0, 2.0, 3.0]:
        rows = []
        for s in loud:
            r = run(s, -1, am, rr, 500)
            if r: rows.append((s, r[0]))
        if len(rows) < 25: continue
        t = pd.DataFrame(rows, columns=["sym","R"]); t["year"] = t.sym.map(yr)
        se = t.R.std()/np.sqrt(len(t))
        tr, te = t[t.year <= 2023], t[t.year >= 2024]
        print(f"{am:>5.1f}x {rr:>7.1f}R {len(t):>5} {t.R.mean():>+8.3f} {(t.R>0).mean():>6.1%} "
              f"{t.R.mean()/se:>6.2f} {tr.R.mean():>+7.3f} {te.R.mean():>+7.3f}")

print("\n" + "="*104)
print("R3. THE SQUEEZE TAIL  (what kills short books)")
print("="*104)
if 5 in store:
    t = store[5]
    v = np.sort(t.R.values)
    print(f"  n={len(t)}  worst {v[0]:+.2f}R  "
          + "  ".join(f"p{q}={np.percentile(t.R,q):+.2f}R" for q in [1,5,50,95,99]))
    print(f"  trades worse than -2R: {(t.R<-2).mean():.1%}   "
          f"worst 5 trades sum {v[:5].sum():+.1f}R of total {t.R.sum():+.1f}R")
    m, k = None, None
    rng = np.random.default_rng(3)
    t2 = t.copy(); t2["m"] = pd.to_datetime(t2.exit, utc=True).dt.to_period("M")
    groups = [g.R.to_numpy() for _, g in t2.groupby("m")]
    means = np.array([np.concatenate([groups[i] for i in rng.integers(0,len(groups),len(groups))]).mean()
                      for _ in range(4000)])
    lo, hi = np.percentile(means, [2.5, 97.5])
    print(f"  monthly block bootstrap: E={t.R.mean():+.3f}R  95% CI [{lo:+.3f},{hi:+.3f}]  "
          f"P(E<=0)={np.mean(means<=0):.3f}  ({len(groups)} blocks)")

print("\n" + "="*104)
print("R4. HOW MANY TRADES IS THIS, REALLY?")
print("="*104)
if 5 in store:
    t = store[5]; t["year"] = t.sym.map(yr)
    print(t.groupby("year").R.agg(["size","mean"]).round(3).to_string())
    print(f"\n  ~{len(t)/6:.0f} trades per year. This is a low-frequency, one-shot-per-listing trade.")
