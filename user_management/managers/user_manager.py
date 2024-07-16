import datetime
import uuid
from typing import Dict, Optional

from pydantic import EmailStr
from sqlalchemy import delete, desc, func, or_, select
from sqlalchemy.engine import ScalarResult
from sqlalchemy.exc import NoResultFound
from sqlalchemy.sql.selectable import Select

from user_management.api.utils.hashers import PasswordHasher
from user_management.config import config
from user_management.database.db_settings import async_session_maker
from user_management.database.models import User


class UserManager:
    """A class for managing user-related data in a database."""

    model = User
    password_hasher = PasswordHasher()

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

    async def get_by_email(self, email: EmailStr) -> Optional[User]:
        async with async_session_maker() as session:
            try:
                user = await session.scalar(select(self.model).filter_by(email=email))
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

    async def get_all(
        self,
        offset: int,
        limit: int = 50,
        name: Optional[str] = None,
        sort_field: Optional[str] = None,
        ord_direction: str = "asc",
        moderator: Optional[User] = None,
    ) -> Dict:
        query: Select = select(self.model).limit(limit=limit).offset(offset=offset)
        total_count_query: Select = select(func.count()).select_from(self.model)

        if sort_field:
            query = query.order_by(desc(sort_field)) if ord_direction == "desc" else query.order_by(sort_field)

        if name:
            query = query.filter(self.model.name.ilike(f"%{name}%"))

        if moderator:
            query = query.filter(self.model.group_id == moderator.group.group_id)
            total_count_query = total_count_query.filter(self.model.group_id == moderator.group_id)

        async with async_session_maker() as session:
            users: ScalarResult = await session.scalars(query)
            total_count: int = await session.scalar(total_count_query)

        result: Dict = {"total_count": total_count, "users": users.unique().all()}

        return result

    async def create_user(self, user_data: Dict) -> User:
        password = user_data.pop("password")

        hashed_password = self.password_hasher.hash_password(password)
        user_data["password"] = hashed_password

        user = self.model(**user_data)

        async with async_session_maker() as session:
            session.add(user)
            await session.commit()

        return user

    async def update_user(self, user_id: uuid.UUID, user_data: Dict) -> Optional[User]:
        user: User = await self.get_by_id(user_id)

        if "password" in user_data:
            password = user_data.pop("password")

            hashed_password = self.password_hasher.hash_password(password)
            user_data["password"] = hashed_password

        if user is None:
            return None

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
