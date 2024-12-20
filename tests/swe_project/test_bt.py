import datetime
import json

import pytest
from faker import Faker
from fastapi import status
from pydantic import ValidationError
from pytest_mock import MockerFixture
from sqlalchemy.exc import DataError

from auth.authenticate import create_access_token
from crud.users_crud import db_create_user
from models.user_models import UserModel
from schemas.user_schemas import UserCreate
from tests.conf_test_db import override_get_db

fake = Faker()


@pytest.fixture
def new_user_fixture(faker, faker_seed):
    return UserCreate(
        first_name=faker.first_name(),
        last_name=faker.last_name(),
        email=faker.email(),
        job_title=faker.job(),
        id=faker.uuid4(),
        password=faker.password(),
        is_super_user=faker.boolean(),
    )


# ---------------------------- UserModel - Database Constraints Boundaries ---------------------------- #
@pytest.mark.usefixtures("anyio_backend")
@pytest.mark.parametrize(
    "first_name, expected_result",
    [
        (None, ValidationError),
        ("A", UserModel),
        (fake.password(length=254, special_chars=False, upper_case=False), UserModel),
        (fake.password(length=255, special_chars=False, upper_case=False), UserModel),
        (fake.password(length=256, special_chars=False, upper_case=False), UserModel),
    ],
)
async def test_db_create_user_with_firstname(
    new_user_fixture, first_name, expected_result
):
    new_user: UserCreate = new_user_fixture
    db = next(override_get_db())

    if not first_name:
        with pytest.raises(ValidationError):
            new_user.first_name = first_name
            await db_create_user(db, new_user)

    elif len(first_name) > 255:
        with pytest.raises(DataError):
            new_user.first_name = first_name
            await db_create_user(db, new_user)
    else:
        new_user.first_name = first_name
        user_model = await db_create_user(db, new_user)
        assert isinstance(user_model, expected_result)
        assert user_model.created_at is not None
        assert isinstance(user_model.created_at, datetime.datetime)


@pytest.mark.usefixtures("anyio_backend")
@pytest.mark.parametrize(
    "last_name, expected_result",
    [
        (None, ValidationError),
        ("A", UserModel),
        (fake.password(length=254, special_chars=False, upper_case=False), UserModel),
        (fake.password(length=255, special_chars=False, upper_case=False), UserModel),
        (fake.password(length=256, special_chars=False, upper_case=False), DataError),
    ],
)
async def test_db_create_user_with_lastname(
    new_user_fixture, last_name, expected_result
):
    new_user: UserCreate = new_user_fixture
    db = next(override_get_db())

    if not last_name:
        with pytest.raises(expected_result):
            new_user.last_name = last_name
            await db_create_user(db, new_user)

    elif len(last_name) > 255:
        with pytest.raises(expected_result):
            new_user.last_name = last_name
            await db_create_user(db, new_user)
    else:
        new_user.last_name = last_name
        user_model = await db_create_user(db, new_user)
        assert isinstance(user_model, expected_result)
        assert user_model.created_at is not None
        assert isinstance(user_model.created_at, datetime.datetime)


@pytest.mark.usefixtures("anyio_backend")
@pytest.mark.parametrize(
    "job_title, expected_result",
    [
        (None, ValidationError),
        ("A", UserModel),
        (fake.password(length=149, special_chars=False, upper_case=False), UserModel),
        (fake.password(length=150, special_chars=False, upper_case=False), UserModel),
        (fake.password(length=151, special_chars=False, upper_case=False), DataError),
    ],
)
async def test_db_create_user_with_job_title(
    new_user_fixture, job_title, expected_result
):
    new_user: UserCreate = new_user_fixture
    db = next(override_get_db())

    if not job_title:
        with pytest.raises(expected_result):
            new_user.job_title = job_title
            await db_create_user(db, new_user)

    elif len(job_title) > 150:
        with pytest.raises(expected_result):
            new_user.job_title = job_title
            await db_create_user(db, new_user)
    else:
        new_user.job_title = job_title
        user_model = await db_create_user(db, new_user)
        assert isinstance(user_model, expected_result)
        assert user_model.created_at is not None
        assert isinstance(user_model.created_at, datetime.datetime)


# ---------------------------- UserCreate - Client/User Supplied Input Constraints ---------------------------- #


@pytest.mark.parametrize(
    "email, expected_result",
    [
        ("a", ValidationError),
        ("a.b.com", ValidationError),
        ("a@v", ValidationError),
        (None, ValidationError),
    ],
)
def test_db_create_user_with_invalid_email(email, expected_result):
    with pytest.raises(expected_result):
        UserCreate(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=email,
            job_title=fake.job(),
            password=fake.password(),
            is_super_user=fake.boolean(),
        )


def test_db_create_user_with_valid_email(new_user_fixture):
    new_user: UserCreate = UserCreate(
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        email=fake.email(),
        job_title=fake.job(),
        password=fake.password(),
        is_super_user=fake.boolean(),
    )

    assert new_user.email is not None


@pytest.mark.parametrize(
    "password, expected_result",
    [
        (None, ValidationError),
        (fake.password(length=5), ValidationError),
        (fake.password(length=6, special_chars=False, upper_case=False), UserCreate),
        (fake.password(length=29, special_chars=False, upper_case=False), UserCreate),
        (fake.password(length=30, special_chars=False, upper_case=False), UserCreate),
        (
            fake.password(length=31, special_chars=False, upper_case=False),
            ValidationError,
        ),
    ],
)
def test_db_create_user_with_password(password, expected_result):
    if not password:
        with pytest.raises(expected_result):
            UserCreate(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.email(),
                job_title=fake.job(),
                password=password,
                is_super_user=fake.boolean(),
            )

    elif len(password) < 6 or len(password) > 30:
        with pytest.raises(expected_result):
            UserCreate(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.email(),
                job_title=fake.job(),
                password=password,
                is_super_user=fake.boolean(),
            )
    else:
        new_user: UserCreate = UserCreate(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            job_title=fake.job(),
            password=fake.password(),
            is_super_user=fake.boolean(),
        )

        assert new_user.password is not None
        assert len(new_user.password) > 6
        assert len(new_user.password) < 31


# ---------------------------- UserCreate - Authentication and Authorization Boundaries ---------------------------- #
def test_db_create_user_with_valid_token(
    create_super_user_instance, test_client, mocker: MockerFixture
):
    mocker.patch(
        "utils.dependencies.get_user_by_email", return_value=create_super_user_instance
    )

    # creates token with 30min validity
    token = create_access_token(data={"user": create_super_user_instance.email})

    response = test_client.post(
        "/modules",
        headers={"accept": "application/json", "Authorization": f"Bearer {token}"},
        data=json.dumps(
            {
                "title": "Tempsoft",
                "description": "Morbi vel lectus in quam fringilla rhoncus",
            }
        ),
    )

    assert response.status_code == status.HTTP_201_CREATED


def test_db_create_user_with_valid_almost_expired_token(
    create_super_user_instance, test_client, mocker: MockerFixture
):
    mocker.patch(
        "utils.dependencies.get_user_by_email", return_value=create_super_user_instance
    )

    # creates token with 1 second validity
    token = create_access_token(
        data={"user": create_super_user_instance.email},
        expires_delta=datetime.timedelta(seconds=1),
    )

    response = test_client.post(
        "/modules",
        headers={"accept": "application/json", "Authorization": f"Bearer {token}"},
        data=json.dumps(
            {
                "title": "Tempsoft",
                "description": "Morbi vel lectus in quam fringilla rhoncus",
            }
        ),
    )

    assert response.status_code == status.HTTP_201_CREATED


def test_db_create_user_with_valid_expired_token(
    create_super_user_instance, test_client, mocker: MockerFixture
):
    mocker.patch(
        "utils.dependencies.get_user_by_email", return_value=create_super_user_instance
    )

    # creates token with -5 minutes validity
    token = create_access_token(
        data={"user": create_super_user_instance.email},
        expires_delta=datetime.timedelta(minutes=-5),
    )

    response = test_client.post(
        "/modules",
        headers={"accept": "application/json", "Authorization": f"Bearer {token}"},
        data=json.dumps(
            {
                "title": "Tempsoft",
                "description": "Morbi vel lectus in quam fringilla rhoncus",
            }
        ),
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_db_create_user_with_invalid_token(
    create_super_user_instance, test_client, mocker: MockerFixture
):
    mocker.patch(
        "utils.dependencies.get_user_by_email", return_value=create_super_user_instance
    )

    response = test_client.post(
        "/modules",
        headers={
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6Ikpva"
            "GFuI.JvY2siLCJpYXQiOjE1MTYyMzkwMjIsImV4cCI6MTY0NzgxNTAyMn0.5i81Wq1yQzqYV27i1f1H1I3d",
        },
        data=json.dumps(
            {
                "title": "Tempsoft",
                "description": "Morbi vel lectus in quam fringilla rhoncus",
            }
        ),
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
