"""Full audit of the prior study's surviving strategy: 4H volume-spike trend
continuation (study/STRATEGY_FINDINGS.md, study/finalists.py kind='volspike').

Rule, ported exactly from the study code:
  4H bars. Long signal at bar close: close > EMA200(close, ewm span) AND
  volume > 1.8 x SMA20(volume, current bar included) AND close > open.
  Short mirrored below EMA200. Entry next 4H open. Stop 1.5 x ATR14
  (TR ewm alpha=1/14). Target 2:1. Timeout 300 4H bars (mark to market).
  One position at a time: signals while busy are skipped.

Audit engine differences vs the study (all harsher, none favorable):
  - resolution on the 15m path with same-bar stop+target resolved as STOP
    (study used nearest-to-open); adverse gaps exit at the gapped open
  - slippage 1bp per fill; swap 0.0055% per 4h boundary held (study: none)
  - sizing 0.5% per Amendment 1 for the K5 venue bootstrap

Selection caveat reported alongside results: this rule is the best survivor
of a ~30-family scan whose train segment was pre-2025 and test 2025+, all
inside the studied span. Full-span numbers therefore contain the data that
selected the rule. Only the live holdout is clean, and it stays locked.
"""
import os
import sys
from collections import defaultdict

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from phase1 import regime_labels, k5_bootstrap, half_label, streaks

COMMISSION_RT = 0.0008
SWAP_PER_4H = 0.000055


def build_4h(df15):
    g = df15["time"] // 14400
    agg = df15.groupby(g).agg(
        time=("time", "first"), open=("open", "first"), high=("high", "max"),
        low=("low", "min"), close=("close", "last"), volume=("Volume", "sum"),
        first_15m_idx=("time", "idxmin"), n15=("time", "size"))
    agg = agg.reset_index(drop=True)
    agg["time"] = (agg["time"] // 14400) * 14400   # 4h bucket open time
    return agg


def signals_4h(h4):
    c, o, v = h4["close"], h4["open"], h4["volume"]
    ema200 = c.ewm(span=200, adjust=False).mean()
    vol_ratio = v / v.rolling(20).mean()
    tr = pd.concat([(h4["high"] - h4["low"]),
                    (h4["high"] - c.shift(1)).abs(),
                    (h4["low"] - c.shift(1)).abs()], axis=1).max(axis=1)
    atr14 = tr.ewm(alpha=1 / 14, adjust=False).mean()
    spike = vol_ratio > 1.8
    long_sig = (c > ema200) & spike & (c > o)
    short_sig = (c < ema200) & spike & (c < o)
    out = []
    for i in np.where(long_sig | short_sig)[0]:
        if not np.isfinite(atr14.iloc[i]) or atr14.iloc[i] <= 0 or i < 20:
            continue
        out.append((int(i), "long" if long_sig.iloc[i] else "short",
                    1.5 * float(atr14.iloc[i])))
    return out


def simulate(df15, h4, sigs, slip=0.0001, swap=SWAP_PER_4H, worst_case=True):
    t15 = df15["time"].to_numpy()
    o = df15["open"].to_numpy(float)
    h = df15["high"].to_numpy(float)
    l = df15["low"].to_numpy(float)
    c = df15["close"].to_numpy(float)
    n = len(df15)
    idx_of_open = {v: i for i, v in enumerate(t15)}
    h4_time = h4["time"].to_numpy()
    trades = []
    busy_until = -1
    skipped_busy = 0
    for i, direction, stop_d in sigs:
        if i + 1 >= len(h4):
            continue
        e = idx_of_open.get(int(h4_time[i + 1]))
        if e is None:
            continue
        if e <= busy_until:
            skipped_busy += 1
            continue
        entry = o[e]
        sgn = 1 if direction == "long" else -1
        stop = entry - sgn * stop_d
        target = entry + sgn * 2 * stop_d
        last = min(e + 300 * 16, n - 1)
        gross = None
        for b in range(e, last + 1):
            gap_sl = (o[b] <= stop) if sgn > 0 else (o[b] >= stop)
            gap_tp = (o[b] >= target) if sgn > 0 else (o[b] <= target)
            if b == e:
                gap_sl = gap_tp = False
            hit_sl = (l[b] <= stop) if sgn > 0 else (h[b] >= stop)
            hit_tp = (h[b] >= target) if sgn > 0 else (l[b] <= target)
            if gap_sl or gap_tp:
                px = o[b]
                gross = sgn * (px - entry) / stop_d
                x = b
                break
            if hit_sl and hit_tp:
                gross, x = (-1.0, b) if worst_case else (
                    (-1.0, b) if abs(o[b] - stop) < abs(o[b] - target) else (2.0, b))
                break
            if hit_sl:
                gross, x = -1.0, b
                break
            if hit_tp:
                gross, x = 2.0, b
                break
        if gross is None:
            gross = sgn * (c[last] - entry) / stop_d
            x = last
        busy_until = x
        n_swaps = int(t15[x] // 14400) - int(t15[e] // 14400)
        cost_r = (COMMISSION_RT + 2 * slip + n_swaps * swap) * entry / stop_d
        trades.append(dict(dir=direction, entry=entry, stop_d=stop_d,
                           gross_r=gross, net_r=gross - cost_r,
                           t_entry=t15[e], t_exit=t15[x], n_swaps=n_swaps))
    return trades, skipped_busy


def block(trades, label):
    rs = np.array([t["net_r"] for t in trades])
    if not len(rs):
        return f"{label}: no trades"
    order = np.argsort([t["t_exit"] for t in trades])
    ls, ls_d = streaks(rs[order], np.array([t["t_exit"] for t in trades])[order])
    gp, gl = rs[rs > 0].sum(), -rs[rs < 0].sum()
    return (f"{label}: n={len(rs)} exp={rs.mean():+.4f}R (SE {rs.std()/np.sqrt(len(rs)):.4f}) "
            f"win={np.mean(rs > 0):.1%} PF={gp/gl if gl else float('inf'):.3f} "
            f"streak={ls} ({ls_d:.0f}d)")


def main():
    df15 = pd.read_parquet(os.path.join(os.path.dirname(HERE), "audit", "studied_15m.parquet"))
    df15 = df15.reset_index(drop=True)
    h4 = build_4h(df15)
    print(f"4H bars: {len(h4)}, partial buckets (n15<16): {(h4['n15'] < 16).sum()}")
    sigs = signals_4h(h4)
    print(f"signals: {len(sigs)} (long {sum(1 for s in sigs if s[1]=='long')}, "
          f"short {sum(1 for s in sigs if s[1]=='short')})")

    # port-fidelity run: study's cost model (fees only, no slip/swap, nearest-open)
    tr0, _ = simulate(df15, h4, sigs, slip=0.0, swap=0.0, worst_case=False)
    print("\nPORT FIDELITY (study cost model, expect ~+0.21R): " + block(tr0, "study-model"))

    # audit run
    trades, skipped_busy = simulate(df15, h4, sigs)
    print(f"\nAUDIT MODEL (full cost stack, worst-case bars): skipped_busy={skipped_busy}")
    print(block(trades, "pooled"))
    rs = np.array([t["net_r"] for t in trades])

    print("\nPer window:")
    by_w = defaultdict(list)
    for t in trades:
        by_w[half_label(t["t_entry"])].append(t)
    neg = 0
    means = {}
    for w in sorted(by_w):
        print("  " + block(by_w[w], w))
        means[w] = np.mean([t["net_r"] for t in by_w[w]])
        neg += means[w] < 0

    print("\nTrain/test split as the study defined it:")
    cut = pd.Timestamp("2025-01-01", tz="UTC").timestamp()
    print("  " + block([t for t in trades if t["t_entry"] < cut], "train(<2025)"))
    print("  " + block([t for t in trades if t["t_entry"] >= cut], "test(>=2025)"))

    print("\nPer regime:")
    trend_map, vol_map = regime_labels()
    by_r = defaultdict(list)
    for t in trades:
        day = pd.to_datetime(t["t_entry"], unit="s", utc=True).floor("D")
        by_r[trend_map.get(day, "na")].append(t)
        by_r[vol_map.get(day, "na")].append(t)
    for r in ("bull", "bear", "chop", "highvol", "lowvol"):
        if by_r.get(r):
            print("  " + block(by_r[r], r))

    print("\nCost sweep (slippage bp/fill):")
    be = None
    prev = None
    for bp in (0, 1, 2, 3, 5, 10, 15, 20, 30):
        tr, _ = simulate(df15, h4, sigs, slip=bp * 1e-4)
        m = np.mean([t["net_r"] for t in tr])
        print(f"  {bp:3d} bp: {m:+.4f}R (n={len(tr)})")
        if prev and prev[1] > 0 >= m:
            be = prev[0] + prev[1] * (bp - prev[0]) / (prev[1] - m)
        prev = (bp, m)
    print(f"  breakeven slippage: {f'{be:.1f} bp/fill' if be else 'beyond 30bp' if prev[1]>0 else 'below 0bp'}")

    print("\nKill checks (K-form):")
    span_y = (df15['time'].iloc[-1] - df15['time'].iloc[0]) / (365.25 * 86400)
    best = max(means, key=means.get)
    rs_wo = np.array([t["net_r"] for t in trades if half_label(t["t_entry"]) != best])
    pb = k5_bootstrap(trades, len(trades) / span_y)
    print(f"  K1 pooled expectancy: {rs.mean():+.4f}R -> {'KILL' if rs.mean()<=0 else 'pass'}")
    print(f"  K2 windows negative: {neg}/{len(by_w)} -> {'KILL' if neg > len(by_w)/2 else 'pass'}")
    print(f"  K3 breakeven slippage: {'KILL' if (be is not None and be < 3) else 'pass'}")
    print(f"  K4 without best window ({best}): {rs_wo.mean():+.4f}R -> "
          f"{'KILL' if rs_wo.mean()<=0 else 'pass'}")
    print(f"  K5 P(breach Classic in 1y at 0.5% risk): {pb:.1%} -> "
          f"{'FAIL AT VENUE' if pb > 0.5 else 'pass'} (closed-trade approx, optimistic)")
    pd.DataFrame(trades).to_csv(os.path.join(HERE, "volspike_trades.csv"), index=False)


if __name__ == "__main__":
    main()
