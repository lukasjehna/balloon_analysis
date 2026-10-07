#!/usr/bin/env python3
"""Despiking, and saving/loading of detected spike positions."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import NamedTuple

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

_MAD_TO_SIGMA = 1.4826  # scales MAD to a standard deviation for Gaussian data
_MIN_FINITE_SAMPLES = 3


# --------------------------------------------------------------------------- #
# Detection / despiking
# --------------------------------------------------------------------------- #

def _odd_window(window: int) -> int:
    """Smallest odd integer >= max(3, window)."""
    return max(3, int(window) | 1)


def _running_median(values: np.ndarray, window: int) -> np.ndarray:
    """Centered running median with edge-replicated padding (same length as input)."""
    pad = window // 2
    padded = np.pad(values, (pad, pad), mode="edge")
    return np.median(sliding_window_view(padded, window), axis=1)


def _detect_spikes(
    arr: np.ndarray, window: int, sigma_thresh: float
) -> tuple[np.ndarray, np.ndarray]:
    """Return (spike indices into `arr`, median replacement values)."""
    finite = np.isfinite(arr)
    if np.count_nonzero(finite) < _MIN_FINITE_SAMPLES:
        return np.empty(0, dtype=np.intp), np.empty(0, dtype=float)

    vals = arr[finite]
    med = _running_median(vals, _odd_window(window))

    resid = vals - med
    mad = np.median(np.abs(resid))
    sigma = max(_MAD_TO_SIGMA * mad, np.finfo(float).eps)
    spikes = np.abs(resid) > sigma_thresh * sigma

    return np.flatnonzero(finite)[spikes], med[spikes]


def _window_bounds(size: int, bin_start: int, bin_stop: int) -> tuple[int, int] | None:
    """Clip [bin_start, bin_stop] (inclusive) to the array; None if empty."""
    if size == 0:
        return None
    i0 = max(0, int(bin_start))
    i1 = min(size - 1, int(bin_stop))
    return None if i0 > i1 else (i0, i1)


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
    out = np.array(y, dtype=float)  # copy
    idx, replacement = _detect_spikes(out, window, sigma_thresh)
    out[idx] = replacement
    return out, int(idx.size)


def despike_1d_in_window(
    y: np.ndarray,
    bin_start: int,
    bin_stop: int,
    window: int = 5,
    sigma_thresh: float = 6.0,
) -> tuple[np.ndarray, int]:
    """Despike only inside [bin_start, bin_stop] (inclusive); the rest is unchanged."""
    out = np.array(y, dtype=float)  # copy
    bounds = _window_bounds(out.size, bin_start, bin_stop)
    if bounds is None:
        return out, 0

    i0, i1 = bounds
    idx, replacement = _detect_spikes(out[i0 : i1 + 1], window, sigma_thresh)
    out[idx + i0] = replacement
    return out, int(idx.size)


def find_spikes_1d(
    y: np.ndarray,
    window: int = 5,
    sigma_thresh: float = 6.0,
    bin_start: int | None = None,
    bin_stop: int | None = None,
) -> np.ndarray:
    """Return the positions (indices into `y`) that despike_1d[_in_window] would replace.

    If bin_start / bin_stop are given (inclusive), only that range is searched;
    returned indices are still relative to the full array.
    """
    arr = np.asarray(y, dtype=float)
    bounds = _window_bounds(
        arr.size,
        0 if bin_start is None else bin_start,
        arr.size - 1 if bin_stop is None else bin_stop,
    )
    if bounds is None:
        return np.empty(0, dtype=np.intp)

    i0, i1 = bounds
    idx, _ = _detect_spikes(arr[i0 : i1 + 1], window, sigma_thresh)
    return idx + i0


# --------------------------------------------------------------------------- #
# Saving / loading spike positions
# --------------------------------------------------------------------------- #

class SpikeFile(NamedTuple):
    indices: np.ndarray            # int array of spike positions
    values: np.ndarray | None      # original sample values, if they were saved
    meta: dict[str, str]           # '# key: value' header entries (all strings)


def save_spike_positions(
    path: Path | str,
    indices: np.ndarray,
    values: np.ndarray | None = None,
    **meta: object,
) -> Path:
    """Write spike positions to a CSV file and return its path.

    Format: optional '# key: value' comment lines (from **meta), then a header
    row 'index' or 'index,value', then one row per spike. `values` (e.g. the
    original samples at the spike positions) is optional.

    Example:
        idx = find_spikes_1d(y, window=5, sigma_thresh=6.0)
        save_spike_positions("run1_spikes.csv", idx, y[idx],
                             source="run1_hot.spec", window=5, sigma_thresh=6.0)
    """
    path = Path(path)
    idx = np.asarray(indices, dtype=np.intp).ravel()
    vals = None if values is None else np.asarray(values, dtype=float).ravel()
    if vals is not None and vals.shape != idx.shape:
        raise ValueError("values must have the same length as indices.")

    with path.open("w", newline="", encoding="utf-8") as f:
        for key, val in meta.items():
            clean = str(val).replace("\n", " ")
            f.write(f"# {key}: {clean}\n")

        writer = csv.writer(f)
        if vals is None:
            writer.writerow(["index"])
            writer.writerows([int(i)] for i in idx)
        else:
            writer.writerow(["index", "value"])
            writer.writerows([int(i), repr(float(v))] for i, v in zip(idx, vals))
    return path


def load_spike_positions(path: Path | str) -> SpikeFile:
    """Read a file written by `save_spike_positions`."""
    meta: dict[str, str] = {}
    rows: list[list[str]] = []

    with Path(path).open("r", newline="", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("#"):
                key, sep, val = line[1:].partition(":")
                if sep:
                    meta[key.strip()] = val.strip()
                continue
            rows.append(next(csv.reader([line])))

    if not rows or rows[0][0].strip().lower() != "index":
        raise ValueError(f"{path}: missing 'index' header row.")

    has_values = len(rows[0]) > 1
    data = rows[1:]
    indices = np.array([int(r[0]) for r in data], dtype=np.intp)
    values = np.array([float(r[1]) for r in data], dtype=float) if has_values else None
    return SpikeFile(indices, values, meta)
