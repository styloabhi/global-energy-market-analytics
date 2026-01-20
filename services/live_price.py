# services/live_price.py

import yfinance as yf
import streamlit as st

@st.cache_data(ttl=120)
def get_live_price_snapshot(ticker: str) -> dict:
    """
    Fetches a best-effort live price snapshot.
    Falls back to latest available close if live data is unavailable.
    """

    try:
        t = yf.Ticker(ticker)

        # -----------------------------
        # Try FAST live data
        # -----------------------------
        info = t.fast_info or {}

        current_price = info.get("last_price")
        prev_close = info.get("previous_close")

        # -----------------------------
        # Fallback: use recent history
        # -----------------------------
        if current_price is None or prev_close is None:
            hist = t.history(period="5d")

            if hist.empty:
                return {}

            current_price = hist["Close"].iloc[-1]

            if len(hist) > 1:
                prev_close = hist["Close"].iloc[-2]
            else:
                prev_close = current_price

        pct_change = ((current_price / prev_close) - 1) * 100

        return {
            "current_price": float(current_price),
            "previous_close": float(prev_close),
            "pct_change": float(pct_change),
        }

    except Exception:
        return {}
