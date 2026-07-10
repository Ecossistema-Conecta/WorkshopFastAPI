import redis.asyncio as redis
from redis.asyncio import Redis

from .settings import settings

redis_connection: Redis = redis.from_url(settings.REDIS_URL, decode_responses=True)


async def get_redis_connection() -> Redis:
    return redis_connection
