from fastapi import Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from user_management.database.db_settings import get_async_session

from ...database.models.user import User


class AuthBackend:
    async def authenticate(self, username, password, session: AsyncSession = Depends(get_async_session)):
        try:
            query = await session.execute(
                select(User).filter(
                    or_(
                        User.username == username,
                        User.phone_number == username,
                        User.email == username,
                    )
                )
            )
            user = query.scalar_one()

        except NoResultFound:
            user = None

        if not user or not self.verify_password(user.password, password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid credentials")

        return user

    @staticmethod
    def verify_password(password1: str, password2: str) -> bool:
        return password1 == password2


auth_backend = AuthBackend()
