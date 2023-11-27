import uuid
from typing import Optional

from fastapi import UploadFile
from pydantic import BaseModel, EmailStr, Field


class LoginModel(BaseModel):
    access_token: str
    refresh_token: str


class SignupModel(BaseModel):
    name: str = Field(min_length=1)
    surname: str = Field(min_length=1)
    username: str = Field(min_length=1)
    password: str = Field(min_length=5)
    phone_number: str
    email: EmailStr
    is_blocked: bool = False
    role_id: int
    group_id: int
    file: UploadFile = Field(exclude=True)


class SignupResponseModel(SignupModel):
    user_id: uuid.UUID
    password: Optional[str] = Field(exclude=True, default=None)
    image_s3_path: str


class ResetPasswordModel(BaseModel):
    email: EmailStr


class ResetPasswordConfirmModel(BaseModel):
    token: str
    password: str
    password_retype: str
