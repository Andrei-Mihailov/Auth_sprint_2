import orjson

from enum import Enum
from pydantic import BaseModel as PydanticBaseModel
from typing import Union


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class BaseModel(PydanticBaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class PersonRole(str, Enum):
    actor = "actor"
    writer = "writer"
    director = "director"


class Genre(BaseModel):
    id: str
    name: str


class PersonInFilm(BaseModel):
    id: str
    name: str


class Film(BaseModel):
    id: str
    title: str
    description: Union[str, None]
    imdb_rating: Union[float, None]
    genres: Union[list[Genre], None]
    actors: Union[list[PersonInFilm], None]
    writers: Union[list[PersonInFilm], None]
    directors: Union[list[PersonInFilm], None]
    actors_names: Union[list[str], None, str]
    directors_names: Union[list[str], None, str]
    writers_names: Union[list[str], None, str]


class PersonFilmDetails(BaseModel):
    id: str
    title: Union[str, None]
    imdb_rating: Union[float, None]


class PersonFilms(PersonFilmDetails):
    roles: Union[list[PersonRole], None]


class Person(BaseModel):
    id: str
    full_name: str
    films: Union[list[PersonFilms], None]
