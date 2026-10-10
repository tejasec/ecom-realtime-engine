-- ============================================================================
-- Relational Warehouse & Vector Store Schema Initialization
-- ============================================================================

-- 1. Enable the pgvector extension for dense vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Products Catalog with Vector Embeddings (384-d for all-MiniLM-L6-v2)
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    description TEXT,
    embedding vector(384),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Users Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    user_uuid VARCHAR(64) UNIQUE NOT NULL,
    age INT,
    price_sensitivity_score FLOAT DEFAULT 0.5,
    preferred_category VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. User Interactions & Clickstream (Lake to Warehouse transformation)
CREATE TABLE IF NOT EXISTS interactions (
    id BIGSERIAL PRIMARY KEY,
    user_uuid VARCHAR(64) NOT NULL,
    product_id INT REFERENCES products(id),
    event_type VARCHAR(50) NOT NULL, -- 'view', 'search_click', 'add_to_cart', 'purchase'
    dwell_time_seconds FLOAT DEFAULT 0.0,
    session_id VARCHAR(64) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Offline Feature Store Snapshots
CREATE TABLE IF NOT EXISTS offline_features (
    user_uuid VARCHAR(64) PRIMARY KEY,
    historical_ctr FLOAT DEFAULT 0.0,
    total_views INT DEFAULT 0,
    total_clicks INT DEFAULT 0,
    avg_price_viewed FLOAT DEFAULT 0.0,
    favorite_category VARCHAR(100),
    last_active TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 6. Indexes for Performance and Low-Latency Serving
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_interactions_user_time ON interactions(user_uuid, timestamp DESC);

-- Vector Cosine Similarity Index (HNSW for high-speed sub-100ms P99 latency)
CREATE INDEX IF NOT EXISTS idx_products_embedding_hnsw 
ON products USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
