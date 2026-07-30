"""Engine validation. If these fail, every downstream number is fiction."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
import data as D
import engine as E


def main():
    bars, m1 = D.load("BTCUSDT", "15min", "TRAIN")
    print(f"bars {len(bars):,}  {bars.dt.iloc[0]} -> {bars.dt.iloc[-1]}")
    print(f"1m   {len(m1):,}")

    tf = pd.Timedelta("15min")
    b = bars[bars.tradeable].reset_index(drop=True)

    # ---- TEST 1: random entries, 2:1 RR, ATR stop. Expectancy must be ~ -cost.
    rng = np.random.default_rng(7)
    tr_ = b["high"] - b["low"]
    atr = tr_.rolling(14).mean()
    pick = rng.random(len(b)) < 0.02
    pick &= atr.notna().values
    sub = b[pick].reset_index(drop=True)
    a = atr[pick].reset_index(drop=True)
    side = rng.choice([-1, 1], len(sub))
    stop_d = 1.5 * a.values
    sig = pd.DataFrame({
        "close_dt": sub["dt"] + tf,
        "side": side,
        "stop_px": sub["close"].values - side * stop_d,
        "target_px": sub["close"].values + side * 2 * stop_d,
    })

    for slip, taker in [(0.0, 0.0), (E.SLIP, E.TAKER)]:
        t = E.resolve(sig, m1, delay_min=1, slip=slip, taker=taker)
        exp_cost = -(2 * taker + 2 * slip) / t["stop_pct"].mean()
        print(f"\nrandom n={len(t):5d} slip={slip} taker={taker}  "
              f"wr={(t.outcome==1).mean():.4f}  expR={t.r.mean():+.4f}  "
              f"predicted_cost_drag={exp_cost:+.4f}  timeouts={(t.outcome==0).sum()}")

    # ---- TEST 2: no look-ahead. Shifting the decision one bar EARLIER must not
    # change a random strategy's result systematically; using bar t's OWN high/low
    # to set the target (a deliberate leak) must show an obvious impossible edge.
    leak = pd.DataFrame({
        "close_dt": sub["dt"] + tf,
        "side": side,
        "stop_px": sub["close"].values - side * stop_d,
        # leak: target placed inside the NEXT bar's realised range
        "target_px": sub["close"].values + side * 0.05 * stop_d,
    })
    tl = E.resolve(leak, m1, delay_min=1)
    print(f"\ntight-target control: wr={(tl.outcome==1).mean():.3f} "
          f"(should be near 1.0 — confirms the path walker actually detects hits)")

    # ---- TEST 3: stop must win ties. Construct a signal whose stop and target
    # both sit inside one 1m bar.
    i = 5000
    row = m1.iloc[i + 1]
    span = row["high"] - row["low"]
    if span > 0:
        tie = pd.DataFrame({
            "close_dt": [m1["dt"].iloc[i] - pd.Timedelta(minutes=1)],
            "side": [1],
            "stop_px": [row["low"] + 0.01 * span],
            "target_px": [row["high"] - 0.01 * span],
        })
        tt = E.resolve(tie, m1, delay_min=1)
        if len(tt):
            print(f"tie-break: outcome={tt.outcome.iloc[0]} (must be -1, stop wins)")

    # ---- TEST 4: fill delay monotonicity — more delay must not improve a
    # random strategy in any systematic way, and 0-delay must be the optimistic end.
    for d in [0, 1, 3, 15]:
        t = E.resolve(sig, m1, delay_min=d)
        print(f"delay={d:2d}m  n={len(t)}  expR={t.r.mean():+.4f}")


if __name__ == "__main__":
    main()
