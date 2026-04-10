from __future__ import annotations

import pandas as pd


def top_complaints(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    complaint_col = (
        "Problem (formerly Complaint Type)"
        if "Problem (formerly Complaint Type)" in df.columns
        else ("complaint_type" if "complaint_type" in df.columns else None)
    )
    if not complaint_col:
        return pd.DataFrame()
    return df[complaint_col].value_counts(dropna=True).head(n).rename_axis("Complaint Type").reset_index(name="Count")


def borough_counts(df: pd.DataFrame) -> pd.DataFrame:
    borough_col = "Borough" if "Borough" in df.columns else ("borough" if "borough" in df.columns else None)
    if not borough_col:
        return pd.DataFrame()
    return df[borough_col].value_counts(dropna=True).rename_axis("Borough").reset_index(name="Count")


def daily_requests(df: pd.DataFrame, min_daily_requests: int = 1) -> tuple[pd.DataFrame, bool]:
    created_col = "Created Date" if "Created Date" in df.columns else ("created_date" if "created_date" in df.columns else None)
    if not created_col:
        return pd.DataFrame(), False
    out = df.dropna(subset=[created_col]).copy()
    out[created_col] = pd.to_datetime(out[created_col], errors="coerce")
    out = out.dropna(subset=[created_col])
    if out.empty:
        return pd.DataFrame(), False

    out["Day"] = out[created_col].dt.floor("D")
    daily = out.groupby("Day", as_index=False).size().rename(columns={"size": "Requests"}).sort_values("Day")
    if daily.empty:
        return pd.DataFrame(), False

    if min_daily_requests > 1:
        daily = daily[daily["Requests"] >= min_daily_requests]
    if daily.empty:
        return pd.DataFrame(), False

    trimmed = False
    # Focus the chart on the dense activity cluster when the date span is very wide.
    # This keeps the plot readable instead of stretching a small cluster across a huge empty range.
    if len(daily) > 14:
        rolling = daily["Requests"].rolling(window=7, center=True, min_periods=1).mean()
        threshold = max(1, rolling.max() * 0.1)
        active = daily[rolling >= threshold].copy()
        if not active.empty:
            gaps = active["Day"].diff().dt.days.fillna(1).astype(int)
            segment_id = (gaps > 3).cumsum()
            segment_sizes = active.groupby(segment_id)["Requests"].sum()
            best_segment = segment_sizes.idxmax()
            active = active[segment_id == best_segment][["Day", "Requests"]].copy()
            if not active.empty:
                if len(active) < len(daily):
                    trimmed = True
                daily = active

    return daily, trimmed
