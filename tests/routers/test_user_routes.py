# cSpell: ignore usefixtures pytestmark

from typing import Dict

import pytest
from httpx import AsyncClient

from tests.conf_test_db import app


def user_payload_generator() -> Dict[str, str]:
    from faker import Faker
    from random import randint

    Faker.seed(randint(100000, 1000000))

    fake = Faker()
    return {
        "id": fake.uuid4(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.email(),
        "job_title": fake.job(),
        "is_super_user": "false",
        "password": fake.password()
    }


@pytest.mark.usefixtures("anyio_backend")
class TestAsyncUserRoutes:
    pytestmark = pytest.mark.anyio

    async def test_register_user(self):

        async with AsyncClient(app=app, base_url="http://localhost/user") as client:
            res = await client.post(
                "/register",
                headers={"Content-type": "application/json; charset=utf-8"},
                json=user_payload_generator()
            )

        assert res.status_code == 201

    async def test_unauthenticated_create_user(self):

        async with AsyncClient(app=app, base_url="http://localhost/user") as client:
            res = await client.post(
                "/",
                headers={"Content-type": "application/json; charset=utf-8"},
                json=user_payload_generator())

        assert res.status_code == 401

    async def test_unauthenticated_create_many_users(self):

        users_payload = [user_payload_generator() for _ in range(3)]

        async with AsyncClient(app=app, base_url="http://localhost/user") as client:
            res = await client.post(
                "/create_many",
                headers={"Content-type": "application/json; charset=utf-8"},
                json=users_payload
            )

        assert res.status_code == 401

    @pytest.mark.usefixtures("authenticated_user")
    async def test_authenticated_create_user(self):

        async with AsyncClient(app=app, base_url="http://localhost/user") as client:
            res = await client.post(
                "/",
                headers={"Content-type": "application/json; charset=utf-8"},
                json=user_payload_generator()
            )

        assert res.status_code == 201

    @pytest.mark.usefixtures("authenticated_user")
    async def test_authenticated_create_many_users(self):

        users_payload = [user_payload_generator() for _ in range(3)]

        async with AsyncClient(app=app, base_url="http://localhost/user") as client:
            res = await client.post(
                "/create_many",
                headers={"Content-type": "application/json; charset=utf-8"},
                json=users_payload
            )

        assert res.status_code == 201


class TestSyncUserRoutes:
    from pytest_mock import MockerFixture

    def test_login_no_user(self, test_client, faker, mocker: MockerFixture):
        payload = {
            "username": faker.email(),
            "password": faker.password()
        }

        mock_get_user_by_email = mocker.patch(
            "routers.users_routes.get_user_by_email", return_value=None, autospec=True)

        res = test_client.post(
            "/user/login",
            headers={"Content-Type": "application/x-www-form-urlencoded",
                     "accept": 'application/json'},
            data=payload
        )

        mock_get_user_by_email.assert_called_once()

        assert res.status_code == 404
        assert res.json()["detail"] == "Invalid Credentials"

    def test_login_user_wrong_password(self, test_client, faker, create_user_instance, mocker: MockerFixture):
        user_ = create_user_instance

        payload = {
            "username": user_.email,
            "password": faker.password()
        }
        mock_get_user_by_email = mocker.patch(
            "routers.users_routes.get_user_by_email", return_value=user_)

        res = test_client.post(
            "/user/login",
            headers={"Content-Type": "application/x-www-form-urlencoded",
                     "accept": 'application/json'},
            data=payload
        )

        mock_get_user_by_email.assert_called_once()

        assert res.status_code == 400
        assert res.json()["detail"] == "Invalid Credentials"

    def test_login_valid_user(self, test_client, create_user_instance, mocker: MockerFixture):
        user_ = create_user_instance

        #  cSpell: ignore kPrzJ20IllmN
        payload = {
            "username": user_.email,
            "password": "kPrzJ20IllmN"
        }

        mock_get_user_by_email = mocker.patch(
            "routers.users_routes.get_user_by_email", return_value=user_)

        res = test_client.post(
            "/user/login",
            headers={"Content-Type": "application/x-www-form-urlencoded",
                     "accept": 'application/json'},
            data=payload
        )

        mock_get_user_by_email.assert_called_once()

        assert res.status_code == 200
        assert "access_token" in res.json()
        assert "token_type" in res.json()

    def test_get_users(self, test_client, create_user_instance, mocker: MockerFixture):
        users_ = [create_user_instance for _ in range(3)]

        mock_get_all_users = mocker.patch(
            "routers.users_routes.get_all_users", return_value=users_)

        res = test_client.get(
            "/user/",
            headers={"Content-Type": "application/json"}
        )

        mock_get_all_users.assert_called_once()

        assert res.status_code == 200
        assert len(res.json()) == 3

    def test_get_user(self, test_client, create_user_instance, mocker: MockerFixture):

        user_ = create_user_instance

        mock_get_user_by_id = mocker.patch(
            "routers.users_routes.get_user_by_id", return_value=user_
        )

        res = test_client.get(
            f"/user/{user_.id}",
            headers={"Content-Type": "application/json"}
        )

        mock_get_user_by_id.assert_called_once_with(
            db=mocker.ANY, user_id=user_.id)

        assert res.status_code == 200

    def test_get_non_existent_user(self, test_client, mocker: MockerFixture, faker):
        _id: str = faker.uuid4()

        mock_get_user_by_id = mocker.patch(
            "routers.users_routes.get_user_by_id",
            return_value=None
        )

        res = test_client.get(
            f"/user/{_id}", headers={"Content-Type": "application/json"})

        mock_get_user_by_id.assert_called_once_with(db=mocker.ANY, user_id=_id)

        assert res.status_code == 404
