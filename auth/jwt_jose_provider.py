from typing import Dict, Any
from jose import jwt, JWTError

from auth.jwt_provider import JWTProvider
from core.exceptions import InvalidCredentialsException


class JoseJWTProvider(JWTProvider):
    def __init__(self, algorithm: str, secret_key: str) -> None:
        self.algorithm = algorithm
        self.secret_key = secret_key

    def encode(self, payload: Dict[str, Any]) -> str:
        return jwt.encode(
            payload, self.secret_key, algorithm=self.algorithm)

    def decode(self, token: str) -> Dict[str, Any]:
        try:
            return jwt.decode(token, self.secret_key,
                              algorithms=[self.algorithm])

        except JWTError:
            raise InvalidCredentialsException()
