#!/usr/bin/env python3
"""Data conversion utilities."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from balloon_analysis.utility import io

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #

DEFAULT_N_BINS = 8192
DEFAULT_BIN_OFFSET = 615
FALLBACK_BIN_WINDOW = (200, 1850)  # used when f_RX / bandwidth are unknown

_USB_NAMES = {"usb", "upper", "u"}
_LSB_NAMES = {"lsb", "lower", "l"}


# --------------------------------------------------------------------------- #
# Spectroscopy frequency conversion (currently unused)
# --------------------------------------------------------------------------- #

def _sideband_sign(sideband: str) -> int:
    sb = (sideband or "").strip().lower()
    if sb in _USB_NAMES:
        return +1
    if sb in _LSB_NAMES:
        return -1
    raise ValueError(f"Unknown sideband: {sideband!r} (expected 'USB' or 'LSB')")


def spectroscopy_convert(
    f_if: float | None = None,
    f_lo: float | None = None,
    f_sig: float | None = None,
    sideband: str = "USB",
    tol_ghz: float = 1e-6,
) -> dict[str, float]:
    """
    Given any two of (f_if, f_lo, f_sig) in GHz and the sideband, compute the
    third and return {'f_if', 'f_lo', 'f_sig'}.

    Conventions:
      USB: f_sig = f_lo + f_if
      LSB: f_sig = f_lo - f_if

    Raises ValueError if fewer than two inputs are given, or if all three are
    given but inconsistent (beyond `tol_ghz`).
    """
    sign = _sideband_sign(sideband)

    if sum(v is not None for v in (f_if, f_lo, f_sig)) < 2:
        raise ValueError("Need at least two of f_if, f_lo, f_sig to compute the third.")

    if f_if is None:
        f_if = sign * (f_sig - f_lo)
    elif f_lo is None:
        f_lo = f_sig - sign * f_if
    elif f_sig is None:
        f_sig = f_lo + sign * f_if
    else:
        expected_sig = f_lo + sign * f_if
        if abs(expected_sig - f_sig) > tol_ghz:
            raise ValueError(
                f"Inconsistent frequencies for sideband {sideband!r}: "
                f"expected f_sig={expected_sig:.9f} GHz but got f_sig={f_sig:.9f} GHz"
            )

    return {"f_if": float(f_if), "f_lo": float(f_lo), "f_sig": float(f_sig)}


# --------------------------------------------------------------------------- #
# Linear <-> log conversion (currently unused)
# --------------------------------------------------------------------------- #

def _db_factor(is_power: bool) -> float:
    return 10.0 if is_power else 20.0


def convert_array(arr, mode="dBm", reference=1e-3, is_power=True, eps=1e-15):
    """
    Convert a linear array to dB, dBm, or natural log.

    mode:      'dBm', 'dB', or 'log'
    reference: reference value for dBm (default 1 mW = 1e-3 W)
    is_power:  power (10*log10) vs amplitude (20*log10); ignored for 'dBm',
               which is always a power quantity
    eps:       floor applied to the input to avoid log(0)
    """
    arr = np.maximum(np.asarray(arr, dtype=float), eps)
    mode = mode.lower()

    if mode == "dbm":
        return 10.0 * np.log10(arr / reference)
    if mode == "db":
        return _db_factor(is_power) * np.log10(arr)
    if mode == "log":
        return np.log(arr)
    raise ValueError("Unsupported mode. Choose 'dBm', 'dB', or 'log'.")


def inverse_convert_array(arr, mode="dBm", reference=1e-3, is_power=True):
    """Inverse of `convert_array`: dBm / dB / natural log back to linear."""
    arr = np.asarray(arr, dtype=float)
    mode = mode.lower()

    if mode == "dbm":
        return reference * 10.0 ** (arr / 10.0)
    if mode == "db":
        return 10.0 ** (arr / _db_factor(is_power))
    if mode == "log":
        return np.exp(arr)
    raise ValueError("Unsupported mode. Choose 'dBm', 'dB', or 'log'.")


# --------------------------------------------------------------------------- #
# Frequency -> bin window
# --------------------------------------------------------------------------- #

def _frequency_offset_to_bin_index(
    freq_offset_ghz: float,
    bandwidth_ghz: float,
    n_bins: int = DEFAULT_N_BINS,
) -> int:
    """Convert a frequency offset (GHz) to a bin index, clamped to [0, n_bins-1].

    Assumes a linear mapping: bin i <-> offset (i / n_bins) * bandwidth_ghz.
    """
    if bandwidth_ghz <= 0 or n_bins <= 0:
        return 0
    idx = round(freq_offset_ghz / bandwidth_ghz * n_bins)
    return max(0, min(n_bins - 1, idx))


def compute_bin_window_from_center_freq(
    center_freq_ghz: float,
    f_rx_ghz: float | None,
    bandwidth_ghz: float | None,
    bin_offset: int = DEFAULT_BIN_OFFSET,
    n_bins: int = DEFAULT_N_BINS,
) -> tuple[int, int]:
    """Return (bin_start, bin_stop) of ±bin_offset around center_freq_ghz.

    Falls back to FALLBACK_BIN_WINDOW if f_rx_ghz or bandwidth_ghz is unusable.
    """
    if f_rx_ghz is None or bandwidth_ghz is None or bandwidth_ghz <= 0:
        return FALLBACK_BIN_WINDOW

    # Absolute offset gives a symmetric window regardless of sideband.
    offset_ghz = abs(center_freq_ghz - f_rx_ghz)
    center_bin = _frequency_offset_to_bin_index(offset_ghz, bandwidth_ghz, n_bins)

    return max(0, center_bin - bin_offset), min(n_bins - 1, center_bin + bin_offset)


# --------------------------------------------------------------------------- #
# Calibration (Y-factor)
# --------------------------------------------------------------------------- #

def compute_noise_temperature(
    avg_hot: np.ndarray,
    avg_cold: np.ndarray,
    t_hot_k: float,
    t_cold_k: float,
) -> np.ndarray:
    """Y-factor noise temperature; NaN where cold <= 0 or Y <= 1."""
    y = avg_hot / np.maximum(avg_cold, np.finfo(float).eps)
    valid = (avg_cold > 0) & (y > 1.0)

    t_noise = np.full_like(avg_hot, np.nan, dtype=float)
    t_noise[valid] = (float(t_hot_k) - y[valid] * float(t_cold_k)) / (y[valid] - 1.0)
    return t_noise


def compute_normalized_spectrum(avg_sig, avg_cold, avg_hot):
    """(sig - cold) / (hot - cold); inf/NaN where hot == cold."""
    with np.errstate(divide="ignore", invalid="ignore"):
        return (avg_sig - avg_cold) / (avg_hot - avg_cold)


def compute_brightness_temperature(avg_sig, avg_cold, avg_hot, t_cold_k, t_hot_k):
    # NOTE: argument order is (t_cold_k, t_hot_k), the reverse of
    # compute_noise_temperature(t_hot_k, t_cold_k). Kept for compatibility.
    normalized = compute_normalized_spectrum(avg_sig, avg_cold, avg_hot)
    return t_cold_k + (t_hot_k - t_cold_k) * normalized


# --------------------------------------------------------------------------- #
# Averaging of .spec files
# --------------------------------------------------------------------------- #

def _squared_counts(spectra: np.ndarray) -> np.ndarray:
    """All power calculations use squared counts."""
    return np.square(spectra.astype(float))


def accumulate_group_average(files: list[Path]) -> tuple[np.ndarray, int]:
    """Mean squared-count spectrum over all spectra in `files`, and their count."""
    sum_spectrum: np.ndarray | None = None
    total_n = 0

    for spec_path in files:
        _, spectra, _ = io.load_spec_file(spec_path)
        n_spectra, n_bins = spectra.shape

        if sum_spectrum is None:
            sum_spectrum = np.zeros(n_bins, dtype=float)
        elif n_bins != sum_spectrum.shape[0]:
            raise ValueError(
                f"Bin count mismatch between files; {spec_path} has {n_bins} bins, "
                f"expected {sum_spectrum.shape[0]}"
            )

        sum_spectrum += _squared_counts(spectra).sum(axis=0)
        total_n += n_spectra

    if sum_spectrum is None or total_n == 0:
        raise ValueError("No spectra found in provided file list.")

    return sum_spectrum / total_n, total_n


def file_mean_spectrum(spec_path: Path) -> np.ndarray:
    """Mean squared-count spectrum of a single .spec file."""
    _, spectra, _ = io.load_spec_file(spec_path)
    return _squared_counts(spectra).mean(axis=0)
