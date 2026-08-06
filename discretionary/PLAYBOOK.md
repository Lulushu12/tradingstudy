# Playbook: the four setups

This is the desk document. Keep it open while trading. If the trade in front of you does
not match one of these four pages, it is not a trade.

Common requirements for every setup (from `SYSTEM_SPEC_v1.md`):

- Level was on the map **before** price arrived (Layer 1).
- Direction permitted by the 4H EMA200 context gate (Layer 2).
- Trigger evaluated on a **closed bar**, entry after the close (Layer 4).
- Trigger timeframe fixed by the anchor: 1D->1h, 4H->15m, 1h->5m, 15m->5m (1m for S2 only).
- At least **2.0R to the next opposing level** (Layer 5).
- Stop clears both minimums: **fee drag <= 0.20R** (>= 0.40% at Breakout's 0.08% round
  trip) and **>= 0.75 x ATR14 on the trigger timeframe** (Layer 5).
- Confluence counted from the anchor timeframe **or higher**, never lower (Layer 1).
- Pre-trade journal row written **before** entry, including `anchor_tf` (Layer 6).

---

## S1: Level Rejection

**Basis:** `study/STRATEGY_FINDINGS.md` section B. Short at a held 4H swing resistance in
a 4H downtrend measured 61% train / 64% test at 1:1 and 44% / 55% at 2:1. Short at a held
prior-week high measured 52% / 68% at 1:1 across ~370 instances. These were rejected by
the mechanical scan for frequency alone.

**What it is:** price travels into a graded level from the far side and fails to take it,
in the direction the 4H trend already favours.

### Checklist

- [ ] Grade A or B zone, marked in advance
- [ ] 4H trend agrees with the trade direction (`close < EMA200` for a short into
      resistance, `close > EMA200` for a long into support)
- [ ] If long into support: **one extra confluence family required** (see Layer 2
      asymmetry note; provisional, under test)
- [ ] Price actually reaches the zone. Not "nearly". Inside the 0.25 x ATR band.
- [ ] No close beyond the far edge of the zone on the 4H. A 4H close through it means the
      level is broken, not held, and this setup is dead.
- [ ] Trigger timeframe 15m: MC divergence + money flow turning
- [ ] Cooldown satisfied: 3+ bars since the opposing dot
- [ ] Two consecutive lower highs (short) or higher lows (long) on 15m

### Entry, stop, target

- **Entry:** market, on the close of the confirming 15m bar.
- **Stop:** beyond the far edge of the zone plus the 0.25 x ATR tolerance band, plus a
  small buffer. Not at the exact level; that is where the stop hunt lives.
- **Target:** next opposing level on the map. Must be >= 2.0R.

### Kills this setup

- A 4H close beyond the zone before your trigger fires.
- Price arriving at the zone in a vertical impulse with no deceleration. Lesson 28: do not
  grab a falling knife into a level, wait for the reaction.
- The zone was upgraded to A grade *after* price started approaching it.

---

## S2: SFP / Chickens Drinking Water

**Basis:** course lesson 26, the standalone tutorial. This is the only setup permitted
against the 4H trend, and only at A grade.

**What it is:** price wicks beyond a prior swing high or low and **closes back on the
original side**. If it closes beyond, it is a successful breakout, not an SFP, and this
setup does not apply, no matter what happens afterward.

### Checklist

- [ ] A specific prior swing high/low was marked in advance as the level to be swept
- [ ] Wick goes beyond it, candle **closes back inside**. Verify on a closed bar.
- [ ] Zone is grade A (or B if trading with the 4H trend)
- [ ] Money flow diverging from price, checked on the trigger timeframe **and one higher**
- [ ] Momentum divergence on the wave, same multi-timeframe check
- [ ] RSI and Stochastic RSI tight/converging on Market Cipher B at the wick (lesson 26
      calls this the icing; treat it as a strong upgrade, not a requirement)
- [ ] Trigger timeframe: 15m, or 5m permitted for this setup only

### Entry, stop, target

- **Entry:** market order on the close of the sweeping candle, or on the close of the
  first confirming lower-timeframe bar after it. Never a resting limit; you cannot know
  where the wick ends (lesson 26).
- **Stop:** beyond the wick extreme, plus a buffer. The wick extreme is the invalidation
  by definition.
- **Target:** next opposing level, >= 2.0R.

### Kills this setup

- The candle closes beyond the level. That is a breakout. Walk away.
- No divergence, only the wick. Lesson 26 is explicit that an SFP with no level and no
  divergence backing it is a weak setup.
- Front-running the wick before it reverses. This is the single most tempting and most
  expensive version of the anti-front-run rule.

---

## S3: Range-Boundary Rotation

**Basis:** course lesson 28. This is the frequency engine. When a post-impulse range is
active on a watchlist symbol, it can produce several setups from one structure.

**What it is:** after a large impulsive move, a range forms. Mark its first real high and
first real low (several candles of confirmation, not a single wick). Pull a fib from high
to low, mark the 0.618-0.786 golden pocket. Trade rejections at the boundaries and at the
golden pocket, and re-pull everything each time a new extreme extends the range.

### Checklist

- [ ] A genuine impulse happened, and a range is forming after it
- [ ] Range high and low each confirmed by multiple candles, not one wick
- [ ] Fib pulled high to low, golden pocket marked
- [ ] Fixed-range volume profile pulled across the whole developing range; POC / VAH / VAL
      marked
- [ ] The specific price you are trading is a graded zone (the golden pocket coinciding
      with the POC or VAH is the classic A grade from lesson 13)
- [ ] Trigger: MC divergence + money flow on 15m
- [ ] **Range still valid**: no 4H close outside the boundary you are fading

### Entry, stop, target

- **Entry:** market on the confirming closed bar.
- **Stop:** beyond the range boundary being faded, or beyond the golden pocket's far edge
  if trading the pocket rather than the boundary.
- **Target:** the opposite side of the range or the next internal level, >= 2.0R.

### Re-pull discipline

Every time price makes a new high or low that extends the range, the **whole updated
range** becomes the working range. Re-pull the fib and the volume profile against the new
extremes. Old golden pockets from the previous range are no longer levels. Delete them.
Trading a stale fib is one of the easiest ways to lose money in a range that is expanding.

### Kills this setup

- 4H close outside the range. The range is over; you are now in an impulse and S3 does not
  apply until a new range forms.
- Trading the middle of the range. Only the boundaries and the graded internal levels.
- Taking more than 2 rotations in the same range in the same direction without a review.
  That is the overtrading failure mode this setup is most exposed to.

---

## S4: 4H Volume-Spike Continuation (the control)

**Basis:** `study/STRATEGY_FINDINGS.md`, the one validated edge. Winrate 41.7% at 2:1,
expectancy +0.21R net, train 42.2% / test 40.4%, CAGR +21.6% at 1% risk, max drawdown
-12.3%, positive expectancy in every year 2021-2026 and in both trend regimes.

**This setup has no discretion in it and must not be given any.** It is the benchmark that
S1, S2 and S3 are measured against. Skipping S4 signals because a discretionary setup
looks more attractive corrupts the comparison and destroys the only clean measurement in
the system.

### Rules, exactly as validated

- Timeframe: **4H**.
- Trend filter: `close` vs `EMA200` on 4H.
- Trigger: a 4H bar whose **volume > 1.8x its 20-bar average**, closing in the direction
  of the trend (up bar in an uptrend, down bar in a downtrend).
- **Entry:** market at the next 4H bar open.
- **Stop:** 1.5 x ATR(14). Not the structural invalidation. This is the validated
  parameter and it does not get "improved".
- **Target:** 2 x stop distance (2:1).
- **One position at a time per symbol.** Skip new S4 signals on a symbol while an S4 trade
  is open on it.

### What does not apply to S4

- The 2.0R-to-next-level rule does not apply. The target is mechanical at 2R.
- The 0.5% minimum stop does not apply. The ATR stop is the spec.
- Grade multipliers do not apply. S4 is always 1.0 unit.
- The exit policy comparison **does** still apply: log MFE_R and MAE_R as normal so S4 can
  be evaluated under each exit policy alongside everything else.

### Note on frequency

The study measured roughly 8 S4 trades a month on BTC alone. Across a watchlist this
setup alone may exceed your 2-3 per week target. If S4 volume becomes overwhelming,
restrict S4 to a fixed subset of 3-4 symbols and record that decision in the Amendment
Log, rather than skipping signals ad hoc.

---

## Quick reference

| | S1 Rejection | S2 SFP | S3 Range | S4 Volume spike |
|---|---|---|---|---|
| Anchor TF | 1D / 4H / 1h / 15m | any, incl. 15m | the range's own TF | 4H, fixed |
| Trigger TF | one step below anchor | one step below, 1m allowed | one step below anchor | 4H close |
| Min grade with trend | B | B | B | n/a |
| Min grade vs trend | not allowed | A | not allowed | not allowed |
| Stop | far edge of zone + buffer | beyond wick | beyond boundary | 1.5 x ATR14 |
| Target | next level, >= 2R | next level, >= 2R | opposite side, >= 2R | fixed 2R |
| Discretion | high | high | high | **none** |

### Breakeven winrate by stop distance, at 2:1

Keep this in view when a tight stop is tempting. `breakeven p = (1 + fee_drag) / 3`.

| Stop | Fee drag | Breakeven WR @ 2:1 |
|---|---|---|
| 0.40% (the cap) | 0.20R | 40.0% |
| 0.60% | 0.13R | 37.8% |
| 1.00% | 0.08R | 36.0% |
| 2.00% | 0.04R | 34.7% |

The measured winrate on the validated 4H setup was 41.7%. A 0.40% stop leaves 1.7 points
of margin against that. A 1.00% stop leaves 5.7. That is the real cost of a low anchor,
and it is why anchors get dropped on measurement rather than on preference.
