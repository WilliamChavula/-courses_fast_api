from typing import Union, List

from sqlalchemy.orm import Session

from models import CourseModel, ModuleModel, SubjectModel
from schemas import CourseBase, UpdateCourseBase


## READ QUERIES ##


def get_all_courses(db: Session, limit: int) -> List[CourseModel]:
    return (
        db.query(CourseModel)
        .join(SubjectModel, CourseModel.subject_id == SubjectModel.id)
        .join(ModuleModel, CourseModel.module_id == ModuleModel.id)
        .limit(limit=limit).all()
    )


def get_course_by_id(db: Session, course_id: str) -> Union[None, CourseModel]:
    course: CourseModel = (
        db.query(CourseModel)
        .join(CourseModel.module)
        .join(CourseModel.subject)
        .filter(CourseModel.id == course_id)
        .first()
    )

    if course is None:
        return

    return course


## CREATE QUERIES ##


async def db_create_course(db: Session, course: CourseBase) -> CourseModel:
    course_item = CourseModel(
        module=ModuleModel(**course.module.dict()),
        subject=SubjectModel(**course.subject.dict()),
        owner=course.owner,
        title=course.title,
        slug=course.slug,
        overview=course.overview,
        created=course.created,
    )

    db.add(course_item)
    db.commit()
    db.refresh(course_item)
    return course_item


async def db_insert_many(db: Session, courses: List[CourseBase]) -> List[CourseModel]:
    courses_ = [CourseModel(
        module=ModuleModel(**course.module.dict()),
        subject=SubjectModel(**course.subject.dict()),
        owner=course.owner,
        title=course.title,
        slug=course.slug,
        overview=course.overview,
        created=course.created,
    ) for course in courses]

    db.add_all(courses_)
    db.commit()
    return courses_


# UPDATE QUERIES


def update_course_by_id(
    db: Session,
    course_id: str,
    body: UpdateCourseBase,
) -> Union[None, CourseModel]:

    course: CourseModel = (
        db.query(CourseModel).filter(CourseModel.id == course_id).one_or_none()
    )

    if course is None:
        return None

    update_data = body.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(course, key, value)

    db.commit()
    db.refresh(course)

    return course


# DELETE QUERIES

def delete_course_by_id(db: Session, course_id: str) -> Union[None, CourseModel]:
    course: CourseModel = (
        db.query(CourseModel).filter(CourseModel.id == course_id).one_or_none()
    )

    if course is None:
        return None

    db.delete(course)
    db.commit()

    return course
