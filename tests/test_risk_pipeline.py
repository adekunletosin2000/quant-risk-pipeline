import unittest

import numpy as np
import pandas as pd

from risk_pipeline import calculate_metrics, clean_prices


class RiskPipelineTests(unittest.TestCase):
    def test_clean_prices_sorts_deduplicates_and_drops_invalid_values(self):
        prices = pd.DataFrame(
            {"A": ["12", "10", "11", None], "B": [0, -20, np.inf, None]},
            index=["2024-01-03", "2024-01-01", "2024-01-02", "invalid"],
        )

        cleaned = clean_prices(prices)

        self.assertEqual(list(cleaned.index), list(pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"])))
        self.assertEqual(cleaned["A"].tolist(), [10.0, 11.0, 12.0])
        self.assertNotIn("B", cleaned.columns)

    def test_metrics_use_lower_tail_var_and_report_drawdown_magnitude(self):
        prices = pd.DataFrame(
            {"TEST": [100, 90, 81, 89.1, 98.01]},
            index=pd.date_range("2024-01-01", periods=5),
        )

        returns, rolling_volatility, metrics = calculate_metrics(
            prices, confidence=0.75, rolling_window=2
        )

        self.assertAlmostEqual(metrics.loc["TEST", "Historical VaR"], 0.10)
        self.assertAlmostEqual(metrics.loc["TEST", "Maximum Drawdown"], 0.19)
        self.assertTrue(rolling_volatility["TEST"].iloc[2:].notna().all())
        self.assertEqual(len(returns), 5)

    def test_clean_prices_rejects_empty_data(self):
        with self.assertRaisesRegex(ValueError, "No price data"):
            clean_prices(pd.DataFrame())


if __name__ == "__main__":
    unittest.main()
