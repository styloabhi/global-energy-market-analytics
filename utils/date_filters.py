import pandas as pd

def filter_by_start_date(df: pd.DataFrame, start_date):
    if df is None or df.empty:
        return df

    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"])

    return df[df["Date"] >= pd.to_datetime(start_date)]
