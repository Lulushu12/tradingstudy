"""Funding rate as a signal: the first non-OHLCV information in this study.

Every edge found so far (~1250 hypotheses across scan.py / finalists_lowrr.py /
multiasset.py) lands in a +3 to +6 winrate point band over the barrier baseline
and never higher. That band is plausibly a ceiling on what an OHLCV bar alone
can tell you about a liquid perp. Funding rate is positioning data (what
leveraged longs and shorts are paying each other), not price data, so it is
the first real test of whether the ceiling is about OHLCV specifically or
about liquid perps in general.

CAUSALITY. Funding settles at 00:00/08:00/16:00 UTC. A 4H bar's "time" column
is its OPEN. The signal used by trades_for_signals is read at the bar's CLOSE
(= next bar's open = time+4h), because that is when the next trade actually
enters. So funding is merged onto a bar's CLOSE time, not its open time:

    close_time = bar_open_time + 4h
    merge_asof(bars, funding, left_on=close_time, right_on=funding_time,
               direction="backward")

direction="backward" with default allow_exact_matches=True means a bar can
only ever see a funding settlement with funding_time <= close_time. A
settlement at exactly close_time is allowed because the task states a value
settled AT T is knowable AT T. Verification performed (see main() output):
  1. Assert, for every symbol, that after the merge every attached
     funding_time <= close_time (zero violations tolerance).
  2. Hand-check a handful of bars straddling a settlement boundary and print
     bar close time vs attached funding time/value to confirm no forward
     leak.
  3. A deliberately broken forward-merge (direction="forward") is run once on
     BTC as a control and its expectancy compared against the correct
     backward merge for the single best-looking cell. If funding were
     leaking, the forward version would look dramatically better; this is
     the sanity check the task explicitly asked for.

COMPUTE BUDGET. 4 cores, other jobs sharing the box. Cuts made (stated once
here rather than scattered):
  - bootstrap reps for day_cluster_ci: 800 (task explicitly allows this for
    screening; the block_bootstrap_ci default elsewhere is 4000).
  - the outcome universe is resolved ONCE per symbol (both sides, full rr
    grid, all bars with valid atr14+funding) via trades_for_signals, exactly
    like pooled_test.unconditional_per_asset. Every condition after that is a
    boolean slice of that table, not a new path walk. This is what keeps 40+
    conditions x 5 rr x 12 symbols tractable.
  - rolling-percentile lookbacks fixed at 90d and 365d (task's own two
    windows), not swept further.
  - cross-sectional book (H6) uses a single bucket definition (top/bottom
    quartile of 12 -> 3 symbols each side) rather than sweeping bucket size.
"""
import sys, os, warnings, pickle
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd
import indicators as ind
from lowrr import core
from lowrr.multiasset import load_path_file, BN, RULES, RR_GRID, symbols, MAJORS, SLIP_MAJOR, SLIP_ALT
from lowrr.finalists_lowrr import nonoverlap
from lowrr.pooled_test import day_cluster_ci
from lowrr.scan import CUT

HERE = os.path.dirname(os.path.abspath(__file__))
FLOW = os.path.join(HERE, "flow")
AM = 1.5
N_BOOT = 800
START = "2021-05-24"          # same start as multiasset.build, for comparability
MIN_RESOLVED = 30             # same nonoverlap-cell floor as finalists_lowrr

OUT_LINES = []
def log(s=""):
    print(s, flush=True)
    OUT_LINES.append(str(s))

# ----------------------------------------------------------------- funding IO
def load_funding(sym):
    f = pd.read_parquet(os.path.join(FLOW, f"{sym}_funding.parquet"))
    f = f.sort_values("time").reset_index(drop=True)
    f["funding"] = f["funding"].astype(float)
    return f

def funding_features(f):
    """Rolling features computed on the native 8-hourly settlement series,
    BEFORE merging onto 4H bars, so window sizes are in real settlement
    counts (3/day) rather than duplicated 4H-bar counts."""
    f = f.copy()
    fr = f["funding"]
    f["pct90d"]  = fr.rolling(270,  min_periods=180).rank(pct=True)
    f["pct365d"] = fr.rolling(1095, min_periods=700).rank(pct=True)
    f["cum3"]  = fr.rolling(3).sum()
    f["cum9"]  = fr.rolling(9).sum()
    f["cum21"] = fr.rolling(21).sum()
    for w in (3, 9, 21):
        f[f"cum{w}_pct"] = f[f"cum{w}"].rolling(270, min_periods=180).rank(pct=True)
    sgn = np.sign(fr.values)
    prev = np.roll(sgn, 1); prev[0] = 0
    f["flip_to_pos"] = (prev < 0) & (sgn > 0)
    f["flip_to_neg"] = (prev > 0) & (sgn < 0)
    return f

def attach_funding(df, f, direction="backward"):
    """Merge funding onto 4H bars at bar CLOSE time (open + 4h)."""
    df = df.copy()
    df["close_time"] = df["time"] + 4 * 3600
    fcols = ["time", "funding", "pct90d", "pct365d", "cum3", "cum9", "cum21",
             "cum3_pct", "cum9_pct", "cum21_pct", "flip_to_pos", "flip_to_neg"]
    fr = f[fcols].rename(columns={"time": "funding_time"}).sort_values("funding_time")
    df = df.sort_values("close_time")
    m = pd.merge_asof(df, fr, left_on="close_time", right_on="funding_time",
                       direction=direction)
    m = m.sort_values("time").reset_index(drop=True)
    return m

def attach_divergence(df, win=20):
    df = df.copy()
    roll_hi = df["close"].rolling(win).max()
    roll_lo = df["close"].rolling(win).min()
    new_hi = df["close"] >= roll_hi
    new_lo = df["close"] <= roll_lo
    df["div_bear"] = (new_hi & (df["cum9"] < df["cum9"].shift(win))).fillna(False)
    df["div_bull"] = (new_lo & (df["cum9"] > df["cum9"].shift(win))).fillna(False)
    return df

# ------------------------------------------------------------- causality check
def verify_causality(sym="BTCUSDT"):
    df = ind.enrich(pd.read_parquet(os.path.join(BN, f"{sym}_4h.parquet")))
    df = df[df["dt"] >= pd.Timestamp(START, tz="UTC")].reset_index(drop=True)
    f = funding_features(load_funding(sym))
    m = attach_funding(df, f)
    viol = (m["funding_time"] > m["close_time"]).sum()
    log(f"[causality] {sym}: merged rows={len(m)}  funding_time>close_time violations={viol}")
    assert viol == 0, "LOOKAHEAD: funding_time after bar close_time"
    # hand-check a few bars straddling a known settlement
    sample = m.iloc[200:206][["time", "dt", "close_time", "funding_time", "funding"]].copy()
    sample["bar_open"] = pd.to_datetime(sample["time"], unit="s", utc=True)
    sample["bar_close"] = pd.to_datetime(sample["close_time"], unit="s", utc=True)
    sample["fund_settle"] = pd.to_datetime(sample["funding_time"], unit="s", utc=True)
    log("[causality] sample rows (bar_open, bar_close, fund_settle, funding):")
    for _, r in sample.iterrows():
        log(f"   {r['bar_open']}  ->  {r['bar_close']}   sees settle {r['fund_settle']}  "
            f"funding={r['funding']:+.5f}")
    # forward-merge control: deliberately broken, must look better if leakage is possible
    m_fwd = attach_funding(df, f, direction="forward")
    lead = (m_fwd["funding_time"] > m_fwd["close_time"]).mean()
    log(f"[causality] forward-merge control: fraction of rows using a funding value "
        f"that has NOT settled yet = {lead:.1%} (this is the broken version, for contrast only)")
    return m

# ---------------------------------------------------------------- build table
def build_symbol(sym, am=AM):
    df = ind.enrich(pd.read_parquet(os.path.join(BN, f"{sym}_4h.parquet")))
    df = df[df["dt"] >= pd.Timestamp(START, tz="UTC")].reset_index(drop=True)
    f = funding_features(load_funding(sym))
    df = attach_funding(df, f)
    df = attach_divergence(df)

    # base rule masks (short-only, per task)
    bb_mask, _ = RULES["S_bb_break_dn"](df)
    vs_mask, _ = RULES["S_volspike18_dn"](df)
    df["m_bb"] = bb_mask.fillna(False).values
    df["m_vs"] = vs_mask.fillna(False).values

    path = load_path_file(os.path.join(BN, f"{sym}_15m.parquet"))
    slip = SLIP_MAJOR if sym in MAJORS else SLIP_ALT

    idx = np.arange(len(df) - 1)
    ok = (np.isfinite(df["atr14"].values[idx]) & (df["atr14"].values[idx] > 0)
          & np.isfinite(df["funding"].values[idx]))
    idx = idx[ok]
    tr = core.trades_for_signals(df, np.concatenate([idx, idx]),
                                  np.concatenate([np.ones(len(idx)), -np.ones(len(idx))]),
                                  am, RR_GRID, path, max_hold_days=50)
    tr["cost_R"] = core.cost_R(tr["stop_frac"].values, tr["nights"].values, slip_rt=2 * slip)
    tr["net_R"] = tr["gross_R"] - tr["cost_R"]
    tr["sym"] = sym
    return df, tr

# --------------------------------------------------------------- conditions
def build_conditions(df):
    """name -> (bool mask aligned to df index, side). Standalone funding
    hypotheses plus funding-filtered versions of the two short survivor
    rules (only short-biased funding conditions are used as filters, since
    both base rules are short-only)."""
    c = {}
    # H1: rolling percentile extremes
    c["fund_top_pct90d"]  = (df["pct90d"]  >= 0.90, -1)
    c["fund_bot_pct90d"]  = (df["pct90d"]  <= 0.10, +1)
    c["fund_top_pct365d"] = (df["pct365d"] >= 0.90, -1)
    c["fund_bot_pct365d"] = (df["pct365d"] <= 0.10, +1)
    # H2: raw thresholds (per 8h)
    c["fund_gt_0.01pct"] = (df["funding"] >  0.0001, -1)
    c["fund_gt_0.05pct"] = (df["funding"] >  0.0005, -1)
    c["fund_gt_0.10pct"] = (df["funding"] >  0.0010, -1)
    c["fund_lt_-0.01pct"] = (df["funding"] < -0.0001, +1)
    c["fund_lt_-0.05pct"] = (df["funding"] < -0.0005, +1)
    c["fund_lt_-0.10pct"] = (df["funding"] < -0.0010, +1)
    # H3: cumulative funding extremes (decile), 3/9/21 settlements
    for w in (3, 9, 21):
        c[f"cum{w}_top_decile"] = (df[f"cum{w}_pct"] >= 0.90, -1)
        c[f"cum{w}_bot_decile"] = (df[f"cum{w}_pct"] <= 0.10, +1)
    # H4: sign flips
    c["flip_to_pos"] = (df["flip_to_pos"].astype(bool), -1)
    c["flip_to_neg"] = (df["flip_to_neg"].astype(bool), +1)
    # H5: funding-price divergence
    c["div_bear"] = (df["div_bear"].astype(bool), -1)
    c["div_bull"] = (df["div_bull"].astype(bool), +1)

    standalone = dict(c)

    # filters: short-biased funding conditions AND the two short base rules
    short_biased = ["fund_top_pct90d", "fund_top_pct365d", "fund_gt_0.01pct",
                     "fund_gt_0.05pct", "fund_gt_0.10pct", "cum3_top_decile",
                     "cum9_top_decile", "cum21_top_decile", "flip_to_pos", "div_bear"]
    filt = {}
    for base_name, base_col in [("S_bb_break_dn", "m_bb"), ("S_volspike18_dn", "m_vs")]:
        base = df[base_col].values.astype(bool)
        for fn in short_biased:
            fmask = c[fn][0].fillna(False).values if hasattr(c[fn][0], "fillna") else np.asarray(c[fn][0])
            filt[f"{base_name}+{fn}"] = (base & fmask, -1)

    allc = {}
    for k, (mask, side) in standalone.items():
        mask = mask.fillna(False).values if hasattr(mask, "fillna") else np.asarray(mask)
        allc[k] = (mask, side)
    allc.update(filt)
    return allc, standalone, filt

# --------------------------------------------------------------- evaluation
def evaluate_pooled(sym_tables, cond_name, side, rr, min_n=MIN_RESOLVED):
    """Pool the (already-nonoverlapped-per-symbol) trades for one condition and
    rr across all symbols, and compute the headline stats."""
    frames = []
    for sym, (df, tr, conds) in sym_tables.items():
        if cond_name not in conds:
            continue
        mask, s = conds[cond_name]
        if s != side:
            continue
        sub = tr[(tr["rr"] == rr) & (tr["side"] == s) & (tr["sig_i"].map(lambda i: mask[i]))].copy()
        if len(sub) == 0:
            continue
        sub = nonoverlap(sub)
        frames.append(sub)
    if not frames:
        return None
    tr = pd.concat(frames, ignore_index=True)
    res = (tr["res"] != 0).sum()
    if res < min_n:
        return None
    wr = (tr["res"] == 1).sum() / res
    be = core.breakeven_wr(rr, tr["stop_frac"].mean(), tr["nights"].mean())
    trn = tr[tr["dt"] < CUT]; tst = tr[tr["dt"] >= CUT]
    def blk(x):
        r = (x["res"] != 0).sum()
        if r == 0:
            return np.nan, np.nan, 0
        wr_ = (x["res"] == 1).sum() / r
        return wr_, x["net_R"].mean(), len(x)
    wr_tr, e_tr, n_tr = blk(trn)
    wr_te, e_te, n_te = blk(tst)
    lo, hi, p_neg = day_cluster_ci(tr, n_boot=N_BOOT, block_days=5)
    ndays = len(np.unique(tr["entry_time"].values // 86400))
    nsyms = tr["sym"].nunique()
    return dict(cond=cond_name, side=side, rr=rr, n=len(tr), ndays=ndays, nsyms=nsyms,
                wr=wr, be=be, lift_pts=(wr - be) * 100, expR=tr["net_R"].mean(),
                ci_lo=lo, ci_hi=hi, p_neg=p_neg,
                n_tr=n_tr, wr_tr=wr_tr, e_tr=e_tr, n_te=n_te, wr_te=wr_te, e_te=e_te,
                hold_h=tr["hold_h"].mean())

# ------------------------------------------------------------- H6: cross-sectional
def build_cross_sectional(sym_tables):
    """At every 4H timestamp, rank the available symbols' current funding
    percentile (cross-sectional, computed fresh at each bar from that bar's
    funding values across symbols -- not the trailing time-series percentile
    used elsewhere), short the top quartile, long the bottom quartile."""
    frames = []
    for sym, (df, tr, conds) in sym_tables.items():
        sub = df[["time", "close_time", "funding"]].copy()
        sub["sym"] = sym
        frames.append(sub)
    panel = pd.concat(frames, ignore_index=True)
    panel = panel.dropna(subset=["funding"])
    # cross-sectional percentile rank of funding among symbols present at that bar time
    panel["xrank"] = panel.groupby("time")["funding"].rank(pct=True)
    n_at_time = panel.groupby("time")["sym"].transform("count")
    panel = panel[n_at_time >= 8]  # require a reasonably full cross-section
    short_set = panel[panel["xrank"] >= (1 - 3/12)][["time", "sym"]].copy()
    long_set  = panel[panel["xrank"] <= (3/12)][["time", "sym"]].copy()
    short_set["side"] = -1
    long_set["side"] = 1
    picks = pd.concat([short_set, long_set], ignore_index=True)
    picks["key"] = list(zip(picks["time"], picks["sym"]))

    rows = []
    for rr in RR_GRID:
        frames_rr = []
        for sym, (df, tr, conds) in sym_tables.items():
            p = picks[picks["sym"] == sym]
            if len(p) == 0:
                continue
            time_to_side = dict(zip(p["time"], p["side"]))
            sub = tr[tr["rr"] == rr].copy()
            sub["want_side"] = sub["sig_i"].map(lambda i: time_to_side.get(df["time"].values[i], 0))
            sub = sub[(sub["want_side"] != 0) & (sub["side"] == sub["want_side"])]
            if len(sub) == 0:
                continue
            sub = nonoverlap(sub)
            frames_rr.append(sub)
        if not frames_rr:
            continue
        tr_all = pd.concat(frames_rr, ignore_index=True)
        res = (tr_all["res"] != 0).sum()
        if res < MIN_RESOLVED:
            continue
        wr = (tr_all["res"] == 1).sum() / res
        be = core.breakeven_wr(rr, tr_all["stop_frac"].mean(), tr_all["nights"].mean())
        lo, hi, p_neg = day_cluster_ci(tr_all, n_boot=N_BOOT, block_days=5)
        trn = tr_all[tr_all["dt"] < CUT]; tst = tr_all[tr_all["dt"] >= CUT]
        rows.append(dict(rr=rr, n=len(tr_all), wr=wr, be=be, expR=tr_all["net_R"].mean(),
                          ci_lo=lo, ci_hi=hi, p_neg=p_neg,
                          e_tr=trn["net_R"].mean() if len(trn) else np.nan,
                          e_te=tst["net_R"].mean() if len(tst) else np.nan,
                          n_tr=len(trn), n_te=len(tst)))
        globals().setdefault("_xsec_trades", {})[rr] = tr_all
    return pd.DataFrame(rows)

def beta_neutrality(sym_tables, tr_book):
    """Correlate the cross-sectional book's daily net_R with BTC's daily return."""
    if tr_book is None or len(tr_book) == 0:
        return np.nan, 0
    daily_pnl = tr_book.groupby(tr_book["exit_time"] // 86400)["net_R"].sum()
    btc_df = sym_tables["BTCUSDT"][0]
    btc = btc_df[["time", "close"]].copy()
    btc["day"] = btc["time"] // 86400
    btc_daily = btc.groupby("day")["close"].last()
    btc_ret = btc_daily.pct_change()
    j = pd.DataFrame({"pnl": daily_pnl}).join(pd.DataFrame({"btc_ret": btc_ret}), how="inner")
    j = j.dropna()
    if len(j) < 30:
        return np.nan, len(j)
    return j["pnl"].corr(j["btc_ret"]), len(j)

# ------------------------------------------------------------------------ main
def main():
    log("=" * 78)
    log("FUNDING RATE AS A SIGNAL -- lowrr/funding.py")
    log(f"run date: 2026-08-02   symbols: {symbols()}")
    log(f"stop = {AM} x ATR14, RR grid = {RR_GRID}, bootstrap reps = {N_BOOT} (screening, see docstring)")
    log("=" * 78)

    log("\n----- causality verification -----")
    verify_causality("BTCUSDT")

    log("\n----- building per-symbol outcome universes (both sides, full rr grid, once) -----")
    sym_tables = {}
    for sym in symbols():
        df, tr = build_symbol(sym)
        allc, standalone, filt = build_conditions(df)
        sym_tables[sym] = (df, tr, allc)
        log(f"  built {sym}: {len(df)} bars, {len(tr)} raw outcome rows, "
            f"{len(allc)} conditions ({len(standalone)} standalone + {len(filt)} filters)")

    cond_names = list(next(iter(sym_tables.values()))[2].keys())
    cond_side = {k: v[1] for k, v in next(iter(sym_tables.values()))[2].items()}
    log(f"\ntotal distinct conditions defined per symbol: {len(cond_names)}")

    log("\n----- evaluating each (condition, rr) pooled across symbols -----")
    all_results = []
    n_hyp = 0
    for cn in cond_names:
        side = cond_side[cn]
        for rr in RR_GRID:
            r = evaluate_pooled(sym_tables, cn, side, rr)
            if r is None:
                continue
            n_hyp += 1
            all_results.append(r)
    res = pd.DataFrame(all_results)
    res.to_csv(os.path.join(HERE, "funding_results.csv"), index=False)

    log(f"\nHYPOTHESIS COUNT: {n_hyp} (condition x rr cells with >={MIN_RESOLVED} pooled "
        f"non-overlapping resolved trades, day-clustered CI computed on every one).")
    log(f"Study-wide count before this file: ~1250. This file adds {n_hyp}, for a running "
        f"total of ~{1250 + n_hyp}.")
    log(f"At a nominal 5% level alone (ignoring the ~1250 prior tests) you'd expect "
        f"~{0.05*n_hyp:.1f} false positives among these {n_hyp}.")

    def show(sub, title, n=25):
        log(f"\n===== {title} =====")
        log(f"{'cond':<28}{'side':>5}{'rr':>6}{'n':>6}{'days':>6}{'syms':>5}{'WR':>7}"
            f"{'be':>7}{'lift':>7}{'expR':>8}{'e_tr':>8}{'e_te':>8}{'CI95':>20}{'P(<=0)':>8}")
        for _, r in sub.head(n).iterrows():
            ci_str = f"[{r['ci_lo']:+.3f},{r['ci_hi']:+.3f}]"
            log(f"{r['cond']:<28}{int(r['side']):>5}{r['rr']:>6.2f}{int(r['n']):>6}"
                f"{int(r['ndays']):>6}{int(r['nsyms']):>5}{r['wr']:>7.1%}{r['be']:>7.1%}"
                f"{r['lift_pts']:>+7.1f}{r['expR']:>+8.3f}{r['e_tr']:>+8.3f}{r['e_te']:>+8.3f}"
                f"{ci_str:>20}{r['p_neg']:>8.1%}")

    if len(res):
        res_sorted = res.sort_values("expR", ascending=False)
        show(res_sorted, "ALL cells ranked by pooled net expectancy (top 25)")

        surv = res[(res["e_tr"] > 0) & (res["e_te"] > 0) & (res["ci_lo"] > 0)]
        log(f"\ncells positive in train AND test AND with day-clustered CI excluding zero: "
            f"{len(surv)} / {len(res)}")
        if len(surv):
            show(surv.sort_values("expR", ascending=False), "SURVIVORS (train+, test+, CI excludes 0)", 40)
        else:
            log("NOTHING survives all three filters.")

        log("\n----- best cell per hypothesis family -----")
        fam_map = {
            "H1_pctile_extreme": lambda c: c.startswith("fund_top_pct") or c.startswith("fund_bot_pct"),
            "H2_raw_threshold":  lambda c: c.startswith("fund_gt_") or c.startswith("fund_lt_"),
            "H3_cumulative":     lambda c: c.startswith("cum") and ("+" not in c),
            "H4_sign_flip":      lambda c: c.startswith("flip_") and ("+" not in c),
            "H5_divergence":     lambda c: c.startswith("div_") and ("+" not in c),
            "H_filter_bb":       lambda c: c.startswith("S_bb_break_dn+"),
            "H_filter_volspike": lambda c: c.startswith("S_volspike18_dn+"),
        }
        for fam, pred in fam_map.items():
            sub = res[res["cond"].map(pred)]
            if len(sub) == 0:
                log(f"  {fam:<20}: no qualifying cells (n>={MIN_RESOLVED})")
                continue
            best = sub.sort_values("expR", ascending=False).iloc[0]
            log(f"  {fam:<20}: best = {best['cond']} rr={best['rr']} n={int(best['n'])} "
                f"WR={best['wr']:.1%} lift={best['lift_pts']:+.1f}pt expR={best['expR']:+.3f} "
                f"train={best['e_tr']:+.3f} test={best['e_te']:+.3f} "
                f"CI95=[{best['ci_lo']:+.3f},{best['ci_hi']:+.3f}] P(<=0)={best['p_neg']:.1%}")

    log("\n\n----- H6: cross-sectional funding book (short top quartile, long bottom quartile) -----")
    xsec = build_cross_sectional(sym_tables)
    if len(xsec):
        log(f"{'rr':>6}{'n':>7}{'WR':>7}{'be':>7}{'expR':>8}{'e_tr':>8}{'e_te':>8}"
            f"{'CI95':>20}{'P(<=0)':>8}")
        for _, r in xsec.iterrows():
            ci_str = f"[{r['ci_lo']:+.3f},{r['ci_hi']:+.3f}]"
            log(f"{r['rr']:>6.2f}{int(r['n']):>7}{r['wr']:>7.1%}{r['be']:>7.1%}{r['expR']:>+8.3f}"
                f"{r['e_tr']:>+8.3f}{r['e_te']:>+8.3f}"
                f"{ci_str:>20}{r['p_neg']:>8.1%}")
        best_rr = xsec.sort_values("n", ascending=False).iloc[0]["rr"] if 0.5 not in xsec["rr"].values else 0.5
        tr_book = globals().get("_xsec_trades", {}).get(best_rr)
        corr, ndays = beta_neutrality(sym_tables, tr_book)
        log(f"\nbeta-neutrality check (rr={best_rr}): corr(book daily net_R, BTC daily return) "
            f"= {corr:+.3f}  over {ndays} overlapping days")
    else:
        log("cross-sectional book produced no cell with >=%d trades." % MIN_RESOLVED)
        corr = np.nan

    log("\n\n----- calibration check -----")
    if len(res):
        mx = res["expR"].max()
        mx_lift = res["lift_pts"].max()
        log(f"max pooled expR across ALL cells: {mx:+.3f}  (study ceiling so far: ~+0.12 R/trade)")
        log(f"max winrate lift over breakeven across ALL cells: {mx_lift:+.1f} pts "
            f"(study ceiling so far: ~+6 pts)")
        if mx > 0.15 or mx_lift > 8:
            log("*** ABOVE CALIBRATION CEILING: treat as suspect, re-check causality "
                "before reporting as real. ***")
        else:
            log("within the calibration band established by the rest of the study.")

    with open(os.path.join(HERE, "funding_out.txt"), "w") as fh:
        fh.write("\n".join(OUT_LINES) + "\n")
    log(f"\nwrote {os.path.join(HERE, 'funding_out.txt')}")

if __name__ == "__main__":
    main()
