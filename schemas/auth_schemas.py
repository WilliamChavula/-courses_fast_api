"""Auth schemas module."""

from typing import Optional

from pydantic import BaseModel, Field


class Token(BaseModel):
    """Token schema."""

    access_token: str
    token_type: str = Field("Bearer")


class TokenData(BaseModel):
    """Token data schema."""

    email: Optional[str] = None
