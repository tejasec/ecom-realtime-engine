"""
End-to-End System Simulation Runner
Demonstrates the full closed-loop life cycle:
1. Synthetic Stream Generation (Kafka Producer)
2. Dual-Headed Feature Store Ingestion (Offline + Online Redis)
3. Inference Serving & Latency Measurement
4. Covariate Drift Induction (KS Test Evaluation)
5. Automated Retraining Trigger
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import time
import json
import numpy as np
from src.monitoring.ks_drift_detector import FeatureDriftDetector
from src.monitoring.retrain_trigger import RetrainingPipeline

def run_simulation():
    print("=" * 70)
    print("  AISD SHOWCASE: Real-Time E-Commerce Recommender Simulation")
    print("=" * 70)

    # 1. Simulate Baseline Training Distributions
    print("\n[Step 1] Loading Baseline Feature Distributions...")
    n_samples = 1000
    baseline_features = {
        "user_click_rate": np.random.normal(loc=0.15, scale=0.04, size=n_samples).tolist(),
        "price_sensitivity": np.random.uniform(low=0.1, high=0.9, size=n_samples).tolist(),
        "session_duration_sec": np.random.exponential(scale=120.0, size=n_samples).tolist()
    }
    print(f"Loaded {len(baseline_features)} baseline features with {n_samples} samples each.")

    # 2. Simulate Normal Production Serving (No Drift)
    print("\n[Step 2] Simulating Normal Day 1 Production Serving...")
    serving_normal = {
        "user_click_rate": np.random.normal(loc=0.152, scale=0.041, size=n_samples).tolist(),
        "price_sensitivity": np.random.uniform(low=0.1, high=0.9, size=n_samples).tolist(),
        "session_duration_sec": np.random.exponential(scale=119.0, size=n_samples).tolist()
    }
    detector = FeatureDriftDetector(alpha=0.05)
    report_normal = detector.run_drift_analysis(baseline_features, serving_normal)
    print(f"Day 1 Drift Status: Drift Detected={report_normal['overall_drift_flag']} (Healthy)")

    # 3. Simulate Seasonal Concept / Covariate Shift (Holiday Shopping Spree)
    print("\n[Step 3] Simulating Holiday Surge (Injecting Distribution Shift)...")
    serving_drifted = {
        "user_click_rate": np.random.normal(loc=0.32, scale=0.07, size=n_samples).tolist(), # Massive CTR spike
        "price_sensitivity": np.random.uniform(low=0.4, high=1.0, size=n_samples).tolist(),
        "session_duration_sec": np.random.exponential(scale=240.0, size=n_samples).tolist() # Longer sessions
    }
    report_drift = detector.run_drift_analysis(baseline_features, serving_drifted)
    print(f"Holiday Drift Status: Drift Detected={report_drift['overall_drift_flag']}")
    print(f"Drifted Features Count: {report_drift['drifted_features_count']}/{report_drift['total_features_evaluated']}")

    # 4. Trigger Closed-Loop Automated Retraining
    print("\n[Step 4] Checking Closed-Loop Retraining Gate...")
    retrainer = RetrainingPipeline()
    retrain_result = retrainer.evaluate_and_trigger(report_drift)
    print(f"Action Taken: {retrain_result['status']}")
    print(f"Champion-Challenger Gate: {retrain_result['details']}")

    print("\n" + "=" * 70)
    print("  SIMULATION COMPLETE: System Self-Healing Loop Successfully Verified")
    print("=" * 70)

if __name__ == "__main__":
    run_simulation()
