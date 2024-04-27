from http import HTTPStatus
import uuid

import pytest

from ..settings import test_settings

SERVICE_URL = test_settings.SERVISE_URL

new_email = str(uuid.uuid4())
new_user_pass = "test"


def pytest_namespace():
    return {"access_token": None, "refresh_token": None, "new_user_id": None}


def cookies_superuser():
    cookies_ = {
        "access_token": pytest.access_token_superuser,
        "refresh_token": pytest.refresh_token_superuser,
    }
    return cookies_


async def login_user(make_post_request):
    # логин суперпользователя
    query_data = {"email": "superuser", "password": "superuser"}
    url = SERVICE_URL + "/api/v1/users/login"
    response = await make_post_request(url, query_data)

    status = response.status

    if status == HTTPStatus.OK:
        access_token = response.cookies.get("access_token")
        refresh_token = response.cookies.get("refresh_token")

        pytest.access_token_superuser = access_token
        pytest.refresh_token_superuser = refresh_token


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        ({"email": new_email, "password": new_user_pass}, {"status": HTTPStatus.OK}),
        ({"email": new_email, "password": "test"}, {"status": HTTPStatus.BAD_REQUEST}),
    ],
)
@pytest.mark.order(1)
@pytest.mark.asyncio
async def test_registration_user(make_post_request, query_data, expected_answer):
    url = SERVICE_URL + "/api/v1/users/user_registration"
    query_data = {"email": query_data["email"], "password": query_data["password"]}

    response = await make_post_request(url, query_data)

    status = response.status
    assert status == expected_answer["status"]
    if status == HTTPStatus.OK:
        body = await response.json()
        pytest.new_user_id = body["uuid"]


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (
            {"email": new_email, "password": "testtest"},
            {"status": HTTPStatus.FORBIDDEN},
        ),
        ({"email": new_email, "password": new_user_pass}, {"status": HTTPStatus.OK}),
        (
            {"email": str(uuid.uuid4()), "password": "user"},
            {"status": HTTPStatus.NOT_FOUND},
        ),
    ],
)
@pytest.mark.order(2)
@pytest.mark.asyncio
async def test_login_user(make_post_request, query_data, expected_answer):
    url = SERVICE_URL + "/api/v1/users/login"
    query_data = {"email": query_data["email"], "password": query_data["password"]}

    response = await make_post_request(url, query_data)

    status = response.status
    assert status == expected_answer["status"]

    if expected_answer["status"] == HTTPStatus.OK:
        access_token = response.cookies.get("access_token")
        refresh_token = response.cookies.get("refresh_token")

        pytest.access_token = access_token
        pytest.refresh_token = refresh_token

        assert access_token is not None
        assert refresh_token is not None

    if expected_answer["status"] == HTTPStatus.NOT_FOUND:
        assert response.cookies.get("access_token") is None
        assert response.cookies.get("refresh_token") is None
    await login_user(make_post_request)


@pytest.mark.parametrize(
    "query_data",
    [
        (
            {
                "first_name": "ivan",
                "last_name": "petrov",
                "email": str(uuid.uuid4()),
                "password": "user55",
            }
        ),
    ],
)
@pytest.mark.order(3)
@pytest.mark.asyncio
async def test_change_user(make_put_request, query_data):
    url = SERVICE_URL + "/api/v1/users/change_user_info"
    query_data = {"email": query_data["email"], "password": query_data["password"]}

    response = await make_put_request(url, query_data)
    assert response.status == HTTPStatus.NOT_FOUND

    cookies = {
        "access_token": pytest.access_token,
        "refresh_token": pytest.refresh_token,
    }
    response = await make_put_request(url, query_data, cookies)

    assert response.status == HTTPStatus.OK


@pytest.mark.order(4)
@pytest.mark.asyncio
async def test_refresh_token(make_post_request):
    url = SERVICE_URL + "/api/v1/users/refresh_token"
    # проверяем запрос без куки
    response = await make_post_request(url)
    assert response.status == HTTPStatus.NOT_FOUND
    # проверяем с куками автризованного пользователя
    cookies = {
        "access_token": pytest.access_token,
        "refresh_token": pytest.refresh_token,
    }
    response = await make_post_request(url, cookie=cookies)
    access_token = response.cookies.get("access_token")
    refresh_token = response.cookies.get("refresh_token")
    pytest.access_token = access_token
    pytest.refresh_token = refresh_token
    assert access_token is not None
    assert refresh_token is not None
    assert response.status == HTTPStatus.OK
    # проверяем со старыми токенами
    response = await make_post_request(url, cookie=cookies)
    assert response.status == HTTPStatus.UNAUTHORIZED


@pytest.mark.order(5)
@pytest.mark.asyncio
async def test_login_history(make_post_request):
    url = SERVICE_URL + "/api/v1/users/login_history"
    query_data = {"page_size": 50, "page_number": 1}
    # проверяем запрос без куки
    response = await make_post_request(url, query_data)
    assert response.status == HTTPStatus.NOT_FOUND
    # проверяем с куками автризованного пользователя
    cookies = {
        "access_token": pytest.access_token,
        "refresh_token": pytest.refresh_token,
    }
    response = await make_post_request(url, query_data, cookie=cookies)
    body = await response.json()

    assert response.status == HTTPStatus.OK
    assert len(body) == 1


@pytest.mark.order(6)
@pytest.mark.asyncio
async def test_check_permission(make_post_request):
    url = SERVICE_URL + "/api/v1/users/check_permission"
    permission_name = str(uuid.uuid4())
    query_data = {"name": permission_name}
    # проверяем запрос без куки
    response = await make_post_request(url, query_data)
    assert response.status == HTTPStatus.NOT_FOUND
    # проверяем с куками автризованного пользователя
    cookies = {
        "access_token": pytest.access_token,
        "refresh_token": pytest.refresh_token,
    }
    # проверяем новое разрешение
    response = await make_post_request(url, query_data, cookie=cookies)
    body = await response.json()
    assert body is False

    # создаем новую роль
    query_data = {"type": str(uuid.uuid4())}
    url_role = SERVICE_URL + "/api/v1/roles/create"
    response = await make_post_request(url_role, query_data, cookie=cookies_superuser())
    response_role = await response.json()

    # создаем новое разрешение
    url_permission = SERVICE_URL + "/api/v1/permissions/create_permission"
    query_data = {"name": permission_name}
    response = await make_post_request(
        url_permission, query_data, cookie=cookies_superuser()
    )
    response_permission = await response.json()

    # назначение прав роли
    query_data = {
        "role_id": response_role["uuid"],
        "permissions_id": response_permission["uuid"],
    }
    url_role_permission = SERVICE_URL + "/api/v1/permissions/assign_permission_to_role"
    response = await make_post_request(
        url_role_permission, query_data, cookie=cookies_superuser()
    )
    # присвоение роли пользователю
    url = (
        SERVICE_URL + f"/api/v1/roles/set/{pytest.new_user_id}/{response_role['uuid']}"
    )
    response = await make_post_request(url, cookie=cookies_superuser())
    # проверяем только что выданное разрешение
    url = SERVICE_URL + "/api/v1/users/check_permission"
    query_data = {"name": permission_name}
    response = await make_post_request(url, query_data, cookie=cookies)
    body = await response.json()
    assert body is True


@pytest.mark.order(7)
@pytest.mark.asyncio
async def test_logout(make_post_request):
    url = SERVICE_URL + "/api/v1/users/logout"
    # проверяем запрос без куки
    response = await make_post_request(url)
    assert response.status == HTTPStatus.NOT_FOUND
    # проверяем с куками автризованного пользователя
    cookies = {
        "access_token": pytest.access_token,
        "refresh_token": pytest.refresh_token,
    }
    response = await make_post_request(url, cookie=cookies)
    assert response.status == HTTPStatus.OK

    url = SERVICE_URL + "/api/v1/users/login_history"
    response = await make_post_request(url, cookie=cookies)
    assert response.status == HTTPStatus.UNAUTHORIZED
