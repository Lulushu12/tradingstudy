"""engine2: engine.simulate plus Breakoutprop's daily swap (0.033% of notional per position open at
00:00 UTC) and an optional forced exit at the close of the last bar before 00:00 UTC (flat=True).
day_open[k] = 1 if bar k opens at 00:00 UTC; flat_flag[k] = 1 if bar k closes at 00:00 UTC."""
import numpy as np
from numba import njit
from engine import _first_hit_1m, FEE, SLIP

SWAP = 0.00033


@njit(cache=True)
def simulate2(o, h, l, c, h1, l1, mm, sig, sl_dist, atr_v, trail_src,
              tp_r, be_r, trail_type, trail_mult, max_bars, exit_on_opp,
              partial_r, partial_frac, fee, slip, day_open, flat_flag, flat, swap):
    """Returns array of trades: [entry_bar, exit_bar, dir, entry_px, exit_px, sl_pct, r_net, reason]
    reason: 1 stop, 2 target, 3 time, 4 opposite signal, 5 trail/ema close exit, 6 end of data, 7 flat before 00:00 UTC
    """
    n = c.size
    n1 = h1.size
    out = np.empty((n // 2 + 1, 8))
    t = 0
    i = 0
    while i < n - 1:
        d = sig[i]
        if d == 0 or np.isnan(sl_dist[i]) or sl_dist[i] <= 0:
            i += 1
            continue
        e = i + 1
        raw = o[e]
        entry = raw * (1 + d * slip)
        sd = sl_dist[i]
        stop = raw - d * sd
        tp = raw + d * tp_r * sd if tp_r > 0 else (np.inf if d == 1 else -np.inf)
        ptp = raw + d * partial_r * sd if partial_r > 0 else np.nan
        sl_pct = sd / entry
        remaining = 1.0
        realized = 0.0   # in pct of entry notional, weighted by fraction
        be_done = False
        part_done = partial_r <= 0
        ext = raw  # extreme since entry
        exit_px = np.nan
        reason = 6
        j = e
        while j < n:
            # --- intrabar checks
            if d == 1:
                gap_stop = o[j] <= stop
                hit_s = l[j] <= stop
                hit_t = h[j] >= tp
                hit_p = (not part_done) and h[j] >= ptp
            else:
                gap_stop = o[j] >= stop
                hit_s = h[j] >= stop
                hit_t = l[j] <= tp
                hit_p = (not part_done) and l[j] <= ptp
            if gap_stop:
                exit_px = o[j] * (1 - d * slip)
                reason = 1
                break
            if hit_p and not hit_s:
                realized += partial_frac * (d * (ptp - entry) / entry - fee)
                remaining -= partial_frac
                part_done = True
            if hit_s and hit_t:
                s1 = mm[j]
                e1 = mm[j + 1] if j + 1 < n else n1
                w = _first_hit_1m(h1, l1, s1, e1, d, stop, tp)
                if w == 1:
                    exit_px = stop * (1 - d * slip)
                    reason = 1
                else:
                    exit_px = tp
                    reason = 2
                break
            if hit_s:
                if hit_p and not part_done:
                    pass
                exit_px = stop * (1 - d * slip)
                reason = 1
                break
            if hit_t:
                exit_px = tp
                reason = 2
                break
            # --- bar close management
            if d == 1:
                ext = max(ext, h[j])
            else:
                ext = min(ext, l[j])
            if max_bars > 0 and j - e + 1 >= max_bars:
                exit_px = c[j] * (1 - d * slip)
                reason = 3
                break
            if flat and flat_flag[j]:
                exit_px = c[j] * (1 - d * slip)
                reason = 7
                break
            if exit_on_opp and j < n - 1 and sig[j] == -d:
                exit_px = c[j] * (1 - d * slip)
                reason = 4
                break
            if trail_type == 3:
                # close beyond trail_src (e.g. an EMA) exits
                if (d == 1 and c[j] < trail_src[j]) or (d == -1 and c[j] > trail_src[j]):
                    exit_px = c[j] * (1 - d * slip)
                    reason = 5
                    break
            if trail_type == 4:
                # profit-taking exit: close back beyond trail_src in the trade's favour
                # (Connors-style: long exits when close > SMA(n))
                if (d == 1 and c[j] > trail_src[j]) or (d == -1 and c[j] < trail_src[j]):
                    exit_px = c[j] * (1 - d * slip)
                    reason = 5
                    break
            if be_r > 0 and not be_done:
                if d * (ext - raw) >= be_r * sd:
                    # breakeven plus round-trip costs
                    nb = raw + d * raw * (2 * fee + 2 * slip)
                    if d == 1:
                        stop = max(stop, nb)
                    else:
                        stop = min(stop, nb)
                    be_done = True
            if trail_type == 1 and not np.isnan(atr_v[j]):
                ns = ext - d * trail_mult * atr_v[j]
                if d == 1:
                    stop = max(stop, ns)
                else:
                    stop = min(stop, ns)
            elif trail_type == 2:
                ns = l[j] if d == 1 else h[j]
                if d * (ext - raw) >= trail_mult * sd:  # activate after trail_mult R
                    if d == 1:
                        stop = max(stop, ns)
                    else:
                        stop = min(stop, ns)
            j += 1
        if j >= n:
            j = n - 1
            exit_px = c[j]
        nswap = 0
        for k in range(e + 1, j + 1):
            if day_open[k]:
                nswap += 1
        pnl = realized + remaining * (d * (exit_px - entry) / entry - fee) - fee - nswap * swap
        out[t, 0] = i
        out[t, 1] = j
        out[t, 2] = d
        out[t, 3] = entry
        out[t, 4] = exit_px
        out[t, 5] = sl_pct
        out[t, 6] = pnl / sl_pct
        out[t, 7] = reason
        t += 1
        if t >= out.shape[0]:
            break
        i = j  # a signal on the exit bar's close may open the next trade
    return out[:t]
