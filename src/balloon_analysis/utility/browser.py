#!/usr/bin/env python3
"""Interactive file/folder browser helpers."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from tkinter import filedialog

SPEC_GLOB = "*.spec"


@contextmanager
def _hidden_root() -> Iterator[tk.Tk]:
    """Hidden Tk root window, always destroyed (even if the dialog raises)."""
    root = tk.Tk()
    root.withdraw()
    try:
        yield root
    finally:
        root.destroy()


def _initialdir_arg(initialdir: Path | None) -> str | None:
    return str(initialdir) if initialdir else None


def select_folder(initialdir: Path | None = None) -> Path | None:
    """Ask the user for an existing folder. Returns None if cancelled."""
    with _hidden_root():
        path = filedialog.askdirectory(
            title="Select folder",
            initialdir=_initialdir_arg(initialdir),
            mustexist=True,
        )
    return Path(path) if path else None


def select_file(initialdir: Path | None = None, title: str = "Select file") -> Path | None:
    """Ask the user for a file. Returns None if cancelled."""
    with _hidden_root():
        path = filedialog.askopenfilename(
            title=title,
            initialdir=_initialdir_arg(initialdir),
        )
    return Path(path) if path else None


def _has_spec_files(folder: Path) -> bool:
    return any(folder.glob(SPEC_GLOB))


def resolve_measurement_dir_with_specs(meas_dir: Path) -> Path:
    """Return `meas_dir` if it contains .spec files, else a subfolder that does.

    If several subfolders qualify, the one whose name sorts last is used
    (e.g. the latest timestamped run). If none qualify, `meas_dir` is returned
    unchanged.
    """
    if _has_spec_files(meas_dir):
        return meas_dir

    candidates = [d for d in meas_dir.iterdir() if d.is_dir() and _has_spec_files(d)]
    if not candidates:
        return meas_dir

    chosen = max(candidates, key=lambda d: d.name)
    print(f"No .spec files in {meas_dir}; using subfolder {chosen}")
    return chosen
