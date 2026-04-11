from __future__ import annotations

import csv
import json
import time
from pathlib import Path

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

from src.clean_data import clean_data
from src.metrics import build_metrics
from src.charts import top_complaints, borough_counts, daily_requests

APP_TITLE = "NYC 311 Data Quality Dashboard"
DATA_DIR = Path("data/raw")
SAMPLE_FILE = DATA_DIR / "nyc_311_sample.csv"
FULL_FILE = DATA_DIR / "nyc_311_full.csv"
CHECKPOINT_FILE = DATA_DIR / "nyc_311_checkpoint.json"
DATASET_URL = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"
PAGE_SIZE = 50000
FULL_DATASET_ROWS = 20772175
DEFAULT_SAMPLE_ROWS = 5000
TIMEOUT = 120
MAX_RETRIES = 6
SLEEP_SECONDS = 1.0
HEADERS = {
    # "X-App-Token": "YOUR_APP_TOKEN"
}


def load_checkpoint():
    if CHECKPOINT_FILE.exists():
        with CHECKPOINT_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {"offset": 0, "total_rows": 0}


def save_checkpoint(offset, total_rows):
    CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with CHECKPOINT_FILE.open("w", encoding="utf-8") as f:
        json.dump({"offset": offset, "total_rows": total_rows}, f)


def fetch_page(offset: int, limit: int):
    params = {"$limit": limit, "$offset": offset, "$order": ":id"}
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.get(DATASET_URL, params=params, headers=HEADERS, timeout=TIMEOUT)
            if r.status_code == 429:
                retry_after = r.headers.get("Retry-After")
                wait = int(retry_after) if retry_after and retry_after.isdigit() else 15
                time.sleep(wait)
                continue
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            if attempt == MAX_RETRIES:
                raise
            time.sleep(min(2**attempt, 60))
    return []


def ensure_parent(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)


def write_rows(rows, output_file: Path, fieldnames=None):
    if not rows:
        return fieldnames
    if fieldnames is None:
        keys = set()
        for row in rows:
            keys.update(row.keys())
        fieldnames = sorted(keys)
    file_exists = output_file.exists() and output_file.stat().st_size > 0
    with output_file.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        if not file_exists:
            writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})
    return fieldnames


def load_data_file(path: Path, nrows: int | None = None) -> tuple[pd.DataFrame, str]:
    if not path.exists():
        raise FileNotFoundError(f"Missing data file: {path}")
    df = pd.read_csv(path, nrows=nrows, low_memory=False)
    df.columns = [c.strip() for c in df.columns]
    return clean_data(df), str(path)


def estimate_download_seconds(requested_rows: int | None) -> str:
    if requested_rows is None:
        return "about 10-30 minutes or longer, depending on network speed"
    if requested_rows <= 1000:
        return "about 30 seconds to a few minutes"
    if requested_rows <= 5000:
        return "about 1-5 minutes"
    if requested_rows <= 25000:
        return "about 5-15 minutes"
    return "about 10-30 minutes or longer"


def run_download(mode: str, requested_rows: int | None, total_dataset_rows: int | None = None):
    ensure_parent(FULL_FILE)
    ensure_parent(CHECKPOINT_FILE)

    checkpoint = load_checkpoint()
    offset = checkpoint.get("offset", 0)
    total_rows = checkpoint.get("total_rows", 0)
    fieldnames = None

    if FULL_FILE.exists() and FULL_FILE.stat().st_size > 0:
        with FULL_FILE.open("r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            try:
                fieldnames = next(reader)
            except StopIteration:
                fieldnames = None

    progress = st.progress(0)
    eta_placeholder = st.empty()

    # When we're downloading a fixed target, use the exact requested row count.
    # Otherwise, if we know the full dataset row count, show true percentages.
    # As a fallback, use a simple two-step progress model so huge downloads still feel discrete.
    if requested_rows is None:
        total_target_rows = total_dataset_rows
    else:
        total_target_rows = requested_rows

    start_time = time.monotonic()

    def format_eta(seconds: float | None) -> str:
        if seconds is None or seconds < 0 or seconds == float("inf"):
            return "unknown"
        seconds = int(seconds)
        hrs, rem = divmod(seconds, 3600)
        mins, secs = divmod(rem, 60)
        if hrs:
            return f"{hrs:d} hour{'s' if hrs != 1 else ''} {mins:d} minute{'s' if mins != 1 else ''}"
        if mins:
            return f"{mins:d} minute{'s' if mins != 1 else ''} {secs:d} second{'s' if secs != 1 else ''}"
        return f"{secs:d} second{'s' if secs != 1 else ''}"

    def update_progress(done_rows: int):
        elapsed = max(time.monotonic() - start_time, 0.001)
        rows_per_sec = done_rows / elapsed if done_rows > 0 else 0
        eta_seconds = None

        if total_target_rows is None:
            pct = 50 if done_rows > 0 else 0
            text = "0% complete (0 / 500,000 rows)" if pct == 0 else "50% complete"
            progress.progress(pct, text=text)
            eta_placeholder.markdown("<span class='progress-estimate'>Estimated time remaining: unknown</span>", unsafe_allow_html=True)
        else:
            pct = min(100, int((done_rows / total_target_rows) * 100))
            if rows_per_sec > 0:
                eta_seconds = max((total_target_rows - done_rows) / rows_per_sec, 0)
            progress.progress(pct, text=f"{pct}% complete ({done_rows:,} / {total_target_rows:,} rows)")
            eta_text = f"Estimated time remaining: {format_eta(eta_seconds)}" if eta_seconds is not None else "Estimated time remaining: unknown"
            eta_placeholder.markdown(f"<span class='progress-estimate'>{eta_text}</span>", unsafe_allow_html=True)

    update_progress(total_rows)

    while True:
        if requested_rows is None:
            current_limit = PAGE_SIZE
        else:
            remaining = requested_rows - total_rows
            if remaining <= 0:
                break
            current_limit = min(PAGE_SIZE, remaining)

        rows = fetch_page(offset, current_limit)
        if not rows:
            break
        fieldnames = write_rows(rows, FULL_FILE, fieldnames)
        count = len(rows)
        total_rows += count
        offset += count
        save_checkpoint(offset, total_rows)
        update_progress(total_rows)
        if count < current_limit:
            break
        time.sleep(SLEEP_SECONDS)

    if requested_rows is not None:
        update_progress(total_rows)
    else:
        progress.progress(100, text=f"Downloading data… 100% complete ({total_rows:,} / {total_target_rows:,} rows)")
        eta_placeholder.markdown("<span class='progress-estimate'>Estimated time remaining: 0 seconds</span>", unsafe_allow_html=True)
    if "status" in globals() and hasattr(status, "write"):
        status.write(f"Saved dataset to {FULL_FILE.resolve()}")
    else:
        st.info(f"Saved dataset to {FULL_FILE.resolve()}")


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, layout="wide")

    st.markdown(
        """
        <style>
        .block-container { padding-top: 1.5rem; }
        .hero {
            padding: 1.25rem 1.5rem;
            border-radius: 18px;
            background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 100%);
            color: white;
            margin-bottom: 1rem;
        }
        .hero h1 { color: white; margin-bottom: 0.25rem; }
        .hero p { color: #dbeafe; margin: 0; }
        .data-badge {
            display: inline-block;
            padding: 0.35rem 0.7rem;
            border-radius: 999px;
            background: #e0f2fe;
            color: #0f172a;
            font-size: 0.9rem;
            margin-top: 0.6rem;
        }
        .data-badge.sample { background: #fef3c7; color: #92400e; }
        .data-badge.full { background: #dcfce7; color: #166534; }
        .progress-estimate { color: #94a3b8; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="hero">
            <h1>{APP_TITLE}</h1>
            <p>A simple dashboard for turning NYC 311 service requests into something readable.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(f"Sample file path: {SAMPLE_FILE}")

    sample_exists = SAMPLE_FILE.exists()
    full_exists = FULL_FILE.exists()
    if sample_exists:
        st.warning("A local sample dataset was found, so the app will use that automatically.")
    elif full_exists:
        st.warning("A cached full dataset was found, so the app will use that automatically.")
    else:
        st.info(f"No local dataset was found. Place a sample CSV at `{SAMPLE_FILE}` or download data from the NYC Open Data API below.")

    requested_rows = None
    download_mode = None
    if sample_exists:
        data_file = SAMPLE_FILE
    elif full_exists:
        data_file = FULL_FILE
    else:
        data_file = None
        download_mode = st.radio(
            "Download mode",
            ["Small sample", "Full dataset"],
            horizontal=True,
            index=0,
            help="Choose a smaller number of rows or download the entire dataset.",
        )
        if download_mode == "Small sample":
            requested_rows = int(
                st.number_input(
                    "Rows to download",
                    min_value=1,
                    value=DEFAULT_SAMPLE_ROWS,
                    step=1000,
                )
            )
            st.caption(f"Estimated download time: {estimate_download_seconds(requested_rows)}")
        else:
            st.warning(
                "The full dataset can take a long time to download. If you only need a preview, choose Small sample instead."
            )
            st.caption("Estimated download time: about 10-30 minutes or longer depending on network speed")
        if st.button("Run download"):
            with st.spinner("Downloading data…"):
                run_download(download_mode, requested_rows, FULL_DATASET_ROWS if download_mode == "Full dataset" else None)
            st.success("Download finished. Reloading dashboard…")
            st.rerun()
            
    if data_file is None:
        st.stop()

    df, data_mode = load_data_file(data_file, nrows=DEFAULT_SAMPLE_ROWS if data_file == SAMPLE_FILE else None)

    data_label = "cached full dataset" if data_file == FULL_FILE else "sample dataset"
    badge_class = "full" if data_file == FULL_FILE else "sample"
    st.markdown(
        f'<div class="data-badge {badge_class}">Data source: {data_label}</div>',
        unsafe_allow_html=True,
    )
    st.info(
        "This dashboard uses a sample by default for fast startup. If you download the full dataset, it will be saved locally and used automatically on the next load."
    )

    st.sidebar.header("Filters")
    boroughs = sorted([b for b in df["Borough"].dropna().unique().tolist() if b != "nan"]) if "Borough" in df.columns else []
    selected_boroughs = st.sidebar.multiselect("Borough", boroughs, default=boroughs)

    if "Created Date" in df.columns:
        min_date = df["Created Date"].min()
        max_date = df["Created Date"].max()
        if pd.notna(min_date) and pd.notna(max_date):
            date_range = st.sidebar.date_input("Date range", value=(min_date.date(), max_date.date()))
        else:
            date_range = None
    else:
        date_range = None

    filtered = df.copy()
    if selected_boroughs and "Borough" in filtered.columns:
        filtered = filtered[filtered["Borough"].isin(selected_boroughs)]
    if date_range and "Created Date" in filtered.columns and isinstance(date_range, tuple) and len(date_range) == 2:
        start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        filtered = filtered[(filtered["Created Date"] >= start) & (filtered["Created Date"] <= end + pd.Timedelta(days=1))]

    metrics = build_metrics(filtered)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows", f"{metrics['rows']:,}")
    c2.metric("Boroughs", metrics["boroughs"] if metrics["boroughs"] is not None else "—")
    c3.metric("Complaint types", metrics["complaints"] if metrics["complaints"] is not None else "—")
    c4.metric("Missing created dates", metrics["missing_created"] if metrics["missing_created"] is not None else "—")

    left, right = st.columns(2)
    with left:
        st.subheader("Top complaint types")
        top = top_complaints(filtered, 10)
        if not top.empty:
            fig = px.bar(top, x="Count", y="Complaint Type", orientation="h", height=420)
            fig.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No complaint type data available.")

    with right:
        st.subheader("Requests by borough")
        borough_df = borough_counts(filtered)
        if not borough_df.empty:
            fig = px.bar(borough_df, x="Borough", y="Count", height=420)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No borough data available.")

    st.subheader("Daily requests over time")
    daily, trimmed = daily_requests(filtered, min_daily_requests=1)
    if not daily.empty:
        if trimmed:
            st.caption("Showing the main activity cluster only, since the full date span is mostly sparse.")
        fig = px.bar(daily, x="Day", y="Requests", height=400)
        fig.update_yaxes(rangemode="tozero")
        fig.update_xaxes(range=[daily["Day"].min(), daily["Day"].max()])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No date data available after trimming sparse days.")

    st.subheader("Sample data")
    st.dataframe(filtered.head(25), use_container_width=True)

    st.download_button(
        "Download filtered data as CSV",
        filtered.to_csv(index=False).encode("utf-8"),
        file_name="nyc_311_filtered.csv",
        mime="text/csv",
    )


if __name__ == "__main__":
    main()
