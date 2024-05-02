from http import HTTPStatus

import pytest

from ..settings import test_settings


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {'id': test_settings.es_person_id_field},
            {'status': HTTPStatus.OK, 'length': 3}
        ),
        (
            {'id': '00000000-0000-0000-0000-00000000000'},
            {'status': HTTPStatus.NOT_FOUND, 'length': 1}
        )
    ]
)
@pytest.mark.asyncio
async def test_person_by_id(persons_data, es_write_data, make_get_request,
                            query_data, expected_answer):
    await es_write_data(persons_data, test_settings.es_person_index)

    url = test_settings.service_url + f"/api/v1/persons/{query_data['id']}"
    response = await make_get_request(url, None)
    if response.status == HTTPStatus.UNPROCESSABLE_ENTITY:
        body = {}
    else:
        body = await response.json()

    assert response.status == expected_answer['status']
    assert len(body) == expected_answer['length']
    if response.status == HTTPStatus.OK:
        person_data = {}
        for data in persons_data:
            if data['_id'] == body['uuid']:
                person_data = data['_source']
        assert person_data['id'] == body['uuid']
        assert person_data['full_name'] == body['full_name']
        for films_transmit, films_recieve in zip(person_data['films'], body['films']):
            assert films_transmit['id'] == films_recieve['uuid']
            assert films_transmit['roles'] == films_recieve['roles']


@pytest.mark.parametrize(
    'query_data, expected_answer, end_point',
    [
        # граничные случаи:
        (  # Пустой поисковый запрос или некорректное значение для других параметров
            {'search': '', 'page_number': 0, 'page_size': 0},
            {'status': HTTPStatus.UNPROCESSABLE_ENTITY, 'length': 0,
                'reason': 'Unprocessable Entity'},
            test_settings.es_person_index
        ),
        (  # Запрос с недействительным page_number и page_size
            {'search': 'Stan', 'page_number': -1, 'page_size': -1},
            {'status': HTTPStatus.UNPROCESSABLE_ENTITY,
                'length': 0, 'reason': 'Unprocessable Entity'},
            test_settings.es_person_index
        ),
        (  # Запрос с максимально возможным значением page_number и page_size
            {'search': 'Stan', 'page_number': 1, 'page_size': 100},
            {'status': HTTPStatus.OK, 'length': 60},
            test_settings.es_person_index
        ),
        (  # Запрос с поиском, в результате которого не найдено ни одной записи:
            {'search': 'Nonexistent_person'},
            {'status': HTTPStatus.NOT_FOUND, 'length': 1,
                'detail': 'list of persons is finished'},
            test_settings.es_person_index
        ),
        # N записей:
        (
            {'search': 'Stan', 'page_number': 1, 'page_size': 10},
            {'status': HTTPStatus.OK, 'length': 10},
            test_settings.es_person_index
        ),
        # поиск по фразе
        (
            {'search': 'Stan'},
            {'status': HTTPStatus.OK, 'length': 50},
            test_settings.es_person_index
        ),

    ]
)
@pytest.mark.asyncio
async def test_search_persons(es_write_data, request_search, persons_data,
                              end_point: str, query_data: dict, expected_answer: dict):
    await es_write_data(persons_data, end_point)
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
            persons_dict = {}
            for person in body:
                persons_dict[person['uuid']] = person
            for transmit in persons_data:
                if transmit['_id'] in persons_dict.keys():
                    assert transmit['_source']['full_name'] == persons_dict[transmit['_id']]['full_name']
                    for films_transmit, films_recieve in zip(transmit['_source']['films'],
                                                             persons_dict[transmit['_id']]['films']):
                        assert films_transmit['id'] == films_recieve['uuid']
                        assert films_transmit['roles'] == films_recieve['roles']


@pytest.mark.parametrize(
    'query_data, expected_answer, end_point',
    [
        # """Поиск с учетом кэша Redis"""
        # поиск по персонам
        (
            {'search': 'Stan', 'page_size': 70},
            {'status': HTTPStatus.OK, 'length': 60},
            test_settings.es_person_index
        )
    ]
)
@pytest.mark.asyncio
async def test_search_persons_redis(es_write_data, request_by_id, request_search, delete_from_es, persons_data,
                                    end_point: str, query_data: dict, expected_answer: dict):
    await es_write_data(persons_data, end_point)

    # первичный запрос на API
    response = await request_search(end_point, query_data)
    body = await response.json()
    status = response.status

    assert status == expected_answer['status']
    assert len(body) == expected_answer['length']

    # удаляем запись из ES
    await delete_from_es(end_point, test_settings.es_person_id_field)

    # повторный запрос на API
    response = await request_search(end_point, query_data)
    body = await response.json()
    status = response.status

    assert status == expected_answer['status']
    assert len(body) == expected_answer['length']
    # проверка что удаленная запись есть в ответе, то есть в кэше Redis
    assert body[-1]['uuid'] == test_settings.es_person_id_field


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {'id': test_settings.es_person_id_field,
                'page_size': 6, 'page_number': 1},
            {'status': HTTPStatus.OK, 'length': 2}
        ),
        (
            {'id': '00000000-0000-0000-0000-00000000000',
                'page_size': 1, 'page_number': 1},
            {'status': HTTPStatus.INTERNAL_SERVER_ERROR, 'length': 0}
        ),
        (
            {'id': test_settings.es_person_id_field,
                'page_size': -5, 'page_number': 1},
            {'status': HTTPStatus.UNPROCESSABLE_ENTITY, 'length': 0}
        )
    ]
)
@pytest.mark.asyncio
async def test_person_films(persons_data, es_write_data, make_get_request,
                            query_data, expected_answer):
    await es_write_data(persons_data, test_settings.es_person_index)

    url = test_settings.service_url + \
        f"/api/v1/persons/{query_data['id']}/film"
    query = {
        'page_size': query_data['page_size'],
        'page_number': query_data['page_number']}
    response = await make_get_request(url, query)
    if response.status in [HTTPStatus.INTERNAL_SERVER_ERROR, HTTPStatus.UNPROCESSABLE_ENTITY]:
        body = {}
    else:
        body = await response.json()

    assert response.status == expected_answer['status']
    assert len(body) == expected_answer['length']
    if response.status == HTTPStatus.OK:
        films_dict = {}
        for film in body:
            films_dict[film['uuid']] = film
        data_films = {}
        for data in persons_data:
            data_films[data['_id']] = data['_source']

        for films_transmit, films_recieve in zip(data_films[query_data['id']]['films'], films_dict.values()):
            assert films_transmit['id'] == films_recieve['uuid']
            assert films_transmit['title'] == films_recieve['title']
            assert films_transmit['imdb_rating'] == films_recieve['imdb_rating']
