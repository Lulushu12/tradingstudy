"""Shared machinery for the low R:R / high winrate investigation.

Two things here that the earlier study did not have:

1. A Breakout-specific cost model. Breakout charges $3.50 per side per $10,000
   traded (0.035% per side, 0.07% round trip) PLUS an overnight financing fee of
   5 bps of notional levied at 00:00 UTC. The earlier study only modelled the
   0.08% round-trip commission. The overnight fee is a per-night cost that scales
   with holding time, and on a high timeframe system it is not small.

   Expressed in R (where 1R = risk_frac of equity):
       notional / equity = risk_frac / stop_frac
       commission cost as fraction of equity = comm_rt * notional/equity
       => comm_R  = comm_rt / stop_frac
       => carry_R = overnight_bps * nights / stop_frac
       => cost_R  = (comm_rt + slip_rt + overnight_bps*nights) / stop_frac
   Both terms scale as 1/stop_frac, so a wide stop dilutes commission AND carry,
   but carry keeps accruing while the trade is open.

2. Barrier resolution on the 5-minute path with a full R:R ladder resolved in a
   single forward walk. At low R:R the target sits close to the entry, so the
   same-bar stop/target ambiguity that a 4H bar leaves unresolved is exactly
   where the answer lives. Resolving on 5m instead of 4H is not a nicety here.
"""
import os
import numpy as np
import pandas as pd

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

# ---------------------------------------------------------------- cost model
COMM_RT = 0.0007        # 0.035% per side, verified against Breakout's published schedule
SLIP_RT = 0.0002        # 1 bp per side market-order slippage assumption (swept later)
OVERNIGHT = 0.0005      # 5 bps of notional at 00:00 UTC, per Breakout
RISK_FRAC = 0.01

def cost_R(stop_frac, nights, comm_rt=COMM_RT, slip_rt=SLIP_RT, overnight=OVERNIGHT):
    """Total round-trip cost of a trade expressed in R."""
    return (comm_rt + slip_rt + overnight * np.asarray(nights)) / np.asarray(stop_frac)

def nights_between(t_entry, t_exit):
    """Number of 00:00 UTC boundaries strictly crossed between two unix timestamps."""
    return np.maximum(0, np.floor(np.asarray(t_exit) / 86400.0).astype(np.int64)
                        - np.floor(np.asarray(t_entry) / 86400.0).astype(np.int64))

def breakeven_wr(rr, stop_frac, nights, **kw):
    """Winrate at which net expectancy is zero, given rr and the realised cost."""
    return (1.0 + cost_R(stop_frac, nights, **kw)) / (1.0 + rr)

def fair_wr(rr):
    """Driftless barrier odds: P(hit +rr*S before -S) = 1/(1+rr).

    This is the line the whole question lives on. Cutting R:R buys winrate at
    exactly fair odds and creates nothing.
    """
    return 1.0 / (1.0 + rr)

# ------------------------------------------------------------- path resolver
def load_path(tf="5m"):
    p = pd.read_parquet(os.path.join(DATA, f"{tf}.parquet")).sort_values("time")
    p = p.reset_index(drop=True)
    return (p["time"].values.astype(np.int64), p["open"].values,
            p["high"].values, p["low"].values, p["close"].values)

def resolve_ladder(path, t_entry, entry, side, rdist, rr_grid, max_hold_sec):
    """Resolve ONE trade against every rr in rr_grid in a single forward walk.

    rr_grid must be ascending. Targets are nested, so once the stop is touched
    every still-unresolved (larger) target is a loss. Same-bar stop+target is
    broken by nearest-open on the 5m bar, which is the least-assumption tiebreak
    available without tick data.

    Returns (outcome[], exit_ts[]) aligned with rr_grid.
       outcome: +1 target, -1 stop, 0 timeout (marked to market by caller)
    """
    pt, po, ph, pl, pc = path
    n_rr = len(rr_grid)
    out = np.zeros(n_rr, dtype=np.int8)
    ets = np.zeros(n_rr, dtype=np.int64)
    epx = np.zeros(n_rr, dtype=float)

    if side > 0:
        stop = entry - rdist
        tgts = entry + rr_grid * rdist
    else:
        stop = entry + rdist
        tgts = entry - rr_grid * rdist

    start = np.searchsorted(pt, t_entry, side="left")
    end = np.searchsorted(pt, t_entry + max_hold_sec, side="right")
    end = min(end, len(pt))

    k = 0  # index of the smallest unresolved rr
    j = start
    while j < end and k < n_rr:
        hj = ph[j]; lj = pl[j]; oj = po[j]
        if side > 0:
            hit_stop = lj <= stop
            # resolve every pending target reached on this bar
            while k < n_rr and hj >= tgts[k]:
                if hit_stop and abs(oj - stop) <= abs(oj - tgts[k]):
                    out[k] = -1; ets[k] = pt[j]; epx[k] = stop
                else:
                    out[k] = 1; ets[k] = pt[j]; epx[k] = tgts[k]
                k += 1
        else:
            hit_stop = hj >= stop
            while k < n_rr and lj <= tgts[k]:
                if hit_stop and abs(oj - stop) <= abs(oj - tgts[k]):
                    out[k] = -1; ets[k] = pt[j]; epx[k] = stop
                else:
                    out[k] = 1; ets[k] = pt[j]; epx[k] = tgts[k]
                k += 1
        if hit_stop:
            while k < n_rr:
                out[k] = -1; ets[k] = pt[j]; epx[k] = stop
                k += 1
            break
        j += 1
    if k < n_rr:
        jj = max(start, min(j, end) - 1)
        if jj >= len(pt):
            jj = len(pt) - 1
        while k < n_rr:
            out[k] = 0; ets[k] = pt[jj]; epx[k] = pc[jj]
            k += 1
    return out, ets, epx

def trades_for_signals(df, sig_idx, sig_side, atr_mult, rr_grid, path,
                       max_hold_days=50, stop_dist=None, min_stop_frac=None):
    """Build a trade table for every (signal, rr) pair.

    Signal is read at bar CLOSE of df row i, entry at OPEN of row i+1, resolved on
    the fine path. Nothing here looks ahead.

    stop_dist: optional explicit per-signal stop distance in PRICE, aligned with
        sig_idx. When given it overrides atr_mult. Needed for rule sets whose stop
        is not a plain ATR multiple (e.g. the FROZEN_SPEC ATR-band stop).
    min_stop_frac: optional entry invalidation. Signals whose stop distance is a
        smaller fraction of entry than this are skipped entirely.
    """
    o = df["open"].values; t = df["time"].values; atrv = df["atr14"].values
    n = len(df)
    rr_grid = np.asarray(sorted(rr_grid), dtype=float)
    max_hold_sec = int(max_hold_days * 86400)
    rows = []
    for k_sig, (i, s) in enumerate(zip(sig_idx, sig_side)):
        ei = i + 1
        if ei >= n:
            continue
        if stop_dist is not None:
            rdist = stop_dist[k_sig]
        else:
            rdist = atr_mult * atrv[i]
        if not np.isfinite(rdist) or rdist <= 0:
            continue
        if min_stop_frac is not None and rdist / o[ei] < min_stop_frac:
            continue
        entry = o[ei]; t_entry = int(t[ei])
        sf = rdist / entry
        out, ets, epx = resolve_ladder(path, t_entry, entry, s, rdist, rr_grid, max_hold_sec)
        for m, rr in enumerate(rr_grid):
            if out[m] == 1:
                gross = rr
            elif out[m] == -1:
                gross = -1.0
            else:
                gross = s * (epx[m] - entry) / rdist
            rows.append((rr, i, t_entry, int(ets[m]), s, sf, out[m], gross,
                         int(nights_between(t_entry, ets[m]))))
    tr = pd.DataFrame(rows, columns=["rr", "sig_i", "entry_time", "exit_time", "side",
                                     "stop_frac", "res", "gross_R", "nights"])
    if len(tr) == 0:
        return tr
    tr["cost_R"] = cost_R(tr["stop_frac"].values, tr["nights"].values)
    tr["net_R"] = tr["gross_R"] - tr["cost_R"]
    tr["hold_h"] = (tr["exit_time"] - tr["entry_time"]) / 3600.0
    tr["dt"] = pd.to_datetime(tr["entry_time"], unit="s", utc=True)
    return tr

# ------------------------------------------------------------------ reporting
def sequential_equity(tr, risk=RISK_FRAC, start=10000.0, mode="single"):
    """Equity walk. 'single' takes at most one position at a time (skips signals
    fired while a trade is open), 'concurrent' takes every signal.

    Realised-equity drawdown only. With one position risking `risk`, floating
    drawdown exceeds realised by at most ~risk, so realised DD is a usable proxy
    in single mode. In concurrent mode it is NOT, and that is flagged.
    """
    if len(tr) == 0:
        return {}, None
    tr = tr.sort_values("entry_time").reset_index(drop=True)
    eq = start; peak = start; maxdd = 0.0
    busy = -1
    curve = []; taken = []
    for r in tr.itertuples():
        if mode == "single" and r.entry_time < busy:
            continue
        eq += risk * eq * r.net_R
        busy = r.exit_time
        peak = max(peak, eq)
        maxdd = min(maxdd, (eq - peak) / peak)
        curve.append((r.exit_time, eq))
        taken.append(r)
    if not taken:
        return {}, None
    c = pd.DataFrame(curve, columns=["time", "equity"])
    c["dt"] = pd.to_datetime(c["time"], unit="s", utc=True)
    u = pd.DataFrame(taken)
    wins = (u["res"] == 1).sum(); res = (u["res"] != 0).sum()
    streak = mx = 0
    for w in (u["net_R"] > 0).values:
        if w: streak = 0
        else: streak += 1; mx = max(mx, streak)
    span_years = (c["time"].iloc[-1] - c["time"].iloc[0]) / (365.25 * 86400)
    span_months = span_years * 12
    cm = c.set_index("dt")["equity"]
    monthly = cm.resample("ME").last().ffill().pct_change(fill_method=None).dropna()
    m = dict(
        n=len(u), wr=wins / res if res else np.nan,
        expR=u["net_R"].mean(), gross_expR=u["gross_R"].mean(),
        costR=u["cost_R"].mean(), nights=u["nights"].mean(),
        hold_h=u["hold_h"].mean(), median_hold_h=u["hold_h"].median(),
        trades_per_month=len(u) / span_months if span_months > 0 else np.nan,
        total=eq / start - 1,
        cagr=(eq / start) ** (1 / span_years) - 1 if span_years > 0 else np.nan,
        maxdd=maxdd, lose_streak=mx,
        mo_mean=monthly.mean(), mo_min=monthly.min(),
        mo_pos=(monthly > 0).mean(), n_months=len(monthly),
        timeouts=(u["res"] == 0).sum(),
    )
    return m, c

def summarise(tr, label=""):
    """Pooled per-trade stats, no equity path, no position-count assumption."""
    if len(tr) == 0:
        return dict(label=label, n=0)
    wins = (tr["res"] == 1).sum(); res = (tr["res"] != 0).sum()
    wr = wins / res if res else np.nan
    sf = tr["stop_frac"].mean(); nights = tr["nights"].mean()
    rr = tr["rr"].iloc[0]
    return dict(
        label=label, n=len(tr), wr=wr,
        gross_expR=tr["gross_R"].mean(), expR=tr["net_R"].mean(),
        costR=tr["cost_R"].mean(), stop_frac=sf, nights=nights,
        hold_h=tr["hold_h"].mean(),
        be_wr=breakeven_wr(rr, sf, nights), fair_wr=fair_wr(rr),
        se_wr=np.sqrt(wr * (1 - wr) / res) if res else np.nan,
    )
