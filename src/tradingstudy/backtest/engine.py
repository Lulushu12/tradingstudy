"""Trade simulation on 1m bars (PROTOCOL section 3). One call simulates many independent signals; portfolio rules
(position caps, daily guard, account limits) are applied afterwards in portfolio.py.

Per signal (long shown, short mirrored):
  Pending:  limit at `entry`, from the first 1m bar opening at or after the signal bar's close.
            fill    if low  <= entry - tick              (trade-through by one tick, fill price = entry)
            cancel  if high >= entry + 0.5R               (0.5R = cancel_dist), checked after the fill test
            expire  when 24 h have passed since the signal without fill or cancel
            touched if low <= entry (used to define missed fills)
  In trade: fill minute: only the stop is checked (order of fill and stop inside the minute is unknown).
            later minutes: stop  if low  <= stop  -> exit at min(stop, open) x (1 - slip)   (gap through = worse)
                           target if high >= target + tick -> exit at target (limit)
                           both in one minute -> stop
            timeout: at the close of the last 1m bar inside 24 h after the fill, x (1 - slip)
  Result in R (R = stop distance): gross = (exit - entry) / R; fee = fee_rate x (entry + exit) / R; net = gross - fee.
  Missed fill: touched but never filled. Its hypothetical result = the same simulation with a fill at entry on the
  first touch minute.
"""
from __future__ import annotations

import numba as nb
import numpy as np

MIN_NS = 60 * 10**9
DAY_NS = 1440 * MIN_NS
FEE_RATE = 0.0004

# status codes
FILLED, CANCELLED, EXPIRED, NO_DATA, SKIPPED = 0, 1, 2, 3, 4
# exit reasons
STOP, TARGET, TIMEOUT, END_OF_DATA = 1, 2, 3, 4


@nb.njit(cache=True)
def _run_trade(ts, o, h, l, c, j, d, entry, stop, target, tick, slip, fee_rate, R, hold_ns=DAY_NS):
    """Trade filled at minute j. Returns exit_idx, reason, exit_px, gross_R, fee_R, slip_R. Timeout after hold_ns."""
    n = ts.shape[0]
    t_end = ts[j] + hold_ns
    # fill minute: stop only
    if (d == 1 and l[j] <= stop) or (d == -1 and h[j] >= stop):
        px = stop * (1 - slip) if d == 1 else stop * (1 + slip)
        g = d * (px - entry) / R
        return j, STOP, px, g, fee_rate * (entry + px) / R, abs(px - stop) / R
    last = j
    timed_out = False
    for i in range(j + 1, n):
        if ts[i] >= t_end:
            timed_out = True
            break
        last = i
        if d == 1:
            if l[i] <= stop:
                ideal = min(stop, o[i])
                px = ideal * (1 - slip)
                return i, STOP, px, (px - entry) / R, fee_rate * (entry + px) / R, abs(px - stop) / R
            if h[i] >= target + tick:
                return i, TARGET, target, (target - entry) / R, fee_rate * (entry + target) / R, 0.0
        else:
            if h[i] >= stop:
                ideal = max(stop, o[i])
                px = ideal * (1 + slip)
                return i, STOP, px, (entry - px) / R, fee_rate * (entry + px) / R, abs(px - stop) / R
            if l[i] <= target - tick:
                return i, TARGET, target, (entry - target) / R, fee_rate * (entry + target) / R, 0.0
    reason = TIMEOUT if timed_out else END_OF_DATA
    px = c[last] * (1 - slip) if d == 1 else c[last] * (1 + slip)
    return last, reason, px, d * (px - entry) / R, fee_rate * (entry + px) / R, abs(px - c[last]) / R


@nb.njit(cache=True)
def simulate(ts, o, h, l, c, start_idx, sig_ts, direction, entry, stop_dist, target, tick, slip, fee_rate):
    """Arrays of length n_signals except the 1m arrays. start_idx = first 1m bar at or after the signal close.
    Returns a (n_signals, 14) float array; see COLS. Protocol defaults: limit entry, 24 h order life and timeout."""
    return simulate_ex(ts, o, h, l, c, start_idx, sig_ts, direction, entry, stop_dist, target, tick, slip, fee_rate,
                       DAY_NS, DAY_NS, False)


@nb.njit(cache=True)
def simulate_ex(ts, o, h, l, c, start_idx, sig_ts, direction, entry, stop_dist, target, tick, slip, fee_rate,
                pend_ns, hold_ns, market):
    """As simulate, plus: pend_ns = limit order life; hold_ns = timeout after the fill; market=True fills at the open of
    the first 1m bar at/after the signal close (worse by slippage) and then `target` is read as an R MULTIPLE measured
    from the fill price, with the stop at fill -/+ stop_dist (as in the user's original study)."""
    ns = start_idx.shape[0]
    n = ts.shape[0]
    out = np.full((ns, 14), np.nan)
    for s in range(ns):
        d = direction[s]
        R = stop_dist[s]
        e = entry[s]
        tgt = target[s]
        if np.isnan(tgt) or np.isnan(R) or R <= 0 or np.isnan(e):
            out[s, 0] = SKIPPED
            continue
        j0 = start_idx[s]
        if j0 >= n:
            out[s, 0] = NO_DATA
            continue
        if market:
            e = o[j0] * (1 + d * slip[s])
            stop = e - d * R
            tgt = e + d * target[s] * R
            xi, reason, px, g, f, sl = _run_trade(ts, o, h, l, c, j0, d, e, stop, tgt, tick[s], slip[s], fee_rate, R, hold_ns)
            out[s, 0] = FILLED; out[s, 1] = 1.0
            out[s, 2] = j0; out[s, 3] = xi; out[s, 4] = reason; out[s, 5] = px
            out[s, 6] = g; out[s, 7] = f; out[s, 8] = sl; out[s, 9] = g - f
            out[s, 10] = ts[j0]; out[s, 11] = ts[xi]
            continue
        stop = e - d * R
        cancel_lvl = e + d * 0.5 * R
        t_exp = sig_ts[s] + pend_ns
        fill = -1
        touch = -1
        status = EXPIRED
        end_i = j0
        for i in range(j0, n):
            if ts[i] >= t_exp:
                break
            end_i = i
            if d == 1:
                if touch < 0 and l[i] <= e:
                    touch = i
                if l[i] <= e - tick[s]:
                    fill = i; status = FILLED
                    break
                if h[i] >= cancel_lvl:
                    status = CANCELLED
                    break
            else:
                if touch < 0 and h[i] >= e:
                    touch = i
                if h[i] >= e + tick[s]:
                    fill = i; status = FILLED
                    break
                if l[i] <= cancel_lvl:
                    status = CANCELLED
                    break
        out[s, 0] = status
        out[s, 1] = 1.0 if touch >= 0 else 0.0
        if status == FILLED:
            xi, reason, px, g, f, sl = _run_trade(ts, o, h, l, c, fill, d, e, stop, tgt, tick[s], slip[s], fee_rate, R, hold_ns)
            out[s, 2] = fill; out[s, 3] = xi; out[s, 4] = reason; out[s, 5] = px
            out[s, 6] = g; out[s, 7] = f; out[s, 8] = sl; out[s, 9] = g - f
            out[s, 10] = ts[fill]; out[s, 11] = ts[xi]
        else:
            out[s, 11] = ts[end_i]  # time the order stopped occupying the coin
            if touch >= 0:  # missed fill: hypothetical fill at the first touch
                xi, reason, px, g, f, sl = _run_trade(ts, o, h, l, c, touch, d, e, stop, tgt, tick[s], slip[s], fee_rate, R, hold_ns)
                out[s, 12] = g - f
                out[s, 13] = reason
    return out


COLS = ["status", "touched", "fill_idx", "exit_idx", "exit_reason", "exit_px", "gross_R", "fee_R", "slip_R", "net_R",
        "fill_ts", "end_ts", "missed_hyp_net_R", "missed_hyp_reason"]
