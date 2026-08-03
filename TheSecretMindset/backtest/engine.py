"""Event-driven backtester.

Guards, all implemented explicitly rather than assumed:

1. No look-ahead. A signal for bar t is computed from a precomputed frame whose row t uses
   only bars <= t, and the engine never reads row t+1 when deciding at t.
2. Fills. Default is the open of the bar after the signal. `entry_on_close` models the one
   strategy whose author explicitly says to enter at the signal candle's close.
3. Intrabar ambiguity. If a bar could have hit both the stop and a profit level, the stop is
   taken first, always. Never relaxed, in either direction.
4. Stops and trails move only on confirmed closes.
5. Costs are charged on every fill including partials, as a fraction of notional traded.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd


@dataclass
class Trade:
    side: int
    entry_i: int
    entry_dt: object
    entry_px: float
    qty: float
    risk_per_unit: float
    exit_i: int = -1
    exit_dt: object = None
    exit_px: float = 0.0
    pnl: float = 0.0
    cost: float = 0.0
    r_multiple: float = 0.0
    reason: str = ""
    partials: list = field(default_factory=list)


class Engine:
    """One position at a time, long or short, sized either by stop distance or by notional."""

    def __init__(self, df: pd.DataFrame, cost_per_side: float = 0.0005,
                 equity0: float = 10_000.0, risk_frac: float = 0.01):
        self.df = df.reset_index(drop=True)
        self.cost = cost_per_side
        self.equity0 = equity0
        self.risk_frac = risk_frac

    def run(self, signals: pd.DataFrame, entry_on_close: bool = False,
            tiered_exit: bool = False) -> tuple[list[Trade], pd.Series]:
        """`signals` columns, all aligned to the price frame:

        entry  : +1 long, -1 short, 0 nothing (evaluated at that bar's close)
        exit   : True to close any open position on the signal
        stop   : stop price for a new entry, NaN if the strategy has no stop
        target : optional fixed target price, NaN if none
        trail  : per-bar trailing stop level, NaN if the strategy does not trail
        """
        df = self.df
        o, h, l, c = (df[k].values for k in ("open", "high", "low", "close"))
        dt = df["dt"].values
        n = len(df)

        sig_entry = signals["entry"].fillna(0).values.astype(int)
        sig_exit = signals["exit"].fillna(False).values.astype(bool)
        sig_stop = signals["stop"].values if "stop" in signals else np.full(n, np.nan)
        sig_targ = signals["target"].values if "target" in signals else np.full(n, np.nan)
        sig_trail = signals["trail"].values if "trail" in signals else np.full(n, np.nan)
        # a trail must sit below a long and above a short; one shared column cannot do both
        sig_tl = signals["trail_long"].values if "trail_long" in signals else sig_trail
        sig_ts = signals["trail_short"].values if "trail_short" in signals else sig_trail
        # stop_dist lets a strategy express "2 x ATR from the fill" rather than from the
        # signal bar's close, so the stop is anchored to the price actually paid.
        sig_sdist = signals["stop_dist"].values if "stop_dist" in signals else np.full(n, np.nan)

        equity = self.equity0
        curve = np.full(n, np.nan)
        trades: list[Trade] = []
        pos: Trade | None = None
        stop_px = np.nan
        half_done = False
        pending: tuple[int, float, float] | None = None   # (side, stop, target)

        def close_out(t: Trade, i: int, px: float, reason: str, frac: float = 1.0,
                      final: bool = True):
            """`frac` is how much of the original size is being closed. `final` says whether
            the position is finished. These are independent: a trade that already scaled out
            half closes its last half with frac=0.5 and final=True, and must still be
            recorded. Conflating the two silently discards every trade that scaled out."""
            nonlocal equity
            q = t.qty * frac
            gross = (px - t.entry_px) * q * t.side
            fee = abs(px * q) * self.cost
            equity += gross - fee
            t.pnl += gross - fee
            t.cost += fee
            t.partials.append((i, px, reason, gross - fee))
            if final:
                t.exit_i, t.exit_dt, t.exit_px, t.reason = i, dt[i], px, reason
                denom = t.risk_per_unit * t.qty
                t.r_multiple = t.pnl / denom if denom > 0 else np.nan
                trades.append(t)

        for i in range(n):
            # ---- 1. fill any order queued on the previous bar, at this bar's open
            if pending is not None and pos is None:
                side, st, sd = pending
                pending = None
                px = o[i]
                if np.isnan(st) and not np.isnan(sd):
                    st = px - side * sd
                pos, stop_px, half_done = self._open(px, side, st, equity, i, dt), st, False
                if pos is not None:
                    equity -= abs(px * pos.qty) * self.cost
                    pos.cost += abs(px * pos.qty) * self.cost

            # ---- 2. manage an open position inside this bar (stop first, always)
            if pos is not None:
                exited = False
                if not np.isnan(stop_px):
                    hit = l[i] <= stop_px if pos.side > 0 else h[i] >= stop_px
                    if hit:
                        close_out(pos, i, stop_px, "stop", 1.0 - (0.5 if half_done else 0.0))
                        pos, exited = None, True
                if not exited and tiered_exit and not half_done:
                    one_r = pos.entry_px + pos.side * pos.risk_per_unit
                    hit = h[i] >= one_r if pos.side > 0 else l[i] <= one_r
                    if hit:
                        close_out(pos, i, one_r, "1R_partial", 0.5, final=False)
                        half_done = True
                        stop_px = pos.entry_px          # tier 2: breakeven
                # target is read per bar, not latched, so a strategy can express a moving
                # exit level (S2's 50-channel midpoint) rather than a fixed price
                if not exited and not tiered_exit and not np.isnan(sig_targ[i]):
                    tp = sig_targ[i]
                    already = (pos.entry_px >= tp) if pos.side > 0 else (pos.entry_px <= tp)
                    hit = (h[i] >= tp if pos.side > 0 else l[i] <= tp) and not already
                    if hit:
                        close_out(pos, i, tp, "target")
                        pos, exited = None, True
                if not exited and sig_exit[i]:
                    close_out(pos, i, c[i], "signal", 1.0 - (0.5 if half_done else 0.0))
                    pos = None
                # trailing level: only on a confirmed close, and only ever tighten.
                # Under tiered_exit this is S4's tier 3 and waits for the 1R partial; without
                # it, the trail is live from the start (S2's give-back exit).
                active = half_done if tiered_exit else True
                t_px = (sig_tl[i] if pos is not None and pos.side > 0 else sig_ts[i])
                if pos is not None and active and not np.isnan(t_px):
                    if pos.side > 0 and (np.isnan(stop_px) or t_px > stop_px):
                        stop_px = t_px
                    elif pos.side < 0 and (np.isnan(stop_px) or t_px < stop_px):
                        stop_px = t_px

            # ---- 3. evaluate this bar's close for a new signal
            if sig_entry[i] != 0:
                side = sig_entry[i]
                if pos is not None and pos.side != side:
                    close_out(pos, i, c[i], "reverse", 1.0 - (0.5 if half_done else 0.0))
                    pos = None
                if pos is None:
                    if entry_on_close:
                        px = c[i]
                        st = sig_stop[i]
                        if np.isnan(st) and not np.isnan(sig_sdist[i]):
                            st = px - side * sig_sdist[i]
                        pos = self._open(px, side, st, equity, i, dt)
                        stop_px, half_done = st, False
                        if pos is not None:
                            equity -= abs(px * pos.qty) * self.cost
                            pos.cost += abs(px * pos.qty) * self.cost
                    else:
                        pending = (side, sig_stop[i], sig_sdist[i])

            curve[i] = equity + (0.0 if pos is None else
                                 (c[i] - pos.entry_px) * pos.qty * pos.side)

        if pos is not None:
            close_out(pos, n - 1, c[n - 1], "end_of_data",
                      1.0 - (0.5 if half_done else 0.0))

        return trades, pd.Series(curve, index=df.index)

    def _open(self, px: float, side: int, stop: float, equity: float, i: int, dt) -> Trade | None:
        if equity <= 0 or not np.isfinite(px) or px <= 0:
            return None
        if np.isnan(stop):
            qty = equity / px                      # no stop stated: full notional, unlevered
            risk_unit = px                          # R is defined against entry price
        else:
            dist = abs(px - stop)
            if dist <= 0:
                return None
            qty = (equity * self.risk_frac) / dist
            risk_unit = dist
            if qty * px > equity * 20:              # sanity cap, logged by caller if hit
                qty = equity * 20 / px
        return Trade(side=side, entry_i=i, entry_dt=dt[i], entry_px=px,
                     qty=qty, risk_per_unit=risk_unit)


def stats(trades: list[Trade], curve: pd.Series, equity0: float = 10_000.0) -> dict:
    if not trades:
        return {"trades": 0}
    pnl = np.array([t.pnl for t in trades])
    r = np.array([t.r_multiple for t in trades], dtype=float)
    wins, losses = pnl[pnl > 0], pnl[pnl <= 0]
    gross_w, gross_l = wins.sum(), abs(losses.sum())

    eq = curve.ffill().fillna(equity0)
    dd = (eq / eq.cummax() - 1.0)

    streak = worst = 0
    for p in pnl:
        streak = streak + 1 if p <= 0 else 0
        worst = max(worst, streak)

    return {
        "trades": len(trades),
        "net_pnl": round(pnl.sum(), 2),
        "return_pct": round(100 * (eq.iloc[-1] / equity0 - 1), 2),
        "expectancy_per_trade": round(pnl.mean(), 2),
        "expectancy_R": round(np.nanmean(r), 4),
        "win_rate_pct": round(100 * len(wins) / len(trades), 1),
        "profit_factor": round(gross_w / gross_l, 3) if gross_l > 0 else float("inf"),
        "max_drawdown_pct": round(100 * dd.min(), 2),
        "longest_losing_streak": int(worst),
        "avg_win": round(wins.mean(), 2) if len(wins) else 0.0,
        "avg_loss": round(losses.mean(), 2) if len(losses) else 0.0,
        "total_costs": round(sum(t.cost for t in trades), 2),
    }
