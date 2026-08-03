"""Run the declared list from FROZEN_SPEC_TSM.md and report. No optimisation anywhere.

Holdout is enforced here, in the loader, not by convention: anything dated on or after
HOLDOUT_START is dropped before a strategy ever sees the frame.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import data as D                      # noqa: E402
import indicators as I                # noqa: E402
from engine import Engine, stats      # noqa: E402
from strategies import RUNS           # noqa: E402

HOLDOUT_START = pd.Timestamp("2025-01-01", tz="UTC")
COST_SWEEP = [0.0000, 0.0005, 0.0010, 0.0015, 0.0020, 0.0030]
BASE_COST = 0.0005
MIN_TRADES = 30


def studied(key: str) -> pd.DataFrame:
    df = D.load(key)
    cut = df[df["dt"] < HOLDOUT_START].reset_index(drop=True)
    if len(cut) == len(df):
        raise RuntimeError(f"{key}: holdout cut removed nothing, check the date filter")
    return cut


def lookahead_selftest(df: pd.DataFrame) -> list[str]:
    """Recompute each indicator on a truncated frame; the last value must be unchanged.

    If any indicator peeked forward, truncating the future would move it.
    """
    fails = []
    k = len(df) - 40
    full, trunc = df, df.iloc[:k].copy()
    checks = {
        "ema20": lambda d: I.ema(d["close"], 20),
        "ema200": lambda d: I.ema(d["close"], 200),
        "atr14": lambda d: I.atr(d, 14),
        "macd_line": lambda d: I.macd(d["close"])[0],
        "macd_sig": lambda d: I.macd(d["close"])[1],
        "mfi50": lambda d: I.mfi(d, 50),
        "don_hi20": lambda d: I.donchian(d, 20)[0],
        "swing_low": lambda d: I.fractal_pivots(d, 2, 2)[0],
    }
    for name, fn in checks.items():
        a, b = fn(full).iloc[k - 1], fn(trunc).iloc[k - 1]
        if not (pd.isna(a) and pd.isna(b)) and not np.isclose(float(a), float(b), rtol=1e-9):
            fails.append(f"{name}: full={a} truncated={b}")
    return fails


def causality_selftest(trades, df) -> list[str]:
    """No fill may precede its own signal bar, and no exit may precede its entry."""
    bad = []
    for t in trades:
        if t.exit_i >= 0 and t.exit_i < t.entry_i:
            bad.append(f"exit {t.exit_i} before entry {t.entry_i}")
        if not (df["low"].iloc[t.entry_i] * 0.5 <= t.entry_px <= df["high"].iloc[t.entry_i] * 2.0):
            bad.append(f"entry price {t.entry_px} implausible for bar {t.entry_i}")
    return bad


def buy_and_hold(df: pd.DataFrame, cost: float = BASE_COST) -> dict:
    """The control that matters. A long-biased strategy on BTC over a bull span has to beat
    simply holding, or its edge is the asset's drift wearing a strategy costume."""
    eq = 10_000.0 * (1 - cost) * df["close"] / df["close"].iloc[0] * (1 - cost)
    dd = (eq / eq.cummax() - 1.0).min()
    return {"return_pct": round(100 * (eq.iloc[-1] / 10_000 - 1), 2),
            "max_drawdown_pct": round(100 * dd, 2)}


def time_in_market(trades, n_bars: int) -> float:
    held = sum(max(1, (t.exit_i - t.entry_i)) for t in trades if t.exit_i >= 0)
    return round(100 * held / n_bars, 1)


def s4_filter_census(df: pd.DataFrame) -> dict:
    """Which invented gate is doing the work when S4 produces almost no signals."""
    e20, e50 = I.ema(df["close"], 20), I.ema(df["close"], 50)
    o, h, l, c = df["open"], df["high"], df["low"], df["close"]
    bh = pd.concat([o, c], axis=1).max(axis=1)
    bl = pd.concat([o, c], axis=1).min(axis=1)
    outside = (h > h.shift(1)) & (l < l.shift(1)) & (bh >= bh.shift(1)) & (bl <= bl.shift(1))
    align = (e20 > e50) | (e20 < e50)
    slope_up = I.monotonic_run(e20, 5, True) & I.monotonic_run(e50, 5, True)
    slope_dn = I.monotonic_run(e20, 5, False) & I.monotonic_run(e50, 5, False)
    trend = ((e20 > e50) & slope_up & (c > e20)) | ((e20 < e50) & slope_dn & (c < e20))
    zone = (((l <= e20) & (h >= e50) & (c > e50)) | ((h >= e20) & (l <= e50) & (c < e50)))
    return {
        "bars": len(df),
        "outside_bars": int(outside.sum()),
        "ema_aligned": int(align.sum()),
        "trend_gate_pass (INVENTED slope)": int(trend.sum()),
        "zone_touch (INVENTED zone test)": int(zone.sum()),
        "trend AND zone": int((trend & zone).sum()),
        "trend AND zone AND outside": int((trend & zone & outside).sum()),
    }


def main():
    print("=" * 100)
    print("FROZEN_SPEC_TSM.md  |  studied span only, holdout >= %s is not loaded"
          % HOLDOUT_START.date())
    print("=" * 100)

    frames = {}
    for key in {k for k, _ in RUNS.values()}:
        frames[key] = studied(key)
        d = frames[key]
        print(f"{key:14s} {len(d):6d} bars  {d['dt'].iloc[0].date()} -> {d['dt'].iloc[-1].date()}")

    print("\nlook-ahead self-test")
    ok = True
    for key, d in frames.items():
        f = lookahead_selftest(d)
        print(f"  {key:14s} {'PASS' if not f else 'FAIL ' + '; '.join(f)}")
        ok &= not f
    if not ok:
        raise SystemExit("look-ahead self-test failed, refusing to report results")

    rows, sweeps, all_trades = [], [], {}
    for name, (key, build) in RUNS.items():
        df = frames[key]
        sig, kw = build(df)
        trades, curve = Engine(df, cost_per_side=BASE_COST).run(sig, **kw)
        bad = causality_selftest(trades, df)
        if bad:
            raise SystemExit(f"{name}: causality self-test failed: {bad[:3]}")
        st = stats(trades, curve)
        st["run"] = name
        st["series"] = key
        st["time_in_market_pct"] = time_in_market(trades, len(df))
        rows.append(st)
        all_trades[name] = trades

        for cst in COST_SWEEP:
            tr, cv = Engine(df, cost_per_side=cst).run(sig, **kw)
            s2 = stats(tr, cv)
            sweeps.append({"run": name, "cost_per_side_pct": round(cst * 100, 3),
                           "expectancy": s2.get("expectancy_per_trade", np.nan),
                           "profit_factor": s2.get("profit_factor", np.nan),
                           "trades": s2.get("trades", 0)})

    res = pd.DataFrame(rows).set_index("run")
    cols = ["series", "trades", "expectancy_per_trade", "expectancy_R", "win_rate_pct",
            "profit_factor", "return_pct", "max_drawdown_pct", "longest_losing_streak",
            "time_in_market_pct", "avg_win", "avg_loss", "total_costs"]
    pd.set_option("display.width", 250, "display.max_columns", 60)
    print("\n" + "=" * 100)
    print("RESULTS  (0.05% per side, 0.10% round trip, 1% equity risk where a stop exists)")
    print("=" * 100)
    print(res[cols].to_string())

    print("\n" + "=" * 100)
    print("CONTROL: buy and hold over the same studied span, same cost")
    print("=" * 100)
    for key, d in frames.items():
        bh = buy_and_hold(d)
        print(f"  {key:14s} return {bh['return_pct']:>10.2f}%   max drawdown {bh['max_drawdown_pct']:>8.2f}%")
    print("  Note: only the risk-sized runs (s2, s3_atr, s4) are scale-comparable to each")
    print("  other. s1 and s3_nostop take full unlevered notional, so their returns are the")
    print("  ones that must be read against buy and hold.")

    print("\n" + "=" * 100)
    print("S4 FILTER CENSUS: where the signals go")
    print("=" * 100)
    for k, v in s4_filter_census(frames["BTCUSDT_1D"]).items():
        print(f"  {k:36s} {v}")

    print("\n" + "=" * 100)
    print("KILL RULE  (expectancy <= 0, or PF < 1.0, or fewer than %d trades = undecidable)" % MIN_TRADES)
    print("=" * 100)
    for name, r in res.iterrows():
        n = r["trades"]
        if n == 0:
            verdict = "NO TRADES"
        elif n < MIN_TRADES:
            verdict = f"UNDECIDABLE (only {n} trades)"
        elif r["expectancy_per_trade"] <= 0 or r["profit_factor"] < 1.0:
            verdict = "DEAD"
        else:
            verdict = "not yet falsified"
        print(f"  {name:12s} {verdict}")

    print("\n" + "=" * 100)
    print("BOOTSTRAP 95% CI on mean R per trade (10,000 resamples of the trade list)")
    print("=" * 100)
    rng = np.random.default_rng(20260803)
    for name, trs in all_trades.items():
        r = np.array([t.r_multiple for t in trs], dtype=float)
        r = r[np.isfinite(r)]
        if len(r) < 5:
            print(f"  {name:12s} too few trades to bootstrap ({len(r)})")
            continue
        boot = rng.choice(r, size=(10_000, len(r)), replace=True).mean(axis=1)
        lo, hi = np.percentile(boot, [2.5, 97.5])
        # 4 independent strategy families were tested, so a 95% interval is too generous.
        # The 98.75% interval is the Bonferroni-corrected equivalent for 4 tests.
        blo, bhi = np.percentile(boot, [0.625, 99.375])
        tag95 = "excl 0" if lo > 0 or hi < 0 else "INCL 0"
        tagbf = "excl 0" if blo > 0 or bhi < 0 else "INCL 0"
        print(f"  {name:12s} meanR {r.mean():+7.3f}  95% [{lo:+7.3f},{hi:+7.3f}] {tag95}"
              f"   Bonf [{blo:+7.3f},{bhi:+7.3f}] {tagbf}")

    print("\n" + "=" * 100)
    print("REGIME CHECK: net R by calendar year (an edge in one year is a regime bet)")
    print("=" * 100)
    per_year = {}
    for name, trs in all_trades.items():
        d = {}
        for t in trs:
            if t.exit_dt is None:
                continue
            y = pd.Timestamp(t.exit_dt).year
            d[y] = d.get(y, 0.0) + (t.r_multiple if np.isfinite(t.r_multiple) else 0.0)
        per_year[name] = d
    yr = pd.DataFrame(per_year).T.sort_index(axis=1).round(1)
    print(yr.to_string())

    sw = pd.DataFrame(sweeps).pivot(index="run", columns="cost_per_side_pct",
                                    values="expectancy")
    print("\n" + "=" * 100)
    print("COST SWEEP: expectancy per trade vs cost per side (%)")
    print("=" * 100)
    print(sw.to_string())

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
    os.makedirs(out, exist_ok=True)
    res.to_csv(os.path.join(out, "summary.csv"))
    pd.DataFrame(sweeps).to_csv(os.path.join(out, "cost_sweep.csv"), index=False)
    for name, trs in all_trades.items():
        pd.DataFrame([{
            "side": t.side, "entry_dt": t.entry_dt, "entry_px": t.entry_px,
            "exit_dt": t.exit_dt, "exit_px": t.exit_px, "pnl": t.pnl,
            "r_multiple": t.r_multiple, "reason": t.reason, "cost": t.cost,
        } for t in trs]).to_csv(os.path.join(out, f"trades_{name}.csv"), index=False)
    print(f"\nwritten to {out}")


if __name__ == "__main__":
    main()
