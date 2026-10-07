from pathlib import Path
import pandas as pd


class TelemetryAnalysis:
    @staticmethod
    def default_data_dir() -> Path:
        return Path(__file__).resolve().parents[2] / "data"

    @staticmethod
    def default_csv_path() -> Path | None:
        data_dir = TelemetryAnalysis.default_data_dir()

        candidates = sorted(data_dir.glob("*_system_telemetry.csv"))
        if candidates:
            return candidates[-1]  # latest by filename timestamp

        direct_name = data_dir / "system_telemetry.csv"
        if direct_name.exists():
            return direct_name

        typo_name = data_dir / "system_telemtry.csv"
        if typo_name.exists():
            return typo_name

        return None

    @staticmethod
    def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        if "timestamp" in df.columns and "time" not in df.columns:
            df = df.rename(columns={"timestamp": "time"})

        if "time" in df.columns:
            df["time"] = pd.to_datetime(df["time"], errors="coerce")

        if "throttled" in df.columns:
            def _to_int(v):
                if isinstance(v, str) and v.startswith("0x"):
                    try:
                        return int(v, 16)
                    except ValueError:
                        return pd.NA
                return v

            df["throttled_int"] = df["throttled"].map(_to_int)

        return df

    @staticmethod
    def get_series_specs():
        return [
            {"column": "cpu_temp_c", "label": "CPU Temp", "unit": "°C"},
            {"column": "pmic_temp_c", "label": "PMIC Temp", "unit": "°C"},
            {"column": "core_voltage_v", "label": "Core Voltage", "unit": "V"},
            {"column": "passive_state", "label": "Passive State", "unit": ""},
            {"column": "throttled_int", "label": "Throttled (int)", "unit": ""},
        ]


class TemperatureAnalysis:
    @staticmethod
    def get_series_specs():
        return [
            {
                "column": "temperature_c",
                "label": "Temperature",
                "unit": "°C",
            },
        ]

    @staticmethod
    def default_data_dir() -> Path:
        return Path("data")


class GyroAnalysis:
    @staticmethod
    def get_series_specs():
        return [
            # Gyro
            {"column": "gyro_x_dps", "label": "Gyro X", "unit": "°/s"},
            {"column": "gyro_y_dps", "label": "Gyro Y", "unit": "°/s"},
            {"column": "gyro_z_dps", "label": "Gyro Z", "unit": "°/s"},
            # Acceleration
            {"column": "accel_x_g", "label": "Accel X", "unit": "g"},
            {"column": "accel_y_g", "label": "Accel Y", "unit": "g"},
            {"column": "accel_z_g", "label": "Accel Z", "unit": "g"},
            # Integrated/estimated rotation
            {"column": "rot_x_deg", "label": "Rot X", "unit": "°"},
            {"column": "rot_y_deg", "label": "Rot Y", "unit": "°"},
        ]

    @staticmethod
    def default_data_dir() -> Path:
        return Path("data")


class PressureAnalysis:
    @staticmethod
    def get_series_specs():
        return [
            {
                "column": "temperature_c",
                "label": "Temperature",
                "unit": "°C",
                "transform": lambda s: s - 273.15,
            },
            {
                "column": "humidity_pct",
                "label": "Humidity",
                "unit": "%",
            },
            {
                "column": "pressure_mbar",
                "label": "Pressure",
                "unit": "mbar",
            },
        ]

    @staticmethod
    def preprocess_data(df):
        """Normalize pressure data to mbar if it's in hpa."""
        if "pressure_hpa" in df.columns:
            df["pressure_mbar"] = df["pressure_hpa"]
        elif "pressure_mbar" not in df.columns:
            raise ValueError("No 'pressure_mbar' or 'pressure_hpa' column found")
        return df

    @staticmethod
    def default_data_dir() -> Path:
        return Path("data")