"""
Unit Test: Kolmogorov-Smirnov Statistical Drift Detector
"""

import numpy as np
import pytest
from src.monitoring.ks_drift_detector import FeatureDriftDetector

def test_ks_drift_detector_stable_distribution():
    np.random.seed(42)
    sample_size = 500
    baseline = np.random.normal(loc=0.15, scale=0.05, size=sample_size)
    # Serving identical distribution
    serving = np.random.normal(loc=0.15, scale=0.05, size=sample_size)

    detector = FeatureDriftDetector(alpha=0.05)
    ks_stat, p_val, is_drift = detector.evaluate_feature_drift(baseline, serving)

    assert not is_drift, f"Expected no drift, but got p_val={p_val}"
    assert p_val >= 0.05

def test_ks_drift_detector_flags_significant_drift():
    np.random.seed(42)
    sample_size = 500
    baseline = np.random.normal(loc=0.15, scale=0.05, size=sample_size)
    # Shifted distribution (simulated concept drift)
    serving = np.random.normal(loc=0.35, scale=0.05, size=sample_size)

    detector = FeatureDriftDetector(alpha=0.05)
    ks_stat, p_val, is_drift = detector.evaluate_feature_drift(baseline, serving)

    assert is_drift, "Expected drift to be detected"
    assert p_val < 0.05

def test_full_dataset_drift_analysis():
    np.random.seed(42)
    n = 300
    baseline_data = {
        "feat_a": np.random.normal(0, 1, n).tolist(),
        "feat_b": np.random.uniform(0, 1, n).tolist()
    }
    # One stable, one shifted
    serving_data = {
        "feat_a": np.random.normal(0, 1, n).tolist(),
        "feat_b": np.random.uniform(2, 3, n).tolist()
    }

    detector = FeatureDriftDetector(alpha=0.05)
    report = detector.run_drift_analysis(baseline_data, serving_data)

    assert report["overall_drift_flag"] is True
    assert report["drifted_features_count"] == 1
    assert report["action_recommended"] == "TRIGGER_AUTOMATED_CHECKPOINT_RETRAINING"
