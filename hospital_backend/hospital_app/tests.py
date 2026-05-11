from django.test import TestCase, RequestFactory, Client, override_settings
from django.contrib.auth.models import User
from django.http import JsonResponse
from unittest.mock import patch, MagicMock
import json

from hospital_app.models import Hospital, HospitalUser
from hospital_app.views import get_forecast, test_ai_connection
from hospital_project.grpc import forecasting_pb2

#H: in here we test the integration between hospital service and the forcasting oe (ai service)

class AIIntegrationTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        # Create test user and hospital
        self.user = HospitalUser.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123'
        )
        self.hospital = Hospital.objects.create(
            user=self.user,
            name='Test Hospital',
            city='TestCity',
            region='TestRegion',
            phone='123456789',
            address='Test Address'
        )

    @override_settings(AI_SERVICE_TARGET='localhost:50051')
    @patch('hospital_app.views.forecasting_pb2_grpc.ForecastingServiceStub')
    @patch('hospital_app.views.grpc.insecure_channel')
    def test_get_forecast_success(self, mock_grpc, mock_stub_class):
        #H: testing when the forecast is succeeded

        # Mock the gRPC channel
        mock_channel = MagicMock()
        mock_grpc.return_value = mock_channel

        # Mock the stub
        mock_stub = MagicMock()
        mock_stub_class.return_value = mock_stub

        # Mock the response
        mock_response = MagicMock()
        mock_response.city = 'TestCity'
        mock_response.region = 'TestRegion'
        mock_response.month = 'January 2026'
        mock_response.forecasts = [
            MagicMock(blood_type='A+', predicted_quantity=30.0, confidence=85.0),
            MagicMock(blood_type='B+', predicted_quantity=25.0, confidence=85.0),
        ]
        mock_stub.PredictNextMonth.return_value = mock_response

        # Use test client without login (uses GET params)
        response = self.client.get('/api/forecast/', {'city': 'TestCity', 'region': 'TestRegion'})

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'SUCCESS')
        self.assertEqual(len(data['forecasts']), 2)
        self.assertEqual(data['forecasts'][0]['blood_type'], 'A+')

    @patch('hospital_app.views.forecasting_pb2_grpc.ForecastingServiceStub')
    @patch('hospital_app.views.grpc.insecure_channel')
    def test_get_forecast_grpc_error(self, mock_grpc, mock_stub_class):
        # Mock the gRPC channel
        mock_channel = MagicMock()
        mock_grpc.return_value = mock_channel

        # Mock the stub to raise error
        import grpc
        mock_error = grpc.RpcError('Connection failed')
        status_mock = MagicMock()
        status_mock.name = 'UNAVAILABLE'
        mock_error.code = MagicMock(return_value=status_mock)
        mock_error.details = MagicMock(return_value='Connection failed details')
        mock_stub = MagicMock()
        mock_stub.PredictNextMonth.side_effect = mock_error
        mock_stub_class.return_value = mock_stub

        # Use test client
        response = self.client.get('/api/forecast/', {'city': 'TestCity', 'region': 'TestRegion'})

        self.assertEqual(response.status_code, 500)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'FAILURE')

    @patch('hospital_app.views.ai_pb2_grpc.PredictionServiceStub')
    @patch('hospital_app.views.grpc.insecure_channel')
    @patch('hospital_app.views.settings')
    def test_test_ai_connection_success(self, mock_settings, mock_grpc, mock_stub_class):
        mock_settings.AI_SERVICE_TARGET = 'localhost:50051'

        # Mock the gRPC channel
        mock_channel = MagicMock()
        mock_grpc.return_value = mock_channel

        # Mock the stub
        mock_stub = MagicMock()
        mock_stub_class.return_value = mock_stub

        # Mock the response
        mock_response = MagicMock()
        mock_response.status = 'OK'
        mock_stub.HealthCheck.return_value = mock_response

        # Use test client
        response = self.client.get('/test-ai-grpc/')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'SUCCESS')
        self.assertEqual(data['ai_service_response'], 'OK')

    @patch('hospital_app.views.ai_pb2_grpc.PredictionServiceStub')
    @patch('hospital_app.views.grpc.insecure_channel')
    @patch('hospital_app.views.settings')
    def test_test_ai_connection_grpc_error(self, mock_settings, mock_grpc, mock_stub_class):
        mock_settings.AI_SERVICE_TARGET = 'localhost:50051'

        # Mock the gRPC channel
        mock_channel = MagicMock()
        mock_grpc.return_value = mock_channel

        # Mock the stub to raise error
        import grpc
        mock_error = grpc.RpcError('Connection failed')
        status_mock = MagicMock()
        status_mock.name = 'UNAVAILABLE'
        mock_error.code = MagicMock(return_value=status_mock)
        mock_error.details = MagicMock(return_value='Connection failed details')
        mock_stub = MagicMock()
        mock_stub.HealthCheck.side_effect = mock_error
        mock_stub_class.return_value = mock_stub

        # Use test client
        response = self.client.get('/test-ai-grpc/')

        self.assertEqual(response.status_code, 500)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'FAILURE')
