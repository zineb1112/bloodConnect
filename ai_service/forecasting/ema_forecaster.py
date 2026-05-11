import pandas as pd
from forecasting.validator import backtest_ema

def compute_confidence(mape, data_points):
    """
    Compute confidence score based on MAPE and data points.
    Lower MAPE and more data points = higher confidence.
    """
    if mape is None:
        return 50.0  # Default low confidence if no error data
    
    # Confidence decreases as MAPE increases
    # MAPE of 0% = 100% confidence, MAPE of 50%+ = 0% confidence
    mape_factor = max(0, 100 - (mape * 2))
    
    # More data points = higher confidence (up to 12 months)
    data_factor = min(100, (data_points / 12) * 30 + 70)
    
    # Weighted average
    confidence = (mape_factor * 0.7) + (data_factor * 0.3)
    
    return round(max(0, min(100, confidence)), 1)

#H: usage of exponetial moving average to forast next month's needs distribution
def forecast_next_month_from_df(df, city, alpha=0.3):
    city_data = df[df["city"] == city]

    if city_data.empty:
        return None

    city_data["request_date"] = pd.to_datetime(city_data["request_date"])
    city_data["year_month"] = city_data["request_date"].dt.to_period("M")

    monthly = (
        city_data
        .groupby(["year_month", "blood_type"])["quantity_needed"]
        .sum()
        .unstack(fill_value=0)
    )

    forecast = {}
    for blood_type in monthly.columns:
        ts = monthly[blood_type].values
        ema = ts[0]
        for x in ts[1:]:
            ema = alpha * x + (1 - alpha) * ema
        forecast[blood_type] = ema

    total = sum(forecast.values())
    forecast_pct = {bt: round(q/total*100, 1) for bt, q in forecast.items()}

    mape = backtest_ema(monthly, alpha)
    confidence = compute_confidence(mape, len(monthly))

    top_bt = max(forecast_pct, key=forecast_pct.get)

    return {
        "city": city,
        "forecast_percent": forecast_pct,
        "top_blood_type": top_bt,
        "confidence": confidence,
        "model_error": mape
    }