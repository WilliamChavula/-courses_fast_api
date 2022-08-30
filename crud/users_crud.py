import asyncio
from typing import Union, List
from sqlalchemy import select
from sqlalchemy.orm import Session

from auth.hashing import get_password_hash
from models.user_models import UserModel
from schemas.user_schemas import UserCreate

# CREATE QUERIES #


async def _create_user_helper(user: UserCreate) -> UserModel:
    return UserModel(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password=get_password_hash(user.password),
        job_title=user.job_title,
        is_super_user=user.is_super_user,
    )


async def db_create_user(db: Session, user: UserCreate) -> UserModel:
    user_ = await _create_user_helper(user)
    db.add(user_)
    db.commit()

    return user_


async def db_insert_many(db: Session, users: List[UserCreate]) -> List[UserModel]:
    users_coro = [_create_user_helper(user) for user in users]

    users_ = await asyncio.gather(*users_coro, return_exceptions=True)

    db.add_all(users_)
    db.commit()
    return list(users_)


async def user_registration(request: UserCreate, database) -> UserModel:
    new_user = await _create_user_helper(user=request)

    database.add(new_user)
    database.commit()
    database.refresh(new_user)

    return new_user


# READ QUERIES #


def get_all_users(db: Session, limit: int) -> List[UserModel]:
    return db.scalars(select(UserModel)).fetchmany(size=limit)


def get_user_by_id(db: Session, user_id: str) -> Union[None, UserModel]:
    user: UserModel = db.scalars(
        select(UserModel).where(UserModel.id == user_id)
    ).one_or_none()

    return user


def get_user_by_email(db: Session, email_address: str) -> Union[UserModel, None]:
    user: Union[UserModel, None] = db.scalars(
        select(UserModel).where(UserModel.email == email_address)
    ).one_or_none()

    if user is None:
        return

    return user
