import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing

def powerbi_style_forecast(
    df: pd.DataFrame,
    horizon_days: int = 30,
    confidence: float = 0.80
) -> pd.DataFrame:
    """
    Power BI–style ETS forecast with confidence bands.
    """

    if df is None or df.empty or len(df) < 90:
        return pd.DataFrame()

    df = df.sort_values("Date")
    series = df["Close"].astype(float)

    model = ExponentialSmoothing(
        series,
        trend="add",
        seasonal="add",
        seasonal_periods=5,
        damped_trend=True
    )

    fitted = model.fit(optimized=True)

    forecast = fitted.forecast(horizon_days)

    # -----------------------------
    # Confidence interval
    # -----------------------------
    residuals = series - fitted.fittedvalues
    sigma = residuals.std()

    z = 1.28 if confidence == 0.80 else 1.96

    upper = forecast + z * sigma
    lower = forecast - z * sigma

    future_dates = pd.date_range(
        start=df["Date"].iloc[-1] + pd.Timedelta(days=1),
        periods=horizon_days,
        freq="B"
    )

    return pd.DataFrame({
        "Date": future_dates,
        "Forecast": forecast.values,
        "Upper": upper.values,
        "Lower": lower.values
    })
