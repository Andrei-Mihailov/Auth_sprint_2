import requests
from auth_service.src.core.config import Settings
from auth_service.src.services.oauth.base import  OAuthService

class YandexOAuthService(OAuthService):
    def __init__(self):
        self.client_id = Settings().oauth_yandex.client_id
        self.client_secret = Settings().oauth_yandex.client_secret
        self.oauth_url = Settings().oauth_yandex.oauth_url
        self.login_url = Settings().oauth_yandex.login_url

    def get_authorize_url(self, state: str = None) -> str:
        """Формирование адреса для авторизации в яндексе"""
        authorize_url = self.oauth_url + "authorize?"
        authorize_url = authorize_url + "response_type=code"
        authorize_url = authorize_url + f"&client_id={self.client_id}"

        if state:
            authorize_url = authorize_url + f'&state={state}'

        return authorize_url

    def get_token(self, confirmation_code: str, state: str = None) -> dict:
        """Обмен кода подтверждения на токен."""
        url = self.oauth_url + "token"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        payload = {
            'grant_type': 'authorization_code',
            'code': confirmation_code,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }
        request = requests.post(url, data=payload, headers=headers)
        data = None

        if request.status_code == 400:
            data = request.json()
            data['authorize_url'] = self.get_authorize_url()

        if request.status_code == 200:
            data = request.json()

        return data

    def refresh_token(self, refresh_token) -> dict:
        """Обновление токена через refresh_token."""
        url = self.oauth_url + 'token'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        payload = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }
        request = requests.post(url, data=payload, headers=headers)
        data = None

        if request.status_code == 400:
            data = request.json()

        if request.status_code == 200:
            data = request.json()

    def get_user_info(self, access_token) -> dict:
        """Запрос информации о пользователе."""
        url = self.login_url + 'info'
        headers = {
            'Authorization': f'OAuth {access_token}',
        }
        request = requests.get(url, headers=headers)

        data = None

        if request.status_code == 400:
            data = request.json()

        if request.status_code == 200:
            data = request.json()

        return data

