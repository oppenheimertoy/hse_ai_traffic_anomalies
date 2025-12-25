from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Column, ForeignKey, Table, func
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


class Role(Base, IDMixin):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    users: Mapped["User"] = relationship(back_populates="roles", secondary=accounts_roles)
