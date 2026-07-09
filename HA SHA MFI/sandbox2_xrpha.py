"""SANDBOX backtest: XRP HA/SHA/MFI trend continuation, CANDIDATE 2 (convergence rule).

Implements FROZEN_SPEC_XRPHA.md "CANDIDATE 2: convergence rule" section exactly,
SANDBOX segment only (2020-01-06 through 2023-12-31; the VALIDATION segment
2024-01-01 onward is untouched by this script -- truncated immediately after
load and never referenced again). No optimization, no tuning; the rule and
cost model are frozen before this file ever ran.

This file is derived from sandbox_xrpha.py (candidate 1). Entry resolution,
path walk (resolve_exit), cost arithmetic, block() stats, sanity checks, report
structure, and the hard sandbox truncation (time < 2024-01-01 UTC) are kept
EXACTLY as in candidate 1. ONLY the signal-generation logic (generate_and_resolve)
differs, plus output file paths, plus a new census split (path_old vs path_new)
and a fourth sanity check (d) cross-referencing candidate 1's entries.

Signal generation (see FROZEN_SPEC_XRPHA.md "CANDIDATE 2" section):
  Window: bars r+1, r+2, r+3 after the most recent red HA bar r (long side;
  short side mirrored off the most recent green HA bar). Setup completes at
  the first bar t in the window such that: (1) some bar k in the window with
  k <= t was a momentum candle (green, no lower wick) with mfi[k] > 0 --
  MFI is evaluated ON the momentum bar k, not on t; (2) SHA is bullish at t
  (sha_close[t] > sha_open[t]); (3) bar t's HA candle is green (strict); (4)
  the window is not yet consumed by an actual entry. When t == k this reduces
  exactly to candidate 1. A red bar cannot complete a long setup (must be
  green), so the anchor-move-at-end-of-bar-t timing (identical to candidate 1)
  never lets an in-progress completion get missed.

  Implementation: armed_long is tracked per current long window, set True the
  first time a bar in the window is a momentum-candle-with-mfi>0 bar, and
  reset to False whenever the window anchor (last_red) moves. At each bar t
  in the window, armed_long is updated first (using bar t's own momentum/mfi
  status), then the completion test (armed_long AND green[t] AND sha bullish
  at t AND not consumed) is evaluated using the just-updated armed_long, so a
  bar that is simultaneously the momentum bar and the completion bar (t == k)
  is handled correctly in one pass. Shorts fully mirrored.

Bar indices used for "the window" and "the next bar" (entry bar t+1) are
POSITIONAL indices into the truncated, gate0-merged/deduped/sorted 15m series,
identical convention to candidate 1 (see that file's docstring for the full
ambiguity discussion; sanity check (a) below quantifies it for this run).
"""
import os
import subprocess
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "audit"))
from phase1 import half_label, streaks  # noqa: E402

COMMISSION_RT = 0.0008          # 0.08% round trip
SWAP_PER_4H = 0.000055          # 0.0055% per 4h UTC boundary crossed while open
BASELINE_SLIP = 0.0001          # 1 bp per fill, baseline
MIN_STOP_PCT = 0.006            # 0.6% of entry
WICK_TOL = 1e-9                 # relative float tolerance on "no wick"

PARQUET_PATH = os.path.join(HERE, "xrpha_15m.parquet")
GATE0_SCRIPT = os.path.join(HERE, "gate0_xrpha.py")
SANDBOX_CUT = int(pd.Timestamp("2024-01-01T00:00:00", tz="UTC").timestamp())
CSV_PATH = os.path.join(HERE, "sandbox2_trades.csv")
REPORT_PATH = os.path.join(HERE, "SANDBOX2_XRPHA_REPORT.md")
CANDIDATE1_CSV_PATH = os.path.join(HERE, "sandbox_trades.csv")

REPORT_LINES = []


def log(msg: str = "") -> None:
    print(msg)
    REPORT_LINES.append(msg)


# ── load ──────────────────────────────────────────────────────────────────

def load_sandbox():
    if not os.path.exists(PARQUET_PATH):
        print(f"{PARQUET_PATH} missing, regenerating via gate0_xrpha.py ...")
        subprocess.run([sys.executable, GATE0_SCRIPT], check=True, cwd=HERE)
    df = pd.read_parquet(PARQUET_PATH)
    df = df.sort_values("time").reset_index(drop=True)
    df = df[df["time"] < SANDBOX_CUT].reset_index(drop=True)
    assert df["time"].max() < SANDBOX_CUT, "sandbox truncation failed"
    return df


# ── signal generation (CANDIDATE 2 convergence rule) + entry resolution ────
# (single causal pass) ───────────────────────────────────────────────────────

def generate_and_resolve(df):
    """Single left-to-right pass implementing the candidate 2 convergence
    rule. Returns (census: dict, raw_trades: list of dicts with
    t_signal/direction/e/entry/stop/stop_d/target/sgn/t_momentum/path)."""
    ha_o = df["port_ha_open"].to_numpy(float)
    ha_h = df["port_ha_high"].to_numpy(float)
    ha_l = df["port_ha_low"].to_numpy(float)
    ha_c = df["port_ha_close"].to_numpy(float)
    sha_o = df["port_sha_open"].to_numpy(float)
    sha_c = df["port_sha_close"].to_numpy(float)
    mfi = df["port_mfi_real"].to_numpy(float)
    real_o = df["open"].to_numpy(float)
    real_l = df["low"].to_numpy(float)
    real_h = df["high"].to_numpy(float)
    n = len(df)

    red = ha_c < ha_o
    green = ha_c > ha_o
    doji = ~red & ~green

    mom_long = green & (ha_l >= ha_o - WICK_TOL * ha_o)
    mom_short = red & (ha_h <= ha_o + WICK_TOL * ha_o)

    long_mfi_ok = mfi > 0
    long_sha_ok = sha_c > sha_o
    short_mfi_ok = mfi < 0
    short_sha_ok = sha_c < sha_o

    mom_long_mfi = mom_long & long_mfi_ok      # long momentum bar with mfi>0
    mom_short_mfi = mom_short & short_mfi_ok   # short momentum bar with mfi<0

    census = dict(
        bars=n, red=int(red.sum()), green=int(green.sum()), doji=int(doji.sum()),
        mom_long=int(mom_long.sum()), mom_short=int(mom_short.sum()),
        mfi_long_bars=0, sha_long_bars=0, momwin_long_bars=0, joint_long_bars=0,
        mfi_short_bars=0, sha_short_bars=0, momwin_short_bars=0, joint_short_bars=0,
        signals_long=0, signals_short=0,
        entries_long=0, entries_short=0,
        skipped_min_stop_long=0, skipped_min_stop_short=0,
        skipped_degenerate_long=0, skipped_degenerate_short=0,
        skipped_no_next_bar_long=0, skipped_no_next_bar_short=0,
        entries_long_old=0, entries_long_new=0,
        entries_short_old=0, entries_short_new=0,
    )

    last_red, last_green = None, None
    long_consumed, short_consumed = False, False
    armed_long, armed_short = False, False
    armed_long_bar, armed_short_bar = None, None
    raw_trades = []

    for t in range(n):
        in_long_win = last_red is not None and 1 <= (t - last_red) <= 3
        in_short_win = last_green is not None and 1 <= (t - last_green) <= 3

        # census bar counts kept identical in spirit to candidate 1 (unconditional
        # filter counts, plus in-window momentum count) for comparability.
        if long_mfi_ok[t]:
            census["mfi_long_bars"] += 1
        if long_sha_ok[t]:
            census["sha_long_bars"] += 1
        if mom_long[t] and in_long_win:
            census["momwin_long_bars"] += 1

        # ── LONG side: candidate 2 convergence logic ──
        if in_long_win:
            if mom_long_mfi[t]:
                if not armed_long:
                    armed_long = True
                    armed_long_bar = t
            long_joint = armed_long and green[t] and long_sha_ok[t]
            if long_joint:
                census["joint_long_bars"] += 1
                if not long_consumed:
                    census["signals_long"] += 1
                    e = t + 1
                    if e >= n:
                        census["skipped_no_next_bar_long"] += 1
                    else:
                        entry = real_o[e]
                        stop = real_l[t]
                        stop_d = entry - stop
                        if stop_d <= 0:
                            census["skipped_degenerate_long"] += 1
                        elif stop_d < MIN_STOP_PCT * entry:
                            census["skipped_min_stop_long"] += 1
                        else:
                            census["entries_long"] += 1
                            path = "old" if t == armed_long_bar else "new"
                            if path == "old":
                                census["entries_long_old"] += 1
                            else:
                                census["entries_long_new"] += 1
                            long_consumed = True
                            raw_trades.append(dict(
                                direction="long", t_signal=t, e=e, sgn=1,
                                entry=entry, stop=stop, stop_d=stop_d,
                                target=entry + 2 * stop_d,
                                t_momentum=armed_long_bar, path=path,
                                anchor=last_red))
        else:
            # not in window: armed_long carries no meaning until a window exists
            pass

        if short_mfi_ok[t]:
            census["mfi_short_bars"] += 1
        if short_sha_ok[t]:
            census["sha_short_bars"] += 1
        if mom_short[t] and in_short_win:
            census["momwin_short_bars"] += 1

        # ── SHORT side: candidate 2 convergence logic (mirrored) ──
        if in_short_win:
            if mom_short_mfi[t]:
                if not armed_short:
                    armed_short = True
                    armed_short_bar = t
            short_joint = armed_short and red[t] and short_sha_ok[t]
            if short_joint:
                census["joint_short_bars"] += 1
                if not short_consumed:
                    census["signals_short"] += 1
                    e = t + 1
                    if e >= n:
                        census["skipped_no_next_bar_short"] += 1
                    else:
                        entry = real_o[e]
                        stop = real_h[t]
                        stop_d = stop - entry
                        if stop_d <= 0:
                            census["skipped_degenerate_short"] += 1
                        elif stop_d < MIN_STOP_PCT * entry:
                            census["skipped_min_stop_short"] += 1
                        else:
                            census["entries_short"] += 1
                            path = "old" if t == armed_short_bar else "new"
                            if path == "old":
                                census["entries_short_old"] += 1
                            else:
                                census["entries_short_new"] += 1
                            short_consumed = True
                            raw_trades.append(dict(
                                direction="short", t_signal=t, e=e, sgn=-1,
                                entry=entry, stop=stop, stop_d=stop_d,
                                target=entry - 2 * stop_d,
                                t_momentum=armed_short_bar, path=path,
                                anchor=last_green))

        # window anchor moves at END of bar t processing (as candidate 1 does);
        # a new red bar starts a fresh long window and un-arms it (momentum
        # bars from an older window do not carry into the new one). Mirrored
        # for shorts off green bars.
        if red[t]:
            last_red = t
            long_consumed = False
            armed_long = False
            armed_long_bar = None
        if green[t]:
            last_green = t
            short_consumed = False
            armed_short = False
            armed_short_bar = None

    raw_trades.sort(key=lambda r: r["e"])
    return census, raw_trades


# ── path walk (mirrors audit_volspike.simulate()'s bar walk exactly, ───────
# unchanged from candidate 1) ────────────────────────────────────────────────

def resolve_exit(o, h, l, c, t_arr, e, sgn, entry, stop, target, stop_d, n):
    """Walk from entry bar e to the end of the sandbox array. Returns
    (gross_r, x_bar, exit_reason)."""
    for b in range(e, n):
        gap_sl = (o[b] <= stop) if sgn > 0 else (o[b] >= stop)
        gap_tp = (o[b] >= target) if sgn > 0 else (o[b] <= target)
        if b == e:
            gap_sl = gap_tp = False
        hit_sl = (l[b] <= stop) if sgn > 0 else (h[b] >= stop)
        hit_tp = (h[b] >= target) if sgn > 0 else (l[b] <= target)
        if gap_sl or gap_tp:
            px = o[b]
            gross = sgn * (px - entry) / stop_d
            reason = "gap_sl" if gap_sl else "gap_tp"
            return gross, b, reason
        if hit_sl and hit_tp:
            return -1.0, b, "sl_tp_ambiguous_worstcase_sl"
        if hit_sl:
            return -1.0, b, "sl"
        if hit_tp:
            return 2.0, b, "tp"
    gross = sgn * (c[n - 1] - entry) / stop_d
    return gross, n - 1, "open_at_end"


def simulate(df, raw_trades, slip=BASELINE_SLIP, swap=SWAP_PER_4H):
    o = df["open"].to_numpy(float)
    h = df["high"].to_numpy(float)
    l = df["low"].to_numpy(float)
    c = df["close"].to_numpy(float)
    t_arr = df["time"].to_numpy()
    n = len(df)
    trades = []
    for r in raw_trades:
        gross, x, reason = resolve_exit(
            o, h, l, c, t_arr, r["e"], r["sgn"], r["entry"], r["stop"],
            r["target"], r["stop_d"], n)
        n_swaps = int(t_arr[x] // 14400) - int(t_arr[r["e"]] // 14400)
        cost_r = (COMMISSION_RT + 2 * slip + n_swaps * swap) * r["entry"] / r["stop_d"]
        trades.append(dict(
            direction=r["direction"], t_signal=t_arr[r["t_signal"]],
            t_entry=t_arr[r["e"]], t_exit=t_arr[x], entry=r["entry"],
            stop_d=r["stop_d"], gross_r=gross, net_r=gross - cost_r,
            n_swaps=n_swaps, exit_reason=reason,
            t_momentum=t_arr[r["t_momentum"]], path=r["path"]))
    return trades


# ── stats (block() adapted from audit/audit_volspike.py, unchanged) ────────

def block(trades, label):
    if not trades:
        return f"{label}: no trades"
    rs = np.array([t["net_r"] for t in trades])
    order = np.argsort([t["t_exit"] for t in trades])
    ls, ls_d = streaks(rs[order], np.array([t["t_exit"] for t in trades])[order])
    gp, gl = rs[rs > 0].sum(), -rs[rs < 0].sum()
    return (f"{label}: n={len(rs)} exp={rs.mean():+.4f}R (SE {rs.std()/np.sqrt(len(rs)):.4f}) "
            f"win={np.mean(rs > 0):.1%} PF={gp/gl if gl else float('inf'):.3f} "
            f"streak={ls} ({ls_d:.0f}d)")


# ── candidate 1 signal regeneration (for sanity check (d)) ─────────────────

def generate_candidate1(df):
    """Regenerate candidate 1's signal set (identical logic to
    sandbox_xrpha.py's generate_and_resolve) so sanity check (d) can compare
    entry sets without depending on a stale sandbox_trades.csv on disk."""
    ha_o = df["port_ha_open"].to_numpy(float)
    ha_l = df["port_ha_low"].to_numpy(float)
    ha_c = df["port_ha_close"].to_numpy(float)
    ha_h = df["port_ha_high"].to_numpy(float)
    sha_o = df["port_sha_open"].to_numpy(float)
    sha_c = df["port_sha_close"].to_numpy(float)
    mfi = df["port_mfi_real"].to_numpy(float)
    real_o = df["open"].to_numpy(float)
    real_l = df["low"].to_numpy(float)
    real_h = df["high"].to_numpy(float)
    n = len(df)

    red = ha_c < ha_o
    green = ha_c > ha_o

    mom_long = green & (ha_l >= ha_o - WICK_TOL * ha_o)
    mom_short = red & (ha_h <= ha_o + WICK_TOL * ha_o)

    long_mfi_ok = mfi > 0
    long_sha_ok = sha_c > sha_o
    short_mfi_ok = mfi < 0
    short_sha_ok = sha_c < sha_o

    last_red, last_green = None, None
    long_consumed, short_consumed = False, False
    c1_trades = []

    for t in range(n):
        in_long_win = last_red is not None and 1 <= (t - last_red) <= 3
        in_short_win = last_green is not None and 1 <= (t - last_green) <= 3

        long_joint = long_mfi_ok[t] and long_sha_ok[t] and mom_long[t] and in_long_win
        if long_joint and not long_consumed:
            e = t + 1
            if e < n:
                entry = real_o[e]
                stop = real_l[t]
                stop_d = entry - stop
                if stop_d > 0 and stop_d >= MIN_STOP_PCT * entry:
                    long_consumed = True
                    c1_trades.append(dict(direction="long", t_signal=t, e=e,
                                           window_anchor=last_red))

        short_joint = short_mfi_ok[t] and short_sha_ok[t] and mom_short[t] and in_short_win
        if short_joint and not short_consumed:
            e = t + 1
            if e < n:
                entry = real_o[e]
                stop = real_h[t]
                stop_d = stop - entry
                if stop_d > 0 and stop_d >= MIN_STOP_PCT * entry:
                    short_consumed = True
                    c1_trades.append(dict(direction="short", t_signal=t, e=e,
                                           window_anchor=last_green))

        if red[t]:
            last_red = t
            long_consumed = False
        if green[t]:
            last_green = t
            short_consumed = False

    return c1_trades


# ── sanity checks ────────────────────────────────────────────────────────────

def sanity_checks(df, trades, raw_trades):
    log("\n## Sanity checks")
    n = len(df)

    # (a) every entry bar's time is exactly signal bar time + 900s
    bad_adjacency = [t for t in trades if t["t_entry"] - t["t_signal"] != 900]
    log(f"(a) entry-bar-is-signal+900s: {len(trades) - len(bad_adjacency)}/{len(trades)} "
        f"exact; violations={len(bad_adjacency)} "
        f"(would occur only if a signal bar immediately precedes one of the "
        f"sandbox's 4 documented small data holes -- positional 'next bar' "
        f"indexing is used throughout, per the file docstring)")
    if bad_adjacency:
        for t in bad_adjacency[:10]:
            log(f"    signal={t['t_signal']} entry={t['t_entry']} "
                f"delta={t['t_entry']-t['t_signal']}s dir={t['direction']}")

    # (b) no trade references any bar with time >= 2024-01-01
    bad_2024 = [t for t in trades
                if t["t_signal"] >= SANDBOX_CUT or t["t_entry"] >= SANDBOX_CUT
                or t["t_exit"] >= SANDBOX_CUT]
    log(f"(b) no trade touches time>=2024-01-01: violations={len(bad_2024)}")
    assert not bad_2024, "HARD SEGMENT LIMIT violated: a trade referenced 2024+ data"
    assert df["time"].max() < SANDBOX_CUT

    # (c) recompute 5 randomly-chosen trades with an independent slow-path loop
    rng = np.random.default_rng(20260709)
    if trades:
        k = min(5, len(trades))
        picks = rng.choice(len(trades), size=k, replace=False)
        log(f"(c) independent slow-path recheck of {k} randomly-chosen trades:")
        real_o = df["open"].tolist()
        real_h = df["high"].tolist()
        real_l = df["low"].tolist()
        real_c = df["close"].tolist()
        real_t = df["time"].tolist()
        idx_of_time = {v: i for i, v in enumerate(real_t)}
        for p in picks:
            tr = trades[p]
            e = idx_of_time[int(tr["t_entry"])]
            sgn = 1 if tr["direction"] == "long" else -1
            entry_slow = real_o[e]
            # recover stop from stored stop_d/entry/target relationship
            stop_d_slow = tr["stop_d"]
            stop_slow = entry_slow - sgn * stop_d_slow
            target_slow = entry_slow + sgn * 2 * stop_d_slow
            gross_slow = None
            x_slow = None
            reason_slow = None
            b = e
            while b < n:
                if b == e:
                    gap_sl = False
                    gap_tp = False
                else:
                    gap_sl = (real_o[b] <= stop_slow) if sgn > 0 else (real_o[b] >= stop_slow)
                    gap_tp = (real_o[b] >= target_slow) if sgn > 0 else (real_o[b] <= target_slow)
                hit_sl = (real_l[b] <= stop_slow) if sgn > 0 else (real_h[b] >= stop_slow)
                hit_tp = (real_h[b] >= target_slow) if sgn > 0 else (real_l[b] <= target_slow)
                if gap_sl or gap_tp:
                    px = real_o[b]
                    gross_slow = sgn * (px - entry_slow) / stop_d_slow
                    x_slow = b
                    reason_slow = "gap_sl" if gap_sl else "gap_tp"
                    break
                if hit_sl and hit_tp:
                    gross_slow, x_slow, reason_slow = -1.0, b, "sl_tp_ambiguous_worstcase_sl"
                    break
                if hit_sl:
                    gross_slow, x_slow, reason_slow = -1.0, b, "sl"
                    break
                if hit_tp:
                    gross_slow, x_slow, reason_slow = 2.0, b, "tp"
                    break
                b += 1
            if gross_slow is None:
                gross_slow = sgn * (real_c[n - 1] - entry_slow) / stop_d_slow
                x_slow, reason_slow = n - 1, "open_at_end"
            n_swaps_slow = int(real_t[x_slow] // 14400) - int(real_t[e] // 14400)
            cost_r_slow = (COMMISSION_RT + 2 * BASELINE_SLIP + n_swaps_slow * SWAP_PER_4H) \
                * entry_slow / stop_d_slow
            net_r_slow = gross_slow - cost_r_slow
            assert abs(gross_slow - tr["gross_r"]) < 1e-9, \
                f"gross_r mismatch: slow={gross_slow} fast={tr['gross_r']}"
            assert abs(net_r_slow - tr["net_r"]) < 1e-9, \
                f"net_r mismatch: slow={net_r_slow} fast={tr['net_r']}"
            assert real_t[x_slow] == tr["t_exit"]
            assert reason_slow == tr["exit_reason"]
            log(f"    trade #{p} ({tr['direction']}, t_signal={tr['t_signal']}): "
                f"gross_r slow={gross_slow:+.4f} fast={tr['gross_r']:+.4f} OK, "
                f"net_r slow={net_r_slow:+.4f} fast={tr['net_r']:+.4f} OK")
    else:
        log("(c) no trades to recheck")

    # (d) every candidate 1 entry whose window was not consumed earlier by a
    # candidate-2 new-path entry must appear in candidate 2's entry set.
    log("")
    log("(d) candidate 1 subsumption check: every candidate 1 entry should "
        "appear in candidate 2's entry set UNLESS its window was already "
        "consumed by an earlier candidate-2 new-path (t>k) completion.")
    c1_trades = generate_candidate1(df)
    c2_index = {(r["direction"], r["e"]) for r in raw_trades}
    # at most one candidate-2 entry per (direction, window anchor), since the
    # consumption flag prevents a second entry in the same window
    c2_by_dir_anchor = {(r["direction"], r["anchor"]): r for r in raw_trades}
    missing = []
    for c1 in c1_trades:
        key = (c1["direction"], c1["e"])
        if key not in c2_index:
            missing.append(c1)
    log(f"    candidate 1 entries: {len(c1_trades)}")
    log(f"    candidate 1 entries missing from candidate 2: {len(missing)}")
    if missing:
        unexplained = 0
        for c1 in missing:
            cover = c2_by_dir_anchor.get((c1["direction"], c1["window_anchor"]))
            if cover is not None and cover["t_signal"] < c1["t_signal"] and cover["path"] == "new":
                log(f"    MISSING (explained): dir={c1['direction']} "
                    f"t_signal={c1['t_signal']} e={c1['e']} "
                    f"window_anchor={c1['window_anchor']} -- window already "
                    f"consumed at t_signal={cover['t_signal']} by an earlier "
                    f"candidate-2 new-path entry (t_momentum={cover['t_momentum']}, "
                    f"e={cover['e']})")
            else:
                unexplained += 1
                log(f"    MISSING (UNEXPLAINED -- BUG): dir={c1['direction']} "
                    f"t_signal={c1['t_signal']} e={c1['e']} "
                    f"window_anchor={c1['window_anchor']} cover={cover}")
        log(f"    unexplained missing entries: {unexplained} "
            f"({'OK, all explained by earlier new-path consumption' if unexplained == 0 else 'INVESTIGATE -- possible bug'})")
        assert unexplained == 0, (
            f"{unexplained} candidate 1 entries missing from candidate 2 with no "
            f"valid earlier-new-path-consumption explanation -- likely a bug")
    else:
        log("    all candidate 1 entries present in candidate 2's entry set "
            "(no window was consumed early by a new-path completion in this "
            "run).")


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    log("# SANDBOX2 XRPHA REPORT (CANDIDATE 2: convergence rule)")
    log("")
    log("Frozen rule per FROZEN_SPEC_XRPHA.md, 'CANDIDATE 2: convergence rule' "
        "section. Sandbox segment only: bars with time < 2024-01-01 00:00 UTC. "
        "No number from 2024 onward appears anywhere in this report.")
    log("")

    df = load_sandbox()
    n = len(df)

    census, raw_trades = generate_and_resolve(df)

    log("## 1. Census")
    log("")
    log(f"bars in sandbox: {census['bars']}")
    log(f"HA colors: red={census['red']} green={census['green']} doji={census['doji']}")
    log(f"momentum candles: long-side(green,no-lower-wick)={census['mom_long']} "
        f"short-side(red,no-upper-wick)={census['mom_short']}")
    log("")
    log("LONG side filters (bar counts, independent):")
    log(f"  mfi>0: {census['mfi_long_bars']}")
    log(f"  sha bullish: {census['sha_long_bars']}")
    log(f"  momentum AND in-window: {census['momwin_long_bars']}")
    log(f"  jointly (armed [momentum-with-mfi>0 seen in window] AND green AND sha AND window, "
        f"pre window-consumption dedup): {census['joint_long_bars']}")
    log(f"  signals (joint AND window not yet consumed): {census['signals_long']}")
    log(f"  entries (signals passing stop filter): {census['entries_long']}")
    log(f"  skipped_min_stop: {census['skipped_min_stop_long']}")
    log(f"  skipped_degenerate (stop_d<=0): {census['skipped_degenerate_long']}")
    if census['skipped_no_next_bar_long']:
        log(f"  skipped_no_next_bar (signal at final sandbox bar, no t+1 to enter on): "
            f"{census['skipped_no_next_bar_long']}")
    log("")
    log("SHORT side filters (bar counts, independent):")
    log(f"  mfi<0: {census['mfi_short_bars']}")
    log(f"  sha bearish: {census['sha_short_bars']}")
    log(f"  momentum AND in-window: {census['momwin_short_bars']}")
    log(f"  jointly (armed [momentum-with-mfi<0 seen in window] AND red AND sha AND window, "
        f"pre window-consumption dedup): {census['joint_short_bars']}")
    log(f"  signals (joint AND window not yet consumed): {census['signals_short']}")
    log(f"  entries (signals passing stop filter): {census['entries_short']}")
    log(f"  skipped_min_stop: {census['skipped_min_stop_short']}")
    log(f"  skipped_degenerate (stop_d<=0): {census['skipped_degenerate_short']}")
    if census['skipped_no_next_bar_short']:
        log(f"  skipped_no_next_bar (signal at final sandbox bar, no t+1 to enter on): "
            f"{census['skipped_no_next_bar_short']}")
    log("")
    total_signals = census['signals_long'] + census['signals_short']
    total_entries = census['entries_long'] + census['entries_short']
    total_skip_minstop = census['skipped_min_stop_long'] + census['skipped_min_stop_short']
    total_skip_degen = census['skipped_degenerate_long'] + census['skipped_degenerate_short']
    log(f"TOTAL: signals={total_signals} entries={total_entries} "
        f"skipped_min_stop={total_skip_minstop} skipped_degenerate={total_skip_degen}")

    log("")
    log("Path split (t==k 'old' path reduces exactly to candidate 1; t>k 'new' "
        "path is the convergence extension):")
    log(f"  long: old={census['entries_long_old']} new={census['entries_long_new']}")
    log(f"  short: old={census['entries_short_old']} new={census['entries_short_new']}")
    log(f"  total: old={census['entries_long_old']+census['entries_short_old']} "
        f"new={census['entries_long_new']+census['entries_short_new']}")

    trades = simulate(df, raw_trades)
    n_open_at_end = sum(1 for t in trades if t["exit_reason"] == "open_at_end")
    n_ambiguous = sum(1 for t in trades if t["exit_reason"] == "sl_tp_ambiguous_worstcase_sl")
    log(f"open_at_end (marked to market at final sandbox close): {n_open_at_end}")
    log(f"(informational) same-bar SL+TP ambiguous bars resolved as SL (worst case): "
        f"{n_ambiguous}")

    log("")
    log("## 2. Pooled result at baseline costs (1bp slip)")
    log("")
    log(block(trades, "pooled"))
    log(block([t for t in trades if t["direction"] == "long"], "longs"))
    log(block([t for t in trades if t["direction"] == "short"], "shorts"))

    log("")
    log("## 2b. Path split at baseline costs (path_old: t==k, reduces to "
        "candidate 1; path_new: t>k, the convergence extension)")
    log("")
    log(block([t for t in trades if t["path"] == "old"], "path_old"))
    log(block([t for t in trades if t["path"] == "new"], "path_new"))

    log("")
    log("## 3. Per half-year window (2020H1-2023H2)")
    log("")
    from collections import defaultdict
    by_w = defaultdict(list)
    for t in trades:
        by_w[half_label(t["t_entry"])].append(t)
    window_means = {}
    for w in sorted(by_w):
        log(block(by_w[w], w))
        window_means[w] = np.mean([t["net_r"] for t in by_w[w]])
    n_windows = len(by_w)
    n_neg_windows = sum(1 for m in window_means.values() if m < 0)
    n_nonneg_windows = n_windows - n_neg_windows
    log("")
    log(f"windows with trades: {n_windows}, nonnegative: {n_nonneg_windows}, "
        f"negative: {n_neg_windows}")

    log("")
    log("## 4. Cost sweep (slippage bp/fill)")
    log("")
    rs_base = np.array([t["gross_r"] for t in trades])
    entry_arr = np.array([t["entry"] for t in trades])
    stopd_arr = np.array([t["stop_d"] for t in trades])
    nswaps_arr = np.array([t["n_swaps"] for t in trades])
    sweep_pts = []
    for bp in (0, 1, 2, 3, 5, 10):
        slip = bp * 1e-4
        cost_r = (COMMISSION_RT + 2 * slip + nswaps_arr * SWAP_PER_4H) * entry_arr / stopd_arr
        net_r = rs_base - cost_r
        m = net_r.mean() if len(net_r) else float("nan")
        sweep_pts.append((bp, m))
        log(f"  {bp:3d} bp: {m:+.4f}R (n={len(net_r)})")
    be = None
    prev = None
    for bp, m in sweep_pts:
        if prev and prev[1] > 0 >= m:
            be = prev[0] + prev[1] * (bp - prev[0]) / (prev[1] - m)
        prev = (bp, m)
    be_str = (f"{be:.1f} bp/fill" if be is not None
              else ("beyond swept range (10bp)" if prev[1] > 0 else "below 0bp (already negative at 0bp)"))
    log(f"  breakeven slippage: {be_str}")

    log("")
    log("## 5. Frozen pass bar evaluation")
    log("")
    rs = np.array([t["net_r"] for t in trades]) if trades else np.array([])
    pooled_exp = rs.mean() if len(rs) else float("nan")
    pass_bar = (len(rs) > 0 and pooled_exp >= 0.15 and n_nonneg_windows > n_windows / 2)
    log(f"Sandbox pass bar: net expectancy >= +0.15R AND more than half of the "
        f"half-year windows nonnegative.")
    log(f"  pooled net expectancy: {pooled_exp:+.4f}R "
        f"({'>= +0.15R' if len(rs) and pooled_exp >= 0.15 else '< +0.15R'})")
    log(f"  windows nonnegative: {n_nonneg_windows}/{n_windows} "
        f"({'> half' if n_nonneg_windows > n_windows / 2 else 'NOT > half'})")
    log(f"  => pass bar: {'MET' if pass_bar else 'NOT MET'}")

    log("")
    log("Kill checks (K-form):")
    k1 = (not len(rs)) or pooled_exp <= 0
    k2 = n_neg_windows > n_windows / 2
    k3 = (be is not None and be < 3.0) or (be is None and prev[1] <= 0)
    best_w = max(window_means, key=window_means.get) if window_means else None
    rs_wo = np.array([t["net_r"] for t in trades if half_label(t["t_entry"]) != best_w]) \
        if best_w is not None else np.array([])
    k4 = (not len(rs_wo)) or rs_wo.mean() <= 0
    log(f"  K1 pooled expectancy <= 0: {pooled_exp:+.4f}R -> {'KILL' if k1 else 'pass'}")
    log(f"  K2 windows negative: {n_neg_windows}/{n_windows} -> {'KILL' if k2 else 'pass'}")
    log(f"  K3 breakeven slippage < 3bp: {be_str} -> {'KILL' if k3 else 'pass'}")
    if best_w is not None:
        log(f"  K4 pooled expectancy <= 0 without best window ({best_w}): "
            f"{rs_wo.mean():+.4f}R -> {'KILL' if k4 else 'pass'}")
    else:
        log(f"  K4: no trades, KILL")

    verdict = "PASS" if (pass_bar and not (k1 or k2 or k3 or k4)) else "DEAD"
    log("")
    log(f"VERDICT: {verdict}")
    if verdict == "DEAD":
        reasons = []
        if not pass_bar:
            reasons.append("pass bar not met")
        if k1:
            reasons.append("K1 kill")
        if k2:
            reasons.append("K2 kill")
        if k3:
            reasons.append("K3 kill")
        if k4:
            reasons.append("K4 kill")
        log(f"  reason(s): {', '.join(reasons)}")

    sanity_checks(df, trades, raw_trades)

    log("")
    log("## 6. Trade log")
    log(f"per-trade CSV written to {CSV_PATH}")
    cols = ["direction", "t_signal", "t_entry", "t_exit", "entry", "stop_d",
            "gross_r", "net_r", "n_swaps", "exit_reason", "t_momentum", "path"]
    pd.DataFrame(trades)[cols].to_csv(CSV_PATH, index=False)

    with open(REPORT_PATH, "w") as f:
        f.write("\n".join(REPORT_LINES) + "\n")
    log(f"\nwrote report to {REPORT_PATH}")


if __name__ == "__main__":
    main()
