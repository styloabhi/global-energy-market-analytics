import pandas as pd
import numpy as np

def calculate_kpis(df: pd.DataFrame) -> dict:
    """
    Calculates key performance & risk KPIs
    for a single stock.
    ALWAYS returns a dictionary.
    """

    # ---------------------------------
    # STEP 0: Safety guards
    # ---------------------------------
    if df is None or df.empty:
        return _empty_kpis()

    required_cols = ["Date", "Close", "High", "Low"]

    if not all(col in df.columns for col in required_cols):
        return _empty_kpis()

    # ---------------------------------
    # STEP 1: Ensure Date dtype & sort
    # ---------------------------------
    if not pd.api.types.is_datetime64_any_dtype(df["Date"]):
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    df = df.sort_values("Date")

    # ---------------------------------
    # STEP 2: Basic price metrics
    # ---------------------------------
    latest_price = df["Close"].iloc[-1]
    start_price = df["Close"].iloc[0]

    total_return_pct = ((latest_price / start_price) - 1) * 100

    # ---------------------------------
    # STEP 3: Volatility (20-day)
    # ---------------------------------
    volatility_20 = (
        df["volatility_20"].iloc[-1]
        if "volatility_20" in df.columns
        else None
    )

    # ---------------------------------
    # STEP 4: 52-week high & low
    # ---------------------------------
    high_52w = df["High"].tail(252).max()
    low_52w = df["Low"].tail(252).min()

    # ---------------------------------
    # STEP 5: CAGR (annualized return)
    # ---------------------------------
    days = (df["Date"].iloc[-1] - df["Date"].iloc[0]).days

    if days > 0:
        years = days / 365.25
        cagr = ((latest_price / start_price) ** (1 / years) - 1) * 100
    else:
        cagr = None

    # ---------------------------------
    # STEP 6: Daily returns (for risk)
    # ---------------------------------
    daily_returns = df["Close"].pct_change()

    # Win rate (% positive days)
    win_rate = (
        (daily_returns > 0).mean() * 100
        if daily_returns.notna().any()
        else None
    )

    # Downside volatility (only negative returns)
    downside_returns = daily_returns[daily_returns < 0]
    downside_vol = (
        downside_returns.std() * 100
        if not downside_returns.empty
        else None
    )

    # ---------------------------------
    # STEP 7: Max drawdown
    # ---------------------------------
    cumulative = (1 + daily_returns).cumprod()
    rolling_max = cumulative.cummax()
    drawdown = (cumulative / rolling_max - 1) * 100
    max_drawdown = drawdown.min()

    return {
        # Price & return
        "latest_price": latest_price,
        "total_return_pct": total_return_pct,
        "cagr_pct": cagr,

        # Risk
        "volatility_20": volatility_20,
        "downside_vol": downside_vol,
        "max_drawdown": max_drawdown,

        # Extremes
        "high_52w": high_52w,
        "low_52w": low_52w,

        # Behaviour
        "win_rate_pct": win_rate,
    }


def _empty_kpis() -> dict:
    """Standard empty KPI structure."""
    return {
        "latest_price": None,
        "total_return_pct": None,
        "cagr_pct": None,
        "volatility_20": None,
        "downside_vol": None,
        "max_drawdown": None,
        "high_52w": None,
        "low_52w": None,
        "win_rate_pct": None,
    }
