"""Three angles the study planned and never ran.

(A) SESSION / TIME OF DAY. 4H bars start at 00,04,08,12,16,20 UTC. Slice the
    unconditional barrier outcomes AND the two surviving rules (S_bb_break_dn,
    S_volspike18_dn) by the signal bar's UTC start hour, day of week, and a
    session split (Asia = 00/04, Europe = 08/12, US = 16/20 -- the only session
    split that lines up exactly with 4H bar boundaries, stated plainly as a
    simplification, not a real FX-style session calendar).

(B) CROSS-SECTIONAL RELATIVE STRENGTH. Each common 4H bar, rank the 12 perps by
    trailing return (lookback 6/12/30/90 bars, using only data up to and
    including that bar's close). Short the weakest N, long the strongest N
    (N=1,2,3), each leg an independent trade to a fixed R:R. Report the paired
    result and the correlation of the paired book's daily P&L with BTC's daily
    return -- the beta-neutrality number is the whole point of this angle.

(C) ENSEMBLE SCORING. Nine causal, unweighted, non-fitted boolean conditions
    (trend, macd, rsi, bollinger, volume, volatility regime, distance from
    ema200, 3-bar run, daily trend alignment), directionally mirrored for
    long/short, summed into a 0-9 score. Test score >= k against each
    condition alone. No weight fitting -- a plain count, as instructed.

Method notes shared by all three:
  - Costs: core.cost_R (Breakout commission + overnight carry), slippage 1bp/
    side majors (BTC, ETH), 3bp/side alts -- exactly as in multiasset.py.
  - Signal read at 4H bar close, entry at next 4H bar open, resolved on the
    symbol's own 15m path. No look-ahead.
  - De-overlap to one position at a time PER SYMBOL (finalists_lowrr.nonoverlap)
    is applied to the already-FILTERED signal stream for each hypothesis (i.e.
    "only trade when hour==X" is de-overlapped as its own stream, not sliced
    out of the de-overlapped unconditional stream -- the latter would be wrong,
    since a different-hour trade can't block a trade you'd never have taken).
  - Expectancy reported with day-clustered bootstrap CI (pooled_test.
    day_cluster_ci, block_days=5). Train = pre-2025-01-01, test = 2025-01-01+.
  - Compute is bounded (4 shared cores). What was cut, stated plainly:
      * Full day-clustered CIs (n_boot=800, cheaper than the 4000 used
        elsewhere in this study) are run on every cell at rr=0.5 (the
        emphasis rung) and on the single best cell per angle across the
        full ladder. Every other ladder cell gets point estimates
        (n, WR, train/test expR) with no bootstrap -- screening, not proof.
      * Angle B ranks all 12 symbols every bar (no symbol cut) across all 4
        requested lookbacks; nothing was cut there because it was cheap
        (bar selection, not extra path resolution).
      * Angle C conditions are exactly 9, unweighted, as instructed. No
        weight fit, no threshold search beyond the plain k in 1..9 sweep.
  - Every hypothesis actually evaluated (n_resolved >= 40, pooled across all
    12 symbols) is counted in a running total, printed at the end.
"""
import sys, os, time, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd
import indicators as ind
from lowrr import core
from lowrr.multiasset import BN, symbols, load_path_file, MAJORS, SLIP_MAJOR, SLIP_ALT, RULES
from lowrr.finalists_lowrr import nonoverlap
from lowrr.pooled_test import day_cluster_ci

HERE = os.path.dirname(os.path.abspath(__file__))
OUTFILE = os.path.join(HERE, "crosssec_out.txt")
CUT = pd.Timestamp("2025-01-01", tz="UTC")
RR_GRID = [0.25, 0.5, 0.75, 1.0, 2.0]
START = "2021-05-24"
SESSION_MAP = {0: "Asia", 4: "Asia", 8: "Europe", 12: "Europe", 16: "US", 20: "US"}
DOWN = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

HYP = {"A": 0, "B": 0, "C": 0}
BEST = {"A": [], "B": [], "C": []}   # collected rows for the final verdict

_LOGF = None
def log(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    if _LOGF is not None:
        _LOGF.write(s + "\n")
        _LOGF.flush()

# ---------------------------------------------------------------- data build
def recost(tr, slip):
    tr = tr.copy()
    c = core.cost_R(tr["stop_frac"].values, tr["nights"].values, slip_rt=2 * slip)
    tr["cost_R"] = c
    tr["net_R"] = tr["gross_R"] - c
    return tr

def build_symbol(sym):
    raw = pd.read_parquet(os.path.join(BN, f"{sym}_4h.parquet")).sort_values("time").reset_index(drop=True)
    df = ind.enrich(raw)
    df = df[df["dt"] >= pd.Timestamp(START, tz="UTC")].reset_index(drop=True)
    # daily trend context: resampled from this symbol's own 4H data (no separate
    # 1D file exists for the 12-symbol set), only usable after the daily bar closes
    d1 = raw.set_index("dt").resample("1D").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
    ).dropna().reset_index()
    d1 = ind.enrich(d1)
    d1 = d1[["dt", "close", "ema200", "rsi14", "atr14"]].copy()
    d1.columns = ["dt", "d_close", "d_ema200", "d_rsi", "d_atr"]
    d1["dt"] = (d1["dt"] + pd.Timedelta(days=1)).astype("datetime64[ns, UTC]")
    df["dt"] = df["dt"].astype("datetime64[ns, UTC]")
    df = pd.merge_asof(df.sort_values("dt"), d1.sort_values("dt"), on="dt", direction="backward")
    path = load_path_file(os.path.join(BN, f"{sym}_15m.parquet"))
    slip = SLIP_MAJOR if sym in MAJORS else SLIP_ALT
    return df, path, slip

def tag_time(tr, df):
    hour = df["dt"].dt.hour.values
    dow = df["dt"].dt.dayofweek.values
    i = tr["sig_i"].values
    tr = tr.copy()
    tr["hour"] = hour[i]
    tr["dow"] = dow[i]
    tr["session"] = tr["hour"].map(SESSION_MAP)
    return tr

def build_uncond(df, path, slip, sym):
    idx = np.arange(len(df) - 1)
    ok = np.isfinite(df["atr14"].values[idx]) & (df["atr14"].values[idx] > 0)
    idx = idx[ok]
    sides = np.concatenate([np.ones(len(idx)), -np.ones(len(idx))])
    idx2 = np.concatenate([idx, idx])
    tr = core.trades_for_signals(df, idx2, sides, 1.5, RR_GRID, path, max_hold_days=50)
    tr = recost(tr, slip)
    tr["sym"] = sym
    tr = tag_time(tr, df)
    return tr

def build_rule(df, path, slip, sym, rulename):
    mask, side = RULES[rulename](df)
    mask = mask.fillna(False).values
    idx = np.where(mask)[0]
    idx = idx[idx < len(df) - 1]
    if len(idx) < 10:
        return None
    tr = core.trades_for_signals(df, idx, np.full(len(idx), side), 1.5, RR_GRID, path, max_hold_days=50)
    if len(tr) == 0:
        return None
    tr = recost(tr, slip)
    tr["sym"] = sym
    tr = tag_time(tr, df)
    return tr

def score_components(df):
    """9 plain, unweighted, non-fitted causal conditions, mirrored for side."""
    close = df["close"]; openp = df["open"]
    up = close > df["ema200"]
    macd_up = (df["macd"] > 0) & (df["macd_hist"] > df["macd_hist"].shift(1))
    macd_dn = (df["macd"] < 0) & (df["macd_hist"] < df["macd_hist"].shift(1))
    rsi = df["rsi14"]
    bb_mid = df["bb_mid"]
    vol = df.get("vol_ratio", pd.Series(np.nan, index=df.index))
    atrq = df["atr_pct"].rolling(500).rank(pct=True)
    ext = (close - df["ema200"]) / df["atr14"]
    upbar = close > openp
    up1 = upbar.shift(1).fillna(False).astype(bool)
    up2 = upbar.shift(2).fillna(False).astype(bool)
    dn1 = (~upbar).shift(1).fillna(False).astype(bool)
    dn2 = (~upbar).shift(2).fillna(False).astype(bool)
    d_up = df["d_close"] > df["d_ema200"]

    long_c = {
        "trend": up, "macd": macd_up, "rsi": rsi > 50, "bollinger": close > bb_mid,
        "volume": vol > 1.0, "vol_regime": atrq < 0.67, "dist_ema200": ext.abs() <= 2.0,
        "run3": upbar & up1 & up2, "daily_trend": d_up,
    }
    short_c = {
        "trend": ~up, "macd": macd_dn, "rsi": rsi < 50, "bollinger": close < bb_mid,
        "volume": vol > 1.0, "vol_regime": atrq < 0.67, "dist_ema200": ext.abs() <= 2.0,
        "run3": (~upbar) & dn1 & dn2, "daily_trend": ~d_up,
    }
    long_c = {k: v.fillna(False).values.astype(bool) for k, v in long_c.items()}
    short_c = {k: v.fillna(False).values.astype(bool) for k, v in short_c.items()}
    score_long = np.sum([v.astype(int) for v in long_c.values()], axis=0)
    score_short = np.sum([v.astype(int) for v in short_c.values()], axis=0)
    return long_c, short_c, score_long, score_short

# ------------------------------------------------------------------ machinery
def nonoverlap_by_sym(tr):
    if len(tr) == 0:
        return tr
    return pd.concat([nonoverlap(g) for _, g in tr.groupby("sym")], ignore_index=True)

def slice_stats(tr_all, rr):
    s = tr_all[tr_all["rr"] == rr]
    if len(s) == 0:
        return None, None
    s = nonoverlap_by_sym(s)
    res = int((s["res"] != 0).sum())
    if res < 40:
        return None, None
    wr = (s["res"] == 1).sum() / res
    trn = s[s["dt"] < CUT]; tst = s[s["dt"] >= CUT]
    res_tr = max(int((trn["res"] != 0).sum()), 1); res_te = max(int((tst["res"] != 0).sum()), 1)
    d = dict(
        n=len(s), res=res, wr=wr, expR=s["net_R"].mean(),
        n_tr=len(trn), e_tr=trn["net_R"].mean() if len(trn) else np.nan,
        wr_tr=(trn["res"] == 1).sum() / res_tr,
        n_te=len(tst), e_te=tst["net_R"].mean() if len(tst) else np.nan,
        wr_te=(tst["res"] == 1).sum() / res_te,
        be=core.breakeven_wr(rr, s["stop_frac"].mean(), s["nights"].mean()),
    )
    return d, s

def with_ci(d, s, n_boot=800, block_days=5):
    lo, hi, p = day_cluster_ci(s, n_boot=n_boot, block_days=block_days)
    d = dict(d)
    d["ci_lo"] = lo; d["ci_hi"] = hi; d["p_le0"] = p
    return d

def row_line(prefix, rr, d, width_prefix=28):
    ci = f"{d.get('ci_lo', np.nan):+.3f} {d.get('ci_hi', np.nan):+.3f}" if "ci_lo" in d else ""
    return (f"{prefix:<{width_prefix}}{rr:>6.2f}{d['n']:>7}{d['wr']:>7.1%}{d['be']:>7.1%}"
            f"{d['expR']:>+8.3f}{d['n_tr']:>6}{d['e_tr']:>+8.3f}{d['n_te']:>6}{d['e_te']:>+8.3f}"
            f"  {ci:>16}")

# =========================================================================
# ANGLE A -- SESSION / TIME OF DAY
# =========================================================================
def angle_A(store):
    log("\n" + "=" * 100)
    log("ANGLE A: SESSION / TIME OF DAY")
    log("=" * 100)
    log("hour = signal bar's UTC start hour (0,4,8,12,16,20); dow = Mon..Sun of signal bar;")
    log("session = Asia(00,04 UTC) / Europe(08,12 UTC) / US(16,20 UTC) by bar-start hour.")
    log("Each bucket is de-overlapped as its OWN stream (filter first, then nonoverlap),")
    log("not sliced out of the already de-overlapped unconditional stream.\n")

    pops = {}
    frames_ul, frames_us, frames_bb, frames_vs = [], [], [], []
    for sym, d in store.items():
        u = d["uncond"]
        frames_ul.append(u[u["side"] > 0])
        frames_us.append(u[u["side"] < 0])
        if d["S_bb_break_dn"] is not None:
            frames_bb.append(d["S_bb_break_dn"])
        if d["S_volspike18_dn"] is not None:
            frames_vs.append(d["S_volspike18_dn"])
    pops["uncond_long"] = pd.concat(frames_ul, ignore_index=True)
    pops["uncond_short"] = pd.concat(frames_us, ignore_index=True)
    pops["S_bb_break_dn"] = pd.concat(frames_bb, ignore_index=True)
    pops["S_volspike18_dn"] = pd.concat(frames_vs, ignore_index=True)

    groupers = {
        "hour": sorted(pops["uncond_long"]["hour"].unique().tolist()),
        "dow": list(range(7)),
        "session": ["Asia", "Europe", "US"],
    }

    rows = []
    t0 = time.time()
    for pop_name, tr_all in pops.items():
        for grp, buckets in groupers.items():
            for b in buckets:
                sub = tr_all[tr_all[grp] == b]
                for rr in RR_GRID:
                    d, s = slice_stats(sub, rr)
                    if d is None:
                        continue
                    HYP["A"] += 1
                    if rr == 0.5:
                        d = with_ci(d, s)
                    d.update(pop=pop_name, grp=grp, bucket=b, rr=rr)
                    rows.append(d)
    tab = pd.DataFrame(rows)
    log(f"(angle A grid built in {time.time()-t0:.0f}s, {len(tab)} cells with n_resolved>=40)")

    lab = {"hour": lambda b: f"h={b:02d}", "dow": lambda b: DOWN[int(b)], "session": lambda b: str(b)}
    for pop_name in pops:
        for grp in groupers:
            log(f"\n--- {pop_name}  by {grp}  (rr=0.50 shown with day-clustered 95% CI, n_boot=800) ---")
            log(f"{'bucket':<28}{'rr':>6}{'n':>7}{'WR':>7}{'be':>7}{'expR':>8}"
                f"{'n_tr':>6}{'e_tr':>8}{'n_te':>6}{'e_te':>8}  {'5day CI':>16}")
            sub = tab[(tab["pop"] == pop_name) & (tab["grp"] == grp) & (tab["rr"] == 0.5)]
            for _, r in sub.sort_values("expR", ascending=False).iterrows():
                log(row_line(lab[grp](r["bucket"]), r["rr"], r.to_dict()))

    log("\n--- full R:R ladder, point estimates only (no bootstrap), all buckets ---")
    for pop_name in pops:
        for grp in groupers:
            log(f"\n  {pop_name} x {grp}:")
            log(f"  {'bucket':<12}" + "".join(f"{'rr'+str(rr):>10}" for rr in RR_GRID) + "   (net expR)")
            for b in groupers[grp]:
                vals = []
                for rr in RR_GRID:
                    row = tab[(tab["pop"] == pop_name) & (tab["grp"] == grp)
                              & (tab["bucket"] == b) & (tab["rr"] == rr)]
                    vals.append(f"{row['expR'].iloc[0]:>+10.3f}" if len(row) else f"{'--':>10}")
                log(f"  {lab[grp](b):<12}" + "".join(vals))

    # best cell overall (rr=0.5, both train and test positive) gets full-ladder CI
    surv = tab[(tab["rr"] == 0.5) & (tab["e_tr"] > 0) & (tab["e_te"] > 0)].sort_values("expR", ascending=False)
    log("\n--- best rr=0.5 cells with positive train AND test (screening survivors) ---")
    if len(surv) == 0:
        log("  NONE. No time-of-day/day-of-week/session slice is positive in both train and test at rr=0.5.")
    else:
        log(f"{'pop':<18}{'grp':<9}{'bucket':<8}{'n':>6}{'expR':>8}{'e_tr':>8}{'e_te':>8}{'ci_lo':>8}{'ci_hi':>8}")
        for _, r in surv.head(10).iterrows():
            log(f"{r['pop']:<18}{r['grp']:<9}{str(r['bucket']):<8}{r['n']:>6}{r['expR']:>+8.3f}"
                f"{r['e_tr']:>+8.3f}{r['e_te']:>+8.3f}{r['ci_lo']:>+8.3f}{r['ci_hi']:>+8.3f}")
        top = surv.iloc[0]
        log(f"\n  full ladder + full CI (n_boot=800) for the single best cell: "
            f"{top['pop']} / {top['grp']}={top['bucket']}")
        tr_all = pops[top["pop"]]
        subfull = tr_all[tr_all[top["grp"]] == top["bucket"]]
        for rr in RR_GRID:
            d, s = slice_stats(subfull, rr)
            if d is None:
                continue
            d = with_ci(d, s)
            log(row_line(f"{top['pop']}/{top['grp']}={top['bucket']}", rr, d))
            if rr == 0.5:
                BEST["A"].append(dict(label=f"{top['pop']} {top['grp']}={top['bucket']}", rr=rr, **d))
    return tab

# =========================================================================
# ANGLE B -- CROSS-SECTIONAL RELATIVE STRENGTH
# =========================================================================
def angle_B(store):
    log("\n" + "=" * 100)
    log("ANGLE B: CROSS-SECTIONAL RELATIVE STRENGTH (market-neutral pair)")
    log("=" * 100)
    syms = sorted(store.keys())
    close_df = pd.DataFrame({s: pd.Series(store[s]["df"]["close"].values,
                                          index=store[s]["df"]["time"].values) for s in syms})
    close_df = close_df.dropna(how="any").sort_index()
    log(f"common 4H bars across all 12 symbols (inner join on timestamp): {len(close_df)}")

    time_to_row = {s: {int(t): i for i, t in enumerate(store[s]["df"]["time"].values)} for s in syms}
    LOOKBACKS = [6, 12, 30, 90]
    NMAX = 3
    xs_store = {}
    t0 = time.time()
    for L in LOOKBACKS:
        ret = close_df / close_df.shift(L) - 1.0
        rank_asc = ret.rank(axis=1, method="first")     # 1 = weakest
        valid = ret.notna().all(axis=1)
        weak_rank = rank_asc.where(valid)
        strong_rank = (len(syms) + 1 - rank_asc).where(valid)
        for s in syms:
            df = store[s]["df"]; path = store[s]["path"]; slip = store[s]["slip"]
            t2r = time_to_row[s]
            wr_s = weak_rank[s].dropna()
            sr_s = strong_rank[s].dropna()
            short_times = wr_s[wr_s <= NMAX]
            long_times = sr_s[sr_s <= NMAX]
            short_idx, short_rk = [], []
            for t, rk in short_times.items():
                i = t2r.get(int(t))
                if i is not None and i < len(df) - 1:
                    short_idx.append(i); short_rk.append(rk)
            long_idx, long_rk = [], []
            for t, rk in long_times.items():
                i = t2r.get(int(t))
                if i is not None and i < len(df) - 1:
                    long_idx.append(i); long_rk.append(rk)
            if not short_idx and not long_idx:
                continue
            idx_all = np.array(short_idx + long_idx, dtype=int)
            side_all = np.concatenate([-np.ones(len(short_idx)), np.ones(len(long_idx))])
            rank_all = np.array(short_rk + long_rk, dtype=float)
            tr = core.trades_for_signals(df, idx_all, side_all, 1.5, RR_GRID, path, max_hold_days=50)
            if len(tr) == 0:
                continue
            tr = recost(tr, slip)
            tr["sym"] = s; tr["L"] = L
            rank_map = dict(zip(idx_all.tolist(), rank_all.tolist()))
            tr["xs_rank"] = tr["sig_i"].map(rank_map)
            xs_store[(s, L)] = tr
        log(f"  L={L}: built ({time.time()-t0:.0f}s elapsed)")

    # ---- beta reference: BTC daily close-to-close return from its own 4H closes
    btc = store["BTCUSDT"]["df"]
    btc_day = (btc["time"].values // 86400).astype(np.int64)
    btc_close_daily = pd.Series(btc["close"].values, index=btc_day).groupby(level=0).last()
    btc_ret_daily = btc_close_daily.pct_change()

    def beta_corr(s_sub):
        """corr of the paired book's daily net_R sum (0 on flat days) with BTC daily return."""
        if len(s_sub) == 0:
            return np.nan, 0
        day = (s_sub["exit_time"].values // 86400).astype(np.int64)
        strat_daily = pd.Series(s_sub["net_R"].values, index=day).groupby(level=0).sum()
        full = strat_daily.reindex(btc_ret_daily.index, fill_value=0.0)
        mask = btc_ret_daily.notna()
        x = full[mask].values; y = btc_ret_daily[mask].values
        if mask.sum() < 30:
            return np.nan, int(mask.sum())
        return float(np.corrcoef(x, y)[0, 1]), int(mask.sum())

    rows = []
    tR0 = time.time()
    for L in LOOKBACKS:
        for N in [1, 2, 3]:
            frames = [xs_store[(s, L)][xs_store[(s, L)]["xs_rank"] <= N]
                      for s in syms if (s, L) in xs_store]
            combined = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
            for rr in RR_GRID:
                d, s = slice_stats(combined, rr)
                if d is None:
                    continue
                HYP["B"] += 1
                if rr == 0.5:
                    d = with_ci(d, s)
                    corr, ndays = beta_corr(s)
                    d["btc_corr"] = corr; d["corr_days"] = ndays
                    # legs separately, informational only
                    lg = s[s["side"] > 0]; sh = s[s["side"] < 0]
                    d["n_long"] = len(lg); d["n_short"] = len(sh)
                    d["e_long"] = lg["net_R"].mean() if len(lg) else np.nan
                    d["e_short"] = sh["net_R"].mean() if len(sh) else np.nan
                d.update(L=L, N=N, rr=rr)
                rows.append(d)
    tab = pd.DataFrame(rows)
    log(f"(angle B eval grid built in {time.time()-tR0:.0f}s, {len(tab)} cells with n_resolved>=40)")

    log("\n--- rr=0.50 (emphasis rung), paired long+short combined, day-clustered 95% CI ---")
    log(f"{'L':>4}{'N':>4}{'n':>7}{'n_lg':>6}{'n_sh':>6}{'WR':>7}{'be':>7}{'expR':>8}"
        f"{'e_long':>8}{'e_short':>8}{'e_tr':>8}{'e_te':>8}{'5day CI':>18}{'corr(BTCday)':>13}")
    sub = tab[tab["rr"] == 0.5].sort_values("expR", ascending=False)
    for _, r in sub.iterrows():
        ci = f"{r['ci_lo']:+.3f} {r['ci_hi']:+.3f}"
        log(f"{int(r['L']):>4}{int(r['N']):>4}{int(r['n']):>7}{int(r['n_long']):>6}{int(r['n_short']):>6}"
            f"{r['wr']:>7.1%}{r['be']:>7.1%}{r['expR']:>+8.3f}{r['e_long']:>+8.3f}{r['e_short']:>+8.3f}"
            f"{r['e_tr']:>+8.3f}{r['e_te']:>+8.3f}{ci:>18}{r['btc_corr']:>+13.3f}")

    log("\n--- full R:R ladder, point estimates only, paired combined expR ---")
    log(f"{'L':>4}{'N':>4}" + "".join(f"{'rr'+str(rr):>10}" for rr in RR_GRID))
    for L in LOOKBACKS:
        for N in [1, 2, 3]:
            vals = []
            for rr in RR_GRID:
                row = tab[(tab["L"] == L) & (tab["N"] == N) & (tab["rr"] == rr)]
                vals.append(f"{row['expR'].iloc[0]:>+10.3f}" if len(row) else f"{'--':>10}")
            log(f"{L:>4}{N:>4}" + "".join(vals))

    surv = tab[(tab["rr"] == 0.5) & (tab["e_tr"] > 0) & (tab["e_te"] > 0)].sort_values("expR", ascending=False)
    log("\n--- rr=0.5 combos positive in BOTH train and test ---")
    if len(surv) == 0:
        log("  NONE.")
    else:
        for _, r in surv.iterrows():
            log(f"  L={int(r['L'])} N={int(r['N'])}: expR={r['expR']:+.3f} "
                f"tr={r['e_tr']:+.3f} te={r['e_te']:+.3f} CI=[{r['ci_lo']:+.3f},{r['ci_hi']:+.3f}] "
                f"BTC-day-corr={r['btc_corr']:+.3f}")
        top = surv.iloc[0]
        log(f"\n  full ladder + full CI for the single best combo: L={int(top['L'])} N={int(top['N'])}")
        frames = [xs_store[(s, top["L"])][xs_store[(s, top["L"])]["xs_rank"] <= top["N"]]
                  for s in syms if (s, top["L"]) in xs_store]
        combined = pd.concat(frames, ignore_index=True)
        for rr in RR_GRID:
            d, s = slice_stats(combined, rr)
            if d is None:
                continue
            d = with_ci(d, s)
            corr, ndays = beta_corr(s)
            d["btc_corr"] = corr
            log(row_line(f"L={int(top['L'])} N={int(top['N'])}", rr, d) + f"  corr={corr:+.3f}")
            if rr == 0.5:
                BEST["B"].append(dict(label=f"L={int(top['L'])} N={int(top['N'])}", rr=rr, **d))
    return tab

# =========================================================================
# ANGLE C -- ENSEMBLE SCORING
# =========================================================================
def angle_C(store):
    log("\n" + "=" * 100)
    log("ANGLE C: ENSEMBLE SCORING (unweighted count of 9 causal conditions)")
    log("=" * 100)
    log("Conditions (directionally mirrored, no weights, no fit):")
    log("  trend: close vs ema200 | macd: sign + rising/falling hist | rsi: >/< 50")
    log("  bollinger: close vs bb_mid | volume: vol_ratio > 1.0 | vol_regime: atr_pct")
    log("  500-bar percentile < 0.67 | dist_ema200: |close-ema200|/atr14 <= 2.0")
    log("  run3: 3 consecutive same-direction bars | daily_trend: daily close vs daily ema200\n")

    comp_names = ["trend", "macd", "rsi", "bollinger", "volume", "vol_regime", "dist_ema200",
                  "run3", "daily_trend"]
    pooled = pd.concat([store[s]["uncond"] for s in store], ignore_index=True)

    rows = []
    t0 = time.time()
    for name in comp_names:
        sub_all = pooled[pooled[f"c_{name}"]]
        for rr in RR_GRID:
            d, s = slice_stats(sub_all, rr)
            if d is None:
                continue
            HYP["C"] += 1
            if rr == 0.5:
                d = with_ci(d, s)
            d.update(kind="single", name=name, rr=rr)
            rows.append(d)
    for k in range(1, 10):
        sub_all = pooled[pooled["score"] >= k]
        for rr in RR_GRID:
            d, s = slice_stats(sub_all, rr)
            if d is None:
                continue
            HYP["C"] += 1
            if rr == 0.5:
                d = with_ci(d, s)
            d.update(kind="ensemble", name=f"score>={k}", rr=rr)
            rows.append(d)
    tab = pd.DataFrame(rows)
    log(f"(angle C grid built in {time.time()-t0:.0f}s, {len(tab)} cells with n_resolved>=40)")

    log("\n--- rr=0.50 (emphasis rung): single conditions vs ensemble score>=k, day-clustered 95% CI ---")
    log(f"{'name':<16}{'kind':<10}{'n':>7}{'WR':>7}{'be':>7}{'expR':>8}"
        f"{'n_tr':>6}{'e_tr':>8}{'n_te':>6}{'e_te':>8}  {'5day CI':>16}")
    sub = tab[tab["rr"] == 0.5].sort_values("expR", ascending=False)
    for _, r in sub.iterrows():
        log(row_line(r["name"], 0.5, r.to_dict(), width_prefix=16) + f"  [{r['kind']}]")

    log("\n--- full R:R ladder, point estimates only ---")
    log(f"{'name':<16}" + "".join(f"{'rr'+str(rr):>10}" for rr in RR_GRID))
    for name in list(comp_names) + [f"score>={k}" for k in range(1, 10)]:
        vals = []
        for rr in RR_GRID:
            row = tab[(tab["name"] == name) & (tab["rr"] == rr)]
            vals.append(f"{row['expR'].iloc[0]:>+10.3f}" if len(row) else f"{'--':>10}")
        log(f"{name:<16}" + "".join(vals))

    best_single = tab[(tab["kind"] == "single") & (tab["rr"] == 0.5)]["expR"].max() \
        if len(tab[(tab["kind"] == "single") & (tab["rr"] == 0.5)]) else np.nan
    surv = tab[(tab["rr"] == 0.5) & (tab["kind"] == "ensemble")
               & (tab["e_tr"] > 0) & (tab["e_te"] > 0)].sort_values("expR", ascending=False)
    log(f"\n--- best single condition at rr=0.5: expR={best_single:+.3f} ---")
    log("--- ensemble score>=k combos positive in BOTH train and test at rr=0.5 ---")
    if len(surv) == 0:
        log("  NONE. No score threshold beats the train/test-positive bar at rr=0.5.")
    else:
        for _, r in surv.iterrows():
            beats = "beats best single" if r["expR"] > best_single else "does NOT beat best single"
            log(f"  {r['name']}: expR={r['expR']:+.3f} tr={r['e_tr']:+.3f} te={r['e_te']:+.3f} "
                f"CI=[{r['ci_lo']:+.3f},{r['ci_hi']:+.3f}] n={int(r['n'])}  ({beats})")
        top = surv.iloc[0]
        log(f"\n  full ladder + full CI for the single best ensemble threshold: {top['name']}")
        sub_all = pooled[pooled["score"] >= int(top["name"].split(">=")[1])]
        for rr in RR_GRID:
            d, s = slice_stats(sub_all, rr)
            if d is None:
                continue
            d = with_ci(d, s)
            log(row_line(top["name"], rr, d))
            if rr == 0.5:
                BEST["C"].append(dict(label=top["name"], rr=rr, **d))
    return tab

# =========================================================================
def main():
    global _LOGF
    _LOGF = open(OUTFILE, "w")
    t_start = time.time()
    log("lowrr/crosssec.py -- session/time-of-day, cross-sectional relative strength,")
    log("and ensemble scoring: three angles this study planned and never ran.")
    log(f"run started {pd.Timestamp.now(tz='UTC')}")
    log(f"RR grid: {RR_GRID}   train/test cut: {CUT}   symbols: 12 (BTC,ETH,SOL,XRP,DOGE,BNB,")
    log("ADA,LINK,AVAX,LTC,DOT,BCH), 4H signal / 15m resolution, stop = 1.5xATR14, Breakout costs.\n")

    syms = symbols()
    log(f"symbols with 4h+15m data: {syms}\n")
    store = {}
    for sym in syms:
        t0 = time.time()
        df, path, slip = build_symbol(sym)
        uncond = build_uncond(df, path, slip, sym)
        long_c, short_c, score_long, score_short = score_components(df)
        side_pos = uncond["side"].values > 0
        si = uncond["sig_i"].values
        uncond["score"] = np.where(side_pos, score_long[si], score_short[si])
        for name in long_c:
            uncond[f"c_{name}"] = np.where(side_pos, long_c[name][si], short_c[name][si])
        rule_bb = build_rule(df, path, slip, sym, "S_bb_break_dn")
        rule_vs = build_rule(df, path, slip, sym, "S_volspike18_dn")
        store[sym] = dict(df=df, path=path, slip=slip, uncond=uncond,
                           S_bb_break_dn=rule_bb, S_volspike18_dn=rule_vs)
        log(f"  built {sym}: uncond_rows={len(uncond)} "
            f"bb_signals={0 if rule_bb is None else rule_bb['sig_i'].nunique()} "
            f"volspike_signals={0 if rule_vs is None else rule_vs['sig_i'].nunique()} "
            f"({time.time()-t0:.1f}s)")

    tabA = angle_A(store)
    tabB = angle_B(store)
    tabC = angle_C(store)

    total = HYP["A"] + HYP["B"] + HYP["C"]
    log("\n" + "=" * 100)
    log("HYPOTHESIS COUNT AND FALSE-POSITIVE BUDGET")
    log("=" * 100)
    log(f"Angle A (session/time-of-day): {HYP['A']} hypotheses evaluated (n_resolved>=40, pooled)")
    log(f"Angle B (cross-sectional):     {HYP['B']} hypotheses evaluated")
    log(f"Angle C (ensemble scoring):    {HYP['C']} hypotheses evaluated")
    log(f"TOTAL this run:                {total} hypotheses")
    log(f"At a nominal 5% level this run alone buys ~{0.05*total:.0f} false positives for free.")
    log("This study had already burned ~500 hypotheses before this script (scan.py's 492-condition")
    log(f"sweep plus the earlier finalists/multiasset/stacking work); the honest cumulative count is")
    log(f"now on the order of {500+total}. Any single 'winner' below has to be read against that budget,")
    log("not against its own p-value in isolation.")

    log("\n" + "=" * 100)
    log("CALIBRATION CHECK")
    log("=" * 100)
    log("Prior best survivors in this study: +0.024 to +0.074 R/trade, winrate lift +3 to +6 pts")
    log("over the barrier baseline. Nothing has exceeded +6 pts lift. Any result far outside that")
    log("range below should be treated as a probable bug, not a discovery.")
    flagged = []
    for angle, rows in BEST.items():
        for r in rows:
            if r["expR"] > 0.10 or (r["wr"] - fair_ref(r)) > 0.10:
                flagged.append((angle, r))
    if flagged:
        log("FLAGGED for bug-hunting (exceeds the +0.10R / +10pt sanity bound):")
        for angle, r in flagged:
            log(f"  angle {angle}: {r['label']} rr={r['rr']} expR={r['expR']:+.3f} wr={r['wr']:.1%}")
    else:
        log("Nothing in the final best-per-angle results exceeds the +0.10R / +10pt sanity bound.")

    log("\n" + "=" * 100)
    log("BLUNT VERDICT PER ANGLE")
    log("=" * 100)
    verdict_angle("A", "session/time-of-day", tabA)
    verdict_angle("B", "cross-sectional relative strength", tabB)
    verdict_angle("C", "ensemble scoring", tabC)

    log(f"\ntotal wall time: {time.time()-t_start:.0f}s")
    log(f"\nwritten to {OUTFILE}")
    _LOGF.close()

def fair_ref(r):
    return core.fair_wr(r["rr"])

def verdict_angle(letter, title, tab):
    surv = tab[(tab["rr"] == 0.5) & (tab["e_tr"] > 0) & (tab["e_te"] > 0)]
    n_surv = len(surv)
    ci_ok = int((surv["ci_lo"] > 0).sum()) if n_surv else 0
    log(f"\n[{letter}] {title}: {n_surv} rr=0.5 cells positive in train AND test "
        f"out of the cells tested; CI computed only on this subset, {ci_ok} of those have a "
        f"day-clustered 95% CI excluding zero.")

if __name__ == "__main__":
    main()
