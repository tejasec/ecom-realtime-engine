"""
Schemas for Semantic Vector Search (/search)
"""

from typing import List, Optional
from pydantic import BaseModel, Field

class SearchRequest(BaseModel):
    query: str = Field(..., description="Natural language search query")
    top_k: int = Field(default=10, ge=1, le=50, description="Number of results to retrieve")
    category_filter: Optional[str] = Field(default=None, description="Optional category filter")

class ProductItem(BaseModel):
    id: int
    title: str
    category: str
    price: float
    score: float = Field(..., description="Cosine similarity score (0 to 1)")

class SearchResponse(BaseModel):
    query: str
    total_results: int
    took_ms: float
    results: List[ProductItem]
