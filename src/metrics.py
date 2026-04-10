from __future__ import annotations

import pandas as pd


def build_metrics(df: pd.DataFrame) -> dict[str, object]:
    borough_col = "Borough" if "Borough" in df.columns else ("borough" if "borough" in df.columns else None)
    complaint_col = (
        "Problem (formerly Complaint Type)"
        if "Problem (formerly Complaint Type)" in df.columns
        else ("complaint_type" if "complaint_type" in df.columns else None)
    )
    created_col = "Created Date" if "Created Date" in df.columns else ("created_date" if "created_date" in df.columns else None)

    return {
        "rows": len(df),
        "boroughs": df[borough_col].nunique(dropna=True) if borough_col else None,
        "complaints": df[complaint_col].nunique(dropna=True) if complaint_col else None,
        "missing_created": df[created_col].isna().sum() if created_col else None,
    }
