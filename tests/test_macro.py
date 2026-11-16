import numpy as np
import pandas as pd
import pytest

from tradingstudy.data.resample import resample_1m
from tradingstudy.features import macro
from tests.test_features import synth


def test_lean_rule_matches_user_description():
    # green, neutral, neutral, red, neutral, green(strong), neutral
    s = [np.nan, 0, 1, 0, 0, -1, 0, 2, 0]
    assert macro.lean_bias(s).tolist()[1:] == [0, 1, -1, -1, -1, 1, 1, -1]
    # leading NaN stays NaN; neutral before any colour = 0 (no trade)
    assert np.isnan(macro.lean_bias(s)[0])


def test_align_uses_only_sources_closed_by_chart_open():
    idx = pd.date_range("2024-01-01", periods=10, freq="150min", tz="UTC")
    vals = pd.DataFrame({"state": np.arange(10, dtype=float)}, index=idx)
    chart = pd.date_range("2024-01-01 02:30", periods=4, freq="15min", tz="UTC")  # first chart bar opens exactly at source close
    a = macro.align_on_open(vals, 150, chart)
    assert a["state"].tolist() == [0.0, 0.0, 0.0, 0.0]  # source bar 0 closed at 02:30, bar 1 not yet
    late = pd.DatetimeIndex([pd.Timestamp("2024-01-01 04:45", tz="UTC")])  # last 15m bar inside source bar 1
    assert macro.align_on_open(vals, 150, late)["state"].iloc[0] == 0.0  # still bar 0, as in the indicator


@pytest.mark.parametrize("cut", [20 * 1440 + 7, 33 * 1440 + 401])
def test_macro_no_lookahead(cut):
    m1 = synth(45 * 1440, seed=11, freq="1min")
    def feats(m):
        chart, htf = resample_1m(m, 15), resample_1m(m, 150)
        return macro.macro_bias(htf, 150, chart.index, length=20)
    full = feats(m1)
    tr = feats(m1.iloc[:cut])
    last_ok = m1.index[cut - 1] + pd.Timedelta(minutes=1) - pd.Timedelta(minutes=15)
    ok = tr.index[tr.index <= last_ok]
    pd.testing.assert_frame_equal(full.loc[ok].astype(float), tr.loc[ok].astype(float))
