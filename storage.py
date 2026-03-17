"""storage.py - Persistence layer for Project 41: Weather Data Explorer With Forecasts."""

import json
from pathlib import Path
from typing import Any, Dict, List

DATA_DIR = Path(__file__).resolve().parent / 'data'
OUTPUTS_DIR = DATA_DIR / 'outputs'
LOCATION_LIBRARY_FILE = DATA_DIR / 'locations.json'
RUN_CATALOG_FILE = DATA_DIR / 'runs.json'
READING_CATALOG_FILE = DATA_DIR / 'readings.json'


def ensure_data_dirs() -> None:
    """Create local data/output directories if they do not exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


def _load_list_file(path: Path) -> List[Dict[str, Any]]:
    """Safely load a list-based JSON file."""
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []


def _save_list_file(path: Path, data: List[Dict[str, Any]]) -> None:
    """Persist list-based JSON with indentation."""
    path.write_text(json.dumps(data, indent=2), encoding='utf-8')


def load_location_library() -> List[Dict[str, Any]]:
    """Load location definitions from disk."""
    ensure_data_dirs()
    return _load_list_file(LOCATION_LIBRARY_FILE)


def save_location_library(library: List[Dict[str, Any]]) -> str:
    """Persist location definitions to disk."""
    ensure_data_dirs()
    _save_list_file(LOCATION_LIBRARY_FILE, library)
    return str(LOCATION_LIBRARY_FILE)


def load_run_catalog() -> List[Dict[str, Any]]:
    """Load run catalog entries from disk."""
    ensure_data_dirs()
    return _load_list_file(RUN_CATALOG_FILE)


def save_run_catalog(catalog: List[Dict[str, Any]]) -> None:
    """Persist run catalog to disk."""
    ensure_data_dirs()
    _save_list_file(RUN_CATALOG_FILE, catalog)


def load_reading_catalog() -> List[Dict[str, Any]]:
    """Load reading catalog entries from disk."""
    ensure_data_dirs()
    return _load_list_file(READING_CATALOG_FILE)


def save_reading_catalog(catalog: List[Dict[str, Any]]) -> None:
    """Persist reading catalog to disk."""
    ensure_data_dirs()
    _save_list_file(READING_CATALOG_FILE, catalog)


def save_run_record(run_record: Dict[str, Any]) -> str:
    """Persist one run record and update run catalog."""
    ensure_data_dirs()
    session_id = run_record['session_id']
    file_path = OUTPUTS_DIR / f'run_{session_id}.json'
    file_path.write_text(json.dumps(run_record, indent=2), encoding='utf-8')

    catalog = load_run_catalog()
    catalog.append(
        {
            'session_id': session_id,
            'locations_processed': run_record.get('locations_processed', 0),
            'readings_total': run_record.get('readings_total', 0),
            'anomalies_detected': run_record.get('anomalies_detected', 0),
            'forecast_points': run_record.get('forecast_points', 0),
            'elapsed_ms': run_record.get('elapsed_ms', 0.0),
            'finished_at': run_record.get('finished_at', ''),
            'run_file': str(file_path),
        }
    )
    save_run_catalog(catalog)
    return str(file_path)


def save_forecast_file(forecasts: List[Dict[str, Any]], session_id: str) -> str:
    """Persist the full forecast bundle for a session."""
    ensure_data_dirs()
    file_path = OUTPUTS_DIR / f'forecast_{session_id}.json'
    file_path.write_text(
        json.dumps({'session_id': session_id, 'forecasts': forecasts}, indent=2),
        encoding='utf-8',
    )
    return str(file_path)


def load_json(filename: str):
    """Load JSON data from the local data directory."""
    ensure_data_dirs()
    path = DATA_DIR / filename
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        return []


def save_json(filename: str, data) -> None:
    """Save JSON data to the local data directory."""
    ensure_data_dirs()
    path = DATA_DIR / filename
    path.write_text(json.dumps(data, indent=2), encoding='utf-8')
