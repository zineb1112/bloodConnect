# ai_service/forecasting/seasonal_adjuster.py

class SeasonalAdjuster:
    def adjust(self, predictions, month):
        factors = {}

        if month in [12, 1, 2]:      # Winter
            factors = {'O+': 1.3}
        elif month in [6, 7, 8]:     # Summer
            factors = {'A+': 1.2, 'B+': 1.1}

        adjusted = {}
        for bt, prob in predictions.items():
            adjusted[bt] = prob * factors.get(bt, 1.0)

        total = sum(adjusted.values())
        return {bt: v / total for bt, v in adjusted.items()}
