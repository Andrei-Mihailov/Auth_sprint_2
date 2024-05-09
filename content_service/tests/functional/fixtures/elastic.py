import pytest_asyncio
import json
import asyncio
import sys
from os import path
import backoff

from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from elasticsearch.exceptions import NotFoundError
from elasticsearch.exceptions import ConnectionError as conn_err_es


sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from settings import test_settings


@pytest_asyncio.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@backoff.on_exception(backoff.expo, conn_err_es, max_tries=5)
@pytest_asyncio.fixture(name='es_client', scope='session')
async def es_client():
    es_client = AsyncElasticsearch(hosts=test_settings.es_host,
                                   verify_certs=False)
    yield es_client
    await es_client.close()


@backoff.on_exception(backoff.expo, conn_err_es, max_tries=5)
@pytest_asyncio.fixture(name='es_write_data')
def es_write_data(es_client: AsyncElasticsearch):
    async def inner(data: list[dict], index):
        if await es_client.indices.exists(index=index):
            await es_client.indices.delete(index=index)
        with open(f'testdata/{index}_schema.txt', "r", encoding="utf-8") as f:
            request_body = json.load(f)
        await es_client.indices.create(index=index,
                                       body=request_body)

        updated, errors = await async_bulk(client=es_client,
                                           actions=data,
                                           refresh="wait_for")

        if errors:
            raise Exception('Ошибка записи данных в Elasticsearch')
    return inner


@backoff.on_exception(backoff.expo, conn_err_es, max_tries=5)
@pytest_asyncio.fixture(name='request_by_id')
def request_by_id(es_client: AsyncElasticsearch):
    async def inner(index, id):
        try:
            doc = await es_client.get(index=index,
                                      id=id)
            return doc
        except NotFoundError:
            return None
    return inner


@backoff.on_exception(backoff.expo, conn_err_es, max_tries=5)
@pytest_asyncio.fixture(name='delete_from_es')
async def delete_from_es(es_client: AsyncElasticsearch):
    async def inner(index, id):
        try:
            await es_client.delete(index=index,
                                   id=id,
                                   refresh="wait_for")
        except NotFoundError:
            pass

    yield inner
