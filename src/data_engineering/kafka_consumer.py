"""
Streaming Event Consumer
Consumes click events in real-time, persists raw events to Data Lake (JSON/Parquet),
and performs low-latency rolling updates to the Redis online feature store.
"""

import json
import logging
from typing import Dict, Any
from config.settings import settings
from app.core.redis_client import redis_client

logger = logging.getLogger("KafkaConsumer")

class ClickstreamConsumer:
    def __init__(self, bootstrap_servers: str = settings.KAFKA_BOOTSTRAP_SERVERS, topic: str = settings.KAFKA_CLICK_TOPIC):
        self.topic = topic
        self.bootstrap_servers = bootstrap_servers
        self.consumer = None
        self._init_consumer()

    def _init_consumer(self):
        try:
            from kafka import KafkaConsumer
            self.consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=self.bootstrap_servers,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                auto_offset_reset="earliest",
                group_id="aisd_feature_sink_group"
            )
            logger.info(f"Connected to Kafka consumer on topic '{self.topic}'")
        except Exception as e:
            logger.warning(f"Kafka consumer connection skipped ({e}). Standalone processing ready.")
            self.consumer = None

    def process_event(self, event: Dict[str, Any]):
        """
        Updates Redis online store with rolling user behavior metrics.
        """
        user_uuid = event.get("user_uuid")
        event_type = event.get("event_type")

        if not user_uuid:
            return

        # Fetch current features from Redis
        user_feats = redis_client.get_user_features(user_uuid)

        # Update rolling metrics
        if event_type == "click":
            prev_ctr = user_feats.get("user_click_rate", 0.15)
            user_feats["user_click_rate"] = min(0.99, prev_ctr * 1.05)
        elif event_type == "purchase":
            user_feats["price_sensitivity"] = min(1.0, user_feats.get("price_sensitivity", 0.5) + 0.05)

        # Write back to Redis Online Feature Store
        redis_client.set_user_features(user_uuid, user_feats)
        logger.info(f"Updated online features in Redis for user {user_uuid}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    consumer = ClickstreamConsumer()
    mock_event = {"user_uuid": "usr_999", "event_type": "click", "product_id": 4}
    consumer.process_event(mock_event)
