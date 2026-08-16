"""One-shot holdout validation of the pre-registered rule candidates.

Every rule below was fully specified on TRAIN data (pre-2025) by the family
deep-dives. This script is the single look at the 2025+ holdout for each.
Trade lists saved to data/rtrades_{name}.parquet for portfolio combination.
"""
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import core, portfolio

RULES = [
    # name, ival, side, rr, condition(M) -> bool mask
    ("tlsr_long",   "4h", "long",  2.0, lambda M: M["M_tlsr_acct_z"] <= -1.5),
    ("glsr_short",  "4h", "short", 2.0, lambda M: M["M_glsr_z"] >= 1.75),
    ("btclead_alt", "1h", "long",  2.0, lambda M: (M["sym"] != "BTCUSDT") &
                                                  (M["X_btc_lead1"] >= 0.015)),
    ("whale_long",  "4h", "long",  2.0, lambda M: (M["O_whale"] == 1) &
                                                  (M["P_close_pos"] > 0.5)),
    ("rslag_long",  "4h", "long",  2.0, lambda M: M["X_rs_btc_z"] <= -2.0),
    ("squeeze_long","4h", "long",  2.0, lambda M: (M["F_rate"] < -0.0002) &
                                                  (M["T_ret_24h"] > 0.02)),
]

def stats(t, lo, hi):
    t = t[(t["entry_dt"] >= np.datetime64(lo)) & (t["entry_dt"] < np.datetime64(hi))]
    if len(t) < 5:
        return {"n": len(t)}
    months = max((t["entry_dt"].max() - t["entry_dt"].min()) / np.timedelta64(1, "D") / 30.4, 1e-9)
    return {"n": len(t), "wr": round(float((t["netR"] > 0).mean()), 3),
            "expR": round(float(t["netR"].mean()), 3),
            "tpm": round(len(t) / months, 1),
            "totR": round(float(t["netR"].sum()), 1)}

if __name__ == "__main__":
    for name, ival, side, rr, cond in RULES:
        M = pd.read_parquet(f"{core.DATA}/matrix_{ival}.parquet")
        sig = M[cond(M).fillna(False)][["sym", "dt"]].copy()
        sig["side"] = side; sig["rr"] = rr
        t = portfolio.resolve_trades(sig, ival)
        t.to_parquet(f"{core.DATA}/rtrades_{name}.parquet")
        tr = stats(t, "2020-01-01", "2025-01-01")
        ho = stats(t, "2025-01-01", "2027-01-01")
        print(f"{name:13s} {ival} {side:5s} | TRAIN {tr} | HOLDOUT {ho}", flush=True)
