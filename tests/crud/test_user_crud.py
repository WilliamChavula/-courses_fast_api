import datetime
from typing import List

import pytest

from crud.users_crud import (
    db_create_user,
    db_insert_many,
    get_all_users,
    get_user_by_id,
    get_user_by_email,
)
from models.user_models import UserModel
from schemas.user_schemas import UserCreate
from tests.conf_test_db import override_get_db


@pytest.fixture
def user_create_pydantic_fixture(faker, faker_seed):
    return UserCreate(
        first_name=faker.first_name(),
        last_name=faker.last_name(),
        email=faker.email(),
        job_title=faker.job(),
        id=faker.uuid4(),
        password=faker.password(),
        is_super_user=faker.boolean(),
    )


@pytest.mark.usefixtures("anyio_backend")
async def test_db_create_user(user_create_pydantic_fixture):
    new_user: UserCreate = user_create_pydantic_fixture
    db = next(override_get_db())

    user_model = await db_create_user(db, new_user)

    assert isinstance(user_model, UserModel)
    assert user_model.created_at is not None
    assert isinstance(user_model.created_at, datetime.datetime)


@pytest.mark.usefixtures("anyio_backend")
async def test_db_insert_many(faker):
    new_users: List[UserCreate] = [
        UserCreate(
            first_name=faker.first_name(),
            last_name=faker.last_name(),
            email=faker.email(),
            job_title=faker.job(),
            id=faker.uuid4(),
            password=faker.password(),
            is_super_user=faker.boolean(),
        )
        for _ in range(5)
    ]
    db = next(override_get_db())

    user_models = await db_insert_many(db, new_users)

    assert len(user_models) == len(new_users)


@pytest.mark.usefixtures("anyio_backend")
async def test_get_user_by_email(user_create_pydantic_fixture):
    user_ = user_create_pydantic_fixture
    db = next(override_get_db())
    await db_create_user(db, user_)

    user = get_user_by_email(db, user_.email)

    assert user is not None
    assert isinstance(user, UserModel)


def test_get_all_users():
    db = next(override_get_db())

    users = get_all_users(db, 3)

    assert isinstance(users, List)
    assert isinstance(users[0], UserModel)
    assert len(users) == 3


def test_get_user_by_id():
    db = next(override_get_db())
    user_ = get_all_users(db, 1)[0]

    user = get_user_by_id(db, user_.id)

    assert user is not None
    assert user_.id == user.id
