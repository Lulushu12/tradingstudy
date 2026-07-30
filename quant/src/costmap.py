"""How much of each unit of risk do costs eat, per timeframe and stop width?

This decides where an edge is even POSSIBLE, before searching for one.
Also measures the unconditional 2:1 and 1:1 hit rates so every later claim of
'edge' is measured against the correct null, not against 33.3%.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
import data as D
import engine as E

rng = np.random.default_rng(11)


def run(symbol="BTCUSDT"):
    out = []
    for tf, hold_h in [("5min", 24), ("15min", 48), ("30min", 96),
                       ("1h", 168), ("4h", 480), ("1D", 1440)]:
        bars, m1 = D.load(symbol, tf, "TRAIN")
        b = bars[bars.tradeable].reset_index(drop=True)
        step = pd.Timedelta(tf)
        tr_ = pd.concat([b.high - b.low,
                         (b.high - b.close.shift()).abs(),
                         (b.low - b.close.shift()).abs()], axis=1).max(axis=1)
        atr = tr_.ewm(alpha=1 / 14, adjust=False).mean()

        for mult in [1.0, 2.0, 4.0]:
            n_target = 4000
            p = min(1.0, n_target / len(b))
            pick = (rng.random(len(b)) < p) & atr.notna().values & (np.arange(len(b)) > 50)
            sub = b[pick].reset_index(drop=True)
            a = atr[pick].reset_index(drop=True).values
            side = rng.choice([-1, 1], len(sub))
            sd = mult * a
            for rr in [1.0, 2.0]:
                sig = pd.DataFrame({
                    "close_dt": sub["dt"] + step,
                    "side": side,
                    "stop_px": sub["close"].values - side * sd,
                    "target_px": sub["close"].values + side * rr * sd,
                })
                gross = E.resolve(sig, m1, delay_min=1, slip=0.0, taker=0.0,
                                  max_hold_min=hold_h * 60)
                net = E.resolve(sig, m1, delay_min=1, max_hold_min=hold_h * 60)
                if len(net) < 50:
                    continue
                stop_pct = net["stop_pct"].mean()
                drag = gross["r"].mean() - net["r"].mean()
                # breakeven WR at this RR after costs
                be = (1 + drag) / (1 + rr)
                out.append({
                    "tf": tf, "atr_mult": mult, "rr": rr, "n": len(net),
                    "stop_pct": 100 * stop_pct,
                    "raw_wr": float((gross.outcome == 1).mean()),
                    "be_wr": be,
                    "edge_needed_pp": 100 * (be - (gross.outcome == 1).mean()),
                    "drag_R": drag,
                    "timeout_pct": 100 * float((net.outcome == 0).mean()),
                    "hold_h": net["hold_min"].mean() / 60,
                })
                print(f"{tf:>6} {mult:>4.1f}xATR rr={rr:.0f}  stop={100*stop_pct:5.2f}%  "
                      f"raw_wr={float((gross.outcome==1).mean()):.3f}  drag={drag:.3f}R  "
                      f"be_wr={be:.3f}  need +{100*(be-(gross.outcome==1).mean()):4.1f}pp  "
                      f"hold={net['hold_min'].mean()/60:6.1f}h  n={len(net)}")
    df = pd.DataFrame(out)
    df.to_csv(os.path.join(os.path.dirname(__file__), "..", "reports", "costmap.csv"), index=False)
    return df


if __name__ == "__main__":
    run()
