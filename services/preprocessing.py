import pandas as pd


def preprocess_price_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and normalize OHLC price data.
    Safe for stocks, indices, crypto, ETFs.
    """

    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()

    # ----------------------------------
    # 1️⃣ Flatten MultiIndex columns
    # ----------------------------------
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # ----------------------------------
    # 2️⃣ Ensure Date column
    # ----------------------------------
    if "Date" not in df.columns:
        return pd.DataFrame()

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # ----------------------------------
    # 3️⃣ Ensure OHLC columns exist
    # ----------------------------------
    if "Close" not in df.columns:
        return pd.DataFrame()

    for col in ["Open", "High", "Low"]:
        if col not in df.columns:
            df[col] = df["Close"]

    if "Volume" not in df.columns:
        df["Volume"] = 0

    # ----------------------------------
    # 4️⃣ Convert to numeric safely
    # ----------------------------------
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # ----------------------------------
    # 5️⃣ Drop invalid rows (minimal)
    # ----------------------------------
    df = df.dropna(subset=["Close"])

    return df
