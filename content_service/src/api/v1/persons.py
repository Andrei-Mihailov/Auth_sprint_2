from http import HTTPStatus
from typing import Annotated, Union
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, TypeAdapter

from core.config import page_max_size
from services.person import PersonService, get_person_service

router = APIRouter()


class Films(BaseModel):
    uuid: str
    title: str
    imdb_rating: float


class PersonFilms(BaseModel):
    uuid: str
    roles: Union[list[str], None]


class Person(BaseModel):
    uuid: str
    full_name: str
    films: Union[list[PersonFilms], None]


# /api/v1/persons/search?query=captain&page_number=1&page_size=50
@router.get('/search',
            response_model=list[Person],
            summary="Поиск персоны по ФИО",
            description="Поиск персоны по ФИО с пагинацией",
            response_description="Ид, ФИО, список фильмов",
            tags=['Персоны'])
async def find_persons(query: str,
                       page_number: Annotated[int, Query(
                           description='Номер страницы', ge=1)] = 1,
                       page_size: Annotated[int, Query(
                           description='Количество результатов запроса на странице', ge=1, le=page_max_size)] = page_max_size,
                       person_service: PersonService = Depends(get_person_service)) -> list[Person]:

    persons = await person_service.find_persons_by_name(query, page_number, page_size)
    if not persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='list of persons is finished')

    persons_response = TypeAdapter(list[Person]).validate_python(persons)
    return persons_response


# /api/v1/persons/<uuid:UUID>/
@router.get('/{person_id}',
            response_model=Person,
            summary="Поиск персоны по ид",
            description="Поиск персоны по ид",
            response_description="Ид, ФИО, список фильмов",
            tags=['Персоны'])
async def person_details(person_id: str, person_service: PersonService = Depends(get_person_service)) -> Person:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='person not found')
    return Person(uuid=person.id,
                  full_name=person.full_name,
                  films=[
                      {
                          "uuid": p.id,
                          "roles": [
                              r.value for r in p.roles
                          ]
                      }
                      for p in person.films
                  ]
                  )


# /api/v1/persons/<uuid:UUID>/film/
@router.get('/{person_id}/film',
            response_model=list[Films],
            summary="Поиск фильмов по ид персоны",
            description="Поиск фильмов с участием персоны",
            response_description="Список фильмов с ид, наименованием и рейтингом",
            tags=['Персоны'])
async def all_person_films(person_id: str,
                           page_number: Annotated[int, Query(
                               description='Номер страницы', ge=1)] = 1,
                           page_size: Annotated[int, Query(
                               description='Количество результатов запроса на странице', ge=1, le=page_max_size)] = page_max_size,
                           person_service: PersonService = Depends(
                               get_person_service),
                           ) -> list[Films]:

    films = await person_service.get_all_person_films(person_id, page_number, page_size)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='list of persons is finished')

    films_response = TypeAdapter(list[Films]).validate_python(films)
    return films_response
