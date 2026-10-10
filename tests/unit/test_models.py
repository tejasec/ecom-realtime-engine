"""
Unit Test: Model Evaluation & Temporal Data Splitting
"""

import pandas as pd
import numpy as np
import pytest
from src.modeling.time_split import TimeSeriesSplitter
from src.modeling.evaluate import ModelEvaluator

def test_time_series_splitter_prevents_leakage():
    df = pd.DataFrame({
        "timestamp": pd.date_range(start="2026-01-01", periods=100, freq="D"),
        "val": range(100)
    })

    splitter = TimeSeriesSplitter(n_splits=3, test_size_ratio=0.2)
    splits = list(splitter.split(df, time_column="timestamp"))

    assert len(splits) == 3

    for train_df, test_df in splits:
        # Train timestamps must be strictly earlier than test timestamps
        assert train_df["timestamp"].max() < test_df["timestamp"].min()

def test_model_evaluator_metrics():
    y_true = [1, 0, 1, 1, 0, 0, 1, 0]
    y_prob = [0.9, 0.1, 0.8, 0.7, 0.2, 0.3, 0.85, 0.15]

    metrics = ModelEvaluator.evaluate_classifier(y_true, y_prob)
    assert metrics["roc_auc"] == 1.0
    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 1.0
