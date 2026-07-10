from typing import Annotated, Any

from fastapi import Depends
from redis.asyncio import Redis

from src.common.application.interfaces.repository import IRedisRepository
from src.main.config import get_redis_connection


class RedisRepository(IRedisRepository):
    def __init__(self, redis: Annotated[Redis, Depends(get_redis_connection)]) -> None:
        self.__redis = redis

    async def get(self, key: str) -> Any:
        value = await self.__redis.get(key)

        return value

    async def insert_expires(self, key: str, value: Any, expires_in: int) -> None:
        await self.__redis.set(key, value, ex=expires_in)
