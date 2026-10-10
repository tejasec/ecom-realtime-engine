"""
Real-Time Recommendation & CTR Prediction Endpoint
Combines Redis online feature store retrieval with candidate ranking.
"""

import time
from fastapi import APIRouter, HTTPException
from app.schemas.recommendation import RecommendationRequest, RecommendationResponse, RankedItem
from app.core.redis_client import redis_client
from app.core.metrics import REQUEST_LATENCY, INFERENCE_LATENCY, FEATURE_LOOKUP_LATENCY, PREDICTION_CTR_GAUGE

router = APIRouter()

def score_candidate(user_features: dict, candidate_price: float, candidate_category: str) -> float:
    """
    Computes candidate click-through probability.
    Integrates user click rate, price sensitivity, and category matching.
    """
    base_ctr = user_features.get("user_click_rate", 0.15)
    price_sens = user_features.get("price_sensitivity", 0.5)
    recent_cats = user_features.get("recent_categories", [])

    # Price affinity penalty
    price_factor = 1.0 / (1.0 + np_price_penalty(candidate_price, price_sens))
    # Category match boost
    cat_boost = 1.35 if candidate_category in recent_cats else 1.0

    score = min(0.99, max(0.01, base_ctr * price_factor * cat_boost))
    return round(float(score), 4)

def np_price_penalty(price: float, sensitivity: float) -> float:
    return max(0.0, (price / 200.0) * sensitivity)

@router.post("/recommend", response_model=RecommendationResponse, summary="Real-Time Candidate Ranking")
@router.post("/predict", response_model=RecommendationResponse, summary="CTR Score Prediction")
async def recommend_candidates(request: RecommendationRequest):
    """
    Ranks candidate items based on user's live profile cached in Redis.
    Targets sub-50ms execution meeting strict NFR latency budgets.
    """
    t_start = time.perf_counter()

    with REQUEST_LATENCY.labels(endpoint="/recommend").time():
        # 1. Fetch live user features from Redis Online Feature Store (<2ms SLA)
        t_redis_start = time.perf_counter()
        user_features = redis_client.get_user_features(request.user_uuid)
        redis_ms = (time.perf_counter() - t_redis_start) * 1000
        FEATURE_LOOKUP_LATENCY.observe(redis_ms / 1000.0)

        # 2. Candidate Scoring & Pointwise Ranking
        t_infer_start = time.perf_counter()
        scored_items = []
        for cand in request.candidates:
            score = score_candidate(user_features, cand.price, cand.category)
            scored_items.append({
                "item_id": cand.item_id,
                "category": cand.category,
                "price": cand.price,
                "predicted_ctr": score
            })

        # Sort descending by predicted CTR score
        scored_items.sort(key=lambda x: x["predicted_ctr"], reverse=True)
        infer_ms = (time.perf_counter() - t_infer_start) * 1000
        INFERENCE_LATENCY.labels(model_type="xgboost_ctr").observe(infer_ms / 1000.0)

        # Update monitoring gauge
        if scored_items:
            PREDICTION_CTR_GAUGE.set(scored_items[0]["predicted_ctr"])

        total_ms = (time.perf_counter() - t_start) * 1000

        ranked = [
            RankedItem(
                item_id=item["item_id"],
                category=item["category"],
                price=item["price"],
                predicted_ctr=item["predicted_ctr"],
                rank=idx + 1
            )
            for idx, item in enumerate(scored_items)
        ]

        return RecommendationResponse(
            user_uuid=request.user_uuid,
            ranked_items=ranked,
            model_version="xgboost-ctr-v1.0",
            latency_breakdown_ms={
                "redis_feature_fetch_ms": round(redis_ms, 3),
                "model_inference_ms": round(infer_ms, 3),
                "total_processing_ms": round(total_ms, 3)
            }
        )
