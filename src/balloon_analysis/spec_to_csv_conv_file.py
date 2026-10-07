#!/usr/bin/env python3
from __future__ import annotations

import csv
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

import numpy as np

from balloon_analysis.utility import spec_analysis_utils as sau
from balloon_analysis.utility import io

def select_spec_file(initialdir: Path | None = None) -> Path | None:
    root = tk.Tk()
    root.withdraw()
    path = filedialog.askopenfilename(
        title="Select a .spec file",
        initialdir=str(initialdir) if initialdir else None,
        filetypes=[("SPEC files", "*.spec"), ("All files", "*.*")],
    )
    root.destroy()
    return Path(path) if path else None


def spec_to_csv(spec_path: Path) -> Path:
    times, spectra, meta = io.load_spec_file(spec_path)
    out_path = spec_path.with_suffix(".csv")

    x, xlabel = sau._build_x_axis(spectra.shape[1], meta, "frequency")
    np.repeat(times, spectra.shape[0])
    spectra.reshape(-1)
    np.tile(x, spectra.shape[0])

    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp_s", xlabel, "spectrum_index", "count"])
        for i, (t, row) in enumerate(zip(times, spectra)):
            for xi, yi in zip(x, row):
                writer.writerow([float(t), float(xi), i, int(yi)])

    return out_path


def main() -> None:
    spec_path = select_spec_file(Path.cwd())
    if spec_path is None:
        return
    if spec_path.suffix.lower() != ".spec":
        messagebox.showerror("Invalid file", "Please select a .spec file.")
        return

    try:
        out_path = spec_to_csv(spec_path)
    except Exception as exc:
        messagebox.showerror("Conversion failed", str(exc))
        return

    messagebox.showinfo("Done", f"Saved CSV as:\n{out_path}")


if __name__ == "__main__":
    main()
