from enum import IntEnum


class RoleAccess(IntEnum):
    USER = 1
    ADMIN = 10
    SUPERUSER = 20


DEFAULT_ROLE_DATA = {"name": "user", "access_level": 1}
