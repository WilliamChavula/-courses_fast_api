import asyncio
import json
import pytest

from faker import Faker
from fastapi import status
from httpx import AsyncClient

from auth.authenticate import create_access_token
from tests.conf_test_db import app

fake = Faker()


@pytest.fixture
async def seed_courses(mocker, create_super_user_instance, course_schema_fixture):
    courses_ = [course_schema_fixture for _ in range(20)]
    user_ = create_super_user_instance
    token_ = create_access_token(data={"user": user_.email})

    mocker.patch("utils.dependencies.get_user_by_email", return_value=user_)

    async with AsyncClient(app=app, base_url="http://localhost") as client:
        """
        Use semaphore to avoid sqlalchemy.exc.TimeoutError: QueuePool limit
        """
        semaphore = asyncio.Semaphore(5)  # Limit to 5 concurrent requests

        async def post_course(course):
            async with semaphore:
                return await client.post(
                    "/courses",
                    headers={"Authorization": f"Bearer {token_}"},
                    content=course.json(),
                )

        responses = await asyncio.gather(*[post_course(course) for course in courses_])

        return responses


@pytest.mark.usefixtures("anyio_backend")
class TestDDG:
    def test_update_with_incorrect_uuid_returns_404(
        self, mocker, create_super_user_instance, test_client
    ):
        mocker.patch(
            "utils.dependencies.get_user_by_email",
            return_value=create_super_user_instance,
        )

        token_ = create_access_token(data={"user": create_super_user_instance.email})

        response = test_client.put(
            f"/courses/{fake.uuid4()}",
            headers={"accept": "application/json", "Authorization": f"Bearer {token_}"},
            data=json.dumps(
                {
                    "title": "Namfix",
                    "slug": "grow transparent interfaces",
                    "overview": "Fusce lacus purus, aliquet at, feugiat non, pretium quis, lectus. Suspendisse potenti.",
                }
            ),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_with_incorrect_uuid_and_none_user_returns_403(
        self, test_client, mocker, create_user_instance
    ):
        mocker.patch("utils.dependencies.get_user_by_email", return_value=None)

        token_ = create_access_token(data={"user": create_user_instance.email})

        response = test_client.put(
            f"/courses/{fake.uuid4()}",
            headers={"accept": "application/json", "Authorization": f"Bearer {token_}"},
            data=json.dumps(
                {
                    "title": "Namfix",
                    "slug": "grow transparent interfaces",
                    "overview": "Fusce lacus purus, aliquet at, feugiat non, pretium quis, lectus. Suspendisse potenti.",
                }
            ),
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_with_incorrect_uuid_and_non_superuser_returns_403(
        self, test_client, mocker, create_user_instance
    ):
        mocker.patch(
            "utils.dependencies.get_user_by_email", return_value=create_user_instance
        )

        token_ = create_access_token(data={"user": create_user_instance.email})

        response = test_client.put(
            f"/courses/{fake.uuid4()}",
            headers={"accept": "application/json", "Authorization": f"Bearer {token_}"},
            data=json.dumps(
                {
                    "title": "Namfix",
                    "slug": "grow transparent interfaces",
                    "overview": "Fusce lacus purus, aliquet at, feugiat non, pretium quis, lectus. Suspendisse potenti.",
                }
            ),
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_with_correct_uuid_and_non_superuser_returns_403(
        self, test_client, mocker, create_course_fixture, create_user_instance
    ):
        mocker.patch(
            "utils.dependencies.get_user_by_email", return_value=create_user_instance
        )

        token_ = create_access_token(data={"user": create_user_instance.email})

        response = test_client.put(
            f"/courses/{create_course_fixture.id}",
            headers={"accept": "application/json", "Authorization": f"Bearer {token_}"},
            data=json.dumps(
                {
                    "title": "Namfix",
                    "slug": "grow transparent interfaces",
                    "overview": "Fusce lacus purus, aliquet at, feugiat non, pretium quis, lectus. Suspendisse potenti.",
                }
            ),
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_with_correct_uuid_and_superuser_returns_202(
        self, test_client, mocker, create_course_fixture, create_super_user_instance
    ):
        mocker.patch(
            "utils.dependencies.get_user_by_email",
            return_value=create_super_user_instance,
        )

        token_ = create_access_token(data={"user": create_super_user_instance.email})

        response = test_client.put(
            f"/courses/{create_course_fixture.id}",
            headers={"accept": "application/json", "Authorization": f"Bearer {token_}"},
            data=json.dumps(
                {
                    "title": "Namfix",
                    "slug": "grow transparent interfaces",
                    "overview": "Fusce lacus purus, aliquet at, feugiat non, pretium quis, lectus. Suspendisse potenti.",
                }
            ),
        )

        assert response.status_code == status.HTTP_202_ACCEPTED
