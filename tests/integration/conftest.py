import asyncio
import datetime
import secrets
import string
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import delete

from user_management.config import config
from user_management.database.db_settings import async_session_maker, get_async_session
from user_management.database.models import Group, Role, User


@pytest.fixture(scope="package")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="package")
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(base_url=config.WEBAPP_TEST_HOST) as ac:
        yield ac


@pytest_asyncio.fixture(scope="package")
async def roles():
    admin_role = Role(role_name="ADMIN")
    moderator_role = Role(role_name="MODERATOR")
    user_role = Role(role_name="USER")

    async with async_session_maker() as session:
        session.add_all((admin_role, moderator_role, user_role))
        await session.commit()

    yield {"admin_role": admin_role, "moderator_role": moderator_role, "user_role": user_role}

    async with async_session_maker() as session:
        stmt = delete(Role)
        await session.execute(stmt)
        await session.commit()


@pytest_asyncio.fixture(scope="package")
async def group():
    test_group = Group(name="test group", created_at=datetime.datetime.now())

    async with async_session_maker() as session:
        session.add(test_group)
        await session.commit()

    yield test_group

    async with async_session_maker() as session:
        stmt = delete(Group).filter(Group.group_id == test_group.group_id)
        await session.execute(stmt)
        await session.commit()


def generate_credentials():
    email = "test." + "".join(secrets.choice(string.ascii_lowercase) for _ in range(6)) + "@example.com"
    password = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
    username = "test_".join(secrets.choice(string.ascii_lowercase) for _ in range(8))
    phone_number = "+37529" + "".join(secrets.choice(string.digits) for _ in range(7))
    return {"email": email, "password": password, "username": username, "phone_number": phone_number}


@pytest_asyncio.fixture
async def user(roles, group):
    # when an API is created for creating and deleting users, this fixture will work with this API instead of database

    role_id = roles["user_role"].role_id
    user_data = generate_credentials()
    user_data.update(
        {
            "name": "test_name",
            "surname": "test_surname",
            "is_blocked": False,
            "image_s3_path": "stub_path",
            "created_at": datetime.datetime.now(),
            "role_id": role_id,
            "group_id": group.group_id,
        }
    )
    test_user = User(**user_data)

    async with async_session_maker() as session:
        session.add(test_user)
        await session.commit()

    yield test_user

    async with async_session_maker() as session:
        stmt = delete(User).filter(User.user_id == test_user.user_id)
        await session.execute(stmt)
        await session.commit()
