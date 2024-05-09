from services.oauth.base import AbstractOAuthService
from services.oauth.yandex import YandexOAuthService


def get_provider_service(provider_name: str) -> AbstractOAuthService:
    oauth_service = None

    if provider_name == 'yandex':
        oauth_service = YandexOAuthService()

    return oauth_service
