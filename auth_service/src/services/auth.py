from fastapi import Depends, HTTPException, status
from functools import lru_cache
from sqlalchemy.ext.asyncio import AsyncSession

from models.entity import Authentication
from .base_service import BaseService
from .utils import decode_jwt

from db.postgres_db import get_session
from db.redis_db import RedisCache, get_redis


class AuthService(BaseService):
    def __init__(self, cache: RedisCache, storage: AsyncSession):
        super().__init__(cache, storage)
        self.model = Authentication

    async def new_auth(self, auth_params) -> None:
        # добавление в бд pg данных об аутентификации модель Authentication
        await self.create_new_instance(auth_params)

    async def login_history(
        self, access_token: str, limit: int = 10, page_number: int = 1
    ) -> list[Authentication]:

        payload = decode_jwt(jwt_token=access_token)
        user_uuid = payload.get("sub")
        # получить историю авторизаций по id_user_history модель Authentication
        auths_list = await self.get_login_history(
            user_uuid, limit=limit, offset=limit * (page_number - 1)
        )
        if auths_list is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="user not found"
            )
        return auths_list


@lru_cache()
def get_auth_service(
    redis: RedisCache = Depends(get_redis),
    db: AsyncSession = Depends(get_session),
) -> AuthService:

    return AuthService(redis, db)
