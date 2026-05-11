import unittest
import pandas as pd
import numpy as np
from forecasting.validator import backtest_ema


class TestValidator(unittest.TestCase):
    def test_backtest_ema(self):
        # Create sample monthly data
        data = {
            'A+': [10, 12, 15, 11, 13, 14],
            'B+': [20, 22, 25, 21, 23, 24]
        }
        monthly_df = pd.DataFrame(data)

        mape = backtest_ema(monthly_df, alpha=0.3)
        #H: ensure mape is a correct value
        self.assertIsNotNone(mape)
        self.assertIsInstance(mape, float)
        self.assertGreaterEqual(mape, 0)

    def test_backtest_ema_insufficient_data(self):
        # Less than 4 data points (when data is not enough for historical analyses -> no backtest)
        data = {'A+': [10, 12]}
        monthly_df = pd.DataFrame(data)

        mape = backtest_ema(monthly_df, alpha=0.3)

        self.assertIsNone(mape) #H: it should be none no fake base

    def test_backtest_ema_no_errors(self):
        # Data with no errors (perfect prediction)
        data = {'A+': [10, 10, 10, 10, 10, 10]}
        monthly_df = pd.DataFrame(data)

        mape = backtest_ema(monthly_df, alpha=0.3)

        self.assertEqual(mape, 0.0)


if __name__ == '__main__':
    unittest.main()