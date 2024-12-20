"""The module contains the schemas for the course model."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from .module_schemas import ModuleBase, ModuleResponse, UpdateModuleBase
from .subject_schemas import SubjectBase, SubjectResponse, UpdateSubjectBase


class CourseBase(BaseModel):
    """CourseBase schema class."""

    module: ModuleBase
    owner: str
    subject: SubjectBase
    title: str = Field(..., max_length=200)
    slug: str = Field(..., max_length=200)
    overview: str
    created: datetime = Field(default_factory=datetime.utcnow)


class CourseResponse(CourseBase):
    """CourseResponse schema class."""

    id: UUID
    module: ModuleResponse
    subject: SubjectResponse

    class Config:
        """Config schema class."""

        orm_mode = True


class UpdateCourseBase(CourseBase):
    """UpdateCourseBase schema class."""

    module: Optional[UpdateModuleBase] = None
    owner: Optional[str] = None
    subject: Optional[UpdateSubjectBase] = None
    title: Optional[str] = None
    slug: Optional[str] = None
    overview: Optional[str] = None
    created: Optional[datetime] = None

    class Config:
        """Config schema class."""

        orm_mode = True
