#!/usr/bin/env python3
# despiking

import numpy as np


def despike_1d(y: np.ndarray, window: int = 5, sigma_thresh: float = 6.0) -> tuple[np.ndarray, int]:
    """Replace impulse-like outliers in finite samples using a median/MAD rule.
    smaller sigma_thresh  is more aggressive; window is the size of the median filter (odd integer >= 3)."""
    arr = np.asarray(y, dtype=float)
    out = arr.copy()

    finite = np.isfinite(arr)
    if np.count_nonzero(finite) < 3:
        return out, 0

    vals = arr[finite]
    w = max(3, int(window) | 1)  # odd window >= 3
    pad = w // 2
    padded = np.pad(vals, (pad, pad), mode="edge")
    med = np.array([np.median(padded[i:i + w]) for i in range(vals.size)], dtype=float)

    resid = vals - med
    mad = float(np.median(np.abs(resid)))
    sigma = max(1.4826 * mad, np.finfo(float).eps)
    spikes = np.abs(resid) > (sigma_thresh * sigma)

    idx = np.where(finite)[0]
    out[idx[spikes]] = med[spikes]
    return out, int(np.count_nonzero(spikes))


def despike_1d_in_window(
    y: np.ndarray,
    bin_start: int,
    bin_stop: int,
    window: int = 5,
    sigma_thresh: float = 6.0,
) -> tuple[np.ndarray, int]:
    """Apply despike only inside [bin_start, bin_stop] (inclusive)."""
    arr = np.asarray(y, dtype=float)
    out = arr.copy()
    if out.size == 0:
        return out, 0

    i0 = max(0, int(bin_start))
    i1 = min(out.size - 1, int(bin_stop))
    if i0 > i1:
        return out, 0

    filtered, removed = despike_1d(out[i0:i1 + 1], window=window, sigma_thresh=sigma_thresh)
    out[i0:i1 + 1] = filtered
    return out, removed