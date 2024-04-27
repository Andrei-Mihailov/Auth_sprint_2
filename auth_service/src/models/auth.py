from pydantic import BaseModel
from datetime import datetime, timezone
from models.value_objects import AuthID, UserID


class Authentication(BaseModel):
    """Модель аутификации."""

    id: AuthID
    user_id: UserID
    user_agent: str
    date_auth: datetime = datetime.now(timezone.utc)


class Tokens(BaseModel):
    """Модель токена."""

    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
