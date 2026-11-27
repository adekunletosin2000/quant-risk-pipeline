# Multi-Asset Financial Risk Dashboard

A Streamlit dashboard and Python pipeline for downloading adjusted daily prices
from Yahoo Finance, cleaning time-series observations, and comparing market risk
across equities, rates, currencies, and crypto.

## Open and update the live app without local Python

The deployed dashboard runs on [Streamlit Community Cloud](https://share.streamlit.io/)
and can be opened from any browser. Edit the repository in a
[GitHub Codespace](https://github.com/codespaces/new?repo=adekunletosin2000/quant-risk-pipeline&ref=main),
which provides VS Code and Python in the cloud. Nothing needs to be installed
on your computer.

### First-time setup

1. Make sure this project is pushed to the `main` branch of your GitHub repository.
2. Deploy it once on Streamlit Community Cloud using the
   [prefilled deployment page](https://share.streamlit.io/deploy?repository=adekunletosin2000/quant-risk-pipeline&branch=main&mainModule=app.py).
3. Sign in with GitHub and authorize access to the repository.
4. Select **Create app**, choose the repository and `main` branch, set **Main
   file path** to `app.py`, and select **Deploy**. Streamlit installs the
   packages from `requirements.txt` and gives you a shareable app URL.

### Change dashboard code from your browser

1. Open the repository in a
   [GitHub Codespace](https://github.com/codespaces/new?repo=adekunletosin2000/quant-risk-pipeline&ref=main).
   On first launch, the Codespace installs the requirements and starts the
   dashboard preview automatically.
2. Edit project files in the browser-based VS Code. Codespaces opens the
   preview on port `8501`.
3. In the **Source Control** panel, commit your changes and sync/push them to
   `main`. Streamlit Community Cloud detects the commit and redeploys the
   public dashboard. Refresh its URL to see the update.

To try a change without publishing it, create a branch in Codespaces and use
the port preview there; merge it into `main` when it is ready.

### Refresh market data

The app loads data on opening and caches prices for one hour. Change tickers or
dates in the sidebar to load a different selection, or choose **Refresh market
data** to bypass the cache and download again. Risk settings recalculate from
the loaded prices. Yahoo Finance and the hosting service need internet access.
Defaults include equities (`AAPL`, `MSFT`), a Treasury yield index (`^TNX`), a
currency pair (`EURUSD=X`), and crypto (`BTC-USD`).

## Risk measures

- **Annualized volatility:** standard deviation of daily simple returns times
  the square root of 252.
- **Historical VaR:** magnitude of the lower-tail daily return quantile at the
  selected confidence level.
- **Maximum drawdown:** worst peak-to-trough loss in the cumulative return
  series, displayed as a positive loss magnitude in the dashboard.
- **Sharpe ratio:** annualized mean daily excess return divided by annualized
  volatility, using the configured annual risk-free rate.

The pipeline sorts observations, removes invalid timestamps and duplicate
dates, coerces prices to numeric values, and excludes non-finite and non-positive
prices. It does not forward-fill missing prices, avoiding synthetic returns
across missing observations. Yahoo Finance data is provided for educational
purposes and should not be treated as investment advice.

## Optional tests

Run in the Codespace terminal:

```powershell
python -m unittest discover -s tests
```
