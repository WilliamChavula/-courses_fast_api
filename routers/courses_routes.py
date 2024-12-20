from typing import Annotated, List, Union

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from crud.courses_crud import (
    db_create_course,
    db_insert_many,
    delete_course_by_id,
    get_all_courses,
    get_course_by_id,
    update_course_by_id,
)
from models.course_models import CourseModel
from schemas import (
    CourseBase,
    CourseResponse,
    UpdateCourseBase,
)
from utils import Tags, get_db, verify_super_user

courses_router = APIRouter(prefix="/courses", tags=[Tags.courses])


@courses_router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=List[CourseResponse],
)
def get_courses(
    db: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(10, gt=0, le=100, description="Number of records to fetch")],
):
    courses = get_all_courses(db, limit)

    return courses


@courses_router.get(
    "/{course_id}",
    status_code=status.HTTP_200_OK,
    response_model=CourseResponse,
)
def get_course(course_id: str, db: Annotated[Session, Depends(get_db)]):
    course: Union[None, CourseModel] = get_course_by_id(db=db, course_id=course_id)

    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not find course with ID: {course_id}",
        )

    return course


@courses_router.post(
    path="",
    status_code=status.HTTP_201_CREATED,
    response_model=CourseResponse,
    dependencies=[Depends(verify_super_user)],
)
async def create_course(course: CourseBase, db: Annotated[Session, Depends(get_db)]):
    return await db_create_course(db, course)


@courses_router.post(
    "/course_many",
    status_code=status.HTTP_201_CREATED,
    response_model=List[CourseResponse],
    dependencies=[Depends(verify_super_user)],
)
async def create_courses(
    courses: List[CourseBase], db: Annotated[Session, Depends(get_db)]
):
    return await db_insert_many(db, courses)


@courses_router.put(
    "/{course_id}",
    response_model=CourseResponse,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(verify_super_user)],
)
def update_course(
    course_id: str, course: UpdateCourseBase, db: Annotated[Session, Depends(get_db)]
):
    updated: Union[None, CourseModel] = update_course_by_id(
        db=db, course_id=course_id, body=course
    )

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not find course with ID: {course_id}",
        )

    return updated


@courses_router.delete(
    "/{course_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(verify_super_user)],
)
def delete_course(course_id: str, db: Annotated[Session, Depends(get_db)]):
    deleted_course = delete_course_by_id(db, course_id)

    if deleted_course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not find course with ID: {course_id}",
        )
