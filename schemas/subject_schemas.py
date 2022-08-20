from uuid import UUID
from typing import Optional

from pydantic import BaseModel, Field


class SubjectBase(BaseModel):
    title: str = Field(..., max_length=200)
    slug: str = Field(..., max_length=200)


class SubjectResponse(SubjectBase):
    id: UUID

    class Config:
        orm_mode = True


class UpdateSubjectBase(SubjectBase):
    title: Optional[str] = Field(None, max_length=200)
    slug: Optional[str] = Field(None, max_length=200)

    class Config:
        orm_mode = True
