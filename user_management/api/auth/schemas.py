import datetime
import uuid
from typing import Optional

from fastapi import Form
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
    is_blocked: bool
    role_id: int
    group_id: int

    @classmethod
    def as_form(
        cls,
        name: str = Form(min_length=1),
        surname: str = Form(min_length=1),
        username: str = Form(min_length=1),
        password: str = Form(min_length=5),
        phone_number: str = Form(),
        email: EmailStr = Form(),
        is_blocked: bool = Form(default=False),
        role_id: int = Form(),
        group_id: int = Form(),
    ):
        return cls(
            name=name,
            surname=surname,
            username=username,
            password=password,
            phone_number=phone_number,
            email=email,
            is_blocked=is_blocked,
            role_id=role_id,
            group_id=group_id,
        )


class SignupResponseModel(SignupModel):
    user_id: uuid.UUID
    password: Optional[str] = Field(exclude=True, default=None)
    image_s3_path: str
    modified_at: datetime.datetime
    created_at: datetime.datetime


class ResetPasswordModel(BaseModel):
    email: EmailStr


class ResetPasswordConfirmModel(BaseModel):
    token: str
    password: str
    password_retype: str
