import pandas as pd

def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds financial & risk indicators to stock price data.
    Assumes data is already preprocessed.
    Safe for global markets.
    """

    # -----------------------------------
    # Step 0: Safety check
    # -----------------------------------
    if df is None or df.empty:
        return df

    df = df.copy()

    # Ensure correct sorting
    df = df.sort_values(["stock", "Date"])

    # -----------------------------------
    # Step 1: Daily Returns (%)
    # -----------------------------------
    df["daily_return_pct"] = (
        df.groupby("stock")["Close"]
        .pct_change() * 100
    )

    # ------------------------------------
    # Step 2: Moving Averages
    # ------------------------------------
    df["ma_20"] = (
        df.groupby("stock")["Close"]
        .rolling(window=20, min_periods=5)
        .mean()
        .reset_index(level=0, drop=True)
    )

    df["ma_50"] = (
        df.groupby("stock")["Close"]
        .rolling(window=50, min_periods=10)
        .mean()
        .reset_index(level=0, drop=True)
    )

    # ------------------------------------
    # Step 3: Rolling Volatility (20D)
    # ------------------------------------
    df["volatility_20"] = (
        df.groupby("stock")["daily_return_pct"]
        .rolling(window=20, min_periods=5)
        .std()
        .reset_index(level=0, drop=True)
    )

    # ------------------------------------
    # Step 4: Drawdown (%)
    # ------------------------------------
    def _drawdown(series):
        returns = series.pct_change()
        cumulative = (1 + returns).cumprod()
        rolling_max = cumulative.cummax()
        return (cumulative / rolling_max - 1) * 100

    df["drawdown_pct"] = (
        df.groupby("stock")["Close"]
        .apply(_drawdown)
        .reset_index(level=0, drop=True)
    )

    # ❗ DO NOT drop rows here
    return df
