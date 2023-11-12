import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, UUID, Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...config import config
from .base import Base


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
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    modified_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=datetime.now(tz=config.get_timezone())
    )

    group_id: Mapped[int] = mapped_column(ForeignKey("group.group_id"))
    role_id: Mapped[int] = mapped_column(ForeignKey("role.role_id"))

    role = relationship("Role", back_populates="user", uselist=False)
    group = relationship("Group", back_populates="user", uselist=False)

    def __str__(self):
        return f"{self.username}"
