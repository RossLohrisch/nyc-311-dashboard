# NYC 311 Data Quality Dashboard

A Streamlit dashboard that explores NYC 311 service requests, highlights basic data quality issues, and turns the raw data into simple charts and summary metrics.

Use a sample CSV for fast startup, or download data from within the app when you want the full dataset.

## Quick start

1. Put a sample CSV at `data/raw/nyc_311_sample.csv` **or** open the dashboard and choose a download mode.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
streamlit run app.py
```

4. If no local data exists, choose **Small sample** or **Full dataset**, then click **Run download**.

## What it does

- loads a local NYC 311 sample CSV
- cleans and standardizes key fields
- shows summary metrics
- charts complaint volume over time
- breaks down complaints by borough and complaint type
- lets you filter and download the cleaned data

## Sample + full dataset workflow

This project now prefers a **local sample file first**, then the cached full dataset, and only then lets you download data from the API if no local file is available.

Expected file paths:

```text
data/raw/nyc_311_sample.csv
data/raw/nyc_311_full.csv
```

### Priority order

1. If `data/raw/nyc_311_sample.csv` exists, the app uses it.
2. Otherwise, if `data/raw/nyc_311_full.csv` exists, the app uses the cached full file.
3. Otherwise, the dashboard shows download options so you can fetch data from NYC Open Data.

### Why a sample file?

The full NYC 311 dataset is large and can be slow to download at startup. Using a sample keeps the app responsive and avoids long waits.

### How to use the sample

1. Download or generate a CSV subset
2. Save it at `data/raw/nyc_311_sample.csv`
3. Run the app with:

```bash
streamlit run app.py
```

### How to download data from the dashboard

If no local sample exists, the dashboard shows:
- a choice between **Small sample** and **Full dataset**
- a row count input if you choose the smaller sample
- a **Run download** button

When you click **Run download**:
- the app downloads data from NYC Open Data
- it saves the result locally
- the dashboard reloads and uses the downloaded file immediately

## Using the full dataset instead

If you want the full dataset, choose **Full dataset** in the dashboard download flow and click **Run download**.

The downloaded file is cached locally at `data/raw/nyc_311_full.csv`, and future launches will prefer the sample first if it exists, otherwise the cached full file.

A good approach is to:
- keep the raw full dataset outside the repo if it’s large
- preprocess it into a smaller cache/sample when possible
- only use the full download when you really need it

## Dataset

NYC Open Data 311 service requests:
https://data.cityofnewyork.us/api/views/erm2-nwe9/rows.csv?accessType=DOWNLOAD

## Screenshots

_Add screenshots here once the app is running._

## How to run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Notes

This is intended to be a portfolio-style project: small enough to finish, but polished enough to show analysis, cleanup, and presentation.
