#!/usr/bin/env python3
# .spec and header CSV parsing

#%%
import csv
import re
from pathlib import Path

import numpy as np

from balloon_analysis.utility import plot

#%%

def _parse_dedicated_header_csv(header_csv: Path) -> dict[str, str]:
    raw: dict[str, str] = {}
    with header_csv.open("r", newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 2:
                continue
            k = row[0].strip().lower()
            v = row[1].strip()
            if k == "key" and v.lower() == "value":
                continue
            raw[k] = v

    mapped: dict[str, str] = {}
    if "n_spectra" in raw:
        mapped["number of spectra"] = raw["n_spectra"]
    if "integration_time_ms" in raw:
        mapped["integration time"] = raw["integration_time_ms"]
    if "bandwidth" in raw:
        mapped["bandwidth"] = raw["bandwidth"]

    for k, v in raw.items():
        mapped.setdefault(k, v)
    return mapped


def load_spec_file(spec_path: Path):
    with spec_path.open("rb") as f:
        file_bytes = f.read()

    header_line = ""
    meta_raw: dict[str, str] = {}
    payload = file_bytes
    header_source = "inline"

    nl = file_bytes.find(b"\n")
    if nl >= 0:
        first_line = file_bytes[:nl].decode("ascii", errors="replace").strip()
        parsed = parse_header_line(first_line)
        if "number of spectra" in parsed:
            header_line = first_line
            meta_raw = parsed
            payload = file_bytes[nl + 1 :]

    if "number of spectra" not in meta_raw:
        header_csv = _find_dedicated_header_file(spec_path)
        if header_csv is None:
            raise ValueError(
                f"Missing inline header in {spec_path.name} and no dedicated header CSV "
                f"found in {spec_path.parent}"
            )
        meta_raw = _parse_dedicated_header_csv(header_csv)
        header_line = f"[dedicated header] {header_csv.name}"
        header_source = str(header_csv)

    try:
        n_spectra_str = meta_raw.get("number of spectra", "")
        m = re.search(r"\d+", n_spectra_str)
        if m is None:
            raise ValueError("No integer found")
        n_spectra = int(m.group(0))
    except Exception as exc:
        raise ValueError(
            f"Could not parse 'number of spectra' from metadata: {header_line!r}"
        ) from exc

    int_time_ms: int | None = None
    s = meta_raw.get("integration time", "")
    if s:
        m = re.search(r"[-+]?\d*\.?\d+", s)
        if m is not None:
            try:
                int_time_ms = int(float(m.group(0)))
            except ValueError:
                int_time_ms = None

    bandwidth = meta_raw.get("bandwidth")
    rest = payload

    n_times = n_spectra + 1
    times_bytes = 8 * n_times
    if len(rest) < times_bytes:
        raise ValueError(f"File too short for expected {n_times} timestamps: {spec_path}")

    times_raw = rest[:times_bytes]
    spectra_raw = rest[times_bytes:]

    times = np.frombuffer(times_raw, dtype=">f8").astype("float64")

    if len(spectra_raw) % 4 != 0:
        raise ValueError(
            f"Spectra block length {len(spectra_raw)} is not a multiple of 4 bytes"
        )

    total_samples = len(spectra_raw) // 4
    if total_samples % n_spectra != 0:
        raise ValueError(
            f"Total samples {total_samples} not divisible by n_spectra={n_spectra}"
        )

    n_bins = total_samples // n_spectra
    spectra = (
        np.frombuffer(spectra_raw, dtype=">i4")
        .astype("int64")
        .reshape(n_spectra, n_bins)
    )

    meta: dict[str, object] = {
        "header_line": header_line,
        "header_source": header_source,
        "n_spectra": n_spectra,
        "int_time_ms": int_time_ms,
        "bandwidth": bandwidth,
    }
    return times, spectra, meta

def parse_header_csv(meas_dir: Path) -> dict[str, str]:
    header_files = sorted(meas_dir.glob("*_header.csv"))
    if not header_files:
        return {}

    header_path = header_files[0]
    try:
        with header_path.open("r", encoding="utf-8") as f:
            lines = [ln.strip() for ln in f.readlines() if ln.strip()]
    except OSError:
        return {}

    meta: dict[str, str] = {}
    if not lines:
        return meta

    if "\t" in lines[0] and "=" in lines[0]:
        for part in lines[0].split("\t"):
            if "=" in part:
                k, v = part.split("=", 1)
                meta[k.strip()] = v.strip()
        return meta

    for line in lines:
        if "," not in line:
            continue
        k, v = line.split(",", 1)
        key = k.strip()
        val = v.strip()
        if key.lower() == "key" and val.lower() == "value":
            continue
        if key:
            meta[key] = val
    return meta


def parse_frequency_ghz(raw: str | None) -> float | None:
    if raw is None:
        return None
    s = raw.strip().replace(" ", "").replace(",", ".")
    if not s:
        return None

    lower = s.lower()
    num = "".join(ch for ch in s if ch.isdigit() or ch in ".-+eE")
    if not num:
        return None
    try:
        value = float(num)
    except ValueError:
        return None

    if "ghz" in lower:
        return value
    if "mhz" in lower:
        return value / 1e3
    if "khz" in lower:
        return value / 1e6
    if "hz" in lower:
        return value / 1e9
    return value


def parse_temperature_value(raw: str | None) -> float | None:
    if raw is None:
        return None
    s = raw.strip().replace(",", ".")
    if not s:
        return None

    lower = s.lower()
    is_celsius = ("c" in lower) and ("k" not in lower)
    num = "".join(ch for ch in s if ch.isdigit() or ch in ".-+eE")
    if not num:
        return None
    try:
        value = float(num)
    except ValueError:
        return None
    return value + 273.15 if is_celsius else value



def _get_header_value(header_meta: dict[str, str], *keys: str) -> str | None:
    meta_lc = {k.lower(): v for k, v in header_meta.items()}
    for k in keys:
        v = meta_lc.get(k.lower())
        if v is not None:
            return v
    return None


def get_lo_ghz(header_meta: dict[str, str]) -> float | None:
    raw = _get_header_value(header_meta, "f_LO", "f_RX")
    return parse_frequency_ghz(raw)


def get_bw_ghz(header_meta: dict[str, str]) -> float | None:
    raw = _get_header_value(header_meta, "BW", "bandwidth")
    return parse_frequency_ghz(raw)


def extract_hot_cold_kelvin(header_meta: dict[str, str]) -> tuple[float | None, float | None]:
    meta_lc = {k.lower(): v for k, v in header_meta.items()}
    t_hot_raw = meta_lc.get("t_hot") or meta_lc.get("thot")
    t_cold_raw = meta_lc.get("t_cold") or meta_lc.get("tcold")
    return parse_temperature_value(t_hot_raw), parse_temperature_value(t_cold_raw)



def save_hot_cold_average_csv(
    meas_dir: Path,
    avg_hot: np.ndarray,
    avg_cold: np.ndarray,
    header_meta: dict[str, str],
) -> Path:
    if avg_hot.size != avg_cold.size:
        raise ValueError("avg_hot and avg_cold must have the same length.")

    x_freq, _ = plot.build_x_axis(avg_hot.size, header_meta, x_axis_mode="frequency")
    out_path = meas_dir / f"{meas_dir.name}_hot_cold_avg.csv"

    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["frequency_ghz", "cold_load", "hot_load"])
        for freq, cold_val, hot_val in zip(x_freq, avg_cold, avg_hot):
            writer.writerow(
                [f"{float(freq):.9f}", f"{float(cold_val):.9f}", f"{float(hot_val):.9f}"]
            )

    return out_path



def print_header_meta(header_meta: dict[str, str]) -> None:
    if not header_meta:
        print("Header metadata: <none found>")
        return
    print("Header metadata:")
    for k in sorted(header_meta.keys()):
        print(f"  {k}={header_meta[k]}")
# %%
