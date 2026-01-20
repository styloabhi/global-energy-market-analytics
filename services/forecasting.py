import numpy as np
import pandas as pd

def powerbi_style_forecast(
    df: pd.DataFrame,
    horizon_days: int = 30,
    alpha: float = 0.3,
    beta: float = 0.1,
    confidence: float = 0.80
) -> pd.DataFrame:

    if df is None or df.empty or len(df) < 60:
        return pd.DataFrame()

    df = df.sort_values("Date")
    y = df["Close"].astype(float).values

    # Initialize
    level = y[0]
    trend = y[1] - y[0]

    levels = []
    trends = []

    for i in range(len(y)):
        prev_level = level
        level = alpha * y[i] + (1 - alpha) * (level + trend)
        trend = beta * (level - prev_level) + (1 - beta) * trend
        levels.append(level)
        trends.append(trend)

    # Forecast
    forecast = [
        level + (i + 1) * trend
        for i in range(horizon_days)
    ]

    # Confidence band (simple, realistic)
    residuals = y - np.array(levels)
    sigma = residuals.std()

    z = 1.28 if confidence == 0.80 else 1.96

    upper = np.array(forecast) + z * sigma
    lower = np.array(forecast) - z * sigma

    future_dates = pd.date_range(
        start=df["Date"].iloc[-1] + pd.Timedelta(days=1),
        periods=horizon_days,
        freq="B"
    )

    return pd.DataFrame({
        "Date": future_dates,
        "Forecast": forecast,
        "Upper": upper,
        "Lower": lower
    })
