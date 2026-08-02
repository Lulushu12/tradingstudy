"""Frequency without dropping timeframe: run the same rule on many instruments.

This is also the strongest falsification test available here. The BTC rules were
selected by scanning BTC, so their BTC numbers are contaminated by construction.
Eleven other perps were never scanned. If the low R:R short edge is real it should
show up on them too. If it is BTC-only, it was noise wearing a rule.

Costs: Breakout commission 0.035%/side plus the 5 bps overnight fee, and a larger
slippage assumption on alts than on BTC/ETH because they are thinner.

Resolution: each symbol's own 15m path. The BTC-only 5m-vs-15m comparison at the
bottom quantifies how much the coarser path flatters or penalises the result.
"""
import sys, os, glob, warnings, pickle
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd
import indicators as ind
from lowrr import core
from lowrr.finalists_lowrr import nonoverlap, block_bootstrap_ci
from lowrr.scan import CUT

HERE = os.path.dirname(os.path.abspath(__file__))
BN = os.path.join(HERE, "bn")
MAJORS = {"BTCUSDT", "ETHUSDT"}
SLIP_MAJOR = 0.0001      # per side
SLIP_ALT = 0.0003        # per side

RULES = {
    "S_bb_break_dn":  lambda d: ((d["close"] < d["bb_lo"]), -1),
    "L_bb_break_up":  lambda d: ((d["close"] > d["bb_up"]), +1),
    "S_volspike18_dn": lambda d: ((d["close"] < d["ema200"]) & (d["vol_ratio"] > 1.8)
                                  & (d["close"] < d["open"]), -1),
    "L_volspike18_up": lambda d: ((d["close"] > d["ema200"]) & (d["vol_ratio"] > 1.8)
                                  & (d["close"] > d["open"]), +1),
}
RR_GRID = [0.25, 0.5, 0.75, 1.0, 2.0]

def symbols():
    out = []
    for p in sorted(glob.glob(os.path.join(BN, "*_4h.parquet"))):
        sym = os.path.basename(p).replace("_4h.parquet", "")
        if os.path.exists(os.path.join(BN, f"{sym}_15m.parquet")):
            out.append(sym)
    return out

def load_path_file(p):
    d = pd.read_parquet(p).sort_values("time").reset_index(drop=True)
    return (d["time"].values.astype(np.int64), d["open"].values, d["high"].values,
            d["low"].values, d["close"].values)

def build(sym, am=1.5, start="2021-05-24"):
    df = ind.enrich(pd.read_parquet(os.path.join(BN, f"{sym}_4h.parquet")))
    df = df[df["dt"] >= pd.Timestamp(start, tz="UTC")].reset_index(drop=True)
    path = load_path_file(os.path.join(BN, f"{sym}_15m.parquet"))
    slip = SLIP_MAJOR if sym in MAJORS else SLIP_ALT
    out = {}
    for name, fn in RULES.items():
        mask, side = fn(df)
        mask = mask.fillna(False).values
        idx = np.where(mask)[0]
        idx = idx[idx < len(df) - 1]
        if len(idx) < 40:
            continue
        tr = core.trades_for_signals(df, idx, np.full(len(idx), side), am,
                                     RR_GRID, path, max_hold_days=50)
        if len(tr) == 0:
            continue
        tr["cost_R"] = core.cost_R(tr["stop_frac"].values, tr["nights"].values,
                                   slip_rt=2 * slip)
        tr["net_R"] = tr["gross_R"] - tr["cost_R"]
        tr["sym"] = sym
        for rr in RR_GRID:
            out[(name, rr)] = nonoverlap(tr[tr["rr"] == rr].copy())
    return out

def per_asset_table(store, rule, rr):
    print(f"\n===== {rule}  rr={rr}  per asset (non-overlapping, Breakout costs) =====")
    print(f"{'sym':<10}{'n':>5}{'t/mo':>6}{'WR':>7}{'be':>7}{'expR':>8}{'trE':>8}"
          f"{'teE':>8}{'R/mo':>7}{'hold':>6}")
    rows = []
    for sym, d in store.items():
        tr = d.get((rule, rr))
        if tr is None or len(tr) < 30:
            continue
        res = (tr["res"] != 0).sum()
        wr = (tr["res"] == 1).sum() / res
        be = core.breakeven_wr(rr, tr["stop_frac"].mean(), tr["nights"].mean())
        span = (tr["entry_time"].iloc[-1] - tr["entry_time"].iloc[0]) / (86400 * 30.44)
        trn = tr[tr["dt"] < CUT]; tst = tr[tr["dt"] >= CUT]
        r = dict(sym=sym, n=len(tr), tpm=len(tr) / span, wr=wr, be=be,
                 expR=tr["net_R"].mean(),
                 e_tr=trn["net_R"].mean() if len(trn) else np.nan,
                 e_te=tst["net_R"].mean() if len(tst) else np.nan,
                 Rmo=tr["net_R"].mean() * len(tr) / span, hold=tr["hold_h"].mean())
        rows.append(r)
        print(f"{sym:<10}{r['n']:>5}{r['tpm']:>6.1f}{wr:>7.1%}{be:>7.1%}"
              f"{r['expR']:>+8.3f}{r['e_tr']:>+8.3f}{r['e_te']:>+8.3f}"
              f"{r['Rmo']:>+7.2f}{r['hold']:>6.0f}")
    t = pd.DataFrame(rows)
    if len(t):
        pos = (t["expR"] > 0).sum()
        print(f"{'POOLED':<10}{t['n'].sum():>5}{t['tpm'].sum():>6.1f}"
              f"{'':>7}{'':>7}{np.average(t['expR'], weights=t['n']):>+8.3f}"
              f"{'':>8}{'':>8}{t['Rmo'].sum():>+7.2f}")
        print(f"  assets with positive net expectancy: {pos}/{len(t)}   "
              f"non-BTC positive: {(t[t.sym!='BTCUSDT']['expR']>0).sum()}/{len(t)-1}")
    return t

def portfolio(store, rule, rr, risk, max_conc=4, one_per_sym=True):
    frames = [d[(rule, rr)] for d in store.values() if (rule, rr) in d]
    if not frames:
        return None
    tr = pd.concat(frames, ignore_index=True).sort_values("entry_time").reset_index(drop=True)
    open_pos = []   # (exit_time, sym)
    taken = []
    for r in tr.itertuples():
        open_pos = [p for p in open_pos if p[0] > r.entry_time]
        if len(open_pos) >= max_conc:
            continue
        if one_per_sym and any(p[1] == r.sym for p in open_pos):
            continue
        open_pos.append((r.exit_time, r.sym))
        taken.append(r)
    u = pd.DataFrame(taken).sort_values("exit_time").reset_index(drop=True)
    eq = 1.0; peak = 1.0; mdd = 0.0
    curve = []
    for r in u["net_R"].values:
        eq += risk * eq * r
        peak = max(peak, eq); mdd = min(mdd, (eq - peak) / peak)
        curve.append(eq)
    u["equity"] = curve
    yrs = (u["exit_time"].iloc[-1] - u["exit_time"].iloc[0]) / (365.25 * 86400)
    daily = u.groupby(u["exit_time"] // 86400)["net_R"].sum() * risk
    streak = mx = 0
    for w in (u["net_R"] > 0).values:
        if w: streak = 0
        else: streak += 1; mx = max(mx, streak)
    return dict(n=len(u), tpm=len(u) / (yrs * 12), wr=(u["res"] == 1).mean(),
                expR=u["net_R"].mean(), total=eq - 1,
                cagr=eq ** (1 / yrs) - 1, per_mo=eq ** (1 / (yrs * 12)) - 1,
                maxdd=mdd, worst_day=daily.min(), streak=mx,
                R_per_month=u["net_R"].sum() / (yrs * 12)), u

def main():
    syms = symbols()
    print(f"symbols with 4h+15m: {syms}\n")
    store = {}
    for s in syms:
        store[s] = build(s)
        print(f"  built {s}", flush=True)
    with open(os.path.join(HERE, "multiasset_store.pkl"), "wb") as f:
        pickle.dump(store, f)

    for rule in ["S_bb_break_dn", "L_bb_break_up", "S_volspike18_dn", "L_volspike18_up"]:
        for rr in [0.25, 0.5, 1.0, 2.0]:
            per_asset_table(store, rule, rr)

    print("\n\n===== portfolio (max 4 concurrent, 1 per symbol) =====")
    print(f"{'rule':<18}{'rr':>5}{'risk':>7}{'n':>6}{'t/mo':>6}{'WR':>7}{'expR':>8}"
          f"{'R/mo':>7}{'per-mo':>8}{'CAGR':>8}{'maxDD':>8}{'worstDay':>9}{'strk':>5}")
    book = {}
    for rule in ["S_bb_break_dn", "L_bb_break_up", "S_volspike18_dn", "L_volspike18_up"]:
        for rr in [0.25, 0.5, 1.0, 2.0]:
            for risk in [0.0025, 0.005]:
                out = portfolio(store, rule, rr, risk)
                if out is None: continue
                m, u = out
                if risk == 0.0025:
                    book[f"{rule} rr{rr}"] = u
                print(f"{rule:<18}{rr:>5.2f}{risk:>7.2%}{m['n']:>6}{m['tpm']:>6.1f}"
                      f"{m['wr']:>7.1%}{m['expR']:>+8.3f}{m['R_per_month']:>+7.2f}"
                      f"{m['per_mo']:>+8.2%}{m['cagr']:>+8.1%}{m['maxdd']:>8.1%}"
                      f"{m['worst_day']:>+9.2%}{m['streak']:>5}")
    with open(os.path.join(HERE, "portfolio_trades.pkl"), "wb") as f:
        pickle.dump(book, f)

if __name__ == "__main__":
    main()
