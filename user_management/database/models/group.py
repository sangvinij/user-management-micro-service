from datetime import datetime

from sqlalchemy import TIMESTAMP, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Group(Base):
    __tablename__ = "group"
    group_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(length=255), unique=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))

    user = relationship("User", back_populates="group", uselist=True)

    def __str__(self):
        return f"{self.name}"
