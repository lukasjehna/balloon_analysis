import sys
from pathlib import Path

import allantools
import matplotlib.pyplot as plt
import numpy as np

from balloon_analysis.utility import io_handlers
from balloon_analysis.utility.browser import select_file


def analyze_allan_time(
    spec_path: Path, 
    bin_index: int = 0, 
    plot_result: bool = True
) -> tuple[float, np.ndarray, np.ndarray, np.ndarray]:
    """
    Reads a .spec file, calculates the Overlapping Allan Deviation for a specific 
    frequency bin, and identifies the optimal integration time (Allan time).

    Args:
        spec_path: Path to the binary .spec file.
        bin_index: Index of the frequency bin to analyze (default is 0).
        plot_result: Whether to generate the log-log matplotlib plot.

    Returns:
        allan_time: The optimal integration time in seconds.
        taus: Array of integration times evaluated.
        adev: Array of Overlapping Allan Deviations.
        adev_err: 1-sigma confidence intervals for the deviation.
    """
    if not spec_path.is_file():
        raise FileNotFoundError(f"Hardware data file not found: {spec_path}")

    # Extract time vector, 2D spectra array (n_spectra, n_bins), and metadata
    times, spectra, meta = io_handlers.load_spec_file(spec_path)

    n_spectra = spectra.shape[0]
    if n_spectra < 3:
        raise ValueError("Insufficient spectra collected to compute Allan variance (minimum 3 required).")

    # Extract the 1D radiometric time series for the targeted frequency channel
    data_series = spectra[:, bin_index].astype(np.float64)

    # Derive sample rate strictly from hardware timestamps to account for UDP/I2C jitter
    # Fall back to metadata int_time_ms if timestamp array is corrupted
    dt_array = np.diff(times)
    if np.any(dt_array <= 0):
        print("Warning: Non-monotonic timestamps detected. Falling back to metadata integration time.", file=sys.stderr)
        tau0 = meta.get("int_time_ms", 1000.0) / 1000.0
    else:
        tau0 = float(np.mean(dt_array))
    
    sample_rate = 1.0 / tau0

    # Calculate Overlapping Allan Deviation
    taus, adev, adev_err, adev_n = allantools.oadev(
        data_series, 
        rate=sample_rate, 
        data_type="freq", 
        taus="all"
    )

    optimal_idx = np.argmin(adev)
    allan_time = taus[optimal_idx]
    min_adev = adev[optimal_idx]

    if plot_result:
        _plot_allan_deviation(taus, adev, adev_err, allan_time, min_adev, spec_path.name, bin_index)

    return allan_time, taus, adev, adev_err

def _plot_allan_deviation(
    taus: np.ndarray, 
    adev: np.ndarray, 
    adev_err: np.ndarray, 
    allan_time: float, 
    min_adev: float, 
    filename: str, 
    bin_index: int
) -> None:
    """Handles matplotlib rendering for the Allan deviation curve."""
    plt.figure(figsize=(10, 6))
    
    plt.errorbar(taus, adev, yerr=adev_err, fmt='o-', markersize=4, label='Overlapping ADEV', ecolor='gray', capsize=3)
    plt.plot(allan_time, min_adev, 'r*', markersize=12, label=f'Optimal Allan Time: {allan_time:.2f} s')
    
    plt.xscale('log')
    plt.yscale('log')
    plt.grid(True, which="both", ls="--", alpha=0.6)
    
    plt.title(f"Allan Deviation Analysis - {filename} (Bin {bin_index})")
    plt.xlabel(r"Integration Time $\tau$ (s)")
    plt.ylabel(r"Allan Deviation $\sigma_y(\tau)$ (Counts)")
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # Specify the default Windows-mapped DLR Data directory in WSL
    initial_dir = Path("/mnt/c/DLR/Data")
    
    # Prompt user for the target hardware data file
    target_file = select_file(initialdir=initial_dir, title="Select .spec hardware data file")
    
    if target_file is None:
        print("File selection cancelled. Exiting.", file=sys.stderr)
        sys.exit(0)
        
    print(f"Analyzing: {target_file}")
    try:
        optimal_tau, taus, adev, err = analyze_allan_time(target_file, bin_index=0)
        print(f"Analysis complete. Optimal Allan time: {optimal_tau:.2f} s")
    except Exception as e:
        print(f"Error during analysis: {e}", file=sys.stderr)
        sys.exit(1)