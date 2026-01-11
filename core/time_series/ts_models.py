from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from statsmodels.tsa.arima.model import ARIMA
from scipy import stats
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX


class TimeSeriesAnomalyDetector:
    """методы детекции аномалий через временные ряды"""

    def __init__(self):
        self.models: Dict = {}
        self.scalers: Dict = {}
        self.thresholds: Dict = {}

    def detect_with_arima(
        self,
        train_data: pd.Series,
        test_data: pd.Series,
        order: Tuple[int, int, int] = (2, 1, 2),
        threshold: float = 3.0,
    ) -> Dict:
        """ARIMA детекция через residuals и k-sigma правило"""
        from statsmodels.tsa.stattools import adfuller

        # проверка стационарности и подбор d
        d = order[1]
        diff_data = train_data.copy()
        adf_result = adfuller(diff_data.dropna())

        while adf_result[1] > 0.05 and d < 2:
            diff_data = diff_data.diff().dropna()
            adf_result = adfuller(diff_data)
            d += 1

        adjusted_order = (order[0], d, order[2])

        model = ARIMA(train_data, order=adjusted_order)
        fitted = model.fit()

        forecast = fitted.forecast(steps=len(test_data))
        forecast.index = test_data.index

        train_resid = fitted.resid
        sigma = float(np.std(train_resid))
        thr = sigma * threshold

        # confidence interval
        lower = forecast - thr
        upper = forecast + thr

        residuals = test_data.values - forecast.values
        anomalies = np.abs(residuals) > thr
        scores = np.abs(residuals) / thr

        return {
            "predictions": forecast,
            "residuals": residuals,
            "anomalies": anomalies,
            "threshold": thr,
            "anomaly_scores": scores,
            "lower_bound": lower,
            "upper_bound": upper,
            "model": fitted,
        }

    def detect_with_sarima(
        self,
        train_data: pd.Series,
        test_data: pd.Series,
        order: Tuple[int, int, int] = (1, 1, 1),
        seasonal_order: Tuple[int, int, int, int] = (1, 1, 1, 12),
        threshold: float = 3.0,
    ) -> Dict:
        """SARIMA для сезонных паттернов"""
        model = SARIMAX(
            train_data,
            order=order,
            seasonal_order=seasonal_order,
            enforce_stationarity=False,
            enforce_invertibility=False,
        )
        fitted = model.fit(disp=False)

        forecast = fitted.forecast(steps=len(test_data))
        forecast.index = test_data.index

        train_resid = fitted.resid
        sigma = float(np.std(train_resid))
        thr = sigma * threshold

        lower = forecast - thr
        upper = forecast + thr

        residuals = test_data.values - forecast.values
        anomalies = np.abs(residuals) > thr

        return {
            "predictions": forecast,
            "residuals": residuals,
            "anomalies": anomalies,
            "threshold": thr,
            "anomaly_scores": np.abs(residuals) / thr,
            "lower_bound": lower,
            "upper_bound": upper,
            "model": fitted,
        }

    def detect_with_prophet(
        self,
        train_data: pd.Series,
        test_data: pd.Series,
        interval_width: float = 0.95,
    ) -> Dict:
        """Prophet для сложной сезонности"""
        from prophet import Prophet

        train_df = pd.DataFrame({"ds": train_data.index, "y": train_data.values})

        model = Prophet(
            interval_width=interval_width,
            yearly_seasonality=False,
            weekly_seasonality=True,
            daily_seasonality=True,
            changepoint_prior_scale=0.05,
        )
        model.fit(train_df)

        future_df = pd.DataFrame({"ds": test_data.index})
        forecast = model.predict(future_df)

        predictions = forecast["yhat"].values
        lower_bound = forecast["yhat_lower"].values
        upper_bound = forecast["yhat_upper"].values

        anomalies = (test_data.values < lower_bound) | (test_data.values > upper_bound)

        distances = np.where(
            test_data.values < lower_bound,
            lower_bound - test_data.values,
            np.where(
                test_data.values > upper_bound,
                test_data.values - upper_bound,
                0.0,
            ),
        )

        return {
            "predictions": pd.Series(predictions, index=test_data.index),
            "lower_bound": pd.Series(lower_bound, index=test_data.index),
            "upper_bound": pd.Series(upper_bound, index=test_data.index),
            "anomalies": anomalies,
            "anomaly_scores": distances,
            "model": model,
        }

    def detect_with_isolation_forest_ts(
        self,
        train_data: pd.DataFrame,
        test_data: pd.DataFrame,
        feature_cols: List[str] | None = None,
        contamination: float = 0.1,
        window_size: int = 10,
    ) -> Dict:
        """Isolation Forest на оконных признаках"""
        if feature_cols is None:
            feature_cols = [
                c for c in train_data.columns
                if c not in {"timestamp", "label", "source"}
            ]

        def add_rolling_features(df: pd.DataFrame, cols: List[str], w: int) -> pd.DataFrame:
            out = df[cols].copy()
            for c in cols:
                out[f"{c}_roll_mean"] = df[c].rolling(w, min_periods=1).mean()
                out[f"{c}_roll_std"] = df[c].rolling(w, min_periods=1).std().fillna(0)
            return out

        x_train = add_rolling_features(train_data, feature_cols, window_size)
        x_test = add_rolling_features(test_data, feature_cols, window_size)

        model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100,
        )
        model.fit(x_train)

        preds = model.predict(x_test)
        scores = -model.score_samples(x_test)

        return {
            "anomalies": preds == -1,
            "anomaly_scores": scores.tolist(),
            "model": model,
        }