import asyncio

from sqlalchemy.exc import IntegrityError

from user_management.api.utils.hashers import PasswordHasher
from user_management.config import config
from user_management.database.db_settings import async_session_maker
from user_management.database.models import Group, User
from user_management.logger_settings import logger


async def create_admin():
    async with async_session_maker() as session:
        hashed_password = PasswordHasher().hash_password(config.ADMIN_PASSWORD)

        try:
            admin: User = User(
                username=config.ADMIN_USERNAME,
                password=hashed_password,
                email=config.ADMIN_EMAIL,
                phone_number=config.ADMIN_PHONE_NUMBER,
                role="ADMIN",
            )
            session.add(admin)
            await session.commit()
            logger.info("admin created")

        except IntegrityError as e:
            logger.error(e)


async def main():
    await create_admin()


if __name__ == "__main__":
    asyncio.run(main())
