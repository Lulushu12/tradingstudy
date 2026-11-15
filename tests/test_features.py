"""Feature tests. The look-ahead test is the core one: a feature value at bar t must not change when bars after t
are removed or altered. Every feature function in the project must be registered in FEATURES below."""
import numpy as np
import pandas as pd
import pytest

from tradingstudy.features import mcb, ta


def synth(n=3000, seed=1, freq="15min") -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2023-01-02", periods=n, freq=freq, tz="UTC", name="ts")
    close = 100 * np.exp(np.cumsum(rng.standard_normal(n) * 0.003))
    open_ = np.r_[close[0], close[:-1]] * (1 + rng.standard_normal(n) * 0.0005)
    high = np.maximum(open_, close) * (1 + rng.random(n) * 0.002)
    low = np.minimum(open_, close) * (1 - rng.random(n) * 0.002)
    vol = rng.random(n) * 100 + 1
    return pd.DataFrame({"open": open_, "high": high, "low": low, "close": close, "volume": vol}, index=idx)


# name -> function(df) returning a DataFrame or array aligned with df
FEATURES = {
    "wavetrend": lambda d: mcb.wavetrend(d),
    "wt_signals": lambda d: mcb.wt_signals(mcb.wavetrend(d)),
    "mf_pine": lambda d: mcb.mf_pine(d),
    "mf_pine_ha": lambda d: mcb.mf_pine_ha(d, smooth=1),
    "mf_clone": lambda d: mcb.mf_clone(d),
    "mf_htf_developing": lambda d: mcb.mf_htf(d, 15, 45, developing=True),
    "mf_htf_step": lambda d: mcb.mf_htf(d, 15, 45, developing=False),
    "atr": lambda d: ta.atr(d["high"], d["low"], d["close"]),
}


def as_frame(x, index) -> pd.DataFrame:
    if isinstance(x, pd.DataFrame):
        return x.astype(float)
    if isinstance(x, pd.Series):
        return x.to_frame().astype(float)
    return pd.DataFrame({"v": np.asarray(x, dtype=float)}, index=index)


@pytest.mark.parametrize("name", list(FEATURES))
@pytest.mark.parametrize("cut", [1000, 1777, 2500])
def test_no_lookahead(name, cut):
    df = synth()
    full = as_frame(FEATURES[name](df), df.index)
    # 1) truncate the future
    trunc = as_frame(FEATURES[name](df.iloc[:cut]), df.index[:cut])
    pd.testing.assert_frame_equal(full.iloc[:cut], trunc, check_exact=False, rtol=1e-12, atol=1e-12)
    # 2) scramble the future (prices after cut replaced by a different random walk)
    other = synth(seed=99)
    df2 = df.copy()
    df2.iloc[cut:] = other.iloc[cut:].to_numpy() * (df["close"].iloc[cut - 1] / other["close"].iloc[cut - 1])
    alt = as_frame(FEATURES[name](df2), df.index)
    pd.testing.assert_frame_equal(full.iloc[:cut], alt.iloc[:cut], check_exact=False, rtol=1e-12, atol=1e-12)


def test_primitives_match_reference():
    x = synth()["close"].to_numpy()
    # SMA
    np.testing.assert_allclose(ta.sma(x, 20)[19:], pd.Series(x).rolling(20).mean().to_numpy()[19:], rtol=1e-10)
    # population stdev
    np.testing.assert_allclose(ta.stdev(x, 7)[6:], pd.Series(x).rolling(7).std(ddof=0).to_numpy()[6:], rtol=1e-8)
    # Pine EMA: SMA seed then recursion
    e = ta.ema(x, 10)
    assert np.isnan(e[:9]).all() and np.isclose(e[9], x[:10].mean())
    a = 2 / 11
    assert np.isclose(e[10], a * x[10] + (1 - a) * e[9])
    # RMA alpha
    r = ta.rma(x, 14)
    assert np.isclose(r[14], r[13] + (x[14] - r[13]) / 14)


def test_wavetrend_dots_alternate():
    wt = mcb.wavetrend(synth())
    d = wt.loc[wt.dot_green | wt.dot_red]
    colours = np.where(d.dot_green, 1, -1)
    assert (np.diff(colours) != 0).all(), "green and red cross dots must alternate"


def test_heikin_ashi():
    df = synth(50)
    ha = mcb.heikin_ashi(df)
    hc = df[["open", "high", "low", "close"]].mean(axis=1)
    np.testing.assert_allclose(ha["close"], hc)
    np.testing.assert_allclose(ha["open"].iloc[1:], ((ha["open"] + ha["close"]) / 2).iloc[:-1].to_numpy())
