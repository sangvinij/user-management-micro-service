import sqlalchemy.exc
from fastapi import HTTPException, status
from passlib.hash import pbkdf2_sha256

from user_management.api.auth.schemas import SignupModel
from user_management.database.models.user import User
from user_management.managers.user_manager import UserManager


class AuthService:
    manager = UserManager()

    async def authenticate(self, username, password) -> User:
        user = await self.manager.get_by_username(username)
        if not user or not self.verify_password(user.password, password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid credentials")

        if user.is_blocked:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user blocked")

        return user

    @staticmethod
    def verify_password(hashed_password: str, request_password: str) -> bool:
        return pbkdf2_sha256.verify(request_password, hashed_password)

    async def signup(self, user: SignupModel) -> User:
        try:
            created_user: User = await self.manager.create(user.model_dump())
        except sqlalchemy.exc.IntegrityError:
            raise HTTPException(
                status_code=400, detail="user with such credentials already exists or invalid role/group"
            )

        return created_user
