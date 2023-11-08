from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from ...database.db_settings import get_async_session
from .backends import auth_backend
from .exceptions import TokenError
from .schemas import LoginModel
from .tokens import AuthToken, auth_token

security = OAuth2PasswordBearer(tokenUrl="auth/login")
auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: AsyncSession = Depends(get_async_session)
):
    user = await auth_backend.authenticate(username=form_data.username, password=form_data.password, session=session)

    token_pair = auth_token.create_token_pair(user_id=user.user_id)
    response = LoginModel(access_token=token_pair["access_token"], refresh_token=token_pair["refresh_token"])
    return JSONResponse(status_code=status.HTTP_200_OK, content=response.model_dump())


@auth_router.post("/refresh-token")
async def refresh(refresh_token: Annotated[str, Depends(security)]):
    try:
        tokens = await auth_token.refresh_token(refresh_token)
    except TokenError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    response = LoginModel(access_token=tokens["access_token"], refresh_token=tokens["refresh_token"])

    return JSONResponse(status_code=status.HTTP_200_OK, content=response.model_dump())
