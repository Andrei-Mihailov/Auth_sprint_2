import http
import uuid
from enum import auto
from strenum import StrEnum

import requests
from requests.exceptions import ConnectionError
from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class Roles(StrEnum):
    ADMIN = auto()
    SUBSCRIBER = auto()


class CustomBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        url = settings.AUTH_API_LOGIN_URL
        payload = {
            'email': username,
            'password': password,
            # 'set_cookie': False
        }
        headers = {'X-Request-Id': str(uuid.uuid4())}
        try:
            response = requests.post(
                url,
                headers=headers,
                params=payload,
            )
        except ConnectionError:
            return None
        if response.status_code != http.HTTPStatus.OK:
            return None

        data = response.json()

        try:
            user, _ = User.objects.get_or_create(id=data['uuid'])
            user.email = data.get('email')
            user.first_name = data.get('first_name')
            user.last_name = data.get('last_name')
            user.is_staff = data.get('role') == Roles.ADMIN or data.get('is_superuser')
            user.is_superuser = data.get('is_superuser')
            user.is_active = data.get('active')
            user.save()
        except Exception as e:
            return None

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
