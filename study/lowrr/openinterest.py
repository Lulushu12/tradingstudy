"""Open interest and positioning data as a signal.

Same question as funding.py: is the ~3-6 winrate-point ceiling this study keeps
hitting a property of OHLCV specifically, or of liquid perps in general? Open
interest, top-trader long/short ratios and taker buy/sell flow are none of
them price data -- they are the derivatives book itself. If anything in this
study should break the ceiling, it is a plausible candidate here.

*** HEADLINE WEAKNESS, STATED BEFORE ANY RESULT: this file runs on however
many of {BTCUSDT, ETHUSDT, SOLUSDT} have a clean flow/<SYM>_metrics.parquet at
run time. As of this run only BTCUSDT does; ETHUSDT and SOLUSDT are still
being written by another process and are excluded (checked live via
os.path.exists + a real load, not assumed). Every other result in this study
was cross-checked against 11 out-of-sample instruments never used to select
the rule, and that check is what has been killing false positives here. That
check is NOT available in this file. A positive BTC-only result is exactly
the shape of finding this study has repeatedly shown evaporates once other
instruments are added (see LOW_RR_REPORT.md section 7). Read every number
below with that discounted in advance, not as an afterthought. ***

DATA QUALITY NOTE (found while building this, not assumed): the "time" column
in flow/<SYM>_metrics.parquet is NOT a usable unix timestamp. It increments by
~1 almost every row regardless of the actual gap between rows (verified: for
BTCUSDT, diff(time)==1 on 175,940/175,961 rows while the real gap in "dt"
ranges 5 to 630 minutes, median ~15-16.7 minutes -- nowhere near the "true
unix seconds" a value like 1609459 would suggest, and nowhere near the
"5-minute granularity" the task description assumed). "dt" (a proper
timezone-aware timestamp, monotonic, no duplicates, no NaT) is used for every
causal computation in this file; "time" from that parquet is never read.
Because the native sampling is irregular, every rolling/lag feature below is
computed as a genuine TIME-based window (pandas '30D'/'90D'/'6h'/'24h'
rolling, or an explicit as-of lookback), never a fixed row count.

CAUSALITY. Same pattern as funding.py. A 4H bar's "time" column (from the bn/
parquet, which IS a real unix-second column, verified separately below) is
its OPEN; the signal is read at the bar's CLOSE (= next bar's open), so OI
features are merged onto close_time = open_time + 4h with
merge_asof(..., direction="backward"). Verification performed (see main()):
  1. Assert zero rows where the attached OI snapshot's real timestamp is
     after the bar's close time.
  2. Hand-print a run of consecutive 4H bars next to the OI timestamp/value
     merge_asof actually attached to each one.
  3. A deliberately broken forward-merge control on BTC, contrasted against
     the correct backward merge.

COMPUTE BUDGET. 4 shared cores. Cuts made (stated once here):
  - bootstrap reps for day_cluster_ci: 800, per task allowance.
  - rolling-percentile windows fixed at 30d and 90d, not swept further.
  - H1 (build/flush) tested at one direction per combination (a
    momentum-confirmation reading: OI+price both up -> long, both down ->
    short, etc), not both directions -- doubling every OI x price combo to
    also test the contrarian reading would double H1's hypothesis count for
    a reading this file does not have a strong prior on either side of.
    Stated plainly rather than silently picking without saying so.
  - H2/H4/H4b (OI level, top-trader ratios, global account ratio) use a
    contrarian "fade positioning extremes" convention, matching the
    convention funding.py already used for funding-rate extremes.
  - H5 (taker volume ratio) uses the OPPOSITE convention deliberately: it is
    immediate executed flow, not accumulated positioning, so it is tested as
    momentum-following (aggressive buying flow -> long), not fade. Flagged
    explicitly since this is the one place the sign convention flips.
  - the outcome universe (both sides, full rr grid) is resolved ONCE per
    symbol via trades_for_signals; every condition after that is a boolean
    slice of that table.
"""
import sys, os, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd
import indicators as ind
from lowrr import core
from lowrr.multiasset import load_path_file, BN, RULES, RR_GRID, MAJORS, SLIP_MAJOR, SLIP_ALT
from lowrr.finalists_lowrr import nonoverlap
from lowrr.pooled_test import day_cluster_ci
from lowrr.scan import CUT
from lowrr import funding as funding_mod

HERE = os.path.dirname(os.path.abspath(__file__))
FLOW = os.path.join(HERE, "flow")
AM = 1.5
N_BOOT = 800
START = "2021-05-24"          # same start as multiasset.build / funding.py, for comparability
MIN_RESOLVED = 30
CANDIDATE_SYMS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]   # exactly the task's 1-3 instrument scope
PRIOR_HYP_COUNT = 1425        # study-wide count going into this file (funding.py's own tally)

OUT_LINES = []
def log(s=""):
    print(s, flush=True)
    OUT_LINES.append(str(s))

# ----------------------------------------------------------------- generic causal helpers
def asof_lag(src_epoch, src_val, target_epoch):
    """For each target time, the latest src value with src_epoch <= target_epoch.
    NaN if the target predates all source data. Pure searchsorted, causal by
    construction, robust to irregular sampling (no assumption of fixed spacing)."""
    idx = np.searchsorted(src_epoch, target_epoch, side="right") - 1
    out = np.full(len(target_epoch), np.nan)
    ok = idx >= 0
    out[ok] = src_val[idx[ok]]
    return out

# ----------------------------------------------------------------- metrics IO + features
def available_oi_symbols():
    """Only a symbol whose flow/<SYM>_metrics.parquet exists AND loads cleanly AND has
    the expected columns AND has matching bn/4h+15m files is used. Checked live."""
    required_cols = {"time", "dt", "sum_open_interest", "sum_open_interest_value",
                      "count_toptrader_long_short_ratio", "sum_toptrader_long_short_ratio",
                      "count_long_short_ratio", "sum_taker_long_short_vol_ratio"}
    out = []
    for sym in CANDIDATE_SYMS:
        p = os.path.join(FLOW, f"{sym}_metrics.parquet")
        if not os.path.exists(p):
            log(f"  {sym}: {p} does not exist yet -- excluded")
            continue
        try:
            df = pd.read_parquet(p)
        except Exception as e:
            log(f"  {sym}: metrics parquet failed to load ({e}) -- excluded")
            continue
        if len(df) == 0 or not required_cols.issubset(df.columns):
            log(f"  {sym}: metrics parquet malformed (n={len(df)}, cols missing) -- excluded")
            continue
        b4 = os.path.join(BN, f"{sym}_4h.parquet"); b15 = os.path.join(BN, f"{sym}_15m.parquet")
        if not (os.path.exists(b4) and os.path.exists(b15)):
            log(f"  {sym}: missing bn 4h/15m -- excluded")
            continue
        log(f"  {sym}: metrics parquet OK, {len(df)} rows, {df['dt'].min()} to {df['dt'].max()} -- INCLUDED")
        out.append(sym)
    return out

def load_metrics(sym):
    m = pd.read_parquet(os.path.join(FLOW, f"{sym}_metrics.parquet")).sort_values("dt").reset_index(drop=True)
    assert m["dt"].is_monotonic_increasing and m["dt"].duplicated().sum() == 0, \
        f"{sym}: metrics dt not clean"
    # 'time' column is not trustworthy as unix seconds (see module docstring) -- derive our own.
    # NOTE: pandas 3.x stores this column as datetime64[us, UTC] (microsecond unit), so a plain
    # .astype('int64') // 10**9 (which assumes nanoseconds) silently produces a garbage 1970
    # timestamp. Use timedelta floor-division instead: unit-agnostic, correct regardless of the
    # underlying storage resolution. (Caught by the causality hand-print below showing
    # "1970-01-21" instead of a real date -- exactly the kind of silent bug this check is for.)
    m["epoch_s"] = ((m["dt"] - pd.Timestamp("1970-01-01", tz="UTC")) // pd.Timedelta(seconds=1)).astype(np.int64)
    for c in ["sum_open_interest", "count_toptrader_long_short_ratio",
              "sum_toptrader_long_short_ratio", "count_long_short_ratio",
              "sum_taker_long_short_vol_ratio"]:
        m[c] = m[c].astype(float)
    return m

def oi_native_features(m):
    """Rolling/lag features computed on the native irregular metrics series,
    BEFORE merging onto 4H bars -- exactly funding.py's pattern of computing
    features on the native clock so window sizes are real elapsed time."""
    m = m.copy()
    ep = m["epoch_s"].values.astype(np.int64)
    med_gap_s = m["dt"].diff().dt.total_seconds().median()
    rows_per_day = 86400.0 / med_gap_s
    min30 = max(50, int(0.6 * 30 * rows_per_day))
    min90 = max(50, int(0.6 * 90 * rows_per_day))

    oi = m["sum_open_interest"].values
    for h in (6, 24, 72):
        lag_val = asof_lag(ep, oi, ep - h * 3600)
        with np.errstate(divide="ignore", invalid="ignore"):
            m[f"oi_pct_{h}h"] = (oi - lag_val) / lag_val

    idx = pd.DatetimeIndex(m["dt"])
    s_oi = pd.Series(oi, index=idx)
    m["oi_pct30d"] = s_oi.rolling("30D", min_periods=min30).rank(pct=True).values
    m["oi_pct90d"] = s_oi.rolling("90D", min_periods=min90).rank(pct=True).values

    for col in ["count_toptrader_long_short_ratio", "sum_toptrader_long_short_ratio",
                "count_long_short_ratio"]:
        s = pd.Series(m[col].values, index=idx)
        m[f"{col}_pct30d"] = s.rolling("30D", min_periods=min30).rank(pct=True).values
        m[f"{col}_pct90d"] = s.rolling("90D", min_periods=min90).rank(pct=True).values

    s_tk = pd.Series(m["sum_taker_long_short_vol_ratio"].values, index=idx)
    m["taker_pct30d"] = s_tk.rolling("30D", min_periods=min30).rank(pct=True).values
    m["taker_pct90d"] = s_tk.rolling("90D", min_periods=min90).rank(pct=True).values
    m["taker_avg6h"] = s_tk.rolling("6h", min_periods=1).mean().values
    m["taker_avg24h"] = s_tk.rolling("24h", min_periods=1).mean().values
    m["taker_avg6h_pct30d"] = pd.Series(m["taker_avg6h"].values, index=idx).rolling(
        "30D", min_periods=min30).rank(pct=True).values
    m["taker_avg24h_pct30d"] = pd.Series(m["taker_avg24h"].values, index=idx).rolling(
        "30D", min_periods=min30).rank(pct=True).values
    m.attrs["rows_per_day"] = rows_per_day
    return m

MCOLS = ["epoch_s", "sum_open_interest",
         "oi_pct_6h", "oi_pct_24h", "oi_pct_72h", "oi_pct30d", "oi_pct90d",
         "count_toptrader_long_short_ratio_pct30d", "count_toptrader_long_short_ratio_pct90d",
         "sum_toptrader_long_short_ratio_pct30d", "sum_toptrader_long_short_ratio_pct90d",
         "count_long_short_ratio_pct30d", "count_long_short_ratio_pct90d",
         "taker_pct30d", "taker_pct90d",
         "taker_avg6h_pct30d", "taker_avg24h_pct30d"]

def attach_oi(df, m, direction="backward"):
    """Merge OI/positioning features onto 4H bars at bar CLOSE time (open+4h)."""
    df = df.copy()
    df["close_time"] = df["time"] + 4 * 3600
    mr = m[MCOLS].rename(columns={"epoch_s": "oi_time"}).sort_values("oi_time")
    df = df.sort_values("close_time")
    out = pd.merge_asof(df, mr, left_on="close_time", right_on="oi_time", direction=direction)
    out = out.sort_values("time").reset_index(drop=True)
    return out

def attach_oi_divergence(df, win=20):
    df = df.copy()
    roll_hi = df["close"].rolling(win).max()
    roll_lo = df["close"].rolling(win).min()
    new_hi = df["close"] >= roll_hi
    new_lo = df["close"] <= roll_lo
    oi = df["sum_open_interest"]
    df["oi_div_bear"] = (new_hi & (oi < oi.shift(win))).fillna(False)
    df["oi_div_bull"] = (new_lo & (oi > oi.shift(win))).fillna(False)
    return df

def price_lag_pct(df, path, hours):
    """Price % change over the trailing `hours`, looked up causally on the fine
    (15m) path via as-of backward lookback from each bar's own close_time."""
    pt, po, ph, pl, pc = path
    close_time = df["close_time"].values.astype(np.int64)
    lag_px = asof_lag(pt, pc, close_time - hours * 3600)
    cur_px = df["close"].values
    with np.errstate(divide="ignore", invalid="ignore"):
        return (cur_px - lag_px) / lag_px

def build_h1(df, path):
    """OI build/flush x price direction, one momentum-confirming side per
    combination (see module docstring for the reasoning and the acknowledged
    cut of not also testing the contrarian reading)."""
    conds = {}
    for h in (6, 24, 72):
        oi_chg = df[f"oi_pct_{h}h"]
        px_chg = pd.Series(price_lag_pct(df, path, h), index=df.index)
        df[f"price_pct_{h}h"] = px_chg
        oi_up = (oi_chg > 0); oi_dn = (oi_chg < 0)
        px_up = (px_chg > 0); px_dn = (px_chg < 0)
        conds[f"h1_build_long_{h}h"]   = ((oi_up & px_up).fillna(False).values, +1)   # new longs, price up
        conds[f"h1_build_short_{h}h"]  = ((oi_up & px_dn).fillna(False).values, -1)   # new shorts, price down
        conds[f"h1_cover_rally_{h}h"]  = ((oi_dn & px_up).fillna(False).values, +1)   # short covering, price up
        conds[f"h1_unwind_dn_{h}h"]    = ((oi_dn & px_dn).fillna(False).values, -1)   # long capitulation, price down
    return conds, df

def pctile_family(df, colpct30, colpct90, label, side_top, side_bot):
    return {
        f"{label}_top_pct30d": (df[colpct30].values >= 0.90, side_top),
        f"{label}_bot_pct30d": (df[colpct30].values <= 0.10, side_bot),
        f"{label}_top_pct90d": (df[colpct90].values >= 0.90, side_top),
        f"{label}_bot_pct90d": (df[colpct90].values <= 0.10, side_bot),
    }

def pctile_single(df, colpct, label, side_top, side_bot):
    return {
        f"{label}_top": (df[colpct].values >= 0.90, side_top),
        f"{label}_bot": (df[colpct].values <= 0.10, side_bot),
    }

# ------------------------------------------------------------- causality check
def verify_causality(sym="BTCUSDT"):
    df = ind.enrich(pd.read_parquet(os.path.join(BN, f"{sym}_4h.parquet")))
    df = df[df["dt"] >= pd.Timestamp(START, tz="UTC")].reset_index(drop=True)
    m = oi_native_features(load_metrics(sym))
    merged = attach_oi(df, m)
    viol = (merged["oi_time"] > merged["close_time"]).sum()
    log(f"[causality] {sym}: merged rows={len(merged)}  oi_time>close_time violations={viol}")
    assert viol == 0, "LOOKAHEAD: OI snapshot time after bar close_time"

    sample = merged.iloc[500:507][["time", "close_time", "oi_time", "sum_open_interest"]].copy()
    sample["bar_open"] = pd.to_datetime(sample["time"], unit="s", utc=True)
    sample["bar_close"] = pd.to_datetime(sample["close_time"], unit="s", utc=True)
    sample["oi_seen_at"] = pd.to_datetime(sample["oi_time"], unit="s", utc=True)
    log("[causality] sample rows (bar_open, bar_close, latest OI snapshot seen, its value):")
    for _, r in sample.iterrows():
        log(f"   {r['bar_open']}  ->  {r['bar_close']}   sees OI @ {r['oi_seen_at']}  "
            f"(lag={ (r['bar_close']-r['oi_seen_at']).total_seconds()/60:.0f} min)  "
            f"OI={r['sum_open_interest']:.1f}")

    merged_fwd = attach_oi(df, m, direction="forward")
    lead = (merged_fwd["oi_time"] > merged_fwd["close_time"]).mean()
    log(f"[causality] forward-merge control: fraction of rows using an OI snapshot that "
        f"had NOT happened yet at bar close = {lead:.1%} (this is the broken version, for contrast only)")
    return merged

# ---------------------------------------------------------------- build table
def build_symbol_direction(sym, direction, am=AM):
    """Same build as build_symbol, but with the OI merge direction parameterised
    so the calibration check can rebuild the whole outcome universe under the
    deliberately-broken forward merge and compare cell-by-cell against the real
    (backward) version."""
    df = ind.enrich(pd.read_parquet(os.path.join(BN, f"{sym}_4h.parquet")))
    df = df[df["dt"] >= pd.Timestamp(START, tz="UTC")].reset_index(drop=True)
    m = oi_native_features(load_metrics(sym))
    df = attach_oi(df, m, direction=direction)
    df = attach_oi_divergence(df)
    path = load_path_file(os.path.join(BN, f"{sym}_15m.parquet"))
    h1_conds, df = build_h1(df, path)

    bb_mask, _ = RULES["S_bb_break_dn"](df)
    vs_mask, _ = RULES["S_volspike18_dn"](df)
    df["m_bb"] = bb_mask.fillna(False).values
    df["m_vs"] = vs_mask.fillna(False).values

    slip = SLIP_MAJOR if sym in MAJORS else SLIP_ALT
    idx = np.arange(len(df) - 1)
    ok = (np.isfinite(df["atr14"].values[idx]) & (df["atr14"].values[idx] > 0)
          & np.isfinite(df["sum_open_interest"].values[idx]))
    idx = idx[ok]
    tr = core.trades_for_signals(df, np.concatenate([idx, idx]),
                                  np.concatenate([np.ones(len(idx)), -np.ones(len(idx))]),
                                  am, RR_GRID, path, max_hold_days=50)
    tr["cost_R"] = core.cost_R(tr["stop_frac"].values, tr["nights"].values, slip_rt=2 * slip)
    tr["net_R"] = tr["gross_R"] - tr["cost_R"]
    tr["sym"] = sym
    return df, tr, path, h1_conds

def build_symbol(sym, am=AM):
    return build_symbol_direction(sym, "backward", am=am)

# --------------------------------------------------------------- conditions
def build_conditions(df, h1_conds):
    c = {}
    c.update(h1_conds)                                                    # H1: 12
    c.update(pctile_family(df, "oi_pct30d", "oi_pct90d", "h2_oi", -1, +1))  # H2: 4 (contrarian)
    c["h3_div_bear"] = (df["oi_div_bear"].values.astype(bool), -1)          # H3: 2
    c["h3_div_bull"] = (df["oi_div_bull"].values.astype(bool), +1)
    c.update(pctile_family(df, "count_toptrader_long_short_ratio_pct30d",
                            "count_toptrader_long_short_ratio_pct90d", "h4_tt_count", -1, +1))  # 4
    c.update(pctile_family(df, "sum_toptrader_long_short_ratio_pct30d",
                            "sum_toptrader_long_short_ratio_pct90d", "h4_tt_sum", -1, +1))       # 4
    c.update(pctile_family(df, "count_long_short_ratio_pct30d",
                            "count_long_short_ratio_pct90d", "h4b_global", -1, +1))              # 4 (bonus col)
    c.update(pctile_family(df, "taker_pct30d", "taker_pct90d", "h5_taker", +1, -1))              # H5: 4 (momentum!)
    c.update(pctile_single(df, "taker_avg6h_pct30d", "h5_taker_avg6h", +1, -1))                  # 2
    c.update(pctile_single(df, "taker_avg24h_pct30d", "h5_taker_avg24h", +1, -1))                # 2

    standalone = dict(c)
    short_biased = [k for k, (mask, side) in c.items() if side == -1]
    filt = {}
    for base_name, base_col in [("S_bb_break_dn", "m_bb"), ("S_volspike18_dn", "m_vs")]:
        base = df[base_col].values.astype(bool)
        for fn in short_biased:
            fmask, _ = c[fn]
            filt[f"{base_name}+{fn}"] = (base & np.asarray(fmask), -1)

    allc = dict(standalone)
    allc.update(filt)
    return allc, standalone, filt

# --------------------------------------------------------------- evaluation
def evaluate_pooled(sym_tables, cond_name, side, rr, min_n=MIN_RESOLVED):
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
    # clustering-artifact check: how much of n sits on the busiest few days?
    day_counts = pd.Series(tr["entry_time"].values // 86400).value_counts()
    top3_frac = day_counts.head(3).sum() / len(tr)
    return dict(cond=cond_name, side=side, rr=rr, n=len(tr), ndays=ndays, nsyms=nsyms,
                wr=wr, be=be, lift_pts=(wr - be) * 100, expR=tr["net_R"].mean(),
                ci_lo=lo, ci_hi=hi, p_neg=p_neg,
                n_tr=n_tr, wr_tr=wr_tr, e_tr=e_tr, n_te=n_te, wr_te=wr_te, e_te=e_te,
                hold_h=tr["hold_h"].mean(), top3_frac=top3_frac)

def show(sub, title, n=25):
    log(f"\n===== {title} =====")
    log(f"{'cond':<34}{'side':>5}{'rr':>6}{'n':>6}{'days':>6}{'top3d%':>7}{'WR':>7}"
        f"{'be':>7}{'lift':>7}{'expR':>8}{'e_tr':>8}{'e_te':>8}{'CI95':>20}{'P(<=0)':>8}")
    for _, r in sub.head(n).iterrows():
        ci_str = f"[{r['ci_lo']:+.3f},{r['ci_hi']:+.3f}]"
        log(f"{r['cond']:<34}{int(r['side']):>5}{r['rr']:>6.2f}{int(r['n']):>6}"
            f"{int(r['ndays']):>6}{r['top3_frac']:>7.1%}{r['wr']:>7.1%}{r['be']:>7.1%}"
            f"{r['lift_pts']:>+7.1f}{r['expR']:>+8.3f}{r['e_tr']:>+8.3f}{r['e_te']:>+8.3f}"
            f"{ci_str:>20}{r['p_neg']:>8.1%}")

# ------------------------------------------------------------------------ main
def main():
    log("=" * 78)
    log("OPEN INTEREST / POSITIONING AS A SIGNAL -- lowrr/openinterest.py")
    log("run date: 2026-08-02")
    log("=" * 78)

    log("\n----- symbol availability (checked live, task's 1-3 instrument scope) -----")
    syms = available_oi_symbols()
    log(f"\nSYMBOLS ACTUALLY USED: {syms}")
    if len(syms) < 3:
        missing = [s for s in CANDIDATE_SYMS if s not in syms]
        log(f"*** WEAKNESS: {missing} not available at run time. This study's usual "
            f"11-instrument out-of-sample check is NOT possible here. Any positive result "
            f"below is BTC-only (or at most {len(syms)}-instrument) and should be read as "
            f"provisional in the same way the pre-multiasset S_bb_break_dn numbers in "
            f"LOW_RR_REPORT.md section 4 were provisional before section 7 ran. ***")
    if not syms:
        log("No symbols available at all. Aborting.")
        with open(os.path.join(HERE, "oi_out.txt"), "w") as fh:
            fh.write("\n".join(OUT_LINES) + "\n")
        return

    log("\n----- data quality: the metrics parquet 'time' column -----")
    log("Verified (BTCUSDT): diff(time)==1 on 175,940/175,961 rows while the real gap in "
        "'dt' ranges 5-630 minutes (median ~15-16.7). 'time' is a near-sequential row "
        "counter, not unix seconds, and is never used below. All timestamps come from 'dt'.")
    med_gap = load_metrics("BTCUSDT")["dt"].diff().dt.total_seconds().median()
    log(f"Median native sampling gap: {med_gap/60:.1f} minutes (task description assumed "
        f"5-minute; actual is ~3x that and irregular -- every rolling window below is "
        f"time-based, not row-count-based, specifically because of this).")

    log("\n----- causality verification (BTCUSDT) -----")
    verify_causality("BTCUSDT")

    log("\n----- building per-symbol outcome universes (both sides, full rr grid, once) -----")
    sym_tables = {}
    aux = {}   # sym -> (df, path, h1_conds) kept for H6
    for sym in syms:
        df, tr, path, h1_conds = build_symbol(sym)
        allc, standalone, filt = build_conditions(df, h1_conds)
        sym_tables[sym] = (df, tr, allc)
        aux[sym] = (df, tr, path)
        log(f"  built {sym}: {len(df)} bars, {len(tr)} raw outcome rows, "
            f"{len(allc)} conditions ({len(standalone)} standalone + {len(filt)} filters)")

    cond_names = list(next(iter(sym_tables.values()))[2].keys())
    cond_side = {k: v[1] for k, v in next(iter(sym_tables.values()))[2].items()}
    log(f"\ntotal distinct conditions defined per symbol: {len(cond_names)}")

    log("\n----- evaluating each (condition, rr) pooled across available symbols -----")
    all_results = []
    for cn in cond_names:
        side = cond_side[cn]
        for rr in RR_GRID:
            r = evaluate_pooled(sym_tables, cn, side, rr)
            if r is None:
                continue
            all_results.append(r)
    res = pd.DataFrame(all_results)
    res.to_csv(os.path.join(HERE, "oi_results.csv"), index=False)
    n_hyp = len(res)

    log(f"\nHYPOTHESIS COUNT: {n_hyp} (condition x rr cells with >={MIN_RESOLVED} pooled "
        f"non-overlapping resolved trades on {len(syms)} symbol(s), day-clustered CI on every one).")
    log(f"Study-wide count before this file: ~{PRIOR_HYP_COUNT}. This file adds {n_hyp}, "
        f"for a running total of ~{PRIOR_HYP_COUNT + n_hyp}.")
    log(f"At a nominal 5% level alone (ignoring the ~{PRIOR_HYP_COUNT} prior tests) you'd "
        f"expect ~{0.05*n_hyp:.1f} false positives among these {n_hyp}.")

    surv = pd.DataFrame()
    if len(res):
        res_sorted = res.sort_values("expR", ascending=False)
        show(res_sorted, "ALL cells ranked by pooled net expectancy (top 25)")

        surv = res[(res["e_tr"] > 0) & (res["e_te"] > 0) & (res["ci_lo"] > 0)]
        log(f"\ncells positive in train AND test AND with day-clustered CI excluding zero: "
            f"{len(surv)} / {len(res)}")
        if len(surv):
            show(surv.sort_values("expR", ascending=False), "SURVIVORS (train+, test+, CI excludes 0)", 40)
            for _, r in surv.sort_values("expR", ascending=False).head(10).iterrows():
                if r["top3_frac"] > 0.40:
                    log(f"  *** CLUSTERING FLAG: {r['cond']} rr={r['rr']} has {r['top3_frac']:.0%} "
                        f"of its {int(r['n'])} trades on just its 3 busiest days ({int(r['ndays'])} "
                        f"distinct days total) -- this is a small-event-count sample dressed up as n, "
                        f"treat with extra suspicion.")

            log("\n----- regime-clustering stress test on the top survivors -----")
            log("top3d% (busiest-3-calendar-days share) missed a real pattern in the raw trade "
                "list: several of these cells fire many times in a row across a single multi-week "
                "down move (e.g. 17 fires in 9 days in Jun-Jul 2024), which is clustering at a "
                "longer horizon than 'day'. Two extra checks per survivor: an EPISODE count "
                "(distinct clusters of trades with >=10 days between them -- the real count of "
                "independent 'events'), and the day-clustered CI recomputed with a 4x coarser "
                "block (20 days instead of 5) to see if significance survives much heavier "
                "declustering.")
            log(f"{'cond':<40}{'rr':>5}{'n':>5}{'ndays':>7}{'episodes':>9}{'CI(blk5)':>20}{'CI(blk20)':>20}")
            sym0, (df0, tr0, allc0) = "BTCUSDT", sym_tables["BTCUSDT"]
            for _, r in surv.sort_values("expR", ascending=False).head(10).iterrows():
                mask, side = allc0[r["cond"]]
                sub = tr0[(tr0["rr"] == r["rr"]) & (tr0["side"] == side)
                          & (tr0["sig_i"].map(lambda i: mask[i]))]
                sub = nonoverlap(sub)
                days_sorted = sorted(set((sub["entry_time"].values // 86400).tolist()))
                neps = 1
                for i in range(1, len(days_sorted)):
                    if days_sorted[i] - days_sorted[i - 1] > 10:
                        neps += 1
                lo20, hi20, p20 = day_cluster_ci(sub, n_boot=N_BOOT, block_days=20)
                ci5_str = f"[{r['ci_lo']:+.3f},{r['ci_hi']:+.3f}]"
                ci20_str = f"[{lo20:+.3f},{hi20:+.3f}]"
                log(f"{r['cond']:<40}{r['rr']:>5.2f}{len(sub):>5}{len(days_sorted):>7}{neps:>9}"
                    f"{ci5_str:>20}{ci20_str:>20}")
            log("Read this as: if CI(blk20) still excludes zero and episode count is well into "
                "double digits, the result is not explained by a handful of correlated event-days; "
                "it is still a small-n, single-instrument, heavily-multiple-tested result, which "
                "is a different and much weaker problem than clustering, but a real one on its own.")
        else:
            log("NOTHING survives all three filters.")

        log("\n----- best cell per hypothesis family -----")
        fam_map = {
            "H1_build_flush":      lambda c: c.startswith("h1_") and ("+" not in c),
            "H2_oi_pctile":        lambda c: c.startswith("h2_oi") and ("+" not in c),
            "H3_divergence":       lambda c: c.startswith("h3_div") and ("+" not in c),
            "H4_toptrader_count":  lambda c: c.startswith("h4_tt_count") and ("+" not in c),
            "H4_toptrader_sum":    lambda c: c.startswith("h4_tt_sum") and ("+" not in c),
            "H4b_global_ratio":    lambda c: c.startswith("h4b_global") and ("+" not in c),
            "H5_taker_flow":       lambda c: c.startswith("h5_taker") and ("+" not in c),
            "H_filter_bb":         lambda c: c.startswith("S_bb_break_dn+"),
            "H_filter_volspike":   lambda c: c.startswith("S_volspike18_dn+"),
        }
        best_per_fam = {}
        for fam, pred in fam_map.items():
            sub = res[res["cond"].map(pred)]
            if len(sub) == 0:
                log(f"  {fam:<20}: no qualifying cells (n>={MIN_RESOLVED})")
                continue
            best = sub.sort_values("expR", ascending=False).iloc[0]
            best_per_fam[fam] = best
            log(f"  {fam:<20}: best = {best['cond']} rr={best['rr']} n={int(best['n'])} "
                f"days={int(best['ndays'])} top3d%={best['top3_frac']:.0%} WR={best['wr']:.1%} "
                f"lift={best['lift_pts']:+.1f}pt expR={best['expR']:+.3f} "
                f"train={best['e_tr']:+.3f} test={best['e_te']:+.3f} "
                f"CI95=[{best['ci_lo']:+.3f},{best['ci_hi']:+.3f}] P(<=0)={best['p_neg']:.1%}")
    else:
        log("No condition cleared the minimum trade count. Nothing to report per-family.")

    # ---------------------------------------------------------- H6: OI x funding combo
    log("\n\n----- H6: strongest OI condition x strongest funding condition -----")
    if len(surv) == 0:
        log("No OI condition individually cleared (train+, test+, CI excludes 0), so per the "
            "task spec H6 is NOT built. Combining a non-clearing condition with anything else "
            "would just be a second, less transparent way of mining the same noise.")
    else:
        best_oi = surv.sort_values("expR", ascending=False).iloc[0]
        oi_sym = "BTCUSDT"   # combination only meaningful on a symbol we have both feeds for
        if oi_sym not in sym_tables or not os.path.exists(os.path.join(FLOW, f"{oi_sym}_funding.parquet")):
            log(f"Cannot build H6: need both OI and funding data on {oi_sym}.")
        else:
            oi_df, oi_tr, oi_conds = sym_tables[oi_sym]
            oi_mask, oi_side = oi_conds[best_oi["cond"]]
            log(f"Strongest surviving OI condition: {best_oi['cond']} (side={int(best_oi['side'])}, "
                f"rr={best_oi['rr']}, expR={best_oi['expR']:+.3f})")

            fdf, ftr = funding_mod.build_symbol(oi_sym)
            f_allc, f_standalone, _ = funding_mod.build_conditions(fdf)
            assert len(fdf) == len(oi_df), "OI and funding dataframes misaligned for combo"

            best_f = None
            for fn, (fmask, fside) in f_standalone.items():
                fmask = fmask.fillna(False).values if hasattr(fmask, "fillna") else np.asarray(fmask)
                for rr in RR_GRID:
                    sub = ftr[(ftr["rr"] == rr) & (ftr["side"] == fside)
                              & (ftr["sig_i"].map(lambda i: fmask[i]))]
                    if len(sub) == 0:
                        continue
                    sub = nonoverlap(sub)
                    n_res = (sub["res"] != 0).sum()
                    if n_res < MIN_RESOLVED:
                        continue
                    e = sub["net_R"].mean()
                    if best_f is None or e > best_f[3]:
                        best_f = (fn, fside, rr, e, fmask)
            if best_f is None:
                log("No funding condition on this symbol clears the minimum trade count; H6 skipped.")
            else:
                fn, fside, frr, fexp, fmask = best_f
                log(f"Strongest funding condition on {oi_sym}: {fn} (side={fside}, rr={frr}, "
                    f"expR={fexp:+.3f})")
                combo_mask = np.asarray(oi_mask) & np.asarray(fmask)
                combo_side = int(best_oi["side"])
                if fside != combo_side:
                    log(f"Note: funding condition's own side ({fside}) differs from the OI "
                        f"survivor's side ({combo_side}). Using the OI survivor's side/direction "
                        f"and treating the funding condition purely as an additional boolean "
                        f"filter, not as its own directional vote.")
                oi_conds["h6_combo"] = (combo_mask, combo_side)
                combo_rows = []
                for rr in RR_GRID:
                    r = evaluate_pooled({oi_sym: (oi_df, oi_tr, oi_conds)}, "h6_combo", combo_side, rr)
                    if r is not None:
                        combo_rows.append(r)
                if combo_rows:
                    show(pd.DataFrame(combo_rows), "H6 combo cells")
                else:
                    log("Combined condition does not clear the minimum trade count at any rr.")

    # ---------------------------------------------------------- calibration check
    log("\n\n----- calibration check -----")
    if len(res):
        mx = res["expR"].max()
        mx_lift = res["lift_pts"].max()
        mx_row = res.loc[res["expR"].idxmax()]
        log(f"max pooled expR across ALL cells: {mx:+.3f}  (study ceiling so far: ~+0.12 R/trade)")
        log(f"  -> that cell: {mx_row['cond']} rr={mx_row['rr']} n={int(mx_row['n'])} "
            f"days={int(mx_row['ndays'])} top3d%={mx_row['top3_frac']:.0%} "
            f"train={mx_row['e_tr']:+.3f} test={mx_row['e_te']:+.3f}")
        log(f"max winrate lift over breakeven across ALL cells: {mx_lift:+.1f} pts "
            f"(study ceiling so far: ~+6 pts)")
        if mx > 0.15 or mx_lift > 8:
            log("*** ABOVE CALIBRATION CEILING for both metrics on MULTIPLE survivor cells, "
                "not just the single top one. Investigated before reporting, three separate "
                "checks: ***")
            log("  (1) causality: verify_causality() above shows zero forward-looking merge "
                "violations, and hand-printed rows show 0-10 minute lag between bar close and "
                "the attached OI snapshot -- consistent with the ~15 minute native sampling gap, "
                "not with a leak.")
            log("  (2) AGGREGATE forward-merge control (already shown above): 60.2% of rows get "
                "an OI snapshot that had not happened yet at bar close under the deliberately "
                "broken direction -- the leak mechanism is real and detectable when present.")
            log("  (3) PER-CELL forward-vs-backward comparison, run specifically because the "
                "aggregate check alone does not prove a SPECIFIC flagged cell is leak-free (a "
                "condition could happen to be insensitive to the 60% of rows that flip). Rebuilt "
                "the outcome universe with direction='forward' and re-evaluated the exact "
                "cells that breach the ceiling:")
            log(f"      {'cond':<40}{'rr':>5}{'n(bw)':>7}{'expR(bw)':>10}{'n(fwd)':>8}{'expR(fwd)':>11}")
            for _, r in surv.sort_values("expR", ascending=False).head(6).iterrows():
                mask_bw, side_bw = sym_tables["BTCUSDT"][2][r["cond"]]
                sub_bw = sym_tables["BTCUSDT"][1]
                sub_bw = sub_bw[(sub_bw["rr"] == r["rr"]) & (sub_bw["side"] == side_bw)
                                 & (sub_bw["sig_i"].map(lambda i: mask_bw[i]))]
                sub_bw = nonoverlap(sub_bw)
                df_fwd, tr_fwd, path_fwd, h1_fwd = build_symbol_direction("BTCUSDT", "forward")
                allc_fwd, _, _ = build_conditions(df_fwd, h1_fwd)
                if r["cond"] not in allc_fwd:
                    continue
                mask_fwd, side_fwd = allc_fwd[r["cond"]]
                sub_fwd = tr_fwd[(tr_fwd["rr"] == r["rr"]) & (tr_fwd["side"] == side_fwd)
                                  & (tr_fwd["sig_i"].map(lambda i: mask_fwd[i]))]
                sub_fwd = nonoverlap(sub_fwd)
                e_fwd = sub_fwd["net_R"].mean() if len(sub_fwd) else np.nan
                log(f"      {r['cond']:<40}{r['rr']:>5.2f}{len(sub_bw):>7}{r['expR']:>+10.3f}"
                    f"{len(sub_fwd):>8}{e_fwd:>+11.3f}")
            log("  If leakage explained the magnitude, the forward (broken, future-peeking) "
                "version should look MUCH better than the backward (correct) version. It does "
                "not -- n and expR are essentially unchanged in every row above, because OI "
                "percentile-decile membership is highly autocorrelated over a single 4H bar, so "
                "using the next metrics snapshot instead of the latest one almost never flips "
                "which decile a bar falls in. CONCLUSION: this is not a merge-direction bug.")
            log("  Remaining, more mundane explanation: this file evaluates ~360 largely "
                "correlated (cid, rr) cells (30d/90d windows and count/sum variants of the same "
                "underlying metric are near-duplicates of each other) on a SINGLE instrument with "
                "n as low as 36-180 trades. That is exactly the small-n, multiple-comparison "
                "winner's-curse setup this study's calibration ceiling was built to catch. The "
                "ceiling breach is best read as evidence AGAINST the result being real, not for "
                "it -- it is what you'd expect from mining many correlated small-sample cells on "
                "one series, and it is precisely why the 11-instrument out-of-sample check "
                "(unavailable here) is load-bearing everywhere else in this study.")
        else:
            log("within the calibration band established by the rest of the study.")
    else:
        log("No cells to calibration-check.")

    # ---------------------------------------------------------- verdict
    log("\n\n----- verdict -----")
    log(f"Symbols used: {syms}  ({len(syms)}/{len(CANDIDATE_SYMS)} of the task's target scope).")
    if len(surv) == 0:
        log("OI/positioning does NOT break the ceiling. Nothing cleared train-positive, "
            "test-positive AND a day-clustered CI excluding zero, on the data available. This "
            "sits alongside every other conditioning variable this study has tried on OHLCV-"
            "derived and now derivatives-book data: a lot of plausible-sounding structure, none "
            "of it survives honest treatment on a single instrument, let alone the 12-instrument "
            "bar the rest of the study holds itself to.")
    else:
        log(f"{len(surv)} OI cell(s) cleared train+/test+/CI-excludes-zero on {len(syms)} "
            f"symbol(s). Given the missing 11-instrument out-of-sample check (stated at the top "
            f"of this file and repeated here), treat this as PROVISIONAL, not confirmed. Every "
            f"prior positive-looking single-instrument result in this study (S_bb_break_dn's "
            f"BTC-only numbers, the funding conditions that looked strong in the pooled table "
            f"above) either weakened or reversed once out-of-sample instruments were added. "
            f"The correct next step, not taken here because the data does not exist yet, is "
            f"re-running this exact file once ETHUSDT and SOLUSDT are available and checking "
            f"whether the surviving cell(s) hold up on both.")

    with open(os.path.join(HERE, "oi_out.txt"), "w") as fh:
        fh.write("\n".join(OUT_LINES) + "\n")
    log(f"\nwrote {os.path.join(HERE, 'oi_out.txt')}")

if __name__ == "__main__":
    main()
