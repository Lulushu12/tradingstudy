"""Portfolio pass over independently simulated signals (PROTOCOL section 3).

Rules, applied in signal-time order across all coins:
  - a coin with an open position or a pending limit takes no new signal;
  - at most 3 coins occupied (pending or open) account-wide;
  - no new entries once realized P&L for the current UTC day reaches -2% of the start-of-day balance;
  - risk 0.5% of current equity per trade (P&L = net_R x 0.5% x equity at the signal).
Account limits are tracked, not enforced, so the edge can be measured on the full sample: a day whose realized loss
reaches 3% of the start-of-day balance is a daily breach; equity at or below 94% of the start is a max breach. The
probability of breaching is estimated by the Monte Carlo, not by this single path.
"""
from __future__ import annotations

import heapq

import numpy as np
import pandas as pd

from tradingstudy.backtest.engine import FILLED, NO_DATA, SKIPPED

RISK = 0.005
MAX_OPEN = 3
DAILY_GUARD = -0.02
DAILY_LIMIT = -0.03
MAX_DD_LEVEL = 0.94
DAY_NS = 86400 * 10**9


def run_portfolio(sims: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """sims: one row per signal with coin, sig_ts (ns), status, fill_ts, end_ts, net_R. Returns (sims + taken/pnl
    columns, account summary)."""
    s = sims.sort_values(["sig_ts", "coin"], kind="stable").reset_index(drop=True)
    taken = np.zeros(len(s), dtype=bool)
    pnl = np.full(len(s), np.nan)
    equity = 1.0
    active = []  # heap of (end_ts, row)
    occupied = set()
    day = None
    day_start_eq = 1.0
    day_pnl = 0.0
    daily_breaches, max_breach_ts = [], None
    peak = 1.0
    max_dd = 0.0
    risk_at = {}

    def roll_day(t):
        nonlocal day, day_start_eq, day_pnl
        d = t // DAY_NS
        if d != day:
            day, day_start_eq, day_pnl = d, equity, 0.0

    def realize(upto):
        nonlocal equity, day_pnl, peak, max_dd, max_breach_ts
        while active and active[0][0] <= upto:
            end, r = heapq.heappop(active)
            occupied.discard(s.at[r, "coin"])
            if s.at[r, "status"] == FILLED:
                roll_day(end)
                p = s.at[r, "net_R"] * RISK * risk_at[r]
                pnl[r] = p
                equity += p
                day_pnl += p
                if day_pnl <= DAILY_LIMIT * day_start_eq and (not daily_breaches or daily_breaches[-1] != day):
                    daily_breaches.append(day)
                peak = max(peak, equity)
                max_dd = max(max_dd, 1 - equity / peak)
                if equity <= MAX_DD_LEVEL and max_breach_ts is None:
                    max_breach_ts = end

    for r in range(len(s)):
        t = s.at[r, "sig_ts"]
        realize(t)
        roll_day(t)
        st = s.at[r, "status"]
        if st in (SKIPPED, NO_DATA):
            continue
        if s.at[r, "coin"] in occupied or len(occupied) >= MAX_OPEN or day_pnl <= DAILY_GUARD * day_start_eq:
            continue
        taken[r] = True
        risk_at[r] = equity
        occupied.add(s.at[r, "coin"])
        heapq.heappush(active, (s.at[r, "end_ts"], r))
    realize(np.iinfo(np.int64).max)
    s["taken"] = taken
    s["pnl_frac"] = pnl
    summary = {"final_equity": equity, "max_dd": max_dd, "daily_breaches": len(daily_breaches),
               "first_daily_breach": str(pd.Timestamp(daily_breaches[0] * DAY_NS, tz="UTC").date()) if daily_breaches else None,
               "max_breach": str(pd.Timestamp(max_breach_ts, tz="UTC")) if max_breach_ts is not None else None}
    return s, summary
