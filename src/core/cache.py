from typing import Any, Optional, Type, TypeVar

from pydantic import TypeAdapter
from redis.asyncio import Redis

from src.config import settings
from src.core.redis import get_redis_client

T = TypeVar("T")


class CacheService:
    def __init__(self):
        self._redis: Optional[Redis] = None

    @property
    def redis(self) -> Redis:
        if not self._redis:
            self._redis = get_redis_client()
        return self._redis

    async def get(self, key: str, type_model: Type[T]) -> Optional[T]:
        """
        Get value from cache and deserialize into type_model.
        Returns None if key not found or error occurs.
        """
        if not settings.CACHE_ENABLED:
            return None

        try:
            data = await self.redis.get(key)
            if not data:
                return None

            adapter = TypeAdapter(type_model)
            return adapter.validate_json(data)
        except Exception:
            # Log error ideally
            return None

    async def set(self, key: str, value: Any, ttl: int = settings.CACHE_TTL):
        """
        Serialize value to JSON and save to cache with TTL.
        """
        if not settings.CACHE_ENABLED:
            return

        try:
            # Create adapter for the specific type of value
            adapter = TypeAdapter(type(value))
            # export to json string
            json_data = adapter.dump_json(value).decode("utf-8")
            await self.redis.set(key, json_data, ex=ttl)
        except Exception:
            pass

    async def delete(self, key: str):
        if not settings.CACHE_ENABLED:
            return
        try:
            await self.redis.delete(key)
        except Exception:
            pass

    async def delete_pattern(self, pattern: str):
        """
        Delete all keys matching the pattern.
        Uses SCAN to be non-blocking.
        """
        if not settings.CACHE_ENABLED:
            return

        try:
            cursor = 0
            while True:
                cursor, keys = await self.redis.scan(cursor, match=pattern, count=100)
                if keys:
                    await self.redis.delete(*keys)
                if cursor == 0:
                    break
        except Exception:
            pass
