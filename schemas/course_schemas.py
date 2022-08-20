from uuid import UUID
from datetime import datetime

from typing import Optional

from pydantic import BaseModel, Field

from .module_schemas import ModuleBase, UpdateModuleBase, ModuleResponse
from .subject_schemas import SubjectBase, UpdateSubjectBase, SubjectResponse


class CourseBase(BaseModel):
    module: ModuleBase
    owner: str
    subject: SubjectBase
    title: str = Field(..., max_length=200)
    slug: str = Field(..., max_length=200)
    overview: str
    created: datetime = Field(default_factory=datetime.utcnow)


class CourseResponse(CourseBase):
    id: UUID
    module: ModuleResponse
    subject: SubjectResponse

    class Config:
        orm_mode = True


class UpdateCourseBase(CourseBase):
    module: Optional[UpdateModuleBase] = None
    owner: Optional[str] = None
    subject: Optional[UpdateSubjectBase] = None
    title: Optional[str] = None
    slug: Optional[str] = None
    overview: Optional[str] = None
    created: Optional[datetime] = None

    class Config:
        orm_mode = True
