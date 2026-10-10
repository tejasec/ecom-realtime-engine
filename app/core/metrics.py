"""
Prometheus Metrics Instrumentation
Tracks operational latency percentiles (P95, P99), throughput, and predictions.
"""

try:
    from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
except ImportError:
    CONTENT_TYPE_LATEST = "text/plain; version=0.0.4; charset=utf-8"
    def generate_latest():
        return b"# Mock Prometheus metrics for testing without prometheus_client\naisd_http_requests_total 1\n"

    class _MockMetric:
        def __init__(self, *args, **kwargs):
            pass
        def labels(self, *args, **kwargs):
            return self
        def inc(self, amount=1):
            pass
        def set(self, val):
            pass
        def observe(self, val):
            pass
        def time(self):
            class _Timer:
                def __enter__(self): return self
                def __exit__(self, *args): pass
            return _Timer()

    Counter = Histogram = Gauge = _MockMetric

# Operational Metrics
REQUEST_COUNT = Counter(
    "aisd_http_requests_total",
    "Total HTTP Requests received",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "aisd_http_request_duration_seconds",
    "HTTP Request Latency in seconds",
    ["endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 1.0) # sub-100ms buckets
)

# AI System Specific Metrics
INFERENCE_LATENCY = Histogram(
    "aisd_model_inference_duration_seconds",
    "Pure Model Inference Execution Time in seconds",
    ["model_type"],
    buckets=(0.001, 0.005, 0.01, 0.02, 0.05, 0.1)
)

FEATURE_LOOKUP_LATENCY = Histogram(
    "aisd_redis_feature_fetch_duration_seconds",
    "Latency of fetching online user features from Redis in seconds",
    buckets=(0.0005, 0.001, 0.002, 0.005, 0.01)
)

PREDICTION_CTR_GAUGE = Gauge(
    "aisd_last_predicted_ctr_score",
    "Most recent predicted Click-Through Rate probability score"
)

ACTIVE_DRIFT_ALERT = Gauge(
    "aisd_feature_drift_alert_active",
    "Binary indicator (1 or 0) indicating whether statistical feature drift is detected"
)
