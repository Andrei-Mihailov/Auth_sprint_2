from .settings import test_settings
import pytest_asyncio
import aiohttp
import sys
import os

fixtures_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), 'fixtures'))


sys.path.append(fixtures_path)


pytest_plugins = [
    'elastic',
    'test_data',
]


@pytest_asyncio.fixture(name='request_search')
def request_search():
    async def inner(endpoint, query_data: dict):
        session = aiohttp.ClientSession()
        url = f'{test_settings.service_url}/api/v1/{endpoint}/search'
        query_data = {'query': query_data['search'],
                      'page_number': query_data.get('page_number', 1),
                      'page_size': query_data.get('page_size', 50)}
        response = await session.get(url,
                                     params=query_data)
        await session.close()
        return response
    return inner


@pytest_asyncio.fixture(name='request_genres')
def request_genres():
    async def inner(endpoint, query_data: dict, id: str = None):
        session = aiohttp.ClientSession()
        url = f'{test_settings.service_url}/api/v1/{endpoint}/'
        if id:
            url += id
            response = await session.get(url)
        else:
            query_data = {'page_number': query_data.get('page_number', 1),
                          'page_size': query_data.get('page_size', 100)}
            response = await session.get(url,
                                         params=query_data)

        await session.close()
        return response
    return inner


@pytest_asyncio.fixture()
def make_get_request():
    async def inner(url: str, param: dict = None):
        session = aiohttp.ClientSession()
        response = await session.get(url, params=param)
        await session.close()
        return response
    return inner
