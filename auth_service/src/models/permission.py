from pydantic import BaseModel
from models.value_objects import PermissionID


class Permission(BaseModel):
    """Модель разрешений."""

    id: PermissionID
    name: str
