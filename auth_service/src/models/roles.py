from pydantic import BaseModel
from models.value_objects import RoleID, Role_names
from models.permission import Permission
from models.user import User


class Role(BaseModel):
    """Модель роли."""

    id: RoleID
    type: Role_names
    permissions: Permission


class User_Role(BaseModel):
    """Модель роли для пользователя."""

    user: User
    role: Role
