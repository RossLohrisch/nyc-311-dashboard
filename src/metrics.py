from __future__ import annotations

import pandas as pd


def build_metrics(df: pd.DataFrame) -> dict[str, object]:
    return {
        "rows": len(df),
        "boroughs": df["Borough"].nunique(dropna=True) if "Borough" in df.columns else None,
        "complaints": df["Problem (formerly Complaint Type)"].nunique(dropna=True) if "Problem (formerly Complaint Type)" in df.columns else None,
        "missing_created": df["Created Date"].isna().sum() if "Created Date" in df.columns else None,
    }
