import datetime
import json

import pytest

from faker import Faker
from fastapi import status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

import crud.users_crud
import routers

from auth.authenticate import jwt_provider, create_access_token
from routers.users_routes import login
from schemas.auth_schemas import Token
from tests.conf_test_db import override_get_db

fake = Faker()


@pytest.fixture(scope="function")
def seed_user(test_client):
    test_client.post(
        "/user/register",
        headers={
            "accept": "application/json",
        },
        data=json.dumps(
            {
                "first_name": "Berny",
                "last_name": "Stoop",
                "email": "bstoop2@mashable.com",
                "job_title": "Social Worker",
                "is_super_user": False,
                "password": "rdpK37533T",
            }
        ),
    )


# noinspection DuplicatedCode
class TestFSMTesting:
    @pytest.mark.parametrize(
        "email, password, expected_status_code, expected_message",
        [
            (
                fake.email(),
                fake.password(),
                status.HTTP_404_NOT_FOUND,
                "Invalid Credentials",
            ),
            (
                "bstoop2@mashable.com",
                fake.password(),
                status.HTTP_404_NOT_FOUND,
                "Invalid Credentials",
            ),
            ("bstoop2@mashable.com", "rdpK37533T", status.HTTP_200_OK, None),
        ],
    )
    def test_user_login(
        self,
        test_client,
        mocker,
        seed_user,
        email,
        password,
        expected_status_code,
        expected_message,
    ):
        # database session
        db = next(override_get_db())

        spy_email = mocker.spy(routers.users_routes, "get_user_by_email")
        spy_pwd = mocker.spy(routers.users_routes, "verify_password")
        spy_token = mocker.spy(routers.users_routes, "create_access_token")
        spy_encode = mocker.spy(jwt_provider, "encode")

        # Your mock OAuth2PasswordRequestForm
        mock_req = mocker.Mock(
            spec=OAuth2PasswordRequestForm, username=email, password=password
        )

        if email != "bstoop2@mashable.com" and password != "rdpK37533T":
            # Unregistered user, only query in db state called
            with pytest.raises(HTTPException) as err:
                login(req=mock_req, database=db)

            # assert res is None
            assert err.value.detail == expected_message
            assert err.value.status_code == expected_status_code

            spy_email.assert_called_once_with(db, email)
            spy_pwd.assert_not_called()

        elif email == "bstoop2@mashable.com" and password != "rdpK37533T":
            # registered user, query in db state called and verify pwd called
            with pytest.raises(HTTPException) as err:
                login(req=mock_req, database=db)

            # assert res is None
            assert err.value.detail == expected_message
            assert err.value.status_code == expected_status_code

            spy_email.assert_called_once_with(db, email)
            spy_pwd.assert_called_once()

        else:
            res = login(req=mock_req, database=db)
            assert res is not None
            assert isinstance(res, Token)

            spy_email.assert_called_once_with(db, email)
            spy_pwd.assert_called_once()
            spy_token.assert_called_once_with({"user": email})
            spy_encode.assert_called_once()

    def test_user_token_validity(self, test_client, seed_user):
        res = test_client.post(
            "/user/login",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "accept": "application/json",
            },
            data={"username": "bstoop2@mashable.com", "password": "rdpK37533T"},
        )

        token_json = res.json()["access_token"]
        decoded_token = jwt_provider.decode(token_json)
        validity = datetime.datetime.fromtimestamp(decoded_token["exp"])
        current_time = datetime.datetime.now()

        assert res.status_code == status.HTTP_200_OK
        assert validity > current_time
        assert (validity - current_time) > datetime.timedelta(minutes=29)

    def test_user_token_set_expiry(self):
        test_email = fake.email()
        token = create_access_token(
            data={"user": test_email}, expires_delta=datetime.timedelta(minutes=5)
        )

        decoded_token = jwt_provider.decode(token)
        validity = datetime.datetime.fromtimestamp(decoded_token["exp"])
        current_time = datetime.datetime.now()

        assert token is not None
        assert validity > current_time
        assert (validity - current_time) > datetime.timedelta(minutes=4)

    def test_get_user_by_email_db_query_state_visited(self, mocker, seed_user):
        data = {"username": "bstoop2@mashable.com", "password": "rdpK37533T"}

        # database session
        db = next(override_get_db())

        # Your mock OAuth2PasswordRequestForm
        mock_req = mocker.Mock(
            spec=OAuth2PasswordRequestForm,
            username=data["username"],
            password=data["password"],
        )

        spy = mocker.spy(routers.users_routes, "get_user_by_email")

        login(req=mock_req, database=db)

        spy.assert_called_once_with(db, data["username"])

    def test_verify_password_state_visited(self, mocker, seed_user):
        data = {"username": "bstoop2@mashable.com", "password": "rdpK37533T"}

        # database session
        db = next(override_get_db())

        # Your mock OAuth2PasswordRequestForm
        mock_req = mocker.Mock(
            spec=OAuth2PasswordRequestForm,
            username=data["username"],
            password=data["password"],
        )

        spy_email = mocker.spy(routers.users_routes, "get_user_by_email")
        spy = mocker.spy(routers.users_routes, "verify_password")

        login(req=mock_req, database=db)

        spy_email.assert_called_once_with(db, data["username"])
        spy.assert_called_once()

    def test_create_access_token_state_visited(self, mocker, seed_user):
        data = {"username": "bstoop2@mashable.com", "password": "rdpK37533T"}

        # database session
        db = next(override_get_db())

        # Your mock OAuth2PasswordRequestForm
        mock_req = mocker.Mock(
            spec=OAuth2PasswordRequestForm,
            username=data["username"],
            password=data["password"],
        )

        spy_email = mocker.spy(routers.users_routes, "get_user_by_email")
        spy_pwd = mocker.spy(routers.users_routes, "verify_password")
        spy_token = mocker.spy(routers.users_routes, "create_access_token")

        login(req=mock_req, database=db)
        user = crud.users_crud.get_user_by_email(db, data["username"])

        spy_email.assert_called_once_with(db, data["username"])
        spy_pwd.assert_called_once_with(mock_req.password, user.password)
        spy_token.assert_called_once_with({"user": data["username"]})

    def test_create_encode_payload_state_visited(self, mocker, seed_user):
        data = {"username": "bstoop2@mashable.com", "password": "rdpK37533T"}

        # database session
        db = next(override_get_db())

        # Your mock OAuth2PasswordRequestForm
        mock_req = mocker.Mock(
            spec=OAuth2PasswordRequestForm,
            username=data["username"],
            password=data["password"],
        )

        spy_email = mocker.spy(routers.users_routes, "get_user_by_email")
        spy_pwd = mocker.spy(routers.users_routes, "verify_password")
        spy_token = mocker.spy(routers.users_routes, "create_access_token")
        spy_encode = mocker.spy(jwt_provider, "encode")

        login(req=mock_req, database=db)
        user = crud.users_crud.get_user_by_email(db, data["username"])

        spy_email.assert_called_once_with(db, data["username"])
        spy_pwd.assert_called_once_with(mock_req.password, user.password)
        spy_token.assert_called_once_with({"user": data["username"]})
        spy_encode.assert_called_once()
