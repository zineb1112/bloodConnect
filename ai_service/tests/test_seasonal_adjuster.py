import unittest
from forecasting.seasonal_adjuster import SeasonalAdjuster


class TestSeasonalAdjuster(unittest.TestCase):
    def test_seasonal_adjuster_winter(self):
        adjuster = SeasonalAdjuster()
        predictions = {'A+': 0.3, 'B+': 0.3, 'O+': 0.4}
        adjusted = adjuster.adjust(predictions, 1)  # January

        # O+ should be increased
        self.assertGreater(adjusted['O+'], predictions['O+'])
        # Total should be 1
        self.assertAlmostEqual(sum(adjusted.values()), 1.0, places=5)

    def test_seasonal_adjuster_summer(self):
        adjuster = SeasonalAdjuster()
        predictions = {'A+': 0.3, 'B+': 0.3, 'AB+': 0.4}
        adjusted = adjuster.adjust(predictions, 7)  # July

        # A+ and B+ should be increased
        self.assertGreater(adjusted['A+'], predictions['A+'])
        self.assertGreater(adjusted['B+'], predictions['B+'])
        self.assertAlmostEqual(sum(adjusted.values()), 1.0, places=5)

    def test_seasonal_adjuster_no_season(self):
        adjuster = SeasonalAdjuster()
        predictions = {'A+': 0.5, 'B+': 0.5}
        adjusted = adjuster.adjust(predictions, 5)  # May

        # No changes
        self.assertEqual(adjusted, predictions)


if __name__ == '__main__':
    unittest.main()