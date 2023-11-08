from typing import Any, Dict, Optional

from fastapi.exceptions import HTTPException


class TokenTypeException(HTTPException):
    def __init__(
        self, status_code: int = 400, detail: Any = "invalid token type", headers: Optional[Dict[str, str]] = None
    ) -> None:
        self.status_code = status_code
        self.detail = detail
        self.headers = headers

        super().__init__(status_code=status_code, detail=detail, headers=headers)


class TokenSignatureException(HTTPException):
    def __init__(
        self, status_code: int = 400, detail: Any = "invalid token signature", headers: Optional[Dict[str, str]] = None
    ) -> None:
        self.status_code = status_code
        self.detail = detail
        self.headers = headers

        super().__init__(status_code=status_code, detail=detail, headers=headers)


class TokenDecodeException(HTTPException):
    def __init__(
        self, status_code: int = 400, detail: Any = "invalid token", headers: Optional[Dict[str, str]] = None
    ) -> None:
        self.status_code = status_code
        self.detail = detail
        self.headers = headers

        super().__init__(status_code=status_code, detail=detail, headers=headers)
