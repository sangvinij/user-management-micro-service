import uuid
from typing import Optional

from sqlalchemy import or_, select
from sqlalchemy.exc import NoResultFound

from user_management.database.db_settings import async_session_maker
from user_management.database.models import User


class UserManager:
    """A class for managing user-related data in a database."""

    model = User

    async def get_by_username(self, username: str) -> Optional[User]:
        """Retrieve a user from the database based on the provided username, phone_number or email."""
        async with async_session_maker() as session:
            try:
                user = await session.scalar(
                    select(self.model).filter(
                        or_(
                            User.username == username,
                            User.phone_number == username,
                            User.email == username,
                        )
                    )
                )

            except NoResultFound:
                user = None

        return user

    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        async with async_session_maker() as session:
            try:
                user = await session.get(self.model, user_id)

            except NoResultFound:
                user = None

        return user

    async def get_list(self):
        pass

    async def create(self):
        pass

    async def update(self):
        pass

    async def delete(self):
        pass
