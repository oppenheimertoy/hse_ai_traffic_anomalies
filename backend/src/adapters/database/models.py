from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import JSON, Column, ForeignKey, Table, func
from sqlalchemy import UUID as SAUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=False,
    )

    deleted: Mapped[bool] = mapped_column(server_default="false", nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(nullable=True)


class IDMixin:
    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        index=True,
        nullable=False,
        unique=True,
        default=uuid4,
    )


accounts_roles = Table(
    "accounts_roles",
    Base.metadata,
    Column("account_id", SAUUID(), ForeignKey("accounts.id"), primary_key=True),
    Column("role_id", SAUUID(), ForeignKey("roles.id"), primary_key=True),
)


class User(Base, IDMixin):
    __tablename__ = "accounts"

    username: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False)

    roles = relationship("Role", secondary=accounts_roles, back_populates="users")
    tokens = relationship("UserToken", back_populates="user")
    files = relationship("File", back_populates="user")
    history = relationship("History", back_populates="user")

class Role(Base, IDMixin):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    users: Mapped["User"] = relationship(
        back_populates="roles", secondary=accounts_roles
    )


class UserToken(Base, IDMixin):
    __tablename__ = "tokens"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    token: Mapped[str] = mapped_column(nullable=False, unique=True)
    expires_at: Mapped[datetime] = mapped_column()

    user = relationship("User", back_populates="tokens")


class History(Base, IDMixin):
    __tablename__ = "history"
    user_id: Mapped[UUID] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    file_id: Mapped[UUID] = mapped_column(ForeignKey("files.id"), nullable=False)

    result: Mapped[dict] = mapped_column(JSON, nullable=True, default=None)
    status: Mapped[str] = mapped_column(nullable=False, default="CREATED")
    error: Mapped[str] = mapped_column(nullable=True, default=None)

    user = relationship("User", back_populates="history")
    file = relationship("File", back_populates="history")
class File(Base, IDMixin):
    __tablename__ = "files"
    created_by: Mapped[UUID] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    file_url: Mapped[str] = mapped_column(nullable=False,
    )

    history = relationship("History", back_populates="file")
    user = relationship("User", back_populates="files")