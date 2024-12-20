import pytest
from httpx import AsyncClient
from pytest_mock import MockerFixture

from auth.authenticate import create_access_token
from tests.conf_test_db import app


@pytest.mark.usefixtures("anyio_backend")
class TestAsyncCourseRoutes:
    pytestmark = pytest.mark.anyio

    async def test_get_courses(self, create_course_fixture):
        course_ = create_course_fixture
        async with AsyncClient(app=app, base_url="http://localhost/courses") as ac:
            response = await ac.get("/")

        assert response.status_code == 200
        assert response.json()[0]["id"] is not None
        assert response.json()[0]["owner"] == course_.owner

    async def test_get_course(self, create_course_fixture):
        course_fixture = create_course_fixture

        async with AsyncClient(app=app, base_url="http://localhost/courses") as ac:
            res = await ac.get(f"/{course_fixture.id}")
        assert res.status_code == 200
        assert res.json()["id"] == course_fixture.id

    async def test_create_course_with_no_token(self, course_schema_fixture):
        async with AsyncClient(app=app, base_url="http://localhost/courses") as ac:
            res = await ac.post("/course", json=course_schema_fixture.json())
        assert res.status_code == 401

    async def test_create_course(
        self, mocker: MockerFixture, create_super_user_instance, course_schema_fixture
    ):
        user_ = create_super_user_instance

        mock_get_user_by_email = mocker.patch(
            "utils.dependencies.get_user_by_email", return_value=user_
        )

        token_ = create_access_token(data={"user": user_.email})

        async with AsyncClient(app=app, base_url="http://localhost/courses") as ac:
            res = await ac.post(
                "/course",
                headers={"Authorization": f"Bearer {token_}"},
                content=course_schema_fixture.json(),
            )

        mock_get_user_by_email.assert_called_once()
        assert res.status_code == 201
        assert res.json()["id"] is not None
        assert res.json()["owner"] == course_schema_fixture.owner

    async def test_create_course_not_super_user(
        self, mocker, create_user_instance, course_schema_fixture
    ):
        user_ = create_user_instance

        mock_get_user_by_email = mocker.patch(
            "utils.dependencies.get_user_by_email", return_value=user_
        )

        token_ = create_access_token(data={"user": user_.email})

        async with AsyncClient(app=app, base_url="http://localhost/courses") as ac:
            res = await ac.post(
                "/course",
                headers={"Authorization": f"Bearer {token_}"},
                content=course_schema_fixture.json(),
            )

        mock_get_user_by_email.assert_called_once()
        assert res.status_code == 403


class TestSyncCourseRoutes:
    def test_update_course_not_super_user(
        self, mocker, create_user_instance, create_course_fixture, test_client
    ):
        original_course = create_course_fixture
        user_ = create_user_instance

        mock_get_user_by_email = mocker.patch(
            "utils.dependencies.get_user_by_email", return_value=user_
        )

        token_ = create_access_token(data={"user": user_.email})

        res = test_client.put(
            f"/courses/{original_course.id}/",
            headers={"Authorization": f"Bearer {token_}"},
            data={"title": "Updated title"},
        )

        mock_get_user_by_email.assert_called_once()
        assert res.status_code == 403

    @pytest.mark.usefixtures("authenticated_user")
    def test_update_course_super_user(
        self, create_super_user_instance, create_course_fixture, test_client
    ):
        original_course = create_course_fixture
        user_ = create_super_user_instance

        token_ = create_access_token(data={"user": user_.email})

        res = test_client.put(
            f"/courses/{original_course.id}/",
            headers={
                "Authorization": f"Bearer {token_}",
                "Content-type": "application/json",
            },
            json={"title": "Updated title"},
        )

        assert res.status_code == 202
        assert res.json()["title"] == "Updated title"

    @pytest.mark.usefixtures("authenticated_user")
    def test_delete_course_super_user(
        self, create_super_user_instance, create_course_fixture, test_client
    ):
        original_course = create_course_fixture
        user_ = create_super_user_instance

        token_ = create_access_token(data={"user": user_.email})

        res = test_client.delete(
            f"/courses/{original_course.id}/",
            headers={
                "Authorization": f"Bearer {token_}",
                "Content-type": "application/json",
            },
            json={"title": "Updated title"},
        )

        assert res.status_code == 204
        assert res.json() is None
