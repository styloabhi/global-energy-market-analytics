import yfinance as yf
import pandas as pd


def load_fundamentals(ticker: str, frequency: str = "Yearly") -> pd.DataFrame:
    """
    Load and normalize revenue & net profit data.
    """

    stock = yf.Ticker(ticker)

    if frequency == "Quarterly":
        fin = stock.quarterly_financials
    else:
        fin = stock.financials

    if fin is None or fin.empty:
        return pd.DataFrame()

    fin = fin.loc[fin.index.intersection(["Total Revenue", "Net Income"])]

    if fin.empty:
        return pd.DataFrame()

    df = fin.T.reset_index()
    df.rename(columns={"index": "Period"}, inplace=True)

    df["Period"] = pd.to_datetime(df["Period"], errors="coerce")
    df = df.sort_values("Period")

    df.rename(
        columns={
            "Total Revenue": "Revenue",
            "Net Income": "Net Profit",
        },
        inplace=True
    )

    # 🔹 FIX PERIOD LABELS
    if frequency == "Quarterly":
        df["Period_Label"] = (
            df["Period"].dt.year.astype(str)
            + " Q"
            + df["Period"].dt.quarter.astype(str)
        )
    else:
        df["Period_Label"] = df["Period"].dt.year.astype(str)

    # Remove duplicates caused by fiscal offsets
    df = df.drop_duplicates(subset=["Period_Label"])

    return df
