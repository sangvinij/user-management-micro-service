import datetime
import uuid
from typing import Dict

import jwt
import pytz

from user_management.api.auth.exceptions import TokenError
from user_management.database.redis_settings import create_redis_pool

from ...config import config


class AuthToken:
    @staticmethod
    def get_access_token_expiration_time() -> datetime:
        return datetime.datetime.now(tz=pytz.timezone("Europe/Minsk")) + datetime.timedelta(
            minutes=config.ACCESS_TOKEN_TTL_MINUTES
        )

    @staticmethod
    def get_refresh_token_expiration_time() -> datetime:
        return datetime.datetime.now(tz=pytz.timezone("Europe/Minsk")) + datetime.timedelta(
            days=config.REFRESH_TOKEN_TTL_DAYS
        )

    @staticmethod
    def _create_token(jwt_type: str, expiration_time: datetime, user_id: str) -> str:
        if jwt_type not in ("access", "refresh"):
            raise TypeError("wrong type of token")

        headers = {"token_type": jwt_type}
        payload = {"exp": expiration_time, "user_id": user_id}

        jwt_token = jwt.encode(
            headers=headers,
            payload=payload,
            key=config.SECRET_KEY,
            algorithm=config.TOKEN_HASH_ALGORITHM,
        )

        return jwt_token

    def create_access_token(self, user_id: uuid.UUID):
        return self._create_token(
            jwt_type="access", user_id=str(user_id), expiration_time=self.get_access_token_expiration_time()
        )

    def create_refresh_token(self, user_id: uuid.UUID):
        return self._create_token(
            jwt_type="refresh", user_id=str(user_id), expiration_time=self.get_refresh_token_expiration_time()
        )

    @staticmethod
    def check_token_type(token: str, jwt_type: str) -> None:
        token_headers = jwt.get_unverified_header(token)
        if token_headers["token_type"] != jwt_type:
            raise TokenError("invalid token type")

        return None

    @staticmethod
    async def add_token_to_blacklist(token: str) -> None:
        redis = await create_redis_pool().__anext__()

        await redis.sadd("token_blacklist", token)

        return None

    @staticmethod
    async def check_token_blacklisted(token: str) -> None:
        redis = await create_redis_pool().__anext__()
        tokens = await redis.smembers("token_blacklist")

        if bytes(token, encoding="utf-8") in tokens:
            raise TokenError("token in blacklist")

        return None

    async def verify_token(self, token: str, jwt_type: str) -> Dict:
        try:
            verified_token = jwt.decode(token, key=config.SECRET_KEY, algorithms=[config.TOKEN_HASH_ALGORITHM])

        except jwt.exceptions.InvalidSignatureError:
            raise TokenError("Signature verification failed")

        except jwt.exceptions.ExpiredSignatureError:
            raise TokenError("Signature has expired")

        except jwt.exceptions.DecodeError:
            raise TokenError("invalid token")

        self.check_token_type(token=token, jwt_type=jwt_type)

        if jwt_type == "refresh":
            await self.check_token_blacklisted(token)

        return verified_token

    async def refresh_token(self, refresh_token):
        verified_token = await self.verify_token(refresh_token, jwt_type="refresh")
        new_access_token = self.create_access_token(user_id=verified_token["user_id"])
        new_refresh_token = self.create_refresh_token(user_id=verified_token["user_id"])

        await self.add_token_to_blacklist(refresh_token)

        return {"access_token": new_access_token, "refresh_token": new_refresh_token}


auth_token = AuthToken()
