# Beginner Project 41: Weather Data Explorer With Forecasts

**Time:** 4-6 hours  
**Difficulty:** Intermediate Beginner  
**Focus:** Simulated weather data ingestion, Z-score anomaly detection, linear-regression forecasting, and multi-location time-series visualization

---

## Why This Project?

Weather data analysis is one of the most universally relatable forms of data science—every application from agriculture to logistics depends on understanding temperature trends, detecting unusual conditions, and projecting short-term forecasts. This project demonstrates how to model a complete ingestion-to-insight pipeline entirely in Python, without external APIs or heavy ML libraries.

This project teaches end-to-end weather data exploration concepts where you can:

- load or auto-seed a reusable local location library for New York, Chicago, and Los Angeles,
- simulate realistic daily weather readings driven by a configurable Gaussian noise model,
- compute seasonal sine-wave temperature trends on top of per-location baselines,
- apply Z-score anomaly detection across temperature and wind speed metrics,
- flag individual readings as anomalous and record the detected metric and Z-score,
- generate 7-day short-term temperature forecasts using a pure-Python least-squares linear regression,
- classify each location's forecast trend as warming, cooling, or stable,
- render a multi-line time-series plot with history, forecast extensions, and anomaly markers,
- render a bar chart of anomaly counts per location,
- export a full forecast bundle and per-session run record to JSON,
- persist session summaries and historical reading catalogs for auditing,
- and print a readable terminal report with reading previews and artifact paths.

---

## More Projects

You can access this project and more in this separate repository:

[student-interview-prep](https://github.com/ShamShamsw/student-interview-prep.git)

---

## What You Will Build

You will build a weather data explorer that:

1. Loads location definitions from `data/locations.json` (or seeds a starter set of 3 cities).
2. Generates 14 days of daily weather readings per location using a deterministic random seed.
3. Models temperature as a per-location Gaussian baseline plus a seasonal sine-wave offset.
4. Detects anomalies in temperature and wind speed using the Z-score method with a configurable sigma threshold.
5. Annotates each flagged reading with the anomaly metric and Z-score.
6. Generates a 7-day temperature forecast per location using least-squares linear regression.
7. Labels each location's forecast trend as warming, cooling, or stable based on regression slope.
8. Saves a time-series plot of historical temperatures and dashed forecast extensions, colored by location.
9. Saves a bar chart showing how many anomalies were detected in each location.
10. Persists a full forecast bundle and run summary JSON under `data/outputs/`.
11. Maintains run and reading catalogs for history and auditing across sessions.

---

## Requirements

- Python 3.11+
- `matplotlib`

Install dependencies with:

```bash
pip install -r requirements.txt
```

---

## Example Session

```text
======================================================================
   WEATHER DATA EXPLORER WITH FORECASTS
======================================================================

Configuration:
   Project type:         weather_data_explorer
   Locations:            New York, Chicago, Los Angeles
   History days:         14
   Forecast horizon:     7 days
   Anomaly threshold:    2.0 σ
   Metrics tracked:      temperature_c, humidity_pct, wind_kph
   Time-series plot:     True
   Anomaly chart:        True
   Max readings report:  8
   Random seed:          42

Startup:
   Data directory:       data/
   Outputs directory:    data/outputs/
   Location library:     data/locations.json (loaded 0 locations)
   Run catalog:          data/runs.json (loaded 0 runs)
   Reading catalog:      data/readings.json (loaded 0 readings)
   Recent readings:      None yet

---

Session complete:
   Session ID:           20260317_203215
   Locations processed:  3
   Total readings:       42
   Anomalies detected:   3
   Forecast points:      21
   Elapsed time:         1688.23 ms

Dataset metrics: anomaly_rate=7.1% | mean_temp_c=10.4 | max_anomaly_z=2.70 | forecast_method=linear_regression

Reading previews:
   ID         | Location      | Date       | Temp (°C) | Humid (%) | Anomaly
   -----------+---------------+------------+-----------+-----------+---------
   rdg_001    | New York      | 2026-03-03 | 5.4       | 64.6      | no
   rdg_002    | New York      | 2026-03-04 | 5.9       | 54.0      | no
   rdg_003    | New York      | 2026-03-05 | 5.9       | 66.9      | no
   rdg_004    | New York      | 2026-03-06 | 10.2      | 66.9      | no
   rdg_005    | New York      | 2026-03-07 | 8.7       | 76.5      | no
   rdg_006    | New York      | 2026-03-08 | 10.2      | 54.4      | no
   rdg_007    | New York      | 2026-03-09 | 11.9      | 64.1      | no
   rdg_008    | New York      | 2026-03-10 | 11.5      | 57.1      | no

Artifacts saved:
   Run record:           data/outputs/run_20260317_203215.json
   Forecast file:        data/outputs/forecast_20260317_203215.json
   Time-series plot:     data/outputs/timeseries_20260317_203215.png
   Anomaly chart:        data/outputs/anomalies_20260317_203215.png
   Total readings logged: 42
```

---

## Run

```bash
python main.py
```
