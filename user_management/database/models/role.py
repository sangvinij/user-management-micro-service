import enum

from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Role(Base):
    __tablename__ = "role"
    role_name: Mapped[enum.Enum] = mapped_column(Enum("USER", "ADMIN", "MODERATOR", name="user_role"), primary_key=True)

    user = relationship("User", back_populates="role", uselist=True)

    def __str__(self):
        return f"{self.user}"
