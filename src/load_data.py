from __future__ import annotations

import pandas as pd

DATA_URL = "https://data.cityofnewyork.us/api/views/erm2-nwe9/rows.csv?accessType=DOWNLOAD"


def load_data(source: str = DATA_URL, nrows: int | None = 5000) -> pd.DataFrame:
    df = pd.read_csv(source, nrows=nrows, low_memory=False)
    df.columns = [c.strip() for c in df.columns]
    return df
