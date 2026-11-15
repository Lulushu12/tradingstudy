"""End-to-end look-ahead test on real dev data: build ALL features with the future removed (every timeframe keeps
only bars that had CLOSED by the cut time) and require identical values for every execution bar closed by then.
Skipped when the data has not been built in this container."""
import warnings

import numpy as np
import pandas as pd
import pytest

from tradingstudy.config import CLEAN
from tradingstudy.data import guard

pytestmark = pytest.mark.skipif(not (CLEAN / "15m" / "BTC.parquet").exists(), reason="data not built")

CUT = pd.Timestamp("2023-06-14 13:37", tz="UTC")


def _truncating_loader(real):
    def load(sym, tf, scope="dev"):
        df = real(sym, tf, scope)
        close_t = df.index + pd.Timedelta(minutes=guard.bar_minutes(tf))
        return df.loc[close_t <= CUT]
    return load


def _funding_trunc(real):
    def load(sym, scope="dev"):
        df = real(sym, scope)
        return df.loc[df.index <= CUT]
    return load


@pytest.mark.parametrize("tf", ["15m", "1h"])
def test_all_features_no_lookahead(tf, monkeypatch):
    warnings.filterwarnings("ignore")
    from tradingstudy.features import build as fb
    from tradingstudy.structure import build as sb

    full_f = fb.build_features("BTC", tf)
    full_s, full_ev = sb.build_structure("BTC", tf)

    real_load, real_fund = guard.load_bars, guard.load_funding
    for mod in (fb, sb):
        monkeypatch.setattr(mod, "load_bars", _truncating_loader(real_load))
    monkeypatch.setattr(fb, "load_funding", _funding_trunc(real_fund))
    trunc_f = fb.build_features("BTC", tf)
    trunc_s, trunc_ev = sb.build_structure("BTC", tf)

    cm = fb.EXEC_TFS[tf]
    ok = trunc_f.index[trunc_f.index + pd.Timedelta(minutes=cm) <= CUT]
    assert len(ok) > 1000
    num = full_f.select_dtypes(include=[np.number, bool]).columns
    pd.testing.assert_frame_equal(full_f.loc[ok, num].astype(float), trunc_f.loc[ok, num].astype(float), check_exact=False, rtol=1e-9, atol=1e-9)
    pd.testing.assert_frame_equal(full_s.loc[ok].astype(float), trunc_s.loc[ok].astype(float), check_exact=False, rtol=1e-9, atol=1e-9)
    # every flip event known before the cut must exist, identically, in the truncated run
    key = ["tf", "variant", "direction", "exec_time"]
    fe = full_ev[full_ev["exec_time"] + pd.Timedelta(minutes=cm) <= CUT].sort_values(key).reset_index(drop=True)
    te = trunc_ev.sort_values(key).reset_index(drop=True)
    cols = key + ["range_high", "range_low", "break_bar", "new_swing_px"]
    pd.testing.assert_frame_equal(fe[cols], te[cols])
