"""Resting limit entries where the setup justifies waiting, market where it does not.

Rationale, decided before running anything:

  A pullback or a fade is a bet that price comes BACK to you. Paying the close
  is paying up for something the thesis says will be cheaper shortly. Resting a
  bid below the close costs nothing but patience, and if price never comes back
  the trade was the one you did not want anyway.

  A breakout is the opposite. The thesis is that price leaves and does not
  return, so a limit below the close systematically misses exactly the trades
  the setup exists to catch. Breakouts stay market orders.

So: TREND_PULLBACK, EXHAUSTION and DEFAULT rest a limit; BREAKOUT crosses the
spread.

The second effect matters as much as the price improvement. Across this whole
study friction has been the dominant term, and a resting order is a maker
order: no slippage, and roughly half the fee. Exits are costed by how they
actually happen - a target is a resting limit (maker), a stop or a time exit is
a market order (taker plus slippage).

Fill modelling is deliberately pessimistic:
  * The order rests from the NEXT bar. It can never fill on the signal bar.
  * A buy fills only if the bar's low reaches the limit, and fills AT the limit
    even when the bar opened below it - the improvement is not credited.
  * If the fill bar also touches the stop, the trade is assumed filled and then
    stopped inside that bar: a loss.
  * Unfilled by expiry means no trade at all, not a market entry as consolation.
"""

import numpy as np

TAKER = 0.00045
MAKER = 0.00020
SLIPPAGE = 0.00020
FUNDING_PER_8H = 0.0001
RISK_PER_TRADE = 1000.0

# Setups that rest a limit rather than crossing the spread.
LIMIT_SETUPS = frozenset({"TREND_PULLBACK", "EXHAUSTION", "DEFAULT"})


def entry_cost(mode):
    return MAKER if mode == "LIMIT" else TAKER + SLIPPAGE


def exit_cost(reason):
    # A target is a resting limit; everything else leaves at market.
    return MAKER if reason.startswith("TARGET") else TAKER + SLIPPAGE


def simulate(entry_idx, direction, mode, ref_close, stop_dist, target_r,
             time_stop, offset_atr, expiry, atr, open_, high, low, close, n):
    """Resolve one trade under either entry mode.

    stop_dist is the price distance from entry to stop, decided at signal time
    and then applied to whatever price the order actually fills at.
    Returns None if a limit order expired unfilled.
    """
    if mode == "LIMIT":
        limit_px = ref_close - direction * offset_atr * atr
        fill_idx = None
        last_try = min(entry_idx + expiry, n - 1)
        for j in range(entry_idx + 1, last_try + 1):
            reached = low[j] <= limit_px if direction == 1 else high[j] >= limit_px
            if reached:
                fill_idx = j
                break
        if fill_idx is None:
            return None
        entry_px = limit_px
        # The fill bar itself is live: the stop can be hit after we are filled.
        scan_from = fill_idx
    else:
        entry_px = ref_close * (1 + direction * SLIPPAGE)
        fill_idx = entry_idx
        scan_from = entry_idx + 1

    stop = entry_px - direction * stop_dist
    target = entry_px + direction * target_r * stop_dist

    last = min(fill_idx + time_stop, n - 1)
    exit_idx = exit_px = reason = None
    mae_px = mfe_px = 0.0

    for j in range(scan_from, last + 1):
        o, h, l = open_[j], high[j], low[j]

        if direction == 1:
            mae_px = max(mae_px, entry_px - l)
            mfe_px = max(mfe_px, h - entry_px)
        else:
            mae_px = max(mae_px, h - entry_px)
            mfe_px = max(mfe_px, entry_px - l)

        # Gaps only apply on bars after the fill; on the fill bar the open
        # already happened before we were filled.
        if j > fill_idx:
            if (direction == 1 and o <= stop) or (direction == -1 and o >= stop):
                exit_idx, exit_px, reason = j, o, "STOP_GAP"
                break
            if (direction == 1 and o >= target) or (direction == -1 and o <= target):
                exit_idx, exit_px, reason = j, o, "TARGET_GAP"
                break

        if direction == 1:
            hit_stop, hit_target = l <= stop, h >= target
        else:
            hit_stop, hit_target = h >= stop, l <= target

        if hit_stop:
            exit_idx, exit_px, reason = j, stop, "STOP"
            break
        if hit_target:
            exit_idx, exit_px, reason = j, target, "TARGET"
            break

    if exit_idx is None:
        if fill_idx + time_stop >= n - 1:
            return None  # unresolved at data end; excluded, never counted as a win
        exit_idx, exit_px, reason = last, close[last], "TIME"

    bars_held = exit_idx - fill_idx
    gross = direction * (exit_px - entry_px) / entry_px
    cost = entry_cost(mode) + exit_cost(reason) + FUNDING_PER_8H * (bars_held / 8.0)
    net = gross - cost
    risk_pct = stop_dist / entry_px
    r = net / risk_pct

    return {
        "mode": mode,
        "wait_bars": fill_idx - entry_idx,
        "entry_px": entry_px, "stop": stop, "target": target,
        "exit_idx": exit_idx, "exit_px": exit_px, "exit_reason": reason,
        "bars_held": bars_held,
        "gross_pct": gross, "cost_pct": cost, "net_pct": net,
        "r_multiple": r, "pnl_usd": r * RISK_PER_TRADE,
        "mae_r": mae_px / stop_dist, "mfe_r": mfe_px / stop_dist,
        "cost_share": cost / risk_pct,
    }
