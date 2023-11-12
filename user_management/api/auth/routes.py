from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security.oauth2 import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from user_management.api.auth.services import AuthService
from user_management.api.auth.tokens import AuthToken

from .exceptions import TokenError
from .schemas import LoginModel

security = OAuth2PasswordBearer(tokenUrl="auth/login")
auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: Annotated[AuthService, Depends(AuthService)],
    auth_token: Annotated[AuthToken, Depends(AuthToken)],
):
    user = await service.authenticate(username=form_data.username, password=form_data.password)

    token_pair = auth_token.create_token_pair(user_id=user.user_id)
    response = LoginModel(access_token=token_pair["access_token"], refresh_token=token_pair["refresh_token"])

    return JSONResponse(status_code=status.HTTP_200_OK, content=response.model_dump())


@auth_router.post("/refresh-token")
async def refresh(
    refresh_token: Annotated[str, Depends(security)], auth_token: Annotated[AuthToken, Depends(AuthToken)]
):
    try:
        tokens = await auth_token.refresh_token(refresh_token)
    except TokenError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    response = LoginModel(access_token=tokens["access_token"], refresh_token=tokens["refresh_token"])

    return JSONResponse(status_code=status.HTTP_200_OK, content=response.model_dump())
