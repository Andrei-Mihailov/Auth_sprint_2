import pytest_asyncio
from httpx import AsyncClient

from ..settings import test_settings


SERVICE_URL = test_settings.SERVISE_URL


@pytest_asyncio.fixture
async def client_fixture():
    async with AsyncClient(base_url=SERVICE_URL) as client:
        yield client


@pytest_asyncio.fixture
async def authenticated_client(client_fixture, user_fixture):
    login_data = {"username": user_fixture.username, "password": "testpassword"}
    response = await client_fixture.post("/auth/login", json=login_data)
    assert response.status_code == 200
    cookies = response.cookies
    client_fixture.cookies = cookies
    yield client_fixture


@pytest_asyncio.fixture
async def superuser_authenticated_client(client_fixture, superuser_fixture):
    login_data = {"username": superuser_fixture.username, "password": "testpassword"}
    response = await client_fixture.post("/auth/login", json=login_data)
    assert response.status_code == 200
    cookies = response.cookies
    client_fixture.cookies = cookies
    yield client_fixture


@pytest_asyncio.fixture
async def client_factory(request, client_fixture, user_fixture, superuser_fixture):
    if request.param == "user":
        login_data = {"username": user_fixture.username, "password": "testpassword"}
    elif request.param == "superuser":
        login_data = {
            "username": superuser_fixture.username,
            "password": "testpassword",
        }
    else:
        raise ValueError("Invalid user type")

    response = await client_fixture.post("/auth/login", json=login_data)
    assert response.status_code == 200
    cookies = response.cookies
    client_fixture.cookies = cookies
    yield client_fixture
