from datetime import date, timedelta

import plotly.express as px
import streamlit as st

from risk_pipeline import calculate_metrics, download_prices


@st.cache_data(ttl=3600, show_spinner="Downloading and cleaning adjusted daily prices...")
def load_prices(tickers: tuple[str, ...], start: str, end: str):
    return download_prices(tickers, start, end)


st.set_page_config(page_title="Multi-Asset Risk Dashboard", page_icon="📈", layout="wide")
st.title("Multi-Asset Financial Risk Dashboard")
st.caption(
    "A daily market-data pipeline for exploring volatility, historical VaR, "
    "maximum drawdown, and risk-adjusted returns."
)

with st.sidebar:
    st.header("Pipeline settings")
    ticker_input = st.text_input(
        "Ticker symbols",
        value="AAPL, MSFT, ^TNX, EURUSD=X, BTC-USD",
        help="Separate symbols with commas. Examples: SPY, ^TNX, EURUSD=X, BTC-USD.",
    )
    today = date.today()
    start_date = st.date_input("Start date", value=today - timedelta(days=365 * 3))
    end_date = st.date_input("End date", value=today)
    confidence = st.slider("VaR confidence level", min_value=0.90, max_value=0.99, value=0.95)
    rolling_window = st.slider("Rolling window (trading days)", 5, 90, 21)
    risk_free_rate = st.number_input(
        "Annual risk-free rate (%)", min_value=0.0, max_value=30.0, value=0.0, step=0.25
    )
    refresh_data = st.button("Refresh market data", use_container_width=True)

if start_date >= end_date:
    st.error("Start date must be earlier than end date.")
    st.stop()

if refresh_data:
    load_prices.clear()

tickers = tuple(dict.fromkeys(
    symbol.strip().upper() for symbol in ticker_input.split(",") if symbol.strip()
))
try:
    prices = load_prices(tickers, start_date.isoformat(), end_date.isoformat())
    returns, rolling_volatility, metrics = calculate_metrics(
        prices,
        confidence=confidence,
        rolling_window=rolling_window,
        risk_free_rate=risk_free_rate,
    )

    st.subheader("Risk summary")
    st.caption(
        f"Historical daily VaR at {confidence:.0%} confidence. "
        "VaR and drawdown are shown as positive loss magnitudes."
    )
    formatted_metrics = metrics.copy()
    for column in ("Annualized Volatility", "Historical VaR", "Maximum Drawdown"):
        formatted_metrics[column] = formatted_metrics[column].map(
            lambda value: f"{value:.2%}" if value == value else "—"
        )
    formatted_metrics["Latest Price"] = formatted_metrics["Latest Price"].map(
        lambda value: f"{value:,.4f}" if value < 100 else f"{value:,.2f}"
    )
    formatted_metrics["Sharpe Ratio"] = formatted_metrics["Sharpe Ratio"].map(
        lambda value: f"{value:.2f}" if value == value else "—"
    )
    st.dataframe(formatted_metrics, use_container_width=True)

    left, right = st.columns(2)
    with left:
        st.subheader("Adjusted closing prices")
        price_chart = px.line(prices, x=prices.index, y=prices.columns, labels={"value": "Price"})
        st.plotly_chart(price_chart, use_container_width=True)
    with right:
        st.subheader(f"{rolling_window}-day rolling volatility")
        volatility_chart = px.line(
            rolling_volatility,
            x=rolling_volatility.index,
            y=rolling_volatility.columns,
            labels={"value": "Annualized volatility"},
        )
        volatility_chart.update_yaxes(tickformat=".0%")
        st.plotly_chart(volatility_chart, use_container_width=True)

    st.subheader("Daily returns")
    return_chart = px.line(returns, x=returns.index, y=returns.columns, labels={"value": "Return"})
    return_chart.update_yaxes(tickformat=".0%")
    st.plotly_chart(return_chart, use_container_width=True)

    with st.expander("Data quality and methodology"):
        st.write(
            f"Retained {len(prices):,} unique trading dates across "
            f"{len(prices.columns)} assets ({prices.index.min().date()} to "
            f"{prices.index.max().date()}). Invalid timestamps, duplicate dates, "
            "non-numeric values, non-finite values, and non-positive prices are removed. "
            "Missing prices are not forward-filled."
        )
        st.write(
            "Volatility and Sharpe are annualized using 252 trading days. VaR is the "
            "historical lower-tail daily return quantile. Maximum drawdown is calculated "
            "from each asset's cumulative return series. The risk-free rate is treated "
            "as an annual percentage."
        )
except (ValueError, KeyError) as error:
    st.error(str(error))
except Exception as error:
    st.error(f"Market data could not be loaded: {error}")
