from __future__ import annotations

from pathlib import Path
import pandas as pd
import streamlit as st

DATA_URL = "https://data.cityofnewyork.us/api/views/erm2-nwe9/rows.csv?accessType=DOWNLOAD"
LOCAL_SAMPLE = Path("data/raw/nyc_311_sample.csv")
FULL_DATA_CACHE = Path("data/raw/nyc_311_full.csv")


def _read_csv(path: Path, nrows: int | None = None) -> pd.DataFrame:
    return pd.read_csv(path, nrows=nrows, low_memory=False)


def load_data(
    source: str | Path | None = None,
    nrows: int | None = 5000,
    allow_remote_fallback: bool = False,
) -> tuple[pd.DataFrame, str]:
    """Prefer a sample dataset first, then the cached full dataset, and optionally fall back to the public CSV."""
    sample_path = Path(source) if source is not None else LOCAL_SAMPLE
    sample_path.parent.mkdir(parents=True, exist_ok=True)

    if sample_path.exists():
        try:
            df = _read_csv(sample_path, nrows=nrows)
            mode = f"local sample: {sample_path}"
        except Exception as exc:
            raise RuntimeError(
                f"The sample file at {sample_path} exists but could not be read. "
                f"Replace it with a valid CSV, or remove it to try the cached full dataset. ({exc.__class__.__name__})"
            ) from exc
    elif FULL_DATA_CACHE.exists():
        try:
            df = _read_csv(FULL_DATA_CACHE, nrows=nrows)
            mode = f"cached full dataset: {FULL_DATA_CACHE}"
        except Exception as exc:
            raise RuntimeError(
                f"The cached full dataset at {FULL_DATA_CACHE} exists but could not be read. "
                f"Delete it and try again, or replace it with a valid CSV. ({exc.__class__.__name__})"
            ) from exc
    elif allow_remote_fallback:
        progress = st.progress(0, text="Starting download from NYC Open Data…")
        status = st.empty()
        try:
            status.write("Downloading full NYC 311 dataset…")
            progress.progress(20, text="Downloading full NYC 311 dataset…")
            df = pd.read_csv(DATA_URL, low_memory=False)
            progress.progress(80, text="Saving downloaded dataset locally…")
            df.to_csv(FULL_DATA_CACHE, index=False)
            progress.progress(100, text="Download complete")
            status.write(f"Saved full dataset to {FULL_DATA_CACHE}")
            mode = f"remote fetch cached to: {FULL_DATA_CACHE}"
        except Exception as exc:
            progress.empty()
            status.empty()
            raise RuntimeError(
                f"Unable to load the full NYC 311 dataset from the remote source. ({exc.__class__.__name__})"
            ) from exc
    else:
        raise RuntimeError(
            f"No dataset found. Put a sample CSV at {sample_path}, or enable the remote fallback in the app to download the full dataset on demand."
        )
    df.columns = [c.strip() for c in df.columns]
    return df, mode
