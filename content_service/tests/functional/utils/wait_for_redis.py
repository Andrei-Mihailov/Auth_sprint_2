import sys

from os import path
from redis import Redis
from redis.exceptions import ConnectionError as conn_err_redis
import backoff

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import settings


@backoff.on_exception(backoff.expo, conn_err_redis, max_tries=5)
def connect_to_redis():
    redis_client = Redis(host=settings.test_settings.redis_host,
                         port=settings.test_settings.redis_port)
    redis_client.info()


if __name__ == '__main__':
    connect_to_redis()
