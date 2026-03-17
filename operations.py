"""operations.py - Business logic for Project 41: Weather Data Explorer With Forecasts."""

from __future__ import annotations

import math
import random
import statistics
import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple

import matplotlib

matplotlib.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from models import (
    create_forecast_record,
    create_location_record,
    create_anomaly_record,
    create_reading_record,
    create_session_summary,
    create_weather_config,
)
from storage import (
    OUTPUTS_DIR,
    ensure_data_dirs,
    load_location_library,
    load_reading_catalog,
    load_run_catalog,
    save_forecast_file,
    save_location_library,
    save_reading_catalog,
    save_run_record,
)


def _session_id() -> str:
    """Build a compact session ID from UTC timestamp."""
    return datetime.utcnow().strftime('%Y%m%d_%H%M%S')


def _default_location_library() -> List[Dict[str, Any]]:
    """Return deterministic starter locations used on first run."""
    return [
        create_location_record('loc_001', 'New York', 40.7128, -74.0060, 6.0, 66.0),
        create_location_record('loc_002', 'Chicago', 41.8781, -87.6298, 1.0, 62.0),
        create_location_record('loc_003', 'Los Angeles', 34.0522, -118.2437, 18.0, 55.0),
    ]


_LOCATION_PARAMS: Dict[str, Dict[str, Any]] = {
    'loc_001': {
        'temp_base': 6.0, 'temp_std': 4.5,
        'humid_base': 66.0, 'humid_std': 8.0,
        'wind_base': 18.0, 'wind_std': 6.0,
        'pressure_base': 1012.0, 'pressure_std': 5.0,
    },
    'loc_002': {
        'temp_base': 1.0, 'temp_std': 6.0,
        'humid_base': 62.0, 'humid_std': 10.0,
        'wind_base': 22.0, 'wind_std': 7.0,
        'pressure_base': 1010.0, 'pressure_std': 6.0,
    },
    'loc_003': {
        'temp_base': 18.0, 'temp_std': 3.0,
        'humid_base': 55.0, 'humid_std': 7.0,
        'wind_base': 14.0, 'wind_std': 5.0,
        'pressure_base': 1015.0, 'pressure_std': 4.0,
    },
}


def _generate_readings_for_location(
    location: Dict[str, Any],
    history_days: int,
    start_date: datetime,
    rng: random.Random,
    reading_counter: List[int],
) -> List[Dict[str, Any]]:
    """Generate simulated daily weather readings for one location."""
    location_id = location['location_id']
    params = _LOCATION_PARAMS.get(
        location_id,
        {
            'temp_base': 15.0, 'temp_std': 4.0,
            'humid_base': 60.0, 'humid_std': 8.0,
            'wind_base': 15.0, 'wind_std': 5.0,
            'pressure_base': 1013.0, 'pressure_std': 5.0,
        },
    )

    readings = []
    for day_offset in range(history_days):
        date = start_date + timedelta(days=day_offset)
        date_str = date.strftime('%Y-%m-%d')

        seasonal_offset = 2.0 * math.sin(math.pi * day_offset / history_days)
        temperature_c = params['temp_base'] + seasonal_offset + rng.gauss(0.0, params['temp_std'])
        humidity_pct = max(10.0, min(100.0, params['humid_base'] + rng.gauss(0.0, params['humid_std'])))
        wind_kph = max(0.0, params['wind_base'] + rng.gauss(0.0, params['wind_std']))
        pressure_hpa = params['pressure_base'] + rng.gauss(0.0, params['pressure_std'])

        reading_counter[0] += 1
        reading_id = f'rdg_{reading_counter[0]:03d}'
        readings.append(
            create_reading_record(
                reading_id=reading_id,
                location_id=location_id,
                location_name=location['name'],
                date_str=date_str,
                temperature_c=temperature_c,
                humidity_pct=humidity_pct,
                wind_kph=wind_kph,
                pressure_hpa=pressure_hpa,
            )
        )

    return readings


def _detect_anomalies(
    readings: List[Dict[str, Any]],
    threshold_sigma: float,
    anomaly_counter: List[int],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Detect statistical anomalies in readings using the Z-score method, grouped by location."""
    location_readings: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for reading in readings:
        location_readings[reading['location_id']].append(reading)

    all_anomalies: List[Dict[str, Any]] = []
    annotated_readings = [dict(r) for r in readings]
    reading_index = {r['reading_id']: annotated_readings[i] for i, r in enumerate(readings)}

    metrics = ['temperature_c', 'wind_kph']

    for location_id, loc_readings in location_readings.items():
        for metric in metrics:
            values = [r[metric] for r in loc_readings]
            if len(values) < 3:
                continue
            mean_val = statistics.mean(values)
            try:
                std_val = statistics.stdev(values)
            except statistics.StatisticsError:
                continue
            if std_val < 0.001:
                continue

            for reading in loc_readings:
                value = reading[metric]
                z_score = (value - mean_val) / std_val
                if abs(z_score) > threshold_sigma:
                    anomaly_counter[0] += 1
                    anomaly_id = f'anom_{anomaly_counter[0]:03d}'
                    all_anomalies.append(
                        create_anomaly_record(
                            anomaly_id=anomaly_id,
                            location_id=location_id,
                            location_name=reading['location_name'],
                            date_str=reading['date'],
                            metric=metric,
                            value=value,
                            z_score=z_score,
                            threshold=threshold_sigma,
                        )
                    )
                    rdg = reading_index[reading['reading_id']]
                    rdg['is_anomaly'] = True
                    rdg['anomaly_metric'] = metric
                    rdg['z_score'] = round(z_score, 3)

    return annotated_readings, all_anomalies


def _linear_regression(xs: List[float], ys: List[float]) -> Tuple[float, float]:
    """Compute slope and intercept of least-squares linear regression."""
    n = len(xs)
    if n < 2:
        return 0.0, (ys[0] if ys else 0.0)
    x_mean = sum(xs) / n
    y_mean = sum(ys) / n
    numerator = sum((xs[i] - x_mean) * (ys[i] - y_mean) for i in range(n))
    denominator = sum((xs[i] - x_mean) ** 2 for i in range(n))
    if denominator < 1e-10:
        return 0.0, y_mean
    slope = numerator / denominator
    intercept = y_mean - slope * x_mean
    return slope, intercept


def _generate_forecasts(
    readings: List[Dict[str, Any]],
    locations: List[Dict[str, Any]],
    horizon_days: int,
    forecast_counter: List[int],
) -> List[Dict[str, Any]]:
    """Generate short-term temperature forecasts using linear regression per location."""
    location_readings: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for reading in readings:
        location_readings[reading['location_id']].append(reading)

    all_forecasts: List[Dict[str, Any]] = []

    for location in locations:
        location_id = location['location_id']
        loc_readings = sorted(location_readings[location_id], key=lambda r: r['date'])
        if not loc_readings:
            continue

        xs = list(range(len(loc_readings)))
        ys = [r['temperature_c'] for r in loc_readings]
        slope, intercept = _linear_regression(xs, ys)

        trend = 'warming' if slope > 0.2 else ('cooling' if slope < -0.2 else 'stable')

        last_date = datetime.strptime(loc_readings[-1]['date'], '%Y-%m-%d')
        n_history = len(loc_readings)

        for day_offset in range(1, horizon_days + 1):
            forecast_date = last_date + timedelta(days=day_offset)
            future_x = n_history - 1 + day_offset
            forecast_temp = slope * future_x + intercept
            forecast_counter[0] += 1
            forecast_id = f'fct_{forecast_counter[0]:03d}'
            all_forecasts.append(
                create_forecast_record(
                    forecast_id=forecast_id,
                    location_id=location_id,
                    location_name=location['name'],
                    date_str=forecast_date.strftime('%Y-%m-%d'),
                    forecast_temp_c=forecast_temp,
                    trend=trend,
                )
            )

    return all_forecasts


def _save_timeseries_plot(
    readings: List[Dict[str, Any]],
    forecasts: List[Dict[str, Any]],
    anomalies: List[Dict[str, Any]],
    session_id: str,
    locations: List[Dict[str, Any]],
) -> str:
    """Persist a time-series plot of temperature readings and 7-day forecast per location."""
    location_colors = ['#1d3557', '#e63946', '#2a9d8f', '#f4a261', '#a8dadc']
    color_map = {
        loc['location_id']: location_colors[i % len(location_colors)]
        for i, loc in enumerate(locations)
    }

    figure, axis = plt.subplots(figsize=(12, 5))

    location_readings_map: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for reading in readings:
        location_readings_map[reading['location_id']].append(reading)

    location_forecasts_map: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for fct in forecasts:
        location_forecasts_map[fct['location_id']].append(fct)

    anomaly_keys = {(a['location_id'], a['date']) for a in anomalies if a['metric'] == 'temperature_c'}

    for location in locations:
        location_id = location['location_id']
        color = color_map[location_id]
        sorted_readings = sorted(location_readings_map[location_id], key=lambda r: r['date'])
        if not sorted_readings:
            continue

        dates = [datetime.strptime(r['date'], '%Y-%m-%d') for r in sorted_readings]
        temps = [r['temperature_c'] for r in sorted_readings]
        axis.plot(
            dates, temps,
            color=color, marker='o', markersize=4, linewidth=1.5,
            label=location['name'], zorder=3,
        )

        anom_dates = []
        anom_temps = []
        for r in sorted_readings:
            if (location_id, r['date']) in anomaly_keys:
                anom_dates.append(datetime.strptime(r['date'], '%Y-%m-%d'))
                anom_temps.append(r['temperature_c'])
        if anom_dates:
            axis.scatter(anom_dates, anom_temps, marker='x', color='#ff006e', s=100, linewidths=2.5, zorder=5)

        sorted_forecasts = sorted(location_forecasts_map[location_id], key=lambda f: f['date'])
        if sorted_forecasts:
            fct_dates = [datetime.strptime(f['date'], '%Y-%m-%d') for f in sorted_forecasts]
            fct_temps = [f['forecast_temp_c'] for f in sorted_forecasts]
            axis.plot(
                [dates[-1]] + fct_dates,
                [temps[-1]] + fct_temps,
                color=color, linestyle='--', linewidth=1.2, alpha=0.65, zorder=2,
            )

    axis.scatter([], [], marker='x', color='#ff006e', s=100, linewidths=2.5, label='anomaly')
    axis.axvline(
        x=datetime.strptime(readings[-1]['date'], '%Y-%m-%d') if readings else datetime.utcnow(),
        color='grey', linestyle=':', linewidth=1.0, alpha=0.6,
    )
    axis.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    axis.xaxis.set_major_locator(mdates.DayLocator(interval=3))
    figure.autofmt_xdate(rotation=30)
    axis.set_xlabel('Date')
    axis.set_ylabel('Temperature (°C)')
    axis.set_title('Weather Temperature: History and 7-Day Forecast')
    axis.legend(loc='upper left', fontsize=8)
    axis.grid(alpha=0.25)
    figure.tight_layout()

    file_path = OUTPUTS_DIR / f'timeseries_{session_id}.png'
    figure.savefig(file_path, dpi=150)
    plt.close(figure)
    return str(file_path)


def _save_anomaly_chart(
    anomalies: List[Dict[str, Any]],
    session_id: str,
    locations: List[Dict[str, Any]],
) -> str:
    """Persist a bar chart showing anomaly count per location."""
    from collections import Counter

    name_map = {loc['location_id']: loc['name'] for loc in locations}
    counts = Counter(name_map.get(a['location_id'], a['location_id']) for a in anomalies)
    location_names = [loc['name'] for loc in locations]
    heights = [counts.get(name, 0) for name in location_names]

    figure, axis = plt.subplots(figsize=(8, 4))
    bar_colors = ['#e63946' if h > 1 else '#f4a261' for h in heights]
    bars = axis.bar(location_names, heights, color=bar_colors, edgecolor='white', linewidth=0.8)
    for bar, height in zip(bars, heights):
        if height > 0:
            axis.text(
                bar.get_x() + bar.get_width() / 2.0,
                height + 0.05,
                str(height),
                ha='center',
                va='bottom',
                fontsize=9,
            )
    axis.set_xlabel('Location')
    axis.set_ylabel('Anomalies detected')
    axis.set_title('Anomaly Frequency by Location')
    axis.grid(axis='y', alpha=0.3)
    figure.tight_layout()

    file_path = OUTPUTS_DIR / f'anomalies_{session_id}.png'
    figure.savefig(file_path, dpi=150)
    plt.close(figure)
    return str(file_path)


def load_weather_profile() -> Dict[str, Any]:
    """Return startup profile built from previously saved catalogs."""
    run_catalog = load_run_catalog()
    reading_catalog = load_reading_catalog()
    library = load_location_library()
    recent_readings = [
        f"{item.get('reading_id', '')}:{item.get('location_id', '')}:{item.get('date', '')}"
        for item in reading_catalog[-6:]
    ]
    return {
        'catalog_file': 'data/runs.json',
        'reading_catalog_file': 'data/readings.json',
        'library_file': 'data/locations.json',
        'runs_stored': len(run_catalog),
        'reading_records_stored': len(reading_catalog),
        'locations_available': len(library),
        'recent_readings': recent_readings,
    }


def run_core_flow() -> Dict[str, Any]:
    """Run one complete weather data ingestion, anomaly detection, and forecast session."""
    ensure_data_dirs()
    config = create_weather_config()
    session_id = _session_id()
    rng = random.Random(config['random_seed'])
    started = time.perf_counter()

    library = load_location_library()
    if not library:
        library = _default_location_library()
        save_location_library(library)

    today = datetime.utcnow().date()
    start_date = datetime.combine(today - timedelta(days=config['history_days']), datetime.min.time())

    all_readings: List[Dict[str, Any]] = []
    reading_counter = [0]

    for location in library:
        loc_readings = _generate_readings_for_location(
            location,
            config['history_days'],
            start_date,
            rng,
            reading_counter,
        )
        all_readings.extend(loc_readings)

    anomaly_counter = [0]
    annotated_readings, all_anomalies = _detect_anomalies(
        all_readings,
        config['anomaly_threshold'],
        anomaly_counter,
    )

    forecast_counter = [0]
    all_forecasts = _generate_forecasts(
        annotated_readings,
        library,
        config['forecast_horizon'],
        forecast_counter,
    )

    timeseries_file = ''
    anomaly_chart_file = ''
    if config['include_timeseries_plot']:
        timeseries_file = _save_timeseries_plot(
            annotated_readings, all_forecasts, all_anomalies, session_id, library
        )
    if config['include_anomaly_chart']:
        anomaly_chart_file = _save_anomaly_chart(all_anomalies, session_id, library)

    forecast_file = save_forecast_file(all_forecasts, session_id)

    reading_catalog = load_reading_catalog()
    for rdg in annotated_readings:
        reading_catalog.append(
            {
                'reading_id': rdg['reading_id'],
                'session_id': session_id,
                'location_id': rdg['location_id'],
                'date': rdg['date'],
                'temperature_c': rdg['temperature_c'],
                'is_anomaly': rdg['is_anomaly'],
            }
        )
    save_reading_catalog(reading_catalog)

    elapsed_ms = (time.perf_counter() - started) * 1000.0

    temps = [r['temperature_c'] for r in annotated_readings]
    mean_temp = statistics.mean(temps) if temps else 0.0
    max_z = max((abs(a['z_score']) for a in all_anomalies), default=0.0)
    anomaly_rate = len(all_anomalies) / len(annotated_readings) if annotated_readings else 0.0

    metrics: Dict[str, Any] = {
        'anomaly_rate': round(anomaly_rate, 4),
        'mean_temp_c': round(mean_temp, 1),
        'max_anomaly_z': round(max_z, 2),
        'forecast_method': 'linear_regression',
        'locations_with_anomalies': len({a['location_id'] for a in all_anomalies}),
    }

    reading_previews = [
        {
            'reading_id': rdg['reading_id'],
            'location_name': rdg['location_name'],
            'date': rdg['date'],
            'temperature_c': rdg['temperature_c'],
            'humidity_pct': rdg['humidity_pct'],
            'is_anomaly': rdg['is_anomaly'],
        }
        for rdg in annotated_readings[: config['max_readings_in_report']]
    ]

    artifacts = {
        'forecast_file': forecast_file,
        'timeseries_file': timeseries_file,
        'anomaly_chart_file': anomaly_chart_file,
        'reading_count': len(annotated_readings),
    }

    summary = create_session_summary(
        session_id=session_id,
        locations_processed=len(library),
        readings_total=len(annotated_readings),
        anomalies_detected=len(all_anomalies),
        forecast_points=len(all_forecasts),
        elapsed_ms=elapsed_ms,
        artifacts=artifacts,
        reading_previews=reading_previews,
        metrics=metrics,
    )

    run_record = dict(summary)
    session_file = save_run_record(run_record)
    summary['artifacts']['session_file'] = session_file
    return summary
