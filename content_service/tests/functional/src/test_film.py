from http import HTTPStatus

import pytest

from ..settings import test_settings


#  Название теста должно начинаться со слова `test_`
#  Любой тест с асинхронными вызовами нужно оборачивать декоратором `pytest.mark.asyncio`


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {'page_size': 70, 'page_number': 1},
            {'status': HTTPStatus.OK, 'length': 61}
        ),
        (
            {'page_size': 50, 'page_number': 1},
            {'status': HTTPStatus.OK, 'length': 50}
        ),
        (
            {'page_size': 70, 'page_number': 2},
            {'status': HTTPStatus.NOT_FOUND, 'length': 1}
        ),
        (
            {'page_size': 10, 'page_number': 1},
            {'status': HTTPStatus.OK, 'length': 10}
        ),
        (
            {'page_size': -1, 'page_number': -1},
            {'status': HTTPStatus.UNPROCESSABLE_ENTITY, 'length': 0}
        ),
        (
            {'page_size': 0, 'page_number': 0},
            {'status': HTTPStatus.UNPROCESSABLE_ENTITY, 'length': 0}
        )
    ]
)
@pytest.mark.asyncio
async def test_list_films(films_data, es_write_data, make_get_request,
                          query_data, expected_answer):
    await es_write_data(films_data, test_settings.es_film_index)

    url = test_settings.service_url + '/api/v1/films/'
    query_data = {'sort': '-imdb_rating',
                  'page_size': query_data['page_size'],
                  'page_number': query_data['page_number']}

    response = await make_get_request(url, query_data)
    status = response.status
    if status == HTTPStatus.UNPROCESSABLE_ENTITY:
        body = {}
    else:
        body = await response.json()

    assert status == expected_answer['status']
    assert len(body) == expected_answer['length']

    if status == HTTPStatus.OK:
        films_dict = {}

        for film in body:
            films_dict[film['uuid']] = film

        for transmit in films_data:
            if transmit['_id'] in films_dict.keys():
                assert transmit['_source']['title'] == films_dict[transmit['_source']['id']]['title']
                assert transmit['_source']['imdb_rating'] == films_dict[transmit['_source']
                                                                        ['id']]['imdb_rating']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {'id': test_settings.es_film_id_field},
            {'status': HTTPStatus.OK, 'length': 8}
        ),
        (
            {'id': '00000000-0000-0000-0000-00000000000'},
            {'status': HTTPStatus.NOT_FOUND, 'length': 1}
        )
    ]
)
@pytest.mark.asyncio
async def test_film_by_id(films_data, es_write_data, make_get_request,
                          query_data, expected_answer):
    await es_write_data(films_data, test_settings.es_film_index)

    url = test_settings.service_url + f"/api/v1/films/{query_data['id']}"
    response = await make_get_request(url, None)
    body = await response.json()

    assert response.status == expected_answer['status']
    assert len(body) == expected_answer['length']

    if response.status == HTTPStatus.OK:
        last_film = films_data[60]['_source']
        assert last_film['title'] == body['title']
        assert last_film['id'] == body['uuid']
        assert last_film['imdb_rating'] == body['imdb_rating']
        assert last_film['description'] == body['description']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {'id': test_settings.es_film_id_field},
            {'status': HTTPStatus.OK, 'length': 8}
        )
    ]
)
@pytest.mark.asyncio
async def test_film_redis(films_data, es_write_data, make_get_request,
                          delete_from_es, query_data, expected_answer):
    await es_write_data(films_data, test_settings.es_film_index)
    url = test_settings.service_url + f"/api/v1/films/{query_data['id']}"
    response = await make_get_request(url, None)
    await delete_from_es(test_settings.es_film_index,
                         query_data['id'])

    response = await make_get_request(url, None)
    body = await response.json()

    assert response.status == expected_answer['status']
    assert len(body) == expected_answer['length']
