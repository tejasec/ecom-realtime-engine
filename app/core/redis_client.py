"""
Redis Online Feature Store Adapter
Provides sub-millisecond retrieval of user features during live inference.
"""

import json
import logging
from typing import Dict, Any, Optional
from config.settings import settings

logger = logging.getLogger("RedisStore")

class RedisFeatureClient:
    def __init__(self):
        self.client = None
        self.is_connected = False
        self._local_cache = {}

    def connect(self):
        """Initializes connection to Redis instance."""
        try:
            import redis
            self.client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True,
                socket_timeout=1.0
            )
            self.client.ping()
            self.is_connected = True
            logger.info("Connected to Redis online feature store.")
        except Exception as e:
            logger.warning(f"Could not connect to Redis ({e}). Using local in-memory mock feature store.")
            self.is_connected = False

    def get_user_features(self, user_uuid: str) -> Dict[str, Any]:
        """
        Retrieves real-time user features for online CTR scoring.
        """
        key = f"user:{user_uuid}:features"
        if self.is_connected and self.client:
            try:
                data = self.client.get(key)
                if data:
                    return json.loads(data)
            except Exception as e:
                logger.error(f"Error fetching features from Redis: {e}")

        # Check local cache or return standard default prior
        return self._local_cache.get(key, {
            "user_uuid": user_uuid,
            "user_click_rate": 0.15,
            "price_sensitivity": 0.5,
            "recent_categories": ["Electronics", "Apparel"],
            "session_duration_sec": 120.0
        })

    def set_user_features(self, user_uuid: str, features: Dict[str, Any], ttl_seconds: int = 86400):
        """
        Updates real-time user features with a specified time-to-live.
        """
        key = f"user:{user_uuid}:features"
        if self.is_connected and self.client:
            try:
                self.client.setex(key, ttl_seconds, json.dumps(features))
                return
            except Exception as e:
                logger.error(f"Error writing features to Redis: {e}")

        self._local_cache[key] = features

redis_client = RedisFeatureClient()
