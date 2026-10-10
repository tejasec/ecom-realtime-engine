"""
Schemas for Real-Time Recommendation & CTR Prediction (/recommend, /predict, /feedback)
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class CandidateItem(BaseModel):
    item_id: int
    category: str
    price: float

class RecommendationRequest(BaseModel):
    user_uuid: str = Field(..., description="Pseudonymized user identifier")
    candidates: List[CandidateItem] = Field(..., min_length=1, description="Candidate items to rank")
    context_category: Optional[str] = Field(default=None, description="Current browsing context")

class RankedItem(BaseModel):
    item_id: int
    category: str
    price: float
    predicted_ctr: float = Field(..., description="Estimated click-through probability")
    rank: int

class RecommendationResponse(BaseModel):
    user_uuid: str
    ranked_items: List[RankedItem]
    model_version: str
    latency_breakdown_ms: Dict[str, float]

class FeedbackEvent(BaseModel):
    user_uuid: str
    item_id: int
    event_type: str = Field(..., description="'view', 'click', or 'purchase'")
    dwell_time_seconds: float = Field(default=0.0)
    session_id: str
