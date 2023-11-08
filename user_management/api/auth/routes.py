import datetime
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security.oauth2 import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from ...database.db_settings import get_async_session
from .authentication import get_current_user_by_username
from .schemas import LoginModel
from .tokens import AuthToken

auth_router = APIRouter(prefix="/auth", tags=["Auth"])

fake_user = {"id": uuid.uuid4(), "username": "admin", "password": "password"}

security = OAuth2PasswordBearer(tokenUrl="auth/login")


@auth_router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: AsyncSession = Depends(get_async_session)
):
    user = await get_current_user_by_username(username=form_data.username, session=session)

    if not user or user.password != form_data.password:
        raise HTTPException(status_code=400, detail="invalid credentials")

    auth_token = AuthToken()
    access_token = auth_token.create_access_token(user_id=user.user_id)
    refresh_token = auth_token.create_refresh_token(user_id=user.user_id)
    response = LoginModel(access_token=access_token, refresh_token=refresh_token)
    return JSONResponse(status_code=status.HTTP_200_OK, content=response.model_dump())


@auth_router.post("/refresh-token")
async def refresh(
    refresh_token: Annotated[str, Depends(security)],
):
    decoded_old_refresh_token = AuthToken().verify_token(refresh_token)

    AuthToken().verify_token_type(refresh_token, token_type="refresh")

    auth_token = AuthToken()

    new_access_token = auth_token.create_access_token(user_id=decoded_old_refresh_token["user_id"])
    new_refresh_token = auth_token.create_refresh_token(user_id=decoded_old_refresh_token["user_id"])

    response = LoginModel(access_token=new_access_token, refresh_token=new_refresh_token)

    return JSONResponse(status_code=status.HTTP_200_OK, content=response.model_dump())
