import datetime
import uuid
from typing import Optional

from fastapi import Form
from pydantic import BaseModel, EmailStr, Field


class LoginModel(BaseModel):
    access_token: str
    refresh_token: str


class SignupModel(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=5)
    phone_number: str
    email: EmailStr
    name: Optional[str] = None
    surname: Optional[str] = None
    group_id: Optional[int] = None

    @classmethod
    def as_form(
        cls,
        username: str = Form(min_length=1),
        password: str = Form(min_length=5),
        phone_number: str = Form(),
        email: EmailStr = Form(),
        name: Optional[str] = Form(default=None),
        surname: Optional[str] = Form(default=None),
        group_id: Optional[int] = Form(default=None),
    ):
        return cls(
            name=name,
            surname=surname,
            username=username,
            password=password,
            phone_number=phone_number,
            email=email,
            group_id=group_id,
        )


class SignupResponseModel(SignupModel):
    user_id: uuid.UUID
    password: Optional[str] = Field(exclude=True, default=None)
    image_s3_path: Optional[str]
    is_blocked: Optional[bool]
    role: Optional[str]
    modified_at: datetime.datetime
    created_at: datetime.datetime


class ResetPasswordModel(BaseModel):
    email: EmailStr


class ResetPasswordConfirmModel(BaseModel):
    token: str
    password: str
    password_retype: str
