from pydantic import BaseModel, Field
from datetime import datetime

from models.value_objects import UserID, AuthID


class AuthenticationSchema(BaseModel):
    uuid: AuthID
    user_id: UserID
    user_agent: str
    date_auth: datetime


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


class AuthenticationParams(BaseModel):
    email: str = Field(description="Email")
    password: str = Field(description="Пароль")


class AuthenticationData(BaseModel):
    user_agent: str
    user_id: UserID


class TokenParams(BaseModel):
    access_token: str
    refresh_token: str
