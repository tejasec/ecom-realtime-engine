"""
Streaming Event Producer
Generates high-throughput synthetic user clickstream events and publishes them to Kafka.
"""

import time
import json
import random
import logging
from typing import Dict, Any
from config.settings import settings

logger = logging.getLogger("KafkaProducer")

class ClickstreamProducer:
    def __init__(self, bootstrap_servers: str = settings.KAFKA_BOOTSTRAP_SERVERS, topic: str = settings.KAFKA_CLICK_TOPIC):
        self.topic = topic
        self.bootstrap_servers = bootstrap_servers
        self.producer = None
        self._init_producer()

    def _init_producer(self):
        try:
            from kafka import KafkaProducer
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                acks="all",
                retries=3
            )
            logger.info(f"Connected to Kafka broker at {self.bootstrap_servers}")
        except Exception as e:
            logger.warning(f"Kafka unavailable ({e}). Using local mock producer generator.")
            self.producer = None

    def generate_event(self) -> Dict[str, Any]:
        """Generates a synthetic user clickstream or view interaction."""
        user_id = f"usr_{random.randint(100, 999)}"
        product_id = random.randint(1, 50)
        event_type = random.choices(["view", "click", "add_to_cart", "purchase"], weights=[0.7, 0.2, 0.08, 0.02])[0]
        dwell_time = random.expovariate(1.0 / 45.0) if event_type in ["view", "click"] else 0.0

        return {
            "user_uuid": user_id,
            "product_id": product_id,
            "event_type": event_type,
            "dwell_time_seconds": round(dwell_time, 2),
            "session_id": f"sess_{random.randint(10000, 99999)}",
            "timestamp": time.time()
        }

    def emit_events(self, count: int = 10, delay_seconds: float = 0.1):
        """Streams events to Kafka or logs them."""
        logger.info(f"Emitting {count} events to topic '{self.topic}'...")
        events = []
        for _ in range(count):
            event = self.generate_event()
            events.append(event)
            if self.producer:
                self.producer.send(self.topic, value=event)
            logger.info(f"Published event: {event['event_type']} by {event['user_uuid']} on product {event['product_id']}")
            time.sleep(delay_seconds)

        if self.producer:
            self.producer.flush()
        return events

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    producer = ClickstreamProducer()
    producer.emit_events(count=5)
