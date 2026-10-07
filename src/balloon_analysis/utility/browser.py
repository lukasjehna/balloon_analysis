#!/usr/bin/env python3
# interactive file browser
import tkinter as tk
from pathlib import Path
from tkinter import filedialog

import matplotlib.pyplot as plt
import numpy as np

from balloon_analysis.utility import conversion as conv
from balloon_analysis.utility import filter, io, plot


def select_folder(initialdir: Path | None = None) -> Path | None:
    root = tk.Tk()
    root.withdraw()

    path = filedialog.askdirectory(
        title="Select folder",
        initialdir=str(initialdir) if initialdir else None,
        mustexist=True,
    )

    root.destroy()
    return Path(path) if path else None






# def choose_directory(initialdir: Path) -> Path | None:
#     root = tk.Tk()
#     root.withdraw()
#     path = filedialog.askdirectory(
#         title="Select measurement folder (contains .spec + *_header.csv)",
#         initialdir=str(initialdir),
#     )
#     root.destroy()
#     return Path(path) if path else None


def resolve_measurement_dir_with_specs(meas_dir: Path) -> Path:
    if any(meas_dir.glob("*.spec")):
        return meas_dir
    subdirs = [d for d in meas_dir.iterdir() if d.is_dir()]
    candidates = [d for d in subdirs if any(d.glob("*.spec"))]
    if not candidates:
        return meas_dir
    chosen = max(candidates, key=lambda p: (p.name, p.stat().st_mtime))
    print(f"No .spec files in {meas_dir}; using subfolder {chosen}")
    return chosen



def plot_noise_temperature(
    meas_dir: Path,
    avg_hot: np.ndarray,
    avg_cold: np.ndarray,
    header_meta: dict[str, str],
    x_axis_mode: str = "frequency",
    y_min: float = 0.0,
    y_max: float = 30000.0,
    despike_enabled: bool = False,
) -> Path | None:
    t_hot_k, t_cold_k = io.extract_hot_cold_kelvin(header_meta)
    if t_hot_k is None or t_cold_k is None:
        print("Skipping noise-temperature plot: missing t_hot/t_cold in header.")
        return None

    t_noise =  conv.compute_noise_temperature(avg_hot, avg_cold, t_hot_k, t_cold_k)

    if despike_enabled:
        t_noise, _ = filter.despike_1d(t_noise)

    fig, ax = plt.subplots(figsize=(10, 5))
    x, x_label = plot.build_x_axis(t_noise.size, header_meta, x_axis_mode)
    ax.plot(x, t_noise, color="tab:green", linewidth=1.0)
    plot.apply_x_axis_format(ax, header_meta, x_axis_mode, x_label)
    ax.set_ylabel("Noise temperature [K]")
    ax.set_ylim(y_min, y_max)
    ax.grid(True, alpha=0.3)

    if np.any(np.isfinite(t_noise)):
        i_start = 200
        i_stop = 1851  # Python end index is exclusive, so 1851 includes bin 1850
        t_noise_window = t_noise[i_start:i_stop]

        mean_window = float(np.nanmean(t_noise_window)) if np.any(np.isfinite(t_noise_window)) else float("nan")

        ax.set_title(
            f" T_hot={t_hot_k:.2f} K, "
            f"T_cold={t_cold_k:.2f} K, mean(200..1850)={mean_window:.2f} K"
        )
    else:
        ax.set_title(f" T_hot={t_hot_k:.2f} K, T_cold={t_cold_k:.2f} K (no valid bins)")
    out_path = meas_dir / f"{meas_dir.name}_noise_temperature.png"
    fig.tight_layout()
    fig.savefig(out_path)
    return out_path