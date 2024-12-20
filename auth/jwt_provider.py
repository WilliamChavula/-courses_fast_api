from typing import Any, Dict, Protocol


class JWTProtocol(Protocol):
    def encode(self, payload: Dict[str, Any]) -> str: ...

    def decode(self, token: str) -> Dict[str, Any]: ...
