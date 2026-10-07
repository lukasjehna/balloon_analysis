#!/usr/bin/env python3
# static plots

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from balloon_analysis.utility import conversion as conv
from balloon_analysis.utility import filter, io


def build_x_axis(n_bins: int, header_meta: dict[str, str], x_axis_mode: str) -> tuple[np.ndarray, str]:
    if x_axis_mode == "bins":
        return np.arange(n_bins), "Bin index"

    bw_ghz = io.get_bw_ghz(header_meta)
    if bw_ghz is None or bw_ghz <= 0:
        return np.arange(n_bins), "Bin index"

    x_if = np.linspace(0.0, bw_ghz, n_bins, endpoint=False)
    return x_if, "f_IF [GHz]"


def apply_x_axis_format(
    ax: plt.Axes,
    header_meta: dict[str, str],
    x_axis_mode: str,
    default_label: str,
) -> None:
    if x_axis_mode == "bins" or default_label == "Bin index":
        ax.set_xlabel("Bin index")
        return

    f_lo_ghz = io.get_lo_ghz(header_meta)
    if x_axis_mode == "frequency":
        ax.set_xlabel("f_IF [GHz]" if f_lo_ghz is None else f"f_IF [GHz] (f_LO={f_lo_ghz:.6f} GHz)")
        return

    if x_axis_mode == "sidebands":
        if f_lo_ghz is None:
            ax.set_xlabel("f_IF [GHz] (f_LO missing)")
            return

        ticks_if = ax.get_xticks()
        ax.set_xticks(ticks_if)
        ax.set_xticklabels([f"{(f_lo_ghz + t):.3f}" for t in ticks_if])
        ax.set_xlabel("f_USB [GHz]")

        ax_top = ax.twiny()
        ax_top.set_xlim(ax.get_xlim())
        ax_top.set_xticks(ticks_if)
        ax_top.set_xticklabels([f"{(f_lo_ghz - t):.3f}" for t in ticks_if])
        ax_top.set_xlabel("f_LSB [GHz]")



def plot_hot_cold_average(
    meas_dir: Path,
    avg_hot: np.ndarray,
    n_hot: int,
    avg_cold: np.ndarray,
    n_cold: int,
    header_meta: dict[str, str],
    x_axis_mode: str = "frequency",
) -> Path:
    x, x_label = build_x_axis(avg_hot.size, header_meta, x_axis_mode)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(x, avg_hot, label=f"hot (N={n_hot})", color="tab:red")
    ax.plot(x, avg_cold, label=f"cold (N={n_cold})", color="tab:blue")
    apply_x_axis_format(ax, header_meta, x_axis_mode, x_label)
    ax.set_ylabel("Counts [arb.]")
    ax.grid(True, alpha=0.3)

    f_lo = io.get_header_value(header_meta, "f_LO", "f_RX")
    bw = io.get_header_value(header_meta, "BW", "bandwidth")
    t_hot = header_meta.get("t_hot")
    t_cold = header_meta.get("t_cold")

    title_parts: list[str] = []
    if f_lo:
        title_parts.append(f"f_LO={f_lo}")
    if bw:
        title_parts.append(f"BW={bw}")
    if t_hot and t_cold:
        title_parts.append(f"T_hot={t_hot}, T_cold={t_cold}")
    ax.set_title("Hot vs cold average | " + " | ".join(title_parts) if title_parts else "Hot vs cold average spectra")

    ax.legend(loc="best")
    out_path = meas_dir / f"{meas_dir.name}_hot_cold_avg.png"
    fig.tight_layout()
    fig.savefig(out_path)
    return out_path


def plot_all_hot_cold_lines(
    meas_dir: Path,
    hot_files: list[Path],
    cold_files: list[Path],
    header_meta: dict[str, str],
    x_axis_mode: str = "frequency",
) -> Path:
    fig, ax = plt.subplots(figsize=(10, 5))
    x_label = "Bin index"

    total_hot_spectra = 0
    for spec_path in hot_files:
        _, spectra, _ = io.load_spec_file(spec_path)
        n_spectra, n_bins = spectra.shape
        x, x_label = build_x_axis(n_bins, header_meta, x_axis_mode)
        for i in range(n_spectra):
            ax.plot(
                x, (spectra[i, :].astype(float) ** 2), color="tab:red", alpha=0.15, linewidth=0.5,
                label="hot spectra" if total_hot_spectra == 0 else None
            )
            total_hot_spectra += 1

    total_cold_spectra = 0
    for spec_path in cold_files:
        _, spectra, _ = io.load_spec_file(spec_path)
        n_spectra, n_bins = spectra.shape
        x, x_label = build_x_axis(n_bins, header_meta, x_axis_mode)
        for i in range(n_spectra):
            ax.plot(
                x, (spectra[i, :].astype(float) ** 2), color="tab:blue", alpha=0.15, linewidth=0.5,
                label="cold spectra" if total_cold_spectra == 0 else None
            )
            total_cold_spectra += 1

    apply_x_axis_format(ax, header_meta, x_axis_mode, x_label)
    ax.set_ylabel("Counts [arb.]")
    ax.grid(True, alpha=0.3)

    f_lo = io.get_header_value(header_meta, "f_LO", "f_RX")
    bw = io.get_header_value(header_meta, "BW", "bandwidth")
    title_parts: list[str] = []
    if f_lo:
        title_parts.append(f"f_LO={f_lo}")
    if bw:
        title_parts.append(f"BW={bw}")
    ax.set_title("All hot/cold spectra | " + " | ".join(title_parts) if title_parts else "All hot/cold spectra (all frames)")

    ax.legend(loc="best")
    out_path = meas_dir / f"{meas_dir.name}_hot_cold_lines.png"
    fig.tight_layout()
    fig.savefig(out_path)
    return out_path



def add_relative_frequency_top_axis(
    ax: plt.Axes,
    center_freq_ghz: float,
    label: str = "f_RX - f_center [GHz]",
    decimals: int = 3,
) -> plt.Axes:
    ticks = ax.get_xticks()
    ax_top = ax.twiny()
    ax_top.set_xlim(ax.get_xlim())
    ax_top.set_xticks(ticks)
    d = max(0, int(decimals))
    fmt = f"{{:.{d}f}}"
    ax_top.set_xticklabels([fmt.format(t - center_freq_ghz) for t in ticks])
    ax_top.set_xlabel(label)
    return ax_top


def launch_interactive_noise_temperature_browser(
    entries: list[dict[str, object]],
    bin_start: int = 200,
    bin_stop: int = 1850,
    despike_enabled: bool = False,
    despike_window: int = 5,
    despike_sigma: float = 6.0,
    center_freq_ghz: float | None = None,
) -> plt.Figure | None:
    if not entries:
        return None

    from matplotlib.widgets import Button, Slider

    fig, ax = plt.subplots(figsize=(11, 5))
    plt.subplots_adjust(bottom=0.30 if despike_enabled else 0.18)

    (line,) = ax.plot([], [], color="tab:green", linewidth=1.0)
    span = ax.axvspan(0, 0, color="tab:gray", alpha=0.12, lw=0)
    ax.set_ylabel("Noise temperature [K]")
    ax.grid(True, alpha=0.3)

    ax_top = ax.twiny()
    ax_top.set_xlim(ax.get_xlim())
    ax_top.set_xlabel("Bin index")

    state = {
        "idx": 0,
        "dsp_window": max(3, int(despike_window) | 1),
        "dsp_sigma": max(0.1, float(despike_sigma)),
    }

    slider_w = None
    slider_s = None

    if despike_enabled:
        ax_w = fig.add_axes([0.10, 0.09, 0.50, 0.03])
        ax_s = fig.add_axes([0.10, 0.04, 0.50, 0.03])
        slider_w = Slider(ax_w, "despike window", 3, 51, valinit=state["dsp_window"], valstep=1)
        slider_s = Slider(ax_s, "despike sigma", 0.5, 20.0, valinit=state["dsp_sigma"])

    def _get_bin_window_for_entry(e: dict[str, object]) -> tuple[int, int]:
        """Get bin_start and bin_stop for current entry, using per-entry values or defaults."""
        if "bin_start" in e and "bin_stop" in e:
            return int(e["bin_start"]), int(e["bin_stop"])
        return bin_start, bin_stop

    def _compute_t_noise_for_entry(e: dict[str, object]) -> tuple[np.ndarray, int]:
        entry_bin_start, entry_bin_stop = _get_bin_window_for_entry(e)

        # Backward-compatible path: precomputed t_noise only
        if "avg_hot" not in e or "avg_cold" not in e:
            y_pre = np.asarray(e.get("t_noise", []), dtype=float)
            if despike_enabled:
                y_pre, removed = filter.despike_1d_in_window(
                    y_pre,
                    bin_start=entry_bin_start,
                    bin_stop=entry_bin_stop,
                    window=state["dsp_window"],
                    sigma_thresh=state["dsp_sigma"],
                )
                return y_pre, int(removed)
            return y_pre, int(e.get("removed_spikes", 0))

        hot = np.asarray(e["avg_hot"], dtype=float)
        cold = np.asarray(e["avg_cold"], dtype=float)
        if hot.size == 0 or cold.size != hot.size:
            return np.full_like(hot, np.nan, dtype=float), 0

        removed = 0
        if despike_enabled:
            hot, r_h = filter.despike_1d_in_window(
                hot,
                bin_start=entry_bin_start,
                bin_stop=entry_bin_stop,
                window=state["dsp_window"],
                sigma_thresh=state["dsp_sigma"],
            )
            cold, r_c = filter.despike_1d_in_window(
                cold,
                bin_start=entry_bin_start,
                bin_stop=entry_bin_stop,
                window=state["dsp_window"],
                sigma_thresh=state["dsp_sigma"],
            )
            removed = int(r_h + r_c)

        t_hot_k = e.get("t_hot_k")
        t_cold_k = e.get("t_cold_k")
        if (t_hot_k is None or t_cold_k is None) and isinstance(e.get("header_meta"), dict):
            h = e["header_meta"]
            t_hot_k, t_cold_k = io.extract_hot_cold_kelvin(h)

        if t_hot_k is None or t_cold_k is None:
            return np.full_like(hot, np.nan, dtype=float), removed

        t_noise = conv.compute_noise_temperature(hot, cold, float(t_hot_k), float(t_cold_k))
        return t_noise, removed


    def _get_x_axis_for_entry(e: dict[str, object], n_bins: int) -> tuple[np.ndarray, str]:
        header_meta = e.get("header_meta")
        if isinstance(header_meta, dict):
            x_if, lbl = build_x_axis(n_bins, header_meta, x_axis_mode="frequency")
            x_if = np.asarray(x_if, dtype=float)
            if x_if.size == n_bins and np.all(np.isfinite(x_if)) and lbl != "Bin index":
                return x_if, "f_IF [GHz]"
        return np.arange(n_bins, dtype=float), "Bin index"

    def _update_top_bin_axis(x: np.ndarray) -> None:
        ticks = ax.get_xticks()
        ax_top.set_xlim(ax.get_xlim())
        ax_top.set_xticks(ticks)

        if x.size <= 1:
            ax_top.set_xticklabels(["0"] * len(ticks))
            return

        if np.allclose(x, np.arange(x.size, dtype=float)):
            bin_vals = np.rint(ticks).astype(int)
        else:
            step = (x[-1] - x[0]) / max(1, x.size - 1)
            bin_vals = np.rint((ticks - x[0]) / step).astype(int) if step != 0 else np.zeros_like(ticks, dtype=int)

        bin_vals = np.clip(bin_vals, 0, x.size - 1)
        ax_top.set_xticklabels([str(int(v)) for v in bin_vals])

    def _draw() -> None:
        e = entries[state["idx"]]
        entry_bin_start, entry_bin_stop = _get_bin_window_for_entry(e)
        y, removed_spikes = _compute_t_noise_for_entry(e)
        x, x_label = _get_x_axis_for_entry(e, y.size)

        line.set_data(x, y)
        ax.set_xlim((0, 0.8) if x.size > 1 else (0, 2))
        ax.set_xlabel(x_label)
        ax.set_ylim(3000.0, 35000)

        i0 = max(0, int(entry_bin_start))
        i1 = min(y.size, int(entry_bin_stop) + 1)
        w = y[i0:i1]
        mean_w = float(np.nanmean(w)) if np.any(np.isfinite(w)) else float("nan")

        if x.size > 0:
            l_idx = max(0, min(y.size - 1, i0))
            r_idx = max(0, min(y.size - 1, max(i0, i1 - 1)))
            x_l = float(x[l_idx]); x_r = float(x[r_idx])
            if x_r <= x_l and y.size > 1:
                step = float((x[-1] - x[0]) / max(1, y.size - 1))
                x_r = x_l + abs(step)
            span.set_x(x_l)
            span.set_width(max(0.0, x_r - x_l))

        _update_top_bin_axis(x)

        spikes_txt = ""
        if despike_enabled:
            spikes_txt = (
                f", removed spikes={removed_spikes}, "
                f"w={state['dsp_window']}, sigma={state['dsp_sigma']:.2f}"
            )

        ax.set_title(
            f"{e.get('name', '<unknown>')} | f_RX={float(e.get('f_rx_ghz', float('nan'))):.3f} GHz | "
            f"T_hot={float(e.get('t_hot_k', float('nan'))):.2f} K, "
            f"T_cold={float(e.get('t_cold_k', float('nan'))):.2f} K, "
            f"mean({entry_bin_start}..{entry_bin_stop})={mean_w:.2f} K{spikes_txt}"
        )
        fig.canvas.draw_idle()

    def _step(delta: int) -> None:
        state["idx"] = (state["idx"] + delta) % len(entries)
        _draw()

    def _on_slider(_val) -> None:
        if slider_w is not None:
            w = round(slider_w.val)
            w = max(w, 3)
            if w % 2 == 0:
                w += 1
            state["dsp_window"] = w
        if slider_s is not None:
            state["dsp_sigma"] = max(0.1, float(slider_s.val))
        _draw()

    ax_prev = fig.add_axes([0.76, 0.02, 0.10, 0.07])
    ax_next = fig.add_axes([0.87, 0.02, 0.10, 0.07])
    btn_prev = Button(ax_prev, "Prev")
    btn_next = Button(ax_next, "Next")
    btn_prev.on_clicked(lambda _evt: _step(-1))
    btn_next.on_clicked(lambda _evt: _step(+1))

    if slider_w is not None:
        slider_w.on_changed(_on_slider)
    if slider_s is not None:
        slider_s.on_changed(_on_slider)

    def _on_key(evt) -> None:
        if evt.key in ("left", "up"):
            _step(-1)
        elif evt.key in ("right", "down"):
            _step(+1)

    fig.canvas.mpl_connect("key_press_event", _on_key)
    fig._noise_browser_buttons = (btn_prev, btn_next)
    fig._noise_browser_sliders = (slider_w, slider_s)

    _draw()
    return fig