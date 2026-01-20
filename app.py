import pandas as pd
import streamlit as st
import yfinance as yf
# =====================================================
# IMPORTS
# =====================================================

from data.universe import get_all_tickers, get_ticker_name_map

from services.data_loader import load_global_energy_data
from services.preprocessing import preprocess_price_data
from services.indicators import add_indicators
from services.forecasting import powerbi_style_forecast
from services.live_price import get_live_price_snapshot
from services.fundamentals import load_fundamentals
from components.metrics import calculate_kpis
from components.charts import (
    price_ma_chart,
    volume_chart,
    returns_chart,
    forecast_chart,
    drawdown_chart,
    revenue_profit_chart,
    normalized_comparison_chart,
)
from components.yahoo_style_chart import render_stock_chart
from auth.login import login_page, logout_button
from utils.helpers import format_number, format_percentage
from utils.date_filters import filter_by_start_date



# ======================================================='
# login 
# =======================================================
# ----------------sesssion unit------------------
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# ---------if not logged in -> show login page only
if not st.session_state["logged_in"]:
    login_page()
    st.stop()

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Global Energy Stock Analytics",
    page_icon="🌍",
    layout="wide",
)

st.title("🌍 Global Energy Market Analytics Dashboard")


# =====================================================
# SIDEBAR – STOCK SELECTION
# =====================================================
logout_button()
st.sidebar.header("Stock Selection")

ticker_name_map = get_ticker_name_map()
all_tickers = sorted(get_all_tickers())

# ➕ Add custom option
all_tickers_with_other = all_tickers + ["OTHER"]

selected_option = st.sidebar.selectbox(
    "Select Global Energy Stock",
    options=all_tickers_with_other,
    format_func=lambda x: (
        "➕ Other (Custom Ticker)"
        if x == "OTHER"
        else f"{x} — {ticker_name_map.get(x, x)}"
    ),
)
if selected_option == "OTHER":
    custom_ticker = st.sidebar.text_input(
        "Enter Yahoo Finance Ticker",
        placeholder="e.g. AAPL, TSLA, TCS.NS, BTC-USD"
    )
    selected_stock = custom_ticker.upper().strip() if custom_ticker else None
else:
    selected_stock = selected_option

if not selected_stock:
    st.info("Please select a stock or enter a custom ticker.")
    st.stop()

# 👉 Show selected stock in bold
display_name = ticker_name_map.get(selected_stock, "Custom Ticker")

st.sidebar.markdown(
    f"""
    <div style="margin-top:10px; font-size:16px;">
        <b>{display_name}</b>
        <br>
        <span style="color:gray; font-size:13px;">({selected_stock})</span>
    </div>
    """,
    unsafe_allow_html=True
)
is_custom_ticker = selected_stock not in all_tickers


# =====================================================
# LOAD PRICE DATA
# =====================================================

if is_custom_ticker:
    df = yf.download(
        selected_stock,
        period="5y",
        interval="1d",
        progress=False,
        auto_adjust=False
    )

    if df is None or df.empty:
        st.error("Invalid or unsupported ticker.")
        st.stop()

    df = df.reset_index()
    df["stock"] = selected_stock
else:
    df = load_global_energy_data(all_tickers)

    if df is None or df.empty:
        st.error("No data available. Please check the data source.")
        st.stop()

    df = df[df["stock"] == selected_stock]


df = preprocess_price_data(df)
df = add_indicators(df)

if df.empty:
    st.warning("No usable data after preprocessing.")
    st.stop()


# =====================================================
# KPIs
# =====================================================

kpis = calculate_kpis(df)


# =====================================================
# TABS
# =====================================================

tabs = st.tabs([
    "📈 Overview",
    "📊 Performance",
    "⚠️ Risk",
    "🔁 Peer Comparison",
    "📄 Fundamentals",
    "🔮 Forecast",
    "📝 Notes",
    "🗂 Data",
])



# =====================================================
# 📈 OVERVIEW TAB
# =====================================================

with tabs[0]:


    live = get_live_price_snapshot(selected_stock)

    col1, col2, col3, col4, col5 = st.columns(5)

    if live:
        col1.metric(
            "Live Price",
            format_number(live["current_price"]),
            f"{live['pct_change']:.2f}%"
        )
    else:
        col1.metric("Live Price", "N/A")

    col2.metric("Total Return", format_percentage(kpis["total_return_pct"]))
    col3.metric("CAGR", format_percentage(kpis["cagr_pct"]))
    col4.metric("52W High", format_number(kpis["high_52w"]))
    col5.metric("52W Low", format_number(kpis["low_52w"]))

    st.divider()

    st.subheader(f"{selected_stock} — Price Overview")

    # 🔥 Yahoo-style chart
    render_stock_chart(
        ticker=selected_stock,
        title=f"{selected_stock} Stock Price"
    )

    st.divider()    

    fig_price = price_ma_chart(df, selected_stock)
    if fig_price:
        st.plotly_chart(fig_price, use_container_width=True)
    st.divider()
    
    start_date = st.date_input(
    "Start Date",
    value=df["Date"].min().date(),
    min_value=df["Date"].min().date(),
    max_value=df["Date"].max().date(),
    key="overview_start_date")

    filtered_df = filter_by_start_date(df, start_date)

    

    fig_volume = volume_chart(filtered_df)
    if fig_volume:
        st.plotly_chart(fig_volume, use_container_width=True)

# =====================================================
# 📊 PERFORMANCE TAB
# =====================================================

with tabs[1]:

    col1, col2, col3 = st.columns(3)

    col1.metric("CAGR", format_percentage(kpis["cagr_pct"]))
    col2.metric("Win Rate", format_percentage(kpis["win_rate_pct"]))
    col3.metric("Volatility (20D)", format_number(kpis["volatility_20"]))

    st.divider()

    fig_returns = returns_chart(df)
    if fig_returns:
        st.plotly_chart(fig_returns, use_container_width=True)

# =====================================================
# ⚠️ RISK TAB
# =====================================================

with tabs[2]:

    col1, col2 = st.columns(2)

    col1.metric("Max Drawdown", format_percentage(kpis["max_drawdown"]))
    col2.metric("Downside Volatility", format_number(kpis["downside_vol"]))

    st.divider()

    fig_dd = drawdown_chart(df)
    if fig_dd:
        st.plotly_chart(fig_dd, use_container_width=True)






# =====================================================
# 📄 FUNDAMENTALS TAB
# =====================================================

with tabs[4]:

    st.subheader("Company Fundamentals")

    frequency = st.radio(
        "Reporting Frequency",
        ["Quarterly", "Yearly"],
        horizontal=True
    )

    fin_df = load_fundamentals(selected_stock, frequency)

    if fin_df.empty:
        st.warning("Fundamental data not available.")
    else:
        fig_fund = revenue_profit_chart(
            fin_df,
            selected_stock,
            frequency
        )
        
        st.plotly_chart(fig_fund, use_container_width=True)
        st.caption(
    "Financial data availability depends on company reporting standards. "
    "Some periods may be unavailable for certain stocks."
        )



# =====================================================
# 🔮 FORECAST TAB
# =====================================================

with tabs[5]:

    st.info(
        "Forecast uses exponential smoothing (Power BI–style trend).\n"
        "For analytical exploration only."
    )

    forecast_df = powerbi_style_forecast(df, horizon_days=30)
    fig_forecast = forecast_chart(df, forecast_df, selected_stock)

    if fig_forecast:
        st.plotly_chart(fig_forecast, use_container_width=True)


# =====================================================
# 🗂 DATA TAB
# =====================================================

with tabs[7]:

    st.dataframe(df, use_container_width=True)

    st.download_button(
        "⬇️ Download CSV",
        df.to_csv(index=False),
        file_name=f"{selected_stock}_data.csv",
        mime="text/csv",
    )


# =====================================================
# 📝 NOTES TAB
# =====================================================

with tabs[6]:

    st.subheader("📘 Dashboard Notes & Methodology")

    st.markdown("""
    ### 🔍 What This Dashboard Shows
    This dashboard provides **price, performance, risk, peer comparison, fundamentals, and forecast analysis**
    for global energy stocks and user-defined tickers.

    It is designed for **analytical learning and market understanding**, not for trading execution.
    """)

    st.divider()

    st.markdown("""
    ### 📊 Data Source
    - Market data is fetched using **public financial APIs**
    - Historical prices include **Open, High, Low, Close, Volume (OHLCV)**
    - Live prices are fetched separately for near real-time snapshots

    **Why APIs instead of web scraping?**
    - Financial data is delivered via JavaScript & APIs
    - HTML scraping is unstable and unreliable
    - APIs provide structured, consistent data
    """)

    st.divider()

    st.markdown("""
    ### 📈 Key Metrics Explained

    **Total Return (%)**  
    Measures total price appreciation from the start to the latest date.

    **CAGR (Compound Annual Growth Rate)**  
    Shows annualized growth rate over the holding period.

    **Volatility (20D)**  
    Measures daily price fluctuation risk over 20 trading days.

    **Drawdown (%)**  
    Maximum fall from the peak price — indicates downside risk.

    **VWAP (Volume Weighted Average Price)**  
    Shows the average traded price weighted by volume (intraday only).
    """)

    st.divider()

    st.markdown("""
    ### 🔁 Peer Comparison
    - Prices are **normalized to a base value (100)**
    - This allows fair comparison across stocks with different price levels
    - Start date selection controls comparison window
    """)

    st.divider()

    st.markdown("""
    ### 🔮 Forecasting Method
    - Forecasting uses **exponential smoothing**
    - It captures trend, not exact price levels
    - Forecasts are **indicative**, not predictions
    """)

    st.divider()

    st.markdown("""
    ### ⚠️ Limitations
    - Financial data availability varies by company
    - Fundamental data may be incomplete for some tickers
    - Forecast accuracy decreases in volatile markets
    """)

    st.divider()

    st.markdown("""
    ### ⚖️ Disclaimer
    This dashboard is created **for educational and analytical purposes only**.

    It does **NOT** constitute financial advice, trading recommendations,
    or investment guidance.
    """)

    st.divider()

    st.caption(
        "© 2026 Abhishek Kumar Pandey | Global Energy Market Analytics Dashboard"
    )


# =====================================================
# 🔁 PEER COMPARISON TAB
# =====================================================

with tabs[3]:

    st.subheader("Peer Comparison")

    peer_stocks = st.multiselect(
        "Select energy stocks",
        options=sorted(all_tickers),
        format_func=lambda x: f"{x} — {ticker_name_map.get(x, x)}",
        default=[]
    )

    custom_peer_input = st.text_input(
        "Add custom tickers (comma separated)",
        placeholder="e.g. AAPL, TSLA, MSFT, BTC-USD"
    )

    # -------------------------------------------------
    # Build final peer list
    # -------------------------------------------------
    final_peer_stocks = peer_stocks.copy()

    if custom_peer_input:
        custom_tickers = [
            t.strip().upper()
            for t in custom_peer_input.split(",")
            if t.strip()
        ]
        final_peer_stocks.extend(custom_tickers)

    # Remove duplicates, preserve order
    final_peer_stocks = list(dict.fromkeys(final_peer_stocks))

    if len(final_peer_stocks) < 2:
        st.info("Select at least two stocks to compare.")
    else:
        start_date = st.date_input(
            "Comparison Start Date",
            value=df["Date"].min()
        )

        peer_frames = []

        # -------------------------------------------------
        # 1️⃣ Predefined energy stocks (CSV)
        # -------------------------------------------------
        predefined_peers = [s for s in final_peer_stocks if s in all_tickers]

        if predefined_peers:
            peer_df_pre = load_global_energy_data(all_tickers)
            peer_df_pre = peer_df_pre[
                (peer_df_pre["stock"].isin(predefined_peers)) &
                (peer_df_pre["Date"] >= pd.to_datetime(start_date))
            ]
            peer_frames.append(peer_df_pre)

        # -------------------------------------------------
        # 2️⃣ Custom tickers (Yahoo Finance)
        # -------------------------------------------------
        custom_peers = [s for s in final_peer_stocks if s not in all_tickers]

        for ticker in custom_peers:
            temp = yf.download(
                ticker,
                period="5y",
                interval="1d",
                progress=False,
                auto_adjust=False
            )
            temp = temp.reset_index()
            temp = preprocess_price_data(temp)
            if temp.empty:
                continue
            temp["stock"] = ticker
            temp = temp[temp["Date"] >= pd.to_datetime(start_date)]
            peer_frames.append(temp)

        if not peer_frames:
            st.warning("No valid data available for selected stocks.")
        else:
            peer_df = pd.concat(peer_frames, ignore_index=True)
            peer_df = preprocess_price_data(peer_df)

            if peer_df["stock"].nunique() < 2:
                st.warning("At least two stocks with valid data are required.")
            else:
                fig_peer = normalized_comparison_chart(peer_df)
                st.plotly_chart(fig_peer, use_container_width=True)