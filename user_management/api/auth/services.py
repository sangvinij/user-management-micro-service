from fastapi import HTTPException, status

from user_management.database.models.user import User
from user_management.utils.manager import UserManager


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
    def verify_password(password1: str, password2: str) -> bool:
        # when hashing password feature is implemented this function will be changed
        return password1 == password2
