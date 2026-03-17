"""display.py - Presentation helpers for Project 41: Weather Data Explorer With Forecasts."""

from typing import Any, Dict, List


def format_header() -> str:
    """Format session header banner."""
    return '=' * 70 + '\n' + '   WEATHER DATA EXPLORER WITH FORECASTS\n' + '=' * 70


def format_startup_guide(config: Dict[str, Any], profile: Dict[str, Any]) -> str:
    """Format startup configuration and historical profile."""
    recent = ', '.join(profile.get('recent_readings', [])) or 'None yet'
    metrics_tracked = 'temperature_c, humidity_pct, wind_kph'
    lines = [
        '',
        'Configuration:',
        f"   Project type:         {config['project_type']}",
        f"   Locations:            {', '.join(config['locations'])}",
        f"   History days:         {config['history_days']}",
        f"   Forecast horizon:     {config['forecast_horizon']} days",
        f"   Anomaly threshold:    {config['anomaly_threshold']:.1f} \u03c3",
        f"   Metrics tracked:      {metrics_tracked}",
        f"   Time-series plot:     {config['include_timeseries_plot']}",
        f"   Anomaly chart:        {config['include_anomaly_chart']}",
        f"   Max readings report:  {config['max_readings_in_report']}",
        f"   Random seed:          {config['random_seed']}",
        '',
        'Startup:',
        '   Data directory:       data/',
        '   Outputs directory:    data/outputs/',
        (
            f"   Location library:     {profile['library_file']} "
            f"(loaded {profile['locations_available']} locations)"
        ),
        (
            f"   Run catalog:          {profile['catalog_file']} "
            f"(loaded {profile['runs_stored']} runs)"
        ),
        (
            f"   Reading catalog:      {profile['reading_catalog_file']} "
            f"(loaded {profile['reading_records_stored']} readings)"
        ),
        f"   Recent readings:      {recent}",
        '',
        '---',
    ]
    return '\n'.join(lines)


def format_reading_table(reading_previews: List[Dict[str, Any]]) -> str:
    """Format weather reading preview table."""
    if not reading_previews:
        return 'No readings generated.'
    lines = [
        'Reading previews:',
        '   ID         | Location      | Date       | Temp (°C) | Humid (%) | Anomaly',
        '   -----------+---------------+------------+-----------+-----------+---------',
    ]
    for rdg in reading_previews:
        lines.append(
            '   '
            f"{rdg['reading_id'][:10]:<10} | "
            f"{rdg['location_name'][:13]:<13} | "
            f"{rdg['date'][:10]:<10} | "
            f"{rdg['temperature_c']:<9.1f} | "
            f"{rdg['humidity_pct']:<9.1f} | "
            f"{'yes' if rdg['is_anomaly'] else 'no'}"
        )
    return '\n'.join(lines)


def format_run_report(summary: Dict[str, Any]) -> str:
    """Format final session report."""
    artifacts = summary.get('artifacts', {})
    metrics = summary.get('metrics', {})
    lines = [
        '',
        'Session complete:',
        f"   Session ID:           {summary['session_id']}",
        f"   Locations processed:  {summary['locations_processed']}",
        f"   Total readings:       {summary['readings_total']}",
        f"   Anomalies detected:   {summary['anomalies_detected']}",
        f"   Forecast points:      {summary['forecast_points']}",
        f"   Elapsed time:         {summary['elapsed_ms']:.2f} ms",
        '',
        (
            f"Dataset metrics: "
            f"anomaly_rate={metrics.get('anomaly_rate', 0.0):.1%} | "
            f"mean_temp_c={metrics.get('mean_temp_c', 0.0):.1f} | "
            f"max_anomaly_z={metrics.get('max_anomaly_z', 0.0):.2f} | "
            f"forecast_method={metrics.get('forecast_method', 'N/A')}"
        ),
        '',
        format_reading_table(summary.get('reading_previews', [])),
        '',
        'Artifacts saved:',
        f"   Run record:           {artifacts.get('session_file', 'N/A')}",
        f"   Forecast file:        {artifacts.get('forecast_file', 'N/A')}",
        f"   Time-series plot:     {artifacts.get('timeseries_file', 'N/A')}",
        f"   Anomaly chart:        {artifacts.get('anomaly_chart_file', 'N/A')}",
        f"   Total readings logged: {artifacts.get('reading_count', 0)}",
    ]
    return '\n'.join(lines)


def format_message(message: str) -> str:
    """Format a user-facing message string."""
    return f'[Project 41] {message}'
