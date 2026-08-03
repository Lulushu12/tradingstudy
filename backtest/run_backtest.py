"""Drive the backtest across ETH, LINK and SOL and emit per-trade logs.

Produces, per symbol:
  data/<SYM>_trades.csv   - one row per hourly close (the always-on book)
The selective book is the subset with conviction >= SELECTIVE_THRESHOLD and is
flagged on each row rather than duplicated, so the two views stay reconcilable.
"""

import csv
import json
import os
import time

import numpy as np

import indicators
import strategy
import simulate

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
SYMBOLS = ["ETHUSDT", "LINKUSDT", "SOLUSDT"]

# Bars needed before indicators are trustworthy (EMA200 + ADX + vol regime seed).
WARMUP = 500

# Timeframe of the source candles. All strategy parameters are expressed in
# BARS, not wall-clock, so switching this re-runs the identical system on a
# different timeframe - EMA200 becomes 200 fifteen-minute bars rather than 200
# hourly ones, and a 48-bar time stop becomes 12 hours rather than 48.
SUFFIX = "1h"


def load(symbol):
    path = os.path.join(DATA, f"{symbol}_{SUFFIX}.csv")
    ts, o, h, l, c, v = [], [], [], [], [], []
    with open(path) as fh:
        for row in csv.DictReader(fh):
            ts.append(int(row["open_time"]))
            o.append(float(row["open"]))
            h.append(float(row["high"]))
            l.append(float(row["low"]))
            c.append(float(row["close"]))
            v.append(float(row["volume"]))
    return (
        np.array(ts),
        np.array(o),
        np.array(h),
        np.array(l),
        np.array(c),
        np.array(v),
    )


def iso(ms):
    return time.strftime("%Y-%m-%d %H:%M", time.gmtime(ms / 1000))


def run_symbol(symbol, target_mode="fixed_r"):
    ts, o, h, l, c, v = load(symbol)
    n = len(c)
    f = indicators.build(o, h, l, c, v)
    pivots = indicators.pivot_lists(h, l)

    trades = []
    for i in range(WARMUP, n - 1):  # need at least one forward bar to resolve
        if np.isnan(f["atr"][i]) or f["atr"][i] <= 0 or np.isnan(f["adx"][i]):
            continue

        prev_dh = f["donch_hi"][i - 1]
        prev_dl = f["donch_lo"][i - 1]
        setup, direction = strategy.classify(i, f, c, prev_dh, prev_dl)
        conv = strategy.conviction(setup, direction, i, f, c)

        raw_close = c[i]
        # Market entry pays the spread/slippage in the direction of the trade.
        entry_px = raw_close * (1 + direction * simulate.SLIPPAGE)

        stop, target, tstop, stop_note, r_mult, target_note = strategy.levels(
            setup, direction, entry_px, i, f, pivots, target_mode
        )
        res = simulate.simulate(
            i, direction, entry_px, stop, target, tstop, o, h, l, c, n
        )
        if res is None:
            continue

        th = strategy.thesis(
            setup, direction, i, f, c, entry_px, stop, target, r_mult, stop_note, conv,
            target_note
        )

        trades.append(
            {
                "trade_id": f"{symbol[:-4]}-{len(trades) + 1:05d}",
                "symbol": symbol,
                "entry_time_utc": iso(ts[i]),
                "bar_index": i,
                "setup": setup,
                "direction": "LONG" if direction == 1 else "SHORT",
                "conviction": round(conv, 2),
                "selective": conv >= strategy.SELECTIVE_THRESHOLD,
                "entry_price": round(entry_px, 6),
                "stop_loss": round(stop, 6),
                "take_profit": round(target, 6),
                "stop_pct": round(abs(entry_px - stop) / entry_px * 100, 3),
                "target_pct": round(abs(target - entry_px) / entry_px * 100, 3),
                "planned_rr": round(r_mult, 2),
                "stop_logic": stop_note,
                "target_logic": target_note,
                "time_stop_bars": tstop,
                "atr_pct": round(f["atr_pct"][i] * 100, 3),
                "adx": round(float(f["adx"][i]), 1),
                "rsi": round(float(f["rsi"][i]), 1),
                "stretch_atr": round(float(f["stretch"][i]), 2),
                "vol_regime_pct": (
                    None if np.isnan(f["vol_regime"][i]) else round(float(f["vol_regime"][i]) * 100, 1)
                ),
                "ema21": round(float(f["ema21"][i]), 6),
                "ema55": round(float(f["ema55"][i]), 6),
                "ema200": round(float(f["ema200"][i]), 6),
                "exit_time_utc": iso(ts[res["exit_idx"]]) if res["exit_idx"] is not None else "",
                "exit_price": round(res["exit_px"], 6) if res["exit_px"] is not None else None,
                "exit_reason": res["exit_reason"],
                "bars_held": res["bars_held"],
                "status": res["status"],
                "gross_pct": round(res["gross_pct"] * 100, 4) if res["gross_pct"] is not None else None,
                "cost_pct": round(res["cost_pct"] * 100, 4) if res["cost_pct"] is not None else None,
                "net_pct": round(res["net_pct"] * 100, 4) if res["net_pct"] is not None else None,
                "r_multiple": round(res["r_multiple"], 3) if res["r_multiple"] is not None else None,
                "pnl_usd": round(res["pnl_usd"], 2) if res["pnl_usd"] is not None else None,
                "mae_r": round(res["mae_r"], 2),
                "mfe_r": round(res["mfe_r"], 2),
                "thesis": th,
            }
        )
    return trades


FIELDS = [
    "trade_id", "symbol", "entry_time_utc", "bar_index", "setup", "direction",
    "conviction", "selective", "entry_price", "stop_loss", "take_profit",
    "stop_pct", "target_pct", "planned_rr", "stop_logic", "target_logic", "time_stop_bars",
    "atr_pct", "adx", "rsi", "stretch_atr", "vol_regime_pct",
    "ema21", "ema55", "ema200",
    "exit_time_utc", "exit_price", "exit_reason", "bars_held", "status",
    "gross_pct", "cost_pct", "net_pct", "r_multiple", "pnl_usd",
    "mae_r", "mfe_r", "thesis",
]


def stats(trades):
    closed = [t for t in trades if t["status"] == "CLOSED"]
    if not closed:
        return {}
    rs = [t["r_multiple"] for t in closed]
    wins = [r for r in rs if r > 0]
    losses = [r for r in rs if r <= 0]
    gross_win = sum(wins)
    gross_loss = abs(sum(losses))

    # Max drawdown on the cumulative-R curve, in R.
    eq, peak, mdd = 0.0, 0.0, 0.0
    for r in rs:
        eq += r
        peak = max(peak, eq)
        mdd = max(mdd, peak - eq)

    return {
        "trades": len(trades),
        "closed": len(closed),
        "still_open": len(trades) - len(closed),
        "win_rate_pct": round(100.0 * len(wins) / len(closed), 2),
        "avg_r": round(float(np.mean(rs)), 4),
        "median_r": round(float(np.median(rs)), 4),
        "total_r": round(sum(rs), 1),
        "expectancy_usd": round(float(np.mean(rs)) * simulate.RISK_PER_TRADE, 2),
        "profit_factor": round(gross_win / gross_loss, 3) if gross_loss > 0 else None,
        "max_dd_r": round(mdd, 1),
        "avg_win_r": round(float(np.mean(wins)), 3) if wins else 0.0,
        "avg_loss_r": round(float(np.mean(losses)), 3) if losses else 0.0,
        "avg_bars_held": round(float(np.mean([t["bars_held"] for t in closed])), 1),
        "avg_mae_r": round(float(np.mean([t["mae_r"] for t in closed])), 3),
        "avg_mfe_r": round(float(np.mean([t["mfe_r"] for t in closed])), 3),
    }


def main():
    # The trade logs in this workbook are the RECORD of the original study, and
    # that study is what established RANGE_FADE should be deleted. Regenerating
    # them with the setup already removed would erase the evidence for its own
    # removal, so the flag is turned back on for log generation only. The live
    # configuration - System v3 - has it off.
    strategy.ENABLE_RANGE_FADE = True

    summary = {}
    for symbol in SYMBOLS:
        t0 = time.time()
        trades = run_symbol(symbol)
        path = os.path.join(DATA, "%s_trades.csv" % symbol if SUFFIX == "1h"
                            else "%s_%s_trades.csv" % (symbol, SUFFIX))
        with open(path, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=FIELDS)
            w.writeheader()
            w.writerows(trades)

        sel = [t for t in trades if t["selective"]]
        summary[symbol] = {
            "always_on": stats(trades),
            "selective": stats(sel),
            "setup_mix": {
                s: sum(1 for t in trades if t["setup"] == s)
                for s in strategy.SETUP_PARAMS
            },
        }
        print(f"[{symbol}] {len(trades)} trades ({len(sel)} selective) in {time.time() - t0:.1f}s")
        print(f"    always-on: {summary[symbol]['always_on']}")
        print(f"    selective: {summary[symbol]['selective']}")

    with open(os.path.join(DATA, "summary.json"), "w") as fh:
        json.dump(summary, fh, indent=2)


if __name__ == "__main__":
    main()
