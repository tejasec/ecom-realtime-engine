"""
API Router Package
"""
from fastapi import APIRouter
from app.api.health import router as health_router
from app.api.search import router as search_router
from app.api.recommend import router as recommend_router
from app.api.feedback import router as feedback_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["Health & Observability"])
api_router.include_router(search_router, tags=["Semantic Search"])
api_router.include_router(recommend_router, tags=["Recommendation & CTR"])
api_router.include_router(feedback_router, tags=["User Feedback Telemetry"])
