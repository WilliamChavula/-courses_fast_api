"""This module initializes the schemas package."""

from .course_schemas import CourseBase, CourseResponse, UpdateCourseBase
from .module_schemas import ModuleResponse, UpdateModuleBase
from .subject_schemas import SubjectResponse, UpdateSubjectBase

__all__ = [
    "CourseBase",
    "UpdateCourseBase",
    "CourseResponse",
    "ModuleResponse",
    "UpdateModuleBase",
    "SubjectResponse",
    "UpdateSubjectBase",
]
