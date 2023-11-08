import datetime
import uuid

import jwt
import pytz

from user_management.api.auth.exceptions import TokenDecodeException, TokenSignatureException, TokenTypeException
from user_management.config import config


class AuthToken:
    @staticmethod
    def get_access_token_expiration_time() -> datetime:
        return datetime.datetime.now(tz=pytz.timezone("Europe/Minsk")) + datetime.timedelta(seconds=30)

    @staticmethod
    def get_refresh_token_expiration_time() -> datetime:
        return datetime.datetime.now(tz=pytz.timezone("Europe/Minsk")) + datetime.timedelta(
            days=config.REFRESH_TOKEN_TTL_DAYS
        )

    @staticmethod
    def _create_token(token_type: str, expiration_time: datetime, user_id: str) -> str:
        if token_type not in ("access", "refresh"):
            raise TypeError("wrong type of token")

        headers = {"token_type": token_type}
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
            token_type="access", user_id=str(user_id), expiration_time=self.get_access_token_expiration_time()
        )

    def create_refresh_token(self, user_id: uuid.UUID):
        return self._create_token(
            token_type="refresh", user_id=str(user_id), expiration_time=self.get_refresh_token_expiration_time()
        )

    @staticmethod
    def verify_token(token):
        # if token in token_blacklist:
        #     raise TokenDecodeException(detail="token in blacklist")
        try:
            verified_token = jwt.decode(token, key=config.SECRET_KEY, algorithms=[config.TOKEN_HASH_ALGORITHM])

        except jwt.exceptions.InvalidSignatureError:
            raise TokenSignatureException(detail="Signature verification failed")

        except jwt.exceptions.ExpiredSignatureError:
            raise TokenSignatureException(detail="signature has expired")

        except jwt.exceptions.DecodeError:
            raise TokenDecodeException()

        return verified_token

    def verify_token_type(self, token: str, token_type: str) -> None:
        self.verify_token(token)
        token_headers = jwt.get_unverified_header(token)
        if token_headers["token_type"] != token_type:
            raise TokenTypeException()

        return None
