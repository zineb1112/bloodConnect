import unittest
import pandas as pd
import numpy as np
from forecasting.ema_forecaster import forecast_next_month_from_df, compute_confidence

#H: unit  test for the forcasting logic work
class TestEMAForecaster(unittest.TestCase):
    def test_compute_confidence(self):
        # Test with valid MAPE
        confidence = compute_confidence(10.0, 12)
        self.assertIsInstance(confidence, float) #H: the resturned value shoud be float(test)
        self.assertGreaterEqual(confidence, 0) #H: never negative (confidence)
        self.assertLessEqual(confidence, 100)

        # Test with None MAPE
        confidence = compute_confidence(None, 12) #H: test in case not enough histo data-> neutral
        self.assertEqual(confidence, 50.0)

        # Test with high MAPE
        confidence = compute_confidence(100.0, 12)
        self.assertLess(confidence, 50.0)

    #H: testing the full forecasting flow
    def test_forecast_next_month_from_df(self):
        # Sample data
        data = {
            'request_date': pd.date_range('2023-01-01', periods=12, freq='M'),
            'blood_type': ['A+'] * 6 + ['B+'] * 6,
            'quantity_needed': [10, 12, 15, 11, 13, 14, 20, 22, 25, 21, 23, 24],
            'city': ['TestCity'] * 12,
            'region': ['TestRegion'] * 12
        }
        df = pd.DataFrame(data)

        result = forecast_next_month_from_df(df, 'TestCity') 

        self.assertIsNotNone(result) #H: the fct give  a result and it has all of the bellow elements
        self.assertIn('forecast_percent', result)
        self.assertIn('top_blood_type', result)
        self.assertIn('confidence', result)
        self.assertIn('model_error', result)

        # Check percentages sum to 100
        total_pct = sum(result['forecast_percent'].values())
        self.assertAlmostEqual(total_pct, 100.0, places=1)

        # Check confidence is float
        self.assertIsInstance(result['confidence'], float)

    #H: when there is no enough data there is no forecast
    def test_forecast_next_month_from_df_empty_city(self):
        df = pd.DataFrame({
            'request_date': ['2023-01-01'],
            'blood_type': ['A+'],
            'quantity_needed': [10],
            'city': ['OtherCity'],
            'region': ['Region']
        })

        result = forecast_next_month_from_df(df, 'TestCity')
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()