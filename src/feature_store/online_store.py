"""
Online Feature Store Interface
Connects to Redis to serve sub-millisecond feature vectors to the FastAPI serving layer.
"""

from typing import Dict, Any, Optional
from app.core.redis_client import redis_client

class OnlineFeatureStore:
    def __init__(self):
        self.client = redis_client

    def get_online_features(self, entity_id: str) -> Dict[str, Any]:
        """Fetches low-latency user features."""
        return self.client.get_user_features(entity_id)

    def write_online_features(self, entity_id: str, features: Dict[str, Any]):
        """Persists updated online features."""
        self.client.set_user_features(entity_id, features)
