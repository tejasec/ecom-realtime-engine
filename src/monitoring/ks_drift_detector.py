"""
KS-Test Drift Detector
======================
This service monitors live inference feature distributions against baseline 
training features using the two-sample Kolmogorov-Smirnov (KS) test. 

If statistically significant covariate shift is detected (p-value < alpha), 
it flags feature drift and triggers an automated retraining workflow.
"""

import json
import logging
from typing import Dict, List, Any, Tuple
import numpy as np
from scipy import stats

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("DriftDetector")

class FeatureDriftDetector:
    def __init__(self, alpha: float = 0.05):
        """
        Initialize the Kolmogorov-Smirnov Feature Drift Detector.
        
        :param alpha: Significance threshold for statistical hypothesis testing (default 0.05).
        """
        self.alpha = float(alpha)

    def evaluate_feature_drift(
        self, baseline_data: np.ndarray, serving_data: np.ndarray
    ) -> Tuple[float, float, bool]:
        """
        Performs the two-sample Kolmogorov-Smirnov test on a single feature array.
        
        Null Hypothesis (H0): Baseline and Serving features come from the same distribution.
        Alternative Hypothesis (H1): Baseline and Serving features come from different distributions.
        
        :return: Tuple of (ks_statistic, p_value, is_drift_detected)
        """
        ks_stat, p_value = stats.ks_2samp(baseline_data, serving_data)
        is_drift = bool(p_value < self.alpha)
        return float(ks_stat), float(p_value), is_drift

    def run_drift_analysis(
        self, 
        baseline_dataset: Dict[str, List[float]], 
        serving_dataset: Dict[str, List[float]]
    ) -> Dict[str, Any]:
        """
        Runs drift detection across all numerical features in the dataset.
        
        :param baseline_dataset: Dictionary mapping feature names to training feature arrays.
        :param serving_dataset: Dictionary mapping feature names to live serving feature arrays.
        :return: Summary report containing per-feature metrics and system retrain status.
        """
        report = {
            "significance_level_alpha": self.alpha,
            "overall_drift_flag": False,
            "drifted_features_count": 0,
            "total_features_evaluated": len(baseline_dataset),
            "feature_details": {}
        }

        drifted_count = 0

        for feature_name, baseline_vals in baseline_dataset.items():
            if feature_name not in serving_dataset:
                logger.warning(f"Feature '{feature_name}' missing from serving dataset. Skipping.")
                continue

            baseline_arr = np.array(baseline_vals, dtype=np.float64)
            serving_arr = np.array(serving_dataset[feature_name], dtype=np.float64)

            ks_stat, p_val, is_drift = self.evaluate_feature_drift(baseline_arr, serving_arr)

            if is_drift:
                drifted_count += 1
                logger.warning(
                    f"🚨 DRIFT DETECTED in '{feature_name}'! "
                    f"KS-Stat: {ks_stat:.4f}, p-value: {p_val:.4e} (p < {self.alpha})"
                )
            else:
                logger.info(
                    f"✅ Stable feature '{feature_name}'. "
                    f"KS-Stat: {ks_stat:.4f}, p-value: {p_val:.4f}"
                )

            report["feature_details"][feature_name] = {
                "ks_statistic": round(ks_stat, 5),
                "p_value": round(p_val, 5),
                "drift_detected": is_drift
            }

        report["drifted_features_count"] = int(drifted_count)
        if drifted_count > 0:
            report["overall_drift_flag"] = True
            report["action_recommended"] = "TRIGGER_AUTOMATED_CHECKPOINT_RETRAINING"
        else:
            report["overall_drift_flag"] = False
            report["action_recommended"] = "NO_ACTION_REQUIRED_SYSTEM_HEALTHY"

        return report

# ============================================================================
# Simulation / Execution Example
# ============================================================================
def simulate_drift_scenario():
    print("\n========================================================")
    print("  SIMULATION: Testing KS-Drift Detector on Live Data   ")
    print("========================================================\n")
    
    np.random.seed(42)
    sample_size = 1000

    # 1. Generate Baseline Data (e.g., Training Distribution)
    baseline_data = {
        "user_click_rate": np.random.normal(loc=0.15, scale=0.05, size=sample_size).tolist(),
        "price_sensitivity_score": np.random.uniform(low=0.0, high=1.0, size=sample_size).tolist(),
        "session_duration_sec": np.random.exponential(scale=120.0, size=sample_size).tolist()
    }

    # 2. Generate Live Serving Data (Simulating a seasonal concept drift on user_click_rate)
    serving_data = {
        "user_click_rate": np.random.normal(loc=0.28, scale=0.06, size=sample_size).tolist(),  # DRIFT: Higher CTR
        "price_sensitivity_score": np.random.uniform(low=0.0, high=1.0, size=sample_size).tolist(),  # STABLE
        "session_duration_sec": np.random.exponential(scale=118.0, size=sample_size).tolist()  # STABLE
    }

    detector = FeatureDriftDetector(alpha=0.05)
    drift_report = detector.run_drift_analysis(baseline_data, serving_data)

    print("\n--- FINAL DRIFT EVALUATION REPORT ---")
    print(json.dumps(drift_report, indent=2))
    return drift_report

if __name__ == "__main__":
    simulate_drift_scenario()
