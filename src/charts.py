from __future__ import annotations

import pandas as pd


def top_complaints(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    if "Problem (formerly Complaint Type)" not in df.columns:
        return pd.DataFrame()
    return df["Problem (formerly Complaint Type)"].value_counts(dropna=True).head(n).rename_axis("Complaint Type").reset_index(name="Count")


def borough_counts(df: pd.DataFrame) -> pd.DataFrame:
    if "Borough" not in df.columns:
        return pd.DataFrame()
    return df["Borough"].value_counts(dropna=True).rename_axis("Borough").reset_index(name="Count")


def monthly_trends(df: pd.DataFrame) -> pd.DataFrame:
    if "Created Date" not in df.columns:
        return pd.DataFrame()
    out = df.dropna(subset=["Created Date"]).copy()
    out["Month"] = out["Created Date"].dt.to_period("M").dt.to_timestamp()
    return out.groupby("Month", as_index=False).size().rename(columns={"size": "Requests"})
