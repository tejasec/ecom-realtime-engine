"""
System Configuration Settings (Pydantic BaseSettings)
Loads environment variables configured in docker-compose.yml or local .env file.
"""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # App General Settings
    APP_NAME: str = "Real-Time E-Commerce Recommendation & Search Engine"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000

    # PostgreSQL / pgvector Warehouse Settings
    POSTGRES_USER: str = Field(default="aisd_user", alias="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(default="aisd_password", alias="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field(default="aisd_warehouse", alias="POSTGRES_DB")
    POSTGRES_HOST: str = Field(default="localhost", alias="POSTGRES_HOST")
    POSTGRES_PORT: int = Field(default=5432, alias="POSTGRES_PORT")

    @property
    def postgres_uri(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Redis Online Feature Store Settings
    REDIS_HOST: str = Field(default="localhost", alias="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, alias="REDIS_PORT")
    REDIS_DB: int = 0

    # Kafka Streaming Settings
    KAFKA_BOOTSTRAP_SERVERS: str = Field(default="localhost:29092", alias="KAFKA_BOOTSTRAP_SERVERS")
    KAFKA_CLICK_TOPIC: str = "user-clickstream"
    KAFKA_FEEDBACK_TOPIC: str = "user-feedback"

    # ML & Feature Store Settings
    EMBEDDING_DIMENSION: int = 384  # Matches all-MiniLM-L6-v2
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    DRIFT_SIGNIFICANCE_ALPHA: float = 0.05
    LATENCY_SLA_MS: float = 100.0  # P99 latency target

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")

settings = Settings()
