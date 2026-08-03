"""Tab builders for the deliverable workbook.

Every statistic on the Summary tab is a live formula against the trade-log
sheets, so filtering or editing a log updates it. Numbers that a spreadsheet
formula cannot reasonably express (path-dependent drawdown, the sensitivity
grids, buy & hold) are written as values and labelled with the script that
produced them.
"""

import json
import os

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

WINDOW = "2025-06-12 22:00 UTC to 2026-08-03 13:00 UTC (10,000 hourly candles)"


def _title(ws, f, title, sub=None):
    ws.write(0, 0, title, f["title"])
    if sub:
        ws.write(1, 0, sub, f["sub"])
    ws.set_row(0, 22)


def write_readme(wb, f):
    ws = wb.add_worksheet("Read Me")
    ws.set_column(0, 0, 3)
    ws.set_column(1, 1, 34)
    ws.set_column(2, 2, 104)
    _title(ws, f, "ETH / LINK / SOL - Hourly Trade Simulation Study")
    ws.write(1, 0, "")

    blocks = [
        ("WHAT THIS IS", [
            ("Mandate", "Enter a trade at market on every hourly candle close for ETHUSDT, LINKUSDT and SOLUSDT "
                        "over the last 10,000 hours. Every trade carries a written thesis, a stop loss and a "
                        "take profit. Trades stack without limit - each candle's signal is treated as its own "
                        "independent trade."),
            ("Two books", "'All Trades' is the literal mandate: one trade per candle close. 'Selective' is the same "
                          "engine filtered to conviction >= 6.0/10. The Selective rows are a strict subset of the "
                          "All Trades rows, so the two views always reconcile."),
            ("What it is not", "This is a simulation of one rule set over one window, not a forecast. Read the "
                               "Findings tab before you read anything else - several results point the opposite "
                               "way from what they first appear to."),
        ]),
        ("DATA", [
            ("Source", "Binance spot 1h klines via data-api.binance.vision (the public market-data mirror; "
                       "identical payload to api.binance.com, which is geo-blocked from the build environment)."),
            ("Window", WINDOW),
            ("Integrity", "10,000 contiguous candles per symbol, zero gaps, identical windows across all three "
                          "symbols. Verified by backtest/fetch_data.py."),
            ("Warm-up", "The first 500 bars are consumed warming up EMA200, ADX and the 500-bar volatility "
                        "percentile, and the final bar cannot be entered (no forward bar to resolve it). "
                        "That leaves 9,499 tradeable closes per symbol."),
        ]),
        ("HOW DIRECTION IS CHOSEN", [
            ("TREND_PULLBACK", "EMAs stacked 21/55/200, ADX >= 22, price eased back into the 21 EMA with RSI "
                               "reset but the 55 EMA intact. Buy the dip inside an intact trend."),
            ("BREAKOUT", "Stacked EMAs, ADX >= 25, close takes out the prior 48h extreme on above-average "
                         "volume. Join the expansion."),
            ("EXHAUSTION", "Price > 3.2 ATR from the 21 EMA with RSI at an extreme while ADX < 30. Fade the "
                           "blow-off, tight leash."),
            ("RANGE_FADE", "ADX < 20 and price pinned at the edge of the 48h Donchian channel. Sell the top / "
                           "buy the bottom back toward the mean."),
            ("DEFAULT", "No clean setup. The mandate still requires a fill, so direction comes from a weighted "
                        "composite of trend alignment, DI balance, 200 EMA slope and a mean-reversion tilt on "
                        "stretch. Scored low-conviction on purpose. 90% of all trades land here."),
        ]),
        ("HOW LEVELS ARE SET", [
            ("Stop loss", "An ATR multiple set by setup (1.1x to 1.6x), then pushed BEYOND the last confirmed "
                          "swing pivot plus a 0.25 ATR buffer, so the stop sits past the obvious liquidity pool "
                          "rather than on top of it. Clamped to a 0.6x-2.6x ATR band."),
            ("Take profit", "An R-multiple of the resulting stop distance, set by setup: 3.0R breakouts, 2.5R "
                            "trend pullbacks, 1.5R exhaustion and default fills, 1.3R range fades. Trends get "
                            "room; fades get taken quickly."),
            ("Asymmetry, stated plainly", "The stop reads price action per candle - ATR sizing plus real swing "
                                          "structure, giving 500+ distinct stop distances per symbol. The target "
                                          "does not: it is the stop distance times a per-setup constant, so only "
                                          "FOUR distinct reward ratios exist across all 28,497 trades. The target "
                                          "price varies only because the stop underneath it varies. A "
                                          "structure-aware alternative was built and tested head-to-head - see "
                                          "the Target Method tab. It lost."),
            ("Time stop", "24h to 120h by setup. Without it, 28,000 stacked trades never close."),
            ("Swing pivots", "Confirmed with 3 bars either side, and only made visible 3 bars AFTER the pivot "
                             "bar - the point at which the pivot could actually have been known. This is the "
                             "single easiest place for a backtest to cheat."),
        ]),
        ("FILL ASSUMPTIONS (all chosen to err against the strategy)", [
            ("Entry", "Close of the signal bar, plus slippage, plus taker fee. Exit scanning starts on the NEXT "
                      "bar - a signal bar can never resolve the trade it created."),
            ("Ambiguous bars", "When one bar's range contains BOTH the stop and the target, the STOP is assumed "
                               "to have hit first. Hourly bars hide the path, and assuming the favourable order "
                               "is the most common way a backtest lies to you."),
            ("Gaps", "A bar that opens beyond the stop or target fills at the open, not at the level."),
            ("Costs", "0.045% taker fee per side, 0.02% slippage per side, and 0.01% per 8h funding charged as a "
                      "drag on BOTH directions. Real funding alternates sign; charging it as a cost either way is "
                      "the conservative choice. Total friction consumes 8-10% of one R on the average trade."),
            ("Unresolved", "Trades still open when the data ends are marked OPEN and excluded from all statistics. "
                           "They are never counted as wins. 36 trades across all three symbols."),
        ]),
        ("SIZING AND THE R UNIT", [
            ("1R", "The distance from entry to stop, i.e. the loss taken if the stop fills exactly. All "
                   "performance is quoted in R so that trades with different stop distances are comparable."),
            ("P&L column", "Dollars at a flat $1,000 risked per trade. Because trades stack without limit, a "
                           "compounding equity curve would be meaningless here - the dollar column is a constant-"
                           "risk scorecard, not an account balance."),
            ("Important", "28,461 overlapping trades are NOT 28,461 independent observations. Many are the same "
                          "move sampled repeatedly hour after hour. The effective sample is far smaller than the "
                          "trade count, so treat every confidence interval here as much wider than n suggests."),
        ]),
        ("THE TWO FILES", [
            ("This file", "ETH_LINK_SOL_trading_study.xlsx - all the analysis, ~2 MB, opens instantly. The "
                          "Trade Stats tab holds a compact numeric row per trade, which is what the Summary "
                          "formulas read."),
            ("Companion file", "ETH_LINK_SOL_trade_logs.xlsx - the six full logs, 28,497 rows carrying the "
                               "written thesis, every indicator reading and every level for each trade. Split "
                               "out because ~600 characters of prose per row makes an 8.8 MB file that is slow "
                               "to open and awkward to scroll."),
            ("Reconciling", "Trade IDs match across both files. Every row in Trade Stats has a full-detail "
                            "twin in the logs file."),
            ("On the formulas", "LibreOffice cannot load a workbook in the environment that built this file - "
                                "a 100-cell test file fails identically - so the usual recalculate-and-verify "
                                "pass was unavailable. Each formula therefore ships with a cached value "
                                "computed in Python, and those cached values are cross-checked against "
                                "analyze.py, an independent implementation over the same logs, before the file "
                                "is written. Excel will recalculate everything live on open."),
        ]),
        ("TABS", [
            ("Summary", "Live formula statistics for all six books, plus buy & hold benchmarks."),
            ("Findings", "The seven conclusions worth acting on. Start here."),
            ("Setup Breakdown", "Performance sliced by setup, direction, exit reason and conviction bucket."),
            ("Stop-Target Sweep", "Sensitivity of the selective book to stop width and target distance."),
            ("Target Method", "Fixed-R targets vs targets aimed at real swing structure, head-to-head on "
                              "identical entries and stops."),
            ("System v2", "Two candidate changes and their in-sample results. One was later falsified."),
            ("Out of Sample", "The decisive tab. Every rule re-tested on the strictly disjoint 10,000 "
                              "hours before the main window. Read this before acting on anything."),
            ("System v3", "The live configuration: RANGE_FADE deleted, resting-limit entries on "
                          "pullbacks and fades. The strongest - and still not significant - result here."),
            ("Hypothesis H1", "A new entry idea, pre-registered to git before testing, then falsified. "
                              "The clean example of how the rest of this study should have been run."),
            ("Stability", "Same statistics computed on each half of the sample independently."),
            ("Equity Curves", "Cumulative R for all six books."),
            ("Trade Stats", "One compact row per trade across all three symbols - the Summary tab's data source."),
            ("<SYM> All Trades", "In the companion logs file. 9,499 rows per symbol: every candle close with "
                                 "its thesis, levels and outcome."),
            ("<SYM> Selective", "In the companion logs file. The conviction >= 6.0 subset, ~720-760 rows."),
        ]),
        ("REPRODUCING", [
            ("Scripts", "backtest/fetch_data.py -> run_backtest.py -> analyze.py -> robustness.py -> sweep.py "
                        "-> build_workbook.py. Deterministic given the same data files."),
        ]),
    ]

    r = 3
    for head, items in blocks:
        ws.write(r, 1, head, f["h1"])
        ws.write(r, 2, "", f["h1"])
        r += 1
        for label, body in items:
            ws.write(r, 1, label, f["label"])
            ws.write(r, 2, body, f["wrap"])
            ws.set_row(r, max(14, 11.5 * (len(body) // 100 + 1)))
            r += 1
        r += 1


def write_summary(ws, f, symbols, n_stats, analysis, all_rows, sel_rows, SCOL, colletter):
    _title(ws, f, "Summary",
           "Every figure below is a live formula against the Trade Stats tab. Edit or extend that "
           "sheet and these update.")
    ws.set_column(0, 0, 34)
    ws.set_column(1, 6, 15)

    books = [(f"{short} {'all' if kind == 'all' else 'selective'}", sym, kind)
             for sym, short in symbols for kind in ("all", "sel")]

    S = "'Trade Stats'"

    def rng(field):
        c = colletter(SCOL[field])
        return f"{S}!${c}$2:${c}${n_stats + 1}"

    r_ = rng("r_multiple")
    st_ = rng("status")
    sy_ = rng("symbol")
    se_ = rng("selective")
    usd_ = rng("pnl_usd")
    ex_ = rng("exit_reason")

    # Quoted criteria built as plain strings: nesting them inside f-strings
    # would need escaped quotes, which f-string expressions forbid.
    Q = '"'
    GT0 = "," + r_ + "," + Q + ">0" + Q
    LE0 = "," + r_ + "," + Q + "<=0" + Q

    def sel_only(kind):
        return "," + se_ + "," + Q + "YES" + Q if kind == "sel" else ""

    def crit(sym, kind, extra=""):
        """Common criteria: this symbol, closed, and optionally selective-only."""
        base = sy_ + "," + Q + sym + Q + "," + st_ + "," + Q + "CLOSED" + Q
        return base + sel_only(kind) + extra

    def entered(sym, kind):
        return sy_ + "," + Q + sym + Q + sel_only(kind)

    def exit_is(pattern):
        return "," + ex_ + "," + Q + pattern + Q

    hdr_row = 3
    ws.write(hdr_row, 0, "Metric", f["hdr"])
    for i, (name, _, _) in enumerate(books):
        ws.write(hdr_row, i + 1, name, f["hdr"])
    ws.set_row(hdr_row, 30)

    metrics = [
        ("Trades entered", lambda s, k: "=COUNTIFS(" + entered(s, k) + ")", "int"),
        ("Closed", lambda s, k: "=COUNTIFS(" + crit(s, k) + ")", "int"),
        ("Still open at data end",
         lambda s, k: "=COUNTIFS(" + entered(s, k) + ")-COUNTIFS(" + crit(s, k) + ")", "int"),
        (None, None, None),
        ("Win rate",
         lambda s, k: '=IFERROR(COUNTIFS(' + crit(s, k, GT0) + ')/COUNTIFS(' + crit(s, k) + '),"")', "pct1"),
        ("Average R per trade",
         lambda s, k: "=IFERROR(AVERAGEIFS(" + r_ + "," + crit(s, k) + '),"")', "num3"),
        ("Total R", lambda s, k: "=SUMIFS(" + r_ + "," + crit(s, k) + ")", "num1"),
        ("Profit factor",
         lambda s, k: "=IFERROR(SUMIFS(" + r_ + "," + crit(s, k, GT0) + ")/-SUMIFS("
                      + r_ + "," + crit(s, k, LE0) + '),"")', "num3"),
        ("Average win (R)",
         lambda s, k: "=IFERROR(AVERAGEIFS(" + r_ + "," + crit(s, k, GT0) + '),"")', "num2"),
        ("Average loss (R)",
         lambda s, k: "=IFERROR(AVERAGEIFS(" + r_ + "," + crit(s, k, LE0) + '),"")', "num2"),
        (None, None, None),
        ("Expectancy per trade ($1k risk)",
         lambda s, k: "=IFERROR(AVERAGEIFS(" + usd_ + "," + crit(s, k) + '),"")', "usd"),
        ("Total P&L ($1k risk)", lambda s, k: "=SUMIFS(" + usd_ + "," + crit(s, k) + ")", "usd"),
        (None, None, None),
        ("Stopped out", lambda s, k: "=COUNTIFS(" + crit(s, k, exit_is("STOP*")) + ")", "int"),
        ("Target reached", lambda s, k: "=COUNTIFS(" + crit(s, k, exit_is("TARGET*")) + ")", "int"),
        ("Closed by time stop", lambda s, k: "=COUNTIFS(" + crit(s, k, exit_is("TIME")) + ")", "int"),
        (None, None, None),
        ("Average hours held",
         lambda s, k: "=IFERROR(AVERAGEIFS(" + rng("bars_held") + "," + crit(s, k) + '),"")', "num1"),
        ("Average MAE (R against)",
         lambda s, k: "=IFERROR(AVERAGEIFS(" + rng("mae_r") + "," + crit(s, k) + '),"")', "num2"),
        ("Average MFE (R in favour)",
         lambda s, k: "=IFERROR(AVERAGEIFS(" + rng("mfe_r") + "," + crit(s, k) + '),"")', "num2"),
    ]

    # Each formula is written together with a cached result computed here in
    # Python. LibreOffice cannot load a workbook in this build environment (a
    # 100-cell file fails identically), so the usual recalculate-and-verify pass
    # is unavailable. Without cached values every formula cell would read back as
    # None to pandas and to most previewers. The cached numbers are cross-checked
    # against analyze.py - an independent implementation over the same logs - by
    # _verify_summary() below, and Excel recalculates them live on open.
    values = {}
    for _, sym, kind in books:
        values[(sym, kind)] = _book_values(all_rows[sym] if kind == "all" else sel_rows[sym])

    r = hdr_row + 1
    for label, fn, fmt in metrics:
        if label is None:
            r += 1
            continue
        ws.write(r, 0, label, f["label"])
        for i, (_, sym, kind) in enumerate(books):
            ws.write_formula(r, i + 1, fn(sym, kind), f[fmt], values[(sym, kind)][label])
        r += 1

    r += 1
    ws.write(r, 0, "Computed by analysis scripts, not by this sheet", f["h1"])
    for i in range(len(books)):
        ws.write(r, i + 1, "", f["h1"])
    r += 1
    for label, key, fmt, scale in [
        ("Max drawdown on cumulative R", "max_dd", "num1", 1),
        ("Gross average R (before costs)", "gross_avg_R", "num3", 1),
        ("Buy & hold over window", "buy_hold", "pct1", 0.01),
    ]:
        ws.write(r, 0, label, f["label"])
        for i, (_, sym, kind) in enumerate(books):
            a = analysis[sym]["all" if kind == "all" else "selective"]
            if key == "buy_hold":
                v = analysis[sym]["buy_hold_pct"] * scale
            elif key == "gross_avg_R":
                v = a["gross_avg_R"]
            else:
                v = _max_dd(all_rows[sym] if kind == "all" else sel_rows[sym])
            ws.write_number(r, i + 1, v, f[fmt])
        r += 1

    r += 1
    ws.write(r, 0, "Source: max drawdown and gross-of-cost R computed by backtest/analyze.py and "
                   "backtest/build_workbook.py over the same trade logs shown in this workbook. "
                   "Buy & hold is the close-to-close return of the 10,000-bar window. Drawdown is "
                   "path-dependent along the trade sequence and cannot be expressed as a "
                   "spreadsheet formula, so it is written as a value.", f["note"])
    ws.set_row(r, 40)

    r += 2
    ws.write(r, 0, "Read this before drawing conclusions", f["key"])
    r += 1
    for line in [
        "The 'All Trades' books lose money on all three symbols. Their GROSS average R - before any "
        "fee, slippage or funding - is within 0.04R of zero. Entering on every close has no edge to "
        "erode; costs simply make the absence of edge visible.",
        "The 'Selective' books are better but thin: +0.084R (ETH), +0.042R (LINK), -0.007R (SOL). "
        "Two of three are positive, none is comfortably so.",
        "All three assets fell hard over this window (ETH -30%, LINK -41%, SOL -52%). A short-tilted "
        "book looking good here is largely the market falling, not an edge. See Stability.",
    ]:
        ws.write(r, 0, line, f["wrap"])
        ws.set_row(r, 30)
        r += 1


def _book_values(rows):
    """Python-side results for every Summary metric, keyed by the metric label.

    These become the cached values of the corresponding formula cells. The keys
    must match the labels in write_summary exactly.
    """
    closed = [t for t in rows if t["status"] == "CLOSED"]
    rs = [float(t["r_multiple"]) for t in closed]
    usd = [float(t["pnl_usd"]) for t in closed]
    wins = [x for x in rs if x > 0]
    losses = [x for x in rs if x <= 0]
    gross_loss = -sum(losses)
    n = len(closed)

    def mean(xs):
        return sum(xs) / len(xs) if xs else ""

    def count_exit(pred):
        return sum(1 for t in closed if pred(t["exit_reason"]))

    return {
        "Trades entered": len(rows),
        "Closed": n,
        "Still open at data end": len(rows) - n,
        "Win rate": (len(wins) / n) if n else "",
        "Average R per trade": mean(rs),
        "Total R": sum(rs),
        "Profit factor": (sum(wins) / gross_loss) if gross_loss > 0 else "",
        "Average win (R)": mean(wins),
        "Average loss (R)": mean(losses),
        "Expectancy per trade ($1k risk)": mean(usd),
        "Total P&L ($1k risk)": sum(usd),
        "Stopped out": count_exit(lambda e: e.startswith("STOP")),
        "Target reached": count_exit(lambda e: e.startswith("TARGET")),
        "Closed by time stop": count_exit(lambda e: e == "TIME"),
        "Average hours held": mean([int(t["bars_held"]) for t in closed]),
        "Average MAE (R against)": mean([float(t["mae_r"]) for t in closed]),
        "Average MFE (R in favour)": mean([float(t["mfe_r"]) for t in closed]),
    }


def verify_summary(symbols, all_rows, sel_rows, analysis):
    """Cross-check the cached Summary values against analyze.py's independent run.

    Raises rather than shipping a workbook whose numbers disagree with the
    analysis that produced the written findings.
    """
    problems = []
    for sym, short in symbols:
        for kind, akey in (("all", "all"), ("sel", "selective")):
            v = _book_values(all_rows[sym] if kind == "all" else sel_rows[sym])
            a = analysis[sym][akey]
            checks = [
                ("closed n", v["Closed"], a["n"], 0),
                ("win %", v["Win rate"] * 100, a["win_pct"], 0.05),
                ("avg R", v["Average R per trade"], a["avg_R"], 5e-4),
                ("total R", v["Total R"], a["total_R"], 0.05),
                ("profit factor", v["Profit factor"], a["PF"], 5e-4),
                ("avg MAE", v["Average MAE (R against)"], a["avg_MAE_R"], 5e-3),
            ]
            for name, mine, theirs, tol in checks:
                if theirs is None or mine == "":
                    continue
                if abs(float(mine) - float(theirs)) > tol:
                    problems.append(f"{short}/{kind} {name}: workbook {mine} vs analyze.py {theirs}")
    if problems:
        raise AssertionError("Summary values disagree with analyze.py:\n  " + "\n  ".join(problems))
    return len(symbols) * 2 * 6


def _max_dd(rows):
    eq = peak = mdd = 0.0
    for t in rows:
        if t["status"] != "CLOSED":
            continue
        eq += float(t["r_multiple"])
        peak = max(peak, eq)
        mdd = max(mdd, peak - eq)
    return round(mdd, 1)


def write_findings(ws, f, analysis, robust):
    _title(ws, f, "Findings",
           "Seven conclusions from 28,497 simulated trades. Several point the opposite way from how they first look.")
    ws.set_column(0, 0, 4)
    ws.set_column(1, 1, 30)
    ws.set_column(2, 2, 108)

    mix = json.load(open(os.path.join(DATA, "exit_mix.json")))
    e, l, s = analysis["ETHUSDT"], analysis["LINKUSDT"], analysis["SOLUSDT"]

    findings = [
        ("1. Entering on every close has no edge at all",
         f"Not 'a small edge destroyed by fees' - no edge. The gross average R before any cost is "
         f"{e['all']['gross_avg_R']:+.3f} (ETH), {l['all']['gross_avg_R']:+.3f} (LINK), "
         f"{s['all']['gross_avg_R']:+.3f} (SOL). That is a coin flip. Net of costs it becomes "
         f"{e['all']['avg_R']:+.3f} / {l['all']['avg_R']:+.3f} / {s['all']['avg_R']:+.3f} R per trade, "
         f"because friction eats {e['cost_share_of_R_pct']:.0f}-{l['cost_share_of_R_pct']:.0f}% of one R "
         f"every time you press the button. Total damage at $1,000 risk per trade: about "
         f"$673k, $892k and $356k respectively. The mandate itself is the problem, not the execution."),

        ("2. The filter carries everything, and it is thin",
         f"Restricting to conviction >= 6.0 keeps only ~8% of bars and flips ETH and LINK positive: "
         f"{e['selective']['avg_R']:+.3f} and {l['selective']['avg_R']:+.3f} R per trade, profit factors "
         f"{e['selective']['PF']:.2f} and {l['selective']['PF']:.2f}. SOL stays negative at "
         f"{s['selective']['avg_R']:+.3f}. So the entry filter is worth roughly 0.15R per trade - real, but "
         f"the surviving edge is small enough that a slightly worse fee tier erases it."),

        ("3. My own conviction score is miscalibrated at the top end",
         "Conviction 6-8 is the sweet spot on all three symbols (+0.13 to +0.25 R). Conviction 8-10 is "
         "WORSE, and negative on ETH (-0.15R) and SOL (-0.43R in the 9-10 bucket). The score is not "
         "monotonic with outcome. The setups that look most obvious - every box ticked, ADX screaming, "
         "trend perfectly stacked - are the ones most likely to be late. If you take one behavioural "
         "lesson from this study, take that one: do not size up on the trade that looks easiest."),

        ("4. Almost nothing survives the time split",
         "Cutting the sample in half and recomputing independently, most setup x direction combinations "
         "flip sign between the halves. BREAKOUT/LONG on ETH goes +1.14R in H1 to -0.52R in H2. "
         "TREND_PULLBACK/LONG on SOL goes +0.04R to -0.47R. The only combination positive in 5 of 6 "
         "half-samples is TREND_PULLBACK/SHORT. Treat the per-combination numbers on the Setup Breakdown "
         "tab as description of what happened, not as prediction of what will."),

        ("5. The short bias is the market falling, not an edge",
         f"Shorts beat longs on trend pullbacks across all three symbols. In a window where ETH fell "
         f"{e['buy_hold_pct']:.0f}%, LINK {l['buy_hold_pct']:.0f}% and SOL {s['buy_hold_pct']:.0f}%, that is "
         f"what you would expect from any trend-following rule, and it tells you nothing about whether the "
         f"rule works in a rising market. This study cannot answer that question - the sample contains no "
         f"sustained bull phase. Do not carry the short tilt forward."),

        ("6. The MAE statistic is a trap, and I checked",
         f"Trades that eventually won rarely went far against first: median MAE "
         f"{robust['ETHUSDT']['winner_mae']['median']:.2f}R, and "
         f"{robust['ETHUSDT']['winner_mae']['pct_within_0_50R']:.0f}% of winners never went beyond 0.50R "
         f"against. The obvious inference is 'tighten the stops, you are giving away 0.5R of room you never "
         f"need'. That inference is WRONG. Every 0.70x-stop configuration in the sweep is negative on all "
         f"three symbols. The MAE figure is survivorship: it only measures trades the stop did not kill, so "
         f"it cannot tell you what a tighter stop would have destroyed. The direct test can, and it says "
         f"wider is better."),

        ("7. The real exit is the clock, not the target",
         f"The sweep optimum sits at a moderately wider stop (x1.3 to x1.6) with a far target - but look at "
         f"where the money actually comes from. At a wide-stop setting only "
         f"{mix['ETHUSDT']['sweep_optimum'].get('TARGET', {}).get('share_pct', 0):.0f}-"
         f"{mix['SOLUSDT']['sweep_optimum'].get('TARGET', {}).get('share_pct', 0):.0f}% of trades ever reach "
         f"the target, while "
         f"{mix['ETHUSDT']['sweep_optimum'].get('TIME', {}).get('share_pct', 0):.0f}-"
         f"{mix['LINKUSDT']['sweep_optimum'].get('TIME', {}).get('share_pct', 0):.0f}% exit on the time stop "
         f"averaging +3.5% to +5.2% each. The wide stop is not finding better targets; it is keeping the "
         f"trade alive long enough for the clock to close it in profit. The take-profit level is nearly "
         f"decorative. If I rebuilt this, I would drop fixed targets for a trailing or time-based exit and "
         f"widen the stop, rather than hunting for a better R multiple."),
    ]

    findings.append((
        "8. Aiming at structure makes you right more often and richer less often",
        "The stop in this system reads price action per candle; the target did not - it was the stop distance "
        "times a per-setup constant, giving only four distinct reward ratios across 28,497 trades. So a "
        "structure-aware target was built (nearest confirmed swing level within 240 bars, ~280 distinct ratios) "
        "and tested on identical entries and stops. It raised the win rate on the ETH selective book from 34.1% "
        "to 40.5% and the target-hit rate from 31% to 38% - and LOWERED average R from +0.084 to +0.048. The "
        "nearest level is usually closer than the fixed multiple (median 1.5R vs 2.5R), so it clips winners "
        "while every loser still costs a full -1R. Using structure only when it EXTENDS the target is "
        "marginally best of the three on all three symbols, by about +0.005R - consistent in sign, far too "
        "small to act on. Full table on the Target Method tab."
    ))

    r = 3
    for head, body in findings:
        ws.write(r, 1, head, f["h1"])
        ws.write(r, 2, "", f["h1"])
        r += 1
        ws.write(r, 2, body, f["wrap"])
        ws.set_row(r, 12.5 * (len(body) // 105 + 1))
        r += 2

    ws.write(r, 1, "What I would actually do with this", f["key"])
    ws.write(r, 2, "", f["key"])
    r += 1
    for line in [
        "Stop trading the always-on mandate. It is a fee-payment machine with no underlying edge. If you "
        "want exposure on every bar, hold spot - it costs nothing and did better than the always-on book "
        "on all three symbols.",
        "Trade the filter, not the schedule. Roughly 8% of hourly closes carried anything worth acting on. "
        "The other 92% were noise that the mandate forced me to pay for.",
        "Distrust your best-looking setups. The 8-10 conviction bucket underperformed the 6-8 bucket on "
        "every symbol. Size flat across qualifying setups rather than scaling with confidence.",
        "Fix the exit before the entry. Exit design moved results more than any entry refinement in this "
        "study: on identical entry signals the sweep spans -0.07R to +0.21R per trade. Widening the stop "
        "from the shipped geometry lifts the 6-8 band from +0.177R to +0.257R - worth having, but note "
        "that it still does not clear the bootstrap significance bar.",
        "Re-run this over a rising market before believing any directional conclusion. Every symbol here "
        "fell 30-52%, and that fact contaminates every direction-dependent number in the workbook.",
    ]:
        ws.write(r, 2, "- " + line, f["wrap"])
        ws.set_row(r, 12.5 * (len(line) // 105 + 1))
        r += 1


def _stat_table(ws, f, r, title, cols, rows_data, note=None):
    ws.write(r, 1, title, f["h1"])
    for i in range(len(cols)):
        ws.write(r, i + 2, "", f["h1"])
    r += 1
    for i, c in enumerate(cols):
        ws.write(r, i + 1, c, f["hdr"])
    ws.set_row(r, 28)
    r += 1
    for row in rows_data:
        ws.write(r, 1, row[0], f["label"])
        for i, v in enumerate(row[1:], start=2):
            if v is None:
                ws.write(r, i, "", f["text"])
            elif isinstance(v, str):
                ws.write(r, i, v, f["ctr"])
            elif i == 2:
                ws.write_number(r, i, v, f["int"])
            else:
                ws.write_number(r, i, v, f["num3"])
        r += 1
    if note:
        ws.write(r, 1, note, f["note"])
        r += 1
    return r + 1


def write_breakdown(wb, f, symbols, analysis):
    ws = wb.add_worksheet("Setup Breakdown")
    _title(ws, f, "Setup Breakdown",
           "Closed trades only. 'Gross R' strips fees, slippage and funding, isolating signal quality from friction.")
    ws.set_column(0, 0, 3)
    ws.set_column(1, 1, 30)
    ws.set_column(2, 9, 13)

    cols = ["Bucket", "n", "Win %", "Avg R", "Gross R", "Total R", "Profit factor", "Avg MAE R", "Avg MFE R"]
    r = 3
    for sym, short in symbols:
        a = analysis[sym]
        ws.write(r, 1, f"{short}  -  buy & hold over window: {a['buy_hold_pct']:+.1f}%", f["title"])
        r += 2
        for key, title in [("by_setup", f"{short}: by setup"),
                           ("by_direction", f"{short}: by direction"),
                           ("by_exit", f"{short}: by exit reason"),
                           ("by_conviction", f"{short}: by conviction bucket"),
                           ("selective_by_setup_dir", f"{short}: selective book, setup x direction")]:
            data = []
            for k in sorted(a[key]):
                d = a[key][k]
                if not d:
                    continue
                data.append([k, d["n"], d["win_pct"] / 100.0, d["avg_R"], d["gross_avg_R"],
                             d["total_R"], d["PF"], d["avg_MAE_R"], d["avg_MFE_R"]])
            r = _stat_table(ws, f, r, title, cols, data)
        r += 1

    ws.write(r, 1, "Source: computed by backtest/analyze.py from the trade logs in this workbook. "
                   "Win % is stored as a fraction. Profit factor is blank where there were no losing trades.",
             f["note"])


def write_sweep(wb, f, symbols, sweep):
    ws = wb.add_worksheet("Stop-Target Sweep")
    _title(ws, f, "Stop Width x Target Sensitivity",
           "Selective book only. Scored in average R per trade - the correct metric when a fixed dollar "
           "amount is risked on every trade.")
    ws.set_column(0, 0, 3)
    ws.set_column(1, 1, 24)
    ws.set_column(2, 12, 12)

    scales = sorted({float(k.split("|")[0]) for k in sweep["ETHUSDT"]})
    targets = sorted({float(k.split("|")[1]) for k in sweep["ETHUSDT"]})

    r = 3
    ws.write(r, 1, "How to read this", f["label"])
    ws.write(r, 2, "Each cell re-runs the identical entry signals with the stop distance multiplied by the "
                   "row factor and the target set to the column's R multiple. 1.00 is the geometry actually "
                   "traded in the logs. The optimum is interior - it turns over rather than running to the "
                   "edge - which is what makes it worth reporting.", f["wrap"])
    ws.set_row(r, 42)
    r += 1
    ws.write(r, 1, "Which metric", f["label"])
    ws.write(r, 2, "Average R, because this study risks a fixed $1,000 per trade: position size shrinks as "
                   "the stop widens, so P&L = R x risk and average R is proportional to expected profit. "
                   "Average net % per trade - the score used in an earlier version of this tab - is correct "
                   "only under constant-NOTIONAL sizing, where a wider stop does not shrink the position. "
                   "The distinction matters: net % favoured stop x2.0-3.0, average R favours x1.3-1.6 with a "
                   "far target, and net % made the gain from widening look several times larger than it is.",
             f["wrap"])
    ws.set_row(r, 56)
    r += 2

    for sym, short in symbols:
        ws.write(r, 1, f"{short}: average R per trade", f["h1"])
        for i in range(len(targets) + 1):
            ws.write(r, i + 2, "", f["h1"])
        r += 1
        ws.write(r, 1, "Stop x", f["hdr"])
        for i, t in enumerate(targets):
            ws.write(r, i + 2, f"Target {t:g}R", f["hdr"])
        ws.set_row(r, 28)
        r += 1

        best = max(sweep[sym].values(), key=lambda d: d["avg_R"])["avg_R"]
        for sc in scales:
            ws.write_number(r, 1, sc, f["num2"])
            for i, t in enumerate(targets):
                d = sweep[sym][f"{sc}|{t}"]
                v = d["avg_R"]
                fmt = f["good"] if v == best else (f["bad"] if v < 0 else f["num3"])
                ws.write_number(r, i + 2, v, fmt)
            r += 1
        ws.write(r, 1, f"Best: {best:+.3f} R per trade (highlighted). Win rate rises with stop width on "
                       f"every symbol, from ~30% at the tightest to ~45% at the widest.", f["note"])
        r += 3

    ws.write(r, 1, "Source: backtest/sweep.py, 56 configurations per symbol over the same entry signals. "
                   "Each cell also records average net % and profit factor in data/sweep.json.", f["note"])
    r += 2
    ws.write(r, 1, "The trap", f["key"])
    ws.write(r, 2, "", f["key"])
    r += 1
    ws.write(r, 2, "Tightening the stop is negative on all three symbols at every target - see the 0.70 and "
                   "0.85 rows. That directly contradicts what the MAE statistics appear to suggest "
                   "(see Findings, item 6), and the sweep is the evidence that settles it.", f["wrap"])
    ws.set_row(r, 42)
    r += 2
    ws.write(r, 1, "A second trap, which caught me", f["key"])
    ws.write(r, 2, "", f["key"])
    r += 1
    ws.write(r, 2, "An earlier version of this tab scored the grid in average net % per trade and concluded "
                   "the optimum was a stop around x2.0-2.5. That was wrong for this study's sizing. Net % is "
                   "the return on notional; with a fixed dollar risked per trade, widening the stop shrinks "
                   "the position, so net % credits a wide stop for a move you would have been too small to "
                   "fully capture. Re-scored in average R the optimum moves in to x1.3-x1.6 and the benefit "
                   "of widening shrinks from apparently several-fold to about +0.08R. Same data, same "
                   "trades, different unit - and a materially different recommendation.", f["wrap"])
    ws.set_row(r, 70)


def write_stability(wb, f, symbols, robust):
    ws = wb.add_worksheet("Stability")
    _title(ws, f, "Time-Split Stability",
           "The sample halved and recomputed independently. A rule that only works in one half describes that half.")
    ws.set_column(0, 0, 3)
    ws.set_column(1, 1, 32)
    ws.set_column(2, 8, 13)

    r = 3
    for sym, short in symbols:
        d = robust[sym]
        cols = ["Book / half", "n", "Win %", "Avg R", "Total R", "Profit factor"]
        data = []
        for book, label in [("always_on", "All trades"), ("selective", "Selective")]:
            for half in ("H1", "H2"):
                b = d[book][half]
                data.append([f"{label} - {half}", b["n"], b["win_pct"] / 100.0,
                             b["avg_R"], b["total_R"], b["PF"]])
        r = _stat_table(ws, f, r, f"{short}: whole-book stability", cols, data)

        combo_cols = ["Setup x direction", "H1 n", "H1 avg R", "H2 n", "H2 avg R", "Sign stable?"]
        cdata = []
        for k in sorted(d["combo_stability"]):
            cs = d["combo_stability"][k]
            cdata.append([k, cs["H1"]["n"], cs["H1"]["avg_R"], cs["H2"]["n"], cs["H2"]["avg_R"],
                          "YES" if cs["sign_stable"] else "NO"])
        r = _stat_table(ws, f, r, f"{short}: selective combinations, both halves", combo_cols, cdata,
                        note="Combinations with fewer than 15 trades in either half are omitted as too "
                             "small to read.")

        wm = d["winner_mae"]
        mae_cols = ["Metric", "Value"]
        mdata = [
            ["Median MAE of eventual winners (R)", wm["median"]],
            ["75th percentile", wm["p75"]],
            ["90th percentile", wm["p90"]],
            ["95th percentile", wm["p95"]],
            ["Winners never exceeding 0.50R against", wm["pct_within_0_50R"] / 100.0],
            ["Winners never exceeding 0.75R against", wm["pct_within_0_75R"] / 100.0],
        ]
        r = _stat_table(ws, f, r, f"{short}: how far winners went against first", mae_cols, mdata,
                        note="Survivorship warning: this only measures trades the stop did not kill, so it "
                             "cannot tell you what a tighter stop would have destroyed. See the sweep.")
        r += 1

    ws.write(r, 1, "Source: backtest/robustness.py. Percentages stored as fractions.", f["note"])


def write_targets(wb, f, symbols):
    """Fixed-R vs structure-derived targets, on identical entries and stops."""
    ws = wb.add_worksheet("Target Method")
    _title(ws, f, "Does aiming at structure beat a fixed R multiple?",
           "Same entries, same stops, same costs. Only the take-profit changes between the three runs.")
    ws.set_column(0, 0, 3)
    ws.set_column(1, 1, 26)
    ws.set_column(2, 8, 14)

    cmp_ = json.load(open(os.path.join(DATA, "target_comparison.json")))

    r = 3
    ws.write(r, 1, "Why this tab exists", f["label"])
    ws.write(r, 2, "The stop in this system reads price action directly: it is sized by the bar's ATR and then "
                   "moved to sit beyond the last confirmed swing pivot. The take-profit did not - it was simply "
                   "the stop distance multiplied by a constant chosen per setup type (1.3R, 1.5R, 2.5R or 3.0R), "
                   "so only four distinct reward ratios existed across 28,497 trades. That is a fair criticism, "
                   "so it was tested rather than argued about.", f["wrap"])
    ws.set_row(r, 56)
    r += 2

    ws.write(r, 1, "The three methods", f["h1"])
    for i in range(6):
        ws.write(r, i + 2, "", f["h1"])
    r += 1
    for name, desc in [
        ("fixed R", "Target = stop distance x the setup's R multiple. Four distinct ratios. This is what the "
                    "trade logs in this workbook use."),
        ("structure", "Target = the nearest confirmed swing high above (long) or swing low below (short) within "
                      "240 bars, placed 0.15 ATR in front of the level. ~280 distinct ratios from 1.2R to 6.0R. "
                      "Falls back to fixed R when no level is in range (~27% of trades)."),
        ("structure extend", "Same, but the level is only used when it is FARTHER than the fixed-R target. A "
                             "nearer wall is ignored."),
    ]:
        ws.write(r, 1, name, f["label"])
        ws.write(r, 2, desc, f["wrap"])
        ws.set_row(r, 12.5 * (len(desc) // 95 + 2))
        r += 1
    r += 1

    cols = ["Symbol / book", "Method", "n", "Win %", "Avg R", "Total R", "Profit factor", "Target hit %"]
    data = []
    for sym, short in symbols:
        for book, bl in (("all", "all trades"), ("sel", "selective")):
            for mode, ml in (("fixed_r", "fixed R"), ("structure", "structure"),
                             ("structure_extend", "structure extend")):
                b = cmp_[sym][mode][book]
                data.append([f"{short} {bl}", ml, b["n"], b["win_pct"] / 100.0, b["avg_R"],
                             b["total_R"], b["PF"], b["target_hit_pct"] / 100.0])
    ws.write(r, 1, "Results", f["h1"])
    for i in range(len(cols)):
        ws.write(r, i + 2, "", f["h1"])
    r += 1
    for i, c in enumerate(cols):
        ws.write(r, i + 1, c, f["hdr"])
    ws.set_row(r, 28)
    r += 1
    for row in data:
        ws.write(r, 1, row[0], f["label"])
        ws.write(r, 2, row[1], f["ctr"])
        ws.write_number(r, 3, row[2], f["int"])
        ws.write_number(r, 4, row[3], f["pct1"])
        ws.write_number(r, 5, row[4], f["num3"])
        ws.write_number(r, 6, row[5], f["num1"])
        if row[6] is not None:
            ws.write_number(r, 7, row[6], f["num3"])
        ws.write_number(r, 8, row[7], f["pct1"])
        r += 1
    r += 1

    ws.write(r, 1, "The result, and why", f["key"])
    ws.write(r, 2, "", f["key"])
    r += 1
    for line in [
        "Aiming at the nearest structural level makes you RIGHT more often and RICHER less often. On the ETH "
        "selective book, win rate rises from 34.1% to 40.5% and the target-hit rate from 31% to 38% - but "
        "average R falls from +0.084 to +0.048.",
        "The mechanism is simple: the nearest swing level is usually closer than the fixed multiple. Median "
        "structure ratio is 1.5R against 2.5R for trend pullbacks. So the method converts large winners into "
        "small ones while leaving every loser at a full -1R. In a system whose profitability lives entirely in "
        "the right tail, that is a losing trade.",
        "'Structure extend' - use the level only when it is farther away, ignore it when it is nearer - is "
        "marginally the best of the three on the selective book of all three symbols (+0.089 / +0.047 / -0.004 "
        "against +0.084 / +0.042 / -0.007). The improvement is about +0.005R, which is noise. It is consistent "
        "in sign across three symbols, which is mildly encouraging, and far too small to act on.",
        "Conclusion: the fixed-R target stays. Not because it is elegant, but because the price-action-aware "
        "alternative was tested head-to-head on identical entries and did not beat it. This is also consistent "
        "with the sweep and the exit-mix analysis, which both say the same thing from different angles - what "
        "makes money here is letting winners run, not being right more often.",
    ]:
        ws.write(r, 2, "- " + line, f["wrap"])
        ws.set_row(r, 12.5 * (len(line) // 95 + 1))
        r += 1

    r += 1
    ws.write(r, 1, "Source: backtest/compare_targets.py. Percentages stored as fractions.", f["note"])


def write_h1(wb, f):
    """The pre-registered entry hypothesis, and its failure."""
    ws = wb.add_worksheet("Hypothesis H1")
    _title(ws, f, "H1 - liquidation-wick reversion (pre-registered, then falsified)",
           "The hypothesis and its success criteria were committed to git BEFORE the test was run.")
    ws.set_column(0, 0, 3)
    ws.set_column(1, 1, 34)
    ws.set_column(2, 12, 12)

    d = json.load(open(os.path.join(DATA, "hypothesis_h1.json")))

    r = 3
    for label, body in [
        ("Why a new hypothesis",
         "Everything else in this workbook shares one origin: a trend/regime classifier on EMAs, ADX and "
         "RSI. Its GROSS average R, before any cost, was within 0.04R of zero across 28,461 trades and "
         "negative out of sample. That is not a cost or exit problem - trend continuation on hourly "
         "closes in these assets is a coin flip, and every refinement since was reducing the cost of "
         "trading one. A new hypothesis had to come from a different source of edge."),
        ("The reasoning",
         "If a signal is a coin flip, the counterparty is usually as informed as you are. So look for "
         "trades where the counterparty is not choosing to trade at all. Leveraged perpetuals produce "
         "forced liquidations: when price moves against crowded leverage, liquidation engines emit "
         "market orders regardless of price into whatever depth exists. That spike is margin arithmetic, "
         "not informed repricing, so once the forced flow is exhausted there is no reason for price to "
         "stay there."),
        ("The rule",
         "An hourly bar whose wick is at least 1.0 ATR, makes up at least half the bar's range, closes "
         "back in the recovering half of that range, on volume at least 1 sigma above normal. Fade the "
         "wick. No trend, ADX or EMA condition - adding one would smuggle the old hypothesis back in. "
         "Stop beyond the wick extreme plus 0.25 ATR, target 2.0R, 48-bar time stop."),
        ("Pre-registered criteria",
         "SUPPORTED required mean R > 0 with the 95% bootstrap CI excluding zero on the PRIOR window - "
         "the only dataset no design decision in this study was ever fitted to. SUGGESTIVE required a "
         "positive mean with consistent signs across all three symbols and both replication datasets. "
         "Anything else counts as NOT SUPPORTED. A pooled n under 100 would have been reported as "
         "underpowered rather than as a result."),
    ]:
        ws.write(r, 1, label, f["label"])
        ws.write(r, 2, body, f["wrap"])
        ws.set_row(r, 12.5 * (len(body) // 95 + 2))
        r += 1
    r += 1

    cols = ["Dataset / book", "n", "Win %", "Breakeven %", "Cost as % of 1R",
            "Gross R", "Avg R", "Total R", "Profit factor", "CI low", "CI high", "P(>0)"]
    ws.write(r, 1, "Results", f["h1"])
    for i in range(len(cols)):
        ws.write(r, i + 2, "", f["h1"])
    r += 1
    for i, c in enumerate(cols):
        ws.write(r, i + 1, c, f["hdr"])
    ws.set_row(r, 30)
    r += 1

    rows = [
        ("PRIOR - market entry (PRIMARY)", "1h_prior", "MARKET"),
        ("PRIOR - limit entry", "1h_prior", "LIMIT"),
        ("PRIOR - ETH", "1h_prior", "market_ETHUSDT"),
        ("PRIOR - LINK", "1h_prior", "market_LINKUSDT"),
        ("PRIOR - SOL", "1h_prior", "market_SOLUSDT"),
        ("MAIN - market entry", "1h", "MARKET"),
        ("MAIN - limit entry", "1h", "LIMIT"),
        ("15m - market entry", "15m", "MARKET"),
        ("15m - limit entry", "15m", "LIMIT"),
    ]
    for lab, win, key in rows:
        s = d[win].get(key)
        if not s:
            continue
        ws.write(r, 1, lab, f["label"])
        ws.write_number(r, 2, s["n"], f["int"])
        ws.write_number(r, 3, s["win"] / 100.0, f["pct1"])
        ws.write_number(r, 4, s["be"] / 100.0, f["pct1"])
        ws.write_number(r, 5, s["cost"] / 100.0, f["pct1"])
        ws.write_number(r, 6, s["gross_R"], f["good"] if s["gross_R"] > 0 else f["bad"])
        ws.write_number(r, 7, s["avg"], f["good"] if s["avg"] > 0 else f["bad"])
        ws.write_number(r, 8, s["tot"], f["num1"])
        ws.write_number(r, 9, s["pf"], f["num3"])
        ws.write_number(r, 10, s["lo"], f["num3"])
        ws.write_number(r, 11, s["hi"], f["num3"])
        ws.write_number(r, 12, s["p_pos"] / 100.0, f["pct1"])
        r += 1
    r += 2

    ws.write(r, 1, "Verdict: NOT SUPPORTED", f["key"])
    ws.write(r, 2, "", f["key"])
    r += 1
    p = d["1h_prior"]["MARKET"]
    for line in [
        f"On the primary out-of-sample window H1 returns {p['avg']:+.3f} R over {p['n']} trades, 95% CI "
        f"[{p['lo']:+.3f}, {p['hi']:+.3f}]. The interval includes zero and the point estimate is "
        f"negative. Win rate {p['win']:.1f}% against a {p['be']:.1f}% breakeven.",
        "This is a real negative result, not an underpowered one. 393 trades clears the pre-registered "
        "floor of 100 comfortably, so the hypothesis got a fair test and failed it.",
        "It is worse than merely unsupported. On both replication datasets H1 is SIGNIFICANTLY negative "
        "- MAIN at -0.238 R with CI [-0.366, -0.113], and 15m at -0.202 R with CI [-0.391, -0.014]. "
        "Both intervals exclude zero on the losing side.",
        "Per-symbol signs are inconsistent on the primary window (ETH -0.063, LINK +0.037, SOL -0.232), "
        "so it fails the weaker SUGGESTIVE criterion too.",
        "The mechanism was wrong. Gross R - before any fee - is -0.024 on PRIOR and -0.160 on MAIN, so "
        "this is not costs eating a thin edge. Fading an absorbed wick is simply the wrong side of the "
        "trade. A large wick that closes back inside its range apparently carries information rather "
        "than being noise to fade.",
        "That last observation obviously invites testing the INVERSE. It is not reported here, and it "
        "was not run, because the pre-registration explicitly forbids reporting a flipped variant as "
        "though it were the registered one. The inverse is also not inferable from these numbers: "
        "reversing direction changes which bars hit the stop before the target, and the stop/target "
        "geometry is not symmetric. It would need its own pre-registration and its own test.",
    ]:
        ws.write(r, 2, "- " + line, f["wrap"])
        ws.set_row(r, 12.5 * (len(line) // 100 + 1))
        r += 1

    r += 1
    ws.write(r, 1, "Source: backtest/hypothesis_h1.py, criteria in backtest/PREREGISTRATION.md. The "
                   "pre-registration was committed in a separate, earlier commit containing no results.",
             f["note"])


def write_v3(wb, f):
    """RANGE_FADE deleted for good, plus resting-limit entries where they fit."""
    ws = wb.add_worksheet("System v3")
    _title(ws, f, "System v3 - RANGE_FADE deleted, limit entries where the setup justifies waiting",
           "The closest thing to a real finding in this study, and it still is not significant.")
    ws.set_column(0, 0, 3)
    ws.set_column(1, 1, 36)
    ws.set_column(2, 11, 13)

    d = json.load(open(os.path.join(DATA, "system_v3.json")))
    books, grid, paired = d["books"], d["grid"], d["paired"]

    r = 3
    for label, body in [
        ("RANGE_FADE: deleted",
         "Removed from the classifier outright, not filtered downstream. Those bars now fall through to "
         "DEFAULT, which never scores high enough to reach the selective book. This is the one change "
         "that replicated out of sample, and it replicated because it is arithmetic: its breakeven win "
         "rate exceeded its achieved win rate in every dataset tested."),
        ("Limit entries: the reasoning",
         "A pullback or a fade is a bet that price comes BACK to you, so paying the close is paying up "
         "for something the thesis says will be cheaper shortly. A breakout is the opposite bet - price "
         "leaves and does not return - so a limit below the close systematically misses exactly the "
         "trades the setup exists to catch. TREND_PULLBACK, EXHAUSTION and DEFAULT therefore rest a "
         "limit 0.25 ATR better than the close, good for 6 bars; BREAKOUT still crosses the spread."),
        ("Why it matters twice",
         "Friction has been the dominant term in every part of this study. A resting order is a maker "
         "order: no slippage and roughly half the fee. Exits are now costed by how they actually happen "
         "too - a target is a resting limit, a stop or a time exit is a market order. Cost falls from "
         "6.6% of one R to 4.9% on the out-of-sample window."),
        ("Parameters chosen in advance",
         "0.25 ATR offset and 6-bar expiry were fixed BEFORE any limit-entry result was looked at, as "
         "the natural middle of a plausible range - not by picking the best cell of the grid below. "
         "After the previous round of this study was caught recycling its out-of-sample set, that "
         "discipline is the whole point."),
        ("Fill modelling",
         "The order rests from the next bar and can never fill on the signal bar. A buy fills only if "
         "the bar's low reaches the limit, and fills AT the limit even when the bar opened below it - "
         "the improvement is not credited. If the fill bar also touches the stop, the trade is assumed "
         "filled and then stopped inside that bar. Unfilled by expiry means no trade at all."),
    ]:
        ws.write(r, 1, label, f["label"])
        ws.write(r, 2, body, f["wrap"])
        ws.set_row(r, 12.5 * (len(body) // 95 + 2))
        r += 1
    r += 1

    cols = ["Configuration", "n", "Fill %", "Win %", "Breakeven %", "Cost as % of 1R",
            "Avg R", "Total R", "Profit factor", "CI low", "CI high", "P(>0)"]

    for suffix, label in [("1h_prior", "PRIOR window (out of sample - the honest test)"),
                          ("1h", "MAIN window (in-sample)")]:
        ws.write(r, 1, label, f["h1"])
        for i in range(len(cols)):
            ws.write(r, i + 2, "", f["h1"])
        r += 1
        for i, c in enumerate(cols):
            ws.write(r, i + 1, c, f["hdr"])
        ws.set_row(r, 30)
        r += 1
        for tag, s in books[suffix].items():
            if not s:
                continue
            ws.write(r, 1, tag, f["label"])
            ws.write_number(r, 2, s["n"], f["int"])
            ws.write_number(r, 3, s["fill_rate"] / 100.0, f["pct1"])
            ws.write_number(r, 4, s["win"] / 100.0, f["pct1"])
            ws.write_number(r, 5, s["be"] / 100.0, f["pct1"])
            ws.write_number(r, 6, s["cost"] / 100.0, f["pct1"])
            ws.write_number(r, 7, s["avg"], f["good"] if s["avg"] > 0 else f["bad"])
            ws.write_number(r, 8, s["tot"], f["num1"])
            ws.write_number(r, 9, s["pf"], f["num3"])
            ws.write_number(r, 10, s["lo"], f["num3"])
            ws.write_number(r, 11, s["hi"], f["num3"])
            ws.write_number(r, 12, s["p_pos"] / 100.0, f["pct1"])
            r += 1
        r += 1

    ws.write(r, 1, "Paired test - same signals, both entry methods", f["h1"])
    for i in range(9):
        ws.write(r, i + 2, "", f["h1"])
    r += 1
    ws.write(r, 2, "Comparing two independent averages wastes most of the information here. Running both "
                   "entry methods over the IDENTICAL signal list and measuring the per-signal difference "
                   "is far more powerful. Unfilled limit orders score zero, so the cost of missing a "
                   "trade is charged against the limit method rather than hidden.", f["wrap"])
    ws.set_row(r, 42)
    r += 1
    for i, c in enumerate(["Window / design", "Signals", "Unfilled", "Market avg R",
                           "Limit avg R", "Gain", "CI low", "CI high", "P(gain > 0)"]):
        ws.write(r, i + 1, c, f["hdr"])
    ws.set_row(r, 30)
    r += 1
    for key, lab in [("1h_prior|pullbacks", "PRIOR - limit on pullbacks only"),
                     ("1h_prior|all", "PRIOR - limit on all setups"),
                     ("1h|pullbacks", "MAIN - limit on pullbacks only"),
                     ("1h|all", "MAIN - limit on all setups")]:
        p = paired[key]
        ws.write(r, 1, lab, f["label"])
        ws.write_number(r, 2, p["signals"], f["int"])
        ws.write_number(r, 3, p["unfilled"], f["int"])
        ws.write_number(r, 4, p["market_avg"], f["num3"])
        ws.write_number(r, 5, p["limit_avg"], f["num3"])
        ws.write_number(r, 6, p["mean"], f["good"] if p["mean"] > 0 else f["bad"])
        ws.write_number(r, 7, p["lo"], f["num3"])
        ws.write_number(r, 8, p["hi"], f["num3"])
        ws.write_number(r, 9, p["p_pos"] / 100.0, f["pct1"])
        r += 1
    r += 1

    cb = paired["combined"]
    ws.write(r, 1, "Both windows combined - 20,000 hours, "
                   f"{cb['signals']:,} signals", f["h1"])
    for i in range(9):
        ws.write(r, i + 2, "", f["h1"])
    r += 1
    for i, c in enumerate(["Question", "Estimate", "CI low", "CI high", "P(>0)", "Verdict"]):
        ws.write(r, i + 1, c, f["hdr"])
    ws.set_row(r, 30)
    r += 1
    for q, k in [("Does limit entry beat market entry?", "gain"),
                 ("Is the limit book profitable in absolute terms?", "level")]:
        v = cb[k]
        ws.write(r, 1, q, f["label"])
        ws.write_number(r, 2, v["mean"], f["good"] if v["mean"] > 0 else f["bad"])
        ws.write_number(r, 3, v["lo"], f["num3"])
        ws.write_number(r, 4, v["hi"], f["num3"])
        ws.write_number(r, 5, v["p_pos"] / 100.0, f["pct1"])
        ws.write(r, 6, "significant" if v["lo"] > 0 else "NOT significant", f["ctr"])
        r += 1
    r += 1

    ws.write(r, 1, "Parameter grid - context only, not the basis of any claim", f["h1"])
    for i in range(6):
        ws.write(r, i + 2, "", f["h1"])
    r += 1
    ws.write(r, 1, "Offset (ATR)", f["hdr"])
    for i, (suffix, lab) in enumerate([("1h_prior", "PRIOR"), ("1h", "MAIN")]):
        for j, e in enumerate((3, 6, 12)):
            ws.write(r, 2 + i * 3 + j, f"{lab} exp={e}", f["hdr"])
    ws.set_row(r, 30)
    r += 1
    for off in (0.15, 0.25, 0.40, 0.60):
        ws.write_number(r, 1, off, f["num2"])
        for i, suffix in enumerate(("1h_prior", "1h")):
            for j, e in enumerate((3, 6, 12)):
                s = grid[suffix].get(f"{off}|{e}")
                if s:
                    ws.write_number(r, 2 + i * 3 + j, s["avg"],
                                    f["good"] if s["avg"] > 0 else f["bad"])
        r += 1
    ws.write(r, 1, "Every cell is positive on both windows, so the improvement does not depend on the "
                   "parameter choice - which is more reassuring than any single best cell would be.",
             f["note"])
    r += 2

    ws.write(r, 1, "The verdict", f["key"])
    ws.write(r, 2, "", f["key"])
    r += 1
    for line in [
        "Deleting RANGE_FADE was not enough on its own. With market entries the out-of-sample book is "
        "still -0.013 R. That change removes a broken component; it does not create an edge.",
        "Limit entries do more. On the out-of-sample window they flip the book from -0.013 R to +0.010 R, "
        "and on the main window from +0.051 R to +0.101 R. The direction is the same on both windows and "
        "in all 12 cells of the parameter grid.",
        "Combined over 20,000 hours and 4,421 signals, limit entry beats market entry by +0.030 R per "
        "signal with P(gain > 0) = 93.8%. That is the strongest result anywhere in this study - and it "
        "still misses the 95% bar. It is also the only result with a mechanical explanation rather than "
        "a statistical one: maker fees instead of taker, no slippage, and a better fill price.",
        "Restricting limits to pullbacks and fades - the a-priori design choice - beat applying them "
        "everywhere on the out-of-sample window (+0.022 against +0.016), even though limit-everything "
        "looked better in-sample. The reasoning held up where the fitting did not.",
        "But the book itself is still not profitable with confidence: +0.048 R combined, CI "
        "[-0.092, +0.192], P(>0) = 74.7%. Better execution has lifted this system to roughly breakeven. "
        "It has not found an edge, because there was not one in the entry logic to begin with.",
    ]:
        ws.write(r, 2, "- " + line, f["wrap"])
        ws.set_row(r, 12.5 * (len(line) // 100 + 1))
        r += 1
    r += 1
    ws.write(r, 1, "Source: backtest/system_v3.py and backtest/limit_entry.py. Bootstraps resample "
                   "one-week blocks of entry bars; the combined test uses 8,000 resamples.", f["note"])


def write_oos(wb, f):
    """Cross-dataset replication - the test that decides whether any of this travels."""
    ws = wb.add_worksheet("Out of Sample")
    _title(ws, f, "Out of sample - does any of this survive outside the window it came from?",
           "One rule out of everything in this study replicates. It is not an edge.")
    ws.set_column(0, 0, 3)
    ws.set_column(1, 1, 34)
    ws.set_column(2, 10, 13)

    rep = json.load(open(os.path.join(DATA, "replication.json")))
    DS = [("1h", "MAIN 1h"), ("1h_prior", "PRIOR 1h (out of sample)"), ("15m", "15m")]

    r = 3
    ws.write(r, 1, "The three datasets", f["label"])
    ws.write(r, 2, "MAIN 1h is 2025-06-12 to 2026-08-03 - the window every rule in this workbook was "
                   "derived from. PRIOR 1h is the 10,000 hours immediately before it, 2024-04-22 to "
                   "2025-06-12, strictly disjoint and never seen during any part of the derivation: this "
                   "is the honest test. 15m is 2026-04-21 to 2026-08-03, a different timeframe that "
                   "overlaps the tail of the main window, so it is a robustness check rather than an "
                   "independent sample.", f["wrap"])
    ws.set_row(r, 70)
    r += 2

    def table(title, keys, src, note=None):
        nonlocal r
        ws.write(r, 1, title, f["h1"])
        for i in range(9):
            ws.write(r, i + 2, "", f["h1"])
        r += 1
        ws.write(r, 1, "Configuration", f["hdr"])
        for i, (_, label) in enumerate(DS):
            ws.write(r, 2 + i * 3, f"{label} - n", f["hdr"])
            ws.write(r, 3 + i * 3, f"{label} - avg R", f["hdr"])
            ws.write(r, 4 + i * 3, f"{label} - P(>0)", f["hdr"])
        ws.set_row(r, 40)
        r += 1
        for k in keys:
            ws.write(r, 1, k, f["label"])
            for i, (suffix, _) in enumerate(DS):
                d = src[k].get(suffix)
                if not d:
                    continue
                ws.write_number(r, 2 + i * 3, d["n"], f["int"])
                ws.write_number(r, 3 + i * 3, d["avg"], f["good"] if d["avg"] > 0 else f["bad"])
                ws.write_number(r, 4 + i * 3, d["p_pos"] / 100.0, f["pct1"])
            r += 1
        if note:
            ws.write(r, 1, note, f["note"])
            r += 1
        r += 1

    table("Do the books replicate?", list(rep["books"].keys()), rep["books"],
          note="Every configuration is positive in MAIN and negative in PRIOR. The ordering is the "
               "damning part: the more heavily a book was tuned on the main window, the worse it does "
               "out of sample. v2b, the best in-sample book at +0.269 R, is the worst out of sample "
               "at -0.178 R. That is the signature of overfitting, measured rather than suspected.")

    table("Do the cuts replicate?", list(rep["cuts"].keys()), rep["cuts"],
          note="These are the trades v2 removes. A cut is only justified if the removed trades are "
               "negative everywhere, not just in the window that motivated the cut.")

    ws.write(r, 1, "RANGE_FADE: the structural test", f["h1"])
    for i in range(9):
        ws.write(r, i + 2, "", f["h1"])
    r += 1
    for i, c in enumerate(["Dataset", "n", "Win rate", "Breakeven needed", "Gap", "Verdict"]):
        ws.write(r, i + 1, c, f["hdr"])
    ws.set_row(r, 30)
    r += 1
    for suffix, label in DS:
        d = rep["cuts"]["CUT RANGE_FADE (all >=6)"].get(suffix)
        if not d:
            continue
        gap = d["win"] - d["be"]
        ws.write(r, 1, label, f["label"])
        ws.write_number(r, 2, d["n"], f["int"])
        ws.write_number(r, 3, d["win"] / 100.0, f["pct1"])
        ws.write_number(r, 4, d["be"] / 100.0, f["pct1"])
        ws.write_number(r, 5, gap / 100.0, f["bad"] if gap < 0 else f["good"])
        ws.write(r, 6, "cannot pay for itself" if gap < 0 else "viable", f["ctr"])
        r += 1
    r += 1

    ws.write(r, 1, "What actually survived", f["key"])
    ws.write(r, 2, "", f["key"])
    r += 1
    for line in [
        "Nothing in this study is profitable out of sample. v1 selective goes +0.040 to -0.022, the 6-8 "
        "band +0.177 to -0.049, v2 +0.196 to -0.045, and v2b +0.269 to -0.178. The edge found in the "
        "main window was a property of that window.",
        "Capping conviction at 8 does NOT replicate. The 8-10 bucket is +0.015 R out of sample against "
        "-0.124 in sample. It was a within-window artifact, and it was one of the two changes this "
        "workbook previously described as supported. It is not.",
        "Deleting RANGE_FADE DOES replicate - negative in all three datasets, and significantly so on "
        "15m. More convincing than the outcome is the mechanism: its breakeven win rate exceeds its "
        "achieved win rate in every dataset, by 4.1, 5.4 and 13.3 points. A 1.3R target cannot pay for "
        "the losses at any hit rate that setup reaches. That is arithmetic, not a backtest result, "
        "which is exactly why it travelled when nothing else did.",
        "The practical conclusion is narrower than any earlier version of this workbook claimed. This "
        "system has no demonstrated edge on ETH, LINK or SOL on hourly or 15m candles across 20,000 "
        "hours of data. One component is provably broken and should be deleted. Everything else that "
        "looked promising was the sample talking.",
        "The one methodological lesson worth carrying forward: every improvement made across this study "
        "raised the in-sample point estimate without narrowing the confidence interval, and the "
        "bootstrap said so at each step. The out-of-sample test then confirmed exactly what the "
        "bootstrap had been warning about. The warning was correct and could have been acted on before "
        "the extra data arrived.",
    ]:
        ws.write(r, 2, "- " + line, f["wrap"])
        ws.set_row(r, 12.5 * (len(line) // 100 + 1))
        r += 1

    r += 1
    ws.write(r, 1, "Source: backtest/replication.py. Intervals are block bootstraps over one-week blocks "
                   "of entry bars, 4,000 resamples. Percentages stored as fractions.", f["note"])


def write_v2(wb, f, symbols):
    """System v2: the two subtractive changes the evidence actually supports."""
    ws = wb.add_worksheet("System v2")
    _title(ws, f, "System v2 - and why half of it did not survive",
           "Read the Out of Sample tab alongside this one. One of these two changes was later falsified.")
    ws.set_column(0, 0, 3)
    ws.set_column(1, 1, 40)
    ws.set_column(2, 10, 13)

    h = json.load(open(os.path.join(DATA, "system_v2_1h.json")))
    m = json.load(open(os.path.join(DATA, "system_v2_15m.json")))

    r = 3
    ws.write(r, 1, "STATUS", f["key"])
    ws.write(r, 2, "Everything on this tab was derived from the main window. It has since been re-tested "
                   "on the strictly disjoint 10,000 hours before it. Change 1 (the conviction cap) DID "
                   "NOT replicate and is not supported. Change 2 (deleting RANGE_FADE) did. The v2 and "
                   "v2b books are both negative out of sample. The numbers below are left intact so the "
                   "falsified claim stays visible rather than being quietly edited away - see the Out of "
                   "Sample tab for the test that overturned it.", f["wrap"])
    ws.set_row(r, 70)
    r += 2
    for label, body in [
        ("Change 1: cap conviction at 8  [FALSIFIED]",
         "The 6-8 bucket was positive on all three symbols; the 8-10 bucket was negative on all three "
         "(-0.124 R pooled, profit factor 0.84), suggesting the score was not monotonic with outcome. "
         "Out of sample the 8-10 bucket is +0.015 R. The pattern was a within-window artifact and this "
         "change should not be adopted."),
        ("Change 2: delete RANGE_FADE  [REPLICATED]",
         "Both directions have a breakeven win rate ABOVE their achieved win rate - 48.6% needed against "
         "43.8% achieved (long), 49.5% against 45.8% (short). A 1.3R target cannot pay for the losses at "
         "any hit rate those setups reach. They lose by construction, not by variance. No other "
         "combination in the study has that property - and it is the only finding in this workbook "
         "that survived out-of-sample testing, precisely because it is arithmetic rather than an "
         "observed outcome."),
        ("Optional: v2b geometry",
         "Stop x1.6 with a 4R target - the average-R optimum from the sweep. Kept separate from the two "
         "cuts because it is a tuning choice fitted on this sample, whereas the cuts are structural."),
    ]:
        ws.write(r, 1, label, f["label"])
        ws.write(r, 2, body, f["wrap"])
        ws.set_row(r, 12.5 * (len(body) // 100 + 2))
        r += 1
    r += 1

    cols = ["Book", "n", "Win %", "Breakeven %", "Cost as % of 1R", "Avg R", "Total R",
            "Profit factor", "95% CI low", "95% CI high", "P(avg R > 0)"]

    def block(title, rows_src):
        nonlocal r
        ws.write(r, 1, title, f["h1"])
        for i in range(len(cols)):
            ws.write(r, i + 2, "", f["h1"])
        r += 1
        for i, c in enumerate(cols):
            ws.write(r, i + 1, c, f["hdr"])
        ws.set_row(r, 30)
        r += 1
        for name, d in rows_src:
            if not d:
                continue
            ws.write(r, 1, name, f["label"])
            ws.write_number(r, 2, d["n"], f["int"])
            ws.write_number(r, 3, d["win"] / 100.0, f["pct1"])
            ws.write_number(r, 4, d["be"] / 100.0, f["pct1"])
            ws.write_number(r, 5, d["cost"] / 100.0, f["pct1"])
            ws.write_number(r, 6, d["avg"], f["good"] if d["avg"] > 0 else f["bad"])
            ws.write_number(r, 7, d["tot"], f["num1"])
            ws.write_number(r, 8, d["pf"], f["num3"])
            ws.write_number(r, 9, d["lo"], f["num3"])
            ws.write_number(r, 10, d["hi"], f["num3"])
            ws.write_number(r, 11, d["p_pos"] / 100.0, f["pct1"])
            r += 1
        r += 1

    block("Hourly, pooled across ETH + LINK + SOL", list(h["pooled"].items()))
    block("15m, pooled (same rules, unchanged parameters)", list(m["pooled"].items()))

    per = []
    for sym, short in symbols:
        for label in ("v1  6-8 band (all setups)", "v2  6-8, no RANGE_FADE, shipped geom",
                      "v2b 6-8, no RANGE_FADE, x1.6 / 4R"):
            d = h["per_symbol"][sym].get(label)
            if d:
                per.append((f"{short} - {label}", d))
    block("Hourly, per symbol", per)

    ts = []
    for label, halves in h["time_split"].items():
        for half in ("H1", "H2"):
            if halves.get(half):
                ts.append((f"{label} - {half}", halves[half]))
    block("Hourly, time split - does it hold in both halves?", ts)

    cut = [(f"HOURLY  dropped: {k}", v) for k, v in h["cut"].items()]
    cut += [(f"15m     dropped: {k}", v) for k, v in m["cut"].items()]
    block("What was cut, and whether cutting it was justified", cut)

    ws.write(r, 1, "The verdict, after out-of-sample testing", f["key"])
    ws.write(r, 2, "", f["key"])
    r += 1
    for line in [
        "In the main window v2b looked like a clear improvement: +0.269 R against +0.177, profit factor "
        "1.47 against 1.26, positive on all three symbols and in both sample halves. It never cleared "
        "the significance bar - P(avg R > 0) was 89.5% and the interval always straddled zero.",
        "On the disjoint prior window it is -0.178 R, the WORST of every configuration tested. The "
        "ranking inverts exactly in order of how much each book was tuned: v1 selective -0.022, the "
        "6-8 band -0.049, v2 -0.045, v2b -0.178.",
        "So of the two changes on this tab, one replicated and one did not. Deleting RANGE_FADE is "
        "supported in all three datasets and for a structural reason. Capping conviction at 8 is not "
        "supported and should be discarded.",
        "Neither makes the system profitable. Dropping RANGE_FADE alone moves the out-of-sample result "
        "from -0.022 R to -0.019 R: it removes a component that cannot pay for itself, which is a much "
        "weaker claim than finding an edge.",
    ]:
        ws.write(r, 2, "- " + line, f["wrap"])
        ws.set_row(r, 12.5 * (len(line) // 100 + 1))
        r += 1

    r += 1
    ws.write(r, 1, "Source: backtest/system_v2.py. Confidence intervals are block bootstraps resampling "
                   "one-week blocks of entry bars, 4,000 resamples. Percentages stored as fractions.",
             f["note"])


def write_equity(wb, f, symbols, all_rows, sel_rows):
    ws = wb.add_worksheet("Equity Curves")
    _title(ws, f, "Cumulative R",
           "Constant 1R risk per trade, no compounding - trades stack without limit, so a compounding "
           "curve would be meaningless.")
    ws.set_column(0, 0, 12)
    ws.set_column(1, 6, 15)

    POINTS = 400

    def curve(rows):
        eq, out = 0.0, []
        for t in rows:
            if t["status"] == "CLOSED":
                eq += float(t["r_multiple"])
            out.append(eq)
        return out

    series = [(f"{short} all", curve(all_rows[sym])) for sym, short in symbols]
    series += [(f"{short} selective", curve(sel_rows[sym])) for sym, short in symbols]

    hdr = 4
    ws.write(hdr, 0, "Sample #", f["hdr"])
    for i, (label, _) in enumerate(series):
        ws.write(hdr, i + 1, label, f["hdr"])

    for k in range(POINTS):
        r = hdr + 1 + k
        ws.write_number(r, 0, k, f["int"])
        for i, (_, vals) in enumerate(series):
            idx = min(len(vals) - 1, int(k * len(vals) / POINTS))
            ws.write_number(r, i + 1, round(vals[idx], 3), f["num1"])

    for idx, (title, offset) in enumerate([("All-trades books (every hourly close)", 0),
                                           ("Selective books (conviction >= 6.0)", 3)]):
        chart = wb.add_chart({"type": "line"})
        for i in range(3):
            col = offset + i + 1
            chart.add_series({
                "name": [ws.get_name(), hdr, col],
                "values": [ws.get_name(), hdr + 1, col, hdr + POINTS, col],
                "line": {"width": 1.75},
            })
        chart.set_title({"name": title, "name_font": {"name": "Arial", "size": 12}})
        chart.set_x_axis({"name": "Trade sequence (sampled)", "num_font": {"name": "Arial", "size": 9}})
        chart.set_y_axis({"name": "Cumulative R", "num_font": {"name": "Arial", "size": 9}})
        chart.set_size({"width": 760, "height": 340})
        chart.set_legend({"position": "bottom", "font": {"name": "Arial", "size": 9}})
        ws.insert_chart(2 + idx * 18, 8, chart)

    ws.write(1, 0, "Both charts are in R. The all-trades books fall steadily; the selective books are "
                   "roughly flat with a mild upward drift on ETH and LINK.", f["sub"])
    ws.write(hdr + POINTS + 2, 0,
             "Source: cumulative sum of the R Multiple column, sampled to 400 points per series, computed "
             "by backtest/build_workbook.py. Written as values because a running total is path-dependent "
             "along the trade sequence.", f["note"])
