import sqlalchemy.exc
from fastapi import HTTPException, status

from user_management.api.auth.schemas import SignupModel
from user_management.api.utils.exceptions import AlreadyExistsHTTPException
from user_management.api.utils.hashers import PasswordHasher
from user_management.aws_settings import AWSSettings
from user_management.database.models.user import User
from user_management.managers.user_manager import UserManager

from pydantic import EmailStr
import aioboto3


class AuthService:
    manager = UserManager()
    password_hasher = PasswordHasher()

    async def authenticate(self, username, password) -> User:
        user = await self.manager.get_by_username(username)
        if not user or not self.password_hasher.verify_password(password, user.password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid credentials")

        if user.is_blocked:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user blocked")

        return user

    async def signup(self, user: SignupModel) -> User:
        try:
            created_user: User = await self.manager.create_user(user.model_dump())
        except sqlalchemy.exc.IntegrityError:
            raise AlreadyExistsHTTPException(
                detail="user with such credentials already exists",
            )

        return created_user

    @staticmethod
    async def reset_password(address: EmailStr, ses: aioboto3.Session.client):
        aws_service = AWSSettings(aws_client=ses)

        rs = await aws_service.send_mail(subject_text='fas', message_text='sfa', addresses=(address,))

        return rs
