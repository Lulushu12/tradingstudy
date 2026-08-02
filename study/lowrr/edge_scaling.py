"""Why cutting R:R throws edge away: the winrate lift is roughly constant in
percentage points, but what you get paid for it is proportional to (1+rr).

For each rule, at each rr:
    lift   = conditional winrate - UNCONDITIONAL winrate at the same rr
             (the unconditional number already contains the 1/(1+rr) barrier odds,
              so the lift is the part the signal is actually responsible for)
    grossR = (1+rr) * lift          [exact identity, since EV = W(1+rr) - 1]
    netR   = grossR - cost_R

If lift were proportional to rr/(1+rr) then grossR would be flat and the choice of
rr would not matter. If lift is flat, grossR scales with (1+rr) and low R:R is
simply a worse way to harvest the same signal.
"""
import sys, os, pickle, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd
from lowrr import core

HERE = os.path.dirname(os.path.abspath(__file__))
RR = [0.25, 0.33, 0.5, 0.75, 1.0, 1.5, 2.0]

def unconditional():
    tr = pd.read_parquet(os.path.join(HERE, "barrier_4H.parquet"))
    out = {}
    for rr in RR:
        s = tr[tr["rr"] == rr]
        out[rr] = (s["res"] == 1).sum() / (s["res"] != 0).sum()
    return out

def main():
    unc = unconditional()
    with open(os.path.join(HERE, "trades_store.pkl"), "rb") as f:
        store = pickle.load(f)
    rules = sorted({k[0] for k in store})
    am = 1.5
    print("4H, stop = 1.5 x ATR14, non-overlapping trades, 5m path, Breakout costs\n")
    print(f"{'rule':<19}{'rr':>5}{'WR':>7}{'uncond':>8}{'lift':>7}{'grossR':>8}"
          f"{'costR':>7}{'netR':>7}{'t/mo':>6}{'R/mo':>7}")
    for rule in rules:
        for rr in RR:
            tr = store.get((rule, am, rr))
            if tr is None or len(tr) < 30:
                continue
            res = (tr["res"] != 0).sum()
            wr = (tr["res"] == 1).sum() / res
            lift = wr - unc[rr]
            gross = tr["gross_R"].mean()
            span = (tr["entry_time"].iloc[-1] - tr["entry_time"].iloc[0]) / (86400 * 30.44)
            tpm = len(tr) / span
            print(f"{rule:<19}{rr:>5.2f}{wr:>7.1%}{unc[rr]:>8.1%}{lift:>+7.1%}"
                  f"{gross:>+8.3f}{tr['cost_R'].mean():>7.3f}{tr['net_R'].mean():>+7.3f}"
                  f"{tpm:>6.1f}{tr['net_R'].mean()*tpm:>+7.2f}")
        print()

if __name__ == "__main__":
    main()
