from typing import List, Union
from sqlalchemy.orm import Session
from sqlalchemy import select

from models import SubjectModel
from schemas import SubjectBase, UpdateSubjectBase


async def db_create_subject(db: Session, sub: SubjectBase):
    subject_item = SubjectModel(**sub.model_dump())
    db.add(subject_item)
    db.commit()
    db.refresh(subject_item)

    return subject_item


def db_read_all_subjects(db: Session, limit: int) -> List[SubjectModel]:
    subjects = db.scalars(select(SubjectModel)).fetchmany(size=limit)

    return subjects


def db_read_subject_by_id(db: Session, subject_id: str) -> Union[SubjectModel, None]:
    subject = db.scalar(select(SubjectModel).where(SubjectModel.id == subject_id))

    return subject


async def db_update_subject(
    db: Session, subject_id: str, content: UpdateSubjectBase
) -> Union[SubjectModel, None]:
    subject = db.scalar(select(SubjectModel).where(SubjectModel.id == subject_id))

    if subject is None:
        return

    for key, val in vars(content).items():
        setattr(subject, key, val) if val else None
    db.add(subject)
    db.commit()

    return subject


# DELETE QUERIES


async def delete_subject_by_id(
    db: Session, subject_id: str
) -> Union[None, SubjectModel]:
    subject: SubjectModel = (
        db.query(SubjectModel).filter(SubjectModel.id == subject_id).one_or_none()
    )

    if subject is None:
        return None

    db.delete(subject)
    db.commit()

    return subject
