import jwt
import uuid

from datetime import timedelta, datetime, timezone
from fastapi import HTTPException, status

from core.config import settings

from models.value_objects import Role_names

ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


def create_jwt(token_type: str, token_data: dict, expire_minutes: int) -> str:
    jwt_payload = {"type": token_type}
    jwt_payload.update(token_data)

    now_utc = datetime.now(timezone.utc)
    now_unix = now_utc.timestamp()
    expire_utc = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    expire_unix = expire_utc.timestamp()

    jwt_payload.update(exp=expire_unix, iat=now_unix)
    return encode_jwt(jwt_payload)


def create_access_token(user, user_role: Role_names = Role_names.user):
    # в теле токена хранится UUID пользователя, его роли и UUID самого токена
    payload = {
        "sub": str(user.id),  # userid
        "role_id": str(user.role_id) if user.role_id else None,
        "self_uuid": str(uuid.uuid4()),
        "is_admin": user_role == Role_names.admin,
        "is_superuser": user.is_superuser,
    }
    return create_jwt(
        ACCESS_TOKEN_TYPE, payload, settings.auth_jwt.access_token_expire_minutes
    )


def create_refresh_token(user):
    payload = {"sub": str(user.id), "self_uuid": str(uuid.uuid4())}
    return create_jwt(
        REFRESH_TOKEN_TYPE, payload, settings.auth_jwt.refresh_token_expire_minutes
    )


def encode_jwt(
    payload: dict,
    private_key: str = settings.auth_jwt.secret_key,
    algorithm: str = settings.auth_jwt.algorithm,
):
    return jwt.encode(payload, private_key, algorithm)


def decode_jwt(
    jwt_token: str,
    private_key: str = settings.auth_jwt.secret_key,
    algorithm: str = settings.auth_jwt.algorithm,
):
    try:
        decoded = jwt.decode(jwt_token, private_key, algorithms=[algorithm])
    except jwt.exceptions.DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    except jwt.exceptions.InvalidAlgorithmError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token algorithm"
        )
    except jwt.exceptions.InvalidSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token signature"
        )
    except jwt.exceptions.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired, refresh token",
        )
    return decoded


def hash_password(
    password: str,
) -> bytes:
    hash_pass = settings.pwd_context.hash(password)
    return hash_pass


def validate_password(hashed_password: bytes, password: str) -> bool:
    try:
        return settings.pwd_context.verify(password, hashed_password)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Incorrect password"
        )


def check_date_and_type_token(payload: dict, type_token_need: str) -> bool:

    type_token = payload.get("type")
    # проверка типа токена
    if type_token != type_token_need:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token type"
        )
    # проверяем срок действия access токена
    exp = payload.get("exp")
    now = datetime.timestamp(datetime.now())
    if now > exp:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token has expired, refresh token",
        )
    return True
