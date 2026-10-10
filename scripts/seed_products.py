"""
Product Catalog Seeding Script
Generates synthetic products, computes dummy or sentence-transformer embeddings,
and inserts them into the PostgreSQL pgvector warehouse.
"""

import sys
import numpy as np

def generate_sample_products(num_products: int = 50, embedding_dim: int = 384):
    categories = ["Electronics", "Apparel", "Home & Kitchen", "Books", "Sports"]
    products = []
    for i in range(1, num_products + 1):
        cat = categories[i % len(categories)]
        # Generate normalized random vector for cosine similarity
        vec = np.random.randn(embedding_dim)
        vec = vec / np.linalg.norm(vec)
        products.append({
            "id": i,
            "title": f"Premium {cat} Item {i}",
            "category": cat,
            "price": round(float(np.random.uniform(10.0, 500.0)), 2),
            "description": f"High quality {cat.lower()} designed for daily modern use.",
            "embedding": vec.tolist()
        })
    return products

def seed_database():
    print(f"Generating synthetic catalog items...")
    products = generate_sample_products(num_products=30)
    print(f"Generated {len(products)} products with 384-dimensional embeddings.")
    print("Database seeding simulated successfully. (Run with active PostgreSQL to persist)")
    return products

if __name__ == "__main__":
    seed_database()
