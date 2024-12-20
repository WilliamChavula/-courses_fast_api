"""JWT Jose Provider module."""

from typing import Any, Dict

from jose import JWTError, jwt

from auth.jwt_provider import JWTProtocol
from core.exceptions import InvalidCredentialsError


class JoseJWTProvider(JWTProtocol):
    """JoseJWTProvider class to encode and decode JWT tokens using JOSE library."""

    def __init__(self, algorithm: str, secret_key: str) -> None:
        self.algorithm = algorithm
        self.secret_key = secret_key

    def encode(self, payload: Dict[str, Any]) -> str:
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def decode(self, token: str) -> Dict[str, Any]:
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

        except JWTError as exc:
            raise InvalidCredentialsError() from exc
