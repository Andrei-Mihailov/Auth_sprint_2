from pydantic import BaseModel, Field
from typing import Union

from models.value_objects import UserID


class UserSchema(BaseModel):
    uuid: UserID
    email: str
    first_name: Union[str, None]
    last_name: Union[str, None]


class UserParams(BaseModel):
    email: str = Field(description="Email")
    first_name: Union[str, None] = Field(
        description="Имя", default=None, allow_none=True
    )
    last_name: Union[str, None] = Field(
        description="Фамилия", default=None, allow_none=True
    )
    password: str = Field(description="Пароль")


class UserEditParams(BaseModel):
    email: Union[str, None] = Field(description="Email", default=None, allow_none=True)
    first_name: Union[str, None] = Field(
        description="Имя", default=None, allow_none=True
    )
    last_name: Union[str, None] = Field(
        description="Фамилия", default=None, allow_none=True
    )
    password: Union[str, None] = Field(
        description="Пароль", default=None, allow_none=True
    )
