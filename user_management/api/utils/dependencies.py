from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordBearer

from user_management.api.auth.tokens import AuthToken
from user_management.api.utils.exceptions import PermissionHTTPException, TokenError
from user_management.database.models import User
from user_management.managers.user_manager import UserManager

security = OAuth2PasswordBearer(tokenUrl="auth/login")


async def authenticated_user(
    access_token: Annotated[str, Depends(security)],
    user_manager: Annotated[UserManager, Depends(UserManager)],
    token_service: Annotated[AuthToken, Depends(AuthToken)],
) -> User:
    try:
        verified_token = await token_service.verify_token(token=access_token, jwt_type="access")
    except TokenError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    user_id = verified_token["user_id"]

    user: User = await user_manager.get_by_id(user_id=user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user does not exists")

    if user.is_blocked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="user is blocked")

    return user


async def admin_user(
    access_token: Annotated[str, Depends(security)],
    user_manager: Annotated[UserManager, Depends(UserManager)],
    token_service: Annotated[AuthToken, Depends(AuthToken)],
):
    user: User = await authenticated_user(
        access_token=access_token, user_manager=user_manager, token_service=token_service
    )

    if user.role.role_name != "ADMIN":
        raise PermissionHTTPException()

    return user


async def admin_or_moderator(
    access_token: Annotated[str, Depends(security)],
    user_manager: Annotated[UserManager, Depends(UserManager)],
    token_service: Annotated[AuthToken, Depends(AuthToken)],
) -> User:
    user: User = await authenticated_user(
        access_token=access_token, user_manager=user_manager, token_service=token_service
    )

    if user.role.role_name not in ("ADMIN", "MODERATOR"):
        raise PermissionHTTPException()

    return user
