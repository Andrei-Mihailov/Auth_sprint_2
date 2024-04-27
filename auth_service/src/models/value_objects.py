from typing import NewType

from strenum import StrEnum
from uuid import UUID

# Алиасы для идентификаторов
UserID = NewType("UserID", UUID)
AuthID = NewType("AuthID", UUID)
RoleID = NewType("RoleID", UUID)
PermissionID = NewType("PermissionID", UUID)


class Role_names(StrEnum):
    """Роли пользователя на сайте."""

    admin = "admin"
    user = "user"
    guest = "guest"
