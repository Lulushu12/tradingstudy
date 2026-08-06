#!/usr/bin/env python3
"""Review engine for the discretionary trading journal.

Stdlib only, no dependencies. Run it at every 40-trade block review.

    python3 review.py journal.csv
    python3 review.py journal.csv --fee 0.08
    python3 review.py --self-test        # synthetic data, verifies the engine

It answers the three questions from SYSTEM_SPEC_v1.md Layer 7:

  1. Does the grading work?      A-grade expectancy vs B-grade
  2. Does discipline work?       clean vs deviated
  3. Does discretion beat S4?    S1+S2+S3 pooled vs the mechanical control

plus a reconstruction of every exit policy on every trade, from MFE/MAE.

Every number is printed with a standard error. A difference smaller than about
2 standard errors is not a finding, it is noise. The script says so out loud.
"""

import argparse
import csv
import math
import os
import random
import statistics
import sys

PRE_TRADE_FIELDS = [
    "symbol", "setup", "direction", "grade", "htf_trend", "anchor_tf",
    "planned_entry", "planned_stop", "planned_target", "planned_rr", "risk_pct",
]
POST_TRADE_FIELDS = ["r_realized", "mfe_r", "mae_r", "adherence"]

VALID_SETUP = {"S1", "S2", "S3", "S4"}
VALID_GRADE = {"A", "B", "C"}
VALID_DIRECTION = {"long", "short"}
VALID_ADHERENCE = {"clean", "deviated"}
VALID_HTF = {"with", "against"}
VALID_ANCHOR = {"1D", "4H", "1h", "15m"}

ANCHOR_MIN_N = 40   # per the pre-committed anchor rule in Layer 7
FEE_DRAG_CAP = 0.20  # R, per Layer 5

DISCRETIONARY = {"S1", "S2", "S3"}
CONTROL = {"S4"}

MIN_BUCKET = 30  # below this, a bucket result is reported but not trusted


# ---------------------------------------------------------------- loading

def to_float(value, default=None):
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return default


class Trade(dict):
    """A journal row with parsed numerics and a list of validation problems."""

    @property
    def r(self):
        return self["_r"]


def load(path):
    with open(path, newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    trades, problems = [], []
    for index, row in enumerate(rows, start=2):  # header is line 1
        row = {(k or "").strip(): (v or "").strip() for k, v in row.items()}
        if not any(row.values()):
            continue
        trade = Trade(row)
        ident = row.get("trade_id") or "line %d" % index

        missing = [f for f in PRE_TRADE_FIELDS if not row.get(f)]
        if missing:
            problems.append("trade %s: missing pre-trade field(s): %s"
                            % (ident, ", ".join(missing)))

        missing_post = [f for f in POST_TRADE_FIELDS if not row.get(f)]
        if missing_post:
            problems.append("trade %s: missing post-trade field(s): %s"
                            % (ident, ", ".join(missing_post)))
            continue

        for field, allowed in (("setup", VALID_SETUP), ("grade", VALID_GRADE),
                               ("direction", VALID_DIRECTION),
                               ("adherence", VALID_ADHERENCE),
                               ("htf_trend", VALID_HTF),
                               ("anchor_tf", VALID_ANCHOR)):
            if row.get(field) and row[field] not in allowed:
                problems.append("trade %s: invalid %s=%r" % (ident, field, row[field]))

        r = to_float(row.get("r_realized"))
        if r is None:
            problems.append("trade %s: unparseable r_realized" % ident)
            continue
        trade["_r"] = r
        trade["_mfe"] = max(0.0, to_float(row.get("mfe_r"), 0.0))
        trade["_mae"] = max(0.0, to_float(row.get("mae_r"), 0.0))

        entry = to_float(row.get("planned_entry"))
        stop = to_float(row.get("planned_stop"))
        if entry and stop and entry != stop:
            trade["_stop_pct"] = abs(entry - stop) / entry * 100.0
        else:
            trade["_stop_pct"] = None

        rr = to_float(row.get("planned_rr"))
        if rr is not None and rr < 2.0 and row.get("setup") != "S4":
            if row.get("adherence") == "clean":
                problems.append(
                    "trade %s: planned_rr=%.2f is below the 2.0 floor but is marked clean"
                    % (ident, rr))
        trades.append(trade)

    return trades, problems


# ---------------------------------------------------------------- statistics

def stats(values):
    n = len(values)
    if n == 0:
        return {"n": 0, "mean": 0.0, "se": 0.0, "wr": 0.0, "pf": 0.0,
                "sum": 0.0, "maxdd": 0.0, "streak": 0}
    mean = statistics.fmean(values)
    se = (statistics.stdev(values) / math.sqrt(n)) if n > 1 else 0.0
    wins = [v for v in values if v > 0]
    losses = [v for v in values if v < 0]
    gross_win = sum(wins)
    gross_loss = abs(sum(losses))
    pf = (gross_win / gross_loss) if gross_loss > 0 else float("inf")

    equity, peak, maxdd = 0.0, 0.0, 0.0
    streak, worst_streak = 0, 0
    for v in values:
        equity += v
        peak = max(peak, equity)
        maxdd = max(maxdd, peak - equity)
        if v <= 0:
            streak += 1
            worst_streak = max(worst_streak, streak)
        else:
            streak = 0
    return {"n": n, "mean": mean, "se": se, "wr": len(wins) / n * 100.0, "pf": pf,
            "sum": equity, "maxdd": maxdd, "streak": worst_streak}


def fmt_pf(pf):
    return "inf" if pf == float("inf") else "%.2f" % pf


def line(label, s, width=26):
    flag = "" if s["n"] >= MIN_BUCKET else "   (n<%d, not trusted)" % MIN_BUCKET
    return "%-*s n=%-4d  exp=%+.3fR +/- %.3f  wr=%5.1f%%  pf=%-5s  sumR=%+7.2f%s" % (
        width, label, s["n"], s["mean"], s["se"], s["wr"], fmt_pf(s["pf"]), s["sum"], flag)


def compare(name_a, a, name_b, b, threshold=0.0):
    """Print a difference with the standard error of that difference."""
    if a["n"] == 0 or b["n"] == 0:
        return "  %s vs %s: not enough data (n=%d vs n=%d)" % (
            name_a, name_b, a["n"], b["n"])
    diff = a["mean"] - b["mean"]
    se = math.sqrt(a["se"] ** 2 + b["se"] ** 2)
    if se == 0:
        verdict = "no variance to test"
    elif abs(diff) < 2 * se:
        verdict = "NOT distinguishable from noise (|diff| < 2 SE)"
    elif diff > threshold:
        verdict = "%s is ahead" % name_a
    else:
        verdict = "%s is ahead" % name_b
    return "  %s - %s = %+.3fR  (SE of diff %.3f)  -> %s" % (
        name_a, name_b, diff, se, verdict)


def bucket(trades, key):
    out = {}
    for t in trades:
        out.setdefault(t.get(key, "?") or "?", []).append(t.r)
    return {k: stats(v) for k, v in sorted(out.items())}


# ---------------------------------------------------------------- exit policies

def reconstruct(trade, fee_pct):
    """Reconstruct what each fixed exit policy would have returned, in net R.

    Uses MFE/MAE. 1R is the planned stop distance. Fee drag is converted from a
    round-trip percentage into R using the trade's own stop distance, so a tight
    stop is correctly penalised more than a wide one.

    Assumption, stated openly: if MFE reached a target level, that target was hit
    before the stop. This is true for any single-target policy because the trade
    would have ended there. Where neither target nor stop was reached (a manual or
    time-based exit), the policy falls back to the realised R, which slightly
    flatters every policy equally.
    """
    mfe, mae = trade["_mfe"], trade["_mae"]
    stop_pct = trade["_stop_pct"]
    fee_r = (fee_pct / stop_pct) if (stop_pct and stop_pct > 0) else 0.0
    stopped = mae >= 1.0
    fallback = trade.r

    def result(value, hit):
        return value - fee_r if hit else fallback

    out = {}
    for label, target in (("full_1R", 1.0), ("full_2R", 2.0), ("full_3R", 3.0)):
        if mfe >= target:
            out[label] = result(target, True)
        elif stopped:
            out[label] = result(-1.0, True)
        else:
            out[label] = fallback

    # 40% off at the first target, stop to breakeven, 60% runs to 2R
    for label, first in (("partial_be", 1.0), ("partial_be_early", 0.5)):
        if mfe >= 2.0:
            out[label] = result(0.4 * first + 0.6 * 2.0, True)
        elif mfe >= first:
            out[label] = result(0.4 * first, True)
        elif stopped:
            out[label] = result(-1.0, True)
        else:
            out[label] = fallback
    return out


# ---------------------------------------------------------------- report

def report(trades, problems, fee_pct, path_label):
    w = sys.stdout.write
    w("\n" + "=" * 78 + "\n")
    w("DISCRETIONARY SYSTEM REVIEW   source: %s   fee assumption: %.3f%% round trip\n"
      % (path_label, fee_pct))
    w("=" * 78 + "\n")

    w("\n-- PROCESS AUDIT " + "-" * 61 + "\n")
    if problems:
        w("%d process problem(s). These are failures of the system, not of the market.\n\n"
          % len(problems))
        for p in problems[:40]:
            w("  ! %s\n" % p)
        if len(problems) > 40:
            w("  ... and %d more\n" % (len(problems) - 40))
    else:
        w("  Clean. Every row has its pre-trade fields and valid enums.\n")

    if not trades:
        w("\nNo complete trades to analyse yet.\n")
        return

    all_r = [t.r for t in trades]
    overall = stats(all_r)
    w("\n-- OVERALL " + "-" * 66 + "\n")
    w(line("all trades", overall) + "\n")
    w("  max drawdown %.2fR   longest losing streak %d trades\n"
      % (overall["maxdd"], overall["streak"]))
    n = overall["n"]
    w("  95%% interval on expectancy: %+.3fR to %+.3fR\n"
      % (overall["mean"] - 1.96 * overall["se"], overall["mean"] + 1.96 * overall["se"]))
    if n < 40:
        w("  Below one review block (40 trades). Read this as orientation, not evidence.\n")

    w("\n-- QUESTION 1: DOES THE GRADING WORK? " + "-" * 40 + "\n")
    by_grade = bucket(trades, "grade")
    for k, s in by_grade.items():
        w(line("grade %s" % k, s) + "\n")
    if "A" in by_grade and "B" in by_grade:
        w(compare("A", by_grade["A"], "B", by_grade["B"]) + "\n")
        w("  Spec threshold: A must beat B by >= 0.10R for the grading to be load bearing.\n")

    w("\n-- QUESTION 2: DOES DISCIPLINE WORK? " + "-" * 41 + "\n")
    by_adh = bucket(trades, "adherence")
    for k, s in by_adh.items():
        w(line(k, s) + "\n")
    if "clean" in by_adh and "deviated" in by_adh:
        w(compare("clean", by_adh["clean"], "deviated", by_adh["deviated"]) + "\n")
        dev = by_adh["deviated"]
        w("  Deviation rate: %.1f%% of trades, %+.2fR net on deviated rows.\n"
          % (dev["n"] / n * 100.0, dev["sum"]))
    reasons = {}
    for t in trades:
        if t.get("adherence") == "deviated":
            reasons.setdefault(t.get("deviation_reason") or "(unstated)", []).append(t.r)
    if reasons:
        w("\n  deviation breakdown:\n")
        for k, v in sorted(reasons.items(), key=lambda kv: sum(kv[1])):
            w("    %-34s n=%-3d  sumR=%+6.2f\n" % (k[:34], len(v), sum(v)))

    w("\n-- QUESTION 3: DOES DISCRETION BEAT THE MACHINE? " + "-" * 29 + "\n")
    disc = stats([t.r for t in trades if t.get("setup") in DISCRETIONARY])
    ctrl = stats([t.r for t in trades if t.get("setup") in CONTROL])
    w(line("discretionary S1+S2+S3", disc) + "\n")
    w(line("control S4", ctrl) + "\n")
    w(compare("discretionary", disc, "S4", ctrl) + "\n")
    w("  S4 backtested at +0.21R. If your live S4 differs a lot from that, suspect\n"
      "  execution or data, not the setup.\n")

    w("\n-- BY SETUP " + "-" * 65 + "\n")
    for k, s in bucket(trades, "setup").items():
        w(line("setup %s" % k, s) + "\n")

    w("\n-- QUESTION 4: WHICH ANCHOR TIMEFRAMES PAY? " + "-" * 34 + "\n")
    w("  Each anchor is judged against its OWN breakeven bar, since a tighter stop pays\n"
      "  more in fees. breakeven WR at 2:1 = (1 + fee_drag) / 3.\n\n")
    by_anchor = {}
    for t in trades:
        by_anchor.setdefault(t.get("anchor_tf") or "?", []).append(t)
    order = [a for a in ("1D", "4H", "1h", "15m") if a in by_anchor]
    order += [a for a in sorted(by_anchor) if a not in order]
    for anchor in order:
        group = by_anchor[anchor]
        s = stats([t.r for t in group])
        stop_pcts = [t["_stop_pct"] for t in group if t["_stop_pct"]]
        median_stop = statistics.median(stop_pcts) if stop_pcts else None
        w("  " + line("anchor %s" % anchor, s, width=20) + "\n")
        if median_stop:
            drag = fee_pct / median_stop
            breakeven = (1.0 + drag) / 3.0 * 100.0
            actual_wr = s["wr"]
            margin = actual_wr - breakeven
            w("      median stop %.2f%%  fee drag %.3fR  breakeven WR @2:1 %.1f%%  "
              "actual %.1f%%  margin %+.1f pts\n"
              % (median_stop, drag, breakeven, actual_wr, margin))
            over = [t for t in group
                    if t["_stop_pct"] and fee_pct / t["_stop_pct"] > FEE_DRAG_CAP]
            if over:
                w("      %d trade(s) exceeded the %.2fR fee-drag cap (stop tighter than "
                  "%.2f%%)\n" % (len(over), FEE_DRAG_CAP, fee_pct / FEE_DRAG_CAP))
        if s["n"] < ANCHOR_MIN_N:
            w("      not yet measured: %d of %d trades needed before the anchor rule "
              "applies\n" % (s["n"], ANCHOR_MIN_N))
        elif s["mean"] <= 0:
            w("      *** DROP THIS ANCHOR. Expectancy <= 0 on n>=%d, per the pre-committed\n"
              "      *** anchor rule in SYSTEM_SPEC_v1.md Layer 7. It does not get a second "
              "block.\n" % ANCHOR_MIN_N)
        else:
            w("      clears its bar on n>=%d. Keep.\n" % ANCHOR_MIN_N)

    w("\n-- BY CONTEXT " + "-" * 63 + "\n")
    for label, key in (("direction", "direction"), ("4H trend", "htf_trend"),
                       ("symbol", "symbol")):
        w("  %s:\n" % label)
        for k, s in bucket(trades, key).items():
            w("    " + line(str(k), s, width=20) + "\n")

    w("\n-- EXIT POLICY RECONSTRUCTION " + "-" * 47 + "\n")
    w("  What each policy would have returned across all %d trades, net of fees.\n" % n)
    policies = {}
    for t in trades:
        for name, value in reconstruct(t, fee_pct).items():
            policies.setdefault(name, []).append(value)
    ranked = sorted(((name, stats(v)) for name, v in policies.items()),
                    key=lambda kv: kv[1]["mean"], reverse=True)
    for name, s in ranked:
        w("  " + line(name, s, width=20) + "\n")
    if len(ranked) >= 2:
        best, second = ranked[0], ranked[1]
        w("\n" + compare(best[0], best[1], second[0], second[1]) + "\n")
        w("  Paired samples, so the SE of the difference is conservative here.\n")
    fallbacks = sum(1 for t in trades if t["_mfe"] < 1.0 and t["_mae"] < 1.0)
    if fallbacks:
        w("  Note: %d trade(s) reached neither 1R nor the stop, so every policy fell back\n"
          "  to the realised R for those. That flatters all policies equally.\n" % fallbacks)

    # MFE truncation check. If MFE was only ever measured up to your live exit, then
    # policies with a target beyond that exit cannot be evaluated and will be wrong.
    winners = [t for t in trades if t["_mfe"] >= 1.0]
    beyond_2r = [t for t in winners if t["_mfe"] > 2.05]
    if winners and len(beyond_2r) / len(winners) < 0.05:
        w("\n  WARNING: almost no trade records an MFE above 2.05R. That usually means MFE\n"
          "  was measured only up to your actual exit, not over the full post-entry window.\n"
          "  If so, full_3R above is meaningless and full_2R is a ceiling, not a finding.\n"
          "  Fix by measuring MFE per JOURNAL_SCHEMA.md: from entry until the ORIGINAL stop\n"
          "  is touched or 48 hours pass, whichever comes first, regardless of when you\n"
          "  actually got out.\n")

    w("\n-- KILL RULE " + "-" * 64 + "\n")
    if n < 100:
        w("  %d of 100 trades logged. The pre-committed kill rule is not yet evaluable.\n" % n)
    else:
        cond_exp = disc["mean"] <= 0
        cond_grade = True
        if "A" in by_grade and "B" in by_grade:
            cond_grade = (by_grade["A"]["mean"] - by_grade["B"]["mean"]) < 0.10
        cond_adh = True
        if "clean" in by_adh and "deviated" in by_adh:
            cond_adh = by_adh["clean"]["mean"] <= by_adh["deviated"]["mean"]
        w("  discretionary expectancy <= 0        : %s\n" % cond_exp)
        w("  A does not beat B by 0.10R           : %s\n" % cond_grade)
        w("  clean does not beat deviated         : %s\n" % cond_adh)
        if cond_exp and cond_grade and cond_adh:
            w("\n  *** FALSIFIED. Per the pre-committed rule in SYSTEM_SPEC_v1.md Layer 7,\n"
              "  *** stop trading S1/S2/S3 and trade S4 mechanically only.\n")
        else:
            w("\n  Not falsified. This means NOT YET FALSIFIED, nothing stronger.\n")
    w("\n")


# ---------------------------------------------------------------- self test

def self_test():
    """Generate a synthetic journal and run the full report, to verify the engine."""
    random.seed(7)
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_selftest_journal.csv")
    header = ["trade_id", "date_utc", "symbol", "setup", "direction", "grade",
              "confluence", "htf_trend", "anchor_tf", "trigger_tf", "planned_entry",
              "planned_stop", "planned_target", "planned_rr", "risk_pct", "actual_entry",
              "actual_exit", "exit_reason", "r_realized", "mfe_r", "mae_r", "exit_policy",
              "adherence", "deviation_reason", "notes", "chart"]
    anchors = {"1D": (2.5, 3.5), "4H": (1.2, 2.2), "1h": (0.7, 1.2), "15m": (0.4, 0.7)}
    rows = []
    for i in range(1, 161):
        setup = random.choice(["S1", "S1", "S2", "S3", "S4", "S4"])
        grade = "A" if random.random() < 0.45 else "B"
        clean = random.random() < 0.82
        anchor = "4H" if setup == "S4" else random.choice(["1D", "4H", "4H", "1h", "15m"])
        # A-grade and clean trades get a genuinely better hit rate, and the 15m anchor a
        # worse one, so the comparison logic has something real to detect.
        p = 0.44 if grade == "A" else 0.36
        if not clean:
            p -= 0.08
        if anchor == "15m":
            p -= 0.06
        won = random.random() < p
        entry = 100000.0
        stop_pct = random.uniform(*anchors[anchor])
        stop = entry * (1 - stop_pct / 100.0)
        if won:
            mfe = round(random.uniform(2.0, 3.4), 1)
            mae = round(random.uniform(0.0, 0.8), 1)
            r = 2.0 - 0.08 / stop_pct
        else:
            mfe = round(random.uniform(0.0, 1.6), 1)
            mae = round(random.uniform(1.0, 1.3), 1)
            r = -1.0 - 0.08 / stop_pct
        rows.append([
            i, "2026-0%d-01T12:00:00Z" % (1 + i % 9),
            random.choice(["BTCUSDT.P", "ETHUSDT.P", "SOLUSDT.P", "XRPUSDT.P"]),
            setup, random.choice(["long", "short"]), grade,
            "htf|fib|vp" if grade == "A" else "htf|fib",
            "with" if random.random() < 0.75 else "against", anchor,
            {"1D": "1h", "4H": "15m", "1h": "5m", "15m": "5m"}[anchor],
            "%.2f" % entry, "%.2f" % stop, "%.2f" % (entry * 1.03), "2.4", "0.5",
            "%.2f" % entry, "%.2f" % (entry * 1.02), "target" if won else "stop",
            "%.3f" % r, mfe, mae, "partial_be",
            "clean" if clean else "deviated",
            "" if clean else random.choice(["entered intrabar", "chased after level broke",
                                            "moved stop", "C grade"]),
            "", "",
        ])
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)
    trades, problems = load(path)
    report(trades, problems, 0.08, path + " (SYNTHETIC SELF TEST, not real trades)")
    print("Self test wrote %s with %d synthetic rows. Delete it when done.\n" % (path, len(rows)))


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("journal", nargs="?", default="journal.csv",
                        help="path to the journal CSV (default: journal.csv)")
    parser.add_argument("--fee", type=float, default=0.08,
                        help="round-trip fee in percent, used for exit reconstruction")
    parser.add_argument("--self-test", action="store_true",
                        help="run on generated synthetic data to verify the engine")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return 0
    if not os.path.exists(args.journal):
        print("No journal at %s. Copy journal_template.csv to journal.csv and start "
              "logging.\nTo verify this script works, run: python3 review.py --self-test"
              % args.journal)
        return 1
    trades, problems = load(args.journal)
    report(trades, problems, args.fee, args.journal)
    return 0


if __name__ == "__main__":
    sys.exit(main())
