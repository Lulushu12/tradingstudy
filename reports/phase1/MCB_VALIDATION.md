# MCB clone validation (dev-period rows only)

Indicator matching against the TradingView exports. No returns or signals are evaluated.

## Conclusions

- WaveTrend matches to near-zero error on every timeframe once each export file's first 150 rows are dropped (TradingView recomputes indicators from the start of every exported chunk, so those rows carry warm-up error).
- The BTC exports come from the real Market Cipher B. The XRP 'HA SHA MFI' export comes from MCB_Clone_v1 (the PineScript formula reproduces it exactly), so it validates the port but is not an MCB reference.
- Best Money Flow match to real MCB: the MCB_Clone_v1 formula computed on Heikin-Ashi candles with no outer EMA (smooth 1): correlation 0.989 to 0.995 and 94 to 96% same-sign agreement on 5m to 1D, including years and timeframes not used for any choice. Chosen for discovery (user approved choosing by agreement).
- The brief's reverse-engineered HTF formula (3x TF, developing candle, SMA20, EMA5) reproduces the earlier ~87% figure (85 to 87% sign agreement) but loses to the Heikin-Ashi formula on every timeframe. Fixed 3H HTF is rejected (correlation 0.27 to 0.69). The brief's high-minus-low clone formula is weakest (correlation 0.82 to 0.86).
- Search size for this choice (no trading outcomes involved): HTF grid 440 settings, PineScript-family grid 126 settings, 4 structural variants, Heikin-Ashi grid 45 settings. Fitted on BTC 15m 2022-2023 only.

## WaveTrend

| Coin | TF | Rows | wt1 max abs err | wt2 max abs err | hist max abs err | wt2 corr | green dots = export up | red dots = export down | dots ours (g/r) | export (up/down) |
|---|---|---|---|---|---|---|---|---|---|---|
| BTC | 5m | 396,683 | 1.3698 | 0.6679 | 0.9132 | 1.0 | 1.0 | 1.0 | 39605/39600 | 39605/39600 |
| BTC | 15m | 133,441 | 2.1268 | 1.8928 | 1.4179 | 1.0 | 1.0 | 1.0 | 13349/13348 | 13349/13348 |
| BTC | 1h | 17,290 | 0.0971 | 0.0529 | 0.0647 | 1.0 | 1.0 | 1.0 | 1707/1707 | 1707/1707 |
| BTC | 4h | 8,184 | 0.0275 | 0.0133 | 0.0184 | 1.0 | 1.0 | 1.0 | 799/800 | 799/800 |
| BTC | 1D | 1,264 | 0.0 | 0.0 | 0.0 | 1.0 | 1.0 | 1.0 | 113/114 | 113/114 |
| BTC | 1W | 141 | 0.0973 | 0.1165 | 0.0192 | 1.0 | 1.0 | 1.0 | 14/15 | 14/15 |

## Money Flow: fitted HTF settings (fit on BTC 15m 2022-01..2023-12 only)

| Model | SMA len (HTF bars) | EMA len (chart bars) | Scale | Offset | Corr on fit data |
|---|---|---|---|---|---|
| 3x_developing | 20 | 5 | 169.2 | -0.322 | 0.8908 |
| 3x_step | 20 | 2 | 165.0 | -0.303 | 0.8898 |
| 3H_developing | 10 | 3 | 88.2 | -0.383 | 0.6881 |
| 3H_step | 10 | 1 | 78.7 | -0.324 | 0.6217 |
| pine_affine | | | 0.966 | 2.450 | |
| clone_affine | | | 1.681 | 3.555 | |

## Money Flow: agreement with export

sign agree = same side of zero (green/red). slope agree = moving in the same direction bar to bar.

| Coin | TF | Segment | Candidate | Rows | Corr | Sign agree | Slope agree | MAE |
|---|---|---|---|---|---|---|---|---|
| BTC | 5m | all | pine (as coded) | 396,683 | 0.96205 | 0.9003 | 0.8474 | 4.1185 |
| BTC | 5m | all | clone h-l (as briefed) | 396,683 | 0.82135 | 0.7935 | 0.6623 | 8.603 |
| BTC | 5m | all | pine on Heikin-Ashi (smooth 1) | 396,683 | 0.99003 | 0.9499 | 0.9266 | 13.3612 |
| BTC | 5m | all | pine on Heikin-Ashi (smooth 2) | 396,683 | 0.98946 | 0.9489 | 0.9221 | 13.2652 |
| BTC | 5m | all | pine on Heikin-Ashi (smooth 4) | 396,683 | 0.98358 | 0.9377 | 0.8439 | 13.177 |
| BTC | 5m | all | pine (fitted scale) | 396,683 | 0.96205 | 0.9128 | 0.8474 | 3.6076 |
| BTC | 5m | all | clone h-l (fitted scale) | 396,683 | 0.82135 | 0.8087 | 0.6623 | 7.6358 |
| BTC | 5m | all | htf 3x_developing (sma20, ema5) | 396,683 | 0.89998 | 0.8578 | 0.7642 | 5.8341 |
| BTC | 5m | all | htf 3x_step (sma20, ema2) | 396,683 | 0.89804 | 0.8557 | 0.7192 | 5.8849 |
| BTC | 5m | all | htf 3H_developing (sma10, ema3) | 396,683 | 0.39782 | 0.6327 | 0.6852 | 12.8267 |
| BTC | 5m | all | htf 3H_step (sma10, ema1) | 396,683 | 0.26497 | 0.5885 | 0.0155 | 13.6762 |
| BTC | 15m | fit_2022_2023 | pine (as coded) | 68,677 | 0.95853 | 0.8907 | 0.8403 | 4.1841 |
| BTC | 15m | fit_2022_2023 | clone h-l (as briefed) | 68,677 | 0.82962 | 0.785 | 0.6505 | 8.5991 |
| BTC | 15m | fit_2022_2023 | pine on Heikin-Ashi (smooth 1) | 68,677 | 0.98909 | 0.9444 | 0.926 | 12.542 |
| BTC | 15m | fit_2022_2023 | pine on Heikin-Ashi (smooth 2) | 68,677 | 0.98846 | 0.9433 | 0.9234 | 12.4421 |
| BTC | 15m | fit_2022_2023 | pine on Heikin-Ashi (smooth 4) | 68,677 | 0.9822 | 0.9329 | 0.8445 | 12.3576 |
| BTC | 15m | fit_2022_2023 | pine (fitted scale) | 68,677 | 0.95853 | 0.9006 | 0.8403 | 3.6498 |
| BTC | 15m | fit_2022_2023 | clone h-l (fitted scale) | 68,677 | 0.82962 | 0.8012 | 0.6505 | 7.1716 |
| BTC | 15m | fit_2022_2023 | htf 3x_developing (sma20, ema5) | 68,677 | 0.89075 | 0.8495 | 0.7536 | 5.8083 |
| BTC | 15m | fit_2022_2023 | htf 3x_step (sma20, ema2) | 68,677 | 0.88984 | 0.8464 | 0.7129 | 5.8395 |
| BTC | 15m | fit_2022_2023 | htf 3H_developing (sma10, ema3) | 68,677 | 0.68811 | 0.7387 | 0.6645 | 9.3194 |
| BTC | 15m | fit_2022_2023 | htf 3H_step (sma10, ema1) | 68,677 | 0.62165 | 0.7086 | 0.0486 | 10.054 |
| BTC | 15m | test_2024_2025 | pine (as coded) | 64,764 | 0.96389 | 0.8983 | 0.8436 | 4.1621 |
| BTC | 15m | test_2024_2025 | clone h-l (as briefed) | 64,764 | 0.8602 | 0.8099 | 0.6605 | 8.6615 |
| BTC | 15m | test_2024_2025 | pine on Heikin-Ashi (smooth 1) | 64,764 | 0.99029 | 0.9511 | 0.9275 | 13.689 |
| BTC | 15m | test_2024_2025 | pine on Heikin-Ashi (smooth 2) | 64,764 | 0.98985 | 0.9501 | 0.9241 | 13.5908 |
| BTC | 15m | test_2024_2025 | pine on Heikin-Ashi (smooth 4) | 64,764 | 0.98441 | 0.9398 | 0.8441 | 13.4983 |
| BTC | 15m | test_2024_2025 | pine (fitted scale) | 64,764 | 0.96389 | 0.9122 | 0.8436 | 3.6304 |
| BTC | 15m | test_2024_2025 | clone h-l (fitted scale) | 64,764 | 0.8602 | 0.83 | 0.6605 | 6.9835 |
| BTC | 15m | test_2024_2025 | htf 3x_developing (sma20, ema5) | 64,764 | 0.91296 | 0.868 | 0.7613 | 5.5823 |
| BTC | 15m | test_2024_2025 | htf 3x_step (sma20, ema2) | 64,764 | 0.91057 | 0.8668 | 0.7202 | 5.658 |
| BTC | 15m | test_2024_2025 | htf 3H_developing (sma10, ema3) | 64,764 | 0.65545 | 0.7292 | 0.6707 | 10.3241 |
| BTC | 15m | test_2024_2025 | htf 3H_step (sma10, ema1) | 64,764 | 0.5833 | 0.7041 | 0.049 | 11.0906 |
| BTC | 1h | all | pine (as coded) | 17,290 | 0.96092 | 0.8842 | 0.8469 | 4.5384 |
| BTC | 1h | all | clone h-l (as briefed) | 17,290 | 0.85997 | 0.8017 | 0.6616 | 9.3257 |
| BTC | 1h | all | pine on Heikin-Ashi (smooth 1) | 17,290 | 0.99067 | 0.9466 | 0.9267 | 13.7595 |
| BTC | 1h | all | pine on Heikin-Ashi (smooth 2) | 17,290 | 0.99016 | 0.9438 | 0.9217 | 13.6625 |
| BTC | 1h | all | pine on Heikin-Ashi (smooth 4) | 17,290 | 0.98481 | 0.933 | 0.8442 | 13.5737 |
| BTC | 1h | all | pine (fitted scale) | 17,290 | 0.96092 | 0.8985 | 0.8469 | 3.8863 |
| BTC | 1h | all | clone h-l (fitted scale) | 17,290 | 0.85997 | 0.8213 | 0.6616 | 7.2675 |
| BTC | 1h | all | htf 3x_developing (sma20, ema5) | 17,290 | 0.90815 | 0.8541 | 0.7564 | 5.9563 |
| BTC | 1h | all | htf 3x_step (sma20, ema2) | 17,290 | 0.90716 | 0.8552 | 0.7196 | 5.9726 |
| BTC | 1h | all | htf 3H_developing (sma10, ema3) | 17,290 | 0.60818 | 0.7079 | 0.6452 | 11.1745 |
| BTC | 1h | all | htf 3H_step (sma10, ema1) | 17,290 | 0.60772 | 0.7079 | 0.2157 | 11.1807 |
| BTC | 4h | all | pine (as coded) | 8,184 | 0.96751 | 0.8996 | 0.8469 | 4.0758 |
| BTC | 4h | all | clone h-l (as briefed) | 8,184 | 0.84967 | 0.826 | 0.6557 | 9.36 |
| BTC | 4h | all | pine on Heikin-Ashi (smooth 1) | 8,184 | 0.99199 | 0.9501 | 0.9242 | 14.4571 |
| BTC | 4h | all | pine on Heikin-Ashi (smooth 2) | 8,184 | 0.99113 | 0.9493 | 0.9246 | 14.3739 |
| BTC | 4h | all | pine on Heikin-Ashi (smooth 4) | 8,184 | 0.98513 | 0.9396 | 0.845 | 14.307 |
| BTC | 4h | all | pine (fitted scale) | 8,184 | 0.96751 | 0.9205 | 0.8469 | 3.5647 |
| BTC | 4h | all | clone h-l (fitted scale) | 8,184 | 0.84967 | 0.8229 | 0.6557 | 7.6426 |
| BTC | 4h | all | htf 3x_developing (sma20, ema5) | 8,184 | 0.89224 | 0.8515 | 0.7689 | 6.5422 |
| BTC | 4h | all | htf 3x_step (sma20, ema2) | 8,184 | 0.88964 | 0.8462 | 0.7079 | 6.6187 |
| BTC | 1D | all | pine (as coded) | 1,264 | 0.97482 | 0.8845 | 0.8432 | 3.8174 |
| BTC | 1D | all | clone h-l (as briefed) | 1,264 | 0.86458 | 0.8252 | 0.6698 | 10.0585 |
| BTC | 1D | all | pine on Heikin-Ashi (smooth 1) | 1,264 | 0.99511 | 0.9557 | 0.9359 | 14.7935 |
| BTC | 1D | all | pine on Heikin-Ashi (smooth 2) | 1,264 | 0.99449 | 0.9565 | 0.9153 | 14.6971 |
| BTC | 1D | all | pine on Heikin-Ashi (smooth 4) | 1,264 | 0.98916 | 0.9367 | 0.8448 | 14.6332 |
| BTC | 1D | all | pine (fitted scale) | 1,264 | 0.97482 | 0.8908 | 0.8432 | 3.3633 |
| BTC | 1D | all | clone h-l (fitted scale) | 1,264 | 0.86458 | 0.7959 | 0.6698 | 7.6609 |
| BTC | 1D | all | htf 3x_developing (sma20, ema5) | 1,264 | 0.91283 | 0.8639 | 0.7783 | 5.9033 |
| BTC | 1D | all | htf 3x_step (sma20, ema2) | 1,264 | 0.90668 | 0.8568 | 0.7055 | 6.09 |
| BTC | 1W | all | pine (as coded) | 133 | 0.9719 | 0.9774 | 0.8258 | 2.5629 |
| BTC | 1W | all | clone h-l (as briefed) | 141 | 0.9478 | 0.9362 | 0.65 | 8.7402 |
| BTC | 1W | all | pine on Heikin-Ashi (smooth 1) | 136 | 0.9952 | 0.9044 | 0.9333 | 16.056 |
| BTC | 1W | all | pine on Heikin-Ashi (smooth 2) | 135 | 0.99368 | 0.9037 | 0.9552 | 15.983 |
| BTC | 1W | all | pine on Heikin-Ashi (smooth 4) | 133 | 0.98175 | 0.8872 | 0.8409 | 15.8623 |
| BTC | 1W | all | pine (fitted scale) | 133 | 0.9719 | 0.9624 | 0.8258 | 3.4677 |
| BTC | 1W | all | clone h-l (fitted scale) | 141 | 0.9478 | 0.9504 | 0.65 | 3.3335 |
| BTC | 1W | all | htf 3x_developing (sma20, ema5) | 141 | 0.97463 | 0.9504 | 0.7571 | 4.9016 |
| XRP | 15m | all | pine (as coded) | 125,483 | 1.0 | 1.0 | 1.0 | 0.0011 |
| XRP | 15m | all | clone h-l (as briefed) | 125,483 | 0.83937 | 0.8145 | 0.7757 | 8.4531 |
| XRP | 15m | all | pine on Heikin-Ashi (smooth 1) | 125,483 | 0.96303 | 0.9063 | 0.8348 | 13.6081 |
| XRP | 15m | all | pine on Heikin-Ashi (smooth 2) | 125,483 | 0.96268 | 0.9062 | 0.8067 | 13.5068 |
| XRP | 15m | all | pine on Heikin-Ashi (smooth 4) | 125,483 | 0.95853 | 0.9019 | 0.7617 | 13.3715 |
| XRP | 15m | all | pine (fitted scale) | 125,483 | 1.0 | 0.938 | 1.0 | 2.5221 |
| XRP | 15m | all | clone h-l (fitted scale) | 125,483 | 0.83937 | 0.7876 | 0.7757 | 7.8456 |
| XRP | 15m | all | htf 3x_developing (sma20, ema5) | 125,483 | 0.87254 | 0.8143 | 0.8029 | 7.0528 |
| XRP | 15m | all | htf 3x_step (sma20, ema2) | 125,483 | 0.86779 | 0.8126 | 0.6728 | 7.1464 |
| XRP | 15m | all | htf 3H_developing (sma10, ema3) | 125,483 | 0.66612 | 0.7256 | 0.7144 | 9.8408 |
| XRP | 15m | all | htf 3H_step (sma10, ema1) | 125,483 | 0.6049 | 0.7025 | 0.0488 | 10.4512 |

## HTF model: scale refitted per timeframe (stable scale = model generalises)

| Coin | TF | Model | Scale | Offset |
|---|---|---|---|---|
| BTC | 5m | 3x_developing | 157.3 | -0.302 |
| BTC | 5m | 3x_step | 153.53 | -0.316 |
| BTC | 5m | 3H_developing | 50.42 | -0.449 |
| BTC | 5m | 3H_step | 33.55 | -0.217 |
| BTC | 15m | 3x_developing | 165.1 | -0.313 |
| BTC | 15m | 3x_step | 161.13 | -0.303 |
| BTC | 15m | 3H_developing | 85.23 | -0.648 |
| BTC | 15m | 3H_step | 75.71 | -0.547 |
| BTC | 1h | 3x_developing | 173.34 | -1.279 |
| BTC | 1h | 3x_step | 169.55 | -1.303 |
| BTC | 1h | 3H_developing | 80.78 | -0.234 |
| BTC | 1h | 3H_step | 78.12 | -0.267 |
| BTC | 4h | 3x_developing | 166.86 | -1.34 |
| BTC | 4h | 3x_step | 163.58 | -1.373 |
| BTC | 1D | 3x_developing | 174.29 | 0.7 |
| BTC | 1D | 3x_step | 170.01 | 0.767 |
| BTC | 1W | 3x_developing | 146.97 | -1.836 |
| BTC | 1W | 3x_step | nan | nan |
| XRP | 15m | 3x_developing | 160.05 | -4.303 |
| XRP | 15m | 3x_step | 155.52 | -4.244 |
| XRP | 15m | 3H_developing | 83.91 | -3.19 |
| XRP | 15m | 3H_step | 75.35 | -3.065 |
