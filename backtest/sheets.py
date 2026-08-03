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
