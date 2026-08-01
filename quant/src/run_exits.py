"""Driver: compare divergence-driven exit and stop management against a fixed 2R."""
import os
import sys
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import data as D          # noqa: E402
import exits as X         # noqa: E402
import mcb as MCB         # noqa: E402
import run_mtf as RM      # noqa: E402

REP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reports")
MODES = {"BASE": 0, "TIGHTEN": 1, "REDDOT": 2, "BOTH": 3,
         "SEQ": 4, "SEQ_TIGHT": 5}


def ltf_events(symbol, ltf):
    """Same-direction divergence confirmations with their pivot levels, and
    adverse trigger-wave crosses, per side, timestamped at bar close."""
    bars, _ = D.load(symbol, ltf, "DESIGN", pad_bars=300)
    f = MCB.build(bars)
    step = pd.Timedelta(ltf)
    dt = pd.to_datetime(bars["dt"].values, utc=True) + step
    out = {}
    for side in (1, -1):
        if side > 0:
            dv = (f["wt_div_bull"] | f["mfi_div_bull"]).fillna(False).values
            lvl = f["div_bull_level"].values
            dot = f["wt_cross_dn_ob"].fillna(False).values     # true red dot: cross in OB
        else:
            dv = (f["wt_div_bear"] | f["mfi_div_bear"]).fillna(False).values
            lvl = f["div_bear_level"].values
            dot = f["wt_cross_up_os"].fillna(False).values
        good = dv & np.isfinite(lvl)
        out[side] = {"div_dt": dt[good], "div_lvl": lvl[good],
                     "dot_dt": dt[dot]}
    return out


def main(tf="4h", ltfs=("1min", "5min", "15min", "30min", "1h"), buf=0.05):
    rows = []
    for ltf in ltfs:
        per = {k: [] for k in MODES}
        for sym in RM.CORE:
            try:
                sig, m1 = RM.htf_signals(sym, tf)
                ev = ltf_events(sym, ltf)
            except Exception as e:                       # noqa: BLE001
                print(f"  {sym} {ltf}: {e}")
                continue
            if not len(sig):
                continue
            for name, code in MODES.items():
                parts = []
                for side in (1, -1):
                    ss = sig[sig.side == side]
                    if not len(ss):
                        continue
                    e = ev[side]
                    d = X.run(ss, m1, e["div_dt"], e["div_lvl"], e["dot_dt"],
                              mode=code, buf_frac=buf)
                    if len(d):
                        parts.append(d)
                if parts:
                    per[name].append(pd.concat(parts))
        if not per["BASE"]:
            continue
        print(f"\n=== 4h signal, {ltf} divergence exits "
              f"(stop buffer {100*buf:.0f}% of original risk) ===")
        print(f"{'variant':<9}{'n':>6}{'expR':>9}{'avg win':>9}{'avg loss':>10}"
              f"{'%tgt':>7}{'%stop':>7}{'%sig':>7}{'%moved':>8}"
              f"{'mo R':>8}{'maxDD':>8}{'%/mo':>8}{'R:R':>7}")
        for name in MODES:
            if not per[name]:
                continue
            d = pd.concat(per[name]).sort_values("close_dt").reset_index(drop=True)
            months = ((pd.Timestamp(d.close_dt.max())
                       - pd.Timestamp(d.close_dt.min())).days / 30.44)
            s = X.summarise(d, months, name)
            if not s:
                continue
            s["ltf"] = ltf
            s["buf"] = buf
            rows.append(s)
            s["rr"] = s['avg_win'] / abs(s['avg_loss']) if s['avg_loss'] else float('nan')
            print(f"{name:<9}{s['n']:>6}{s['expR']:>9.4f}{s['avg_win']:>9.3f}"
                  f"{s['avg_loss']:>10.3f}{100*s['pct_target']:>6.0f}%"
                  f"{100*s['pct_stop']:>6.0f}%{100*s['pct_signal_exit']:>6.0f}%"
                  f"{100*s['pct_stop_moved']:>7.0f}%{s['moR']:>8.2f}"
                  f"{s['maxDD_R']:>8.1f}{100*s['monthly_ret']:>7.2f}%{s['rr']:>7.2f}")
    if rows:
        out = pd.DataFrame(rows)
        out.to_csv(os.path.join(REP, "exits.csv"), index=False)
        b = out.sort_values("monthly_ret", ascending=False).head(6)
        print("\n=== ranked by monthly return ===")
        for _, r in b.iterrows():
            print(f"  {r.ltf:>6} {r.variant:<9} expR {r.expR:+.4f}  "
                  f"avg loss {r.avg_loss:+.3f}  {100*r.monthly_ret:+.2f}%/mo")
    return rows


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--buf", type=float, default=0.05)
    a = p.parse_args()
    main(buf=a.buf)
