from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ClaimLens AI"
    environment: str = "development"
    api_version: str = "v1"
    groq_api_key: str | None = None
    groq_model: str = "llama-3.3-70b-versatile"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="CLAIMLENS_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
