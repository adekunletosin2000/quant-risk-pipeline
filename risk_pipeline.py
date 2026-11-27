"""Market-data ingestion, cleaning, and portfolio risk calculations."""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd


TRADING_DAYS_PER_YEAR = 252


def clean_prices(prices: pd.DataFrame) -> pd.DataFrame:
    """Return sorted, numeric, positive prices with invalid observations removed."""
    if prices.empty:
        raise ValueError("No price data was returned for the selected assets.")

    cleaned = prices.copy()
    cleaned.index = pd.to_datetime(cleaned.index, errors="coerce")
    cleaned = cleaned.loc[~cleaned.index.isna()]
    cleaned = cleaned[~cleaned.index.duplicated(keep="last")].sort_index()
    cleaned = cleaned.apply(pd.to_numeric, errors="coerce")
    cleaned = cleaned.replace([np.inf, -np.inf], np.nan)
    cleaned = cleaned.where(cleaned > 0).dropna(axis=1, how="all")
    cleaned = cleaned.dropna(how="all")

    if cleaned.empty:
        raise ValueError("No valid positive price observations remain after cleaning.")
    return cleaned


def download_prices(
    tickers: Iterable[str],
    start: str,
    end: str,
) -> pd.DataFrame:
    """Download adjusted daily close prices from Yahoo Finance."""
    import yfinance as yf

    symbols = list(dict.fromkeys(symbol.strip().upper() for symbol in tickers if symbol.strip()))
    if not symbols:
        raise ValueError("Enter at least one ticker symbol.")

    data = yf.download(
        symbols,
        start=start,
        end=end,
        auto_adjust=True,
        progress=False,
        group_by="ticker",
        threads=True,
    )
    if data.empty:
        raise ValueError("Yahoo Finance returned no data for the selected date range.")

    if isinstance(data.columns, pd.MultiIndex):
        closes: dict[str, pd.Series] = {}
        for symbol in symbols:
            if (symbol, "Close") in data.columns:
                closes[symbol] = data[(symbol, "Close")]
            elif ("Close", symbol) in data.columns:
                closes[symbol] = data[("Close", symbol)]
        prices = pd.DataFrame(closes)
    elif "Close" in data.columns:
        prices = data[["Close"]].rename(columns={"Close": symbols[0]})
    else:
        raise ValueError("The downloaded data did not contain a Close price field.")

    cleaned = clean_prices(prices)
    missing_symbols = [symbol for symbol in symbols if symbol not in cleaned.columns]
    if missing_symbols:
        raise ValueError(
            "No valid positive close prices were returned for: "
            + ", ".join(missing_symbols)
        )
    return cleaned


def calculate_metrics(
    prices: pd.DataFrame,
    confidence: float = 0.95,
    rolling_window: int = 21,
    risk_free_rate: float = 0.0,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Calculate daily returns, rolling volatility, and per-asset risk metrics."""
    if not 0 < confidence < 1:
        raise ValueError("Confidence must be between 0 and 1.")
    if rolling_window < 2:
        raise ValueError("Rolling window must be at least 2 trading days.")

    clean = clean_prices(prices)
    returns = clean.pct_change(fill_method=None).replace([np.inf, -np.inf], np.nan)
    rolling_volatility = (
        returns.rolling(rolling_window, min_periods=rolling_window).std()
        * np.sqrt(TRADING_DAYS_PER_YEAR)
    )
    annual_risk_free_rate = risk_free_rate / 100
    daily_risk_free_rate = (1 + annual_risk_free_rate) ** (
        1 / TRADING_DAYS_PER_YEAR
    ) - 1

    rows = []
    for symbol in clean.columns:
        asset_returns = returns[symbol].dropna()
        if asset_returns.empty:
            continue

        wealth = pd.concat(
            [
                pd.Series([1.0]),
                (1 + asset_returns).reset_index(drop=True).cumprod(),
            ],
            ignore_index=True,
        )
        drawdown = wealth / wealth.cummax() - 1
        annualized_volatility = asset_returns.std() * np.sqrt(TRADING_DAYS_PER_YEAR)
        sharpe = (
            (asset_returns.mean() - daily_risk_free_rate)
            * TRADING_DAYS_PER_YEAR
            / annualized_volatility
            if annualized_volatility > 0
            else np.nan
        )
        rows.append(
            {
                "Asset": symbol,
                "Latest Price": clean[symbol].dropna().iloc[-1],
                "Annualized Volatility": annualized_volatility,
                "Historical VaR": max(
                    0.0, -asset_returns.quantile(1 - confidence)
                ),
                "Maximum Drawdown": -drawdown.min(),
                "Sharpe Ratio": sharpe,
            }
        )

    if not rows:
        raise ValueError("At least two valid price observations are required to calculate risk.")
    metrics = pd.DataFrame(rows).set_index("Asset")
    return returns, rolling_volatility, metrics
