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


def daily_requests(df: pd.DataFrame, min_daily_requests: int = 1) -> tuple[pd.DataFrame, bool]:
    if "Created Date" not in df.columns:
        return pd.DataFrame(), False
    out = df.dropna(subset=["Created Date"]).copy()
    out["Day"] = pd.to_datetime(out["Created Date"], errors="coerce").dt.floor("D")
    out = out.dropna(subset=["Day"])
    if out.empty:
        return pd.DataFrame(), False

    daily = out.groupby("Day", as_index=False).size().rename(columns={"size": "Requests"}).sort_values("Day")
    if daily.empty:
        return pd.DataFrame(), False

    if min_daily_requests > 1:
        daily = daily[daily["Requests"] >= min_daily_requests]
    if daily.empty:
        return pd.DataFrame(), False

    trimmed = False
    if len(daily) > 14:
        rolling = daily["Requests"].rolling(window=7, center=True, min_periods=1).mean()
        threshold = max(1, rolling.max() * 0.1)
        active = daily[rolling >= threshold].copy()
        if not active.empty:
            gaps = active["Day"].diff().dt.days.fillna(1).astype(int)
            segment_id = (gaps > 3).cumsum()
            segment_sums = active.groupby(segment_id)["Requests"].sum()
            best_segment = segment_sums.idxmax()
            active = active[segment_id == best_segment][["Day", "Requests"]].copy()
            if not active.empty:
                if len(active) < len(daily):
                    trimmed = True
                daily = active

    return daily, trimmed
