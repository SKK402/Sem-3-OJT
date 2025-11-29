from redis.asyncio import Redis

from app.cache import Cache, build_cache
from app.database import get_db_session
from app.services.synonyms import SynonymService

# FastAPI dependencies will import callables from here.

cache_instance: Cache | None = None
synonym_service = SynonymService(
    mapping={
        "laptop": {"notebook", "ultrabook"},
        "sneaker": {"shoe"},
        "hoodie": {"sweatshirt"},
    }
)


async def get_cache() -> Cache:
    global cache_instance
    if not cache_instance:
        cache_instance = await build_cache()
    return cache_instance


async def get_synonyms() -> SynonymService:
    return synonym_service

