import enum
import tempfile
from typing import Any, Dict

import numpy as np
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
            return self._serialize_result({"data": df, "result": None})

        if len(df) < 2:
            return self._serialize_result({"data": df, "result": None})

        split_idx = int(len(df) * train_ratio)
        split_idx = min(max(1, split_idx), len(df) - 1)
        train_df = df.iloc[:split_idx]
        test_df = df.iloc[split_idx:]
        result = {}
        for model in models:
            if model.value == "isolation_forest":
                result[model.value] = self._ts_detector.detect_with_isolation_forest_ts(
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
                result[model.value] = self._ts_detector.detect_with_arima(
                    train_series,
                    test_series,
                )
            elif model.value == "sarima":
                train_series, test_series = self._split_series(
                    df,
                    target_col,
                    split_idx,
                )
                result[model.value] = self._ts_detector.detect_with_sarima(
                    train_series,
                    test_series,
                )
            elif model.value == "prophet":
                train_series, test_series = self._split_series(
                    df,
                    target_col,
                    split_idx,
                )
                result[model.value] = self._ts_detector.detect_with_prophet(
                    train_series,
                    test_series,
                )
            else:
                raise ValueError(f"unknown model: {model}")  # noqa: TRY003
        return self._serialize_result(result)

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

    @staticmethod
    def _serialize_result(payload: Any) -> dict[str, Any]:
        def to_jsonable(value: Any) -> Any:
            if isinstance(value, pd.DataFrame):
                return value.to_dict(orient="records")
            if isinstance(value, pd.Series):
                return [
                    {"timestamp": str(idx), "value": to_jsonable(val)}
                    for idx, val in value.items()
                ]
            if isinstance(value, np.ndarray):
                return [to_jsonable(v) for v in value.tolist()]
            if isinstance(value, np.generic):
                return value.item()
            if isinstance(value, pd.Timestamp):
                return value.isoformat()
            if isinstance(value, dict):
                return {
                    str(k): to_jsonable(v)
                    for k, v in value.items()
                    if k != "model"
                }
            if isinstance(value, (list, tuple)):
                return [to_jsonable(v) for v in value]
            return value

        return to_jsonable(payload)
