from typing import Union

import backoff
from redis.asyncio import Redis
from redis.exceptions import ConnectionError as conn_err_redis

from .cache import Cache


CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class RedisCache(Cache):
    def __init__(self):
        self.redis: Union[Redis, None]

    @backoff.on_exception(backoff.expo, conn_err_redis, max_tries=5)
    async def get(self, key) -> Union[bytes, None]:
        data = await self.redis.get(key)
        if not data:
            return None
        return data

    @backoff.on_exception(backoff.expo, conn_err_redis, max_tries=5)
    async def set(self, key, value, expire):
        await self.redis.set(key, value, expire)


redis: Union[RedisCache, None] = None


async def get_redis() -> RedisCache:
    return redis
