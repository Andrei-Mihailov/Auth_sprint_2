from http import HTTPStatus
from typing import Annotated, Union
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, TypeAdapter

from core.config import page_max_size
from services.film import FilmService, get_film_service

router = APIRouter()


class Person(BaseModel):
    uuid: str
    full_name: str


class Genre(BaseModel):
    id: str
    name: str


class Film(BaseModel):
    uuid: str
    title: str
    imdb_rating: Union[float, None]


class FilmDetails(Film):
    description: Union[str, None]
    genres: Union[list[Genre], None]
    actors: Union[list[Person], None]
    writers: Union[list[Person], None]
    directors: Union[list[Person], None]


# /api/v1/films/search?query=star&page_number=1&page_size=50
@router.get('/search',
            response_model=list[Film],
            summary="Поиск фильмов по наименованию с пагинацией",
            description="Полнотекстовый поиск по фильмам",
            response_description="Ид, название, рейтинг",
            tags=['Фильмы'])
async def find_films(query: str,
                     page_number: Annotated[int, Query(
                         description='Номер страницы', ge=1)] = 1,
                     page_size: Annotated[int, Query(
                         description='Количество результатов запроса на странице', ge=1, le=page_max_size)] = page_max_size,
                     film_service: FilmService = Depends(get_film_service)) -> list[Film]:

    films = await film_service.find_films_by_title(query, page_number, page_size)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='list of films is finished')

    films_response = TypeAdapter(list[Film]).validate_python(films)
    return films_response


# /api/v1/films/<uuid:UUID>/
@router.get('/{film_id}',
            response_model=FilmDetails,
            summary="Поиск фильма по ид",
            description="Поиск по ид",
            response_description="Ид, название, рейтинг, описание, жанры, актеры, режиссеры, сценаристы",
            tags=['Фильмы'])
async def film_details(film_id: str, film_service: FilmService = Depends(get_film_service)) -> FilmDetails:
    film = await film_service.get_by_id(film_id)

    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='film not found')

    actors_api = []
    for p in film.actors:
        actors_api.append(Person(uuid=p.id, full_name=p.name))

    writers_api = []
    for p in film.writers:
        writers_api.append(Person(uuid=p.id, full_name=p.name))

    directors_api = []
    for p in film.directors:
        directors_api.append(Person(uuid=p.id, full_name=p.name))

    genres_api = []
    for p in film.genres:
        genres_api.append(Genre(id=p.id, name=p.name))

    return FilmDetails(uuid=film.id,
                       title=film.title,
                       imdb_rating=film.imdb_rating,
                       description=film.description,
                       genres=genres_api,
                       actors=actors_api,
                       writers=writers_api,
                       directors=directors_api
                       )


# /api/v1/films?sort=-imdb_rating&page_size=50&page_number=1
# /api/v1/films?genre=<uuid:UUID>&sort=-imdb_rating&page_size=50&page_number=1
@router.get('/',
            response_model=list[Film],
            summary="Поиск фильмов по жанру с пагинацией",
            description="Полнотекстовый поиск по жанру фильмов",
            response_description="Ид, название, рейтинг",
            tags=['Фильмы'])
async def all_films(page_number: Annotated[int, Query(description='Номер страницы', ge=1)] = 1,
                    page_size: Annotated[int, Query(
                        description='Количество результатов запроса на странице', ge=1, le=page_max_size)] = page_max_size,
                    genre: Union[str, None] = None,
                    sort='imdb_rating',
                    film_service: FilmService = Depends(get_film_service),
                    ) -> list[Film]:

    films = await film_service.get_all_films(sort, page_number, page_size, genre)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='list of films is finished')

    films_response = TypeAdapter(list[Film]).validate_python(films)
    return films_response
