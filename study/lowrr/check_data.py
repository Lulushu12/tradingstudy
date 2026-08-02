"""Two sanity checks before trusting the multi-asset extension.

1. Feed agreement. The BTC study data came from TradingView exports of Binance
   BTCUSDT.P. The multi-asset data comes from data.binance.vision. If the two
   disagree on overlapping 4H bars, everything downstream is suspect.

2. Path-resolution bias. BTC trades were resolved on the 5m path; the alts only
   have 15m. Resolving the SAME BTC trades both ways shows how much the coarser
   path moves the answer, which is exactly the size of the caveat to attach to
   the multi-asset numbers.
"""
import sys, os, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd
import indicators as ind
from lowrr import core
from lowrr.multiasset import load_path_file, BN
from lowrr.finalists_lowrr import nonoverlap

HERE = os.path.dirname(os.path.abspath(__file__))
RR = [0.25, 0.5, 0.75, 1.0, 2.0]

def feed_check():
    a = pd.read_parquet(os.path.join(core.DATA, "4H.parquet"))[["time", "open", "high", "low", "close"]]
    b = pd.read_parquet(os.path.join(BN, "BTCUSDT_4h.parquet"))[["time", "open", "high", "low", "close"]]
    m = a.merge(b, on="time", suffixes=("_tv", "_bn"))
    print(f"=== feed agreement on {len(m)} overlapping 4H bars ===")
    for c in ["open", "high", "low", "close"]:
        d = (m[f"{c}_tv"] - m[f"{c}_bn"]).abs() / m[f"{c}_bn"]
        print(f"  {c:>6}: max rel diff {d.max():.2e}  mean {d.mean():.2e}  "
              f"bars >1bp off: {(d > 1e-4).sum()}")

def path_check(am=1.5):
    df = ind.enrich(pd.read_parquet(os.path.join(core.DATA, "4H.parquet")))
    df = df[df["dt"] >= pd.Timestamp("2021-05-24", tz="UTC")].reset_index(drop=True)
    mask = (df["close"] < df["bb_lo"]).fillna(False).values
    idx = np.where(mask)[0]; idx = idx[idx < len(df) - 1]
    side = np.full(len(idx), -1)
    p5 = core.load_path("5m")
    p15 = load_path_file(os.path.join(BN, "BTCUSDT_15m.parquet"))
    t5 = core.trades_for_signals(df, idx, side, am, RR, p5, max_hold_days=50)
    t15 = core.trades_for_signals(df, idx, side, am, RR, p15, max_hold_days=50)
    print("\n=== S_bb_break_dn resolved on 5m vs 15m path (same signals) ===")
    print(f"{'rr':>5}{'WR_5m':>8}{'WR_15m':>8}{'d':>7}{'expR_5m':>9}{'expR_15m':>10}{'d':>8}")
    for rr in RR:
        a = nonoverlap(t5[t5["rr"] == rr].copy())
        b = nonoverlap(t15[t15["rr"] == rr].copy())
        wa = (a["res"] == 1).sum() / (a["res"] != 0).sum()
        wb = (b["res"] == 1).sum() / (b["res"] != 0).sum()
        print(f"{rr:>5.2f}{wa:>8.1%}{wb:>8.1%}{wb-wa:>+7.1%}"
              f"{a['net_R'].mean():>+9.3f}{b['net_R'].mean():>+10.3f}"
              f"{b['net_R'].mean()-a['net_R'].mean():>+8.3f}")
    print("  a positive 15m-minus-5m difference means the coarser path FLATTERS the rule")

if __name__ == "__main__":
    feed_check()
    path_check()
