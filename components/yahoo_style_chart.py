import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


def calculate_vwap(df: pd.DataFrame) -> pd.Series:
    """
    Calculate intraday VWAP.
    VWAP = cumulative(price * volume) / cumulative(volume)
    """
    pv = df["Close"] * df["Volume"]
    return pv.cumsum() / df["Volume"].cumsum()


def render_stock_chart(
    ticker: str,
    title: str | None = None,
    height: int = 650
):

    TIMEFRAME_CONFIG = {
        "1D":  {"period": "1d",  "interval": "5m"},
        "5D":  {"period": "5d",  "interval": "15m"},
        "1M":  {"period": "1mo", "interval": "1h"},
        "3M":  {"period": "3mo", "interval": "1d"},
        "YTD": {"period": "ytd", "interval": "1d"},
        "1Y":  {"period": "1y",  "interval": "1d"},
        "5Y":  {"period": "5y",  "interval": "1wk"},
    }

    CHART_TYPES = ["Line", "Area", "Candlestick", "OHLC"]
    INTRADAY_FRAMES = ["1D", "5D", "1M"]

    # ---------------- Controls ----------------
    col1, col2 = st.columns([3, 2])

    with col1:
        timeframe = st.radio(
            "Timeframe",
            list(TIMEFRAME_CONFIG.keys()),
            horizontal=True,
            label_visibility="collapsed"
        )

    with col2:
        chart_type = st.selectbox(
            "Chart Type",
            CHART_TYPES,
            label_visibility="collapsed"
        )

    show_vwap = st.checkbox("Show VWAP (Intraday)", value=False)

    is_intraday = timeframe in INTRADAY_FRAMES
    config = TIMEFRAME_CONFIG[timeframe]

    # ---------------- Download ----------------
    df = yf.download(
        ticker,
        period=config["period"],
        interval=config["interval"],
        progress=False,
        auto_adjust=False
    )

    if df is None or df.empty or len(df) < 2:
        st.warning("Not enough data for selected timeframe.")
        return

    # Flatten MultiIndex columns
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.reset_index()

    x_col = "Datetime" if "Datetime" in df.columns else "Date"

    # ---------------- Safe numeric conversion ----------------
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df.dropna(subset=["Close"], inplace=True)

    if len(df) < 2:
        st.warning("Data insufficient after cleaning.")
        return

    # ---------------- VWAP (Intraday only) ----------------
    if show_vwap and is_intraday and "Volume" in df.columns:
        df["VWAP"] = calculate_vwap(df)

    # ---------------- Subplots ----------------
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        row_heights=[0.72, 0.28]
    )

    # ---------------- Price ----------------
    if chart_type == "Line":
        fig.add_trace(
            go.Scatter(
                x=df[x_col],
                y=df["Close"],
                mode="lines",
                name="Price",
                line=dict(width=2)
            ),
            row=1, col=1
        )

    elif chart_type == "Area":
        fig.add_trace(
            go.Scatter(
                x=df[x_col],
                y=df["Close"],
                fill="tozeroy",
                mode="lines",
                name="Price"
            ),
            row=1, col=1
        )

    elif chart_type == "Candlestick":
        fig.add_trace(
            go.Candlestick(
                x=df[x_col],
                open=df["Open"],
                high=df["High"],
                low=df["Low"],
                close=df["Close"],
                name="Candles"
            ),
            row=1, col=1
        )

    elif chart_type == "OHLC":
        fig.add_trace(
            go.Ohlc(
                x=df[x_col],
                open=df["Open"],
                high=df["High"],
                low=df["Low"],
                close=df["Close"],
                name="OHLC"
            ),
            row=1, col=1
        )

    # ---------------- VWAP overlay ----------------
    if show_vwap and is_intraday and "VWAP" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df[x_col],
                y=df["VWAP"],
                mode="lines",
                name="VWAP",
                line=dict(color="#f1c40f", width=1.5, dash="dot")
            ),
            row=1, col=1
        )

    # ---------------- Volume ----------------
    fig.add_trace(
        go.Bar(
            x=df[x_col],
            y=df["Volume"],
            name="Volume",
            marker_color="#7f7f7f",
            opacity=0.4
        ),
        row=2, col=1
    )

    # ---------------- Last price line ----------------
    last_price = float(df["Close"].iloc[-1])

    fig.add_hline(
        y=last_price,
        line_dash="dash",
        line_color="white",
        annotation_text=f"{last_price:.2f}",
        annotation_position="top right",
        row=1, col=1
    )

    # ---------------- Layout ----------------
    fig.update_layout(
        title=title or f"{ticker} Stock Price",
        template="plotly_dark",
        hovermode="x unified",
        height=height,
        margin=dict(l=10, r=10, t=45, b=10),
        legend=dict(orientation="h", y=1.02)
    )

    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)

    # Remove weekend gaps ONLY for non-intraday
    if not is_intraday:
        fig.update_xaxes(
            rangebreaks=[dict(bounds=["sat", "mon"])]
        )

    st.plotly_chart(fig, use_container_width=True)
