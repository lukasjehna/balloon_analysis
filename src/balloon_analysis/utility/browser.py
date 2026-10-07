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


def select_file(initialdir: Path | None = None, title: str = "Select file") -> Path | None:
    root = tk.Tk()
    root.withdraw()

    path = filedialog.askopenfilename(
        title=title,
        initialdir=str(initialdir) if initialdir else None,
    )

    root.destroy()
    return Path(path) if path else None


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
