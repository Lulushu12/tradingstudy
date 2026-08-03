"""
Run every strategy and write the comparison table.

Quick and dirty pass, as scoped: no commission and no slippage. What keeps that
from being misleading is `breakeven_bps`, the round trip cost in basis points
that would take the average trade to zero. Binance perp taker fees are about 8bps
round trip, so any strategy whose breakeven sits under roughly 10bps is already
dead however good its frictionless equity curve looks. That column, not the
return column, is the one to read first.

Strategies are run per contiguous data segment and the trades pooled, so no
setup ever spans a hole in the data.
"""

import sys
import warnings

import pandas as pd

import backtest as bt
import data as dat
import strategies as st
from strategies import Cfg

warnings.filterwarnings("ignore")

TAKER_BPS = 8.0     # Binance USD-M perp, 0.04% per side round trip


def run_one(name, fn, tf, cfg, symbol="BTCUSDT", min_bars=500):
    df = dat.load_tf(symbol, tf, verbose=False)
    # The step must match the frame's own timeframe. Passing the source
    # timeframe for a resampled frame makes every bar look like a gap, which
    # silently disables the gap guard instead of failing.
    segs = dat.contiguous_segments(df, tf, min_bars=min_bars)
    if not segs:
        raise RuntimeError(f"{name}: no contiguous segment of >={min_bars} bars at {tf}")
    trades = []
    for seg in segs:
        if len(seg) < min_bars:
            continue
        try:
            sig = fn(seg, cfg)
        except Exception as e:
            print(f"  !! {name} [{cfg.stop_conv}] failed on a segment: "
                  f"{type(e).__name__}: {e}")
            return None
        trades.extend(bt.run(seg, sig, cost_bps=0.0))
    if not trades:
        return None
    s = bt.stats(trades, name)
    s["tf"] = tf
    s["stop"] = cfg.stop_conv
    s["variant"] = cfg.variant or "-"
    s["breakeven_bps"] = round(bt.breakeven_cost_bps(trades), 1)
    s["survives_costs"] = s["breakeven_bps"] > TAKER_BPS
    return s


def main():
    rows = []
    only = sys.argv[1] if len(sys.argv) > 1 else None

    for name, (fn, tf, sweep_stops) in st.REGISTRY.items():
        if only and only.lower() not in name.lower():
            continue
        convs = ("swing", "nbar", "atr") if sweep_stops else ("stated",)
        for conv in convs:
            cfg = Cfg(stop_conv=conv if conv != "stated" else "swing")
            print(f"running {name} [{tf}] stop={conv} ...", flush=True)
            r = run_one(name, fn, tf, cfg)
            if r:
                r["stop"] = conv
                rows.append(r)
            else:
                print(f"  (no trades for {name} [{conv}])")

    # extra variants worth seeing next to the defaults
    extras = [
        ("S7 Smoothed HA", st.s7_smoothed_ha, "1h", Cfg(stop_conv="swing", variant="flip")),
        ("S2 Donchian+LWTI+vol", st.s2_donchian_lwti, "5m", Cfg(stop_conv="swing", variant="mid")),
        ("S9 SMC sweep->FVG", st.s9_smc, "15m", Cfg(variant="nosweep")),
        ("S9 SMC sweep->FVG", st.s9_smc, "15m", Cfg(variant="nobos")),
        ("S9 SMC sweep->FVG", st.s9_smc, "15m", Cfg(variant="liq")),
        ("S9 SMC sweep->FVG", st.s9_smc, "15m", Cfg(variant="mid")),
    ]
    for name, fn, tf, cfg in extras:
        if only and only.lower() not in name.lower():
            continue
        print(f"running {name} [{tf}] variant={cfg.variant} ...", flush=True)
        r = run_one(name, fn, tf, cfg)
        if r:
            r["stop"] = "stated" if name.startswith("S9") else cfg.stop_conv
            rows.append(r)

    if not rows:
        print("no results")
        return

    df = pd.DataFrame(rows)
    cols = ["label", "tf", "stop", "variant", "n", "win_rate", "avg_pct", "avg_R",
            "profit_factor", "total_return_pct", "max_dd_pct", "max_losing_streak",
            "trades_per_year", "breakeven_bps", "survives_costs"]
    out = df[[c for c in cols if c in df.columns]].round(3)
    out = out.sort_values("breakeven_bps", ascending=False)
    out.to_csv("playlist_study/results/summary.csv", index=False)
    print("\n" + out.to_string(index=False))
    print(f"\nwrote playlist_study/results/summary.csv")
    print(f"survivors at {TAKER_BPS}bps round trip: "
          f"{int(out['survives_costs'].sum())} of {len(out)}")


if __name__ == "__main__":
    main()
