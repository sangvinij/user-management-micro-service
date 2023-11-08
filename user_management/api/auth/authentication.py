import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from user_management.api.auth.tokens import AuthToken
from user_management.database.db_settings import get_async_session

from ...database.models.group import Group
from ...database.models.role import Role
from ...database.models.user import User


async def get_current_user_by_id(user_id, session: AsyncSession = Depends(get_async_session)):
    try:
        user = await session.get(User, user_id)

    except NoResultFound:
        return None

    return user


async def get_current_user_by_username(username, session: AsyncSession = Depends(get_async_session)):
    try:
        query = await session.execute(
            select(User).filter(or_(User.username == username, User.phone_number == username, User.email == username))
        )
        user = query.scalar_one()

    except NoResultFound:
        return None

    return user
