from __future__ import annotations

import pandas as pd


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "Created Date" in out.columns:
        out["Created Date"] = pd.to_datetime(out["Created Date"], errors="coerce")
    if "Closed Date" in out.columns:
        out["Closed Date"] = pd.to_datetime(out["Closed Date"], errors="coerce")
    if "Borough" in out.columns:
        out["Borough"] = out["Borough"].astype(str).str.strip().replace({"nan": pd.NA})
    if "Problem (formerly Complaint Type)" in out.columns:
        out["Problem (formerly Complaint Type)"] = out["Problem (formerly Complaint Type)"].astype(str).str.strip()
    out = out.drop_duplicates(subset=[c for c in ["Unique Key"] if c in out.columns])
    return out
