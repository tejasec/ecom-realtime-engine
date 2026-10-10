"""
Integration Tests for FastAPI Serving Layer
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_metrics_endpoint(client):
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "aisd_http_requests_total" in response.text

def test_semantic_search_endpoint(client):
    response = client.get("/search?query=running+shoes&limit=3")
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "running shoes"
    assert len(data["results"]) == 3
    assert data["took_ms"] > 0

def test_recommendation_endpoint(client):
    payload = {
        "user_uuid": "usr_test_101",
        "candidates": [
            {"item_id": 1, "category": "Electronics", "price": 49.99},
            {"item_id": 2, "category": "Books", "price": 19.99}
        ]
    }
    response = client.post("/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["user_uuid"] == "usr_test_101"
    assert len(data["ranked_items"]) == 2
    assert "latency_breakdown_ms" in data

def test_feedback_endpoint(client):
    payload = {
        "user_uuid": "usr_test_101",
        "item_id": 1,
        "event_type": "click",
        "dwell_time_seconds": 15.2,
        "session_id": "sess_12345"
    }
    response = client.post("/feedback", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "acknowledged"
