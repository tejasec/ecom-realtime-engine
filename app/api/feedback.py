"""
Feedback Ingestion & Telemetry Endpoint
Receives user feedback (clicks, views, purchases) to feed streaming pipelines.
"""

import time
import logging
from fastapi import APIRouter
from app.schemas.recommendation import FeedbackEvent
from app.core.redis_client import redis_client
from app.core.metrics import REQUEST_COUNT

logger = logging.getLogger("FeedbackAPI")
router = APIRouter()

@router.post("/feedback", summary="Record User Interaction Feedback")
async def record_feedback(event: FeedbackEvent):
    """
    Ingests live feedback events.
    Updates the online feature cache and logs the event for streaming.
    """
    REQUEST_COUNT.labels(method="POST", endpoint="/feedback", status="200").inc()

    # Update real-time online features in Redis
    user_feats = redis_client.get_user_features(event.user_uuid)
    if event.event_type == "click":
        user_feats["user_click_rate"] = min(0.95, user_feats.get("user_click_rate", 0.15) * 1.05)
    redis_client.set_user_features(event.user_uuid, user_feats)

    logger.info(f"Feedback recorded: user={event.user_uuid}, item={event.item_id}, event={event.event_type}")

    return {
        "status": "acknowledged",
        "user_uuid": event.user_uuid,
        "event_type": event.event_type,
        "recorded_at": time.time()
    }
