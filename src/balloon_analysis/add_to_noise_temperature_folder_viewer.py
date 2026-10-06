#!/usr/bin/env python3
"""Interactive browser for paired hot/cold .spec files."""
from __future__ import annotations

import argparse
import re
from datetime import datetime
from functools import lru_cache
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button, RadioButtons, TextBox

import balloon_analysis.spec_analysis_utils as sau

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


def find_pairs(directory: Path, recursive: bool, tolerance_s: float):
    pattern = "**/*.spec" if recursive else "*.spec"
    parsed = [item for p in directory.glob(pattern) if (item := parse_file(p))]
    hot = sorted((x for x in parsed if x[1] == "hot"), key=lambda x: x[0])
    cold = sorted((x for x in parsed if x[1] == "cold"), key=lambda x: x[0])
    unused = set(range(len(cold)))
    pairs = []
    for hot_time, _, hot_path in hot:
        candidates = [
            (abs((cold[i][0] - hot_time).total_seconds()), i)
            for i in unused
        ]
        if not candidates:
            break
        delta_s, index = min(candidates)
        if delta_s <= tolerance_s:
            unused.remove(index)
            pairs.append((hot_path, cold[index][2], delta_s))
    return pairs


def bin_spectrum_1d(y: np.ndarray, bin_size: int) -> np.ndarray:
    if bin_size <= 1:
        return y.copy()
    n_bins = len(y) // bin_size
    return y[: n_bins * bin_size].reshape(n_bins, bin_size).mean(axis=1)


class NoiseTemperatureViewer:
    MODES = (
        "noise temperature",
        "normalized spectrum",
        "brightness temperature",
    )

    def __init__(
        self,
        pairs,
        header_meta,
        thot,
        tcold,
        x_axis,
        cache_size,
        pairs_per_average,
        spectral_bin_size,
        offset,
    ):
        if not pairs:
            raise ValueError("No valid hot/cold pairs.")
        self.pairs = pairs
        self.header_meta = header_meta
        self.thot = float(thot)
        self.tcold = float(tcold)
        self.x_axis = x_axis
        self.pairs_per_average = max(1, int(pairs_per_average))
        self.spectral_bin_size = max(1, int(spectral_bin_size))
        self.offset = float(offset)
        self.index = 0
        self.calc_mode = self.MODES[0]
        self._load_cached = lru_cache(maxsize=cache_size)(self._load_uncached)

        self.fig, self.axes = plt.subplots(3, 1, figsize=(11, 9), sharex=True)
        self.fig.subplots_adjust(bottom=0.27, hspace=0.30)
        self.ax_result, self.ax_hotcold, self.ax_aux = self.axes

        self.line_result, = self.ax_result.plot([], [], color="tab:green", lw=1.0)
        self.line_hot, = self.ax_hotcold.plot([], [], color="tab:red", lw=1.0, label="Hot")
        self.line_cold, = self.ax_hotcold.plot([], [], color="tab:blue", lw=1.0, label="Cold")
        self.line_aux, = self.ax_aux.plot([], [], color="tab:purple", lw=1.0)

        self.ax_hotcold.set_ylabel("Counts [arb.]")
        self.ax_hotcold.legend(loc="best")
        for ax in self.axes:
            ax.grid(True, alpha=0.3)

        self._widgets()
        self.fig.canvas.mpl_connect("key_press_event", self._on_key)
        self.draw()

    def _load_uncached(self, hot_name, cold_name):
        hot = sau.file_mean_spectrum(Path(hot_name))
        cold = sau.file_mean_spectrum(Path(cold_name))
        if hot.size != cold.size:
            raise ValueError(f"Bin-count mismatch: hot={hot.size}, cold={cold.size}")
        return hot, cold

    def _widgets(self):
        self.prev = Button(self.fig.add_axes([0.08, 0.06, 0.06, 0.04]), "<-")
        self.next = Button(self.fig.add_axes([0.15, 0.06, 0.06, 0.04]), "->")
        self.prev.on_clicked(lambda _event: self.step(-1))
        self.next.on_clicked(lambda _event: self.step(1))

        self.pairs_box = TextBox(self.fig.add_axes([0.25, 0.06, 0.06, 0.04]), "")
        self.bin_box = TextBox(self.fig.add_axes([0.33, 0.06, 0.06, 0.04]), "")
        self.goto = TextBox(self.fig.add_axes([0.41, 0.06, 0.06, 0.04]), "")
        self.offset_box = TextBox(self.fig.add_axes([0.49, 0.06, 0.06, 0.04]), "")

        self.fig.text(0.28, 0.115, "Avg pairs", ha="center", fontsize=8)
        self.fig.text(0.36, 0.115, "Bin size", ha="center", fontsize=8)
        self.fig.text(0.44, 0.115, "Go to #", ha="center", fontsize=8)
        self.fig.text(0.52, 0.115, "Offset", ha="center", fontsize=8)

        self.pairs_box.set_val(str(self.pairs_per_average))
        self.bin_box.set_val(str(self.spectral_bin_size))
        self.offset_box.set_val(str(self.offset))
        self.pairs_box.on_submit(self._set_pairs_per_average)
        self.bin_box.on_submit(self._set_spectral_bin_size)
        self.offset_box.on_submit(self._set_offset)
        self.goto.on_submit(self._goto)

        ax_mode = self.fig.add_axes([0.60, 0.035, 0.22, 0.15])
        self.radio_mode = RadioButtons(ax_mode, self.MODES, active=0)
        self.radio_mode.on_clicked(self._set_calc_mode)

        ax_autoscale = self.fig.add_axes([0.08, 0.12, 0.09, 0.04])
        self.btn_autoscale = Button(ax_autoscale, "Autoscale")
        self.btn_autoscale.on_clicked(lambda _event: self.autoscale())

    def _set_calc_mode(self, label):
        if label in self.MODES:
            self.calc_mode = label
            self.draw()

    def _set_pairs_per_average(self, text):
        try:
            self.pairs_per_average = max(1, int(text.strip()))
        except ValueError:
            self.pairs_box.set_val(str(self.pairs_per_average))
            return
        self.draw()

    def _set_spectral_bin_size(self, text):
        try:
            self.spectral_bin_size = max(1, int(text.strip()))
        except ValueError:
            self.bin_box.set_val(str(self.spectral_bin_size))
            return
        self.draw()

    def _set_offset(self, text):
        try:
            self.offset = float(text.strip())
        except ValueError:
            self.offset_box.set_val(str(self.offset))
            return
        self.draw()

    def _goto(self, text):
        try:
            self.jump(int(text.strip()) - 1)
        except ValueError:
            pass

    def autoscale(self):
        for ax in self.axes:
            ax.set_autoscale_on(True)
            ax.relim()
            ax.autoscale_view()
        self.fig.canvas.draw_idle()

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

    def _average_window(self):
        group = self.pairs[self.index:self.index + self.pairs_per_average]
        hot_sum = cold_sum = None
        for hot_path, cold_path, _sep in group:
            hot, cold = self._load_cached(str(hot_path), str(cold_path))
            if hot_sum is None:
                hot_sum = np.zeros_like(hot, dtype=float)
                cold_sum = np.zeros_like(cold, dtype=float)
            if hot.size != hot_sum.size or cold.size != cold_sum.size:
                raise ValueError("Bin-count mismatch within averaging window.")
            hot_sum += hot
            cold_sum += cold
        if not group:
            raise ValueError("No pairs to average.")
        count = len(group)
        return group, hot_sum / count, cold_sum / count

    def _calculate(self, avg_hot, avg_cold):
        # For the two signal modes, apply the requested relation:
        # avg_sig = avg_cold and avg_cold = avg_hot + offset.
        if self.calc_mode == "noise temperature":
            result = sau.compute_noise_temperature(
                avg_hot, avg_cold, self.thot, self.tcold
            )
            return result, "Noise temperature [K]"

        avg_sig = avg_cold
        avg_cold_for_signal = avg_hot + self.offset
        if self.calc_mode == "normalized spectrum":
            result = sau.compute_normalized_spectrum(
                avg_sig=avg_sig,
                avg_cold=avg_cold_for_signal,
                avg_hot=avg_hot,
            )
            return result, "Normalized spectrum"

        result = sau.compute_brightness_temperature(
            avg_sig=avg_sig,
            avg_cold=avg_cold_for_signal,
            avg_hot=avg_hot,
            t_cold_k=self.tcold,
            t_hot_k=self.thot,
        )
        return result, "Brightness temperature [K]"

    def draw(self):
        try:
            group, avg_hot, avg_cold, = self._average_window()
            result, result_ylabel = self._calculate(avg_hot, avg_cold)

            hot_plot = avg_hot
            cold_plot = avg_cold
            result_plot = result
            if self.spectral_bin_size > 1:
                hot_plot = bin_spectrum_1d(hot_plot, self.spectral_bin_size)
                cold_plot = bin_spectrum_1d(cold_plot, self.spectral_bin_size)
                result_plot = bin_spectrum_1d(result_plot, self.spectral_bin_size)

            x, xlabel = sau.build_x_axis(result_plot.size, self.header_meta, self.x_axis)
            self.line_result.set_data(x, result_plot)
            self.line_hot.set_data(x, hot_plot)
            self.line_cold.set_data(x, cold_plot)

            with np.errstate(divide="ignore", invalid="ignore"):
                y_factor = hot_plot / cold_plot
            self.line_aux.set_data(x, y_factor)

            self.ax_result.set_ylabel(result_ylabel)
            self.ax_aux.set_ylabel("Y-factor")
            sau._apply_x_axis_format(self.ax_aux, self.header_meta, self.x_axis, xlabel)
            self.ax_result.set_title(
                f"[{self.index + 1}/{len(self.pairs)}] {self.calc_mode} | "
                f"{group[0][0].name} | T_hot={self.thot:.2f} K, "
                f"T_cold={self.tcold:.2f} K | offset={self.offset:g}"
            )
            self.autoscale()
        except Exception as exc:  # noqa: BLE001
            for line in (self.line_result, self.line_hot, self.line_cold, self.line_aux):
                line.set_data([], [])
            self.ax_result.set_title(f"[{self.index + 1}/{len(self.pairs)}] ERROR: {exc}", color="tab:red")
        finally:
            self.fig.canvas.draw_idle()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", nargs="?")
    parser.add_argument("--thot", type=float, default=300.0)
    parser.add_argument("--tcold", type=float, default=5.0)
    parser.add_argument("--offset", type=float, default=0.0)
    parser.add_argument("--x-axis", choices=("frequency", "bins", "sidebands"), default="frequency")
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--pairs-per-average", type=int, default=1)
    parser.add_argument("--spectral-bin-size", type=int, default=1)
    args = parser.parse_args()

    default_folder = Path("/mnt/c/DLR/Data")
    directory = sau.choose_directory(default_folder) if args.directory is None else Path(args.directory).expanduser().resolve()
    if directory is None:
        return
    if not directory.is_dir():
        parser.error(f"Not a directory: {directory}")

    pairs = find_pairs(directory, args.recursive, 60.0)
    if not pairs:
        parser.error("No timestamped hot/cold pairs found within the requested tolerance.")

    NoiseTemperatureViewer(
        pairs=pairs,
        header_meta=sau.parse_header_csv(directory),
        thot=args.thot,
        tcold=args.tcold,
        x_axis=args.x_axis,
        cache_size=4096,
        pairs_per_average=args.pairs_per_average,
        spectral_bin_size=args.spectral_bin_size,
        offset=args.offset,
    )
    plt.show()


if __name__ == "__main__":
    main()
