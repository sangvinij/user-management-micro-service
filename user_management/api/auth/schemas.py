from pydantic import BaseModel


class LoginModel(BaseModel):
    access_token: str
    refresh_token: str
