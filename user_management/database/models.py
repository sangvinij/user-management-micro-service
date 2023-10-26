import enum
import uuid
from datetime import datetime
from typing import List

from sqlalchemy import TIMESTAMP, UUID, Boolean, Enum, ForeignKey, Integer, MetaData, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    metadata = MetaData()


class Group(Base):
    __tablename__ = "group"
    group_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(length=255), unique=True)
    user: Mapped[List["User"]] = relationship(back_populates="group", uselist=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP)

    def __str__(self):
        return f"{self.name}"


class Role(Base):
    __tablename__ = "role"
    role_name: Mapped[enum.Enum] = mapped_column(Enum("USER", "ADMIN", "MODERATOR", name="user_role"), primary_key=True)
    user: Mapped[List["User"]] = relationship(back_populates="role", uselist=True)

    def __str__(self):
        return f"{self.user}"


class User(Base):
    __tablename__ = "user"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(length=255))
    surname: Mapped[str] = mapped_column(String(length=255))
    username: Mapped[str] = mapped_column(String(length=255), unique=True)
    password: Mapped[str] = mapped_column(String(length=255))
    phone_number: Mapped[str] = mapped_column(String(length=20), unique=True)
    email: Mapped[str] = mapped_column(String(length=255), unique=True)
    image_s3_path: Mapped[str] = mapped_column(String(length=255))
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP)
    modified_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.now())

    group_id: Mapped[int] = mapped_column(ForeignKey("group.group_id"))
    role_name: Mapped[enum.Enum] = mapped_column(ForeignKey("role.role_name"))

    role: Mapped["Role"] = relationship(back_populates="user", uselist=False)
    group: Mapped["Group"] = relationship(back_populates="user", uselist=False)

    def __str__(self):
        return f"{self.username}"
