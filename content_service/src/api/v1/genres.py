from http import HTTPStatus
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, TypeAdapter

from core.config import page_max_size
from services.genre import GenreService, get_genre_service

router = APIRouter()


class Genre(BaseModel):
    uuid: str
    name: str


# /api/v1/genres/<uuid:UUID>/
@router.get('/{genre_id}',
            response_model=Genre,
            summary="Поиск жанра по ид",
            description="Поиск по ид",
            response_description="Ид, название",
            tags=['Жанры'])
async def genre_details(genre_id: str, genre_service: GenreService = Depends(get_genre_service)) -> Genre:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='genre not found')

    return Genre(uuid=genre.id,
                 name=genre.name
                 )


# /api/v1/genres/
@router.get('/',
            response_model=list[Genre],
            summary="Список всех жанров",
            description="Список всех жанров с пагинацией",
            response_description="Ид, название",
            tags=['Жанры'])
async def all_genres(page_number: Annotated[int, Query(description='Номер страницы', ge=1)] = 1,
                     page_size: Annotated[int, Query(
                        description='Количество результатов запроса на странице', ge=1, le=page_max_size)] = page_max_size,
                     genre_service: GenreService = Depends(get_genre_service),
                     ) -> list[Genre]:

    genres = await genre_service.get_all_genres(page_number, page_size)
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='list of genres is finished')

    genres_response = TypeAdapter(list[Genre]).validate_python(genres)
    return genres_response
