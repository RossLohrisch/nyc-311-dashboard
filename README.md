# NYC 311 Data Quality Dashboard

An interactive Streamlit dashboard that turns NYC 311 service requests into a clean, readable portfolio project.

## Why this project matters

NYC 311 data is messy, high-volume, and full of real-world inconsistency. This dashboard shows that I can:

- clean and standardize raw public data
- surface data quality issues clearly
- build a useful exploratory dashboard from scratch
- make the result easy for non-technical viewers to understand

## Live demo

_Add your deployed Streamlit link here._

## Features

- loads a local NYC 311 sample when available for fast startup
- falls back to the public dataset if needed
- cleans and standardizes key fields
- shows summary metrics
- charts complaint volume over time
- breaks down complaints by borough and complaint type
- lets users filter and download the cleaned data

## What the dashboard shows

- overall row counts and coverage
- borough-level distribution
- most common complaint types
- request volume over time
- a cleaned sample table for quick inspection

## Screenshots

Add 2-4 screenshots here once the app is deployed or running locally.

Suggested shots:

- full dashboard overview
- filter state
- one chart close-up
- data table / download section

## Dataset

This project uses NYC Open Data 311 service requests:

<https://data.cityofnewyork.us/api/views/erm2-nwe9/rows.csv?accessType=DOWNLOAD>

## How to run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Portfolio polish checklist

Before featuring this project, I’d recommend:

- add a deployed demo link
- add screenshots or a short GIF
- replace placeholder text with a short project story
- mention the most interesting insight you found
- make sure the app opens quickly and behaves well with filters

## Tech stack

- Python
- Streamlit
- Pandas
- Plotly
