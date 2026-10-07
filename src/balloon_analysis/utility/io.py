#!/usr/bin/env python3
"""
io.py: .spec and header CSV parsing

Layout
------
Low-level helpers
    _first_number(), _read_lines(), _parse_key_value_lines()
Header parsing
    _parse_header_line(), _find_dedicated_header_file(),
    _parse_dedicated_header_csv(), parse_header_csv()
.spec loading
    load_spec_file(), _read_inline_header(), _resolve_metadata(),
    _parse_n_spectra(), _parse_int_time_ms(), _decode_spec_payload()
Metadata values
    _get_header_value(), parse_frequency_ghz(), parse_temperature_value(),
    get_lo_ghz(), get_bw_ghz(), extract_hot_cold_kelvin()
Output
    save_hot_cold_average_csv(), print_header_meta()
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

import numpy as np

from balloon_analysis.utility import plot

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #

_RUN_SUFFIXES = ("_hot", "_cold", "_sky", "_amb")
_NUMBER_RE = re.compile(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")

# Longest unit first: "ghz" must be tested before "hz".
_FREQ_UNITS_TO_GHZ = (("ghz", 1.0), ("mhz", 1e-3), ("khz", 1e-6), ("hz", 1e-9))

_TIMESTAMP_DTYPE = ">f8"  # big-endian float64
_SAMPLE_DTYPE = ">i4"     # big-endian int32


# --------------------------------------------------------------------------- #
# Low-level helpers
# --------------------------------------------------------------------------- #

def _first_number(text: str) -> float | None:
    """Return the first number found in `text`, or None."""
    m = _NUMBER_RE.search(text)
    return float(m.group(0)) if m else None


def _read_lines(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8", errors="replace") as f:
        return [ln.strip() for ln in f if ln.strip()]


def _parse_key_value_lines(lines: list[str], *, lowercase_keys: bool) -> dict[str, str]:
    """Parse 'key,value' rows. Skips short rows and a 'key,value' header row."""
    out: dict[str, str] = {}
    for row in csv.reader(lines):
        if len(row) < 2:
            continue
        key = row[0].strip()
        val = ",".join(row[1:]).strip()
        if not key or (key.lower() == "key" and val.lower() == "value"):
            continue
        out[key.lower() if lowercase_keys else key] = val
    return out


# --------------------------------------------------------------------------- #
# Header parsing
# --------------------------------------------------------------------------- #

def _parse_header_line(header: str) -> dict[str, str]:
    """Parse an inline 'key: value, key: value' header line."""
    meta: dict[str, str] = {}
    for part in (p.strip() for p in header.split(",")):
        if ":" in part:
            key, val = part.split(":", 1)
            meta[key.strip().lower()] = val.strip()
    return meta


def _find_dedicated_header_file(spec_path: Path) -> Path | None:
    run_stem = spec_path.stem
    for suffix in _RUN_SUFFIXES:
        if run_stem.endswith(suffix):
            run_stem = run_stem[: -len(suffix)]
            break

    folder = spec_path.parent
    preferred = folder / f"{run_stem}_pi_lab_header.csv"
    candidates = [
        preferred,
        *sorted(folder.glob(f"{run_stem}*header*.csv")),
        *sorted(folder.glob("*header*.csv")),
    ]
    # Order is priority; first existing file wins.
    return next((p for p in candidates if p.is_file()), None)


def _parse_dedicated_header_csv(header_csv: Path) -> dict[str, str]:
    raw = _parse_key_value_lines(_read_lines(header_csv), lowercase_keys=True)

    # Map dedicated-file key names onto the inline-header names.
    aliases = {
        "n_spectra": "number of spectra",
        "integration_time_ms": "integration time",
        "bandwidth": "bandwidth",
    }
    mapped = {new: raw[old] for old, new in aliases.items() if old in raw}
    for k, v in raw.items():
        mapped.setdefault(k, v)
    return mapped


def parse_header_csv(meas_dir: Path) -> dict[str, str]:
    header_files = sorted(meas_dir.glob("*_header.csv"))
    if not header_files:
        return {}

    try:
        lines = _read_lines(header_files[0])
    except OSError:
        return {}
    if not lines:
        return {}

    # Legacy format: one tab-separated line of 'key=value' pairs.
    if "\t" in lines[0] and "=" in lines[0]:
        pairs = (part.split("=", 1) for part in lines[0].split("\t") if "=" in part)
        return {k.strip(): v.strip() for k, v in pairs}

    return _parse_key_value_lines(lines, lowercase_keys=False)


# --------------------------------------------------------------------------- #
# .spec loading
# --------------------------------------------------------------------------- #

def _read_inline_header(file_bytes: bytes) -> tuple[str, dict[str, str], bytes] | None:
    """Return (header_line, meta, payload) if an inline header exists, else None."""
    nl = file_bytes.find(b"\n")
    if nl < 0:
        return None
    first_line = file_bytes[:nl].decode("ascii", errors="replace").strip()
    parsed = _parse_header_line(first_line)
    if "number of spectra" not in parsed:
        return None
    return first_line, parsed, file_bytes[nl + 1 :]


def _resolve_metadata(spec_path: Path, file_bytes: bytes) -> tuple[str, dict[str, str], bytes]:
    """Find metadata (inline or dedicated CSV) and return (header_line, meta, payload)."""
    inline = _read_inline_header(file_bytes)
    if inline is not None:
        return inline

    header_csv = _find_dedicated_header_file(spec_path)
    if header_csv is None:
        raise ValueError(
            f"Missing inline header in {spec_path.name} and no dedicated header CSV "
            f"found in {spec_path.parent}"
        )
    return (
        f"[dedicated header] {header_csv.name}",
        _parse_dedicated_header_csv(header_csv),
        file_bytes,
    )


def _parse_n_spectra(meta_raw: dict[str, str], header_line: str) -> int:
    m = re.search(r"\d+", meta_raw.get("number of spectra", ""))
    if m is None:
        raise ValueError(
            f"Could not parse 'number of spectra' from metadata: {header_line!r}"
        )
    return int(m.group(0))


def _parse_int_time_ms(meta_raw: dict[str, str]) -> int | None:
    value = _first_number(meta_raw.get("integration time", ""))
    return None if value is None else int(value)


def _decode_spec_payload(
    payload: bytes, n_spectra: int, spec_path: Path
) -> tuple[np.ndarray, np.ndarray]:
    """Split payload into (times, spectra[n_spectra, n_bins])."""
    n_times = n_spectra + 1
    times_bytes = 8 * n_times
    if len(payload) < times_bytes:
        raise ValueError(f"File too short for expected {n_times} timestamps: {spec_path}")

    times = np.frombuffer(payload[:times_bytes], dtype=_TIMESTAMP_DTYPE).astype("float64")

    spectra_raw = payload[times_bytes:]
    if len(spectra_raw) % 4 != 0:
        raise ValueError(
            f"Spectra block length {len(spectra_raw)} is not a multiple of 4 bytes"
        )

    total_samples = len(spectra_raw) // 4
    if total_samples % n_spectra != 0:
        raise ValueError(
            f"Total samples {total_samples} not divisible by n_spectra={n_spectra}"
        )

    spectra = (
        np.frombuffer(spectra_raw, dtype=_SAMPLE_DTYPE)
        .astype("int64")
        .reshape(n_spectra, total_samples // n_spectra)
    )
    return times, spectra


def load_spec_file(spec_path: Path):
    file_bytes = spec_path.read_bytes()
    header_line, meta_raw, payload = _resolve_metadata(spec_path, file_bytes)

    n_spectra = _parse_n_spectra(meta_raw, header_line)
    times, spectra = _decode_spec_payload(payload, n_spectra, spec_path)

    header_source = "inline" if not header_line.startswith("[dedicated header]") else (
        str(_find_dedicated_header_file(spec_path))
    )
    meta: dict[str, object] = {
        "header_line": header_line,
        "header_source": header_source,
        "n_spectra": n_spectra,
        "int_time_ms": _parse_int_time_ms(meta_raw),
        "bandwidth": meta_raw.get("bandwidth"),
    }
    return times, spectra, meta


# --------------------------------------------------------------------------- #
# Metadata values
# --------------------------------------------------------------------------- #

def _get_header_value(header_meta: dict[str, str], *keys: str) -> str | None:
    """Case-insensitive lookup; first matching key wins."""
    meta_lc = {k.lower(): v for k, v in header_meta.items()}
    for k in keys:
        v = meta_lc.get(k.lower())
        if v is not None:
            return v
    return None


def parse_frequency_ghz(raw: str | None) -> float | None:
    if raw is None:
        return None
    s = raw.strip().replace(" ", "").replace(",", ".")
    value = _first_number(s)
    if value is None:
        return None

    lower = s.lower()
    for unit, factor in _FREQ_UNITS_TO_GHZ:
        if unit in lower:
            return value * factor
    return value  # no unit: assume GHz


def parse_temperature_value(raw: str | None) -> float | None:
    """Parse a temperature; Celsius values are converted to Kelvin."""
    if raw is None:
        return None
    s = raw.strip().replace(",", ".")
    value = _first_number(s)
    if value is None:
        return None

    lower = s.lower()
    is_celsius = "c" in lower and "k" not in lower
    return value + 273.15 if is_celsius else value


def get_lo_ghz(header_meta: dict[str, str]) -> float | None:
    return parse_frequency_ghz(_get_header_value(header_meta, "f_LO", "f_RX"))


def get_bw_ghz(header_meta: dict[str, str]) -> float | None:
    return parse_frequency_ghz(_get_header_value(header_meta, "BW", "bandwidth"))


def extract_hot_cold_kelvin(
    header_meta: dict[str, str],
) -> tuple[float | None, float | None]:
    t_hot = _get_header_value(header_meta, "t_hot", "thot")
    t_cold = _get_header_value(header_meta, "t_cold", "tcold")
    return parse_temperature_value(t_hot), parse_temperature_value(t_cold)


# --------------------------------------------------------------------------- #
# Output
# --------------------------------------------------------------------------- #

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
        for freq, cold, hot in zip(x_freq, avg_cold, avg_hot):
            writer.writerow([f"{float(freq):.9f}", f"{float(cold):.9f}", f"{float(hot):.9f}"])

    return out_path


def print_header_meta(header_meta: dict[str, str]) -> None:
    if not header_meta:
        print("Header metadata: <none found>")
        return
    print("Header metadata:")
    for k in sorted(header_meta):
        print(f"  {k}={header_meta[k]}")
