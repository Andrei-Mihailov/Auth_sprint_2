import json

from typing import Union

import backoff
from redis.asyncio import Redis
from redis.exceptions import ConnectionError as conn_err_redis

from .cache import Cache


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
    async def set(self, key, value, expire=None):
        await self.redis.set(key, value)
        if expire:
            await self.redis.expire(key, expire)

    @backoff.on_exception(backoff.expo, conn_err_redis, max_tries=5)
    async def delete(self, key):
        await self.redis.delete(key)

    @backoff.on_exception(backoff.expo, conn_err_redis, max_tries=5)
    async def set_user_data(self, user_id, user_data):
        await self.redis.hset("users", f"{user_id}", user_data)

    @backoff.on_exception(backoff.expo, conn_err_redis, max_tries=5)
    async def get_user_data(self, user_id):
        info: bytes = await self.redis.hget("users", user_id)
        return json.loads(info.decode())


redis: Union[RedisCache, None] = None


async def get_redis() -> RedisCache:
    return redis
