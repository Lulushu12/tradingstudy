"""Execution engine: 1m-path trade resolution + Breakout account simulation.

Causality contract, enforced here rather than trusted to callers:
  - A signal is evaluated on the CLOSE of timeframe bar t. Bar t stamped `dt`
    closes at dt + tf. Nothing after that instant may influence the decision.
  - The fill happens at the open of the 1m bar starting `delay_min` minutes
    after that close. Default delay is 1 minute (semi-auto: alert fires, human
    clicks). delay_min=0 would be an instant machine fill and is optimistic.
  - Stops and targets are resolved by walking the real 1m path. If a bar's
    range spans both stop and target, the STOP is taken. Always.
"""
import numpy as np
import pandas as pd
from numba import njit

TAKER = 0.0004          # 0.04% per side, Breakout published
SLIP = 0.0002           # 0.02% per side assumed, swept in sensitivity
MAX_LEV = {"BTCUSDT": 5.0, "ETHUSDT": 5.0}
DEFAULT_LEV = 2.0       # altcoins on Breakout


@njit(cache=True)
def _walk(fill_i, side, stop, target, hi, lo, op, cl, max_bars):
    """Resolve one trade on the 1m path. Returns (exit_i, exit_px, outcome).
    outcome: 1 target, -1 stop, 0 timeout."""
    n = hi.shape[0]
    end = fill_i + max_bars
    if end > n - 1:
        end = n - 1
    i = fill_i
    while i <= end:
        h = hi[i]
        l = lo[i]
        if side > 0:
            hit_s = l <= stop
            hit_t = h >= target
        else:
            hit_s = h >= stop
            hit_t = l <= target
        if hit_s:
            return i, stop, -1        # stop wins ties, always
        if hit_t:
            return i, target, 1
        i += 1
    return end, cl[end], 0


@njit(cache=True)
def _walk_all(fill_idx, sides, stops, targets, hi, lo, op, cl, max_bars):
    n = fill_idx.shape[0]
    ex_i = np.empty(n, dtype=np.int64)
    ex_p = np.empty(n, dtype=np.float64)
    out = np.empty(n, dtype=np.int64)
    for k in range(n):
        a, b, c = _walk(fill_idx[k], sides[k], stops[k], targets[k],
                        hi, lo, op, cl, max_bars)
        ex_i[k] = a
        ex_p[k] = b
        out[k] = c
    return ex_i, ex_p, out


def resolve(signals, m1, delay_min=1, max_hold_min=60 * 24 * 5,
            taker=TAKER, slip=SLIP):
    """signals: DataFrame with columns
         close_dt  (instant the decision bar closed, UTC)
         side      (+1 long, -1 short)
         stop_px, target_px   (raw prices, pre-cost)
       Returns a trade frame with net R and timing. Signals whose fill bar or
       stop/target is unusable are dropped and counted.
    """
    if len(signals) == 0:
        return pd.DataFrame()

    m1 = m1.reset_index(drop=True)
    t = m1["dt"].values.astype("datetime64[ns]")
    hi = m1["high"].to_numpy(np.float64)
    lo = m1["low"].to_numpy(np.float64)
    op = m1["open"].to_numpy(np.float64)
    cl = m1["close"].to_numpy(np.float64)

    s = signals.reset_index(drop=True).copy()
    want = (s["close_dt"] + pd.Timedelta(minutes=delay_min)).values.astype("datetime64[ns]")
    fi = np.searchsorted(t, want, side="left")

    ok = (fi < len(t) - 2)
    # the located 1m bar must actually be the requested minute (no gap jump)
    ok &= np.where(ok, t[np.clip(fi, 0, len(t) - 1)] == want, False)
    s, fi = s[ok].reset_index(drop=True), fi[ok]
    if len(s) == 0:
        return pd.DataFrame()

    side = s["side"].to_numpy(np.int64)
    raw_fill = op[fi]
    # slippage always against the trader
    fill = raw_fill * (1.0 + slip * side)

    stop = s["stop_px"].to_numpy(np.float64)
    tgt = s["target_px"].to_numpy(np.float64)

    good = np.where(side > 0, (stop < fill) & (tgt > fill),
                    (stop > fill) & (tgt < fill))
    s, fi, fill, stop, tgt, side = (s[good].reset_index(drop=True), fi[good],
                                    fill[good], stop[good], tgt[good], side[good])
    if len(s) == 0:
        return pd.DataFrame()

    ex_i, ex_p, out = _walk_all(fi, side, stop, tgt, hi, lo, op, cl, int(max_hold_min))

    exit_px = ex_p * (1.0 - slip * side)          # slippage on the exit too
    risk_px = np.abs(fill - stop)
    gross = (exit_px - fill) * side
    fee = (fill + exit_px) * taker
    net = gross - fee
    r = net / risk_px

    return pd.DataFrame({
        "close_dt": s["close_dt"].values,
        "entry_dt": t[fi],
        "exit_dt": t[ex_i],
        "side": side,
        "entry_px": fill,
        "stop_px": stop,
        "target_px": tgt,
        "exit_px": exit_px,
        "outcome": out,
        "stop_pct": risk_px / fill,
        "r": r,
        "hold_min": (ex_i - fi).astype(np.int64),
        **{c: s[c].values for c in s.columns
           if c not in ("close_dt", "side", "stop_px", "target_px")},
    })


# ---------------------------------------------------------------- account sim

def simulate(trades, start_equity=100_000.0, risk_pct=0.01, symbol="BTCUSDT",
             max_dd_pct=0.06, daily_loss_pct=0.03, max_concurrent=1,
             compound=True, enforce_limits=True):
    """Sequential account simulation under Breakout 1-Step Classic rules.

    - static max drawdown: equity may never touch start_equity*(1-max_dd_pct)
    - daily loss: equity may never fall 3% below the balance at the last
      00:30 UTC reset
    - leverage cap reduces size when the stop is tight; it does not skip trades
    - max_concurrent limits simultaneously open positions (signals arriving
      while full are skipped, which is what a human at a screen actually does)
    """
    if len(trades) == 0:
        return {"n": 0}, pd.DataFrame()

    tr = trades.sort_values("entry_dt").reset_index(drop=True)
    lev_cap = MAX_LEV.get(symbol, DEFAULT_LEV)

    eq = start_equity
    floor_static = start_equity * (1 - max_dd_pct)
    open_until = []            # exit timestamps of live positions
    rows = []
    day_anchor = None
    day_start_eq = start_equity
    breached = None

    # process by entry order, realise PnL at exit order -> use an event queue
    events = []
    for i, t in tr.iterrows():
        events.append((t["entry_dt"], 0, i))
    events.sort()

    pending = {}   # idx -> size info
    realised = []  # (exit_dt, idx)

    def reset_day(ts):
        nonlocal day_anchor, day_start_eq
        anchor = (pd.Timestamp(ts).normalize() + pd.Timedelta(minutes=30))
        if pd.Timestamp(ts) < anchor:
            anchor -= pd.Timedelta(days=1)
        if day_anchor is None or anchor > day_anchor:
            day_anchor = anchor
            day_start_eq = eq

    peak = start_equity
    max_dd = 0.0

    for ts, _, idx in events:
        t = tr.loc[idx]
        # settle everything that exited before this entry
        realised.sort()
        while realised and realised[0][0] <= ts:
            _, j = realised.pop(0)
            info = pending.pop(j)
            eq += info["risk_amt"] * tr.loc[j, "r"] * info["scale"]
            peak = max(peak, eq)
            max_dd = max(max_dd, (peak - eq) / peak)
            rows.append({"dt": tr.loc[j, "exit_dt"], "equity": eq, "idx": j})
            if enforce_limits:
                if eq <= floor_static and breached is None:
                    breached = ("static_dd", tr.loc[j, "exit_dt"])
                if eq <= day_start_eq * (1 - daily_loss_pct) and breached is None:
                    breached = ("daily_loss", tr.loc[j, "exit_dt"])
        if breached is not None:
            break

        reset_day(ts)
        open_until = [u for u in open_until if u > ts]
        if len(open_until) >= max_concurrent:
            continue

        base = eq if compound else start_equity
        risk_amt = base * risk_pct
        notional = risk_amt / max(t["stop_pct"], 1e-9)
        scale = min(1.0, (base * lev_cap) / notional)   # leverage cap bites
        pending[idx] = {"risk_amt": risk_amt, "scale": scale}
        realised.append((t["exit_dt"], idx))
        open_until.append(t["exit_dt"])

    # settle the tail
    realised.sort()
    for _, j in realised:
        if j in pending:
            info = pending.pop(j)
            eq += info["risk_amt"] * tr.loc[j, "r"] * info["scale"]
            peak = max(peak, eq)
            max_dd = max(max_dd, (peak - eq) / peak)
            rows.append({"dt": tr.loc[j, "exit_dt"], "equity": eq, "idx": j})

    curve = pd.DataFrame(rows).sort_values("dt").reset_index(drop=True)
    taken = curve["idx"].tolist() if len(curve) else []
    used = tr.loc[taken] if taken else tr.iloc[:0]

    stats = {
        "n": len(used),
        "n_signals": len(tr),
        "wr": float((used["outcome"] == 1).mean()) if len(used) else 0.0,
        "exp_r": float(used["r"].mean()) if len(used) else 0.0,
        "sum_r": float(used["r"].sum()) if len(used) else 0.0,
        "final_eq": eq,
        "total_ret": eq / start_equity - 1,
        "max_dd": max_dd,
        "breached": breached,
        "start": str(tr["entry_dt"].iloc[0]),
        "end": str(tr["exit_dt"].iloc[-1]),
    }
    return stats, curve


def monthly(curve, start_equity=100_000.0):
    if len(curve) == 0:
        return pd.Series(dtype=float)
    c = curve.set_index(pd.DatetimeIndex(curve["dt"]))["equity"]
    m = c.resample("ME").last().ffill()
    prev = m.shift(1).fillna(start_equity)
    return (m / prev - 1).rename("ret")
