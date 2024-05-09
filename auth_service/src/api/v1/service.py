from fastapi import status, HTTPException, Request, Depends
from pydantic import BaseModel, Field
from pydantic_core import ValidationError
from functools import wraps
from typing import Union
from api.v1.schemas.auth import (
    TokenParams,
)


from services.role import RoleService
from services.permission import PermissionService
from services.utils import decode_jwt, check_date_and_type_token
from services.user import UserService, get_user_service
from models.value_objects import Role_names


class PaginationParams(BaseModel):
    page_number: int = Field(1, ge=1)
    page_size: int = Field(1, ge=1)


def get_tokens_from_cookie(request: Request) -> TokenParams:
    try:
        token = TokenParams(
            access_token=request.cookies.get("access_token"),
            refresh_token=request.cookies.get("refresh_token"),
        )
        return token
    except (ValidationError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tokens is not found"
        )


async def check_jwt(request: Request, service: UserService = Depends(get_user_service)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    tokens = get_tokens_from_cookie(request)
    payload = decode_jwt(jwt_token=tokens.access_token)
    if check_date_and_type_token(payload, "access"):
        # проверка access токена в блэк листе redis
        if await service.get_from_black_list(tokens.access_token):
            raise credentials_exception
    raise credentials_exception


async def is_admin(payload: dict) -> bool:
    """Проверка, является ли пользователь администратором, используя расшифрованный payload."""
    user_is_admin = payload.get("is_admin")
    return user_is_admin


async def is_superuser(payload: dict) -> bool:
    """Проверка, является ли пользователь суперпользователем, используя расшифрованный payload."""
    user_is_superuser = payload.get("is_superuser")
    return user_is_superuser


async def has_permission(access_token: str) -> bool:
    """Проверка разрешений пользователя на основе токена."""
    payload = decode_jwt(jwt_token=access_token)
    if await is_admin(payload):
        return True
    return False


def allow_this_user(function):
    @wraps(function)
    async def wrapper(*args, **kwargs):
        request = kwargs.get("request", None)
        service: Union[RoleService, PermissionService] = kwargs.get(
            "role_service", kwargs.get("permission_service", None)
        )
        user_id = kwargs.get("user_id", None)
        tokens = get_tokens_from_cookie(request)
        payload = decode_jwt(jwt_token=tokens.access_token)
        check_superuser = await is_superuser(payload)

        if check_superuser:
            return await function(*args, **kwargs)

        has_perm = await has_permission(tokens.access_token)
        if has_perm:
            if user_id:
                user_role = await service.get_user_role(user_id)

                if user_role == Role_names.admin:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="This operation is forbidden for you",
                    )

                else:
                    return await function(*args, **kwargs)
            else:
                return await function(*args, **kwargs)
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This operation is forbidden for you",
            )

    return wrapper
