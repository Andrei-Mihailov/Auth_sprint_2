from functools import lru_cache
from typing import Union
from fastapi import Depends

from db.elastic import ElasticStorage, get_elastic
from db.redis import RedisCache, get_redis
from models.models import Person, PersonFilmDetails
from core.config import els_config_persons_data
from .base_service import ExecuteRelationObject

INDEX = els_config_persons_data.index


class PersonService(ExecuteRelationObject):
    def __init__(self, cache: RedisCache, storage: ElasticStorage):
        super().__init__(cache, storage)
        self.model = Person
        self.relation_model = PersonFilmDetails
        self.index = INDEX

    async def get_all_person_films(self, person_id: str, page_number: int, page_size: int) -> Union[list[Person], None]:
        query_str = {"match": {"id": person_id}}
        query = {"size": page_size,
                 "from": page_size*(page_number-1),
                 "query": query_str,
                 }
        films_list = await self._get_from_cache(query)
        if not films_list:
            films_list = await self.execute_query_storage_relation(query)
            if not films_list:
                return None

        return films_list

    async def find_persons_by_name(self, query: str, page_number: int, page_size: int) -> Union[list[Person], None]:
        query_str = {"match": {"full_name": query}}
        query = {"size": page_size,
                 "from": page_size*(page_number-1),
                 "query": query_str,
                 }
        persons_list = await self._get_from_cache(query)
        if not persons_list:
            persons_list = await self.execute_query_storage(query)
            if not persons_list:
                return None

        return persons_list


@lru_cache()
def get_person_service(
        redis: RedisCache = Depends(get_redis),
        elastic: ElasticStorage = Depends(get_elastic),
) -> PersonService:

    return PersonService(redis, elastic)
