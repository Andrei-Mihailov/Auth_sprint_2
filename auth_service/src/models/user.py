from pydantic import BaseModel
from datetime import datetime
from typing import Union

from models.value_objects import UserID


class User(BaseModel):
    """Модель пользователя на сайте."""

    id: UserID
    email: str
    first_name: Union[str, None]
    last_name: Union[str, None]
    password: bytes
    created_at: datetime = datetime.now
    active: bool = True

    class Config:
        orm_mode = True
