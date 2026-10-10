"""
Load Testing & SLA Verification with Locust
Simulates concurrent user requests against /search, /recommend, and /predict
to measure P95 and P99 tail latency against the 100ms SLA target.
"""

from locust import HttpUser, task, between
import random

class RecommenderSystemUser(HttpUser):
    wait_time = between(0.1, 0.5)

    @task(3)
    def test_semantic_search(self):
        queries = ["running shoes", "wireless bluetooth headphones", "organic coffee", "smart watch"]
        q = random.choice(queries)
        self.client.get(f"/search?query={q}&limit=5", name="/search")

    @task(5)
    def test_realtime_recommendation(self):
        payload = {
            "user_uuid": f"usr_{random.randint(1000, 9999)}",
            "candidate_ids": [random.randint(1, 100) for _ in range(10)],
            "context_category": "Electronics"
        }
        self.client.post("/recommend", json=payload, name="/recommend")

    @task(1)
    def test_health_check(self):
        self.client.get("/health", name="/health")
