from pydantic import BaseModel, Base, BaseMixin
from datetime import datetime
from typing import Union
from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, backref

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

class SocialAccount(Base, BaseMixin):
    __tablename__ = 'social_account'

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    user = relationship(User, backref=backref('social_accounts', lazy=True))

    social_id = Column(Text, nullable=False)
    social_name = Column(Text, nullable=False)

    __table_args__ = (UniqueConstraint('social_id', 'social_name', name='social_pk'), )

    def __repr__(self):
        return f'<SocialAccount {self.social_name}:{self.user_id}>'