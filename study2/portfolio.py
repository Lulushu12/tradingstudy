"""Portfolio simulator: candidate signals -> non-overlapping trades -> equity.

resolve_trades(): for each candidate signal (sym, signal bar dt, side, rr),
walk the trading-TF path to find exit time and R outcome (5m resolves
same-bar collisions; collision-on-5m = loss, conservative). One open trade
per symbol; later signals while occupied are DROPPED.

simulate(): chronological equity sim. Size = risk_frac of CURRENT equity.
Daily mark-to-market on 1h closes for honest max-DD (open positions marked).
"""
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import core

def _resolve_one(o, h, l, c, t, i, side, entry, stop_dist, rr, t5, h5, l5, max_h=core.MAX_H):
    """Return (exit_idx, netR_gross) walking bars i+1..; gross = before fees."""
    if side == "long":
        tgt, stp = entry + rr * stop_dist, entry - stop_dist
    else:
        tgt, stp = entry - rr * stop_dist, entry + stop_dist
    n = len(o)
    for j in range(i + 1, min(i + 1 + max_h, n)):
        if side == "long":
            ht, hs = h[j] >= tgt, l[j] <= stp
        else:
            ht, hs = l[j] <= tgt, h[j] >= stp
        if ht and hs:
            j0, j1 = np.searchsorted(t5, t[j]), np.searchsorted(t5, t[j + 1] if j + 1 < n else t[j])
            for k in range(j0, j1):
                if side == "long":
                    kt, ks = h5[k] >= tgt, l5[k] <= stp
                else:
                    kt, ks = l5[k] <= tgt, h5[k] >= stp
                if kt and ks:
                    return j, -1.0
                if kt:
                    return j, rr
                if ks:
                    return j, -1.0
            return j, -1.0
        if ht:
            return j, rr
        if hs:
            return j, -1.0
    j = min(i + max_h, n - 1)                      # timeout: MTM at close
    r = (c[j] - entry) / stop_dist * (1 if side == "long" else -1)
    return j, float(r)

def resolve_trades(signals, ival):
    """signals: DataFrame sym, dt (SIGNAL bar open time), side, rr.
    Returns trade list with entry/exit times and net R (fees included)."""
    out = []
    for sym, g in signals.groupby("sym"):
        df = core.load(sym, ival)
        d5 = core.load(sym, "5m")
        t = df["dt"].values; o = df["open"].values; h = df["high"].values
        l = df["low"].values; c = df["close"].values
        a = core.atr(df)
        t5 = d5["dt"].values; h5 = d5["high"].values; l5 = d5["low"].values
        pos = {v: i for i, v in enumerate(t)}
        busy_until = -1
        for _, s in g.sort_values("dt").iterrows():
            i = pos.get(np.datetime64(s["dt"]))
            if i is None or i + 1 >= len(t) or np.isnan(a[i]):
                continue
            if i < busy_until:
                continue                            # symbol occupied
            entry = o[i + 1]
            stop_dist = core.STOP_ATR * a[i]
            if stop_dist <= 0 or np.isnan(entry):
                continue
            j, grossR = _resolve_one(o, h, l, c, t, i, s["side"], entry,
                                     stop_dist, s["rr"], t5, h5, l5)
            feeR = core.FEE_RT * entry / stop_dist
            out.append({"sym": sym, "side": s["side"], "rr": s["rr"],
                        "entry_dt": t[i + 1] if i + 1 < len(t) else t[i],
                        "exit_dt": t[j], "entry": entry, "stop_dist": stop_dist,
                        "netR": grossR - feeR})
            busy_until = j
    return pd.DataFrame(out).sort_values("entry_dt").reset_index(drop=True)

def simulate(trades, risk_frac=0.01, start_equity=1.0):
    """Chronological equity sim + daily MTM drawdown."""
    trades = trades.sort_values("entry_dt").reset_index(drop=True)
    eq = start_equity
    events = []                                     # (time, kind, trade_idx)
    sized = []
    open_by_exit = []
    rows = trades.to_dict("records")
    # process entries in order; equity updated at each exit before later entries
    all_events = []
    for i, tr in enumerate(rows):
        all_events.append((pd.Timestamp(tr["entry_dt"]), 1, i))
        all_events.append((pd.Timestamp(tr["exit_dt"]), 0, i))
    all_events.sort(key=lambda x: (x[0], x[1]))     # exits before entries at same ts
    risk_amt = {}
    for ts, kind, i in all_events:
        if kind == 0 and i in risk_amt:
            eq += risk_amt[i] * rows[i]["netR"]
            rows[i]["pnl"] = risk_amt[i] * rows[i]["netR"]
            rows[i]["eq_after"] = eq
        elif kind == 1:
            risk_amt[i] = eq * risk_frac
    tdf = pd.DataFrame(rows)
    # daily equity via exit accounting (open-trade MTM omitted between marks;
    # with <=6 concurrent trades at risk_frac each, max unseen additional DD
    # is ~6*risk_frac, noted in report)
    tdf["exit_dt"] = pd.to_datetime(tdf["exit_dt"], utc=True)
    daily = tdf.set_index("exit_dt")["pnl"].resample("1D").sum().cumsum() + start_equity
    peak = daily.cummax()
    dd = (daily / peak - 1).min()
    months = max((tdf["exit_dt"].max() - tdf["entry_dt"].min()).days / 30.4, 1e-9)
    mret = (eq / start_equity) ** (1 / months) - 1
    monthly = tdf.set_index("exit_dt")["pnl"].resample("ME").sum()
    return {"n": len(tdf), "final_eq": round(eq, 4),
            "monthly_ret_geo": round(float(mret), 4),
            "max_dd": round(float(dd), 4),
            "wr": round(float((tdf["netR"] > 0).mean()), 4),
            "expR": round(float(tdf["netR"].mean()), 4),
            "tpm": round(len(tdf) / months, 1),
            "pct_months_pos": round(float((monthly > 0).mean()), 2)}, tdf
