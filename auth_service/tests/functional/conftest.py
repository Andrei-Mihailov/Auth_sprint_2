import pytest_asyncio
import aiohttp


@pytest_asyncio.fixture()
def make_post_request():
    async def inner(url: str, param: dict = None, cookie=None):
        session = aiohttp.ClientSession(cookies=cookie)
        response = await session.post(url, params=param)
        await session.close()
        return response

    return inner


@pytest_asyncio.fixture()
def make_put_request():
    async def inner(url: str, param: dict = None, cookie=None):
        session = aiohttp.ClientSession(cookies=cookie)

        response = await session.put(url, params=param)
        await session.close()
        return response

    return inner
