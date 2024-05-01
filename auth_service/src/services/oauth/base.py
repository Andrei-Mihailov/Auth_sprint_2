from abc import ABC, abstractmethod


class OAuthService(ABC):
    @abstractmethod
    def get_authorize_url(self, state: str = None) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_token(self, confirmation_code: str, state: str = None) -> dict:
        raise NotImplementedError

    @abstractmethod
    def refresh_token(self, refresh_token) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_user_info(self, access_token) -> dict:
        raise NotImplementedError
