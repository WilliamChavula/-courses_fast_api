from pydantic import BaseModel, Field

from typing import Optional


class Token(BaseModel):
    access_token: str
    token_type: str = Field("Bearer")


class TokenData(BaseModel):
    email: Optional[str] = None
