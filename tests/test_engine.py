"""Engine tests on hand-built 1m paths with known answers (PROTOCOL section 3)."""
import numpy as np
import pandas as pd
import pytest

from tradingstudy.backtest import engine as E

T0 = pd.Timestamp("2024-01-01", tz="UTC").value
MIN = E.MIN_NS


def run(bars, d=1, entry=100.0, R=1.0, target=102.0, tick=0.1, slip=0.001, start=0):
    b = np.asarray(bars, dtype=float)  # rows: open, high, low, close
    n = len(b)
    ts = T0 + np.arange(n, dtype=np.int64) * MIN
    out = E.simulate(ts, b[:, 0], b[:, 1], b[:, 2], b[:, 3], np.array([start]), np.array([ts[start]]),
                     np.array([d]), np.array([entry]), np.array([R]), np.array([target]), np.array([tick]),
                     np.array([slip]), E.FEE_RATE)
    return dict(zip(E.COLS, out[0]))


def flat(n, px=100.5):
    return [[px, px + 0.05, px - 0.05, px]] * n


def test_long_fill_then_target():
    bars = [[100.2, 100.3, 99.95, 100.0],   # touches 100 but does not trade through (needs <= 99.9)
            [100.0, 100.1, 99.85, 99.9],    # fills
            [99.9, 101.0, 99.8, 100.9],
            [100.9, 102.05, 100.8, 102.0],  # high 102.05 < target + tick (102.1): not filled
            [102.0, 102.2, 101.9, 102.1]]   # fills target
    r = run(bars)
    assert r["status"] == E.FILLED and r["fill_idx"] == 1 and r["exit_idx"] == 4 and r["exit_reason"] == E.TARGET
    assert r["net_R"] == pytest.approx(2.0 - 0.0004 * (100 + 102))


def test_missed_fill_then_cancel_and_hypothetical():
    bars = [[100.2, 100.3, 100.0, 100.1],   # touch, no trade-through
            [100.1, 100.6, 100.05, 100.5]]  # high 100.6 >= cancel 100.5 -> cancelled
    r = run(bars + flat(5, 102.5))
    assert r["status"] == E.CANCELLED and r["touched"] == 1
    # hypothetical fill at the touch minute (index 0): target reached later (102.5 >= 102.1)
    assert r["missed_hyp_reason"] == E.TARGET
    assert r["missed_hyp_net_R"] == pytest.approx(2.0 - 0.0004 * 202)


def test_expiry_after_24h():
    bars = flat(1500, 100.3)  # never touches 100, never reaches 100.5
    r = run(bars)
    assert r["status"] == E.EXPIRED and r["touched"] == 0
    assert r["end_ts"] == T0 + 1439 * MIN


def test_stop_gap_with_slippage():
    bars = [[100.0, 100.0, 99.85, 99.9],    # fill
            [99.9, 99.95, 99.5, 99.6],
            [98.5, 98.6, 98.4, 98.5]]       # opens below the stop (99) -> exit at open 98.5 minus slippage
    r = run(bars)
    assert r["exit_reason"] == E.STOP
    assert r["exit_px"] == pytest.approx(98.5 * 0.999)
    assert r["gross_R"] == pytest.approx(98.5 * 0.999 - 100)
    assert r["slip_R"] == pytest.approx(99 - 98.5 * 0.999)


def test_stop_and_target_same_minute_is_stop():
    bars = [[100.0, 100.0, 99.85, 99.9], [99.9, 102.5, 98.9, 100.0]]
    r = run(bars)
    assert r["exit_reason"] == E.STOP and r["exit_px"] == pytest.approx(99 * 0.999)


def test_stop_in_fill_minute():
    bars = [[100.0, 100.1, 98.8, 99.0]]  # trades through and down to the stop in the same minute
    r = run(bars)
    assert r["status"] == E.FILLED and r["exit_idx"] == 0 and r["exit_reason"] == E.STOP


def test_timeout_after_24h():
    bars = [[100.0, 100.0, 99.85, 99.9]] + flat(1600, 100.4)  # never hits 99 or 102.1 (and cancel no longer applies)
    r = run(bars)
    assert r["exit_reason"] == E.TIMEOUT and r["exit_idx"] == 1439
    assert r["exit_px"] == pytest.approx(100.4 * 0.999)


def test_short_target():
    bars = [[100.0, 100.15, 99.9, 100.1],   # short fills on high >= 100.1
            [100.1, 100.2, 98.5, 98.6],
            [98.6, 98.7, 97.85, 97.9]]      # target 98 needs low <= 97.9
    r = run(bars, d=-1, target=98.0)
    assert r["status"] == E.FILLED and r["exit_reason"] == E.TARGET
    assert r["net_R"] == pytest.approx(2.0 - 0.0004 * 198)


def test_fill_and_cancel_same_minute_is_fill():
    bars = [[100.2, 100.6, 99.8, 100.4]] + flat(3, 100.4)
    r = run(bars)
    assert r["status"] == E.FILLED and r["fill_idx"] == 0


def test_skipped_when_target_invalid():
    r = run(flat(3), target=np.nan)
    assert r["status"] == E.SKIPPED


def run_ex(bars, d=1, R=1.0, target=2.0, slip=0.0, hold_min=1440, market=True, entry=100.0):
    b = np.asarray(bars, dtype=float)
    ts = T0 + np.arange(len(b), dtype=np.int64) * MIN
    out = E.simulate_ex(ts, b[:, 0], b[:, 1], b[:, 2], b[:, 3], np.array([0]), np.array([ts[0]]), np.array([d]),
                        np.array([entry]), np.array([R]), np.array([target]), np.array([0.1]), np.array([slip]),
                        E.FEE_RATE, E.DAY_NS, hold_min * MIN, market)
    return dict(zip(E.COLS, out[0]))


def test_market_entry_fills_at_open_and_targets_from_fill():
    bars = [[101.0, 101.2, 100.8, 101.0], [101.0, 103.2, 100.9, 103.0]]  # fill at 101 (open), target 101 + 2R = 103
    r = run_ex(bars, slip=0.0)
    assert r["status"] == E.FILLED and r["fill_idx"] == 0
    assert r["exit_reason"] == E.TARGET and r["exit_px"] == pytest.approx(103.0)
    assert r["gross_R"] == pytest.approx(2.0)


def test_market_entry_slippage_and_long_hold():
    bars = [[100.0, 100.1, 99.9, 100.0]] + flat(3000, 100.5)
    r = run_ex(bars, slip=0.001, hold_min=2880)  # 48 h hold, nothing hit -> timeout at minute 2879
    assert r["exit_reason"] == E.TIMEOUT and r["exit_idx"] == 2879
    assert r["gross_R"] == pytest.approx(100.5 * 0.999 - 100.1)  # fill at 100 x 1.001


def test_default_simulate_unchanged():
    bars = [[100.0, 100.0, 99.85, 99.9]] + flat(1600, 100.4)
    r = run(bars)
    assert r["exit_reason"] == E.TIMEOUT and r["exit_idx"] == 1439
