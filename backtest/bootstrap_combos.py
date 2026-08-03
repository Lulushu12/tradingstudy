"""Block-bootstrap confidence intervals for each setup x direction combination.

Overlapping trades are not independent observations - the same move is sampled
hour after hour - so resampling individual trades would understate uncertainty
by roughly 3x. This resamples contiguous blocks of entry bars instead, which
keeps clustered trades together and gives an honest interval.

A combination "clears the bar" only if the 95% interval on average R excludes
zero. Reported per symbol and pooled across all three.
"""

import csv
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
SYMBOLS = ["ETHUSDT", "LINKUSDT", "SOLUSDT"]

BLOCK = 168        # bars per bootstrap block (one week of hourly bars)
RESAMPLES = 4000
MIN_N = 30         # below this, an interval is not worth quoting
CONV_LO, CONV_HI = 6.0, 8.0

rng = np.random.default_rng(11)


def load(symbol, suffix="1h"):
    path = os.path.join(DATA, f"{symbol}_trades.csv" if suffix == "1h"
                        else f"{symbol}_{suffix}_trades.csv")
    return [r for r in csv.DictReader(open(path)) if r["status"] == "CLOSED"]


def in_band(rows):
    return [r for r in rows if CONV_LO <= float(r["conviction"]) < CONV_HI]


def boot(rows, block=BLOCK):
    """Returns point estimates and bootstrap intervals for avg R and win rate."""
    rs = np.array([float(r["r_multiple"]) for r in rows])
    bars = np.array([int(r["bar_index"]) for r in rows])
    wins = (rs > 0).astype(float)

    blk = bars // block
    ub = np.unique(blk)
    idx_by_block = {b: np.flatnonzero(blk == b) for b in ub}

    means = np.empty(RESAMPLES)
    wrs = np.empty(RESAMPLES)
    for i in range(RESAMPLES):
        pick = rng.choice(ub, size=len(ub), replace=True)
        sel = np.concatenate([idx_by_block[p] for p in pick])
        means[i] = rs[sel].mean()
        wrs[i] = 100.0 * wins[sel].mean()

    # Breakeven win rate implied by this group's own payoff shape.
    w = rs[rs > 0]
    l = rs[rs <= 0]
    aw = w.mean() if len(w) else 0.0
    al = abs(l.mean()) if len(l) else 0.0
    breakeven = 100.0 * al / (aw + al) if (aw + al) > 0 else float("nan")

    return {
        "n": len(rs),
        "win": 100.0 * wins.mean(),
        "avg_R": float(rs.mean()),
        "lo": float(np.percentile(means, 2.5)),
        "hi": float(np.percentile(means, 97.5)),
        "p_pos": 100.0 * float((means > 0).mean()),
        "win_lo": float(np.percentile(wrs, 2.5)),
        "win_hi": float(np.percentile(wrs, 97.5)),
        "breakeven_win": breakeven,
        "clears": bool(np.percentile(means, 2.5) > 0),
    }


def report(title, groups, block=BLOCK):
    print("\n" + "=" * 108)
    print(title)
    print("=" * 108)
    print(f"{'combination':<28}{'n':>6}{'win%':>7}{'BE%':>7}{'avgR':>8}"
          f"{'95% CI on avg R':>22}{'P(>0)':>8}{'clears':>8}")
    out = {}
    for k in sorted(groups):
        rows = groups[k]
        if len(rows) < MIN_N:
            print(f"{k:<28}{len(rows):>6}{'':>7}{'':>7}{'':>8}{'too few trades':>22}")
            continue
        b = boot(rows, block)
        out[k] = b
        ci = f"[{b['lo']:+.3f}, {b['hi']:+.3f}]"
        print(f"{k:<28}{b['n']:>6}{b['win']:>7.1f}{b['breakeven_win']:>7.1f}{b['avg_R']:>8.3f}"
              f"{ci:>22}{b['p_pos']:>8.1f}{('YES' if b['clears'] else 'no'):>8}")
    return out


def main():
    suffix = sys.argv[1] if len(sys.argv) > 1 else "1h"
    block = BLOCK if suffix == "1h" else BLOCK * 4  # keep one week of wall-clock

    pooled = []
    per_symbol = {}
    for s in SYMBOLS:
        rows = in_band(load(s, suffix))
        per_symbol[s] = rows
        pooled += rows

    groups = {}
    for r in pooled:
        groups.setdefault(f"{r['setup']}/{r['direction']}", []).append(r)
    groups["ALL 6-8 COMBINED"] = pooled
    report(f"POOLED across ETH+LINK+SOL - conviction 6-8 band ({suffix} bars, "
           f"{block}-bar blocks, {RESAMPLES} resamples)", groups, block)

    for s in SYMBOLS:
        g = {}
        for r in per_symbol[s]:
            g.setdefault(f"{r['setup']}/{r['direction']}", []).append(r)
        g[f"ALL 6-8 {s[:-4]}"] = per_symbol[s]
        report(f"{s} - conviction 6-8 band", g, block)


if __name__ == "__main__":
    main()
