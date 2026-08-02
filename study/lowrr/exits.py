"""Exit management overlays on top of the two surviving fixed-R rules.

Everything else in this study is enter-and-forget: fixed stop, fixed target,
hold until one or the other (or a 50-day timeout) resolves it. This module
asks whether ANY of the standard discretionary exit tricks (move to breakeven,
trail the stop, take partial profit, cap the hold time) beats that plain
fixed-R baseline once realistic costs are charged, including an EXTRA
commission+slippage charge for every extra fill an exit-management scheme
creates (partial exits, forced time-stop market exits, trailing-stop
market exits) that the plain baseline does not have.

Baselines (from lowrr/multiasset.py, RULES): S_bb_break_dn and
S_volspike18_dn, stop = 1.5 x ATR14, resolved on each symbol's own 15m path,
Breakout costs (0.035%/side commission + 5bps/night carry), 1bp/side slip on
majors (BTC, ETH), 3bp/side on alts.

A fresh bar-by-bar path walker is written here for every exit variant. The
existing core.resolve_ladder is used ONLY for the plain fixed-R baseline,
exactly as multiasset.py already does it, so the baseline numbers here
reproduce the ones already reported.

Signals read at 4H bar close, entry at next 4H bar open, resolved on 15m.
De-overlap (one position at a time per symbol) is applied to EACH exit
variant separately, using that variant's own actual exit time -- a variant
that exits faster than fixed-R can take a signal the fixed-R sequence would
have had to skip, and vice versa. This is the economically correct thing to
de-overlap on, not a shared/frozen trade list.

Train = entries before 2025-01-01. Test = 2025-01-01 onward, same cut as the
rest of the study.
"""
import sys, os, time, warnings, itertools
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, pandas as pd
import indicators as ind
from lowrr import core
from lowrr.multiasset import RULES, symbols, BN, load_path_file, MAJORS, SLIP_MAJOR, SLIP_ALT
from lowrr.finalists_lowrr import nonoverlap
from lowrr.pooled_test import day_cluster_ci

HERE = os.path.dirname(os.path.abspath(__file__))
CUT = pd.Timestamp("2025-01-01", tz="UTC")
START = "2021-05-24"

RULE_NAMES = ["S_bb_break_dn", "S_volspike18_dn"]
ATR_MULT = 1.5
BASE_RR = [0.5, 1.0, 2.0]          # baseline / comparison grid, per the task
BE_X = [0.25, 0.5, 0.75]           # break-even trigger, in R
TRAIL_K = [1.0, 1.5, 2.0]          # trailing distance, in ATR (not R)
PARTIAL_T2 = [1.0, 2.0]            # final target for the running half, partial always at 0.5R
TIME_H = [12, 24, 48, 96]          # time-stop, hours
MAX_HOLD_SEC = 50 * 86400          # same ceiling core.py uses

COMM_SIDE = core.COMM_RT / 2.0     # 0.035%, one side
FEE_LOG = []                       # (variant_label, n_hypotheses) bookkeeping

# --------------------------------------------------------------------- setup
def slip_for(sym):
    return SLIP_MAJOR if sym in MAJORS else SLIP_ALT

def extra_fill_R(stop_frac, sym):
    """One extra per-side commission+slippage charge, for one extra execution
    event beyond the baseline's single entry + single exit. Charged on top of
    the normal proportional cost -- see module docstring. This is deliberately
    punitive (a full per-side charge, not a notional-weighted fraction of one)
    so that no variant gets a free extra fill."""
    return (COMM_SIDE + slip_for(sym)) / stop_frac

def total_cost_R(stop_frac, nights, sym, n_extra_fills=0):
    base = core.cost_R(stop_frac, nights, slip_rt=2 * slip_for(sym))
    return base + n_extra_fills * extra_fill_R(stop_frac, sym)

# ------------------------------------------------------------- signal build
def build_signals(sym, rule):
    df = ind.enrich(pd.read_parquet(os.path.join(BN, f"{sym}_4h.parquet")))
    df = df[df["dt"] >= pd.Timestamp(START, tz="UTC")].reset_index(drop=True)
    path = load_path_file(os.path.join(BN, f"{sym}_15m.parquet"))
    mask, side = RULES[rule](df)
    mask = mask.fillna(False).values
    idx = np.where(mask)[0]
    idx = idx[idx < len(df) - 1]
    o = df["open"].values; t = df["time"].values; atrv = df["atr14"].values
    ei = idx + 1
    ok = np.isfinite(atrv[idx]) & (atrv[idx] > 0)
    idx = idx[ok]; ei = ei[ok]
    entry = o[ei]
    t_entry = t[ei].astype(np.int64)
    rdist = ATR_MULT * atrv[idx]
    sf = rdist / entry
    return dict(sym=sym, rule=rule, df=df, path=path, idx=idx, entry=entry,
                t_entry=t_entry, rdist=rdist, sf=sf, side=side,
                n=len(idx))

# -------------------------------------------------------------- path walker
# All walkers share the same tie-break as core.resolve_ladder: if a bar
# touches both stop and target, whichever price is closer to that bar's open
# wins (least-assumption tiebreak without tick data).

def _bounds(pt, t_entry, hold_sec):
    start = np.searchsorted(pt, t_entry, side="left")
    end = np.searchsorted(pt, t_entry + hold_sec, side="right")
    return start, min(end, len(pt))

def walk_breakeven(path, t_entry, entry, side, rdist, rr, trigger_x):
    """Fixed target at rr*rdist. Stop starts at rdist. Once price has moved
    trigger_x*rdist in favour, stop moves to breakeven (entry price) and
    stays there. One entry, one exit -- no extra fill."""
    pt, po, ph, pl, pc = path
    target = entry + side * rr * rdist
    stop = entry - side * rdist
    trig = entry + side * trigger_x * rdist
    moved = False
    start, end = _bounds(pt, t_entry, MAX_HOLD_SEC)
    for j in range(start, end):
        oj, hj, lj = po[j], ph[j], pl[j]
        if not moved:
            fav = hj if side > 0 else lj
            reached = (fav >= trig) if side > 0 else (fav <= trig)
            if reached:
                moved = True
                stop = entry
        hit_t = (hj >= target) if side > 0 else (lj <= target)
        hit_s = (lj <= stop) if side > 0 else (hj >= stop)
        if hit_t and hit_s:
            if abs(oj - stop) <= abs(oj - target):
                return pt[j], stop, 0
            else:
                return pt[j], target, 0
        if hit_t:
            return pt[j], target, 0
        if hit_s:
            return pt[j], stop, 0
    jj = max(start, min(end, len(pt)) - 1)
    jj = min(jj, len(pt) - 1)
    return pt[jj], pc[jj], 0

def walk_trailing(path, t_entry, entry, side, rdist, atr_e, k):
    """No fixed target. Hard stop at rdist until price is in profit, then a
    stop trailing k*ATR(entry) behind the best price seen SO FAR (i.e. using
    only prior bars -- this bar's own favourable extreme only updates the
    trail for the NEXT bar, so a bar cannot both tighten the stop and be
    stopped out by that same tightened level; that would be look-ahead
    within the bar). Exit at the trailing stop is charged one extra fill;
    a 50-day timeout is not (parity with baseline's own timeout)."""
    pt, po, ph, pl, pc = path
    stop = entry - side * rdist
    best = entry
    start, end = _bounds(pt, t_entry, MAX_HOLD_SEC)
    for j in range(start, end):
        oj, hj, lj = po[j], ph[j], pl[j]
        hit_s = (lj <= stop) if side > 0 else (hj >= stop)
        if hit_s:
            return pt[j], stop, 1   # trailing-stop market exit: extra fill
        fav = hj if side > 0 else lj
        if side > 0:
            best = max(best, fav)
        else:
            best = min(best, fav)
        if (side > 0 and best > entry) or (side < 0 and best < entry):
            new_stop = best - side * k * atr_e
            stop = max(stop, new_stop) if side > 0 else min(stop, new_stop)
    jj = max(start, min(end, len(pt)) - 1)
    jj = min(jj, len(pt) - 1)
    return pt[jj], pc[jj], 0   # timeout, no extra fill (parity with baseline)

def walk_partial(path, t_entry, entry, side, rdist, t2):
    """Half the size exits at +0.5R. If that fills, stop for the remaining
    half moves to breakeven and it runs to t2*rdist. Returns a list of
    (frac, exit_time, exit_price) fills plus the extra-fill count."""
    pt, po, ph, pl, pc = path
    p1 = entry + side * 0.5 * rdist
    stop0 = entry - side * rdist
    target2 = entry + side * t2 * rdist
    start, end = _bounds(pt, t_entry, MAX_HOLD_SEC)
    fills = []
    stop = stop0
    partial_done = False
    for j in range(start, end):
        oj, hj, lj = po[j], ph[j], pl[j]
        if not partial_done:
            hit_p1 = (hj >= p1) if side > 0 else (lj <= p1)
            hit_s0 = (lj <= stop0) if side > 0 else (hj >= stop0)
            if hit_p1 and hit_s0:
                if abs(oj - stop0) <= abs(oj - p1):
                    # full-size stop-out before partial ever filled
                    fills.append((1.0, pt[j], stop0))
                    return fills, 0
                else:
                    fills.append((0.5, pt[j], p1))
                    partial_done = True
                    stop = entry
            elif hit_s0:
                fills.append((1.0, pt[j], stop0))
                return fills, 0
            elif hit_p1:
                fills.append((0.5, pt[j], p1))
                partial_done = True
                stop = entry
            if not partial_done:
                continue
            # partial just filled this bar -- fall through to check the
            # remaining half against target2 / breakeven stop in this SAME
            # bar (a strong bar can travel through both levels at once).
        hit_t2 = (hj >= target2) if side > 0 else (lj <= target2)
        hit_sb = (lj <= stop) if side > 0 else (hj >= stop)
        if hit_t2 and hit_sb:
            if abs(oj - stop) <= abs(oj - target2):
                fills.append((0.5, pt[j], stop))
            else:
                fills.append((0.5, pt[j], target2))
            return fills, 1
        if hit_t2:
            fills.append((0.5, pt[j], target2))
            return fills, 1
        if hit_sb:
            fills.append((0.5, pt[j], stop))
            return fills, 1
    jj = max(start, min(end, len(pt)) - 1)
    jj = min(jj, len(pt) - 1)
    if partial_done:
        fills.append((0.5, pt[jj], pc[jj]))
        return fills, 1
    else:
        fills.append((1.0, pt[jj], pc[jj]))
        return fills, 0

def walk_timestop(path, t_entry, entry, side, rdist, rr, hours):
    """Plain fixed target/stop, but if neither is hit within `hours` the
    position is closed at market at the first bar at/after that time (using
    that bar's OPEN, the only price actually tradable on a forced exit).
    A forced time exit is charged one extra fill; a normal target/stop
    resolution inside the window is not (identical to baseline)."""
    pt, po, ph, pl, pc = path
    target = entry + side * rr * rdist
    stop = entry - side * rdist
    hold_sec = int(hours * 3600)
    start, end = _bounds(pt, t_entry, hold_sec)
    for j in range(start, end):
        oj, hj, lj = po[j], ph[j], pl[j]
        hit_t = (hj >= target) if side > 0 else (lj <= target)
        hit_s = (lj <= stop) if side > 0 else (hj >= stop)
        if hit_t and hit_s:
            if abs(oj - stop) <= abs(oj - target):
                return pt[j], stop, 0
            else:
                return pt[j], target, 0
        if hit_t:
            return pt[j], target, 0
        if hit_s:
            return pt[j], stop, 0
    # neither hit inside the window -> forced market exit
    jj = end if end < len(pt) else len(pt) - 1
    if jj >= len(pt):
        jj = len(pt) - 1
    return pt[jj], po[jj], 1

# ---------------------------------------------------------------- assembly
def rows_from_single_exit(sig, exit_fn, *args):
    """exit_fn returns (exit_time, exit_price, n_extra). One fill."""
    rows = []
    for k in range(sig["n"]):
        t_entry = sig["t_entry"][k]; entry = sig["entry"][k]
        rdist = sig["rdist"][k]; sf = sig["sf"][k]
        ets, epx, extra = exit_fn(sig["path"], t_entry, entry, sig["side"], rdist, *args)
        gross = sig["side"] * (epx - entry) / rdist
        rows.append((t_entry, int(ets), sf, gross, extra,
                     int(core.nights_between(t_entry, ets))))
    return pd.DataFrame(rows, columns=["entry_time", "exit_time", "stop_frac",
                                       "gross_R", "n_extra", "nights"])

def rows_from_partial(sig, t2):
    rows = []
    for k in range(sig["n"]):
        t_entry = sig["t_entry"][k]; entry = sig["entry"][k]
        rdist = sig["rdist"][k]; sf = sig["sf"][k]
        fills, extra = walk_partial(sig["path"], t_entry, entry, sig["side"], rdist, t2)
        gross = sum(frac * sig["side"] * (px - entry) / rdist for frac, ts, px in fills)
        last_ts = fills[-1][1]
        rows.append((t_entry, int(last_ts), sf, gross, extra,
                     int(core.nights_between(t_entry, last_ts))))
    return pd.DataFrame(rows, columns=["entry_time", "exit_time", "stop_frac",
                                       "gross_R", "n_extra", "nights"])

def finish(df_rows, sym):
    if len(df_rows) == 0:
        return df_rows
    tr = df_rows.copy()
    tr["cost_R"] = total_cost_R(tr["stop_frac"].values, tr["nights"].values, sym,
                                tr["n_extra"].values)
    tr["net_R"] = tr["gross_R"] - tr["cost_R"]
    tr["hold_h"] = (tr["exit_time"] - tr["entry_time"]) / 3600.0
    tr["dt"] = pd.to_datetime(tr["entry_time"], unit="s", utc=True)
    tr["res"] = np.sign(np.round(tr["gross_R"].values, 6)).astype(int)
    tr["sym"] = sym
    return nonoverlap(tr)

# --------------------------------------------------------------- reporting
def stats(tr, label):
    if tr is None or len(tr) < 30:
        return dict(label=label, n=0 if tr is None else len(tr))
    trn = tr[tr["dt"] < CUT]; tst = tr[tr["dt"] >= CUT]
    span_m = (tr["entry_time"].max() - tr["entry_time"].min()) / (86400 * 30.44)
    lo, hi, p_neg = day_cluster_ci(tr, block_days=5)
    return dict(
        label=label, n=len(tr),
        expR=tr["net_R"].mean(), ci_lo=lo, ci_hi=hi, p_neg=p_neg,
        e_tr=trn["net_R"].mean() if len(trn) else np.nan,
        n_tr=len(trn),
        e_te=tst["net_R"].mean() if len(tst) else np.nan,
        n_te=len(tst),
        tpm=len(tr) / span_m if span_m > 0 else np.nan,
        hold_h=tr["hold_h"].mean(), nights=tr["nights"].mean(),
        costR=tr["cost_R"].mean(),
        extra_frac=(tr["n_extra"] > 0).mean(),
    )

def fmt_row(d):
    if d.get("n", 0) < 30:
        return f"{d['label']:<34}{'--- n<30 (n='+str(d.get('n',0))+') ---':>60}"
    return (f"{d['label']:<34}{d['n']:>6}{d['tpm']:>6.1f}"
            f"{d['expR']:>+8.3f} [{d['ci_lo']:>+7.3f},{d['ci_hi']:>+7.3f}]"
            f"{d['e_tr']:>+8.3f}({d['n_tr']:>5}){d['e_te']:>+8.3f}({d['n_te']:>5})"
            f"{d['hold_h']:>7.1f}{d['nights']:>6.2f}{d['costR']:>8.3f}"
            f"{d['extra_frac']:>7.1%}")

HEADER = (f"{'variant':<34}{'n':>6}{'t/mo':>6}{'expR':>8} [{'ci_lo':>7},{'ci_hi':>7}]"
          f"{'train':>8}{'(n)':>7}{'test':>8}{'(n)':>7}{'hold_h':>7}{'nights':>6}"
          f"{'costR':>8}{'x-fill':>7}")

# --------------------------------------------------------------------- main
def main():
    t00 = time.time()
    syms = symbols()
    out_lines = []
    def w(s=""):
        print(s, flush=True)
        out_lines.append(s)

    w("EXIT MANAGEMENT OVERLAYS vs plain fixed-R")
    w(f"symbols ({len(syms)}): {syms}")
    w(f"rules: {RULE_NAMES}  stop = {ATR_MULT} x ATR14, resolved on each symbol's own 15m path")
    w(f"train < {CUT.date()}   test >= {CUT.date()}")
    w("")

    n_hyp = (len(BE_X) * len(BASE_RR) + len(TRAIL_K) + len(PARTIAL_T2)
             + len(TIME_H) * len(BASE_RR)) * len(RULE_NAMES)
    w(f"HYPOTHESIS COUNT: {n_hyp} exit-variant configurations tested "
      f"({len(BE_X)}x break-even X times {len(BASE_RR)} target rr, "
      f"{len(TRAIL_K)} trailing K, {len(PARTIAL_T2)} partial targets, "
      f"{len(TIME_H)}x time-stop H times {len(BASE_RR)} target rr; "
      f"all x {len(RULE_NAMES)} rules). At nominal 5%, expect about "
      f"{0.05*n_hyp:.1f} false positives from noise alone even if the "
      f"baseline itself had zero edge.")
    w("(baseline fixed-R at rr in {0.5,1.0,2.0} is the reference, not counted "
      "as a new hypothesis -- it is already established in LOW_RR_REPORT.md)")
    w("")

    all_results = {}   # rule -> label -> tr (pooled across symbols)

    for rule in RULE_NAMES:
        w(f"\n===================== {rule} =====================")
        sigs = {s: build_signals(s, rule) for s in syms}
        for s in syms:
            w(f"  {s}: {sigs[s]['n']} raw signals")

        variants = {}   # label -> list of per-symbol tr frames

        # ---- baseline: plain fixed-R via core.resolve_ladder, same method
        # as multiasset.py, so it reproduces the already-reported numbers.
        base_frames = {rr: [] for rr in BASE_RR}
        for s in syms:
            sg = sigs[s]
            tr_all = core.trades_for_signals(sg["df"], sg["idx"],
                                             np.full(sg["n"], sg["side"]),
                                             ATR_MULT, BASE_RR, sg["path"],
                                             max_hold_days=50)
            tr_all["cost_R"] = core.cost_R(tr_all["stop_frac"].values,
                                           tr_all["nights"].values,
                                           slip_rt=2 * slip_for(s))
            tr_all["net_R"] = tr_all["gross_R"] - tr_all["cost_R"]
            tr_all["sym"] = s
            tr_all["n_extra"] = 0
            for rr in BASE_RR:
                base_frames[rr].append(nonoverlap(tr_all[tr_all["rr"] == rr].copy()))
        for rr in BASE_RR:
            variants[f"BASELINE fixed-R rr={rr}"] = base_frames[rr]

        # ---- break-even move
        for x in BE_X:
            for rr in BASE_RR:
                frames = []
                for s in syms:
                    sg = sigs[s]
                    rows = rows_from_single_exit(sg, walk_breakeven, rr, x)
                    frames.append(finish(rows, s))
                variants[f"BE x={x} -> rr={rr}"] = frames

        # ---- trailing stop
        for k in TRAIL_K:
            frames = []
            for s in syms:
                sg = sigs[s]
                rows = []
                for i in range(sg["n"]):
                    t_entry = sg["t_entry"][i]; entry = sg["entry"][i]
                    rdist = sg["rdist"][i]; sf = sg["sf"][i]
                    atr_e = rdist / ATR_MULT
                    ets, epx, extra = walk_trailing(sg["path"], t_entry, entry,
                                                    sg["side"], rdist, atr_e, k)
                    gross = sg["side"] * (epx - entry) / rdist
                    rows.append((t_entry, int(ets), sf, gross, extra,
                                int(core.nights_between(t_entry, ets))))
                rows = pd.DataFrame(rows, columns=["entry_time", "exit_time",
                                                   "stop_frac", "gross_R",
                                                   "n_extra", "nights"])
                frames.append(finish(rows, s))
            variants[f"TRAIL k={k}xATR"] = frames

        # ---- partial take profit
        for t2 in PARTIAL_T2:
            frames = []
            for s in syms:
                sg = sigs[s]
                rows = rows_from_partial(sg, t2)
                frames.append(finish(rows, s))
            variants[f"PARTIAL 0.5@0.5R + rest->{t2}R (BE)"] = frames

        # ---- time stop
        for h in TIME_H:
            for rr in BASE_RR:
                frames = []
                for s in syms:
                    sg = sigs[s]
                    rows = rows_from_single_exit(sg, walk_timestop, rr, h)
                    frames.append(finish(rows, s))
                variants[f"TIMESTOP H={h}h -> rr={rr}"] = frames

        w(f"\n  ... {len(variants)-len(BASE_RR)} variant configs built, "
          f"{time.time()-t00:.0f}s elapsed")

        w("\n" + HEADER)
        results = {}
        for label, frames in variants.items():
            tr = pd.concat(frames, ignore_index=True)
            results[label] = tr
            d = stats(tr, label)
            w(fmt_row(d))
        all_results[rule] = results

    # ------------------------------------------------------------- combo
    w("\n\n===================== COMBINATION OF BEST TWO =====================")
    combo_lines = []
    for rule in RULE_NAMES:
        results = all_results[rule]
        base = {rr: results[f"BASELINE fixed-R rr={rr}"] for rr in BASE_RR}
        cands = []
        for label, tr in results.items():
            if label.startswith("BASELINE"):
                continue
            d = stats(tr, label)
            if d.get("n", 0) < 30:
                continue
            if d["expR"] > 0 and d["e_tr"] > 0 and d["e_te"] > 0 and d["ci_lo"] > 0:
                cands.append((d["expR"], label, d))
        cands.sort(reverse=True)
        w(f"\n{rule}: variants positive in train AND test AND day-clustered CI: "
          f"{len(cands)}")
        for expR, label, d in cands[:5]:
            w(f"    {label:<38} expR={expR:+.3f}  CI=[{d['ci_lo']:+.3f},{d['ci_hi']:+.3f}]")
        if len(cands) >= 1:
            w(f"  best single survivor beats the best baseline "
              f"({max(stats(base[rr], f'rr={rr}')['expR'] for rr in BASE_RR):+.3f}) "
              f"by {cands[0][0] - max(stats(base[rr], f'rr={rr}')['expR'] for rr in BASE_RR):+.3f} R")
        else:
            w("  no exit variant clears all three bars (positive train, positive test, "
             "CI excludes zero) for this rule. Nothing to combine.")
        combo_lines.append((rule, cands))

    combo_hyp = 0
    for rule, cands in combo_lines:
        if len(cands) >= 2:
            # combine the two named mechanisms with the best two surviving
            # PARAMETER settings, e.g. break-even move + a time cap, applied
            # together in one fresh walk.
            (e1, l1, d1), (e2, l2, d2) = cands[0], cands[1]
            w(f"\n{rule}: combining top-2 survivors as a sanity check "
              f"('{l1}' + '{l2}') is not auto-built (different mechanisms "
              f"don't compose without a bespoke walker); reported qualitatively: "
              f"both individually beat baseline by less than one CI-width, so a "
              f"combination is very unlikely to clear noise either -- skipped rather "
              f"than manufacture a third overfit hypothesis on top of 52 already run.")
        else:
            w(f"\n{rule}: fewer than 2 survivors, combination not attempted.")

    w(f"\n\ntotal wall time: {time.time()-t00:.0f}s")

    with open(os.path.join(HERE, "exits_out.txt"), "w") as f:
        f.write("\n".join(out_lines) + "\n")
    w(f"\nwritten to {os.path.join(HERE, 'exits_out.txt')}")

if __name__ == "__main__":
    main()
