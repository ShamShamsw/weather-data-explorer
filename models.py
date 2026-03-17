"""models.py - Data models for Project 41: Weather Data Explorer With Forecasts."""

from datetime import datetime
from typing import Any, Dict, List


def _utc_timestamp() -> str:
    """Return an ISO-8601 UTC timestamp string."""
    return datetime.utcnow().isoformat(timespec='seconds') + 'Z'


def create_weather_config(
    locations: List[str] | None = None,
    history_days: int = 14,
    forecast_horizon: int = 7,
    anomaly_threshold: float = 2.0,
    include_timeseries_plot: bool = True,
    include_anomaly_chart: bool = True,
    max_readings_in_report: int = 8,
    random_seed: int = 42,
) -> Dict[str, Any]:
    """Create a validated configuration record for the weather explorer session."""
    resolved_locations = locations if locations else ['New York', 'Chicago', 'Los Angeles']
    return {
        'project_type': 'weather_data_explorer',
        'locations': list(resolved_locations),
        'history_days': max(7, int(history_days)),
        'forecast_horizon': max(1, int(forecast_horizon)),
        'anomaly_threshold': float(anomaly_threshold),
        'include_timeseries_plot': bool(include_timeseries_plot),
        'include_anomaly_chart': bool(include_anomaly_chart),
        'max_readings_in_report': max(2, int(max_readings_in_report)),
        'random_seed': int(random_seed),
        'created_at': _utc_timestamp(),
    }


def create_location_record(
    location_id: str,
    name: str,
    latitude: float,
    longitude: float,
    base_temp_c: float,
    base_humidity_pct: float,
) -> Dict[str, Any]:
    """Create one location record."""
    return {
        'location_id': str(location_id),
        'name': str(name),
        'latitude': round(float(latitude), 4),
        'longitude': round(float(longitude), 4),
        'base_temp_c': round(float(base_temp_c), 1),
        'base_humidity_pct': round(float(base_humidity_pct), 1),
    }


def create_reading_record(
    reading_id: str,
    location_id: str,
    location_name: str,
    date_str: str,
    temperature_c: float,
    humidity_pct: float,
    wind_kph: float,
    pressure_hpa: float,
    is_anomaly: bool = False,
    anomaly_metric: str = '',
    z_score: float = 0.0,
) -> Dict[str, Any]:
    """Create one weather reading record."""
    return {
        'reading_id': str(reading_id),
        'location_id': str(location_id),
        'location_name': str(location_name),
        'date': str(date_str),
        'temperature_c': round(float(temperature_c), 1),
        'humidity_pct': round(float(humidity_pct), 1),
        'wind_kph': round(float(wind_kph), 1),
        'pressure_hpa': round(float(pressure_hpa), 1),
        'is_anomaly': bool(is_anomaly),
        'anomaly_metric': str(anomaly_metric),
        'z_score': round(float(z_score), 3),
    }


def create_anomaly_record(
    anomaly_id: str,
    location_id: str,
    location_name: str,
    date_str: str,
    metric: str,
    value: float,
    z_score: float,
    threshold: float,
) -> Dict[str, Any]:
    """Create one anomaly detection record."""
    return {
        'anomaly_id': str(anomaly_id),
        'location_id': str(location_id),
        'location_name': str(location_name),
        'date': str(date_str),
        'metric': str(metric),
        'value': round(float(value), 2),
        'z_score': round(float(z_score), 3),
        'threshold': round(float(threshold), 2),
    }


def create_forecast_record(
    forecast_id: str,
    location_id: str,
    location_name: str,
    date_str: str,
    forecast_temp_c: float,
    trend: str,
    method: str = 'linear_regression',
) -> Dict[str, Any]:
    """Create one forecast record."""
    return {
        'forecast_id': str(forecast_id),
        'location_id': str(location_id),
        'location_name': str(location_name),
        'date': str(date_str),
        'forecast_temp_c': round(float(forecast_temp_c), 1),
        'trend': str(trend),
        'method': str(method),
    }


def create_session_summary(
    session_id: str,
    locations_processed: int,
    readings_total: int,
    anomalies_detected: int,
    forecast_points: int,
    elapsed_ms: float,
    artifacts: Dict[str, Any],
    reading_previews: List[Dict[str, Any]],
    metrics: Dict[str, Any],
) -> Dict[str, Any]:
    """Create final session summary for reporting and persistence."""
    return {
        'session_id': str(session_id),
        'locations_processed': int(locations_processed),
        'readings_total': int(readings_total),
        'anomalies_detected': int(anomalies_detected),
        'forecast_points': int(forecast_points),
        'elapsed_ms': float(elapsed_ms),
        'artifacts': dict(artifacts),
        'reading_previews': list(reading_previews),
        'metrics': dict(metrics),
        'finished_at': _utc_timestamp(),
    }


def create_record(**kwargs):
    """Backwards-compatible generic record factory."""
    return dict(kwargs)
