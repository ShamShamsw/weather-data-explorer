"""main.py - Entry point for Project 41: Weather Data Explorer With Forecasts."""

from display import format_header, format_run_report, format_startup_guide
from models import create_weather_config
from operations import load_weather_profile, run_core_flow
from storage import ensure_data_dirs


def main() -> None:
    """Run one complete weather data ingestion, anomaly detection, and forecast session."""
    ensure_data_dirs()
    print(format_header())

    config = create_weather_config()
    profile = load_weather_profile()
    print(format_startup_guide(config, profile))

    summary = run_core_flow()
    print(format_run_report(summary))


if __name__ == '__main__':
    main()
