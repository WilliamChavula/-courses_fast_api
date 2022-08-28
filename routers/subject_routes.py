from typing import List, Union

from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.orm import Session
from models.subject_models import SubjectModel

from schemas import SubjectResponse, UpdateSubjectBase

from crud.subjects_crud import (
    db_read_all_subjects,
    db_read_subject_by_id,
    db_update_subject,
    db_create_subject,
    delete_subject_by_id,
)
from schemas.subject_schemas import SubjectBase
from utils import Tags, get_db, verify_super_user

subject_router = APIRouter(prefix="/subjects", tags=[Tags.subjects])


@subject_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=List[SubjectResponse],
    tags=[Tags.subjects],
)
def get_subjects(db: Session = Depends(get_db), limit: int = Query(10, gt=0, le=100)):
    return db_read_all_subjects(db, limit)


@subject_router.get(
    "/{subject_id}",
    status_code=status.HTTP_200_OK,
    response_model=SubjectResponse,
    tags=[Tags.subjects],
)
def get_subject(subject_id: str, db: Session = Depends(get_db)):
    subject: Union[SubjectModel, None] = db_read_subject_by_id(db, subject_id)

    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not find subject with ID: {subject_id}",
        )
    return subject


@subject_router.post(
    "/subject",
    status_code=status.HTTP_201_CREATED,
    response_model=SubjectResponse,
    dependencies=[Depends(verify_super_user)],
)
async def create_subject(subject: SubjectBase, db: Session = Depends(get_db)):

    return await db_create_subject(db, subject)


@subject_router.put(
    "/{subject_id}",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=SubjectResponse,
    dependencies=[Depends(verify_super_user)],
    tags=[Tags.subjects],
)
async def update_subject(
    *, db: Session = Depends(get_db), subject_id: str, content: UpdateSubjectBase
):

    subject: Union[SubjectModel, None] = await db_update_subject(
        db, subject_id, content
    )

    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not find subject with ID: {subject_id}",
        )

    return subject


@subject_router.delete(
    "/{subject_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(verify_super_user)],
)
async def delete_module(subject_id: str, db: Session = Depends(get_db)):

    subject = db_read_subject_by_id(db, subject_id)

    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not find subject with ID: {subject_id}",
        )

    await delete_subject_by_id(db, subject_id)
