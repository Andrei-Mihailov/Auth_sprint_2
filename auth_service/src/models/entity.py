# models/entity.py
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, DateTime, String, ForeignKey, or_, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import string
from secrets import choice as secrets_choice

from db.postgres_db import Base
from services.utils import hash_password, validate_password


class Roles(Base):
    __tablename__ = "roles"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    type: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    permissions: Mapped[list["Permissions"]] = relationship(
        "Permissions", back_populates="role"
    )
    users: Mapped[list["User"]] = relationship("User", back_populates="role")


class Permissions(Base):
    __tablename__ = "permissions"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"), default=None, nullable=True
    )
    role: Mapped[Roles] = relationship("Roles", back_populates="permissions")


class SocialAccount(Base):
    __tablename__ = 'social_account'

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    user = relationship("User", back_populates='social_accounts')

    social_id = mapped_column(Text, nullable=False)
    social_name = mapped_column(Text, nullable=False)

    __table_args__ = (UniqueConstraint('social_id', 'social_name', name='social_pk'), )

    def __repr__(self):
        return f'<SocialAccount {self.social_name}:{self.user_id}>'


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), default=None, nullable=True)
    last_name: Mapped[str] = mapped_column(String(50), default=None, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now)
    active: Mapped[Boolean] = mapped_column(Boolean, default=True)
    role_id: Mapped[UUID] = mapped_column(ForeignKey("roles.id",
                                                     ondelete="CASCADE"),
                                          default=None,
                                          nullable=True
                                          )
    role: Mapped[Roles] = relationship("Roles",
                                       back_populates="users")
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    social_accounts: Mapped[list["SocialAccount"]] = relationship("SocialAccount",
                                                                  back_populates="user",
                                                                  foreign_keys="[SocialAccount.user_id]")

    def __init__(
        self,
        email: str,
        password: str,
        first_name: str = None,
        last_name: str = None,
        is_superuser: bool = False,
    ) -> None:
        self.email = email
        self.password = hash_password(password)
        self.first_name = first_name
        self.last_name = last_name
        self.is_superuser = is_superuser

    def check_password(self, password: str) -> bool:
        return validate_password(self.password, password)

    @classmethod
    def get_user_by_universal_login(self, login: Optional[str] = None, email: Optional[str] = None):
        return self.query.filter(or_(self.login == login, self.email == email)).first()

    def generate_random_string():
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets_choice(alphabet) for _ in range(16))

    def __repr__(self) -> str:
        return f"<User {self.email}>"


class Authentication(Base):
    __tablename__ = "authentication"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    user_agent: Mapped[str] = mapped_column(String(255), nullable=False)
    date_auth: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now)

    def __repr__(self) -> str:
        return f"<Authentication {self.id}>"
