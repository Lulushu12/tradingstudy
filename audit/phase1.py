"""PHASE 1: historical walk-forward on studied data, both variants, rules
exactly per FROZEN_SPEC.md as amended (0.5% risk) and AUDIT_COMMITMENTS.md.
NO optimization. NO holdout contact (loader refuses quarantined paths via
data_check convention; this file reads only audit/studied_15m.parquet and
the 1D csv filtered to the studied span).

Guards implemented:
- No look-ahead: signals close on bar t, entry at bar t+1 open. All
  indicator values are causal (validated port). SL uses bars t-5..t-1.
- Fractal confirmation lag: pivots confirm 2 bars later (in the port).
- Same-bar SL+TP ambiguity: resolved as SL first (worst case), counted.
- Adverse gaps through SL: exit at the bar's open (worse than SL).
  Favorable gaps through TP: exit at the bar's open (better, symmetric).
- Costs on every fill: commission 0.04%/side, slippage 1bp/fill, swap
  0.0055% of notional per 4h UTC boundary crossed while open.
- Concurrent positions are independent (same or opposite direction).
- Dedup: leg consumption per variant per direction (frozen rule).

Sizing: 0.5% of current realized equity per trade (Amendment 1).
Windows: calendar half-years 2021H1..2026H1 (the frozen file says "ten"
but enumerates 2021H1 through 2026H1, which is eleven; the enumeration
governs and all are reported).
"""
import os
import sys
from collections import defaultdict

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mcb_port import wavetrend, mfi_clone, atr_rma
from census import build_events, div_event_bars, WINDOW

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STUDIED_END = 1782060300

COMMISSION_RT = 0.0008          # 0.04% per side
SLIP_PER_FILL = 0.0001          # 1 bp, baseline
SWAP_PER_4H = 0.000055          # 0.0055% per 4h boundary
RISK_FRAC = 0.005               # Amendment 1
MIN_STOP_PCT = 0.006
START_EQ = 10_000.0
DD_LIMIT = 0.06                 # 1-Step Classic static, from starting balance
DAILY_LIMIT = 0.03


# ── signal generation with frozen dedup (leg consumption) ────────────────────

def variant_a_trades(ev):
    wt_bull, wt_bear, mfi_bull, mfi_bear = div_event_bars(ev)
    out = []
    for direction, wts, mfis in (("long", wt_bull, mfi_bull),
                                 ("short", wt_bear, mfi_bear)):
        pairs = []
        for wb in wts:
            for mb in mfis[np.abs(mfis - wb) <= WINDOW]:
                pairs.append((max(wb, mb), wb, mb))
        pairs.sort()
        used_wt, used_mfi = set(), set()
        for sig, wb, mb in pairs:
            if wb in used_wt or mb in used_mfi:
                continue
            used_wt.add(wb)
            used_mfi.add(mb)
            out.append((sig, direction, "A"))
    return sorted(out)


def variant_b_trades(ev, n):
    wt_bull, wt_bear, mfi_bull, mfi_bear = div_event_bars(ev)
    legs = {("wt", "long"): wt_bull, ("wt", "short"): wt_bear,
            ("mfi", "long"): mfi_bull, ("mfi", "short"): mfi_bear}
    # collect completions chronologically, then consume legs
    completions = []
    for (leg1_osc, direction), conf_bars in legs.items():
        leg2_osc = "mfi" if leg1_osc == "wt" else "wt"
        pre = ev["pre_mfi"] if leg2_osc == "mfi" else ev["pre_wt"]
        raw = pre.pre_bull if direction == "long" else pre.pre_bear
        anchor = pre.bull_ref_bar if direction == "long" else pre.bear_ref_bar
        tick = (ev["tick_up"] if direction == "long" else ev["tick_dn"])[leg2_osc]
        for u in conf_bars:
            p = u - 2
            for t in range(u, min(p + WINDOW, n - 1) + 1):
                if raw[t] and tick[t]:
                    completions.append((t, direction, leg1_osc, u, int(anchor[t])))
                    break
    completions.sort()
    out = []
    used = set()
    for t, direction, leg1_osc, u, a in completions:
        leg2_osc = "mfi" if leg1_osc == "wt" else "wt"
        k1 = (leg1_osc, direction, "div", u)
        k2 = (leg2_osc, direction, "anchor", a)
        if k1 in used or k2 in used:
            continue
        used.add(k1)
        used.add(k2)
        out.append((t, direction, "B"))
    return sorted(out)


# ── trade simulation ─────────────────────────────────────────────────────────

def simulate(signals, df, atr, slip=SLIP_PER_FILL):
    """Resolve each signal into a trade dict, or a skip reason."""
    t_arr = df["time"].to_numpy()
    o = df["open"].to_numpy(float)
    h = df["high"].to_numpy(float)
    l = df["low"].to_numpy(float)
    c = df["close"].to_numpy(float)
    n = len(df)
    up_band = c + atr
    dn_band = c - atr

    trades, skipped_stop, still_open, ambiguous = [], 0, 0, 0
    for sig, direction, variant in signals:
        e_bar = sig + 1
        if e_bar >= n:
            continue
        entry = o[e_bar]
        w = slice(sig - 5, sig)             # bars t-5..t-1
        if direction == "long":
            sl = dn_band[w].min()
            stop_d = entry - sl
        else:
            sl = up_band[w].max()
            stop_d = sl - entry
        if not np.isfinite(stop_d) or stop_d <= 0:
            skipped_stop += 1
            continue
        if stop_d / entry < MIN_STOP_PCT:
            skipped_stop += 1
            continue
        tp = entry + 2 * stop_d if direction == "long" else entry - 2 * stop_d

        gross_r = None
        x_bar = None
        for b in range(e_bar, n):
            if direction == "long":
                gap_sl = o[b] <= sl
                gap_tp = o[b] >= tp
                hit_sl = l[b] <= sl
                hit_tp = h[b] >= tp
            else:
                gap_sl = o[b] >= sl
                gap_tp = o[b] <= tp
                hit_sl = h[b] >= sl
                hit_tp = l[b] <= tp
            if b == e_bar:
                gap_sl = gap_tp = False     # entry is at this bar's open
            if gap_sl:
                px = o[b]
                gross_r = ((px - entry) if direction == "long" else (entry - px)) / stop_d
                x_bar = b
                break
            if gap_tp:
                px = o[b]
                gross_r = ((px - entry) if direction == "long" else (entry - px)) / stop_d
                x_bar = b
                break
            if hit_sl and hit_tp:
                ambiguous += 1
                gross_r, x_bar = -1.0, b     # worst case: stop first
                break
            if hit_sl:
                gross_r, x_bar = -1.0, b
                break
            if hit_tp:
                gross_r, x_bar = 2.0, b
                break
        if gross_r is None:                  # open at end of data
            still_open += 1
            px = c[n - 1]
            gross_r = ((px - entry) if direction == "long" else (entry - px)) / stop_d
            x_bar = n - 1

        n_swaps = int(t_arr[x_bar] // 14400) - int(t_arr[e_bar] // 14400)
        cost_pct = COMMISSION_RT + 2 * slip + n_swaps * SWAP_PER_4H
        cost_r = cost_pct * entry / stop_d
        trades.append(dict(sig=sig, e_bar=e_bar, x_bar=x_bar, dir=direction,
                           variant=variant, entry=entry, stop_d=stop_d,
                           gross_r=gross_r, cost_r=cost_r,
                           net_r=gross_r - cost_r, n_swaps=n_swaps,
                           t_entry=t_arr[e_bar], t_exit=t_arr[x_bar]))
    return trades, dict(skipped_stop=skipped_stop, still_open=still_open,
                        ambiguous_bars=ambiguous)


# ── regimes (pre-committed formulas) ─────────────────────────────────────────

def regime_labels():
    d = pd.read_csv(os.path.join(ROOT, "BINANCE_BTCUSDT.P, 1D.csv"),
                    usecols=lambda k: k in ["time", "close"])
    d = d[d["time"] <= STUDIED_END].reset_index(drop=True)
    d["dt"] = pd.to_datetime(d["time"], unit="s", utc=True)
    d["sma200"] = d["close"].rolling(200).mean()
    sma_prev = d["sma200"].shift(20)
    trend = np.where((d["close"] > d["sma200"]) & (d["sma200"] > sma_prev), "bull",
             np.where((d["close"] < d["sma200"]) & (d["sma200"] < sma_prev), "bear",
                      "chop"))
    lr = np.log(d["close"] / d["close"].shift(1))
    rv = lr.rolling(30).std() * np.sqrt(365)
    med = rv.median()
    vol = np.where(rv > med, "highvol", "lowvol")
    days = d["dt"].dt.floor("D")
    return dict(zip(days, trend)), dict(zip(days, vol))


# ── statistics ───────────────────────────────────────────────────────────────

def half_label(ts):
    dt = pd.to_datetime(ts, unit="s", utc=True)
    return f"{dt.year}H{1 if dt.month <= 6 else 2}"


def streaks(rs, texit):
    worst, worst_span, cur, start = 0, 0, 0, None
    for r, tx in zip(rs, texit):
        if r < 0:
            cur += 1
            if start is None:
                start = tx
            if cur > worst:
                worst, worst_span = cur, tx - start
        else:
            cur, start = 0, None
    return worst, worst_span / 86400.0


def block(trades, label):
    if not trades:
        return f"{label}: no trades\n"
    rs = np.array([t["net_r"] for t in trades])
    gross_pos = rs[rs > 0].sum()
    gross_neg = -rs[rs < 0].sum()
    pf = gross_pos / gross_neg if gross_neg else float("inf")
    order = np.argsort([t["t_exit"] for t in trades])
    rs_x = rs[order]
    tx = np.array([t["t_exit"] for t in trades])[order]
    ls, ls_days = streaks(rs_x, tx)
    win = np.mean(rs > 0)
    q = np.quantile(rs, [0.05, 0.25, 0.5, 0.75, 0.95])
    return (f"{label}: n={len(rs)} expectancy={rs.mean():+.4f}R "
            f"(std {rs.std():.3f}) win={win:.1%} PF={pf:.3f} "
            f"maxLoseStreak={ls} ({ls_days:.1f}d) "
            f"q05/25/50/75/95={q[0]:+.2f}/{q[1]:+.2f}/{q[2]:+.2f}/{q[3]:+.2f}/{q[4]:+.2f}\n")


def equity_curve(trades):
    eq = START_EQ
    curve = []
    for t in sorted(trades, key=lambda x: x["t_exit"]):
        eq *= (1 + RISK_FRAC * t["net_r"])
        curve.append((t["t_exit"], eq))
    peak, mdd = START_EQ, 0.0
    for _, e in curve:
        peak = max(peak, e)
        mdd = max(mdd, 1 - e / peak)
    return curve, mdd


def k5_bootstrap(trades, trades_per_year, n_paths=10_000, block_len=25, seed=7):
    """Probability of breaching Classic limits within one trading year.
    Closed-trade approximation: floating PnL not modeled, so the estimate
    is OPTIMISTIC (true breach probability is higher)."""
    rng = np.random.default_rng(seed)
    seq = sorted(trades, key=lambda x: x["t_exit"])
    rs = np.array([t["net_r"] for t in seq])
    days = np.array([t["t_exit"] // 86400 for t in seq])
    n = len(rs)
    breach = 0
    m = int(trades_per_year)
    for _ in range(n_paths):
        idx = []
        while len(idx) < m:
            s = rng.integers(0, n)
            idx.extend(((s + k) % n) for k in range(block_len))
        idx = idx[:m]
        eq = START_EQ
        floor = START_EQ * (1 - DD_LIMIT)
        day_start_eq = eq
        cur_day = None
        hit = False
        for i in idx:
            if cur_day != days[i]:
                cur_day = days[i]
                day_start_eq = eq
            eq *= (1 + RISK_FRAC * rs[i])
            if eq <= floor or eq <= day_start_eq * (1 - DAILY_LIMIT):
                hit = True
                break
        breach += hit
    return breach / n_paths


def sweep(signals, df, atr):
    rows = []
    for bp in (0, 1, 2, 3, 5, 10, 15, 20):
        tr, _ = simulate(signals, df, atr, slip=bp * 1e-4)
        rs = np.array([t["net_r"] for t in tr])
        rows.append((bp, len(rs), rs.mean()))
    return rows


def main():
    df = pd.read_parquet(os.path.join(ROOT, "audit", "studied_15m.parquet"))
    df = df[["time", "dt", "open", "high", "low", "close", "Volume"]].reset_index(drop=True)
    assert df["time"].iloc[-1] <= STUDIED_END
    n = len(df)
    ev = build_events(df)
    atr = atr_rma(df["high"].to_numpy(float), df["low"].to_numpy(float),
                  df["close"].to_numpy(float), 14)
    trend_map, vol_map = regime_labels()

    out = ["# PHASE 1 REPORT", "",
           "Generated by audit/phase1.py. No optimization anywhere. Studied data",
           "only. Surviving means NOT YET FALSIFIED, nothing more. In-sample",
           "results prove nothing; the rules evolved watching this market.", "",
           f"Costs: commission {COMMISSION_RT:.4%} RT, slippage {SLIP_PER_FILL:.4%}/fill,",
           f"swap {SWAP_PER_4H:.4%} per 4h boundary. Risk {RISK_FRAC:.1%}/trade.",
           "Same-bar SL+TP resolved as SL (worst case). Adverse gaps exit at open.", ""]

    for name, signals in (("A", variant_a_trades(ev)),
                          ("B", variant_b_trades(ev, n))):
        trades, meta = simulate(signals, df, atr)
        span_years = (df["time"].iloc[-1] - df["time"].iloc[0]) / (365.25 * 86400)
        tpy = len(trades) / span_years
        out.append(f"## VARIANT {name}")
        out.append(f"signals={len(signals)} trades={len(trades)} "
                   f"skipped(minstop/nostop)={meta['skipped_stop']} "
                   f"still_open_at_end={meta['still_open']} "
                   f"same-bar-SLTP={meta['ambiguous_bars']} "
                   f"trades/year={tpy:.0f}")
        out.append("")
        out.append("### Pooled")
        out.append(block(trades, "pooled").rstrip())
        rs = np.array([t["net_r"] for t in trades])
        _, mdd = equity_curve(trades)
        out.append(f"equity max drawdown at {RISK_FRAC:.1%} risk (closed-trade): {mdd:.1%}")
        out.append("")
        out.append("### Per window")
        wins_neg = 0
        by_w = defaultdict(list)
        for t in trades:
            by_w[half_label(t["t_entry"])].append(t)
        window_means = {}
        for w in sorted(by_w):
            out.append(block(by_w[w], w).rstrip())
            m = np.mean([t["net_r"] for t in by_w[w]])
            window_means[w] = m
            wins_neg += m < 0
        out.append("")
        out.append("### Per regime (entry-day label)")
        by_r = defaultdict(list)
        for t in trades:
            day = pd.to_datetime(t["t_entry"], unit="s", utc=True).floor("D")
            by_r[trend_map.get(day, "na")].append(t)
            by_r[vol_map.get(day, "na")].append(t)
        for r in ("bull", "bear", "chop", "highvol", "lowvol", "na"):
            if by_r.get(r):
                out.append(block(by_r[r], r).rstrip())
        out.append("")
        out.append("### Cost sweep (slippage bp/fill -> expectancy R)")
        rows = sweep(signals, df, atr)
        for bp, cnt, m in rows:
            out.append(f"  {bp:3d} bp: {m:+.4f}R  (n={cnt})")
        # linear interpolate breakeven
        be = None
        for (b1, _, m1), (b2, _, m2) in zip(rows, rows[1:]):
            if m1 > 0 >= m2:
                be = b1 + m1 * (b2 - b1) / (m1 - m2)
        out.append(f"  breakeven slippage: "
                   f"{'not reached within sweep' if be is None else f'{be:.1f} bp/fill'}")
        out.append("")
        out.append("### Kill thresholds (frozen in AUDIT_COMMITMENTS.md)")
        k1 = rs.mean() <= 0
        k2 = wins_neg > len(by_w) / 2
        k3 = (be is not None and be < 3.0)
        best_w = max(window_means, key=window_means.get)
        rs_wo = np.array([t["net_r"] for t in trades
                          if half_label(t["t_entry"]) != best_w])
        k4 = rs_wo.mean() <= 0 if len(rs_wo) else True
        p_breach = k5_bootstrap(trades, tpy)
        k5 = p_breach > 0.5
        out.append(f"  K1 expectancy<=0: {'KILL' if k1 else 'pass'} ({rs.mean():+.4f}R)")
        out.append(f"  K2 >half windows negative: {'KILL' if k2 else 'pass'} "
                   f"({wins_neg}/{len(by_w)} negative)")
        out.append(f"  K3 breakeven slip < 3bp: {'KILL' if k3 else 'pass'}")
        out.append(f"  K4 expectancy<=0 without best window ({best_w}): "
                   f"{'KILL' if k4 else 'pass'} ({rs_wo.mean():+.4f}R)")
        out.append(f"  K5 P(breach Classic limits in 1y) > 50%: "
                   f"{'FAIL AT VENUE' if k5 else 'pass'} "
                   f"(estimate {p_breach:.1%}, OPTIMISTIC: floating PnL not modeled)")
        out.append("")
        # save trade log
        pd.DataFrame(trades).to_csv(
            os.path.join(ROOT, "audit", f"phase1_trades_{name}.csv"), index=False)

    report = "\n".join(out) + "\n"
    with open(os.path.join(ROOT, "audit", "PHASE1_REPORT.md"), "w") as f:
        f.write(report)
    print(report)


if __name__ == "__main__":
    main()
