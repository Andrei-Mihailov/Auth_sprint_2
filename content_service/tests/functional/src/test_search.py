from http import HTTPStatus

import pytest

from ..settings import test_settings


@pytest.mark.parametrize(
    'query_data, expected_answer, end_point',
    [
        # """поиск по фильмам"""
        # граничные случаи:
        (  # Пустой поисковый запрос или некорректное значение для других параметров
            {'search': '', 'page_number': 0, 'page_size': 0},
            {'status': HTTPStatus.UNPROCESSABLE_ENTITY, 'length': 0,
                'reason': 'Unprocessable Entity'},
            test_settings.es_film_index
        ),
        (  # Запрос с недействительным page_number и page_size
            {'search': 'The Star', 'page_number': -1, 'page_size': -1},
            {'status': HTTPStatus.UNPROCESSABLE_ENTITY,
                'length': 0, 'reason': 'Unprocessable Entity'},
            test_settings.es_film_index
        ),
        (  # Запрос с максимально возможным значением page_number и page_size
            {'search': 'The Star', 'page_number': 1, 'page_size': 70},
            {'status': HTTPStatus.OK, 'length': 61},
            test_settings.es_film_index
        ),
        (  # Запрос с поиском, в результате которого не найдено ни одной записи:
            {'search': 'Nonexistent_film'},
            {'status': HTTPStatus.NOT_FOUND, 'length': 1,
                'detail': 'list of films is finished'},
            test_settings.es_film_index
        ),
        # N записей:
        (
            {'search': 'The Star', 'page_number': 1, 'page_size': 10},
            {'status': HTTPStatus.OK, 'length': 10},
            test_settings.es_film_index
        ),
        # поиск по фразе
        (
            {'search': 'The Star'},
            {'status': HTTPStatus.OK, 'length': 50},
            test_settings.es_film_index
        )
    ]
)
@pytest.mark.asyncio
async def test_search_films(es_write_data, request_search, films_data,
                            end_point: str, query_data: dict, expected_answer: dict):
    await es_write_data(films_data, end_point)
    response = await request_search(end_point, query_data)
    status = response.status

    assert status == expected_answer['status']
    if status == HTTPStatus.UNPROCESSABLE_ENTITY:
        assert response.reason == expected_answer['reason']
    else:
        body = await response.json()
        if status == HTTPStatus.NOT_FOUND:
            assert body['detail'] == expected_answer['detail']
        else:
            assert len(body) == expected_answer['length']
            films_dict = {}
            for film in body:
                films_dict[film['uuid']] = film
            for transmit in films_data:
                id_film = transmit['_id']
                if id_film in films_dict.keys():
                    assert transmit['_source']['title'] == films_dict[id_film]['title']
                    assert transmit['_source']['imdb_rating'] == films_dict[id_film]['imdb_rating']


@pytest.mark.parametrize(
    'query_data, expected_answer, end_point',
    [
        # """Поиск с учетом кэша Redis"""
        # поиск по фильмам
        (
            {'search': 'The Star', 'page_size': 70},
            {'status': HTTPStatus.OK, 'length': 61},
            test_settings.es_film_index
        ),
    ]
)
@pytest.mark.asyncio
async def test_search_films_redis(es_write_data, request_by_id, request_search,
                                  delete_from_es, films_data,
                                  end_point: str, query_data: dict,
                                  expected_answer: dict):
    await es_write_data(films_data, end_point)
    # первичный запрос на API
    response = await request_search(end_point, query_data)
    body = await response.json()
    status = response.status

    assert status == expected_answer['status']
    assert len(body) == expected_answer['length']

    # удаляем запись из ES

    await delete_from_es(end_point, test_settings.es_film_id_field)

    # повторный запрос на API
    response = await request_search(end_point, query_data)
    body = await response.json()
    status = response.status

    assert status == expected_answer['status']
    assert len(body) == expected_answer['length']
    # проверка что удаленная запись есть в ответе, то есть в кэше Redis
    assert body[-1]['uuid'] == test_settings.es_film_id_field
