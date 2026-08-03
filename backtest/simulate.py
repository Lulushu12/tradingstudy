"""Trade simulation with deliberately pessimistic fill assumptions.

Rules, all chosen so the result errs against the strategy rather than for it:

  * Entry is the close of the signal bar, plus slippage, plus taker fee.
  * Exit scanning starts at the NEXT bar. The signal bar itself can never
    resolve the trade it created.
  * If a bar opens beyond the stop (or the target), it fills at the open -
    gaps are honoured, not ignored.
  * If a single bar's range contains BOTH the stop and the target, the stop is
    assumed to have hit first. Hourly bars hide the path, and assuming the
    favourable order is the single most common way a backtest lies.
  * A time stop closes the trade at market if neither level is reached.
  * Trades still open when the data ends are marked OPEN and excluded from the
    realised statistics (they are reported separately, never counted as wins).
"""

TAKER_FEE = 0.00045      # 0.045% per side, Binance USDT-M taker
SLIPPAGE = 0.0002        # 0.02% per side
FUNDING_PER_8H = 0.0001  # 0.01% per 8h, charged as a drag on both directions

RISK_PER_TRADE = 1000.0  # notional $ risked per trade, for the $ columns


def simulate(entry_idx, direction, entry_px, stop, target, time_stop,
             open_, high, low, close, n):
    """Resolve one trade. Returns a dict of outcome fields."""
    risk_px = abs(entry_px - stop)
    if risk_px <= 0:
        return None

    last = min(entry_idx + time_stop, n - 1)
    exit_idx = None
    exit_px = None
    reason = None

    mae_px = 0.0  # worst adverse excursion, in price
    mfe_px = 0.0  # best favourable excursion, in price

    for j in range(entry_idx + 1, last + 1):
        o, h, l = open_[j], high[j], low[j]

        if direction == 1:
            mae_px = max(mae_px, entry_px - l)
            mfe_px = max(mfe_px, h - entry_px)
            if o <= stop:
                exit_idx, exit_px, reason = j, o, "STOP_GAP"
                break
            if o >= target:
                exit_idx, exit_px, reason = j, o, "TARGET_GAP"
                break
            hit_stop = l <= stop
            hit_target = h >= target
        else:
            mae_px = max(mae_px, h - entry_px)
            mfe_px = max(mfe_px, entry_px - l)
            if o >= stop:
                exit_idx, exit_px, reason = j, o, "STOP_GAP"
                break
            if o <= target:
                exit_idx, exit_px, reason = j, o, "TARGET_GAP"
                break
            hit_stop = h >= stop
            hit_target = l <= target

        if hit_stop:
            # Stop wins ties by construction - see module docstring.
            exit_idx, exit_px, reason = j, stop, "STOP"
            break
        if hit_target:
            exit_idx, exit_px, reason = j, target, "TARGET"
            break

    if exit_idx is None:
        if entry_idx + time_stop >= n - 1:
            # Ran out of history before the time stop could fire.
            return {
                "status": "OPEN",
                "exit_idx": None,
                "exit_px": None,
                "exit_reason": "OPEN_AT_DATA_END",
                "bars_held": n - 1 - entry_idx,
                "mae_r": mae_px / risk_px,
                "mfe_r": mfe_px / risk_px,
                "gross_pct": None,
                "net_pct": None,
                "r_multiple": None,
                "pnl_usd": None,
                "cost_pct": None,
            }
        exit_idx, exit_px, reason = last, close[last], "TIME"

    bars_held = exit_idx - entry_idx
    gross_pct = direction * (exit_px - entry_px) / entry_px

    funding = FUNDING_PER_8H * (bars_held / 8.0)
    cost_pct = 2.0 * (TAKER_FEE + SLIPPAGE) + funding
    net_pct = gross_pct - cost_pct

    risk_pct = risk_px / entry_px
    r_multiple = net_pct / risk_pct
    pnl_usd = r_multiple * RISK_PER_TRADE

    return {
        "status": "CLOSED",
        "exit_idx": exit_idx,
        "exit_px": exit_px,
        "exit_reason": reason,
        "bars_held": bars_held,
        "mae_r": mae_px / risk_px,
        "mfe_r": mfe_px / risk_px,
        "gross_pct": gross_pct,
        "net_pct": net_pct,
        "cost_pct": cost_pct,
        "r_multiple": r_multiple,
        "pnl_usd": pnl_usd,
    }
