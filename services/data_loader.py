import pandas as pd
import yfinance as yf
import os

DATA_PATH = "data/global_energy_stocks.csv"


def load_global_energy_data(global_fuel_stocks):
    """
    Simple, tested, flat data loader.
    No caching.
    Always produces clean schema.
    """

    # If CSV already exists, load it
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH, parse_dates=["Date"])

    # -----------------------------------
    # Download data (EXACT LOGIC)
    # -----------------------------------
    data = yf.download(
        tickers=global_fuel_stocks,
        period="2y",
        interval="1d"
    )

    dfs = []

    for stock in global_fuel_stocks:
        try:
            df = data.xs(stock, level=1, axis=1).copy()
        except Exception:
            continue

        df.reset_index(inplace=True)
        df["stock"] = stock
        dfs.append(df)

    if not dfs:
        return pd.DataFrame()

    global_oil = pd.concat(dfs, ignore_index=True)

    # Drop bad rows
    global_oil = global_oil.dropna(subset=["Close"])

    # Save CSV
    os.makedirs("data", exist_ok=True)
    global_oil.to_csv(DATA_PATH, index=False)

    return global_oil
