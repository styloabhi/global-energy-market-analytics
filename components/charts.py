import pandas as pd
import plotly.graph_objects as go




def aggregate_volume_by_range(df):
    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"])

    days = (df["Date"].max() - df["Date"].min()).days

    if days <= 30:
        return df, "Daily", df["Volume"].mean()

    elif days <= 180:
        agg = (
            df.resample("W", on="Date")
            .agg(
                Volume=("Volume", "mean")  # 🔥 avg daily volume
            )
            .reset_index()
        )
        return agg, "Weekly", df["Volume"].mean()

    else:
        agg = (
            df.resample("ME", on="Date")
            .agg(
                Volume=("Volume", "mean")  # 🔥 avg daily volume
            )
            .reset_index()
        )
        return agg, "Monthly", df["Volume"].mean()





def price_ma_chart(df: pd.DataFrame, stock: str):
    """
    Price + moving average chart.
    Returns Plotly figure or None.
    """

    # -------------------------------
    # Safety guards
    # -------------------------------
    if df is None or df.empty:
        return None

    required_cols = ["Date", "Close"]

    if not all(col in df.columns for col in required_cols):
        return None

    # -------------------------------
    # Ensure Date dtype
    # -------------------------------
    if not pd.api.types.is_datetime64_any_dtype(df["Date"]):
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    df = df.sort_values("Date")
 
    fig = go.Figure()

    # Price line
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["Close"],
            mode="lines",
            name="Close Price"
        )
    )

    # Moving averages (if present)
    for ma in ["ma_20", "ma_50", "ma_200"]:
        if ma in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df["Date"],
                    y=df[ma],
                    mode="lines",
                    name=ma.upper()
                )
            )

    fig.update_layout(
        title=f"{stock} Price Trend",
        xaxis_title="Date",
        yaxis_title="Price",
        template="plotly_dark"
    )

    return fig




def volume_chart(df: pd.DataFrame):
    if df is None or df.empty or "Volume" not in df.columns:
        return None

    agg_df, freq_label, overall_avg = aggregate_volume_by_range(df)
   
    fig = go.Figure()

    # Bars
    fig.add_bar(
        x=agg_df["Date"],
        y=agg_df["Volume"],
        name=f"{freq_label} Avg Volume",
        marker_color="#00B4D8"
    )

    # Average reference line
    fig.add_trace(
        go.Scatter(
            x=agg_df["Date"],
            y=[overall_avg] * len(agg_df),
            mode="lines",
            name="Overall Avg Volume",
            line=dict(color="#E74C3C", dash="dash")
        )
    )

    fig.update_layout(
        title=f"Trading Volume ({freq_label} – Avg per Trading Day)",
        xaxis_title="Date",
        yaxis_title="Volume",
        template="plotly_dark",
        height=360
    )

    return fig





def returns_chart(df: pd.DataFrame):
    """
    Daily returns chart.
    """

    if df is None or df.empty or "Close" not in df.columns:
        return None

    returns = df["Close"].pct_change()
    fig = go.Figure(
        go.Scatter(
            x=df["Date"],
            y=returns,
            mode="lines",
            name="Daily Returns"
        )
    )

    fig.update_layout(
        title="Daily Returns",
        xaxis_title="Date",
        yaxis_title="Returns",
        template="plotly_dark"
    )

    return fig





def forecast_chart(df, forecast_df, stock):
    if df.empty or forecast_df.empty:
        return None

    fig = go.Figure()

    # Historical price
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["Close"],
            mode="lines",
            name="Historical Price",
            line=dict(color="#4C78A8")
        )
    )

    # Confidence band
    fig.add_trace(
        go.Scatter(
            x=forecast_df["Date"],
            y=forecast_df["Upper"],
            mode="lines",
            line=dict(width=0),
            showlegend=False
        )
    )

    fig.add_trace(
        go.Scatter(
            x=forecast_df["Date"],
            y=forecast_df["Lower"],
            mode="lines",
            fill="tonexty",
            fillcolor="rgba(255, 99, 71, 0.25)",
            line=dict(width=0),
            name="Forecast Range (80%)"
        )
    )

    # Forecast line
    fig.add_trace(
        go.Scatter(
            x=forecast_df["Date"],
            y=forecast_df["Forecast"],
            mode="lines",
            name="Forecast (Trend)",
            line=dict(color="tomato", dash="dash")
        )
    )

    fig.update_layout(
        title=f"{stock} — Forecast with Confidence Range",
        xaxis_title="Date",
        yaxis_title="Price",
        template="plotly_dark",
        height=500
    )

    return fig





def drawdown_chart(df: pd.DataFrame):
    """
    Drawdown (%) over time chart.
    """

    if df is None or df.empty or "drawdown_pct" not in df.columns:
        return None

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["drawdown_pct"],
            mode="lines",
            name="Drawdown (%)",
            line=dict(color="#E74C3C")
        )
    )

    fig.update_layout(
        title="Drawdown Over Time (%)",
        xaxis_title="Date",
        yaxis_title="Drawdown (%)",
        template="plotly_dark",
        yaxis=dict(ticksuffix="%")
    )

    return fig


def normalized_comparison_chart(df: pd.DataFrame):
    """
    Compare multiple stocks by normalizing prices to 100
    at the selected start date.
    """

    if df is None or df.empty:
        return None

    required_cols = ["Date", "Close", "stock"]
    if not all(col in df.columns for col in required_cols):
        return None

    df = df.copy()

    # Ensure Date is datetime
    if not pd.api.types.is_datetime64_any_dtype(df["Date"]):
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    df = df.sort_values(["stock", "Date"])

    fig = go.Figure()

    for stock, g in df.groupby("stock"):
        if g.empty:
            continue

        base_price = g["Close"].iloc[0]
        if base_price == 0 or pd.isna(base_price):
            continue

        normalized_price = (g["Close"] / base_price) * 100

        fig.add_trace(
            go.Scatter(
                x=g["Date"],
                y=normalized_price,
                mode="lines",
                name=stock
            )
        )

    fig.update_layout(
        title="Peer Comparison (Normalized Performance)",
        xaxis_title="Date",
        yaxis_title="Indexed Price (Base = 100)",
        template="plotly_dark",
        legend_title="Stock",
        height=450
    )

    return fig


def revenue_profit_chart(df: pd.DataFrame, stock: str, frequency: str):

    if df is None or df.empty:
        return None

    fig = go.Figure()

    fig.add_bar(
        x=df["Period_Label"],
        y=df["Revenue"],
        name="Revenue",
        marker_color="#636EFA"
    )

    fig.add_bar(
        x=df["Period_Label"],
        y=df["Net Profit"],
        name="Net Profit",
        marker_color="#EF553B"
    )

    fig.update_layout(
        title=f"{stock} — Revenue vs Net Profit ({frequency})",
        barmode="group",
        xaxis_title="Period",
        yaxis_title="Amount",
        template="plotly_dark",
        height=420
    )
    fig.update_layout(
    title=f"{stock} — Revenue vs Net Profit ({frequency})",
    annotations=[
        dict(
            text="Note: Negative profit indicates quarterly loss",
            xref="paper", yref="paper",
            x=0, y=1.08,
            showarrow=False,
            font=dict(size=11, color="gray")
        )
    ]
)


    return fig

