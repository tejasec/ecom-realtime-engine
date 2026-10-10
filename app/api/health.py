"""
Health Check & Prometheus Metrics Endpoints
"""

from fastapi import APIRouter, Response
from app.core.metrics import REQUEST_COUNT, generate_latest, CONTENT_TYPE_LATEST

router = APIRouter()

@router.get("/health", summary="Service Health Probe")
async def health_check():
    """Returns application liveness and readiness status."""
    return {
        "status": "healthy",
        "service": "aisd_ecommerce_api",
        "version": "1.0.0"
    }

@router.get("/metrics", summary="Prometheus Metrics Endpoint")
async def metrics_endpoint():
    """Exposes operational, latency, and ML performance metrics to Prometheus."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
