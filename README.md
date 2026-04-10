# NYC 311 Data Quality Dashboard

A Streamlit dashboard that explores NYC 311 service requests, highlights basic data quality issues, and turns the raw data into simple charts and summary metrics.

## What it does

- loads a local NYC 311 sample when available
- falls back to the public dataset if needed
- cleans and standardizes key fields
- shows summary metrics
- charts complaint volume over time
- breaks down complaints by borough and complaint type
- lets you filter and download the cleaned data

## Fast startup

For reviewers, the app uses a local cached sample when available so it opens quickly instead of waiting on a full remote download.

## Dataset

This project uses NYC Open Data 311 service requests:
https://data.cityofnewyork.us/api/views/erm2-nwe9/rows.csv?accessType=DOWNLOAD

## Screenshots

_Add screenshots here once the app is running._

## How to run

```bash
pip install -r requirements.txt
```

If that does not work on your system, try:

```bash
python -m pip install -r requirements.txt
```

Then run:

```bash
streamlit run app.py
```
