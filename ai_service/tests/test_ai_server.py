import unittest
from unittest.mock import patch, MagicMock
from ai_server import ForecastingService
from ai_grpc_stubs import forecasting_pb2


#H: tests how the ai_service logic works in diffrent situations
class TestAIServer(unittest.TestCase):
    @patch('ai_server.load_city_data')
    @patch('ai_server.forecast_next_month_from_df')
    def test_predict_next_month_success(self, mock_forecast, mock_load_data):
        service = ForecastingService()

        # Mock request
        request = MagicMock()
        request.city = 'TestCity'
        request.region = 'TestRegion'

        # Mock context
        context = MagicMock()

        # Mock data loading
        mock_df = MagicMock()
        mock_load_data.return_value = mock_df

        # Mock forecast result
        mock_forecast.return_value = {
            'forecast_percent': {'A+': 30.0, 'B+': 25.0, 'O+': 45.0},
            'confidence': 85.0
        }

        response = service.PredictNextMonth(request, context) #H: bellow we check if the data returned by the service is right

        self.assertEqual(response.city, 'TestCity')
        self.assertEqual(response.region, 'TestRegion')
        self.assertEqual(len(response.forecasts), 3)
        self.assertIn(response.forecasts[0].blood_type, ['A+', 'B+', 'O+'])
        self.assertGreater(response.forecasts[0].predicted_quantity, 0)
        self.assertEqual(response.forecasts[0].confidence, 85.0)
        self.assertIn('2026', response.month)  # Since current is Dec 2025, next is Jan 2026

    @patch('ai_server.load_city_data')
    @patch('ai_server.forecast_next_month_from_df')
    def test_predict_next_month_no_data(self, mock_forecast, mock_load_data):
        service = ForecastingService()

        request = MagicMock()
        request.city = 'TestCity'
        request.region = 'TestRegion'

        context = MagicMock()

        mock_load_data.return_value = MagicMock()
        mock_forecast.return_value = None
        #H: when no data returned by forecasting service
        with self.assertRaises(Exception):  # grpc.StatusCode.NOT_FOUND
            service.PredictNextMonth(request, context)

        context.abort.assert_called_once()

    @patch('ai_server.load_city_data')
    @patch('ai_server.forecast_next_month_from_df')
    def test_predict_next_month_empty_data(self, mock_forecast, mock_load_data):
        service = ForecastingService()

        request = MagicMock()
        request.city = 'TestCity'
        request.region = 'TestRegion'

        context = MagicMock()

        mock_df = MagicMock()
        mock_df.empty = True
        mock_load_data.return_value = mock_df

        mock_forecast.return_value = None #H: empty dataset -> no processing 

        with self.assertRaises(Exception):
            service.PredictNextMonth(request, context)

        context.abort.assert_called_once()


if __name__ == '__main__':
    unittest.main()