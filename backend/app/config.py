"""Application settings loaded from environment / .env (pydantic-settings)."""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # LLM (Groq via OpenAI-compatible endpoint)
    groq_api_key: str = ""
    groq_base_url: str = "https://api.groq.com/openai/v1"

    # Auth
    jwt_secret: str = "change-me-to-a-long-random-string"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 days

    # Database
    database_url: str = "sqlite:///./career.db"
    agent_sessions_db: str = "./agent_sessions.db"

    # App
    app_name: str = "AI Career Counselor"
    cors_origins: str = "http://localhost:4200"
    embedding_model: str = "BAAI/bge-small-en-v1.5"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
