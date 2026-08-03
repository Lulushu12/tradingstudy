"""
Costed walk-forward on the three strategies that survived the frictionless pass.

WHAT IS ACTUALLY BEING WALKED FORWARD

These strategies have no parameters fitted to this data. Their lengths and
thresholds come from the videos. So a classic optimise-in-sample walk-forward
has nothing to optimise, and running one anyway would be theatre.

There is exactly one thing that WAS fitted: the stop convention. The videos never
define "stop below the recent low", three readings were tested, and the headline
table reported the best one for S5 and S6. That is a selection made with
knowledge of the results, and it is the thing that could be luck. So the walk
forward selects the stop convention on each in-sample window and applies that
choice to the following out-of-sample window, never seeing the future when it
chooses. Pooled out-of-sample performance is then an honest estimate.

S1 states its own stop (the leg origin), so there is nothing to select. For S1
the folds are a pure out-of-sample consistency check.

WHY TRADES ARE FILTERED BY DATE RATHER THAN THE FRAME BEING SLICED

Slicing the price frame per window would throw away indicator warmup and change
the signals near each boundary. Instead each strategy runs once over the whole
series and its trades are assigned to windows by entry time. This is legitimate
precisely because every signal in this codebase is causal: a signal at bar t uses
only bars up to t, so a trade's existence never depends on data after its entry.

COSTS

Binance USD-M perp taker fees are 0.04% per side, 8bps round trip. Slippage is
charged on top at 1bp per fill, 2bps round trip, which is generous for BTCUSDT
at retail size but not free. Total default 10bps round trip, applied to every
trade. All fills are charged at taker rates including S1's limit entries, which
would in practice earn the maker rebate: the conservative direction.
"""

import warnings

import numpy as np
import pandas as pd

import backtest as bt
import data as dat
import strategies as st
from strategies import Cfg

warnings.filterwarnings("ignore")

COMMISSION_BPS = 8.0      # 0.04% per side, round trip
SLIPPAGE_BPS = 2.0        # 1bp per fill, round trip
COST_BPS = COMMISSION_BPS + SLIPPAGE_BPS

IS_MONTHS = 18
OOS_MONTHS = 6

SURVIVORS = {
    "S1 Fib ABCD 0.88": (st.s1_fib_abcd, "30m", ["stated"]),
    "S5 EMA meter + SMI": (st.s5_ema_meter_smi, "4h", ["swing", "nbar", "atr"]),
    "S6 Impulse MACD": (st.s6_impulse_macd, "4h", ["swing", "nbar", "atr"]),
}


def all_trades(fn, tf, conv):
    """Every trade the strategy would have taken over the whole series."""
    df = dat.load_tf("BTCUSDT", tf, verbose=False)
    cfg = Cfg(stop_conv="swing" if conv == "stated" else conv)
    out = []
    for seg in dat.contiguous_segments(df, tf, min_bars=500):
        out.extend(bt.run(seg, fn(seg, cfg), cost_bps=0.0))
    return out


def net_returns(trades, cost_bps=COST_BPS):
    return np.array([t.ret_pct - cost_bps / 100.0 for t in trades])


def summarise(trades, label, cost_bps=COST_BPS):
    if not trades:
        return {"label": label, "n": 0}
    r = net_returns(trades, cost_bps)
    eq = np.cumprod(1 + r / 100)
    peak = np.maximum.accumulate(eq)
    dd = (eq - peak) / peak
    wins, losses = r[r > 0], r[r <= 0]
    gl = -losses.sum()
    return {
        "label": label,
        "n": len(r),
        "win_rate": round(100 * len(wins) / len(r), 1),
        "net_avg_pct": round(r.mean(), 4),
        "profit_factor": round(wins.sum() / gl, 3) if gl > 0 else np.inf,
        "net_total_pct": round((eq[-1] - 1) * 100, 1),
        "max_dd_pct": round(dd.min() * 100, 1),
        "t_stat": round(r.mean() / (r.std(ddof=1) / np.sqrt(len(r))), 2) if len(r) > 2 else np.nan,
    }


def folds(start, end):
    """Rolling (in-sample, out-of-sample) date windows."""
    out = []
    is_start = pd.Timestamp(start)
    while True:
        is_end = is_start + pd.DateOffset(months=IS_MONTHS)
        oos_end = is_end + pd.DateOffset(months=OOS_MONTHS)
        if is_end >= end:
            break
        out.append((is_start, is_end, min(oos_end, end)))
        is_start = is_start + pd.DateOffset(months=OOS_MONTHS)
    return out


def between(trades, lo, hi):
    return [t for t in trades if lo <= t.entry_time < hi]


def main():
    print(f"costs: {COMMISSION_BPS}bps commission + {SLIPPAGE_BPS}bps slippage "
          f"= {COST_BPS}bps round trip, charged on every trade\n")

    rows, oos_pool, fold_log = [], {}, []

    for name, (fn, tf, convs) in SURVIVORS.items():
        print(f"computing {name} [{tf}] ...", flush=True)
        by_conv = {c: all_trades(fn, tf, c) for c in convs}
        every = [t for ts in by_conv.values() for t in ts]
        lo = min(t.entry_time for t in every)
        hi = max(t.exit_time for t in every)

        picked = []
        for is_s, is_e, oos_e in folds(lo.normalize(), hi):
            # choose the stop convention using ONLY in-sample trades
            scored = {}
            for c in convs:
                ins = between(by_conv[c], is_s, is_e)
                scored[c] = net_returns(ins).mean() if len(ins) >= 10 else -np.inf
            best = max(scored, key=scored.get)
            oos = between(by_conv[best], is_e, oos_e)
            picked.extend(oos)
            fold_log.append({
                "strategy": name,
                "is": f"{is_s.date()}..{is_e.date()}",
                "oos": f"{is_e.date()}..{oos_e.date()}",
                "chosen": best,
                "n_oos": len(oos),
                "oos_net_avg": round(net_returns(oos).mean(), 4) if oos else np.nan,
                "oos_net_total": round(net_returns(oos).sum(), 2) if oos else np.nan,
            })
        oos_pool[name] = picked
        rows.append(summarise(picked, name + " (walk-forward OOS)"))
        # in-sample-everything reference, the number the headline table reported
        ref_conv = convs[0] if len(convs) == 1 else max(
            convs, key=lambda c: net_returns(by_conv[c]).mean())
        rows.append(summarise(by_conv[ref_conv], name + f" (all data, {ref_conv})"))

    fl = pd.DataFrame(fold_log)
    print("\n=== per fold, out of sample ===")
    print(fl.to_string(index=False))

    res = pd.DataFrame(rows)
    print("\n=== pooled, net of costs ===")
    print(res.to_string(index=False))

    # ---- cost sweep on the pooled OOS trades
    print("\n=== net average % per trade vs round trip cost (walk-forward OOS) ===")
    sweep = []
    for c in [0, 5, 8, 10, 12, 15, 20, 25, 30]:
        row = {"cost_bps": c}
        for name, tr in oos_pool.items():
            row[name] = round(net_returns(tr, c).mean(), 4) if tr else np.nan
        sweep.append(row)
    sw = pd.DataFrame(sweep)
    print(sw.to_string(index=False))

    # ---- two different resampling questions, which need two different methods
    #
    # Drawdown depends on the ORDER trades arrived in, so reshuffling the actual
    # trades answers "how bad could the equity path have looked". It cannot
    # answer whether the edge is real: a permutation preserves the trade set, so
    # a positive sum stays positive however it is shuffled.
    #
    # Whether the edge is real is a sampling question, so it needs resampling
    # WITH REPLACEMENT: draw a fresh set of trades of the same size from the
    # observed distribution and ask how often the mean comes out above zero.
    rng = np.random.default_rng(12345)
    mc = []
    for name, tr in oos_pool.items():
        if len(tr) < 20:
            continue
        r = net_returns(tr)
        n = len(r)

        dds = np.empty(2000)
        for k in range(2000):
            eq = np.cumprod(1 + rng.permutation(r) / 100)
            peak = np.maximum.accumulate(eq)
            dds[k] = ((eq - peak) / peak).min() * 100

        boot = np.array([rng.choice(r, size=n, replace=True).mean()
                         for _ in range(5000)])
        mc.append({
            "strategy": name,
            "median_dd": round(float(np.median(dds)), 1),
            "p95_dd": round(float(np.percentile(dds, 5)), 1),
            "worst_dd": round(float(dds.min()), 1),
            "boot_mean_lo95": round(float(np.percentile(boot, 2.5)), 4),
            "boot_mean_hi95": round(float(np.percentile(boot, 97.5)), 4),
            "p_edge_positive": round(float((boot > 0).mean()), 3),
        })
    print("\n=== drawdown under 2000 order reshuffles, and a 5000 sample "
          f"bootstrap of the edge (at {COST_BPS}bps) ===")
    print(pd.DataFrame(mc).to_string(index=False))
    pd.DataFrame(mc).to_csv("playlist_study/results/walkforward_resample.csv", index=False)

    fl.to_csv("playlist_study/results/walkforward_folds.csv", index=False)
    res.to_csv("playlist_study/results/walkforward_summary.csv", index=False)
    sw.to_csv("playlist_study/results/walkforward_costsweep.csv", index=False)
    print("\nwrote walkforward_{folds,summary,costsweep}.csv to playlist_study/results/")


if __name__ == "__main__":
    main()
