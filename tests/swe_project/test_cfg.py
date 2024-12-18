import json
import pytest

from faker import Faker
from fastapi import status
from httpx import AsyncClient
from pytest_mock import MockerFixture

from auth.authenticate import create_access_token
from tests.conf_test_db import app

fake = Faker()


@pytest.fixture(scope="function")
def seed_user(test_client):
    test_client.post(
        "/user",
        headers={
            "accept": "application/json",
        },
        data=json.dumps({
            "first_name": "Berny",
            "last_name": "Stoop",
            "email": "bstoop2@mashable.com",
            "job_title": "Social Worker",
            "is_super_user": False,
            "password": "rdpK37533T"
        }),
    )


@pytest.mark.usefixtures("anyio_backend")
class TestCFGTesting:

    async def test_create_user_not_superuser(
            self,
            create_user_instance,
            mocker: MockerFixture
    ):
        user_ = create_user_instance

        mock_get_user_by_email = mocker.patch(
            "utils.dependencies.get_user_by_email", return_value=user_
        )
        token_ = create_access_token(data={"user": user_.email})

        async with AsyncClient(app=app, base_url="http://localhost") as client:
            response = await client.post(
                "/user",
                headers={"Authorization": f"Bearer {token_}"},
                content=json.dumps({
                    "first_name": "Berny",
                    "last_name": "Stoop",
                    "email": "bstoop2@mashable.com",
                    "job_title": "Social Worker",
                    "is_super_user": False,
                    "password": "rdpK37533T"
                }),
            )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        mock_get_user_by_email.assert_called_once()

    async def test_create_duplicate_user_with_superuser(
            self,
            create_super_user_instance,
            mocker: MockerFixture
    ):
        user_ = create_super_user_instance

        mock_get_user_by_email = mocker.patch(
            "utils.dependencies.get_user_by_email", return_value=user_
        )

        token_ = create_access_token(data={"user": user_.email})

        async with AsyncClient(app=app, base_url="http://localhost") as client:
            await client.post(
                "/user",
                headers={"Authorization": f"Bearer {token_}"},
                content=json.dumps({
                    "first_name": "Berny",
                    "last_name": "Stoop",
                    "email": "bstoop2@mashable.com",
                    "job_title": "Social Worker",
                    "is_super_user": False,
                    "password": "rdpK37533T"
                }),
            )

            response = await client.post(
                "/user",
                headers={"Authorization": f"Bearer {token_}"},
                content=json.dumps({
                    "first_name": "Berny",
                    "last_name": "Stoop",
                    "email": "bstoop2@mashable.com",
                    "job_title": "Social Worker",
                    "is_super_user": False,
                    "password": "rdpK37533T"
                }),
            )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "The user with this email already exists in the system."
        mock_get_user_by_email.call_count = 2

    async def test_create_user_with_superuser(
            self,
            create_super_user_instance,
            mocker: MockerFixture
    ):
        user_ = create_super_user_instance

        mock_get_user_by_email = mocker.patch(
            "utils.dependencies.get_user_by_email", return_value=user_
        )

        token_ = create_access_token(data={"user": user_.email})

        async with AsyncClient(app=app, base_url="http://localhost") as client:

            response = await client.post(
                "/user",
                headers={"Authorization": f"Bearer {token_}"},
                content=json.dumps({
                    "first_name": fake.first_name(),
                    "last_name": fake.last_name(),
                    "email": fake.email(),
                    "job_title": fake.job(),
                    "is_super_user": False,
                    "password": fake.password()
                }),
            )

        assert response.status_code == status.HTTP_201_CREATED
        mock_get_user_by_email.assert_called_once()

    async def test_create_user_with_non_existent_superuser(
            self,
            create_super_user_instance,
            mocker: MockerFixture
    ):
        user_ = create_super_user_instance

        mock_get_user_by_email = mocker.patch(
            "utils.dependencies.get_user_by_email", return_value=None
        )

        token_ = create_access_token(data={"user": user_.email})

        async with AsyncClient(app=app, base_url="http://localhost") as client:

            response = await client.post(
                "/user",
                headers={"Authorization": f"Bearer {token_}"},
                content=json.dumps({
                    "first_name": fake.first_name(),
                    "last_name": fake.last_name(),
                    "email": fake.email(),
                    "job_title": fake.job(),
                    "is_super_user": False,
                    "password": fake.password()
                }),
            )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        mock_get_user_by_email.assert_called_once()
