import grpc
from forecasting.database import load_city_data
from forecasting.ema_forecaster import forecast_next_month_from_df
from ai_grpc_stubs import forecasting_pb2, forecasting_pb2_grpc
from datetime import datetime

class ForecastingService(forecasting_pb2_grpc.ForecastingServiceServicer):

    def PredictNextMonth(self, request, context):
        df = load_city_data(request.city, request.region)

        result = forecast_next_month_from_df(df, request.city)

        if not result:
            context.abort(grpc.StatusCode.NOT_FOUND, "No data for city")

        forecasts = []
        overall_confidence = result.get("confidence", 85.0)  # Default confidence if not available
        for bt, pct in result["forecast_percent"].items():
            forecasts.append(
                forecasting_pb2.BloodTypeForecast(
                    blood_type=bt,
                    predicted_quantity=pct,   # % demand
                    confidence=overall_confidence  # Use overall model confidence
                )
            )

        # Calculate next month
        now = datetime.now()
        if now.month == 12:
            next_month = 1
            next_year = now.year + 1
        else:
            next_month = now.month + 1
            next_year = now.year
        
        month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
        month_str = f"{month_names[next_month - 1]} {next_year}"

        return forecasting_pb2.ForecastResponse(
            city=request.city,
            region=request.region,
            month=month_str,
            forecasts=forecasts
        )


def serve():
    """Start the gRPC server for the Forecasting Service"""
    from concurrent import futures
    
    # Define the port the gRPC server will listen on
    GRPC_PORT = '50051'
    MAX_WORKERS = 10  # Standard worker count for a thread pool
    
    # 1. Create a server instance with a thread pool
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=MAX_WORKERS))
    
    # 2. Register your service implementation
    forecasting_pb2_grpc.add_ForecastingServiceServicer_to_server(
        ForecastingService(), server)
    
    # 3. Bind the server to the port (listen on all interfaces)
    server.add_insecure_port(f'[::]:{GRPC_PORT}')
    
    # 4. Start the server
    server.start()
    print(f"✅ AI gRPC Forecasting Server started on port {GRPC_PORT}. Waiting for requests...")
    
    # 5. 🚨 CRITICAL: Block the process indefinitely 🚨
    # This keeps the Python script running, preventing the container from exiting (Exit 0)
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down server...")
        server.stop(0)


if __name__ == '__main__':
    serve()
