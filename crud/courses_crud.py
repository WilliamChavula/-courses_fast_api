from typing import List, Union

from sqlalchemy.orm import Session

from models import CourseModel, ModuleModel, SubjectModel
from schemas import CourseBase, UpdateCourseBase


def get_all_courses(db: Session, limit: int) -> List[CourseModel]:
    # noinspection PyTypeChecker
    return (
        db.query(CourseModel)
        .join(SubjectModel, CourseModel.subject_id == SubjectModel.id)
        .join(ModuleModel, CourseModel.module_id == ModuleModel.id)
        .limit(limit=limit)
        .all()
    )


def get_course_by_id(db: Session, course_id: str) -> Union[None, CourseModel]:
    course: Union[CourseModel, None] = (
        db.query(CourseModel)
        .join(CourseModel.module)
        .join(CourseModel.subject)
        .filter(CourseModel.id == course_id)
        .first()
    )

    if course is None:
        return

    return course


async def db_create_course(db: Session, course: CourseBase) -> CourseModel:
    module = ModuleModel(
        title=course.module.title, description=course.module.description
    )
    db.add(module)
    db.commit()
    db.refresh(module)

    subject = SubjectModel(title=course.subject.title, slug=course.subject.slug)
    db.add(subject)
    db.commit()
    db.refresh(subject)

    # noinspection PyArgumentList
    course_item = CourseModel(
        module=module,
        subject=subject,
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
    # noinspection PyArgumentList
    courses_ = [
        CourseModel(
            module=ModuleModel(**course.module.model_dump()),
            subject=SubjectModel(**course.subject.model_dump()),
            owner=course.owner,
            title=course.title,
            slug=course.slug,
            overview=course.overview,
            created=course.created,
        )
        for course in courses
    ]

    db.add_all(courses_)
    db.commit()
    return courses_


def update_course_by_id(
    db: Session,
    course_id: str,
    body: UpdateCourseBase,
) -> Union[CourseModel, None]:
    course: Union[CourseModel, None] = (
        db.query(CourseModel).filter(CourseModel.id == course_id).one_or_none()
    )

    if course is None:
        return None

    update_data = body.model_dump(exclude_unset=True)

    db.query(CourseModel).filter(CourseModel.id == course_id).update(update_data)

    db.commit()
    db.refresh(course)

    return course


def delete_course_by_id(db: Session, course_id: str) -> Union[None, CourseModel]:
    course: Union[CourseModel, None] = (
        db.query(CourseModel).filter(CourseModel.id == course_id).one_or_none()
    )

    if course is None:
        return None

    db.delete(course)
    db.commit()

    return course
