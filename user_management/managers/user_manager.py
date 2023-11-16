import datetime
import uuid
from typing import Dict, Optional

from passlib.hash import pbkdf2_sha256
from sqlalchemy import delete, or_, select
from sqlalchemy.exc import NoResultFound

from user_management.config import config
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

    async def create(self, user_data: Dict) -> User:
        password = user_data.pop("password")
        hashed_password = pbkdf2_sha256.hash(password)
        user_data["password"] = hashed_password

        user = self.model(**user_data)

        async with async_session_maker() as session:
            session.add(user)
            await session.commit()

        return user

    async def update_user(self, user_id: uuid.UUID, user_data: Dict) -> User:
        user: User = await self.get_by_id(user_id)
        async with async_session_maker() as session:
            for field, value in user_data.items():
                setattr(user, field, value)

            user.modified_at = datetime.datetime.now(tz=config.get_timezone())

            session.add(user)
            await session.commit()

        return user

    async def delete_user(self, user_id: uuid.UUID) -> uuid.UUID:
        async with async_session_maker() as session:
            deleted_user_id: uuid.UUID = await session.scalar(
                delete(self.model).filter_by(user_id=user_id).returning(self.model.user_id)
            )

            await session.commit()

        return deleted_user_id
