import jwt
import aiohttp

from fastapi import status, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import Optional

from core.config import settings


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


class JWTBearer(HTTPBearer):
    def __init__(self, check_user: bool = False, auto_error: bool = True):
        super().__init__(auto_error=auto_error)
        self.check_user = check_user

    async def __call__(self, request: Request) -> dict:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if not credentials:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid authorization code.')
        if not credentials.scheme == 'Bearer':
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Only Bearer token might be accepted')
        decoded_token = self.parse_token(credentials.credentials)
        if not decoded_token:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid or expired token.')

        if self.check_user:
            # проверить usera в бд
            response = await self.check(
                'http://127.0.0.1:8080/api/v1/users/me',
                params={},
                headers={'Authorization': f'Bearer {credentials.credentials}'}
            )
            if response.status != status.HTTP_202_ACCEPTED:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User doesn't exist"
                )

        return decoded_token

    @staticmethod
    def parse_token(jwt_token: str) -> Optional[dict]:
        return decode_jwt(jwt_token=jwt_token)

    @staticmethod
    async def check(query: str, params: dict = {}, headers: dict = {}, json: dict = {}):
        async with aiohttp.ClientSession(headers=headers) as client:
            response = await client.get(query, json=json, params=params)
        return response


security_jwt = JWTBearer()
security_jwt_check = JWTBearer(check_user=True)
