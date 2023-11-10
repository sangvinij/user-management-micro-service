import datetime
import uuid

import jwt
import pytest

from user_management.api.auth.exceptions import TokenError
from user_management.api.auth.tokens import auth_token
from user_management.config import config


class TestToken:
    jwt_type = "access"
    user_id = uuid.uuid4()

    def test_token_create(self):
        token = auth_token._create_token(jwt_type=self.jwt_type, user_id=self.user_id)

        decoded_token = jwt.decode(jwt=token, key=config.SECRET_KEY, algorithms=[config.TOKEN_HASH_ALGORITHM])

        headers = jwt.get_unverified_header(token)

        assert decoded_token["user_id"] == str(self.user_id)
        assert headers["jwt_type"] == self.jwt_type

    def test_token_create_with_wrong_type(self):
        with pytest.raises(TypeError, match="wrong type of token"):
            auth_token._create_token(jwt_type="wrong", user_id=self.user_id)

            assert False, "token's been created with a wrong type"

    def test_token_expiration_time(self):
        token = auth_token._create_token(
            jwt_type=self.jwt_type, user_id=self.user_id, expiration_time=datetime.datetime.utcnow()
        )

        with pytest.raises(jwt.exceptions.ExpiredSignatureError, match="Signature has expired"):
            jwt.decode(jwt=token, key=config.SECRET_KEY, algorithms=[config.TOKEN_HASH_ALGORITHM])

            assert False, "token is valid despite of expiration time"

    def test_create_token_pair(self):
        token_pair = auth_token.create_token_pair(user_id=self.user_id)

        assert "access_token" in token_pair
        assert "refresh_token" in token_pair

    @pytest.mark.asyncio
    async def test_add_token_to_blacklist(self, fake_redis_client):
        token = auth_token._create_token(
            jwt_type=self.jwt_type,
            user_id=self.user_id,
        )

        await auth_token.add_token_to_blacklist(token, redis_client=fake_redis_client)
        token_blacklist = await fake_redis_client.smembers("token_blacklist")

        assert bytes(token, encoding="utf-8") in token_blacklist

    @pytest.mark.asyncio
    async def test_check_token_blacklisted(self, fake_redis_client):
        token = auth_token._create_token(
            jwt_type=self.jwt_type,
            user_id=self.user_id,
        )

        await fake_redis_client.sadd("token_blacklist", token)

        with pytest.raises(TokenError, match="token in blacklist"):
            await auth_token.check_token_blacklisted(token=token, redis_client=fake_redis_client)
            assert False, "token was not added to blacklist"

    @pytest.mark.asyncio
    async def test_verify_token(self):
        token = auth_token._create_token(
            jwt_type=self.jwt_type,
            user_id=self.user_id,
        )

        verified_token = await auth_token.verify_token(token, jwt_type=self.jwt_type)

        headers = jwt.get_unverified_header(token)

        assert verified_token["user_id"] == str(self.user_id)
        assert headers["jwt_type"] == self.jwt_type

    @pytest.mark.asyncio
    async def test_verify_token_with_wrong_type(self):
        token = auth_token._create_token(
            jwt_type=self.jwt_type,
            user_id=self.user_id,
        )

        with pytest.raises(TokenError, match="invalid token type"):
            await auth_token.verify_token(token, jwt_type="refresh")
            assert False, "token with wrong type passed verification"

    @pytest.mark.asyncio
    async def test_verify_invalid_token(self):
        token = auth_token._create_token(
            jwt_type=self.jwt_type,
            user_id=self.user_id,
        )

        with pytest.raises(TokenError, match="invalid token"):
            await auth_token.verify_token(token[::-1], jwt_type=self.jwt_type)
            assert False, "invalid token passed verification"

    @pytest.mark.asyncio
    async def test_verify_token_with_invalid_signature(self):
        headers = {"jwt_type": self.jwt_type}
        payload = {"sample": "payload"}

        token = jwt.encode(headers=headers, key="fake_key", payload=payload, algorithm=config.TOKEN_HASH_ALGORITHM)

        with pytest.raises(TokenError):
            await auth_token.verify_token(token, jwt_type=self.jwt_type)
            assert False, "token with invalid signature passed verification"
