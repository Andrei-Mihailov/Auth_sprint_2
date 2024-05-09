from functools import lru_cache
from typing import Union
from fastapi import Depends

from db.elastic import ElasticStorage, get_elastic
from db.redis import RedisCache, get_redis
from models.models import Film
from core.config import els_config_films_data
from .base_service import BaseService

INDEX = els_config_films_data.index


class FilmService(BaseService):
    def __init__(self, cache: RedisCache, storage: ElasticStorage):
        super().__init__(cache, storage)
        self.model = Film
        self.index = INDEX

    async def get_all_films(self, sort_by: str,
                            page_number: int,
                            page_size: int,
                            genre: Union[str, None]) -> Union['list[Film]', None]:
        if sort_by[0] == "-":
            sort = [{sort_by[1:]: "desc"}]
        else:
            sort = [{sort_by: "asc"}]
        if genre is None:
            query_str = {"match_all": {}}
        else:
            query_str = {
                "nested": {
                    "path": "genres",
                    "query": {
                        "match": {
                            "genres.name": genre
                        }
                    }
                }
            }

        query = {"size": page_size,
                 "from": page_size * (page_number - 1),
                 "query": query_str,
                 "sort": sort
                 }

        films_list = await self._get_from_cache(query)
        if not films_list:
            films_list = await self.execute_query_storage(query)
            if not films_list:
                return None

        return films_list

    async def find_films_by_title(self, query: str,
                                  page_number: int,
                                  page_size: int) -> Union['list[Film]', None]:
        query_str = {"match": {"title": query}}
        sort = [{"imdb_rating": "desc"}]
        query = {"size": page_size,
                 "from": page_size * (page_number - 1),
                 "query": query_str,
                 "sort": sort
                 }

        film = await self._get_from_cache(query)
        if not film:
            film = await self.execute_query_storage(query)
            if not film:
                return None

        return film


@lru_cache()
def get_film_service(
        redis: RedisCache = Depends(get_redis),
        elastic: ElasticStorage = Depends(get_elastic),
) -> FilmService:

    return FilmService(redis, elastic)
