import asyncio
import json
from uuid import uuid4

import pytest
from faker import Faker
from fastapi import status
from httpx import AsyncClient
from pytest_mock import MockerFixture

from auth.authenticate import create_access_token
from tests.conf_test_db import app

fake = Faker()


@pytest.fixture
def subject_payload_json(faker):
    return {
        "id": str(uuid4()),
        "title": f"{faker.sentence(nb_words=6)}",
        "slug": f"{faker.sentence(nb_words=5)}",
    }


@pytest.fixture
async def seed_subjects(
    mocker: MockerFixture,
    subject_schema_fixture,
    create_super_user_instance,
):
    subjects_ = [subject_schema_fixture for _ in range(20)]
    user_ = create_super_user_instance
    token_ = create_access_token(data={"user": user_.email})

    mocker.patch("utils.dependencies.get_user_by_email", return_value=user_)

    async with AsyncClient(app=app, base_url="http://localhost") as client:
        """
        Use semaphore to avoid sqlalchemy.exc.TimeoutError: QueuePool limit
        """
        semaphore = asyncio.Semaphore(5)  # Limit to 5 concurrent requests

        async def post_subject(subject):
            async with semaphore:
                return await client.post(
                    "/subjects",
                    headers={"Authorization": f"Bearer {token_}"},
                    content=subject.json(),
                )

        responses = await asyncio.gather(
            *[post_subject(subject) for subject in subjects_]
        )

        return responses


@pytest.mark.usefixtures("anyio_backend")
class TestPartitionBasedTesting:
    @pytest.mark.parametrize(
        "limit, expected, status_code",
        [
            (None, 10, status.HTTP_200_OK),
            (1, 1, status.HTTP_200_OK),
            (
                100,
                60,
                status.HTTP_200_OK,
            ),  # 60 because it's the 3rd iteration of 20 batch inserts
            (0, 1, status.HTTP_422_UNPROCESSABLE_ENTITY),
            (-5, 1, status.HTTP_422_UNPROCESSABLE_ENTITY),
            (101, 1, status.HTTP_422_UNPROCESSABLE_ENTITY),
            ("ten", 1, status.HTTP_422_UNPROCESSABLE_ENTITY),
            (10.5, 1, status.HTTP_422_UNPROCESSABLE_ENTITY),
        ],
    )
    async def test_get_subjects(
        self,
        seed_subjects,
        test_client,
        subject_schema_fixture,
        create_super_user_instance,
        limit,
        expected,
        status_code,
    ):
        url = f"/subjects?limit={limit}" if limit is not None else "/subjects"

        async with AsyncClient(app=app, base_url="http://localhost") as client:
            response = await client.get(url)

        assert response.status_code == status_code
        assert len(response.json()) == expected

    async def test_get_subjects_no_limit(
        self,
        mocker: MockerFixture,
        test_client,
        subject_schema_fixture,
        create_super_user_instance,
    ):
        subjects_ = [subject_schema_fixture for _ in range(20)]
        user_ = create_super_user_instance
        token_ = create_access_token(data={"user": user_.email})

        mock_get_user_by_email = mocker.patch(
            "utils.dependencies.get_user_by_email", return_value=user_
        )

        async with AsyncClient(app=app, base_url="http://localhost") as client:
            """
            Use semaphore to avoid sqlalchemy.exc.TimeoutError: QueuePool limit
            """
            semaphore = asyncio.Semaphore(5)  # Limit to 5 concurrent requests

            async def post_subject(subject):
                async with semaphore:
                    return await client.post(
                        "/subjects",
                        headers={"Authorization": f"Bearer {token_}"},
                        content=subject.json(),
                    )

            await asyncio.gather(*[post_subject(subject) for subject in subjects_])

        response = test_client.get("/subjects")

        assert len(response.json()) == 10
        assert mock_get_user_by_email.call_count == len(subjects_)
        assert response.status_code == status.HTTP_200_OK

    async def test_get_subject_returns_200(
        self, test_client, create_super_user_instance, seed_subjects
    ):
        response = seed_subjects[0]

        subject_id = response.json()["id"]
        response = test_client.get(f"/subjects/{subject_id}")

        assert response.status_code == 200

    @pytest.mark.parametrize(
        "subject_id, expected_status_code",
        [
            ("19bc5f87-c77f-4794-b681-e6b12e372bed", 404),
            ("19bc5f87-c77f-4794-b681-e6b12e372bed; DELETE FROM public.subject;", 404),
            (" ", 404),  # use space otherwise it matches `/subjects` route
            (None, 404),
        ],
    )
    async def test_get_subject_returns_404(
        self,
        test_client,
        create_super_user_instance,
        seed_subjects,
        subject_id,
        expected_status_code,
    ):
        response = test_client.get(f"/subjects/{subject_id}")

        assert response.status_code == expected_status_code

    @pytest.mark.parametrize(
        "entity, expected_status_code",
        [
            (
                {
                    "id": str(uuid4()),
                    "title": f"{fake.sentence(nb_words=6)}",
                    "slug": f"{fake.sentence(nb_words=5)}",
                },
                201,
            ),
            (
                {
                    "id": 5.5,
                    "title": 12.6,
                    "slug": True,
                },
                422,
            ),
            (
                {
                    "id": 5.5,
                    "slug": True,
                },
                422,
            ),
            (
                {
                    "id": str(uuid4()),
                    "title": f"{fake.sentence(nb_words=6)}",
                    "slug": f"{fake.sentence(nb_words=5)}",
                    "category": "Testing",
                    "lecturer": fake.name(),
                },
                201,
            ),
        ],
    )
    async def test_create_subject_with_valid_superuser(
        self,
        mocker: MockerFixture,
        create_super_user_instance,
        create_subject_fixture,
        entity,
        expected_status_code,
    ):
        user_ = create_super_user_instance
        token_ = create_access_token(data={"user": user_.email})

        mock_get_user_by_email = mocker.patch(
            "utils.dependencies.get_user_by_email", return_value=user_
        )

        async with AsyncClient(app=app, base_url="http://localhost") as client:
            response = await client.post(
                "/subjects",
                headers={"Authorization": f"Bearer {token_}"},
                content=json.dumps(entity),
            )

        assert response.status_code == expected_status_code
        mock_get_user_by_email.assert_called_once()

    async def test_create_subject_with_not_superuser(
        self,
        mocker: MockerFixture,
        create_user_instance,
        create_subject_fixture,
        subject_payload_json,
    ):
        user_ = create_user_instance
        token_ = create_access_token(data={"user": user_.email})

        mock_get_user_by_email = mocker.patch(
            "utils.dependencies.get_user_by_email", return_value=user_
        )

        async with AsyncClient(app=app, base_url="http://localhost") as client:
            response = await client.post(
                "/subjects",
                headers={"Authorization": f"Bearer {token_}"},
                content=json.dumps(subject_payload_json),
            )

        assert response.status_code == 403
        mock_get_user_by_email.assert_called_once()

    async def test_create_subject_with_non_auth_user(
        self, create_subject_fixture, subject_payload_json
    ):
        async with AsyncClient(app=app, base_url="http://localhost") as client:
            response = await client.post(
                "/subjects",
                content=json.dumps(subject_payload_json),
            )

        assert response.status_code == 401

    @pytest.mark.parametrize(
        "entity, expected_status_code",
        [
            (
                {
                    "title": "This is your super, go for update",
                },
                status.HTTP_202_ACCEPTED,
            ),
            (None, status.HTTP_422_UNPROCESSABLE_ENTITY),
            ({"slug": 1.99}, status.HTTP_422_UNPROCESSABLE_ENTITY),
        ],
    )
    async def test_update_subject_with_valid_superuser(
        self,
        mocker: MockerFixture,
        create_super_user_instance,
        seed_subjects,
        entity,
        expected_status_code,
    ):
        subject_ = seed_subjects.pop().json()
        user_ = create_super_user_instance
        token_ = create_access_token(data={"user": user_.email})

        mocker.patch("utils.dependencies.get_user_by_email", return_value=user_)

        async with AsyncClient(app=app, base_url="http://localhost/subjects") as client:
            res = await client.put(
                f"/{subject_['id']}",
                headers={"Authorization": f"Bearer {token_}"},
                content=json.dumps(entity),
            )

        assert res.status_code == expected_status_code

    async def test_update_subject_with_invalid_subject_id(
        self,
        mocker: MockerFixture,
        create_super_user_instance,
        subject_payload_json,
        seed_subjects,
    ):
        user_ = create_super_user_instance
        token_ = create_access_token(data={"user": user_.email})

        mocker.patch("utils.dependencies.get_user_by_email", return_value=user_)

        async with AsyncClient(app=app, base_url="http://localhost/subjects") as client:
            res = await client.put(
                f"/{fake.uuid4()}",
                headers={"Authorization": f"Bearer {token_}"},
                content=json.dumps(subject_payload_json),
            )

        assert res.status_code == status.HTTP_404_NOT_FOUND

    async def test_update_subject_with_non_superuser(
        self,
        mocker: MockerFixture,
        create_user_instance,
        subject_payload_json,
        seed_subjects,
    ):
        user_ = create_user_instance
        token_ = create_access_token(data={"user": user_.email})
        subject_id = seed_subjects.pop().json()["id"]

        mocker.patch("utils.dependencies.get_user_by_email", return_value=user_)

        async with AsyncClient(app=app, base_url="http://localhost/subjects") as client:
            res = await client.put(
                f"/{subject_id}",
                headers={"Authorization": f"Bearer {token_}"},
                content=json.dumps(subject_payload_json),
            )

        assert res.status_code == status.HTTP_403_FORBIDDEN

    async def test_update_subject_with_non_auth_user(
        self,
        mocker: MockerFixture,
        subject_payload_json,
        seed_subjects,
    ):
        subject_id = seed_subjects.pop().json()["id"]

        mocker.patch("utils.dependencies.get_user_by_email", return_value=None)

        async with AsyncClient(app=app, base_url="http://localhost/subjects") as client:
            res = await client.put(
                f"/{subject_id}",
                content=json.dumps(subject_payload_json),
            )

        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_delete_subject_with_valid_superuser(
        self,
        mocker: MockerFixture,
        create_super_user_instance,
        seed_subjects,
    ):
        subject_id = seed_subjects.pop().json()["id"]
        user_ = create_super_user_instance
        token_ = create_access_token(data={"user": user_.email})

        mocker.patch("utils.dependencies.get_user_by_email", return_value=user_)

        async with AsyncClient(app=app, base_url="http://localhost/subjects") as client:
            res = await client.delete(
                f"/{subject_id}",
                headers={"Authorization": f"Bearer {token_}"},
            )

        assert res.status_code == status.HTTP_204_NO_CONTENT

    async def test_delete_subject_with_valid_superuser_invalid_subject_id(
        self,
        mocker: MockerFixture,
        create_super_user_instance,
        seed_subjects,
    ):
        subject_id = fake.uuid4()
        user_ = create_super_user_instance
        token_ = create_access_token(data={"user": user_.email})

        mocker.patch("utils.dependencies.get_user_by_email", return_value=user_)

        async with AsyncClient(app=app, base_url="http://localhost/subjects") as client:
            res = await client.delete(
                f"/{subject_id}",
                headers={"Authorization": f"Bearer {token_}"},
            )

        assert res.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_subject_with_valid_superuser_double_delete(
        self,
        mocker: MockerFixture,
        create_super_user_instance,
        seed_subjects,
    ):
        subject_id = seed_subjects.pop().json()["id"]
        user_ = create_super_user_instance
        token_ = create_access_token(data={"user": user_.email})

        mocker.patch("utils.dependencies.get_user_by_email", return_value=user_)

        async with AsyncClient(app=app, base_url="http://localhost/subjects") as client:
            await client.delete(
                f"/{subject_id}",
                headers={"Authorization": f"Bearer {token_}"},
            )

            res = await client.delete(
                f"/{subject_id}",
                headers={"Authorization": f"Bearer {token_}"},
            )

        assert res.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_subject_with_non_superuser(
        self,
        mocker: MockerFixture,
        create_user_instance,
        subject_payload_json,
        seed_subjects,
    ):
        user_ = create_user_instance
        token_ = create_access_token(data={"user": user_.email})
        subject_id = seed_subjects.pop().json()["id"]

        mocker.patch("utils.dependencies.get_user_by_email", return_value=user_)

        async with AsyncClient(app=app, base_url="http://localhost/subjects") as client:
            res = await client.delete(
                f"/{subject_id}",
                headers={"Authorization": f"Bearer {token_}"},
            )

        assert res.status_code == status.HTTP_403_FORBIDDEN

    async def test_delete_subject_with_non_auth_user(
        self,
        mocker: MockerFixture,
        subject_payload_json,
        seed_subjects,
    ):
        subject_id = seed_subjects.pop().json()["id"]

        mocker.patch("utils.dependencies.get_user_by_email", return_value=None)

        async with AsyncClient(app=app, base_url="http://localhost/subjects") as client:
            res = await client.delete(
                f"/{subject_id}",
            )

        assert res.status_code == status.HTTP_401_UNAUTHORIZED
