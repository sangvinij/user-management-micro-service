import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, UUID, Boolean, ForeignKey, String, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...config import config
from .base import Base


class User(Base):
    __tablename__ = "user"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(length=255), nullable=True)
    surname: Mapped[str] = mapped_column(String(length=255), nullable=True)
    username: Mapped[str] = mapped_column(String(length=255), unique=True)
    password: Mapped[str] = mapped_column(String(length=255))
    role: Mapped[Enum] = mapped_column(Enum("USER", "ADMIN", "MODERATOR", name="user_role"), default="USER")
    phone_number: Mapped[str] = mapped_column(String(length=20), unique=True)
    email: Mapped[str] = mapped_column(String(length=255), unique=True)
    image_s3_path: Mapped[str] = mapped_column(String(length=255), nullable=True)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=datetime.now(tz=config.get_timezone())
    )
    modified_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=datetime.now(tz=config.get_timezone())
    )

    group_id: Mapped[int] = mapped_column(ForeignKey("group.group_id"), nullable=True)

    group = relationship("Group", back_populates="user", uselist=False, lazy="joined")

    def __str__(self):
        return f"{self.username}"
