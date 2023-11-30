import hashlib

from passlib.context import CryptContext


class PasswordHasher:
    pwd_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password: str, hashed_password: str):
        return self.pwd_context.verify(plain_password, hashed_password)

    def hash_password(self, password: str):
        return self.pwd_context.hash(password)


class ResetPasswordTokenHasher:
    def __init__(self, algorithm: str = "sha256"):
        self.algorithm = algorithm

    def hash_token(self, token: str) -> str:
        hasher = hashlib.new(self.algorithm)
        hasher.update(token.encode("utf-8"))
        hashed_token: str = hasher.hexdigest()
        return hashed_token

    def verify_token(self, verifiable_token: str, compared_token: str) -> bool:
        hashed_verifiable_token: str = self.hash_token(verifiable_token)
        return hashed_verifiable_token == compared_token
