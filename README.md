# Multi-Asset Financial Risk Dashboard

A Streamlit dashboard and Python pipeline for downloading adjusted daily prices
from Yahoo Finance, cleaning time-series observations, and comparing market risk
across equities, rates, currencies, and crypto.

## Always-on online preview

Deploy the app once to [Streamlit Community Cloud](https://share.streamlit.io/);
after that, it runs in the cloud and you can open its URL from any browser
without installing Python.

1. Push this project to the `main` branch of your GitHub repository. You can
   [open the prefilled Streamlit deployment page](https://share.streamlit.io/deploy?repository=adekunletosin2000/quant-risk-pipeline&branch=main&mainModule=app.py).
2. Sign in to Streamlit Community Cloud with GitHub and authorize access to
   that repository (a private repository is fine if your account has access).
3. Select **Create app**, choose the repository and `main` branch, and set
   **Main file path** to `app.py`.
4. Select **Deploy**. Streamlit installs the packages from `requirements.txt`
   and gives you a shareable app URL. Future pushes to `main` are deployed
   automatically.

The app loads data on opening and caches downloaded prices for one hour.
Changing tickers or dates loads the corresponding data; use **Refresh market
data** to bypass the cache. Defaults include equities (`AAPL`, `MSFT`), a
Treasury yield index (`^TNX`), a currency pair (`EURUSD=X`), and crypto
(`BTC-USD`). The hosting service and Yahoo Finance both need internet access.

## Optional local run

If Python is available, install `requirements.txt` and start the app with
`streamlit run app.py`.

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

## Tests

```powershell
python -m unittest discover -s tests
```
