import numpy as np

#H: checking pasts months for comparing and measuring the accuracy
def backtest_ema(monthly_df, alpha=0.3):
    """
    Backtest EMA using rolling prediction.
    Returns mean absolute percentage error (MAPE).
    """
    errors = []

    for blood_type in monthly_df.columns:
        ts = monthly_df[blood_type].values
        if len(ts) < 4:
            continue

        for i in range(2, len(ts)):
            history = ts[:i]
            actual = ts[i]

            ema = history[0]
            for x in history[1:]:
                ema = alpha * x + (1 - alpha) * ema

            if actual > 0:
                errors.append(abs(actual - ema) / actual)

    if not errors:
        return None

    return round(np.mean(errors) * 100, 2)  # % error
