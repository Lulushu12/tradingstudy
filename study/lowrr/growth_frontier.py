"""Two questions, answered numerically rather than by argument.

Q1. Is there an R:R "fraction" where we win far more than we lose AND it pays?
    The barrier ladder already showed winrate is bought at fair odds, so the real
    question is which rung COMPOUNDS fastest once the edge is conditioned properly.
    That is not the rung with the best winrate, nor the best expectancy per trade,
    it is the one maximising geometric growth per unit TIME, which trades off edge
    per trade against how many trades per month and how violent the variance is.

Q2. What does it take to reach 10% a month, and what does it cost in drawdown?
    Monthly return is roughly (R per month) x (risk per trade), and drawdown scales
    close to linearly in risk per trade. So the target pins the risk size, and the
    risk size pins the drawdown. This walks the whole frontier and reports where
    10% lands, including whether it is even reachable before position sizing breaks.

Uses the strongest thing found in the study: the two short rules conditioned on
open interest in the top decile of its trailing 90-day range, over BTC, ETH and
SOL. That is a 3-instrument result and still provisional, so the unconditioned
12-perp portfolio is carried alongside as the conservative comparison.
"""
import sys, os, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd
from lowrr import core
from lowrr.multiasset import load_path_file, BN, MAJORS, SLIP_MAJOR, SLIP_ALT
from lowrr.finalists_lowrr import nonoverlap
from lowrr.oi_verify import build, SYMS, RR, AM

HERE = os.path.dirname(os.path.abspath(__file__))
RR_FULL = [0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0]

def book(oi_filter=True, cap=4):
    """Concurrency-capped portfolio per rr, over the instruments with metrics."""
    out = {rr: [] for rr in RR_FULL}
    for sym in SYMS:
        if not os.path.exists(os.path.join(HERE, "flow", f"{sym}_metrics.parquet")):
            continue
        d = build(sym)
        path = load_path_file(os.path.join(BN, f"{sym}_15m.parquet"))
        slip = SLIP_MAJOR if sym in MAJORS else SLIP_ALT
        base = (((d["close"] < d["bb_lo"])
                 | ((d["close"] < d["ema200"]) & (d["vol_ratio"] > 1.8)
                    & (d["close"] < d["open"])))).fillna(False).values
        mask = base & (d["oi_p90"] >= 0.9).fillna(False).values if oi_filter else base
        idx = np.where(mask)[0]; idx = idx[idx < len(d) - 1]
        tr = core.trades_for_signals(d, idx, -np.ones(len(idx)), AM, RR_FULL, path,
                                     max_hold_days=50)
        tr["cost_R"] = core.cost_R(tr["stop_frac"].values, tr["nights"].values,
                                   slip_rt=2 * slip)
        tr["net_R"] = tr["gross_R"] - tr["cost_R"]
        tr["sym"] = sym
        for rr in RR_FULL:
            out[rr].append(nonoverlap(tr[tr["rr"] == rr].copy()))
    books = {}
    for rr, frames in out.items():
        if not frames:
            continue
        t = pd.concat(frames, ignore_index=True).sort_values("entry_time")
        t = t.reset_index(drop=True)
        open_pos, taken = [], []
        for r in t.itertuples():
            open_pos = [p for p in open_pos if p[0] > r.entry_time]
            if len(open_pos) >= cap or any(p[1] == r.sym for p in open_pos):
                continue
            open_pos.append((r.exit_time, r.sym))
            taken.append(r)
        books[rr] = pd.DataFrame(taken).sort_values("exit_time").reset_index(drop=True)
    return books

def walk(t, f):
    """Compound at risk fraction f per trade. Returns monthly rate and max DD."""
    eq = 1.0; peak = 1.0; mdd = 0.0
    for x in t["net_R"].values:
        eq *= (1 + f * x)
        if eq <= 0:
            return -1.0, -1.0, 0.0
        peak = max(peak, eq); mdd = min(mdd, (eq - peak) / peak)
    yrs = (t["exit_time"].iloc[-1] - t["exit_time"].iloc[0]) / (365.25 * 86400)
    mo = yrs * 12
    return eq ** (1 / mo) - 1, mdd, eq

def stats(t):
    res = (t["res"] != 0).sum()
    wr = (t["res"] == 1).sum() / res
    yrs = (t["exit_time"].iloc[-1] - t["exit_time"].iloc[0]) / (365.25 * 86400)
    tpm = len(t) / (yrs * 12)
    streak = mx = 0
    for w in (t["net_R"] > 0).values:
        if w: streak = 0
        else: streak += 1; mx = max(mx, streak)
    return wr, tpm, t["net_R"].mean(), mx, t["net_R"].std()

def main():
    for label, oif in [("OI-FILTERED (BTC/ETH/SOL, provisional)", True),
                       ("UNFILTERED base rules (same 3 instruments)", False)]:
        books = book(oi_filter=oif)
        print("\n" + "=" * 112)
        print(f"{label}")
        print("=" * 112)
        print("Q1: which R:R fraction compounds fastest?")
        print(f"{'rr':>6}{'n':>6}{'WR':>7}{'W:L ratio':>11}{'t/mo':>7}{'expR':>8}"
              f"{'sd(R)':>7}{'R/mo':>7}{'Kelly f':>9}{'mo@Kelly':>10}"
              f"{'DD@Kelly':>10}{'strk':>5}")
        best = {}
        for rr in RR_FULL:
            if rr not in books or len(books[rr]) < 50:
                continue
            t = books[rr]
            wr, tpm, e, mx, sd = stats(t)
            wl = wr / (1 - wr) if wr < 1 else np.inf
            kelly = max(0.0, e / rr)           # growth-optimal risk fraction
            mo_k, dd_k, _ = walk(t, min(kelly, 0.5))
            print(f"{rr:>6.2f}{len(t):>6}{wr:>7.1%}{wl:>11.2f}{tpm:>7.1f}{e:>+8.3f}"
                  f"{sd:>7.2f}{e*tpm:>+7.2f}{kelly:>9.1%}{mo_k:>+10.2%}"
                  f"{dd_k:>10.1%}{mx:>5}")
            best[rr] = (e * tpm, tpm, e)

        print("\nQ2: the frontier. monthly compound return and max drawdown vs risk/trade")
        print(f"{'rr':>6}{'risk':>7}" + "".join(f"{x:>12}" for x in
              ["mo return", "max DD", "return/DD", "worst streak cost"]))
        for rr in [0.5, 1.0, 2.0]:
            if rr not in books: continue
            t = books[rr]
            _, _, _, mx, _ = stats(t)
            for f in [0.005, 0.01, 0.02, 0.03, 0.05, 0.08, 0.12]:
                mo, dd, eq = walk(t, f)
                if eq <= 0:
                    print(f"{rr:>6.2f}{f:>7.1%}{'BUST':>12}"); continue
                print(f"{rr:>6.2f}{f:>7.1%}{mo:>12.2%}{dd:>12.1%}"
                      f"{(mo/abs(dd) if dd else np.nan):>12.2f}"
                      f"{-(1-(1-f)**mx):>12.1%}")
            print()

        print("what risk is needed for a 10% month, and what it costs:")
        for rr in [0.5, 1.0, 2.0]:
            if rr not in books: continue
            t = books[rr]
            lo, hi = 0.0005, 0.60
            got = None
            for _ in range(60):
                mid = (lo + hi) / 2
                mo, dd, eq = walk(t, mid)
                if eq <= 0 or mo < 0.10:
                    lo = mid
                else:
                    hi = mid; got = (mid, mo, dd)
            if got is None:
                mo_max, dd_max, _ = max(((walk(t, f)) for f in np.linspace(0.01, 0.5, 40)),
                                        key=lambda z: z[0])
                print(f"  rr={rr}: UNREACHABLE. best achievable month "
                      f"{mo_max:+.2%} at max DD {dd_max:.0%}")
            else:
                f, mo, dd = got
                print(f"  rr={rr}: needs {f:.1%} risk per trade -> {mo:+.2%}/month "
                      f"at max drawdown {dd:.0%}  "
                      f"({'BREACHES' if abs(dd)>0.06 else 'within'} Breakout's 6% floor)")

if __name__ == "__main__":
    main()
