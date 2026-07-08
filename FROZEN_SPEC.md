# FROZEN SPEC v1
Status: FROZEN. Written from memory and interrogation before any data exploration. No changes permitted except through an explicit, logged amendment agreed in conversation. If the Python port and this spec ever disagree, this spec wins. TradingView is never a source of backtest numbers.

## 1. Instrument and timeframe
- BTCUSDT.P (Breakout Prop), 15m only.
- 1h and 4h are decorative for the trader and are excluded from the system.

## 2. Indicators (computed exactly per MCB Clone v1 PineScript, uploaded separately)
- WaveTrend: channel length 9, average length 12, source hlc3, MA length 3.
  - wt2 = SMA(wt1, 3). All divergence logic runs on wt2.
- MFI clone: period 60, multiplier 150, Y offset 2.5, stdev length 7, outer EMA smooth 4.
  - Formula: EMA( SMA( (close - open) / stdev(close, 7) * 150, 60 ) - 2.5, 4 ).
- ATR bands: ATR period 14, RMA (Wilder) smoothing, bands = close +/- 1 x ATR.
- RSI / StochRSI: present in indicator, NOT part of this system. Excluded.
- Pre-div warning module: source of the front-run condition in Variant B (see 4).

## 3. Divergence definitions
- Fractal pivot: 5-bar fractal exactly as coded (f_top_fractal / f_bot_fractal). A pivot at bar p is CONFIRMED at bar p+2.
- Regular divergences only. Hidden divergences are excluded entirely from the system.
- Level filters (tested at the pivot per the code):
  - WT bull: pivot wt2 <= -65 (primary) or <= -40 (secondary).
  - WT bear: pivot wt2 >= 45 (primary) or >= 15 (secondary).
  - MFI bull: pivot mfi <= -2.5. MFI bear: pivot mfi >= 2.5.
- Reference comparison per the coded f_findDivs logic (valuewhen chain, price checked at high[2]/low[2] of the respective pivot bars).

## 4. Entry signal
A valid stack requires exactly ONE WT regular divergence plus ONE MFI regular divergence, same direction. WT+WT and MFI+MFI pairs are invalid. (Note: the historical indicator code fired on any two same-direction events. That is a known bug. The buggy variant may be run as a DIAGNOSTIC only and is never a candidate system.)

### Variant B: front-run entry. PRIMARY. This is the system as actually traded.
- Leg 1: either oscillator's divergence, fully fractal-confirmed (symmetric, WT or MFI may be first).
- Leg 2: the other oscillator, entered via front-run. At the close of bar t, ALL of:
  - Pre-div raw condition holds against leg 2's reference fractal per the coded logic: price exceeds the reference extreme (reference extreme taken as the true extreme within the 5-bar swing buffer back from the reference pivot bar), oscillator holding on the divergent side of the reference oscillator value, reference pivot no older than 50 bars (preDivMaxAge = 50 per trader's live settings).
  - Oscillator ticked once in the reversal direction: osc[t] vs osc[t-1]. One bar is sufficient. No trough/peak shape required.
  - Level filter is tested on the REFERENCE ANCHOR pivot only. The current front-run turn is unrestricted. This is intentionally looser than the standard coded divergence and is a deliberate design choice.
- Window: <= 11 candles measured from leg 1's PIVOT bar to leg 2's front-run turn bar (bar t). If leg 2 does not complete within 11 candles, the signal is dead.
- Gap 0 (both legs completing on the same bar close) is a valid stack.
- Entry: market order at the open of bar t+1.
- The front-run CONSUMES the signal. If the diamond later prints for the same stack, no second entry.
- If the front-run divergence never fractal-confirms, the trade is held to SL/TP like any other. No early exit.

### Variant A: standard entry. DECLARED COMPARISON, run alongside B in Phase 1.
- Stack = WT regular div + MFI regular div, same direction, within 11 bars measured between fractal-CONFIRMATION bars. Gap 0 valid.
- Entry: market order at the open of the bar after stack confirmation.

Variant selection commitment: A and B both run Phase 1. Neither is chosen over the other on studied-data results alone. If they disagree, the locked holdout decides.

Open item for Gate 0: stack events sharing a leg (e.g. two WT divs within window of one MFI div producing two signals). The port will log both legs' identities per signal. The dedup rule is decided openly at Gate 0 before any results are shown.

## 5. Risk and trade management
- Stop loss (short): highest value of (close + 1 x ATR14) over bars t-5 through t-1. The signal bar t is EXCLUDED. Mirrored for longs using (close - 1 x ATR14) lowest over t-5..t-1.
- Entry invalidation: if SL distance < 0.6% of entry price, skip the trade entirely.
- No maximum stop distance.
- Take profit: fixed 2:1 R. No trailing, no partials, no break-even moves. Enter and forget.
- Position sizing: 1% of CURRENT account equity at risk per trade. Size = risk amount / stop distance.
- Opposite signal while in a trade: open an independent position (venue supports simultaneous long+short). Both positions run to their own SL/TP. Modeled as independent trades; both-stops-hit chop scenarios are counted, not assumed away.
- Fully symmetric long/short.

## 6. Costs
- Commission: 0.08% round trip (0.04% per side, taker/market) PENDING verification against Breakout's actual fee schedule at Gate 0.
- Slippage: explicit per-fill assumption on top of commission, value set and pre-committed at Gate 0 before any backtest runs.
- All orders are market orders. No limit orders anywhere in the system.

## 7. Known honesty flags (carried through all phases)
- The trader's screen-time intuition was built on the BUGGY stack signal (any two divs, including WT+WT). Prior confidence in "the diamond works" is evidence about a different signal set than the one under audit.
- The intended WT+MFI rule has never been traded or displayed anywhere before this audit.
- Live front-run execution historically involved intrabar discretion. Variant B as specified (closed-bar evaluation, t+1 open entry) is the mechanized form and has not been traded in exactly this form.
- Breakout's ATR indicator formula has NOT been verified against ATR14 RMA. Until verified, live SL placement may deviate from this spec on every trade. Verification is a pre-Phase-4 requirement.
- Recent data is partially contaminated by live trading and replay practice. The holdout is weaker than a true blind holdout and the final verdict is weighted accordingly.
