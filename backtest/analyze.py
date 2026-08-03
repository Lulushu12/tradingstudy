"""Slice the trade log every way that could change how you'd trade it."""

import csv
import json
import os
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
SYMBOLS = ["ETHUSDT", "LINKUSDT", "SOLUSDT"]


def load_trades(symbol):
    out = []
    with open(os.path.join(DATA, f"{symbol}_trades.csv")) as fh:
        for r in csv.DictReader(fh):
            if r["status"] != "CLOSED":
                continue
            for k in ("r_multiple", "gross_pct", "net_pct", "cost_pct",
                      "stop_pct", "conviction", "mae_r", "mfe_r"):
                r[k] = float(r[k])
            r["bars_held"] = int(r["bars_held"])
            r["selective"] = r["selective"] == "True"
            out.append(r)
    return out


def _group(rows, key):
    g = defaultdict(list)
    for r in rows:
        g[key(r)].append(r)
    return g


def agg(rows):
    if not rows:
        return None
    rs = np.array([r["r_multiple"] for r in rows])
    wins = rs[rs > 0]
    losses = rs[rs <= 0]
    gl = abs(losses.sum())
    # Gross R strips fees/slippage/funding out, to separate edge from friction.
    gross_r = np.array([r["gross_pct"] / r["stop_pct"] for r in rows])
    return {
        "n": len(rows),
        "win_pct": round(100 * len(wins) / len(rs), 1),
        "avg_R": round(float(rs.mean()), 4),
        "gross_avg_R": round(float(gross_r.mean()), 4),
        "total_R": round(float(rs.sum()), 1),
        "PF": round(float(wins.sum() / gl), 3) if gl > 0 else None,
        "avg_MAE_R": round(float(np.mean([r["mae_r"] for r in rows])), 2),
        "avg_MFE_R": round(float(np.mean([r["mfe_r"] for r in rows])), 2),
        "avg_bars": round(float(np.mean([r["bars_held"] for r in rows])), 1),
    }


def table(title, groups):
    print(f"\n### {title}")
    print(f"{'bucket':<26}{'n':>7}{'win%':>7}{'avgR':>9}{'grossR':>9}{'totR':>9}{'PF':>7}{'MAE':>6}{'MFE':>6}")
    for k in sorted(groups, key=str):
        a = agg(groups[k])
        if not a:
            continue
        pf = a["PF"] if a["PF"] is not None else 0.0
        print(
            f"{str(k):<26}{a['n']:>7}{a['win_pct']:>7}{a['avg_R']:>9.3f}"
            f"{a['gross_avg_R']:>9.3f}{a['total_R']:>9.1f}{pf:>7.2f}"
            f"{a['avg_MAE_R']:>6.2f}{a['avg_MFE_R']:>6.2f}"
        )


def bench(symbol):
    px = []
    with open(os.path.join(DATA, f"{symbol}_1h.csv")) as fh:
        for r in csv.DictReader(fh):
            px.append(float(r["close"]))
    return (px[-1] / px[0] - 1) * 100, px[0], px[-1]


def main():
    report = {}
    for symbol in SYMBOLS:
        rows = load_trades(symbol)
        bh, p0, p1 = bench(symbol)
        print("\n" + "=" * 96)
        print(f"{symbol}   buy&hold over window: {bh:+.1f}%  ({p0:.2f} -> {p1:.2f})")
        print("=" * 96)

        sel = [r for r in rows if r["selective"]]
        table("by setup", _group(rows, lambda r: r["setup"]))
        table("by direction", _group(rows, lambda r: r["direction"]))
        table("by exit reason", _group(rows, lambda r: r["exit_reason"]))
        table("by conviction bucket", _group(rows, lambda r: f"{int(r['conviction'])}-{int(r['conviction']) + 1}"))
        table("selective vs rest", _group(rows, lambda r: "SELECTIVE" if r["selective"] else "filtered_out"))
        table("selective: setup x dir", _group(sel, lambda r: f"{r['setup'][:9]}/{r['direction'][0]}"))

        cost_share = float(np.mean([r["cost_pct"] / r["stop_pct"] for r in rows]))
        print(f"\n  friction: costs eat {cost_share * 100:.1f}% of one R on the average trade")

        report[symbol] = {
            "buy_hold_pct": round(bh, 2),
            "all": agg(rows),
            "selective": agg(sel),
            "by_setup": {k: agg(v) for k, v in _group(rows, lambda r: r["setup"]).items()},
            "by_direction": {k: agg(v) for k, v in _group(rows, lambda r: r["direction"]).items()},
            "by_exit": {k: agg(v) for k, v in _group(rows, lambda r: r["exit_reason"]).items()},
            "by_conviction": {k: agg(v) for k, v in _group(
                rows, lambda r: f"{int(r['conviction'])}-{int(r['conviction']) + 1}").items()},
            "selective_by_setup_dir": {k: agg(v) for k, v in _group(
                sel, lambda r: f"{r['setup']}/{r['direction']}").items()},
            "cost_share_of_R_pct": round(cost_share * 100, 2),
        }

    with open(os.path.join(DATA, "analysis.json"), "w") as fh:
        json.dump(report, fh, indent=2)
    print("\nwrote analysis.json")


if __name__ == "__main__":
    main()
