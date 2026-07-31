"""Stage B: does the BTC 4H volume-spike trend-continuation edge transfer to alts?

Rules copied verbatim from study/STRATEGY_FINDINGS.md:
  trend  : close vs EMA200 on 4H
  trigger: volume > 1.8x its 20-bar average, bar closes in the trend direction
  stop   : 1.5 x ATR(14)   target: 2R    entry: next 4H bar open
  one position at a time PER SYMBOL
Costs swept, because alt perps are not BTC.
"""
import numpy as np, pandas as pd

RR, ATR_MULT, VOL_MULT, EMA_N = 2.0, 1.5, 1.8, 200
MAXBARS = 500

def prep(d):
    c = d["close"].to_numpy(float); h = d["high"].to_numpy(float); l = d["low"].to_numpy(float)
    pc = np.concatenate([[c[0]], c[:-1]])
    tr = np.maximum(h - l, np.maximum(abs(h - pc), abs(l - pc)))
    atr = pd.Series(tr).ewm(alpha=1/14, adjust=False).mean().to_numpy()
    ema = pd.Series(c).ewm(span=EMA_N, adjust=False).mean().to_numpy()
    vma = pd.Series(d["volume"].to_numpy(float)).rolling(20).mean().to_numpy()
    return c, h, l, atr, ema, vma

def run_symbol(d, fee_rt, slip):
    """Return list of (exit_dt, side, net_R, entry_dt)."""
    d = d.reset_index(drop=True)
    n = len(d)
    if n < EMA_N + 30: return []
    o = d["open"].to_numpy(float); h = d["high"].to_numpy(float); l = d["low"].to_numpy(float)
    c, _, _, atr, ema, vma = prep(d)
    dts = d["dt"].to_numpy()
    v = d["volume"].to_numpy(float)
    up = c > ema
    spike = v > VOL_MULT * vma
    green = c > o; red = c < o
    sig_long = up & spike & green
    sig_short = (~up) & spike & red

    trades = []; busy_until = -1
    for i in range(EMA_N, n - 1):
        if i <= busy_until: continue
        if not (sig_long[i] or sig_short[i]): continue
        if not np.isfinite(atr[i]) or atr[i] <= 0: continue
        s = 1 if sig_long[i] else -1
        ei = i + 1
        entry = o[ei] * (1 + s * slip)
        rdist = ATR_MULT * atr[i]
        if rdist / entry < 0.002: continue          # degenerate stop guard
        stop = entry - s * rdist; tgt = entry + s * RR * rdist
        sdf = rdist / entry
        fee_R = (fee_rt + 2 * slip) / sdf
        res = None
        end = min(ei + MAXBARS, n)
        for j in range(ei, end):
            hs = (l[j] <= stop) if s > 0 else (h[j] >= stop)
            ht = (h[j] >= tgt) if s > 0 else (l[j] <= tgt)
            if hs and ht: res, xi = -1.0, j; break   # pessimistic: stop first
            if hs: res, xi = -1.0, j; break
            if ht: res, xi = RR, j; break
        if res is None:
            xi = end - 1
            res = s * (c[xi] - entry) / rdist
        busy_until = xi
        trades.append((dts[xi], s, res - fee_R, dts[ei]))
    return trades

def report(tr, label):
    if len(tr) < 30:
        print(f"{label:<34} n={len(tr):<6} (too few)"); return
    t = pd.DataFrame(tr, columns=["exit_dt","side","R","entry_dt"])
    t["exit_dt"] = pd.to_datetime(t["exit_dt"], utc=True)
    wr = (t.R > 0).mean(); exp = t.R.mean()
    se = t.R.std() / np.sqrt(len(t))
    tr_ = t[t.exit_dt < "2025-01-01"]; te_ = t[t.exit_dt >= "2025-01-01"]
    print(f"{label:<34} n={len(t):<6} WR={wr:5.1%}  E={exp:+.3f}R "
          f"(SE {se:.3f}, t={exp/se if se else 0:4.1f})  "
          f"train {tr_.R.mean():+.3f} / test {te_.R.mean():+.3f}")
    return t

if __name__ == "__main__":
    p = pd.read_parquet("panel_4h.parquet")
    u = pd.read_parquet("universe.parquet")

    # liquidity-tiered universes: what you could actually trade
    liq = u[u.adv_usd > 1e7].index.tolist()      # >$10M/day
    big = u[u.adv_usd > 5e7].index.tolist()      # >$50M/day
    print(f"universe: all={p.symbol.nunique()}  >$10M/d={len(liq)}  >$50M/d={len(big)}")

    COSTS = [(0.0008, 0.0000, "BTC-study costs (8bp, no slip)"),
             (0.0010, 0.0005, "realistic alt (10bp + 5bp slip)"),
             (0.0010, 0.0015, "small-cap alt (10bp + 15bp slip)"),
             (0.0010, 0.0030, "thin alt (10bp + 30bp slip)")]

    for fee, slip, lab in COSTS:
        print("\n" + "=" * 96)
        print(f"COSTS: {lab}")
        print("=" * 96)
        for name, syms in [("BTC only", ["BTCUSDT"]),
                           ("alts >$50M/day", [s for s in big if s != "BTCUSDT"]),
                           ("alts >$10M/day", [s for s in liq if s != "BTCUSDT"]),
                           ("ALL perps", sorted(p.symbol.unique()))]:
            allt = []
            for s in syms:
                d = p[p.symbol == s]
                allt += run_symbol(d, fee, slip)
            t = report(allt, name)
            if t is not None and name == "alts >$10M/day":
                bys = t.groupby(t.side.map({1: "long", -1: "short"})).R.agg(["size", "mean"])
                print("      by side: " + " | ".join(
                    f"{k} n={int(r['size'])} E={r['mean']:+.3f}R" for k, r in bys.iterrows()))
                t["yr"] = t.exit_dt.dt.year
                print("      by year: " + " | ".join(
                    f"{int(y)}:{v:+.2f}" for y, v in t.groupby("yr").R.mean().items()))
