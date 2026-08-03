"""Do trade outcomes streak, or are they independent draws?

Three separate questions, because they have different answers and different
consequences:

  1. Do consecutive TRADES cluster into runs of wins and losses?
     Confounded by overlap - stacked trades share bars, so they must correlate
     mechanically. Reported with and without overlap removed.

  2. Do outcomes streak once overlap is eliminated?
     Restricting to a sequential book (never enter until the previous trade has
     closed) removes the mechanical component. What remains is real.

  3. Does PERFORMANCE persist at calendar scale - are good weeks followed by
     good weeks? This is the regime question, and it is free of the overlap
     problem entirely.

The Wald-Wolfowitz runs test is the core statistic. Fewer runs than expected
means clustering; more means alternation.
"""

import csv
import json
import math
import os
import sys

import numpy as np

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
SYMBOLS = ["ETHUSDT", "LINKUSDT", "SOLUSDT"]
WEEK_MS = 7 * 24 * 3600 * 1000


def runs_test(wins):
    """Wald-Wolfowitz. Returns (observed runs, expected, z). z<0 = clustering."""
    n = len(wins)
    nw = int(np.sum(wins))
    nl = n - nw
    if nw == 0 or nl == 0:
        return None
    obs = 1 + int(np.sum(wins[1:] != wins[:-1]))
    exp = 2.0 * nw * nl / n + 1.0
    var = 2.0 * nw * nl * (2.0 * nw * nl - n) / (n * n * (n - 1.0))
    if var <= 0:
        return None
    return obs, exp, (obs - exp) / math.sqrt(var)


def max_streak(wins, value):
    best = cur = 0
    for w in wins:
        cur = cur + 1 if w == value else 0
        best = max(best, cur)
    return best


def expected_max_streak(n, p):
    """Approximate expected longest run of an event with probability p."""
    if p <= 0 or p >= 1 or n < 2:
        return float("nan")
    return math.log(n * (1 - p)) / math.log(1 / p)


def analyse(name, trades):
    """trades: list of (entry_bar, exit_bar, r, timestamp_ms) in time order."""
    if len(trades) < 50:
        return None
    r = np.array([t[2] for t in trades])
    wins = (r > 0).astype(int)

    rt = runs_test(wins)
    lag1_win = float(np.corrcoef(wins[:-1], wins[1:])[0, 1]) if len(wins) > 2 else float("nan")
    lag1_r = float(np.corrcoef(r[:-1], r[1:])[0, 1]) if len(r) > 2 else float("nan")

    prev_w = wins[:-1] == 1
    nxt = wins[1:]
    p_after_win = float(nxt[prev_w].mean()) if prev_w.any() else float("nan")
    p_after_loss = float(nxt[~prev_w].mean()) if (~prev_w).any() else float("nan")

    p = float(wins.mean())
    return {
        "name": name, "n": len(r), "win": 100 * p,
        "runs_obs": rt[0] if rt else None,
        "runs_exp": rt[1] if rt else None,
        "runs_z": rt[2] if rt else None,
        "lag1_win": lag1_win, "lag1_r": lag1_r,
        "p_after_win": 100 * p_after_win, "p_after_loss": 100 * p_after_loss,
        "edge_after_win": 100 * (p_after_win - p_after_loss),
        "max_win_streak": max_streak(wins, 1),
        "exp_win_streak": expected_max_streak(len(wins), p),
        "max_loss_streak": max_streak(wins, 0),
        "exp_loss_streak": expected_max_streak(len(wins), 1 - p),
    }


def sequentialise(trades):
    """Keep only trades that start after the previous kept trade has closed."""
    out, free_at = [], -1
    for t in trades:
        if t[0] > free_at:
            out.append(t)
            free_at = t[1]
    return out


def weekly_persistence(trades):
    """Autocorrelation of weekly summed R - the regime question."""
    if not trades:
        return None
    buckets = {}
    for entry, _, r, ts in trades:
        buckets.setdefault(ts // WEEK_MS, []).append(r)
    keys = sorted(buckets)
    if len(keys) < 20:
        return None
    # Contiguous weeks only, so the lag is a real week.
    series, prev = [], None
    pairs = []
    for k in keys:
        v = float(np.sum(buckets[k]))
        if prev is not None and k == prev[0] + 1:
            pairs.append((prev[1], v))
        prev = (k, v)
        series.append(v)
    if len(pairs) < 20:
        return None
    a = np.array([x[0] for x in pairs])
    b = np.array([x[1] for x in pairs])
    pos = np.array([x > 0 for x in series])
    rt = runs_test(pos.astype(int))
    return {"weeks": len(keys), "pairs": len(pairs),
            "lag1_weekly_R": float(np.corrcoef(a, b)[0, 1]),
            "weekly_runs_z": rt[2] if rt else None,
            "pct_weeks_positive": 100 * float(pos.mean())}


def load_v1(symbol, selective_only):
    out = []
    with open(os.path.join(DATA, f"{symbol}_trades.csv")) as fh:
        for row in csv.DictReader(fh):
            if row["status"] != "CLOSED":
                continue
            if selective_only and row["selective"] != "True":
                continue
            entry = int(row["bar_index"])
            out.append((entry, entry + int(row["bars_held"]),
                        float(row["r_multiple"]), 0))
    return out


def load_h3(symbol, suffix):
    """Rebuild H3 trades with timestamps. Imported so no rule can drift."""
    import run_backtest
    import limit_entry
    from hypothesis_h1 import prep, signal
    from hypothesis_h3 import GAP_GUARD, STOP_ATR, TARGET_R, TIME_STOP, gap_indices

    run_backtest.SUFFIX = suffix
    ts, *_ = run_backtest.load(symbol)
    o, h, l, c, f = prep(symbol, suffix)
    n = len(c)
    gaps = gap_indices(symbol, suffix)
    out = []
    for i in range(run_backtest.WARMUP, n - 1):
        s = signal(i, o, h, l, c, f)
        if s == 0 or any(abs(i - g) <= GAP_GUARD for g in gaps):
            continue
        atr = f["atr"][i]
        res = limit_entry.simulate(i, -s, "MARKET", c[i], STOP_ATR * atr, TARGET_R,
                                   TIME_STOP, 0.25, 6, atr, o, h, l, c, n)
        if res:
            out.append((i, res["exit_idx"], res["r_multiple"], int(ts[i])))
    return out


HDR = (f"{'book':<30}{'n':>7}{'win%':>7}{'runs':>7}{'exp':>7}{'z':>7}"
       f"{'lag1':>8}{'P(W|W)':>8}{'P(W|L)':>8}{'diff':>7}{'maxL':>6}{'expL':>6}")


def show(a):
    if not a:
        return
    print(f"{a['name']:<30}{a['n']:>7}{a['win']:>7.1f}{a['runs_obs']:>7}"
          f"{a['runs_exp']:>7.0f}{a['runs_z']:>7.2f}{a['lag1_win']:>8.3f}"
          f"{a['p_after_win']:>8.1f}{a['p_after_loss']:>8.1f}{a['edge_after_win']:>+7.1f}"
          f"{a['max_loss_streak']:>6}{a['exp_loss_streak']:>6.0f}")


def main():
    report = {}
    print("z < -2 means outcomes CLUSTER (streaks). z > +2 means they ALTERNATE.")
    print("Under independence z is roughly standard normal.\n")

    print("=" * 122)
    print("1. v1 books, trades in time order - WITH overlap (stacked positions share bars)")
    print("=" * 122)
    print(HDR)
    for sym in SYMBOLS:
        for sel, lab in [(False, "all"), (True, "selective")]:
            t = load_v1(sym, sel)
            a = analyse(f"{sym[:-4]} v1 {lab}", t)
            report[f"v1_{sym}_{lab}"] = a
            show(a)

    print("\n" + "=" * 122)
    print("2. Same books, overlap REMOVED (sequential: never enter until the last trade closed)")
    print("=" * 122)
    print(HDR)
    for sym in SYMBOLS:
        for sel, lab in [(False, "all"), (True, "selective")]:
            t = sequentialise(load_v1(sym, sel))
            a = analyse(f"{sym[:-4]} v1 {lab} seq", t)
            report[f"v1seq_{sym}_{lab}"] = a
            show(a)

    print("\n" + "=" * 122)
    print("3. H3 across all three windows, sequential")
    print("=" * 122)
    print(HDR)
    h3_all = []
    for sym in SYMBOLS:
        t = []
        for suffix in ("1h_early", "1h_prior", "1h"):
            t += load_h3(sym, suffix)
        h3_all += t
        a = analyse(f"{sym[:-4]} H3 seq", sequentialise(t))
        report[f"h3_{sym}"] = a
        show(a)

    print("\n" + "=" * 122)
    print("4. Weekly performance persistence - are good weeks followed by good weeks?")
    print("=" * 122)
    print(f"{'book':<30}{'weeks':>8}{'pairs':>8}{'lag1 weekly R':>16}{'runs z':>9}{'% weeks +':>11}")
    for sym in SYMBOLS:
        t = [x for x in h3_all if True]
        w = weekly_persistence([x for x in load_h3(sym, "1h_prior")] +
                               [x for x in load_h3(sym, "1h_early")] +
                               [x for x in load_h3(sym, "1h")])
        if w:
            report[f"weekly_{sym}"] = w
            print(f"{sym[:-4] + ' H3':<30}{w['weeks']:>8}{w['pairs']:>8}"
                  f"{w['lag1_weekly_R']:>16.3f}{w['weekly_runs_z']:>9.2f}"
                  f"{w['pct_weeks_positive']:>11.1f}")

    json.dump(report, open(os.path.join(DATA, "streaks.json"), "w"),
              indent=2, default=float)
    print("\nwrote streaks.json")


if __name__ == "__main__":
    main()
