from typing import Union

import backoff
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import ConnectionError as conn_err_es

from .storage import Storage


class ElasticStorage(Storage):
    def __init__(self):
        self.elastic: Union[AsyncElasticsearch, None]

    @backoff.on_exception(backoff.expo, conn_err_es, max_tries=5)
    async def get(self, index: str, id: str) -> dict:
        return await self.elastic.get(index, id)

    @backoff.on_exception(backoff.expo, conn_err_es, max_tries=5)
    async def search(self, index: str, body: dict) -> dict:
        return await self.elastic.search(index, body)


es: Union[ElasticStorage, None] = None


async def get_elastic() -> ElasticStorage:
    return es
