from auth_service.src.services.oauth.base import OAuthService
from auth_service.src.services.oauth.yandex import YandexOAuthService


def get_provider_service(provider_name: str) -> OAuthService:
    oauth_service = None

    if provider_name == 'yandex':
        oauth_service = YandexOAuthService()

    return oauth_service