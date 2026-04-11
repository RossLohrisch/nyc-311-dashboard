# NYC 311 Data Quality Dashboard

An interactive Streamlit dashboard that turns NYC 311 service requests into a clean, readable project.

## Why this project matters

NYC 311 data is messy, high-volume, and full of real-world inconsistency. This dashboard turns that raw public data into something readable, usable, and easy to explore.

## Live demo

https://nyc-311-dashboard-6agf3rq3kcnd3dhbnx2hwf.streamlit.app/

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

<img width="1910" height="864" alt="image" src="https://github.com/user-attachments/assets/f137dbb3-9704-4ad0-8e78-ba16fdfa4b15" />
<img width="721" height="351" alt="image" src="https://github.com/user-attachments/assets/f9116551-24d6-4e3e-9e5c-53388f466c9e" />
<img width="731" height="352" alt="image" src="https://github.com/user-attachments/assets/a93178cf-799e-4acc-9f27-609a736ecc48" />


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
```

If that does not work, try:

```bash
python -m pip install -r requirements.txt
```

Then run:

```bash
streamlit run app.py
```

## Tech stack

- Python
- Streamlit
- Pandas
- Plotly
