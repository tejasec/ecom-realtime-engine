"""
KS-Test Drift Detector
======================
Compatibility shim forwarding to src.monitoring.ks_drift_detector.
This ensures root-level invocations and existing scripts continue working seamlessly.
"""

from src.monitoring.ks_drift_detector import (
    FeatureDriftDetector,
    simulate_drift_scenario,
    logger
)

if __name__ == "__main__":
    simulate_drift_scenario()
