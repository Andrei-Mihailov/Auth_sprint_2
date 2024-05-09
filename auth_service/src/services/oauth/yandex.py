from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from functools import lru_cache
from http import HTTPStatus

from core.config import yandex_settings
from services.oauth.base import AbstractOAuthService
from services.base_service import BaseService
from db.postgres_db import get_session
from models.entity import SocialAccount, User
from services.utils import generate_random_string
from api.v1.schemas.users import UserParams
import httpx


class YandexOAuthService(AbstractOAuthService, BaseService):
    def __init__(self, storage: AsyncSession = None):
        super().__init__(None, storage)
        self.client_id = yandex_settings.client_id
        self.client_secret = yandex_settings.client_secret
        self.oauth_url = yandex_settings.oauth_url
        self.login_url = yandex_settings.login_url
        self.model = SocialAccount

    async def create_social_account(self, social_params) -> SocialAccount:
        social_user = await self.create_new_instance(social_params)
        return social_user

    async def get_social_account(self, social_id, social_name) -> SocialAccount:
        social_accound = await self.get_instance_data(social_id, social_name)
        return social_accound

    async def get_authorize_url(self, state: str = None) -> str:
        """Формирование адреса для авторизации в яндексе"""
        authorize_url = self.oauth_url + "authorize?"
        authorize_url = authorize_url + "response_type=code"
        authorize_url = authorize_url + f"&client_id={self.client_id}"

        if state:
            authorize_url = authorize_url + f'&state={state}'

        return authorize_url

    async def register(self, code):
        data_token = self.get_token(code)
        social_user = self.get_user_info(data_token['access_token'])
        user_params = UserParams(
            first_name=social_user['first_name'],
            last_name=social_user['last_name'],
            email=social_user['default_email'],
            password=generate_random_string()
        )
        account = await self.get_social_account(
            social_id=social_user['psuid'],
            social_name='yandex'
        )
        if account:
            return account, user_params

        user = await self.get_user_by_email(social_user['default_email'])

        social_params = SocialAccount(
            user=user,
            social_id=social_user['psuid'],
            social_name="yandex"
        )
        account = await self.create_social_account(
            social_params
        )
        return account, user_params

    async def set_user_data(self, social_account: SocialAccount, user: User):
        social_account.user_id = user.id
        await self.change_instance_data(social_account.id, social_account)

    async def get_token(self, code: str) -> dict:
        """Обмен кода подтверждения на токен."""
        url = self.oauth_url + "token"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        payload = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=payload, headers=headers)
        data = None

        if response.status_code == HTTPStatus.BAD_REQUEST:
            data = response.json()
            data['authorize_url'] = await self.get_authorize_url()

        if response.status_code == HTTPStatus.OK:
            data = response.json()

        return data

    async def get_user_info(self, access_token) -> dict:
        """Запрос информации о пользователе."""
        url = self.login_url + 'info'
        headers = {
            'Authorization': f'OAuth {access_token}',
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)

        data = None

        if response.status_code == HTTPStatus.BAD_REQUEST:
            data = response.json()

        if response.status_code == HTTPStatus.OK:
            data = response.json()

        return data


@ lru_cache()
def get_yandex_service(
    db: AsyncSession = Depends(get_session)
) -> YandexOAuthService:

    return YandexOAuthService(db)
