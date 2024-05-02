import json
from abc import ABC, abstractmethod
from typing import Union

import backoff
from redis.exceptions import ConnectionError as conn_err_redis
from elasticsearch import NotFoundError
from elasticsearch.exceptions import ConnectionError as conn_err_es

from db.elastic import ElasticStorage
from db.redis import RedisCache
from models.models import Film, Genre, Person
from .utils.response_params import prepare_fields_for_response

CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class AbstractBaseService(ABC):

    @abstractmethod
    async def get_by_id(self, id):
        pass

    @abstractmethod
    async def _get_from_elastic(self, id):
        pass

    @abstractmethod
    async def _get_from_cache(self, key):
        pass

    @abstractmethod
    async def _put_to_cache(self, key, value, expire):
        pass

    @abstractmethod
    async def execute_query_storage(self, query):
        pass


class BaseService(AbstractBaseService):
    def __init__(self, cache: RedisCache, storage: ElasticStorage):
        self.cache = cache
        self.storage = storage
        self.model = None
        self.relation_model = None
        self.index = ''

    async def get_by_id(self, id: str) -> Union[Film, Genre, Person, None]:
        instance = await self._get_from_cache(id)
        if not instance:
            instance = await self._get_from_elastic(id)
            if not instance:
                return None
        return instance

    @backoff.on_exception(backoff.expo, conn_err_es, max_tries=5)
    async def _get_from_elastic(self, id: str) -> Union[Film, Genre, Person, None]:
        try:
            doc = await self.storage.get(index=self.index, id=id)
        except NotFoundError:
            return None

        instance = self.model(**doc['_source'])
        await self._put_to_cache(
            key=id, value=instance, expire=CACHE_EXPIRE_IN_SECONDS)
        return instance

    @backoff.on_exception(backoff.expo, conn_err_redis, max_tries=5)
    async def _get_from_cache(self, key: Union[dict, str]) -> Union[Film, Genre, Person, None]:
        data = await self.cache.get(json.dumps(key) if isinstance(key, dict) else key)
        if not data:
            return None

        instance_data = self.model.Config.json_loads(data)
        if instance_data:
            if isinstance(instance_data, list):
                return instance_data
            else:
                instance_data = self.model(**instance_data)
        return instance_data

    @backoff.on_exception(backoff.expo, conn_err_redis, max_tries=5)
    async def _put_to_cache(
            self, key: Union[dict, str], value: Union[Film, Genre, Person, dict, list[dict]], expire: int):
        await self.cache.set(key if isinstance(key, str) else json.dumps(key),
                             value.json() if isinstance(value, self.model) else json.dumps(value),
                             expire)

    @backoff.on_exception(backoff.expo, conn_err_es, max_tries=5)
    async def execute_query_storage(self, query: dict):
        result = await self.storage.search(index=self.index, body=query)
        docs = result['hits']['hits']
        instance_list = []
        for doc in docs:
            instance = self.model(**doc['_source'])
            params = prepare_fields_for_response(self.model, instance)
            instance_list.append(params)

        await self._put_to_cache(query, instance_list, CACHE_EXPIRE_IN_SECONDS)
        return instance_list


class AbstractExecuteRelation(ABC):
    @abstractmethod
    async def execute_query_storage_relation(self, query: dict):
        pass


class ExecuteRelationObject(BaseService, AbstractExecuteRelation):

    @backoff.on_exception(backoff.expo, conn_err_es, max_tries=5)
    async def execute_query_storage_relation(self, query: dict):
        result = await self.storage.search(index=self.index, body=query)
        docs = result['hits']['hits']
        instance_list = []
        for doc in docs[0]['_source']['films']:
            instance = self.relation_model(**doc)
            params = prepare_fields_for_response(self.relation_model, instance)
            instance_list.append(params)

        await self._put_to_cache(query, instance_list, CACHE_EXPIRE_IN_SECONDS)

        return instance_list
