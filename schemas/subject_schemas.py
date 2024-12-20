"""Subject schemas."""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SubjectBase(BaseModel):
    """Subject base schema."""

    title: str = Field(..., max_length=200)
    slug: str = Field(..., max_length=200)


class SubjectResponse(SubjectBase):
    """Subject response schema."""

    id: UUID

    class Config:
        """Pydantic configuration."""

        orm_mode = True


class UpdateSubjectBase(SubjectBase):
    """Update subject base schema."""

    title: Optional[str] = Field(None, max_length=200)
    slug: Optional[str] = Field(None, max_length=200)

    class Config:
        """Pydantic configuration."""

        orm_mode = True
