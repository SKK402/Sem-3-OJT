import asyncio
import json
import time
from typing import Any, Optional

from redis.asyncio import Redis

from app.config import get_settings


class Cache:
    def __init__(self, redis: Optional[Redis], ttl: int) -> None:
        self._redis = redis
        self._ttl = ttl
        self._fallback_store: dict[str, tuple[int, Any]] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        if self._redis:
            payload = await self._redis.get(key)
            return json.loads(payload) if payload else None
        async with self._lock:
            entry = self._fallback_store.get(key)
            if not entry:
                return None
            expires_at, value = entry
            if expires_at < int(time.time()):
                self._fallback_store.pop(key, None)
                return None
            return value

    async def set(self, key: str, value: Any) -> None:
        if self._redis:
            await self._redis.set(key, json.dumps(value), ex=self._ttl)
            return
        async with self._lock:
            expires_at = int(time.time()) + self._ttl
            self._fallback_store[key] = (expires_at, value)

    async def invalidate(self, key_prefix: str) -> None:
        if self._redis:
            keys = await self._redis.keys(f"{key_prefix}*")
            if keys:
                await self._redis.delete(*keys)
            return
        async with self._lock:
            for key in list(self._fallback_store.keys()):
                if key.startswith(key_prefix):
                    self._fallback_store.pop(key, None)


async def build_cache() -> Cache:
    settings = get_settings()
    redis = None
    try:
        redis = Redis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
        await redis.ping()
    except Exception:
        redis = None
    return Cache(redis, settings.cache_ttl_seconds)

