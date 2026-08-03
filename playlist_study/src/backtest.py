"""
Event driven backtester for the playlist strategies.

Deliberately simple, because the first pass is a quick-and-dirty screen: the
question is "is there any edge here at all", not "what would this have returned".
The guards that are NOT optional even in a quick pass are implemented:

  - No look-ahead. A signal computed on bar t's close enters at bar t+1's OPEN.
  - Intrabar ambiguity resolved pessimistically. If a bar's range contains both
    the stop and the target, the STOP is assumed to have been hit first. Without
    intrabar data there is no way to know, and the optimistic assumption is how
    a losing strategy backtests like a winner.
  - Gaps respected. Entry and exit prices come from real adjacent bars only;
    callers should feed contiguous segments (see data.contiguous_segments).

Costs default to zero for the first pass. `cost_bps` applies a round trip cost
in basis points of notional so the same run can be repeated with realistic
friction without touching strategy code.
"""

from dataclasses import dataclass, field

import numpy as np
import pandas as pd


@dataclass
class Trade:
    side: int              # +1 long, -1 short
    entry_time: pd.Timestamp
    entry: float
    exit_time: pd.Timestamp
    exit: float
    stop: float
    target: float
    reason: str            # stop | target | signal | timeout | eod
    bars_held: int

    @property
    def ret_pct(self):
        """Return on the position, in percent, before costs."""
        return self.side * (self.exit - self.entry) / self.entry * 100

    @property
    def r_multiple(self):
        risk = abs(self.entry - self.stop)
        if not risk or np.isnan(risk):
            return np.nan
        return self.side * (self.exit - self.entry) / risk


@dataclass
class Signals:
    """What a strategy hands the engine.

    Each field is a per-bar array aligned to the price frame. `long` / `short`
    are booleans meaning "the setup completed on this bar's close". `stop` and
    `target` are absolute prices for a position opened from that signal; leave
    them NaN to use the engine's fallbacks.
    """
    long: pd.Series
    short: pd.Series
    stop: pd.Series = None
    target: pd.Series = None
    exit_long: pd.Series = None     # optional discretionary/indicator exit
    exit_short: pd.Series = None
    limit: pd.Series = None         # resting limit price, see run()
    meta: dict = field(default_factory=dict)


def run(df, sig, max_bars=None, allow_pyramiding=False, cost_bps=0.0,
        stop_pct=None, target_r=None):
    """Walk the bars and produce a trade list.

    max_bars    : force an exit after this many bars in the trade (None = never)
    stop_pct    : fallback stop distance as percent of entry when sig.stop is NaN
    target_r    : fallback target as a multiple of risk when sig.target is NaN
    """
    o = df["open"].to_numpy(float)
    h = df["high"].to_numpy(float)
    l = df["low"].to_numpy(float)
    c = df["close"].to_numpy(float)
    idx = df.index

    lng = _arr(sig.long, len(df), False)
    sht = _arr(sig.short, len(df), False)
    stp = _arr(sig.stop, len(df), np.nan, float)
    tgt = _arr(sig.target, len(df), np.nan, float)
    xl = _arr(sig.exit_long, len(df), False)
    xs = _arr(sig.exit_short, len(df), False)
    lim = _arr(sig.limit, len(df), np.nan, float)

    trades = []
    pos = 0
    entry = stop = target = np.nan
    entry_i = 0

    for i in range(len(df) - 1):
        # ---- manage an open position on bar i
        if pos != 0:
            reason = None
            px = np.nan
            if pos == 1:
                # pessimistic ordering: stop checked before target
                if not np.isnan(stop) and l[i] <= stop:
                    reason, px = "stop", stop
                elif not np.isnan(target) and h[i] >= target:
                    reason, px = "target", target
                elif xl[i]:
                    reason, px = "signal", c[i]
            else:
                if not np.isnan(stop) and h[i] >= stop:
                    reason, px = "stop", stop
                elif not np.isnan(target) and l[i] <= target:
                    reason, px = "target", target
                elif xs[i]:
                    reason, px = "signal", c[i]

            if reason is None and max_bars and (i - entry_i) >= max_bars:
                reason, px = "timeout", c[i]

            if reason is not None:
                trades.append(Trade(pos, idx[entry_i], entry, idx[i], px,
                                    stop, target, reason, i - entry_i))
                pos = 0

        # ---- look for a new signal on bar i
        if pos == 0 or allow_pyramiding:
            side = 1 if lng[i] else (-1 if sht[i] else 0)
            if side:
                lp = lim[i]
                if np.isnan(lp):
                    # market order: fill at the NEXT bar's open
                    fill, fill_i = o[i + 1], i + 1
                else:
                    # resting limit order: the strategy placed this level before
                    # the bar traded, so a bar whose range covers it fills AT it.
                    # Modelling these as market-on-next-open would test a
                    # different strategy, one that chases after the touch.
                    if not (l[i] <= lp <= h[i]):
                        continue
                    fill, fill_i = lp, i

                s = stp[i]
                if np.isnan(s) and stop_pct:
                    s = fill * (1 - side * stop_pct / 100)
                t = tgt[i]
                if np.isnan(t) and target_r and not np.isnan(s):
                    t = fill + side * abs(fill - s) * target_r
                pos, entry, stop, target, entry_i = side, fill, s, t, fill_i

                # A limit fill happens mid bar, so that same bar may also reach
                # the stop. Intrabar order is unknowable, so assume the worst
                # and close it here rather than granting a free bar.
                if fill_i == i and not np.isnan(s):
                    hit = (l[i] <= s) if side == 1 else (h[i] >= s)
                    if hit:
                        trades.append(Trade(side, idx[i], entry, idx[i], s,
                                            s, t, "stop", 0))
                        pos = 0

    if pos != 0:
        trades.append(Trade(pos, idx[entry_i], entry, idx[-1], c[-1],
                            stop, target, "eod", len(df) - 1 - entry_i))

    return _apply_costs(trades, cost_bps)


def _arr(s, n, fill, dtype=bool):
    if s is None:
        return np.full(n, fill, dtype=dtype)
    return s.fillna(fill).to_numpy(dtype)


def _apply_costs(trades, cost_bps):
    if cost_bps:
        for t in trades:
            t.cost_pct = cost_bps / 100.0
    else:
        for t in trades:
            t.cost_pct = 0.0
    return trades


def stats(trades, label=""):
    """Summarise a trade list. Compounded equity, 1 unit of notional per trade."""
    if not trades:
        return {"label": label, "n": 0}

    r = np.array([t.ret_pct - t.cost_pct for t in trades])
    rr = np.array([t.r_multiple for t in trades], dtype=float)
    wins, losses = r[r > 0], r[r <= 0]

    eq = np.cumprod(1 + r / 100)
    peak = np.maximum.accumulate(eq)
    dd = (eq - peak) / peak

    streak = best = 0
    for x in r:
        streak = streak + 1 if x <= 0 else 0
        best = max(best, streak)

    gross_win = wins.sum()
    gross_loss = -losses.sum()
    days = (trades[-1].exit_time - trades[0].entry_time).days or 1

    return {
        "label": label,
        "n": len(trades),
        "win_rate": len(wins) / len(r) * 100,
        "avg_pct": r.mean(),
        "median_pct": float(np.median(r)),
        "avg_win": wins.mean() if len(wins) else 0.0,
        "avg_loss": losses.mean() if len(losses) else 0.0,
        "avg_R": float(np.nanmean(rr)) if not np.all(np.isnan(rr)) else np.nan,
        "profit_factor": gross_win / gross_loss if gross_loss > 0 else np.inf,
        "total_return_pct": (eq[-1] - 1) * 100,
        "max_dd_pct": dd.min() * 100,
        "max_losing_streak": best,
        "avg_bars": float(np.mean([t.bars_held for t in trades])),
        "trades_per_year": len(trades) / (days / 365.25),
        "exits": pd.Series([t.reason for t in trades]).value_counts().to_dict(),
    }


def breakeven_cost_bps(trades):
    """Round trip cost in bps that would drive average trade return to zero.

    This is the headroom number that matters for a quick pass: a strategy whose
    breakeven cost is below the venue's actual fees is already dead, however
    good the frictionless equity curve looks.
    """
    if not trades:
        return 0.0
    return float(np.mean([t.ret_pct for t in trades]) * 100)


def summary_table(rows):
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    cols = ["label", "n", "win_rate", "avg_pct", "avg_R", "profit_factor",
            "total_return_pct", "max_dd_pct", "max_losing_streak",
            "trades_per_year", "avg_bars"]
    return df[[c for c in cols if c in df.columns]].round(3)
