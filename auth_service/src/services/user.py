from fastapi import Depends, HTTPException, status
from functools import lru_cache
from sqlalchemy.ext.asyncio import AsyncSession

from models.entity import User
from .base_service import BaseService
from models.auth import Tokens
from .utils import (
    create_refresh_token,
    create_access_token,
    decode_jwt,
    check_date_and_type_token,
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE,
)

from db.postgres_db import get_session
from db.redis_db import RedisCache, get_redis


class UserService(BaseService):
    def __init__(self, cache: RedisCache, storage: AsyncSession):
        super().__init__(cache, storage)
        self.model = User

    def token_decode(self, token):
        return decode_jwt(jwt_token=token)

    async def get_validate_user(self, user_email: str, user_password: str) -> User:
        user: User = await self.get_user_by_email(user_email)
        if user is None:  # если в бд не нашли такой логин
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="invalid email"
            )
        if not user.check_password(user_password):  # если пароль не совпадает
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="uncorrect password"
            )
        if not user.active:  # если пользователь неактивен
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="user is deactive"
            )

        return user

    async def change_user_info(self, access_token: str, user_data: dict) -> User:
        payload = self.token_decode(access_token)
        user_uuid = payload.get("sub")

        if check_date_and_type_token(payload, ACCESS_TOKEN_TYPE):
            # проверка access токена в блэк листе redis
            if not await self.get_from_black_list(access_token):
                user = await self.change_instance_data(user_uuid, user_data)
                if user is None:  # если в бд пг не нашли такой uuid
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="user not found or email exists",
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="uncorrect token"
                )
        return user

    async def create_user(self, user_params) -> User:
        user = await self.create_new_instance(user_params)
        return user

    async def login(self, user_email: str, user_password: str) -> Tokens:
        user = await self.get_validate_user(user_email, user_password)
        user_role = user.role.type if user.role else None
        access_token = create_access_token(user, user_role)
        refresh_token = create_refresh_token(user)

        # добавление refresh токена в вайт-лист редиса
        await self.add_to_white_list(refresh_token, REFRESH_TOKEN_TYPE)
        return Tokens(access_token=access_token, refresh_token=refresh_token), user

    async def logout(self, access_token: str, refresh_token: str) -> bool:
        await self.add_to_black_list(access_token, ACCESS_TOKEN_TYPE)
        await self.del_from_white_list(refresh_token)
        return True

    async def refresh_access_token(
        self, access_token: str, refresh_token: str
    ) -> Tokens:
        # Декодирование refresh-токена
        payload = self.token_decode(refresh_token)
        user_uuid = payload.get("sub")

        # Проверка типа и срока действия токена
        if check_date_and_type_token(payload, REFRESH_TOKEN_TYPE):
            # проверка наличия refresh токена в бд redis (хорошо, если он там есть)
            if await self.get_from_white_list(refresh_token):
                # наити пользователя по user_uuid, вернуть (модель User)
                user = await self.get_instance_by_id(user_uuid)
                new_access_token = create_access_token(user, user.role)
                new_refresh_token = create_refresh_token(user)
                # добавить старый access токен в блэк-лист redis
                await self.add_to_black_list(access_token, ACCESS_TOKEN_TYPE)
                # удалить старый refresh токен из вайт-листа redis
                await self.del_from_white_list(refresh_token)
                # добавить новый refresh токен в вайт-лист redis
                await self.add_to_white_list(new_refresh_token, REFRESH_TOKEN_TYPE)
                return Tokens(
                    access_token=new_access_token, refresh_token=new_refresh_token
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="uncorrect token"
                )

    async def check_permissions(
        self, access_token: str, required_permissions: str
    ) -> bool:
        """Проверка прав доступа у пользователя."""
        payload = self.token_decode(access_token)
        user_uuid = payload.get("sub")
        user = await self.get_instance_by_id(user_uuid)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="user not found",
            )
        try:
            user_role = await self.get_user_role(user_uuid)
            user_permissions = []
            for perm in user_role._data[0].permissions:
                user_permissions.append(perm.name)

            if required_permissions not in user_permissions:
                return False
        except AttributeError:
            return False


@lru_cache()
def get_user_service(
    redis: RedisCache = Depends(get_redis),
    db: AsyncSession = Depends(get_session),
) -> UserService:

    return UserService(redis, db)
