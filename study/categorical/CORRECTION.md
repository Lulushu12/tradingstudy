# CORRECTION: the Gate 0 fade result was wrong

Date found: during the Phase 1 diagnostic, immediately after Phase 1 returned a negative
expectancy at zero cost.

## What was wrong

The Gate 0 fade-template measurement counted **untakeable entries as automatic full-size wins**.

The fade trade enters at the open of bar t+1 and targets the range midpoint computed at bar t.
If the market gapped through the midpoint between the close of bar t and the open of bar t+1, the
entry price is already past the take-profit. That is not a trade. You cannot sell at 100 with a
take-profit at 105 and book a win; the position would open and close at a loss or not at all.

The barrier race had no check for this. It saw "target level touched on the first bar" and
recorded a win at full reward/risk. There was also no check that the stop was still on the far
side of the entry, though that case turned out not to occur.

**In the headline 4H decile-0 set, 404 of 902 signals were untakeable. All 404 were counted as
wins.** That is 44.8% of the sample, and it was injecting a large constant positive.

## The corrected numbers

| configuration | as reported | corrected | change |
|---|---|---|---|
| 4H fade, win rate | 80.7% | **65.5%** | -15.2 pts |
| 4H fade, gross R | +0.1196 | **+0.0297** | -0.0899 |
| 4H fade, net R @0.08% | **+0.0991** | **+0.0017** | -0.0974 |
| 15m fade, net R @0.08% | +0.0165 | **-0.1478** | -0.1643 |

The 4H fade edge is not merely reduced. It is gone. +0.0017 R per trade is zero with extra steps.

## What this invalidates

1. **GATE0_VERDICT.md section 3**, the cost-by-timeframe table, for the fade rows. The claim that
   net expectancy crosses zero between 5m and 15m and reaches +0.0991 R on 4H is void.
2. **GATE0_STABILITY.md**, the entire fade per-year table and its "net positive in 6 of 6 years"
   conclusion. The apparent year-on-year stability was the stability of the contamination, which
   ran at a roughly constant share of the sample.
3. **The three robustness checks that the fade "survived"** were all measuring the wrong thing.
   The fill-penetration test in particular looked reassuring precisely because the untakeable
   entries were already far past the target, so requiring extra penetration could not touch them.
   A check that cannot fail is not a check.
4. **Everything I reported in conversation about the 4H fade surviving.** That was wrong and it was
   stated with confidence.

## What survives unchanged

1. **The Gate 0 headline symmetric-barrier tests (GATE0_RESULTS.md sections 1 through 6).** Those
   place barriers at +/- k x ATR around the entry price, so a barrier can never already be
   breached at entry. Unaffected. They found nothing, and they still find nothing.
2. **The session-window check (GATE0_SESSION.md).** Same symmetric-barrier construction.
   Unaffected.
3. **Phase 1 itself.** The frozen spec included the check `if (side == 1 and tgt <= ref) or
   (side == -1 and tgt >= ref): continue`, which correctly rejects exactly these signals. Phase 1
   was never contaminated. Its verdict of DEAD stands, and the reason is now clear: Phase 1 did
   not destroy an edge, it removed a bug and revealed there had never been one.
4. **The direction (breakout) template was not materially contaminated** and in fact improves when
   the untakeable cases are removed, because for that template the removed cases were ones where
   the stop rather than the target was already breached. See the next section.

## The direction template, and why I am not pivoting to it

Corrected, takeable signals only:

| configuration | gross R | cost/R | net R | n |
|---|---|---|---|---|
| 4H breakout | +0.2389 | 0.0201 | **+0.2189** | 800 |
| 15m breakout | +0.1027 | 0.0682 | **+0.0345** | 12,075 |

This now looks like the stronger candidate by a wide margin. I am not treating it as one, for
three reasons.

First, **AUDIT_COMMITMENTS_CATEGORICAL.md section 6 explicitly forbids it**: "No substituting the
direction template for the fade template if the fade fails." I wrote that before results existed
precisely so that this moment could not become a goalpost move. Refusing here is the entire point
of having written it.

Second, these numbers come from the same code path that just produced a 44.8% contamination rate.
They have not been independently verified. A number from a codebase with a known defect is a
hypothesis, not a result.

Third, the per-year breakout figures in GATE0_STABILITY.md were produced before the correction and
would need to be regenerated. The 4H breakout was already the noisier of the two templates, with
2021 at -0.1262 R and only one of six per-year confidence intervals excluding zero.

If the direction template is to be tested, it needs its own frozen spec, its own pre-committed
kill thresholds, a fresh implementation audited for this class of defect, and ideally a
quarantined holdout established before any of it runs.

## Process failure, and what would have caught it

The bug survived Gate 0, a per-year stability split, an overlap check, a both-hit bound, and a
pessimistic-fill sweep. None of those could catch it because all of them took the trade population
as given and asked whether the outcomes were measured fairly. None asked whether the trades were
takeable in the first place.

Two cheap checks would have caught it immediately and are now the standing requirement for any
barrier-based test in this folder:

1. **Assert the geometry at entry.** For every signal: target strictly on the profitable side of
   the entry price, stop strictly on the losing side. Count and report violations rather than
   letting them through.
2. **Report the first-bar resolution rate.** In the contaminated set, 44.8% of trades resolved on
   the entry bar as wins. A win rate of 80.7% at 0.46 reward/risk should have been interrogated on
   sight: it implies a Sharpe far above anything a 20-line rule on daily-scale crypto data has any
   business producing. I noticed the median hold was 1 bar and treated it as a curiosity about
   holding period rather than as the symptom it was.

The deeper failure was directional. I ran five separate checks trying to break a result I liked,
and every one of them was a check on measurement quality rather than on whether the trade existed.
Skepticism aimed only at the parts you already suspect is not skepticism.
