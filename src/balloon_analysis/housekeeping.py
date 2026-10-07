import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from balloon_analysis.utility.browser import select_file
from balloon_analysis.utility.housekeeping_utils import load_data
from balloon_analysis.utility.sensors import (
    GyroAnalysis,
    PressureAnalysis,
    TelemetryAnalysis,
    TemperatureAnalysis,
)

SENSORS = {
    "pressure": PressureAnalysis,
    "temperature": TemperatureAnalysis,
    "gyro": GyroAnalysis,
    "telemetry": TelemetryAnalysis,
}


def _scatter_series(df, series_specs, title):
    fig, ax = plt.subplots(figsize=(12, 6))
    for spec in series_specs:
        col = spec["column"]
        if col in df.columns:
            ax.scatter(df["time"], df[col], s=10, label=spec.get("label", col))
    ax.set_title(title)
    ax.set_xlabel("time")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right")
    fig.tight_layout()
    plt.show()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sensor",
        choices=SENSORS.keys(),
        default=None,
        help="Which sensor data should be analyzed.",
    )
    args = parser.parse_args()

    if args.sensor is None:
        parser.print_help()
        return

    sensor_mod = SENSORS[args.sensor]

    csv_path = None
    if args.sensor != "telemetry" and hasattr(sensor_mod, "default_csv_path"):
        csv_path = sensor_mod.default_csv_path()

    if csv_path is None:
        custom_default_dir = Path("/mnt/c/DLR/Data")
        
        # Use select_file imported from browser.py
        csv_path = select_file(initialdir=custom_default_dir, title="Select sensor CSV file")
        if csv_path is None or str(csv_path) == ".":
            print("No file selected; exiting.")
            return

    df = load_data(csv_path)

    if hasattr(sensor_mod, "preprocess_data"):
        df = sensor_mod.preprocess_data(df)

    if args.sensor == "temperature":
        # Rename timestamp column to 'time' if needed
        if "timestamp" in df.columns and "time" not in df.columns:
            df = df.rename(columns={"timestamp": "time"})
        if "time" in df.columns:
            df["time"] = pd.to_datetime(df["time"], errors="coerce")

        # Melt the wide-format temperature columns into long format
        id_vars = ["time"] if "time" in df.columns else []
        value_vars = [col for col in df.columns if col.endswith("_temp_C")]
        
        df = df.melt(
            id_vars=id_vars,
            value_vars=value_vars,
            var_name="sensor_id",
            value_name="temperature_c"
        )

        temp_df = (
            df.pivot_table(index="time", columns="sensor_id", values="temperature_c", aggfunc="mean")
            .reset_index()
        )

        fig, ax = plt.subplots(figsize=(12, 6))
        for col in temp_df.columns:
            if col == "time":
                continue
            ax.scatter(temp_df["time"], temp_df[col], s=10, label=str(col))

        ax.set_title("Temperature data")
        ax.set_xlabel("time")
        ax.set_ylabel("Temperature (°C)")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="upper right")
        fig.tight_layout()
        plt.show()
        return

    series_specs = sensor_mod.get_series_specs()

    if args.sensor == "gyro":
        groups = [
            ("Gyro (°/s)", ["gyro_x_dps", "gyro_y_dps", "gyro_z_dps"]),
            ("Accel (g)", ["accel_x_g", "accel_y_g", "accel_z_g"]),
            ("Rot (°)", ["rot_x_deg", "rot_y_deg"]),
        ]

        fig, axes = plt.subplots(3, 1, sharex=True, figsize=(12, 9))
        time_values = df["time"]

        for ax, (ylabel, cols) in zip(axes, groups):
            for col in cols:
                if col in df.columns:
                    ax.scatter(time_values, df[col], s=10, label=col)
            ax.set_ylabel(ylabel)
            ax.grid(True, alpha=0.3)
            ax.legend(loc="upper right")

        axes[-1].set_xlabel("time")
        fig.suptitle("Gyro data")
        fig.tight_layout()
        plt.show()
    else:
        _scatter_series(df, series_specs, title=f"{args.sensor.capitalize()} data")


if __name__ == "__main__":
    main()