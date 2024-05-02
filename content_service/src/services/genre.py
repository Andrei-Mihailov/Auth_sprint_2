from functools import lru_cache
from fastapi import Depends

from db.elastic import ElasticStorage, get_elastic
from db.redis import RedisCache, get_redis
from models.models import Genre
from core.config import els_config_genres_data
from .base_service import BaseService

INDEX = els_config_genres_data.index


class GenreService(BaseService):
    def __init__(self, cache: RedisCache, storage: ElasticStorage):
        super().__init__(cache, storage)
        self.model = Genre
        self.index = INDEX

    async def get_all_genres(self, page_number: int, page_size: int) -> list[Genre]:
        query_str = {"match_all": {}}
        query = {"size": page_size,
                 "from": page_size*(page_number-1),
                 "query": query_str,
                 }
        genres_list = await self._get_from_cache(query)
        if not genres_list:
            genres_list = await self.execute_query_storage(query)
            if not genres_list:
                return None

        return genres_list


@lru_cache()
def get_genre_service(
        redis: RedisCache = Depends(get_redis),
        elastic: ElasticStorage = Depends(get_elastic),
) -> GenreService:

    return GenreService(redis, elastic)
