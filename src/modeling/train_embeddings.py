"""
Semantic Embedding Model & Indexing Pipeline
Generates dense vector embeddings using SentenceTransformers (e.g., all-MiniLM-L6-v2)
for semantic product catalog search.
"""

import logging
from typing import List, Dict, Any
import numpy as np
from config.settings import settings

logger = logging.getLogger("TrainEmbeddings")

class SemanticEmbeddingIndexer:
    def __init__(self, model_name: str = settings.EMBEDDING_MODEL_NAME):
        self.model_name = model_name
        self.model = None
        self._load_model()

    def _load_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Loaded SentenceTransformer model: {self.model_name}")
        except Exception as e:
            logger.warning(f"SentenceTransformer not loaded ({e}). Using deterministic vector encoder fallback.")
            self.model = None

    def encode(self, texts: List[str]) -> np.ndarray:
        """Encodes list of texts into normalized embedding vectors."""
        if self.model:
            embeddings = self.model.encode(texts, normalize_embeddings=True)
            return embeddings

        # Fallback deterministic pseudo-embeddings for fast testing
        vectors = []
        for text in texts:
            np.random.seed(abs(hash(text)) % (2**32))
            v = np.random.randn(settings.EMBEDDING_DIMENSION)
            vectors.append(v / np.linalg.norm(v))
        return np.array(vectors)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    indexer = SemanticEmbeddingIndexer()
    vecs = indexer.encode(["Wireless noise cancelling headphones", "Running shoes"])
    print(f"Encoded shape: {vecs.shape}")
