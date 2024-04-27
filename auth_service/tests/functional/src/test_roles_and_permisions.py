import pytest
import uuid
from httpx import AsyncClient
from http import HTTPStatus

from ..settings import test_settings


SERVICE_URL = test_settings.SERVISE_URL

email = str(uuid.uuid4())
user_pass = "test"


def cookies_superuser():
    cookies_ = {
        "access_token": pytest.access_token_superuser,
        "refresh_token": pytest.refresh_token_superuser,
    }
    return cookies_


async def login_user():
    async with AsyncClient(base_url=SERVICE_URL) as client:
        # логин суперпользователя
        query_data = {
            "email": test_settings.SU_email,
            "password": test_settings.SU_password,
        }
        response = await client.post("/api/v1/users/login", params=query_data)

        if response.status_code == HTTPStatus.OK:
            access_token = response.cookies.get("access_token")
            refresh_token = response.cookies.get("refresh_token")

            pytest.access_token_superuser = access_token
            pytest.refresh_token_superuser = refresh_token

        # создание нового пользователя

        query_data = {"email": email, "password": user_pass}
        response = await client.post(
            "/api/v1/users/user_registration", params=query_data
        )
        pytest.user_id = response.json()["uuid"]
        if response.status_code == HTTPStatus.OK:
            new_response = await client.post("/api/v1/users/login", params=query_data)
            if new_response.status_code == HTTPStatus.OK:
                access_token = new_response.cookies.get("access_token")
                refresh_token = new_response.cookies.get("refresh_token")

                pytest.access_token_other = access_token
                pytest.refresh_token_other = refresh_token


@pytest.mark.order("first")
@pytest.mark.asyncio
async def test_user_permissions():  # тест на доступ к ролям и разрешениям различных типов пользователей
    await login_user()  # логинимся под суперпользователем
    async with AsyncClient(base_url=SERVICE_URL) as client:
        # запрос без куков
        response = await client.get("/api/v1/roles/list")
        assert response.status_code == HTTPStatus.NOT_FOUND
        # куки случайного пользователя
        cookies = {
            "access_token": pytest.access_token_other,
            "refresh_token": pytest.refresh_token_other,
        }
        response = await client.get("/api/v1/roles/list", cookies=cookies)
        assert response.status_code == HTTPStatus.FORBIDDEN
        # куки суперпользователя
        response = await client.get("/api/v1/roles/list", cookies=cookies_superuser())
        assert response.status_code == HTTPStatus.OK


@pytest.mark.order("1")
@pytest.mark.asyncio
async def test_empty_list_roles():
    async with AsyncClient(base_url=SERVICE_URL) as client:
        response = await client.get("/api/v1/roles/list", cookies=cookies_superuser())
        assert response.status_code == HTTPStatus.OK
        assert response.json() == []


@pytest.mark.order(2)
@pytest.mark.asyncio
async def test_create_role():
    async with AsyncClient(base_url=SERVICE_URL) as client:
        pytest.role_type = str(uuid.uuid4())
        response = await client.post(
            "/api/v1/roles/create",
            params={"type": pytest.role_type},
            cookies=cookies_superuser(),
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json()["type"] == pytest.role_type
        pytest.role_id = response.json()["uuid"]


@pytest.mark.order(3)
@pytest.mark.asyncio
async def test_create_role_duplicate_name():
    async with AsyncClient(base_url=SERVICE_URL) as client:
        response = await client.post(
            "/api/v1/roles/create",
            params={"type": pytest.role_type},
            cookies=cookies_superuser(),
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.order(4)
@pytest.mark.asyncio
async def test_change_role():
    async with AsyncClient(base_url=SERVICE_URL) as client:
        pytest.role_type = str(uuid.uuid4())
        response = await client.put(
            f"/api/v1/roles/change/{pytest.role_id}",
            params={"type": pytest.role_type},
            cookies=cookies_superuser(),
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json()["type"] == pytest.role_type


@pytest.mark.order(5)
@pytest.mark.asyncio
async def test_list_roles():
    async with AsyncClient(base_url=SERVICE_URL) as client:
        response = await client.get("/api/v1/roles/list", cookies=cookies_superuser())
        assert response.status_code == HTTPStatus.OK
        assert isinstance(response.json(), list)


@pytest.mark.order(6)
@pytest.mark.asyncio
async def test_create_permission():
    async with AsyncClient(base_url=SERVICE_URL) as client:
        pytest.permissions_name = str(uuid.uuid4())
        response = await client.post(
            "/api/v1/permissions/create_permission",
            params={"name": pytest.permissions_name},
            cookies=cookies_superuser(),
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json()["name"] == pytest.permissions_name
        pytest.permissions_id = response.json()["uuid"]


@pytest.mark.order(7)
@pytest.mark.asyncio
async def test_add_user_role():
    async with AsyncClient(base_url=SERVICE_URL) as client:
        response_set_role = await client.post(
            f"/api/v1/roles/set/{pytest.user_id}/{pytest.role_id}",
            cookies=cookies_superuser(),
        )
        assert response_set_role.status_code == HTTPStatus.OK
        assert response_set_role.json()["id_role"] == pytest.role_id


@pytest.mark.asyncio
async def test_create_role_missing_name():
    async with AsyncClient(base_url=SERVICE_URL) as client:
        response = await client.post(
            "/api/v1/roles/create", params={}, cookies=cookies_superuser()
        )
        assert (
            response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        )  # Unprocessable Entity


@pytest.mark.asyncio
async def test_change_role_nonexistent():
    async with AsyncClient(base_url=SERVICE_URL) as client:
        response = await client.put(
            "/api/v1/roles/change/999",
            params={"type": "Moderator"},
            cookies=cookies_superuser(),
        )
        assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_change_role_missing_name():
    async with AsyncClient(base_url=SERVICE_URL) as client:
        response = await client.put(
            f"/api/v1/roles/change/{pytest.role_id}",
            params={},
            cookies=cookies_superuser(),
        )
        assert (
            response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        )  # Unprocessable Entity


@pytest.mark.asyncio
async def test_add_permissions_nonexistent_role():
    async with AsyncClient(base_url=SERVICE_URL) as client:
        response = await client.post(
            "/api/v1/permissions/assign_permission_to_role",
            params={
                "role_id": str(uuid.uuid4()),
                "permissions_id": pytest.permissions_id,
            },
            cookies=cookies_superuser(),
        )
        assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_add_permissions_nonexistent_permission():
    async with AsyncClient(base_url=SERVICE_URL) as client:
        response = await client.post(
            "/api/v1/permissions/assign_permission_to_role",
            params={"role_id": pytest.role_id, "permissions_id": str(uuid.uuid4())},
            cookies=cookies_superuser(),
        )
        assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_add_permissions():
    async with AsyncClient(base_url=SERVICE_URL) as client:
        response = await client.post(
            "/api/v1/permissions/assign_permission_to_role",
            params={"role_id": pytest.role_id, "permissions_id": pytest.permissions_id},
            cookies=cookies_superuser(),
        )
        assert response.status_code == HTTPStatus.OK


@pytest.mark.asyncio
async def test_add_user_role_nonexistent_role():
    async with AsyncClient(base_url=SERVICE_URL) as client:
        response = await client.post(
            f"/api/v1/roles/set/{pytest.user_id}/{str(uuid.uuid4())}",
            cookies=cookies_superuser(),
        )
        assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_add_user_role_nonexistent_user():
    async with AsyncClient(base_url=SERVICE_URL) as client:
        response = await client.post(
            f"/api/v1/roles/set/{str(uuid.uuid4())}/{pytest.role_id}",
            cookies=cookies_superuser(),
        )
        assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_delete_permissions_nonexistent_role():
    async with AsyncClient(base_url=SERVICE_URL) as client:
        response = await client.post(
            "/api/v1/permissions/remove_permission_from_role",
            params={
                "role_id": str(uuid.uuid4()),
                "permissions_id": pytest.permissions_id,
            },
            cookies=cookies_superuser(),
        )
        assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_delete_permissions_nonexistent_permission():
    async with AsyncClient(base_url=SERVICE_URL) as client:
        response = await client.post(
            "/api/v1/permissions/remove_permission_from_role",
            params={"role_id": pytest.role_id, "permissions_id": str(uuid.uuid4())},
            cookies=cookies_superuser(),
        )
        assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.order("fourth_to_last")
@pytest.mark.asyncio
async def test_delete_permissions():
    async with AsyncClient(base_url=SERVICE_URL) as client:
        response = await client.post(
            "/api/v1/permissions/remove_permission_from_role",
            params={"role_id": pytest.role_id, "permissions_id": pytest.permissions_id},
            cookies=cookies_superuser(),
        )
        assert response.status_code == HTTPStatus.OK


@pytest.mark.order("third_to_last")
@pytest.mark.asyncio
async def test_delete_role_from_user():
    async with AsyncClient(base_url=SERVICE_URL) as client:
        # назначенная пользователю роль
        response = await client.post(
            f"/api/v1/roles/delete/{pytest.user_id}", cookies=cookies_superuser()
        )
        assert response.status_code == HTTPStatus.OK


@pytest.mark.order("second_to_last")
@pytest.mark.asyncio
async def test_delete_role_nonexistent():
    async with AsyncClient(base_url=SERVICE_URL) as client:
        response = await client.delete(
            f"/api/v1/roles/{str(uuid.uuid4())}", cookies=cookies_superuser()
        )
        assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.order("last")
@pytest.mark.asyncio
async def test_delete_role():
    async with AsyncClient(base_url=SERVICE_URL) as client:
        response = await client.delete(
            f"/api/v1/roles/{pytest.role_id}", cookies=cookies_superuser()
        )
        assert response.status_code == HTTPStatus.OK
