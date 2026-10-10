"""
Integration Test: Kafka Producer & Consumer Pipeline
"""

import pytest
from src.data_engineering.kafka_producer import ClickstreamProducer
from src.data_engineering.kafka_consumer import ClickstreamConsumer
from app.core.redis_client import redis_client

def test_producer_consumer_flow():
    producer = ClickstreamProducer()
    consumer = ClickstreamConsumer()

    # Generate synthetic event
    event = producer.generate_event()
    assert event["event_type"] in ["view", "click", "add_to_cart", "purchase"]
    assert "user_uuid" in event

    # Consume event and check Redis online update
    consumer.process_event(event)
    user_feats = redis_client.get_user_features(event["user_uuid"])
    assert user_feats is not None
