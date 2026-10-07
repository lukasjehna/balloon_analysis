#!/usr/bin/env python3
"""Interactive Y-factor noise-temperature browser for paired hot/cold .spec files.

This variant can:
- Average over a user-defined number of hot/cold pairs before computing spectra.
- Bin the x-axis by averaging over n adjacent spectral bins.


Files are recognised case-insensitively when their stem ends in ``hot`` or
``cold``. Each hot file is paired with the closest unused cold file in time;
the timestamp must occur at the beginning of the filename as YYYYMMDDHHMMSS,
e.g. 20260713160551hot.spec and 20260713160605cold.spec.
"""
#%%
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button, RadioButtons, TextBox

from balloon_analysis.utility import browser, io, plot
from balloon_analysis.utility import conversion as conv

#%%
STAMP_RE = re.compile(r"^(\d{14})")
LOAD_RE = re.compile(r"(hot|cold)$", re.IGNORECASE)


def parse_file(path: Path) -> tuple[datetime, str, Path] | None:
    match = STAMP_RE.match(path.stem)
    load = LOAD_RE.search(path.stem)
    if match is None or load is None:
        return None
    try:
        stamp = datetime.strptime(match.group(1), "%Y%m%d%H%M%S")
    except ValueError:
        return None
    return stamp, load.group(1).lower(), path


def find_pairs(directory: Path, recursive: bool, tolerance_s: float) -> list[tuple[Path, Path, float]]:
    pattern = "**/*.spec" if recursive else "*.spec"
    parsed = [item for p in directory.glob(pattern) if (item := parse_file(p))]
    hot = sorted((x for x in parsed if x[1] == "hot"), key=lambda x: x[0])
    cold = sorted((x for x in parsed if x[1] == "cold"), key=lambda x: x[0])
    unused = set(range(len(cold)))
    pairs = []
    for hot_time, _, hot_path in hot:
        candidates = [(abs((cold[i][0] - hot_time).total_seconds()), i) for i in unused]
        if not candidates:
            break
        delta_s, index = min(candidates)
        if delta_s <= tolerance_s:
            unused.remove(index)
            pairs.append((hot_path, cold[index][2], delta_s))
    return pairs


@dataclass
class AveragedPair:
    hot: Path
    cold: Path
    separation_s: float
    hot_avg: np.ndarray
    cold_avg: np.ndarray
    noise_temp: np.ndarray


def bin_spectrum_1d(y: np.ndarray, bin_size: int) -> np.ndarray:
    """Average adjacent samples in 1D array by bin_size.

    Truncates trailing samples that don't fill a complete bin.
    """
    n = len(y)
    if bin_size <= 1:
        return y.copy()
    m = n // bin_size
    trimmed = y[: m * bin_size]
    return trimmed.reshape(m, bin_size).mean(axis=1)


class SpecViewer:
    def __init__(self, pairs, header_meta, thot, tcold, x_axis, cache_size, pairs_per_average, spectral_bin_size, goto=1):
        if not pairs:
            raise ValueError("No valid hot/cold pairs.")
        self.pairs = pairs
        self.header_meta = header_meta
        self.thot = thot
        self.tcold = tcold
        self.x_axis = x_axis
        self.pairs_per_average = max(1, int(pairs_per_average))
        self.spectral_bin_size = max(1, int(spectral_bin_size))
        self.index = max(0, min(len(pairs) - 1, int(goto) - 1))
        self.hot_offset = 0.0
        self._load_cached = lru_cache(maxsize=cache_size)(self._load_uncached)
        self._limits_initialized = False
        self.calc_mode = "yfactor"  # or "diff"
        self.display_mode = "noise_temperature"
        self.fig, self.axes = plt.subplots(3, 1, figsize=(11, 9), sharex=True)
        self.fig.subplots_adjust(bottom=0.20, hspace=0.28)
        self.ax_nt, self.ax_hotcold, self.ax_diff = self.axes
        self.line_nt, = self.ax_nt.plot([], [], color="tab:green", lw=1.0)
        self.line_hot, = self.ax_hotcold.plot([], [], color="tab:red", lw=1.0, label="Hot")
        self.line_cold, = self.ax_hotcold.plot([], [], color="tab:blue", lw=1.0, label="Cold")
        self.y_factor, = self.ax_diff.plot([], [], color="tab:purple", lw=1.0)
        self.ax_nt.set_ylabel("Noise temperature [K]")
        self.ax_hotcold.set_ylabel("Counts [arb.]")
        self.ax_diff.set_ylabel("y-factor")
        self.ax_diff.set_xlabel("Bin index")
        for ax in self.axes:
            ax.grid(True, alpha=0.3)
        self.ax_hotcold.legend(loc="best")
        self._widgets()
        self.fig.canvas.mpl_connect("key_press_event", self._on_key)
        self.draw()

    def _load_uncached(self, hot_name, cold_name):
        hot = conv.file_mean_spectrum(Path(hot_name))
        cold = conv.file_mean_spectrum(Path(cold_name))
        if hot.size != cold.size:
            raise ValueError(f"Bin-count mismatch: hot={hot.size}, cold={cold.size}")
        tnoise = conv.compute_noise_temperature(hot, cold, self.thot, self.tcold)
        return hot, cold, tnoise

    def _set_hot_offset(self, text):
        try:
            self.hot_offset = float(str(text).strip())
        except ValueError:
            self.hot_offset_box.set_val(str(self.hot_offset))
            return

        self.draw()

    def _set_display_mode(self, label: str | None):
        if label is None:
            return

        mode_map = {
            "Noise temperature": "noise_temperature",
            "Brightness temperature": "brightness_temperature",
            "Normalized spectrum": "normalized_spectrum",
        }

        self.display_mode = mode_map[label]
        self.draw()


    def _widgets(self):
        # Existing buttons
        positions = (
            [0.12, 0.05, 0.06, 0.04],
            [0.20, 0.05, 0.06, 0.04],
        )

        self.prev, self.next = [
            Button(self.fig.add_axes(p), label)
            for p, label in zip(positions, ("<-", "->"))
        ]

        self.prev.on_clicked(lambda _e: self.step(-1))
        self.next.on_clicked(lambda _e: self.step(1))

        # Text boxes (create them first)
        self.pairs_box = TextBox(self.fig.add_axes([0.28, 0.05, 0.06, 0.04]), "")
        self.bin_box = TextBox(self.fig.add_axes([0.36, 0.05, 0.06, 0.04]), "")
        self.goto = TextBox(self.fig.add_axes([0.46, 0.05, 0.06, 0.04]), "")
        self.goto.set_val(str(self.index + 1))
        self.goto.on_submit(self._goto)
        self.hot_offset_box = TextBox(self.fig.add_axes([0.86, 0.05, 0.06, 0.04]), "")

        # Labels above boxes
        self.fig.text(0.30, 0.100, "Avg pairs", ha="center", va="center", fontsize=8)
        self.fig.text(0.38, 0.100, "Bin size", ha="center", va="center", fontsize=8)
        self.fig.text(0.47, 0.100, "Go to #", ha="center", va="center", fontsize=8)
        self.fig.text(0.89, 0.100, "Hot offset", ha="center", va="center", fontsize=8)

        # Set initial values
        self.pairs_box.set_val(str(self.pairs_per_average))
        self.bin_box.set_val(str(self.spectral_bin_size))
        self.hot_offset_box.set_val(str(self.hot_offset))

        # Attach callbacks
        self.pairs_box.on_submit(self._set_pairs_per_average)
        self.bin_box.on_submit(self._set_spectral_bin_size)
        self.goto.on_submit(self._goto)
        self.hot_offset_box.on_submit(self._set_hot_offset)

        # Bottom-plot mode: y-factor or hot-minus-cold
        ax_calc_mode = self.fig.add_axes([0.55, 0.05, 0.08, 0.08])
        self.radio_mode = RadioButtons(
            ax_calc_mode,
            ("yfactor", "diff"),
            active=0,
        )
        self.radio_mode.on_clicked(self._set_calc_mode)

        # Top-plot mode: noise temperature, brightness temperature, or normalized spectrum
        ax_display_mode = self.fig.add_axes([0.66, 0.05, 0.17, 0.12])
        self.radio_display_mode = RadioButtons(
            ax_display_mode,
            (
                "Noise temperature",
                "Brightness temperature",
                "Normalized spectrum",
            ),
            active=0,
        )
        self.radio_display_mode.on_clicked(self._set_display_mode)

        # Autoscale button
        ax_autoscale = self.fig.add_axes([0.12, 0.10, 0.07, 0.04])
        self.btn_autoscale = Button(ax_autoscale, "Autoscale")
        self.btn_autoscale.on_clicked(lambda _e: self.autoscale())
    
    def _set_calc_mode(self, label: str | None):
        if label is None:
            return
        if label not in ("yfactor", "diff"):
            return
        self.calc_mode = label
        self.draw()

    def autoscale(self):
        # Re-enable autoscaling
        for ax in self.axes:
            ax.set_autoscale_on(True)

        # Recompute limits from the current data
        for ax in self.axes:
            ax.relim()
            ax.autoscale_view()

        # Optionally disable autoscaling again if you want fixed limits afterwards:
        # for ax in self.axes:
        #     ax.set_autoscale_on(False)

        self.fig.canvas.draw_idle()

    def _set_pairs_per_average(self, text):
        try:
            value = max(1, int(str(text).strip()))
        except ValueError:
            self.pairs_box.set_val(str(self.pairs_per_average))
            return
        self.pairs_per_average = value
        self.draw()

    def _set_spectral_bin_size(self, text):
        try:
            value = max(1, int(str(text).strip()))
        except ValueError:
            self.bin_box.set_val(str(self.spectral_bin_size))
            return
        self.spectral_bin_size = value
        self.draw()

    def _goto(self, text):
        if not text or not text.strip():
            return
        try:
            self.jump(int(text.strip()) - 1)
        except ValueError:
            pass

    def step(self, amount):
        self.jump((self.index + amount) % len(self.pairs))

    def jump(self, index):
        self.index = max(0, min(len(self.pairs) - 1, index))
        self.draw()

    def _on_key(self, event):
        if event.key in ("left", "up"):
            self.step(-1)
        elif event.key in ("right", "down"):
            self.step(1)
        elif event.key == "home":
            self.jump(0)
        elif event.key == "end":
            self.jump(len(self.pairs) - 1)

    def _average_window(self, start_index: int) -> tuple[list[tuple[Path, Path, float]], np.ndarray, np.ndarray, np.ndarray]:
        group = self.pairs[start_index:start_index + self.pairs_per_average]
        hot_sum = None
        cold_sum = None
        noise_sum = None
        count = 0
        for hot, cold, _sep in group:
            hot_arr, cold_arr, tnoise = self._load_cached(str(hot), str(cold))
            if hot_sum is None:
                hot_sum = np.zeros_like(hot_arr, dtype=float)
                cold_sum = np.zeros_like(cold_arr, dtype=float)
                noise_sum = np.zeros_like(tnoise, dtype=float)
            if hot_arr.size != hot_sum.size or cold_arr.size != cold_sum.size:
                raise ValueError("Bin-count mismatch within averaging window.")
            hot_sum += hot_arr
            cold_sum += cold_arr
            noise_sum += tnoise
            count += 1
        if count == 0:
            raise ValueError("No pairs to average.")
        return group, hot_sum / count, cold_sum / count, noise_sum / count

    def draw(self):
        try:
            group, hot_arr, cold_arr, tnoise = self._average_window(self.index)
            separation = float(np.mean([sep for _h, _c, sep in group]))

            if self.spectral_bin_size > 1:
                hot_arr = bin_spectrum_1d(hot_arr, self.spectral_bin_size)
                cold_arr = bin_spectrum_1d(cold_arr, self.spectral_bin_size)
                tnoise = bin_spectrum_1d(tnoise, self.spectral_bin_size)

            x, xlabel = plot.build_x_axis(
                hot_arr.size,
                self.header_meta,
                self.x_axis,
            )
            i_offset = 548
            plot_hot = hot_arr + self.hot_offset
            if self.display_mode == "noise_temperature":
                top_data = tnoise
                top_ylabel = "Noise temperature [K]"

            elif self.display_mode == "brightness_temperature":
                top_data = conv.compute_brightness_temperature(
                    avg_sig=cold_arr,
                    avg_cold=hot_arr*cold_arr[i_offset]/hot_arr[i_offset],
                    avg_hot=hot_arr,
                    t_cold_k=self.tcold,
                    t_hot_k=self.thot,
                )
                top_ylabel = "Brightness temperature [K]"

            elif self.display_mode == "normalized_spectrum":
                top_data = conv.compute_normalized_spectrum(
                    avg_sig=cold_arr,
                    avg_cold=hot_arr*cold_arr[i_offset]/hot_arr[i_offset],
                    avg_hot=hot_arr,
                )
                top_ylabel = "Normalized spectrum"

            else:
                raise ValueError(f"Unknown display mode: {self.display_mode}")

            self.line_nt.set_data(x, top_data)
            self.line_hot.set_data(x, plot_hot)
            self.line_cold.set_data(x, cold_arr)
            self.ax_nt.set_ylabel(top_ylabel)

            # Choose calculation mode for bottom plot
            if self.calc_mode == "yfactor":
                y_data = hot_arr / np.maximum(cold_arr, np.finfo(float).eps)
                self.ax_diff.set_ylabel("y-factor")
            else:  # "diff"
                y_data = hot_arr - cold_arr
                self.ax_diff.set_ylabel("Hot − Cold")

            self.y_factor.set_data(x, y_data)

            # (rest of your axis limit / formatting code here)
            # ...

            plot.apply_x_axis_format(
                self.ax_diff,
                self.header_meta,
                self.x_axis,
                xlabel,
            )

            self.ax_nt.set_title(
                f"[{self.index + 1}/{len(self.pairs)}] pairs starting at "
                f"{group[0][0].name} | mean Δt={separation:.1f} s | "
                f"T_hot={self.thot:.0f} K,T_cold={self.tcold:.0f} K "
            )

        except Exception as exc:  # noqa: BLE001
            self.line_nt.set_data([], [])
            self.line_hot.set_data([], [])
            self.line_cold.set_data([], [])
            self.y_factor.set_data([], [])
            self.ax_nt.set_title(
                f"[{self.index + 1}/{len(self.pairs)}] ERROR: {exc}", color="tab:red"
            )
        finally:
            self.fig.canvas.draw_idle()


def main():
    parser = argparse.ArgumentParser(description="Browse Y-factor noise temperatures from hot/cold .spec pairs. Run with:  uv run src/balloon_analysis/hot_cold_folder_viewer.py --thot 300 --tcold 5 --pairs-per-average 50 --spectral-bin-size 3")
    parser.add_argument("directory", nargs="?", help="Measurement folder; omit to choose it graphically.")
    parser.add_argument("--thot", type=float, default=300, help="Hot-load temperature in K (default: 320).")
    parser.add_argument("--tcold", type=float, default=77, help="Cold-load temperature in K (default: 230).")
    parser.add_argument("--goto", type=int, default=1, help="Start at pair n (1-based, default: 1).")
    parser.add_argument("--x-axis", choices=("frequency", "bins", "sidebands"), default="frequency")
    parser.add_argument("--recursive", action="store_true", help="Search subdirectories too.")
    parser.add_argument("--pairs-per-average", type=int, default=1, help="Average over this many consecutive hot/cold pairs before plotting (default: 1).")
    parser.add_argument("--spectral-bin-size", type=int, default=1, help="Average over this many adjacent spectral bins on the x-axis (default: 1, no binning).")
    if any("ipykernel" in arg for arg in sys.argv):
        args, _ = parser.parse_known_args()
    else:
        args = parser.parse_args()

    default_folder = Path("/mnt/c/DLR/Data")
    directory = browser.select_folder(default_folder) if args.directory is None else Path(args.directory).expanduser().resolve()
    if directory is None:
        return
    if not directory.is_dir():
        parser.error(f"Not a directory: {directory}")

    pairs = find_pairs(directory, args.recursive, 60)
    if not pairs:
        parser.error("No timestamped hot/cold pairs found within the requested tolerance.")

    print(f"Found {len(pairs)} hot/cold pairs in {directory}")
    if args.pairs_per_average > 1:
        print(f"Averaging {args.pairs_per_average} pair(s)")
    if args.spectral_bin_size > 1:
        print(f"x-bin -axis over {args.spectral_bin_size} spectral bins.")

    SpecViewer(pairs, io.parse_header_csv(directory), args.thot, args.tcold, args.x_axis, 4096, args.pairs_per_average, args.spectral_bin_size, args.goto)
    plt.show()


if __name__ == "__main__":
    main()


# %%
