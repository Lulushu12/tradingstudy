"""Driver: HTF signal -> MCB lower-timeframe trigger -> split entry.

Pipeline under test:
  1. Higher timeframe (4h) decides direction, using the one rule that survived
     every test in the study: vol_spike_cont.
  2. Lower timeframe (15m / 5m) decides the moment, using MCB Clone triggers -
     stacked divergence, either-oscillator divergence, or a WaveTrend cross.
  3. Entry is taken three ways and compared on identical signals: all at market,
     all on confirmation, or split half and half.

Also reports the two things that decide whether precision entry is worth
anything: the CONFIRMATION RATE (how often the lower timeframe ever confirms)
and the WINNER MISS RATE (how much of the market-entry edge lives in the
signals that never confirm).
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data as D          # noqa: E402
import features as F      # noqa: E402
import mcb as MCB         # noqa: E402
import splitentry as SE   # noqa: E402

REP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reports")
CORE = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT"]


def htf_signals(symbol, tf="4h"):
    """vol_spike_cont on the higher timeframe."""
    bars, m1 = D.load(symbol, tf, "DESIGN")
    f = F.build(bars, m1, tf)
    f = f[f["tradeable"]].reset_index(drop=True)
    sp = f.trade_intensity > 1.8
    lm = (sp & (f.disp96 > 0) & (f.ret > 0)).fillna(False)
    sm = (sp & (f.disp96 < 0) & (f.ret < 0)).fillna(False)
    step = pd.Timedelta(tf)
    rows = []
    for mask, side in ((lm, 1), (sm, -1)):
        if mask.sum() == 0:
            continue
        rows.append(pd.DataFrame({
            "close_dt": (f.loc[mask.values, "dt"] + step).values,
            "side": side,
            "atr": f.loc[mask.values, "atr"].values,
        }))
    if not rows:
        return pd.DataFrame(), m1
    s = pd.concat(rows).sort_values("close_dt").reset_index(drop=True)
    s["close_dt"] = pd.to_datetime(s["close_dt"], utc=True)
    return s, m1


def ltf_triggers(symbol, ltf, mode):
    """Timestamps at which the MCB trigger became usable on the lower TF."""
    bars, _ = D.load(symbol, ltf, "DESIGN", pad_bars=300)
    f = MCB.build(bars)
    step = pd.Timedelta(ltf)
    out = {}
    for side in (1, -1):
        tr = MCB.trigger(f, side, mode).fillna(False).values
        # a trigger on bar t is only usable at that bar's CLOSE
        out[side] = pd.to_datetime(bars["dt"].values[tr], utc=True) + step
    return out


def main(tf="4h", ltfs=("15min", "5min"),
         modes=("stack", "div", "cross", "cross_ext"), window_min=480):
    allrows = []
    for ltf in ltfs:
        for mode in modes:
            per_sym = []
            conf_rates, miss_stats = [], []
            for sym in CORE:
                try:
                    sig, m1 = htf_signals(sym, tf)
                    if not len(sig):
                        continue
                    trig = ltf_triggers(sym, ltf, mode)
                except Exception as e:                       # noqa: BLE001
                    print(f"  {sym} {ltf} {mode}: {e}")
                    continue
                parts = []
                for side in (1, -1):
                    ss = sig[sig.side == side]
                    if not len(ss):
                        continue
                    df, a, b, c, dep = SE.run(ss, m1, trig[side].values,
                                              window_min=window_min)
                    if not len(df):
                        continue
                    parts.append(df)
                if not parts:
                    continue
                d = pd.concat(parts).sort_values("close_dt")
                per_sym.append(d)
                conf_rates.append(d.confirmed.mean())
                # how much of the market-entry edge sits in unconfirmed signals?
                if d.confirmed.any() and (~d.confirmed).any():
                    miss_stats.append((d.loc[~d.confirmed, "r_market"].mean(),
                                       d.loc[d.confirmed, "r_market"].mean()))
            if not per_sym:
                continue
            D_ = pd.concat(per_sym).sort_values("close_dt").reset_index(drop=True)
            months = ((pd.Timestamp(D_.close_dt.max())
                       - pd.Timestamp(D_.close_dt.min())).days / 30.44)
            a = D_["r_market"]
            b = D_.loc[D_.confirmed, "r_precision"]
            c = 0.5 * D_["r_market"] + 0.5 * D_["r_precision"].fillna(0.0)
            dep = 0.5 + 0.5 * D_["confirmed"].astype(float)
            res = SE.summarise(a, b, c, dep, months)
            res["ltf"] = ltf
            res["mode"] = mode
            res["conf_rate"] = float(np.mean(conf_rates)) if conf_rates else np.nan
            if miss_stats:
                res["r_unconfirmed"] = float(np.mean([m[0] for m in miss_stats]))
                res["r_confirmed"] = float(np.mean([m[1] for m in miss_stats]))
            allrows.append(res)
            print(f"\n--- {tf} signal -> {ltf} {mode} trigger "
                  f"(confirm rate {100*np.mean(conf_rates):.0f}%) ---")
            for _, r in res.iterrows():
                print(f"  {r.variant:<18} n={int(r.n):<5} expR {r.expR:+.4f}  "
                      f"per-unit-risk {r.expR_per_unit_risk:+.4f}  "
                      f"deployed {r.avg_deployed:.2f}  "
                      f"monthly {r.moR:+6.2f}R  maxDD {r.maxDD_R:6.1f}R  "
                      f"{100*r.monthly_ret:+.2f}%/mo")
            if miss_stats:
                ru = np.mean([m[0] for m in miss_stats])
                rc = np.mean([m[1] for m in miss_stats])
                print(f"  market-entry expR on UNCONFIRMED signals {ru:+.4f} "
                      f"vs CONFIRMED {rc:+.4f}"
                      f"  -> {'winners ARE in the skipped set' if ru > rc else 'skipped set is not the winners'}")
    if allrows:
        out = pd.concat(allrows, ignore_index=True)
        out.to_csv(os.path.join(REP, "mtf_split.csv"), index=False)
        print("\n=== best configurations by monthly return ===")
        for _, r in out.sort_values("monthly_ret", ascending=False).head(8).iterrows():
            print(f"  {r.ltf:>6} {r['mode']:<10} {r.variant:<18} "
                  f"expR {r.expR:+.4f}  {100*r.monthly_ret:+.2f}%/mo  "
                  f"confirm {100*r.conf_rate:.0f}%")
    return allrows


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--tf", default="4h")
    p.add_argument("--window", type=int, default=480)
    a = p.parse_args()
    main(tf=a.tf, window_min=a.window)
