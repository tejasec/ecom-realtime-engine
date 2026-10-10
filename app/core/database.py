"""
PostgreSQL & pgvector Database Adapter
Manages connection pooling and vector similarity queries.
"""

import logging
from typing import List, Dict, Any, Optional
from config.settings import settings

logger = logging.getLogger("Database")

class DatabasePool:
    def __init__(self):
        self.is_connected = False

    async def connect(self):
        """Initializes database connection pool."""
        try:
            import asyncpg
            self.pool = await asyncpg.create_pool(
                dsn=settings.postgres_uri,
                min_size=2,
                max_size=10
            )
            self.is_connected = True
            logger.info("Connected to PostgreSQL warehouse.")
        except Exception as e:
            logger.warning(f"Could not connect to PostgreSQL ({e}). Operating in standalone/mock mode.")
            self.is_connected = False

    async def disconnect(self):
        """Closes database connection pool."""
        if self.is_connected and hasattr(self, "pool"):
            await self.pool.close()
            self.is_connected = False

    async def search_similar_products(self, query_vector: List[float], top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Executes Cosine Similarity vector search using pgvector HNSW index.
        """
        if not self.is_connected:
            # Fallback mock for testing and development
            return [
                {
                    "id": i,
                    "title": f"Mock Semantic Match {i}",
                    "category": "Electronics",
                    "price": 99.99 + (i * 10),
                    "score": round(1.0 - (i * 0.05), 4)
                }
                for i in range(1, top_k + 1)
            ]

        query = """
            SELECT id, title, category, price, (1 - (embedding <=> $1)) AS score
            FROM products
            ORDER BY embedding <=> $1 ASC
            LIMIT $2;
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, str(query_vector), top_k)
            return [dict(r) for r in rows]

db_pool = DatabasePool()
