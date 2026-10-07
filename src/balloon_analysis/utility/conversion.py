#!/usr/bin/env python3
# data conversion utilities

from pathlib import Path

import numpy as np

from balloon_analysis.utility import io


# todo this is never used
def spectroscopy_convert(
    f_if: float | None = None,
    f_lo: float | None = None,
    f_sig: float | None = None,
    sideband: str = "USB",
) -> dict[str, float]:
    """
    Given any two of (f_if, f_lo, f_sig) in GHz and the sideband ("USB" or "LSB"),
    compute the third and return a dict {'f_if':..., 'f_lo':..., 'f_sig':...}.

    Conventions:
      USB: f_sig = f_lo + f_if
      LSB: f_sig = f_lo - f_if

    Raises ValueError if fewer than two inputs are provided or if all three are
    provided but inconsistent (within 1e-6 GHz).
    """
    sb = (sideband or "").strip().lower()
    if sb in ("usb", "upper", "u"):
        sign = +1
    elif sb in ("lsb", "lower", "l"):
        sign = -1
    else:
        raise ValueError(f"Unknown sideband: {sideband!r} (expected 'USB' or 'LSB')")

    provided = {"f_if": f_if, "f_lo": f_lo, "f_sig": f_sig}
    n_provided = sum(1 for v in provided.values() if v is not None)
    if n_provided < 2:
        raise ValueError("Need at least two of f_if, f_lo, f_sig to compute the third.")

    # Helper to compare floats
    def _close(a: float, b: float, tol: float = 1e-6) -> bool:
        return abs(a - b) <= tol

    # Compute missing value
    if f_if is None:
        # f_sig = f_lo + sign * f_if  => f_if = sign * (f_sig - f_lo)
        if f_lo is None or f_sig is None:
            raise ValueError("Unexpected missing values while computing f_if.")
        f_if = sign * (f_sig - f_lo)
    elif f_lo is None:
        # f_lo = f_sig - sign * f_if
        if f_if is None or f_sig is None:
            raise ValueError("Unexpected missing values while computing f_lo.")
        f_lo = f_sig - sign * f_if
    elif f_sig is None:
        # f_sig = f_lo + sign * f_if
        if f_if is None or f_lo is None:
            raise ValueError("Unexpected missing values while computing f_sig.")
        f_sig = f_lo + sign * f_if

    # If all three were provided originally, verify consistency
    if sum(1 for v in provided.values() if v is not None) == 3:
        expected_sig = f_lo + sign * f_if
        if not _close(expected_sig, f_sig):
            raise ValueError(
                f"Inconsistent frequencies for sideband {sideband!r}: "
                f"expected f_sig={expected_sig:.9f} GHz but got f_sig={f_sig:.9f} GHz"
            )

    return {"f_if": float(f_if), "f_lo": float(f_lo), "f_sig": float(f_sig)}




# created with chat gpt. Maybe can be used later.
def convert_array(arr, mode='dBm', reference=1e-3, is_power=True, eps=1e-15):
    """
    Converts a linear input array to log (dB) or dBm.
    
    Parameters:
    - arr: Input array (linear scale).
    - mode: 'dBm', 'dB', or 'log' (natural log).
    - reference: Reference value for dBm (default 1mW = 0.001W).
    - is_power: True if input is power, False if amplitude/voltage.
    - eps: Small value to prevent log(0) errors.
    """
    arr = np.asarray(arr, dtype=float)
    arr = np.maximum(arr, eps) # Avoid log of zero or negative numbers
    
    factor = 10.0 if is_power else 20.0
    
    if mode.lower() == 'dbm':
        # dBm is strictly power relative to 1mW
        return 10.0 * np.log10(arr / reference)
    elif mode.lower() == 'db':
        return factor * np.log10(arr)
    elif mode.lower() == 'log':
        return np.log(arr)
    else:
        raise ValueError("Unsupported mode. Choose 'dBm', 'dB', or 'log'.")

# created with chat gpt. Maybe can be used later.
def inverse_convert_array(arr, mode='dBm', reference=1e-3, is_power=True):
    """
    Converts a log, dB, or dBm input array back to the linear scale.
    
    Parameters:
    - arr: Input array (dBm, dB, or log scale).
    - mode: 'dBm', 'dB', or 'log' (natural log).
    - reference: Reference value used during conversion.
    - is_power: True if original scale was power, False if amplitude/voltage.
    """
    arr = np.asarray(arr, dtype=float)
    factor = 10.0 if is_power else 20.0
    
    if mode.lower() == 'dbm':
        return reference * (10.0 ** (arr / 10.0))
    elif mode.lower() == 'db':
        return 10.0 ** (arr / factor)
    elif mode.lower() == 'log':
        return np.exp(arr)
    else:
        raise ValueError("Unsupported mode. Choose 'dBm', 'dB', or 'log'.")



def _frequency_offset_to_bin_index(
    freq_offset_ghz: float,
    bandwidth_ghz: float,
    n_bins: int = 8192,
) -> int:
    """Convert frequency offset (in GHz) to bin index.

    Assumes linear mapping: bin i corresponds to freq_offset = (i / n_bins) * bandwidth_ghz
    """
    if bandwidth_ghz <= 0 or n_bins <= 0:
        return 0
    bin_idx = round((freq_offset_ghz / bandwidth_ghz) * n_bins)
    return max(0, min(n_bins - 1, bin_idx))


def compute_bin_window_from_center_freq(
    center_freq_ghz: float,
    f_rx_ghz: float | None,
    bandwidth_ghz: float | None,
    bin_offset: int = 615,
    n_bins: int = 8192,
) -> tuple[int, int]:
    """Compute bin_start and bin_stop centered on center_freq_ghz.

    If f_rx_ghz and bandwidth_ghz are available, compute the absolute offset frequency
    and convert to bin index. Then apply ±bin_offset. Clamp to [0, n_bins-1].
    """
    if f_rx_ghz is None or bandwidth_ghz is None or bandwidth_ghz <= 0:
        # Fallback: use fixed defaults
        return 200, 1850

    # Frequency offset from f_RX to center_freq (use absolute value for symmetric bin window)
    freq_offset_ghz = abs(center_freq_ghz - f_rx_ghz)
    center_bin = _frequency_offset_to_bin_index(freq_offset_ghz, bandwidth_ghz, n_bins)

    bin_start = max(0, center_bin - bin_offset)
    bin_stop = min(n_bins - 1, center_bin + bin_offset)

    return bin_start, bin_stop


def compute_noise_temperature(avg_hot: np.ndarray, avg_cold: np.ndarray, t_hot_k: float, t_cold_k: float) -> np.ndarray:
    eps = np.finfo(float).eps
    y = avg_hot / np.maximum(avg_cold, eps)
    t_noise = np.full_like(avg_hot, np.nan, dtype=float)
    valid = (avg_cold > 0) & (y > 1.0)
    t_noise[valid] = (float(t_hot_k) - y[valid] * float(t_cold_k)) / (y[valid] - 1.0)
    return t_noise


def compute_normalized_spectrum(avg_sig, avg_cold, avg_hot):
    denominator = avg_hot - avg_cold

    with np.errstate(divide="ignore", invalid="ignore"):
        normalized_spectrum = (avg_sig - avg_cold) / denominator

    return normalized_spectrum


def compute_brightness_temperature(avg_sig, avg_cold, avg_hot, t_cold_k, t_hot_k):
    normalized_spectrum = compute_normalized_spectrum(
        avg_sig=avg_sig,
        avg_cold=avg_cold,
        avg_hot=avg_hot,
    )

    return t_cold_k + (t_hot_k - t_cold_k) * normalized_spectrum




def accumulate_group_average(files: list[Path]) -> tuple[np.ndarray, int]:
    sum_spectrum: np.ndarray | None = None
    total_n = 0

    for spec_path in files:
        _, spectra, _ = io.load_spec_file(spec_path)
        n_spectra, n_bins = spectra.shape

        if sum_spectrum is None:
            sum_spectrum = np.zeros(n_bins, dtype=float)
        elif sum_spectrum.shape[0] != n_bins:
            raise ValueError(
                f"Bin count mismatch between files; {spec_path} has {n_bins} bins, expected {sum_spectrum.shape[0]}"
            )

        # Use squared counts for all calculations
        spec_sq = spectra.astype(float) ** 2
        sum_spectrum += spec_sq.sum(axis=0)
        total_n += n_spectra

    if sum_spectrum is None or total_n == 0:
        raise ValueError("No spectra found in provided file list.")

    return sum_spectrum / total_n, total_n


def file_mean_spectrum(spec_path: Path) -> np.ndarray:
    _, spectra, _ = io.load_spec_file(spec_path)
    # Return mean of squared counts
    return (spectra.astype(float) ** 2).mean(axis=0).astype(float)