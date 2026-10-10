"""
Integration Test: Online & Offline Feature Store Interaction
"""

import pytest
from app.core.redis_client import redis_client
from src.feature_store.offline_store import OfflineFeatureStore

def test_redis_online_feature_store_read_write():
    test_uuid = "usr_integration_001"
    initial_features = {
        "user_uuid": test_uuid,
        "user_click_rate": 0.22,
        "price_sensitivity": 0.45,
        "recent_categories": ["Sports", "Outdoors"]
    }

    # Write
    redis_client.set_user_features(test_uuid, initial_features)

    # Read back
    retrieved = redis_client.get_user_features(test_uuid)
    assert retrieved["user_uuid"] == test_uuid
    assert retrieved["user_click_rate"] == 0.22
    assert "Sports" in retrieved["recent_categories"]

def test_offline_store_load():
    offline_store = OfflineFeatureStore()
    df = offline_store.load_historical_features()
    assert not df.empty
    assert "historical_ctr" in df.columns
