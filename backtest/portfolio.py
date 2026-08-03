"""Portfolio-level exposure caps, and the one-trade-per-symbol limit never tested.

The original mandate allowed unlimited stacking, which turned out to mean 17
concurrent positions on average and up to 57 at once - so a nominal "1% risk
per trade" was really over 50% of the account live simultaneously. This tests
what actually happens when exposure is capped, across four timeframes.

Regimes compared:
  unlimited          - the mandate as originally run
  1 per symbol       - the option declined at the start of the study
  portfolio cap N    - at most N positions open across ALL symbols at once

When a cap binds, signals are taken in chronological order; ties inside the
same bar break toward higher conviction. Both are decidable at that instant, so
no lookahead is involved.

Sizing is genuinely fixed-fractional: risk is 1% of equity AT ENTRY, and equity
updates when a trade closes. With caps in force that number finally means what
it says, which is the whole point of the exercise.

IMPORTANT: H3-Multi showed the underlying signal does not survive on 25 assets.
Nothing here makes this system tradeable. This is risk characterisation of a
book whose edge is not established.
"""

import json
import os
import sys

import numpy as np

import indicators
import run_backtest
import simulate
import strategy

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
SYMBOLS = ["ETHUSDT", "LINKUSDT", "SOLUSDT"]
TIMEFRAMES = ["15m", "1h", "4h", "1d"]
BAR_MS = {"15m": 900_000, "1h": 3_600_000, "4h": 14_400_000, "1d": 86_400_000}
YEAR_MS = 365.25 * 24 * 3600 * 1000

RISK_FRAC = 0.01
_cache = {}


def signals(symbol, tf):
    """Every selective-book signal, with entry/exit bar, timestamp and R."""
    key = (symbol, tf)
    if key in _cache:
        return _cache[key]
    run_backtest.SUFFIX = tf
    ts, o, h, l, c, v = run_backtest.load(symbol)
    f = indicators.build(o, h, l, c, v)
    n = len(c)
    out = []
    for i in range(run_backtest.WARMUP, n - 1):
        if np.isnan(f["atr"][i]) or f["atr"][i] <= 0 or np.isnan(f["adx"][i]):
            continue
        setup, d = strategy.classify(i, f, c, f["donch_hi"][i - 1], f["donch_lo"][i - 1])
        conv = strategy.conviction(setup, d, i, f, c)
        if conv < strategy.SELECTIVE_THRESHOLD:
            continue
        entry = c[i] * (1 + d * simulate.SLIPPAGE)
        stop, target, tstop, _, _, _ = strategy.levels(setup, d, entry, i, f)
        res = simulate.simulate(i, d, entry, stop, target, tstop, o, h, l, c, n)
        if res and res["status"] == "CLOSED":
            out.append({"symbol": symbol, "t": int(ts[i]), "entry_i": i,
                        "exit_i": res["exit_idx"], "conv": conv,
                        "r": res["r_multiple"], "setup": setup})
    _cache[key] = out
    return out


def apply_cap(all_sigs, mode, cap=None):
    """Filter signals under a concurrency regime. Returns kept trades."""
    # Chronological; ties inside a bar resolve to higher conviction first.
    ordered = sorted(all_sigs, key=lambda s: (s["t"], -s["conv"]))
    open_until = {}     # symbol -> exit timestamp
    open_list = []      # exit timestamps of live positions
    kept = []

    for s in ordered:
        t = s["t"]
        open_list = [x for x in open_list if x > t]
        open_until = {k: v for k, v in open_until.items() if v > t}

        if mode == "per_symbol" and s["symbol"] in open_until:
            continue
        if mode == "portfolio" and len(open_list) >= cap:
            continue
        if mode == "both":
            if s["symbol"] in open_until or len(open_list) >= cap:
                continue

        # Exit timestamp in wall-clock, so caps compose across timeframes.
        exit_t = t + (s["exit_i"] - s["entry_i"]) * s["bar_ms"]
        kept.append({**s, "exit_t": exit_t})
        open_until[s["symbol"]] = exit_t
        open_list.append(exit_t)
    return kept


def simulate_account(trades):
    """Fixed-fractional 1% of equity at entry; equity updates on exit."""
    if not trades:
        return None
    events = []
    for k, tr in enumerate(trades):
        events.append((tr["t"], 0, k))          # entry
        events.append((tr["exit_t"], 1, k))     # exit
    events.sort()

    equity = 1.0
    risk_at = {}
    peak = 1.0
    mdd = 0.0
    concurrent = 0
    max_conc = 0
    for _, kind, k in events:
        if kind == 0:
            risk_at[k] = equity * RISK_FRAC
            concurrent += 1
            max_conc = max(max_conc, concurrent)
        else:
            equity += trades[k]["r"] * risk_at.get(k, 0.0)
            concurrent -= 1
            peak = max(peak, equity)
            mdd = max(mdd, (peak - equity) / peak)
            if equity <= 0:
                return {"equity": 0.0, "cagr": -1.0, "max_dd": 1.0,
                        "max_conc": max_conc, "ruined": True}

    span = max(t["exit_t"] for t in trades) - min(t["t"] for t in trades)
    years = span / YEAR_MS
    cagr = equity ** (1 / years) - 1 if years > 0 and equity > 0 else float("nan")
    return {"equity": equity, "cagr": cagr, "max_dd": mdd,
            "max_conc": max_conc, "years": years, "ruined": False}


def stats(trades, n_signals):
    r = np.array([t["r"] for t in trades])
    w = r[r > 0]
    gl = abs(r[r <= 0].sum())
    eq = peak = mdd_r = 0.0
    for x in r:
        eq += x
        peak = max(peak, eq)
        mdd_r = max(mdd_r, peak - eq)
    return {"n": len(r), "taken_pct": 100 * len(r) / n_signals,
            "win": 100 * len(w) / len(r), "avg": float(r.mean()),
            "tot": float(r.sum()), "pf": float(w.sum() / gl) if gl > 0 else float("nan"),
            "mdd_r": mdd_r}


def main():
    caps = [("unlimited", None), ("per_symbol", None),
            ("portfolio", 3), ("portfolio", 6), ("both", 3)]
    report = {}

    for tf in TIMEFRAMES:
        allsig = []
        for sym in SYMBOLS:
            try:
                s = signals(sym, tf)
            except FileNotFoundError:
                continue
            for x in s:
                x["bar_ms"] = BAR_MS[tf]
            allsig += s
        if not allsig:
            continue

        span_years = (max(s["t"] for s in allsig) - min(s["t"] for s in allsig)) / YEAR_MS
        print("\n" + "=" * 124)
        print(f"{tf.upper()}   {len(allsig)} selective signals across 3 symbols   "
              f"span {span_years:.1f} years")
        print("=" * 124)
        print(f"{'regime':<18}{'taken':>7}{'% of sig':>10}{'win%':>7}{'avgR':>8}"
              f"{'totR':>9}{'PF':>6}{'maxDD(R)':>10}{'maxOpen':>9}"
              f"{'equity x':>10}{'CAGR':>9}{'maxDD %':>9}")
        report[tf] = {}

        for mode, cap in caps:
            kept = apply_cap(allsig, mode, cap)
            if not kept:
                continue
            st = stats(kept, len(allsig))
            ac = simulate_account(kept)
            label = mode if cap is None else f"{mode} {cap}"
            report[tf][label] = {**st, **(ac or {})}
            print(f"{label:<18}{st['n']:>7}{st['taken_pct']:>9.1f}%{st['win']:>7.1f}"
                  f"{st['avg']:>8.3f}{st['tot']:>9.1f}{st['pf']:>6.2f}{st['mdd_r']:>10.1f}"
                  f"{ac['max_conc']:>9}{ac['equity']:>10.2f}"
                  f"{ac['cagr'] * 100:>8.1f}%{ac['max_dd'] * 100:>8.1f}%")

    json.dump(report, open(os.path.join(DATA, "portfolio.json"), "w"),
              indent=2, default=float)
    print("\nwrote portfolio.json")
    print("\nNote: RANGE_FADE is disabled (deleted after out-of-sample confirmation),")
    print("so these books differ slightly from the v1 selective book in the workbook.")


if __name__ == "__main__":
    main()
