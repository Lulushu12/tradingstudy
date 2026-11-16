"""Hand-built scenarios with known answers for the structure logic, plus look-ahead tests on synthetic data."""
import numpy as np
import pandas as pd
import pytest

from tradingstudy.features import ta
from tradingstudy.structure import levels as lv
from tradingstudy.structure.profile import volume_profile
from tradingstudy.structure.ranges import ranges_and_flips
from tradingstudy.structure.swings import zigzag


def path_bars(closes):
    closes = np.asarray(closes, dtype=float)
    opens = np.r_[closes[0], closes[:-1]]
    idx = pd.date_range("2024-01-01", periods=len(closes), freq="15min", tz="UTC")
    return pd.DataFrame({"open": opens, "high": np.maximum(opens, closes) + 0.5,
                         "low": np.minimum(opens, closes) - 0.5, "close": closes, "volume": 1.0}, index=idx)


def seg(a, b):
    step = 1 if b > a else -1
    return list(range(a + step, b + step, step))


def bearish_flip_path():
    p = [100] * 20                      # warm-up so ATR exists
    p += seg(100, 110) + seg(110, 100)  # H1, L1
    p += seg(100, 110) + seg(110, 100)  # H2, L2
    p += seg(100, 104)                  # rally confirms L2 -> range confirmed
    p += seg(104, 92)                   # breakdown below 99.5 and new low
    p += seg(92, 99)                    # rally back to the old range low (touch)
    touch_bar = len(p) - 1
    p += [98]                           # bearish rejection bar
    reject_bar = len(p) - 1
    p += seg(98, 90)
    return p, touch_bar, reject_bar


def test_bearish_range_flip_fires_on_the_right_bars():
    closes, touch_bar, reject_bar = bearish_flip_path()
    bars = path_bars(closes)
    sw = zigzag(bars, 3)
    state, ev, rg = ranges_and_flips(bars, sw)
    bear = ev[ev.direction == -1]
    assert len(rg) >= 1 and (rg.outcome == -1).any()
    assert bear.loc[bear.variant == 1, "bar"].tolist() == [touch_bar], "front-run fires on the first touch"
    assert bear.loc[bear.variant == 0, "bar"].tolist() == [reject_bar], "confirmed fires on the bearish rejection"
    r = bear.iloc[0]
    assert r.range_low == pytest.approx(99.5) and r.range_high == pytest.approx(110.5)
    assert r.new_swing_px == pytest.approx(91.5)


def test_flip_invalidated_by_close_back_inside():
    closes, touch_bar, _ = bearish_flip_path()
    closes = closes[: touch_bar + 1] + [101, 102, 98, 97]  # closes back above range low + 0.5 ATR before rejecting
    bars = path_bars(closes)
    _, ev, _ = ranges_and_flips(bars, zigzag(bars, 3))
    assert (ev[(ev.direction == -1) & (ev.variant == 0)]).empty


def test_held_level_holds_then_flips_role():
    # support at ~99.5 tested twice, then broken: it must become resistance (flipped)
    p = [100] * 20 + seg(100, 106) + seg(106, 100) + seg(100, 106) + seg(106, 100) + seg(100, 104) + seg(104, 95)
    bars = path_bars(p)
    atr = ta.atr(bars.high, bars.low, bars.close, 14)
    sw = zigzag(bars, 3)
    held = lv.held_levels(bars, sw, atr, 15)
    last = len(bars) - 1
    j = np.nanargmin(np.abs(held["price"][last] - 99.5))
    assert held["price"][last, j] == pytest.approx(99.5)
    assert held["holds"][last, j] >= 2
    assert held["role"][last, j] == 1 and held["flipped"][last, j]


def test_volume_profile_known_answer():
    idx = pd.date_range("2024-01-01", periods=5, freq="1min", tz="UTC")
    m1 = pd.DataFrame({"low": [100, 100, 104.0, 104.0, 108], "high": [101, 101, 105.0, 105.0, 109],
                       "volume": [1, 1, 10, 10, 1]}, index=idx)
    p = volume_profile(m1, 1.0)
    assert p["poc"] == pytest.approx(104.5)
    assert p["val"] <= 104 and p["vah"] >= 105


def test_fib_math():
    assert lv.fib_retrace(100, 110, 0.618) == pytest.approx(103.82)
    assert lv.fib_extend(100, 110, 1.272) == pytest.approx(112.72)
    assert lv.fib_retrace(110, 100, 0.5) == pytest.approx(105)


@pytest.mark.parametrize("cut", [700, 1500])
def test_structure_no_lookahead_synthetic(cut):
    rng = np.random.default_rng(5)
    closes = 100 * np.exp(np.cumsum(rng.standard_normal(3000) * 0.004))
    bars = path_bars(closes)
    bars["high"] = bars[["open", "close"]].max(axis=1) * (1 + rng.random(3000) * 0.002)
    bars["low"] = bars[["open", "close"]].min(axis=1) * (1 - rng.random(3000) * 0.002)
    def run(b):
        sw = zigzag(b, 2)
        st, ev, rg = ranges_and_flips(b, sw, tol=1.0, h_min=2.0)
        atr = ta.atr(b.high, b.low, b.close, 14)
        held = lv.held_levels(b, sw, atr, 15)
        legs = lv.fib_legs(sw, len(b))
        return sw, st, ev, held, legs
    f_sw, f_st, f_ev, f_h, f_l = run(bars)
    t_sw, t_st, t_ev, t_h, t_l = run(bars.iloc[:cut])
    pd.testing.assert_frame_equal(f_sw[f_sw.confirm_bar < cut].reset_index(drop=True), t_sw.reset_index(drop=True))
    pd.testing.assert_frame_equal(f_st.iloc[:cut], t_st)
    pd.testing.assert_frame_equal(f_ev[f_ev.bar < cut].reset_index(drop=True), t_ev.reset_index(drop=True))
    for k in ("price", "strength", "role", "flipped"):
        np.testing.assert_array_equal(f_h[k][:cut], t_h[k])
    np.testing.assert_array_equal(f_l[:cut], t_l)


# ---------------- v2: armed setups + retest scanner with the "respect" rule ----------------
from tradingstudy.structure.ranges import range_setups_v2, scan_retests  # noqa: E402


def v2_events(bars, same_tf=True, exec_bars=None, exec_min=15):
    sw = zigzag(bars, 3)
    _, su, _ = range_setups_v2(bars, sw)
    return su, scan_retests(su, bars, 15, bars if exec_bars is None else exec_bars, exec_min, same_tf)


def test_v2_flip_fires_with_respect_rule():
    closes, touch_bar, reject_bar = bearish_flip_path()
    bars = path_bars(closes)
    su, ev = v2_events(bars)
    bear = ev[ev.direction == -1]
    assert bear.loc[bear.variant == 1, "bar"].tolist() == [touch_bar]
    assert bear.loc[bear.variant == 0, "bar"].tolist() == [reject_bar]
    # structure stop input: highest high from the first touch to the entry bar
    assert bear.loc[bear.variant == 0, "retest_extreme"].iloc[0] == pytest.approx(bars.high.iloc[touch_bar:reject_bar + 1].max())


def test_v2_rejection_must_not_open_beyond_level():
    closes, touch_bar, reject_bar = bearish_flip_path()
    bars = path_bars(closes)
    # make the rejection candle open ABOVE the old range low (99.5) while still closing red below it
    bars.iloc[reject_bar, bars.columns.get_loc("open")] = 99.8
    bars.iloc[reject_bar, bars.columns.get_loc("high")] = 100.0
    _, ev = v2_events(bars)
    a = ev[(ev.direction == -1) & (ev.variant == 0)]
    assert reject_bar not in a["bar"].tolist()


def test_v2_htf_scan_starts_after_armed_bar_close():
    closes, touch_bar, reject_bar = bearish_flip_path()
    bars = path_bars(closes)
    su, ev_same = v2_events(bars)
    _, ev_htf = v2_events(bars, same_tf=False)
    armed = su[su.direction == -1]["armed_bar"].iloc[0]
    assert (ev_htf["bar"] > armed).all()  # never on or before the armed range-TF bar
    assert len(ev_same) >= len(ev_htf)
