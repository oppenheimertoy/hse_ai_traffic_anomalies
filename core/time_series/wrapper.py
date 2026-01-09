import enum
import tempfile
from typing import Any, Dict

import pandas as pd
import requests

from core.time_series.pcap_converter import PCAPConverter
from core.time_series.ts_models import TimeSeriesAnomalyDetector


class AnomaliesDetectorModels(enum.Enum):
    IsolationForest = "isolation_forest"
    Arima = "arima"
    Sarima = "sarima"
    Prophet = "prophet"


class AnomaliesDetector:
    """
    Wrapper on anomalies detector models to be externally used
    """

    def __init__(self):
        self._ts_detector = TimeSeriesAnomalyDetector()
        self._pcap_converter = PCAPConverter()

    def detect(
        self,
        pcap: bytes | str,
        *,
        models: list[AnomaliesDetectorModels] = [
            AnomaliesDetectorModels.IsolationForest,
        ],
        target_col: str = "packet_count",
        train_ratio: float = 0.7,
        feature_cols: list[str] | None = None,
    ) -> Dict[str, Any]:
        """
        Description

        :param pcap: accepts file bytes or url string
        :type pcap: bytes | str
        """
        pcap_bytes = (
            requests.get(pcap, timeout=10).content if isinstance(pcap, str) else pcap
        )

        with tempfile.NamedTemporaryFile(suffix=".pcap") as tmp:
            tmp.write(pcap_bytes)
            tmp.flush()
            df = self._pcap_converter.convert(tmp.name)

        if df.empty:
            return {"data": df, "result": None}

        if len(df) < 2:
            return {"data": df, "result": None}

        split_idx = int(len(df) * train_ratio)
        split_idx = min(max(1, split_idx), len(df) - 1)
        train_df = df.iloc[:split_idx]
        test_df = df.iloc[split_idx:]
        result = {}
        for model in models:
            if model.value == "isolation_forest":
                result[model] = self._ts_detector.detect_with_isolation_forest_ts(
                    train_df,
                    test_df,
                    feature_cols=feature_cols,
                )
            elif model.value == "arima":
                train_series, test_series = self._split_series(
                    df,
                    target_col,
                    split_idx,
                )
                result[model] = self._ts_detector.detect_with_arima(
                    train_series,
                    test_series,
                )
            elif model.value == "sarima":
                train_series, test_series = self._split_series(
                    df,
                    target_col,
                    split_idx,
                )
                result[model] = self._ts_detector.detect_with_sarima(
                    train_series,
                    test_series,
                )
            elif model.value == "prophet":
                train_series, test_series = self._split_series(
                    df,
                    target_col,
                    split_idx,
                )
                result[model] = self._ts_detector.detect_with_prophet(
                    train_series,
                    test_series,
                )
            else:
                raise ValueError(f"unknown model: {model}")  # noqa: TRY003

        return {"data": df, "result": result}

    @staticmethod
    def _split_series(
        df: pd.DataFrame,
        target_col: str,
        split_idx: int,
    ) -> tuple[pd.Series, pd.Series]:
        if target_col not in df.columns:
            raise ValueError(f"missing target column: {target_col}")  # noqa: TRY003

        series = df[target_col]
        series.index = df["timestamp"]
        return series.iloc[:split_idx], series.iloc[split_idx:]
