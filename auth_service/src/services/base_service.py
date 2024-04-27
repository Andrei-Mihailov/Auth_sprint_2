import backoff
import json

from abc import ABC
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import DBAPIError
from fastapi.encoders import jsonable_encoder
from typing import Union


from redis.exceptions import ConnectionError as conn_err_redis
from asyncpg.exceptions import PostgresConnectionError as conn_err_pg
from db.redis_db import RedisCache
from db.postgres_db import AsyncSession
from models.entity import User, Authentication, Roles, Permissions
from core.config import settings
from services.utils import decode_jwt


class AbstractBaseService(ABC):
    pass


class BaseService(AbstractBaseService):
    def __init__(self, cache: RedisCache, storage: AsyncSession):
        self.cache = cache
        self.storage = storage
        self.model = None

    @backoff.on_exception(backoff.expo, conn_err_pg, max_tries=5)
    async def create_new_instance(self, model_params):
        if not isinstance(model_params, dict):
            models_dto = jsonable_encoder(model_params)
        else:
            models_dto = model_params
        instance = self.model(**models_dto)
        self.storage.add(instance)
        try:
            await self.storage.commit()
        except Exception as e:
            print(f"Ошибка при создании объекта: {e}")
            return None
        await self.storage.refresh(instance)
        return instance

    @backoff.on_exception(backoff.expo, conn_err_pg, max_tries=5)
    async def change_instance_data(self, instance_id: int, model_params: dict):
        try:
            instance = await self.storage.get(self.model, instance_id)
            if instance is None:
                return None

            if not isinstance(model_params, dict):
                updated_data = jsonable_encoder(model_params)
            else:
                updated_data = model_params

            for field, value in updated_data.items():
                if field in ["email", "password"] and value is None:
                    continue
                setattr(instance, field, value)

            await self.storage.commit()
            await self.storage.refresh(instance)
            return instance
        except DBAPIError:
            return None
        except Exception as e:
            print(f"Ошибка при обновлении объекта: {e}")
            return None

    @backoff.on_exception(backoff.expo, conn_err_pg, max_tries=5)
    async def get_user_by_email(self, email):
        stmt = select(User).filter(User.email == email).options(selectinload(User.role))
        result = await self.storage.execute(stmt)
        user = result.scalars().first()
        return user

    @backoff.on_exception(backoff.expo, conn_err_pg, max_tries=5)
    async def get_instance_by_id(self, id: str):
        stmt = select(self.model).filter(self.model.id == id)
        result = await self.storage.execute(stmt)
        instance = result.scalars().first()
        return instance

    @backoff.on_exception(backoff.expo, conn_err_pg, max_tries=5)
    async def get_instance_by_name(self, name: str):
        stmt = select(self.model).filter(self.model.name == name)
        result = await self.storage.execute(stmt)
        instance = result.scalars().first()
        return instance

    @backoff.on_exception(backoff.expo, conn_err_pg, max_tries=5)
    async def del_instance_by_id(self, id: str):
        try:
            instance = await self.storage.get(self.model, id)
            if instance:
                await self.storage.delete(instance)
                await self.storage.commit()
                return True
            else:
                return False
        except DBAPIError:
            raise DBAPIError

    @backoff.on_exception(backoff.expo, conn_err_pg, max_tries=5)
    async def get_all_instance(self):
        stmt = select(Roles).options(selectinload(Roles.permissions))
        result = await self.storage.execute(stmt)
        instance = result.fetchall()
        return instance

    @backoff.on_exception(backoff.expo, conn_err_pg, max_tries=5)
    async def get_login_history(self, user_uuid: str, limit: int = 10, offset: int = 0):
        user = await self.storage.get(User, user_uuid)
        if user is None:
            return None

        stmt = (
            select(self.model)
            .filter(self.model.user_id == user_uuid)
            .offset(offset)
            .limit(limit)
        )
        result = await self.storage.execute(stmt)
        instance = result.scalars().all()
        return instance

    @backoff.on_exception(backoff.expo, conn_err_pg, max_tries=5)
    async def permission_to_role(self, permissions_id: str, role_id: str):
        role = await self.storage.get(Roles, role_id)
        permissions = await self.storage.get(Permissions, permissions_id)
        if role is not None and permissions is not None:
            permissions.role = role
            self.storage.add(permissions)
            await self.storage.commit()
            await self.storage.refresh(permissions)
            await self.storage.refresh(role)
            return role
        else:
            return None

    @backoff.on_exception(backoff.expo, conn_err_pg, max_tries=5)
    async def permission_from_role(self, permissions_id: str, role_id: str):
        role = await self.storage.get(Roles, role_id)
        permissions = await self.storage.get(Permissions, permissions_id)
        if role is not None and permissions is not None:
            if permissions.role_id == role.id:
                permissions.role = None
                await self.storage.commit()
                return True
            else:
                return False
        else:
            return False

    @backoff.on_exception(backoff.expo, conn_err_pg, max_tries=5)
    async def set_user_role(self, user_id, role_id):
        user: User = await self.storage.get(User, user_id)
        role = await self.storage.get(Roles, role_id)
        if user is not None and role is not None:
            user.role = role
            self.storage.add(user)
            await self.storage.commit()
            await self.storage.refresh(user)
            return user
        else:
            return None

    @backoff.on_exception(backoff.expo, conn_err_pg, max_tries=5)
    async def get_user_role(self, user_id):
        user = await self.storage.get(User, user_id)
        if user is not None and user.role_id is not None:
            stmt = (
                select(Roles)
                .options(selectinload(Roles.permissions))
                .where(Roles.id == user.role_id)
            )
            result = await self.storage.execute(stmt)
            role = result.fetchone()
            if role is not None:
                return role
            else:
                return None
        else:
            return None

    @backoff.on_exception(backoff.expo, conn_err_pg, max_tries=5)
    async def del_user_role(self, user_id):
        user: User = await self.storage.get(User, user_id)
        if user is not None:
            user.role_id = None
            self.storage.add(user)
            await self.storage.commit()
            await self.storage.refresh(user)
            return True
        else:
            return False

    @backoff.on_exception(backoff.expo, conn_err_redis, max_tries=5)
    async def _put_to_cache(
        self,
        key: Union[dict, str],
        value: Union[User, Authentication, dict, list[dict]],
        expire: int,
    ):
        await self.cache.set(
            key if isinstance(key, str) else json.dumps(key),
            value.json() if isinstance(value, self.model) else json.dumps(value),
            expire,
        )

    @backoff.on_exception(backoff.expo, conn_err_redis, max_tries=5)
    async def _delete_from_cache(self, key: Union[dict, str]):
        try:
            await self.cache.delete(key if isinstance(key, str) else json.dumps(key))
        except Exception as e:
            print(f"Ошибка при удалении из кэша: {e}")

    @backoff.on_exception(backoff.expo, conn_err_redis, max_tries=5)
    async def _get_from_cache(
        self, key: Union[dict, str]
    ) -> Union[User, Authentication, None]:
        data = await self.cache.get(json.dumps(key) if isinstance(key, dict) else key)
        if not data:
            return None

        instance_data = json.loads(data)
        if instance_data:
            if isinstance(instance_data, list) | isinstance(instance_data, str):
                return instance_data
            else:
                instance_data = self.model(**instance_data)
        return instance_data

    async def add_to_white_list(self, token, token_type):
        payload = decode_jwt(jwt_token=token)
        key = "white_list:" + payload.get("self_uuid")
        if token_type == "refresh":
            expire = settings.auth_jwt.refresh_token_expire_minutes
        else:
            expire = settings.auth_jwt.access_token_expire_minutes
        await self._put_to_cache(key, token, expire)

    async def get_from_white_list(self, token):
        payload = decode_jwt(jwt_token=token)
        key = "white_list:" + payload.get("self_uuid")
        return await self._get_from_cache(key)

    async def del_from_white_list(self, token):
        payload = decode_jwt(jwt_token=token)
        key = "white_list:" + payload.get("self_uuid")
        await self._delete_from_cache(key)

    async def add_to_black_list(self, token, token_type):
        payload = decode_jwt(jwt_token=token)
        key = "black_list:" + payload.get("self_uuid")
        if token_type == "refresh":
            expire = settings.auth_jwt.refresh_token_expire_minutes
        else:
            expire = settings.auth_jwt.access_token_expire_minutes
        await self._put_to_cache(key, token, expire)

    async def get_from_black_list(self, token):
        payload = decode_jwt(jwt_token=token)
        key = "black_list:" + payload.get("self_uuid")
        return await self._get_from_cache(key)
