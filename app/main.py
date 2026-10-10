"""
FastAPI Serving Gateway Main Entrypoint
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import api_router
from app.core.database import db_pool
from app.core.redis_client import redis_client
from config.settings import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("FastAPIApp")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle context manager to connect and close resource pools."""
    logger.info("Initializing AISD E-Commerce Recommendation & Search Engine...")
    await db_pool.connect()
    redis_client.connect()
    yield
    logger.info("Shutting down resources...")
    await db_pool.disconnect()

app = FastAPI(
    title=settings.APP_NAME,
    description="Real-Time E-Commerce Recommendation & Search Engine showcasing complete AI System Design.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include All System Routers
app.include_router(api_router)

@app.get("/", summary="Root API Information")
async def root():
    return {
        "system": settings.APP_NAME,
        "status": "online",
        "documentation": "/docs",
        "health": "/health",
        "metrics": "/metrics"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=settings.DEBUG)
