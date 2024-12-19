import json
from uuid import uuid4

import pytest
from httpx import AsyncClient
from pytest_mock import MockerFixture
from sqlalchemy.orm import Session

from auth.authenticate import create_access_token
from schemas import SubjectBase, UpdateSubjectBase
from tests.conf_test_db import app


class TestSyncSubjectRoutes:
    def test_get_subjects(
        self, mocker: MockerFixture, test_client, create_subject_fixture
    ):
        subjects_ = [create_subject_fixture for _ in range(4)]
        mock_db_read_all_subjects = mocker.patch(
            "routers.subject_routes.db_read_all_subjects", return_value=subjects_
        )

        response = test_client.get("/subjects")

        db_call_args = mock_db_read_all_subjects.call_args.args

        assert response.status_code == 200
        assert isinstance(db_call_args[0], Session)
        assert isinstance(db_call_args[1], int)
        mock_db_read_all_subjects.assert_called_once()

    def test_get_subject(
        self, mocker: MockerFixture, test_client, create_subject_fixture
    ):
        subject_ = create_subject_fixture
        mock_db_read_subject_by_id = mocker.patch(
            "routers.subject_routes.db_read_subject_by_id", return_value=subject_
        )

        response = test_client.get(f"/subjects/{subject_.id}")

        db_call_args = mock_db_read_subject_by_id.call_args.args

        assert response.status_code == 200
        assert isinstance(db_call_args[0], Session)
        assert isinstance(db_call_args[1], str)
        mock_db_read_subject_by_id.assert_called_once()


@pytest.mark.usefixtures("anyio_backend")
class TestAsyncSubjectRoutes:
    @pytest.fixture
    def subject_payload_json(self, faker):
        return {
            "id": str(uuid4()),
            "title": f"{faker.sentence(nb_words=6)}",
            "slug": f"{faker.sentence(nb_words=5)}",
        }

    async def test_create_subject(
        self,
        mocker: MockerFixture,
        create_super_user_instance,
        subject_payload_json,
        create_subject_fixture,
    ):
        subject_ = create_subject_fixture
        payload_ = subject_payload_json
        user_ = create_super_user_instance
        token_ = create_access_token(data={"user": user_.email})

        mock_get_user_by_email = mocker.patch(
            "utils.dependencies.get_user_by_email", return_value=user_
        )

        mock_db_create_subject = mocker.patch(
            "routers.subject_routes.db_create_subject", return_value=subject_
        )

        async with AsyncClient(app=app, base_url="http://localhost/subjects") as client:
            response = await client.post(
                "/subject",
                headers={"Authorization": f"Bearer {token_}"},
                content=json.dumps(payload_),
            )

        db_call_args: tuple = mock_db_create_subject.call_args.args

        print(response.json())
        assert response.status_code == 201
        assert isinstance(db_call_args[0], Session)
        assert isinstance(db_call_args[1], SubjectBase)
        mock_get_user_by_email.assert_called_once()
        mock_db_create_subject.assert_called_once()

    async def test_update_subject(
        self,
        mocker: MockerFixture,
        create_super_user_instance,
        subject_payload_json,
        create_subject_fixture,
    ):
        subject_ = create_subject_fixture
        payload = {"title": "updated title"}
        user_ = create_super_user_instance
        token_ = create_access_token(data={"user": user_.email})

        mock_update_subject = mocker.patch(
            "routers.subject_routes.db_update_subject", return_value=subject_
        )

        async with AsyncClient(app=app, base_url="http://localhost/subjects") as client:
            res = await client.put(
                f"/{subject_.id}",
                headers={"Authorization": f"Bearer {token_}"},
                content=json.dumps(payload),
            )

        db_call_args: tuple = mock_update_subject.call_args.args

        assert res.status_code == 202
        assert isinstance(db_call_args[0], Session)
        assert isinstance(db_call_args[1], str)
        assert isinstance(db_call_args[2], UpdateSubjectBase)

    async def test_delete_module(
        self,
        mocker: MockerFixture,
        create_super_user_instance,
        subject_payload_json,
        create_subject_fixture,
    ):
        subject_ = create_subject_fixture
        user_ = create_super_user_instance
        token_ = create_access_token(data={"user": user_.email})

        mock_get_subject_by_id = mocker.patch(
            "routers.subject_routes.db_read_subject_by_id", return_value=subject_
        )
        mock_delete_subject = mocker.patch(
            "routers.subject_routes.delete_subject_by_id", return_value=None
        )

        async with AsyncClient(app=app, base_url="http://localhost/subjects") as client:
            res = await client.delete(
                f"/{subject_.id}",
                headers={"Authorization": f"Bearer {token_}"},
            )

        db_call_args: tuple = mock_delete_subject.call_args.args

        assert res.status_code == 204
        assert isinstance(db_call_args[0], Session)
        assert isinstance(db_call_args[1], str)
        mock_get_subject_by_id.assert_called_once()
        mock_delete_subject.assert_called_once()
