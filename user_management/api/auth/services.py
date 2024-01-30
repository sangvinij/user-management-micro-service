import secrets
import uuid
from typing import Dict, Optional

import aioboto3
import sqlalchemy.exc
from fastapi import HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from pydantic import EmailStr
from redis.asyncio import Redis

from user_management.api.auth.schemas import SignupModel
from user_management.api.utils.exceptions import AlreadyExistsHTTPException, NotFoundHTTPException
from user_management.api.utils.hashers import PasswordHasher, ResetPasswordTokenHasher
from user_management.aws.service import AWSService
from user_management.config import config
from user_management.database.models.user import User
from user_management.logger_settings import logger
from user_management.managers.user_manager import UserManager
from user_management.redis_settings import get_redis_client


class AuthService:
    manager = UserManager()
    password_hasher = PasswordHasher()
    reset_password_token_hasher = ResetPasswordTokenHasher()

    async def authenticate(self, username, password) -> User:
        user = await self.manager.get_by_username(username)
        if not user or not self.password_hasher.verify_password(password, user.password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid credentials")

        if user.is_blocked:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user blocked")

        return user

    async def signup(self, user: SignupModel, s3: aioboto3.Session.client, file: Optional[UploadFile] = None) -> User:
        aws_service: AWSService = AWSService(aws_client=s3)
        user_data = user.model_dump(exclude_none=True, exclude_unset=True)

        if file:
            image_s3_path = await aws_service.upload_image(key=user.username, file=file)
            user_data["image_s3_path"] = image_s3_path

        try:
            created_user: User = await self.manager.create_user(user_data=user_data)
        except sqlalchemy.exc.IntegrityError as e:
            logger.error(e)
            raise AlreadyExistsHTTPException(
                detail="user with such credentials already exists",
            )

        return created_user

    @staticmethod
    def generate_password_reset_token():
        token: str = secrets.token_urlsafe(64)
        return token

    @staticmethod
    def generate_password_reset_url(token: str) -> str:
        url: str = f"{config.WEBAPP_HOST}/password/reset/{token}"
        return url

    @staticmethod
    async def add_password_reset_token_to_redis(token: str, user_id: uuid.UUID) -> None:
        redis_client: Redis = await get_redis_client().__anext__()

        await redis_client.set(token, str(user_id))

    async def reset_password(self, email: EmailStr, ses: aioboto3.Session.client) -> Dict:
        aws_service: AWSService = AWSService(aws_client=ses)
        user: Optional[User] = await self.manager.get_by_email(email=email)

        token: str = self.generate_password_reset_token()

        if user:
            await self.add_password_reset_token_to_redis(token=token, user_id=user.user_id)

        reset_password_url: str = self.generate_password_reset_url(token=token)

        await aws_service.send_mail(subject_text="Reset Password", message_text=reset_password_url, addresses=[email])

        return {"url": reset_password_url}

    async def reset_password_confirm(self, token: str, password: str, password_retype: str) -> JSONResponse:
        redis_client: Redis = await get_redis_client().__anext__()

        user_id_bytes: bytes = await redis_client.get(token)

        if not user_id_bytes:
            raise NotFoundHTTPException(detail="user not found")

        user_id: uuid.UUID = uuid.UUID(user_id_bytes.decode())

        if password != password_retype:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")

        await self.manager.update_user(user_id=user_id, user_data={"password": password})

        return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "password changed successfully"})
