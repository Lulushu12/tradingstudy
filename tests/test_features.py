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


# ---------------- multi-timeframe look-ahead tests (cut the future at the 1m level) ----------------
from tradingstudy.data.resample import resample_1m  # noqa: E402
from tradingstudy.features import context, divergence, htf  # noqa: E402


def synth_1m(days=40, seed=3):
    d = synth(days * 1440, seed=seed, freq="1min")
    return d


def mtf_features(m1: pd.DataFrame) -> pd.DataFrame:
    chart = resample_1m(m1, 15)
    h150 = resample_1m(m1, 150)
    h4 = resample_1m(m1, 240)
    d1 = resample_1m(m1, 1440)
    parts = [
        htf.htf_layer(h150, 150, chart.index, 15),
        context.trend_regimes(h4, d1, chart.index, 15),
        context.atr_regime(chart, 15, window_days=5),
        context.cmf(chart).to_frame(),
        htf.align_htf(context.cmf(h4).to_frame("cmf_4h"), 240, chart.index, 15),
        session_numeric(chart.index),
    ]
    return pd.concat(parts, axis=1).astype(float)


def session_numeric(idx):
    s = context.session(idx, 15)
    return s[["hour_utc", "weekday"]]


@pytest.mark.parametrize("cut_minutes", [20 * 1440 + 7, 31 * 1440 + 333])
def test_mtf_no_lookahead(cut_minutes):
    m1 = synth_1m()
    full = mtf_features(m1)
    trunc_m1 = m1.iloc[:cut_minutes]
    trunc = mtf_features(trunc_m1)
    # only chart bars fully closed before the cut are comparable
    last_ok = trunc_m1.index[-1] + pd.Timedelta(minutes=1) - pd.Timedelta(minutes=15)
    common = trunc.index[trunc.index <= last_ok]
    pd.testing.assert_frame_equal(full.loc[common], trunc.loc[common], check_exact=False, rtol=1e-10, atol=1e-10)


def test_align_htf_uses_only_closed_bars():
    m1 = synth_1m(10)
    chart, h4 = resample_1m(m1, 15), resample_1m(m1, 240)
    h4 = h4.assign(open_time=h4.index.as_unit("ns").asi8.astype(float))
    a = htf.align_htf(h4[["open_time"]], 240, chart.index, 15)
    htf_end = pd.to_datetime(a["open_time"].dropna().astype("int64"), unit="ns", utc=True) + pd.Timedelta(minutes=240)
    chart_close = a["open_time"].dropna().index + pd.Timedelta(minutes=15)
    assert (htf_end.to_numpy() <= chart_close.to_numpy()).all()
    # and it is the LATEST such bar: next HTF bar must end after the chart close
    assert ((htf_end + pd.Timedelta(minutes=240)).to_numpy() > chart_close.to_numpy()).all()


def test_funding_uses_published_values_only():
    idx = pd.date_range("2024-01-01", periods=96, freq="15min", tz="UTC")
    f = pd.DataFrame({"funding_rate": [0.0001, 0.0002, 0.0003], "interval_hours": [8.0, 8.0, 8.0]},
                     index=pd.to_datetime(["2024-01-01 00:00:00.001", "2024-01-01 08:00:00.001", "2024-01-01 16:00:00.001"], utc=True))
    out = context.funding_features(f, idx, 15)
    # bar opened 07:45 closes 08:00:00.000, before the 08:00:00.001 print -> still the first value
    assert out.loc[pd.Timestamp("2024-01-01 07:45", tz="UTC"), "funding_8h"] == pytest.approx(0.0001)
    assert out.loc[pd.Timestamp("2024-01-01 08:00", tz="UTC"), "funding_8h"] == pytest.approx(0.0002)
    # first bar closes 00:15, after the 00:00:00.001 print
    assert out["funding_8h"].iloc[0] == pytest.approx(0.0001)
    # a bar closing before any print has no value
    early = context.funding_features(f, pd.DatetimeIndex([pd.Timestamp("2023-12-31 23:30", tz="UTC")]), 15)
    assert np.isnan(early["funding_8h"].iloc[0])


DIV_FEATURES = {
    "wt_dot_div_v2": lambda d: divergence.wt_dot_divergences_v2(mcb.wavetrend(d), d),
    "mf_fractal_div_v2": lambda d: divergence.mf_fractal_divergences_v2(mcb.mf_pine_ha(d, smooth=1), d),
    "stack_b_v2": lambda d: divergence.stack_b_v2(pd.concat([divergence.wt_dot_divergences_v2(mcb.wavetrend(d), d),
                                                             divergence.mf_fractal_divergences_v2(mcb.mf_pine_ha(d, smooth=1), d)], axis=1), "bull"),
    "wt_dot_div": lambda d: divergence.wt_dot_divergences(mcb.wavetrend(d), d),
    "mf_pivot_div": lambda d: divergence.pivot_divergences(mcb.mf_pine_ha(d, smooth=1), d),
}


@pytest.mark.parametrize("name", list(DIV_FEATURES))
@pytest.mark.parametrize("cut", [1200, 2333])
def test_divergence_no_lookahead(name, cut):
    df = synth(4000, seed=7)
    full = as_frame(DIV_FEATURES[name](df), df.index)
    trunc = as_frame(DIV_FEATURES[name](df.iloc[:cut]), df.index[:cut])
    pd.testing.assert_frame_equal(full.iloc[:cut], trunc)


def test_divergence_events_on_handmade_series():
    # Two MF troughs: second is higher while price makes a lower low -> regular bullish, known 3 bars after pivot
    n = 40
    mf = np.full(n, 5.0)
    mf[10], mf[9], mf[11], mf[8], mf[12] = -10, -6, -6, -2, -2
    mf[25], mf[24], mf[26], mf[23], mf[27] = -5, -3, -3, -1, -1
    low = np.full(n, 100.0); low[10] = 95; low[25] = 93
    bars = pd.DataFrame({"low": low, "high": low + 1}, index=pd.date_range("2024-01-01", periods=n, freq="15min", tz="UTC"))
    ev = divergence.pivot_divergences(mf, bars)
    assert ev["mfdiv_bull_reg"].to_numpy().nonzero()[0].tolist() == [28]
    assert ev.loc[ev.index[28], "mfdiv_bull_reg_ref"] == 10


def test_mf_fractal_v2_handmade():
    # pivot lows at 10 (-6) and 20 (-4, higher) with price lower at 20 -> regular bullish, known at 22
    n = 30
    mf = np.full(n, 3.0)
    mf[8:13] = [-2, -3, -6, -3, -2]
    mf[18:23] = [-1, -2, -4, -2, -1]
    low = np.full(n, 100.0); low[10] = 95; low[20] = 94
    bars = pd.DataFrame({"low": low, "high": low + 1}, index=pd.date_range("2024-01-01", periods=n, freq="15min", tz="UTC"))
    ev = divergence.mf_fractal_divergences_v2(mf, bars)
    assert ev["mfdiv_bull_reg"].to_numpy().nonzero()[0].tolist() == [22]
    assert ev["mfdiv_bull_reg_pivot"].iloc[22] == 20
    # a pivot above the -2.5 filter does not count
    mf2 = mf.copy(); mf2[20] = -2.0; mf2[19] = mf2[21] = -1.5; mf2[18] = mf2[22] = -1.0
    assert not divergence.mf_fractal_divergences_v2(mf2, bars)["mfdiv_bull_reg"].any()
