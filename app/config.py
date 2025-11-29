from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/products"
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl_seconds: int = 120
    max_page_size: int = 50
    default_page_size: int = 12
    enable_background_jobs: bool = False
    app_name: str = "product-search-api"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

