from http import HTTPStatus
import uuid

import pytest

from ..settings import test_settings


@pytest.mark.parametrize(
    'query_data, expected_answer, end_point',
    [
        # граничные случаи:
        (  # Пустой поисковый запрос или некорректное значение для других параметров
            {'page_number': 0, 'page_size': 0},
            {'status': HTTPStatus.UNPROCESSABLE_ENTITY, 'length': 0,
                'reason': 'Unprocessable Entity'},
            test_settings.es_genre_index
        ),
        (  # Запрос с недействительным page_number и page_size
            {'page_number': -1, 'page_size': -1},
            {'status': HTTPStatus.UNPROCESSABLE_ENTITY,
                'length': 0, 'reason': 'Unprocessable Entity'},
            test_settings.es_genre_index
        ),
        (  # Запрос с максимально возможным значением page_number и page_size
            {'page_number': 1, 'page_size': 100},
            {'status': HTTPStatus.OK, 'length': 60},
            test_settings.es_genre_index
        ),
        # вывести все жанры
        (
            {'page_number': 1, 'page_size': 100},
            {'status': HTTPStatus.OK, 'length': 60},
            test_settings.es_genre_index
        )
    ]
)
@pytest.mark.asyncio
async def test_genres(es_write_data, genres_data, request_genres: list[dict],
                      end_point: str, query_data: dict, expected_answer: dict):
    await es_write_data(genres_data, end_point)
    response = await request_genres(end_point, query_data)
    status = response.status
    assert status == expected_answer['status']

    if status == HTTPStatus.UNPROCESSABLE_ENTITY:
        assert response.reason == expected_answer['reason']
    else:
        body = await response.json()

        assert status == expected_answer['status']
        if status == HTTPStatus.NOT_FOUND:
            assert body['detail'] == expected_answer['detail']
        else:
            assert len(body) == expected_answer['length']
            genres_dict = {}
            for genre in body:
                genres_dict[genre['uuid']] = genre
            for transmit in genres_data:
                if transmit['_id'] in genres_dict.keys():
                    assert transmit['_source']['name'] == genres_dict[transmit['_id']]['name']


@pytest.mark.parametrize(
    'query_data, expected_answer, end_point',
    [
        # граничные случаи:
        (  # Запрос с поиском, в результате которого не найдено ни одной записи:
            {'search': 'Nonexistent_id'},
            {'status': HTTPStatus.NOT_FOUND, 'length': 1,
                'detail': 'genre not found'},
            test_settings.es_genre_index
        ),
        # поиск конкретного жанра:
        (  # поиск по uuid
            {'search': test_settings.es_genre_id_field},
            {'status': HTTPStatus.OK, 'length': 2, 'name': 'action',
                'uuid': test_settings.es_genre_id_field},
            test_settings.es_genre_index
        ),
        (  # поиск по name
            {'search': 'action', 'page_number': 1, 'page_size': 100},
            {'status': HTTPStatus.OK, 'length': 2, 'name': 'action',
                'uuid': test_settings.es_genre_id_field},
            test_settings.es_genre_index
        )
    ]
)
@pytest.mark.asyncio
async def test_search_genres(es_write_data, genres_data, request_genres: list[dict],
                             end_point: str, query_data: dict, expected_answer: dict):
    await es_write_data(genres_data, end_point)
    try:
        uuid.UUID(query_data['search'])
        genre_id = query_data['search']
    except ValueError:
        response = await request_genres(end_point, query_data)
        body = await response.json()
        for doc in body:
            if doc['name'].lower() == query_data['search']:
                genre_id = doc['uuid']
                break
        else:
            genre_id = query_data['search']
    response = await request_genres(end_point, query_data, genre_id)
    status = response.status
    body = await response.json()
    assert status == expected_answer['status']
    if status == HTTPStatus.NOT_FOUND:
        assert body['detail'] == expected_answer['detail']
    else:
        assert body['name'].lower() == expected_answer['name']
        assert body['uuid'] == expected_answer['uuid']


@pytest.mark.parametrize(
    'query_data, expected_answer, end_point',
    [
        # """Поиск с учетом кэша Redis"""
        (  # поиск по uuid
            {'search': test_settings.es_genre_id_field},
            {'status': HTTPStatus.OK, 'length': 2, 'name': 'action',
                'uuid': test_settings.es_genre_id_field},
            test_settings.es_genre_index
        ),
        (  # поиск по name
            {'search': 'action'},
            {'status': HTTPStatus.OK, 'length': 2, 'name': 'action',
                'uuid': test_settings.es_genre_id_field},
            test_settings.es_genre_index
        )
    ]
)
@pytest.mark.asyncio
async def test_genres_redis(es_write_data, genres_data, request_by_id,
                            request_genres, delete_from_es,
                            end_point: str, query_data: dict, expected_answer: dict):
    await es_write_data(genres_data, end_point)
    # первичный запрос на API
    try:
        uuid.UUID(query_data['search'])
        genre_id = query_data['search']
    except ValueError:
        response = await request_genres(end_point, query_data)
        body = await response.json()
        for doc in body:
            if doc['name'].lower() == query_data['search']:
                genre_id = doc['uuid']
                break
        else:
            genre_id = query_data['search']
    response = await request_genres(end_point, query_data, genre_id)
    status = response.status
    body = await response.json()
    assert status == expected_answer['status']
    assert body['name'].lower() == expected_answer['name']
    assert body['uuid'] == expected_answer['uuid']

    # удаляем запись из ES
    await delete_from_es(end_point, test_settings.es_genre_id_field)

    # повторный запрос на API
    response = await request_genres(end_point, query_data, genre_id)
    status = response.status
    body = await response.json()
    assert status == expected_answer['status']
    assert body['name'].lower() == expected_answer['name']
    assert body['uuid'] == expected_answer['uuid']
    # проверка что удаленная запись есть в ответе, то есть в кэше Redis
    assert test_settings.es_genre_id_field == body['uuid']
