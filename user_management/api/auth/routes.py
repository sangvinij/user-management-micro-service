from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from user_management.api.auth.services import AuthService
from user_management.api.auth.tokens import AuthToken

from ...database.models import User
from ..dependencies import security
from .exceptions import TokenError
from .schemas import LoginModel, SignupModel, SignupResponseModel

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: Annotated[AuthService, Depends(AuthService)],
    auth_token: Annotated[AuthToken, Depends(AuthToken)],
):
    user = await service.authenticate(username=form_data.username, password=form_data.password)

    access_token, refresh_token = auth_token.create_token_pair(user_id=user.user_id)
    response = LoginModel(access_token=access_token, refresh_token=refresh_token)

    return JSONResponse(status_code=status.HTTP_200_OK, content=response.model_dump())


@auth_router.post("/refresh-token")
async def refresh(
    refresh_token: Annotated[str, Depends(security)], auth_token: Annotated[AuthToken, Depends(AuthToken)]
):
    try:
        new_access_token, new_refresh_token = await auth_token.refresh_token(refresh_token)
    except TokenError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    response = LoginModel(access_token=new_access_token, refresh_token=new_refresh_token)

    return JSONResponse(status_code=status.HTTP_200_OK, content=response.model_dump())


@auth_router.post("/signup", response_model=SignupResponseModel)
async def create_user(
    data: Annotated[SignupModel, Body()],
    service: Annotated[AuthService, Depends(AuthService)],
):
    created_user: User = await service.signup(data)

    return created_user
