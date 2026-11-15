import numpy as np
import pandas as pd
import pytest

from tradingstudy.config import DEV_END, DEV_START
from tradingstudy.data import guard
from tradingstudy.data.clean import _to_utc
from tradingstudy.data.resample import resample_1m


def make_1m(start: str, minutes: int, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    idx = pd.date_range(start, periods=minutes, freq="1min", tz="UTC", name="ts")
    close = 100 + rng.standard_normal(minutes).cumsum()
    open_ = np.r_[100, close[:-1]]
    high = np.maximum(open_, close) + rng.random(minutes)
    low = np.minimum(open_, close) - rng.random(minutes)
    vol = rng.random(minutes) * 10
    return pd.DataFrame({"open": open_, "high": high, "low": low, "close": close, "volume": vol}, index=idx)


@pytest.mark.parametrize("minutes", [6, 15, 24, 30, 60, 240, 1440])
def test_resample_matches_pandas_and_is_midnight_anchored(minutes):
    df = make_1m("2024-03-01 00:00", 3 * 1440)
    r = resample_1m(df, minutes)
    ref = df.resample(f"{minutes}min", origin="start_day", label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    pd.testing.assert_frame_equal(r[["open", "high", "low", "close", "volume"]], ref, check_freq=False, check_names=False)
    assert (r.index.normalize() == r.index.normalize()).all()
    assert r.index[0] == pd.Timestamp("2024-03-01", tz="UTC")
    assert r["complete"].all()


def test_weekly_anchored_monday():
    df = make_1m("2024-03-06 00:00", 14 * 1440)  # starts on a Wednesday
    r = resample_1m(df, 10080)
    assert all(t.day_of_week == 0 for t in r.index)
    assert r.index[0] == pd.Timestamp("2024-03-04", tz="UTC")
    assert not r["complete"].iloc[0]  # first week only partly covered


def test_gaps_flagged_not_filled():
    df = make_1m("2024-03-01 00:00", 60)
    df = df.drop(df.index[10:13])  # 3 missing minutes inside the first 15m bar
    r = resample_1m(df, 15)
    assert r["n_1m"].iloc[0] == 12 and not r["complete"].iloc[0]
    assert r["complete"].iloc[1:].all()
    assert len(r) == 4


def test_timestamp_units():
    ms = pd.Series([1704067200000, 1704067200000 * 1000])
    t = _to_utc(ms)
    assert (t == pd.Timestamp("2024-01-01", tz="UTC")).all()


def test_dev_scope_excludes_holdouts_and_straddling_bars():
    idx = pd.date_range(DEV_START - pd.Timedelta(days=14), DEV_END + pd.Timedelta(days=14), freq="1D", tz="UTC")
    df = pd.DataFrame({"close": np.arange(len(idx), dtype=float)}, index=idx)
    d = guard.clip_scope(df, "1D", "dev")
    assert d.index.min() >= DEV_START
    assert (d.index + pd.Timedelta(days=1)).max() <= DEV_END
    # weekly bar that opens before DEV_END but closes after it must be excluded
    w = pd.DataFrame({"close": [1.0]}, index=pd.DatetimeIndex([DEV_END - pd.Timedelta(days=2)]))
    assert guard.clip_scope(w, "1W", "dev").empty


@pytest.mark.parametrize("scope", ["holdout_primary", "holdout_secondary"])
def test_holdout_locked(scope, monkeypatch, tmp_path):
    monkeypatch.setattr(guard, "UNLOCK_FILE", tmp_path / "holdout_unlock.json")
    df = pd.DataFrame({"close": [1.0]}, index=pd.DatetimeIndex([DEV_END], tz="UTC"))
    with pytest.raises(guard.HoldoutLocked):
        guard.clip_scope(df, "1h", scope)
    with pytest.raises(guard.HoldoutLocked):
        guard.load_bars("BTC", "1h", scope)


def test_real_unlock_file_absent():
    assert not guard.UNLOCK_FILE.exists(), "holdout_unlock.json must not exist before Phase 4"


def test_bars_from_aggtrades():
    from tradingstudy.data.repair import bars_from_aggtrades, frozen_mask

    t = pd.to_datetime(["2024-01-01 00:00:10", "2024-01-01 00:00:50", "2024-01-01 00:01:05", "2024-01-01 00:01:30"], utc=True)
    agg = pd.DataFrame({"price": [10.0, 12.0, 11.0, 9.0], "quantity": [1.0, 2.0, 1.0, 3.0],
                        "first_trade_id": [1, 2, 5, 6], "last_trade_id": [1, 4, 5, 8],
                        "is_buyer_maker": [False, True, False, True]}, index=t)
    b = bars_from_aggtrades(agg)
    assert list(b.index) == list(pd.to_datetime(["2024-01-01 00:00", "2024-01-01 00:01"], utc=True))
    assert b.iloc[0][["open", "high", "low", "close"]].tolist() == [10.0, 12.0, 10.0, 12.0]
    assert b.iloc[0]["volume"] == 3.0 and b.iloc[0]["count"] == 4 and b.iloc[0]["taker_buy_volume"] == 1.0
    assert b.iloc[1][["open", "high", "low", "close"]].tolist() == [11.0, 11.0, 9.0, 9.0]
    flat = pd.DataFrame({"open": [5.0, 5.0], "high": [5.0, 6.0], "low": [5.0, 5.0], "close": [5.0, 5.0], "volume": [0.0, 0.0]})
    assert frozen_mask(flat).tolist() == [True, False]
