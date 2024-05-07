import http
import uuid
from enum import auto
from strenum import StrEnum

import requests
from requests.exceptions import ConnectionError
from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser


User = get_user_model()


class Roles(StrEnum):
    ADMIN = auto()
    SUBSCRIBER = auto()


class CustomBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        url = settings.AUTH_API_LOGIN_URL
        payload = {
            'email': username,
            'password': password
        }
        headers = {'X-Request-Id': str(uuid.uuid4())}
        try:
            response = requests.post(
                url,
                headers=headers,
                params=payload,
            )
            if response.status_code != http.HTTPStatus.OK:
                return None
            data = response.json()
        except ConnectionError:
            data = AnonymousUser().__dict__

        try:
            user, _ = User.objects.get_or_create(id=data.get('uuid', 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'))
            user.email = data.get('email', 'anonym')
            user.first_name = data.get('first_name', 'anonym')
            user.last_name = data.get('last_name', 'anonym')
            user.is_staff = data.get('role', None) == Roles.ADMIN or data.get('is_superuser', False)
            user.is_superuser = data.get('is_superuser', False)
            user.is_active = data.get('active', True)
            user.save()
        except Exception:
            return None

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
