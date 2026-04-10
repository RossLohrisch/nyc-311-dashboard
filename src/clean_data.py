from __future__ import annotations

import pandas as pd


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    rename_map = {
        "created_date": "Created Date",
        "closed_date": "Closed Date",
        "borough": "Borough",
        "complaint_type": "Problem (formerly Complaint Type)",
        "problem": "Problem (formerly Complaint Type)",
        "complaint": "Problem (formerly Complaint Type)",
        "unique_key": "Unique Key",
    }
    normalized_cols = {c.lower().strip(): c for c in out.columns}
    for src, dest in rename_map.items():
        if src in normalized_cols and dest not in out.columns:
            out = out.rename(columns={normalized_cols[src]: dest})

    if "Created Date" in out.columns:
        out["Created Date"] = pd.to_datetime(out["Created Date"], errors="coerce", utc=True).dt.tz_convert(None)
    if "Closed Date" in out.columns:
        out["Closed Date"] = pd.to_datetime(out["Closed Date"], errors="coerce", utc=True).dt.tz_convert(None)
    if "Borough" in out.columns:
        out["Borough"] = out["Borough"].astype(str).str.strip().replace({"nan": pd.NA})
    if "Problem (formerly Complaint Type)" in out.columns:
        out["Problem (formerly Complaint Type)"] = out["Problem (formerly Complaint Type)"].astype(str).str.strip()
    dedupe_cols = [c for c in ["Unique Key"] if c in out.columns]
    if dedupe_cols:
        out = out.drop_duplicates(subset=dedupe_cols)
    return out
