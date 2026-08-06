"""Trade resolution per FROZEN_SPEC section 5/6.

Entry: market at open of signal_i + 1.
Stop (long): min(close - atr14) over bars t-5..t-1 (signal bar excluded).
Stop (short): max(close + atr14) over bars t-5..t-1.
Skip if stop distance < 0.6% of entry (or stop on wrong side of entry).
Targets: 1R and 2R fixed. Resolved on the 15m path; if stop and target are
both touched inside the same bar the trade counts as a LOSS (conservative)
and is flagged ambiguous. Fees 0.08% of notional round trip, expressed in R.
"""
import numpy as np
import pandas as pd

FEE_RT = 0.0008
MAX_HOLD = 96 * 30  # 30 days of 15m bars; unresolved -> excluded


def resolve_trades(df: pd.DataFrame, signals):
    o = df["open"].to_numpy(float)
    h = df["high"].to_numpy(float)
    l = df["low"].to_numpy(float)
    c = df["close"].to_numpy(float)
    atr = df["atr14"].to_numpy(float)
    n = len(df)
    rows = []
    for s in signals:
        t = s.signal_i
        if t + 1 >= n or t - 5 < 0:
            rows.append(dict(signal_i=t, dt=df["dt"].iloc[min(t, n - 1)],
                             system=s.system, direction=s.direction,
                             entry=np.nan, stop=np.nan, dist=np.nan, skip=True,
                             fee_r=np.nan,
                             **{f"{k}{rr}": (False if k == "ambig" else np.nan)
                                for rr in (1, 2)
                                for k in ("win", "netR", "ambig", "bars")}))
            continue
        entry = o[t + 1]
        if s.direction > 0:
            stop = (c[t - 5 : t] - atr[t - 5 : t]).min()
            dist = entry - stop
        else:
            stop = (c[t - 5 : t] + atr[t - 5 : t]).max()
            dist = stop - entry
        skip = not (dist >= 0.006 * entry)
        row = dict(signal_i=t, dt=df["dt"].iloc[t], system=s.system,
                   direction=s.direction, entry=entry, stop=stop, dist=dist,
                   skip=skip, fee_r=np.nan)
        for rr in (1, 2):
            row[f"win{rr}"] = np.nan
            row[f"netR{rr}"] = np.nan
            row[f"ambig{rr}"] = False
            row[f"bars{rr}"] = np.nan
        if not skip:
            fee_r = FEE_RT * entry / dist
            row["fee_r"] = fee_r
            for rr in (1, 2):
                tp = entry + s.direction * rr * dist
                won = amb = None
                end = min(n, t + 1 + MAX_HOLD)
                for i in range(t + 1, end):
                    hit_sl = l[i] <= stop if s.direction > 0 else h[i] >= stop
                    hit_tp = h[i] >= tp if s.direction > 0 else l[i] <= tp
                    if hit_sl and hit_tp:
                        won, amb = False, True
                    elif hit_sl:
                        won, amb = False, False
                    elif hit_tp:
                        won, amb = True, False
                    if won is not None:
                        row[f"win{rr}"] = float(won)
                        row[f"netR{rr}"] = (rr if won else -1.0) - fee_r
                        row[f"ambig{rr}"] = amb
                        row[f"bars{rr}"] = i - t
                        break
        rows.append(row)
    return pd.DataFrame(rows)
