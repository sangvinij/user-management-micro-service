from passlib.context import CryptContext


class PasswordHasher:
    pwd_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password: str, hashed_password: str):
        return self.pwd_context.verify(plain_password, hashed_password)

    def hash_password(self, password: str):
        return self.pwd_context.hash(password)
