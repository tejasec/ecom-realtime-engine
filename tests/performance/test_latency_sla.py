"""
Performance Test: P99 Latency SLA Verification (< 100ms)
"""

import time
import pytest
import numpy as np
from fastapi.testclient import TestClient
from app.main import app

def test_recommendation_latency_sla():
    """
    Simulates 50 inference requests and verifies that P99 latency is strictly under 100ms.
    """
    client = TestClient(app)
    latencies = []

    payload = {
        "user_uuid": "usr_perf_bench",
        "candidates": [
            {"item_id": i, "category": "Electronics", "price": 50.0 + i}
            for i in range(1, 11)
        ]
    }

    for _ in range(50):
        t0 = time.perf_counter()
        resp = client.post("/recommend", json=payload)
        t1 = time.perf_counter()
        assert resp.status_code == 200
        latencies.append((t1 - t0) * 1000) # milliseconds

    p50 = np.percentile(latencies, 50)
    p95 = np.percentile(latencies, 95)
    p99 = np.percentile(latencies, 99)

    print(f"\nLatency Benchmarks - P50: {p50:.2f}ms, P95: {p95:.2f}ms, P99: {p99:.2f}ms")
    assert p99 < 100.0, f"Violation of P99 < 100ms SLA: P99 was {p99:.2f}ms"
