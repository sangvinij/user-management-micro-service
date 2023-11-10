import datetime
import uuid
from typing import Dict, Optional, Union

import jwt
import pytz
import redis.exceptions
from fakeredis.aioredis import FakeRedis
from redis.asyncio import Redis

from user_management.api.auth.exceptions import TokenError
from user_management.database.redis_settings import create_redis_pool

from ...config import config


class AuthToken:
    @staticmethod
    def get_access_token_expiration_time() -> datetime:
        return datetime.datetime.now(tz=config.get_timezone()) + datetime.timedelta(
            minutes=config.ACCESS_TOKEN_TTL_MINUTES
        )

    @staticmethod
    def get_refresh_token_expiration_time() -> datetime:
        return datetime.datetime.now(tz=config.get_timezone()) + datetime.timedelta(days=config.REFRESH_TOKEN_TTL_DAYS)

    @staticmethod
    def _create_token(jwt_type: str, user_id: uuid.UUID, expiration_time: datetime = None) -> str:
        if jwt_type not in ("access", "refresh"):
            raise TypeError("wrong type of token")

        headers = {"jwt_type": jwt_type}
        payload = {"user_id": str(user_id)}
        if expiration_time is not None:
            payload.update({"exp": expiration_time})

        jwt_token = jwt.encode(
            headers=headers,
            payload=payload,
            key=config.SECRET_KEY,
            algorithm=config.TOKEN_HASH_ALGORITHM,
        )

        return jwt_token

    def create_token_pair(self, user_id: uuid.UUID) -> Dict:
        access_token = self._create_token(
            jwt_type="access", user_id=user_id, expiration_time=self.get_access_token_expiration_time()
        )
        refresh_token = self._create_token(
            jwt_type="refresh", user_id=user_id, expiration_time=self.get_refresh_token_expiration_time()
        )

        return {"access_token": access_token, "refresh_token": refresh_token}

    @staticmethod
    def check_token_type(token: str, jwt_type: str) -> None:
        token_headers = jwt.get_unverified_header(token)
        if token_headers["jwt_type"] != jwt_type:
            raise TokenError("invalid token type")

        return None

    @staticmethod
    async def add_token_to_blacklist(token: str, redis_client=None) -> None:
        if redis_client is None:
            redis_client = await create_redis_pool().__anext__()
        try:
            await redis_client.sadd("token_blacklist", token)

        except redis.exceptions.ConnectionError:
            return None

        return None

    @staticmethod
    async def check_token_blacklisted(token: str, redis_client: Optional[Union[Redis, FakeRedis]] = None) -> None:
        if redis_client is None:
            redis_client = await create_redis_pool().__anext__()

        try:
            tokens = await redis_client.smembers("token_blacklist")
            if bytes(token, encoding="utf-8") in tokens:
                raise TokenError("token in blacklist")

        except redis.exceptions.ConnectionError:
            return None

        return None

    async def verify_token(self, token: str, jwt_type: str) -> Dict:
        try:
            verified_token = jwt.decode(token, key=config.SECRET_KEY, algorithms=[config.TOKEN_HASH_ALGORITHM])

        except jwt.exceptions.InvalidSignatureError:
            raise TokenError("signature verification failed")

        except jwt.exceptions.ExpiredSignatureError:
            raise TokenError("signature has expired")

        except jwt.exceptions.DecodeError:
            raise TokenError("invalid token")

        self.check_token_type(token=token, jwt_type=jwt_type)

        if jwt_type == "refresh":
            await self.check_token_blacklisted(token)

        return verified_token

    async def refresh_token(self, refresh_token: str) -> Dict:
        verified_token = await self.verify_token(refresh_token, jwt_type="refresh")
        new_token_pair = self.create_token_pair(user_id=verified_token["user_id"])

        await self.add_token_to_blacklist(refresh_token)

        return new_token_pair


auth_token = AuthToken()
