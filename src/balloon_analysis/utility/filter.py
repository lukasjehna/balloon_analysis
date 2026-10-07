#!/usr/bin/env python3
"""Despiking."""

from __future__ import annotations

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

_MAD_TO_SIGMA = 1.4826  # scales MAD to a standard deviation for Gaussian data
_MIN_FINITE_SAMPLES = 3


def _odd_window(window: int) -> int:
    """Smallest odd integer >= max(3, window)."""
    return max(3, int(window) | 1)


def _running_median(values: np.ndarray, window: int) -> np.ndarray:
    """Centered running median with edge-replicated padding (same length as input)."""
    pad = window // 2
    padded = np.pad(values, (pad, pad), mode="edge")
    return np.median(sliding_window_view(padded, window), axis=1)


def despike_1d(
    y: np.ndarray,
    window: int = 5,
    sigma_thresh: float = 6.0,
) -> tuple[np.ndarray, int]:
    """Replace impulse-like outliers in the finite samples using a median/MAD rule.

    window:       size of the running median (forced to an odd integer >= 3).
    sigma_thresh: spike threshold in robust sigmas; smaller is more aggressive.

    Non-finite samples are left untouched and ignored when computing medians.
    Returns (despiked copy, number of samples replaced).
    """
    arr = np.asarray(y, dtype=float)
    out = arr.copy()

    finite = np.isfinite(arr)
    if np.count_nonzero(finite) < _MIN_FINITE_SAMPLES:
        return out, 0

    vals = arr[finite]
    med = _running_median(vals, _odd_window(window))

    resid = vals - med
    mad = np.median(np.abs(resid))
    sigma = max(_MAD_TO_SIGMA * mad, np.finfo(float).eps)
    spikes = np.abs(resid) > sigma_thresh * sigma

    out[np.flatnonzero(finite)[spikes]] = med[spikes]
    return out, int(np.count_nonzero(spikes))


def despike_1d_in_window(
    y: np.ndarray,
    bin_start: int,
    bin_stop: int,
    window: int = 5,
    sigma_thresh: float = 6.0,
) -> tuple[np.ndarray, int]:
    """Despike only inside [bin_start, bin_stop] (inclusive); the rest is unchanged."""
    out = np.array(y, dtype=float)  # copy
    if out.size == 0:
        return out, 0

    i0 = max(0, int(bin_start))
    i1 = min(out.size - 1, int(bin_stop))
    if i0 > i1:
        return out, 0

    segment = slice(i0, i1 + 1)
    out[segment], removed = despike_1d(out[segment], window=window, sigma_thresh=sigma_thresh)
    return out, removed
