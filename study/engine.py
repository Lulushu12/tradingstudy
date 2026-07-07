"""Backtest engine.

Trade model (fully causal):
  - Strategy marks a signal at bar i (evaluated on bar-i CLOSE).
  - Entry = OPEN of bar i+1 (next bar). Fee charged on entry+exit notional.
  - Fixed R:R. risk_dist = |entry - stop|. target = entry +/- RR*risk_dist.
  - Walk forward bar-by-bar until stop or target hit, or max_bars (timeout -> MTM at close).
  - Intrabar ordering when both stop & target inside one bar: 'nearest_open'
    (level closer to that bar's open resolves first). 'stop_first' = pessimistic bound.

Fees: sized so a full 1R loss = 1% equity (risk_frac). Round-trip fee expressed in R:
      fee_R = fee_rt / stop_dist_frac,  where stop_dist_frac = risk_dist/entry.
Net R per trade = gross_R - fee_R.

Equity: process trades in EXIT order; each risks `risk_frac` of equity at ENTRY time
(concurrency allowed). Reports winrate, expectancy, and drawdown.
"""
import numpy as np
import pandas as pd

FEE_RT = 0.0008          # 0.04% taker each side, round trip
RISK_FRAC = 0.01         # 1% risk per trade

def simulate_trades(df, entries, side, stop_dist, rr,
                    max_bars=500, resolve="nearest_open", slippage_frac=0.0):
    """
    df: enriched signal-TF frame (needs open/high/low/close/time/dt).
    entries: integer array of bar indices where a signal fired (entry at index+1 open).
    side: array of +1 (long) / -1 (short) aligned with entries.
    stop_dist: array of stop distance in PRICE aligned with entries.
    rr: reward:risk multiple (target dist = rr*stop_dist).
    Returns a trades DataFrame.
    """
    o = df["open"].values; h = df["high"].values; l = df["low"].values
    c = df["close"].values; t = df["time"].values
    n = len(df)
    rows = []
    for k in range(len(entries)):
        si = entries[k]
        ei = si + 1
        if ei >= n:
            continue
        s = side[k]
        entry = o[ei] * (1 + s*slippage_frac)   # adverse slippage on entry
        rdist = stop_dist[k]
        if not np.isfinite(rdist) or rdist <= 0:
            continue
        if s > 0:
            stop = entry - rdist; target = entry + rr*rdist
        else:
            stop = entry + rdist; target = entry - rr*rdist
        sdf = rdist/entry
        outcome = None; exit_price = None; exit_i = None
        end = min(ei+max_bars, n)
        for j in range(ei, end):
            hj, lj, oj = h[j], l[j], c[j]  # oj unused placeholder
            hit_stop = (lj <= stop) if s > 0 else (hj >= stop)
            hit_tgt  = (hj >= target) if s > 0 else (lj <= target)
            if hit_stop and hit_tgt:
                if resolve == "stop_first":
                    first = "stop"
                else:  # nearest_open
                    bar_open = o[j]
                    first = "stop" if abs(bar_open-stop) <= abs(bar_open-target) else "target"
                if first == "stop":
                    outcome, exit_price, exit_i = "stop", stop, j
                else:
                    outcome, exit_price, exit_i = "target", target, j
                break
            elif hit_stop:
                outcome, exit_price, exit_i = "stop", stop, j; break
            elif hit_tgt:
                outcome, exit_price, exit_i = "target", target, j; break
        if outcome is None:
            outcome, exit_price, exit_i = "timeout", c[end-1], end-1
        # gross R
        if outcome == "target":
            gross_R = rr
        elif outcome == "stop":
            gross_R = -1.0
        else:  # timeout, mark to market
            gross_R = s*(exit_price-entry)/rdist
        fee_R = FEE_RT/sdf
        net_R = gross_R - fee_R
        rows.append(dict(
            entry_i=ei, exit_i=exit_i, entry_time=t[ei], exit_time=t[exit_i],
            side=s, entry=entry, stop=stop, target=target, exit=exit_price,
            stop_dist_frac=sdf, bars_held=exit_i-ei, outcome=outcome,
            gross_R=gross_R, fee_R=fee_R, net_R=net_R))
    return pd.DataFrame(rows)

def equity_stats(trades, risk_frac=RISK_FRAC, start=10000.0):
    """Realized equity curve stepping at each exit; each trade risks risk_frac of
    equity at ENTRY time (concurrency allowed). Returns metrics dict + curve."""
    if len(trades) == 0:
        return {"n": 0}, None
    tr = trades.sort_values("entry_time").reset_index(drop=True)
    # We need equity at entry to size; approximate by processing in entry order
    # and realizing PnL at exit. To keep concurrency, track realized equity and
    # a list of open PnL contributions settled at exit_time.
    events = []  # (time, type, k)
    for k, row in tr.iterrows():
        events.append((row["entry_time"], 0, k))  # size at entry
        events.append((row["exit_time"], 1, k))   # settle at exit
    events.sort(key=lambda x: (x[0], x[1]))
    equity = start
    size_at_entry = {}
    realized = []
    eq_curve = []
    for time_, typ, k in events:
        if typ == 0:
            size_at_entry[k] = equity  # equity snapshot for sizing
        else:
            e0 = size_at_entry.get(k, equity)
            pnl = risk_frac * e0 * tr.loc[k, "net_R"]
            equity += pnl
            realized.append((time_, equity))
            eq_curve.append((time_, equity))
    curve = pd.DataFrame(eq_curve, columns=["time", "equity"])
    curve["dt"] = pd.to_datetime(curve["time"], unit="s", utc=True)
    # drawdown
    peak = curve["equity"].cummax()
    dd = (curve["equity"]-peak)/peak
    max_dd = dd.min()
    # monthly returns
    curve = curve.set_index("dt")
    monthly = curve["equity"].resample("ME").last().pct_change(fill_method=None).dropna()
    # daily drawdown: worst intra-day drop of realized equity
    daily = curve["equity"].resample("D").agg(["first","min","last","max"])
    daily_dd = ((daily["min"]-daily["max"].cummax().shift().fillna(daily["max"]))).min()  # rough
    wins = (tr["outcome"]=="target").sum()
    resolved = tr["outcome"].isin(["target","stop"]).sum()
    m = {
        "n": len(tr),
        "resolved": int(resolved),
        "winrate": wins/resolved if resolved else np.nan,
        "winrate_incl_timeout": wins/len(tr),
        "gross_R_sum": tr["gross_R"].sum(),
        "net_R_sum": tr["net_R"].sum(),
        "avg_net_R": tr["net_R"].mean(),
        "expectancy_net_R": tr["net_R"].mean(),
        "avg_fee_R": tr["fee_R"].mean(),
        "final_equity": equity,
        "total_return": equity/start-1,
        "max_dd": max_dd,
        "n_months": len(monthly),
        "monthly_mean": monthly.mean(),
        "monthly_median": monthly.median(),
        "monthly_min": monthly.min(),
        "monthly_pos_frac": (monthly>0).mean(),
        "avg_stop_frac": tr["stop_dist_frac"].mean(),
    }
    return m, curve

def fmt(m):
    if m.get("n",0)==0: return "no trades"
    return (f"n={m['n']} resolved={m['resolved']} WR={m['winrate']:.1%} "
            f"expR={m['expectancy_net_R']:+.3f} feeR={m['avg_fee_R']:.3f} "
            f"ret={m['total_return']:+.1%} maxDD={m['max_dd']:.1%} "
            f"mo_mean={m['monthly_mean']:+.2%} mo_min={m['monthly_min']:+.2%} "
            f"mo_pos={m['monthly_pos_frac']:.0%} stop%={m['avg_stop_frac']:.3%}")
