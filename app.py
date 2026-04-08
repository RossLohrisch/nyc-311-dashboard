from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.load_data import load_data
from src.clean_data import clean_data
from src.metrics import build_metrics
from src.charts import top_complaints, borough_counts, monthly_trends

APP_TITLE = "NYC 311 Data Quality Dashboard"


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
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class=\"hero\">
            <h1>{APP_TITLE}</h1>
            <p>A simple dashboard for turning NYC 311 service requests into something readable.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    @st.cache_data(show_spinner=True)
    def cached_load() -> pd.DataFrame:
        return clean_data(load_data())

    df = cached_load()

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

    st.subheader("Requests over time")
    monthly = monthly_trends(filtered)
    if not monthly.empty:
        fig = px.line(monthly, x="Month", y="Requests", markers=True, height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No date data available.")

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
