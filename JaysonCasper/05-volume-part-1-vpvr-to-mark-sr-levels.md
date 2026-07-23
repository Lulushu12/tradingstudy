# Volume Part 1 — VPVR to Mark S/R Levels

Source lesson: volume-part-1-vpvr-to-mark-s-r-levels

## Two volume tools in TradingView
1. **Standard "Volume"** — volume traded *per time bar*. Useful for confirming breakouts/breakdowns: a level breaking with high volume behind it is more likely to continue than one breaking on low volume.
2. **VPVR ("Visible Range")** — volume traded *per price*, not per time. Search "Visible Range" in TradingView indicators. Instructor's settings: row size 200, value area volume 70%.

## Reading VPVR
- Bright/bold-colored band = the **value area** (most heavily traded price zone in the visible range); **value area high (VAH)** and **value area low (VAL)** mark its top/bottom.
- The brightest single line = **point of control (POC)** — the single price with the most volume traded in the visible range.
- VAH, POC, and VAL all act as support/resistance: rejections tend to occur at VAH, bounces at VAL, and reactions (either direction) at the POC — because the market "remembers" where heavy buying/selling happened and large orders look to fill there again.
- Peaks in the volume profile = **high volume nodes (HVN)** → significant S/R levels. Valleys = **low volume nodes (LVN)** → areas price tends to move through quickly since little trading interest exists there.
- Volume spikes are relative to the visible range — a "small" bump can still be the dominant HVN within a smaller price window even if dwarfed by history at a wider zoom.
- Works best applied on daily/weekly timeframes; zooming out changes which nodes stand out since the profile recalculates over whatever range is visible.

## Workflow: combine with hand-drawn S/R for confluence
1. Draw daily/weekly S/R by hand (per earlier lessons).
2. Overlay VPVR and mark additional HVNs as S/R lines.
3. Look for **confluence** — a zone where a hand-drawn weekly/daily level lines up with an HVN (and later, a Fibonacci level too). The more independent reasons point to the same zone, the stronger the expected reaction ("triple level of resistance/support" when e.g. weekly level + HVN + Fib retracement all line up).

## Entry trigger example referenced
At a high-confluence resistance zone (Fib level + HVN + weekly resistance), the entry signal used was a **swing failure pattern (SFP)**: price makes a higher high at the resistance, gets rejected, comes back and tags the same resistance again but with a *lower* high, accompanied by Market Cipher momentum turning down and a money-flow crossunder → short trigger. (SFPs apply symmetrically at support for longs; covered in more depth in a later lesson.)

## Core takeaway
Mark significant levels using every available method (hand-drawn S/R, VPVR nodes, Fibonacci — next lessons), wait for price to reach a high-confluence zone, then look for a Market Cipher-based trigger (like an SFP) to actually enter.
