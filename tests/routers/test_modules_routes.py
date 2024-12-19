import json
from uuid import uuid4

from httpx import AsyncClient
import pytest
from pytest_mock import MockerFixture
from sqlalchemy.orm import Session

from schemas import ModuleBase, UpdateModuleBase
from auth.authenticate import create_access_token
from tests.conf_test_db import app


class TestSyncModulesRoutes:
    def test_get_modules(
        self, mocker: MockerFixture, test_client, create_module_fixture
    ):
        modules_ = [create_module_fixture for _ in range(4)]
        mock_db_read_all_modules = mocker.patch(
            "routers.modules_routes.db_read_all_modules", return_value=modules_
        )

        res = test_client.get("/modules")

        assert res.status_code == 200
        assert len(res.json()) == 4
        mock_db_read_all_modules.assert_called_once_with(mocker.ANY, 10)

    def test_get_module_by_id(
        self, mocker: MockerFixture, test_client, create_module_fixture
    ):
        module_ = create_module_fixture
        mock_db_read_module_by_id = mocker.patch(
            "routers.modules_routes.db_read_module_by_id", return_value=module_
        )

        res = test_client.get(f"/modules/{module_.id}")

        assert res.status_code == 200
        mock_db_read_module_by_id.assert_called_once_with(
            db=mocker.ANY, module_id=module_.id
        )


@pytest.mark.usefixtures("anyio_backend")
class TestAsyncModulesRoutes:
    @pytest.fixture
    def module_payload_json(self, faker):
        return {
            "id": str(uuid4()),
            "title": f"{faker.sentence(nb_words=6)}",
            "description": f"{faker.sentence(nb_words=5)}",
        }

    async def test_create_module(
        self,
        mocker: MockerFixture,
        create_module_fixture,
        module_payload_json,
        create_super_user_instance,
    ):
        module_ = create_module_fixture
        payload = module_payload_json
        user_ = create_super_user_instance
        token_ = create_access_token(data={"user": user_.email})

        mock_get_user_by_email = mocker.patch(
            "utils.dependencies.get_user_by_email", return_value=user_
        )

        mock_db_create_module = mocker.patch(
            "routers.modules_routes.db_create_module", return_value=module_
        )

        async with AsyncClient(app=app, base_url="http://localhost/modules") as ac:
            res = await ac.post(
                "/module",
                headers={"Authorization": f"Bearer {token_}"},
                content=json.dumps(payload),
            )

        db_call_args: tuple = mock_db_create_module.call_args.args

        assert res.status_code == 201
        assert isinstance(db_call_args[0], Session)
        assert isinstance(db_call_args[1], ModuleBase)
        mock_db_create_module.assert_called_once()
        mock_get_user_by_email.assert_called_once()

    async def test_update_module(
        self,
        mocker: MockerFixture,
        create_module_fixture,
        module_payload_json,
        create_super_user_instance,
    ):
        module_ = create_module_fixture
        payload = {"title": "updated title"}
        user_ = create_super_user_instance
        token_ = create_access_token(data={"user": user_.email})

        mock_update_module = mocker.patch(
            "routers.modules_routes.db_update_module", return_value=module_
        )

        async with AsyncClient(app=app, base_url="http://localhost/modules") as ac:
            res = await ac.put(
                f"/{module_.id}",
                headers={"Authorization": f"Bearer {token_}"},
                content=json.dumps(payload),
            )

        db_call_args: tuple = mock_update_module.call_args.args

        assert res.status_code == 202
        assert isinstance(db_call_args[0], Session)
        assert isinstance(db_call_args[1], str)
        assert isinstance(db_call_args[2], UpdateModuleBase)

    async def test_delete_module(
        self,
        mocker: MockerFixture,
        create_module_fixture,
        module_payload_json,
        create_super_user_instance,
    ):
        module_ = create_module_fixture
        user_ = create_super_user_instance
        token_ = create_access_token(data={"user": user_.email})

        mock_get_module_by_id = mocker.patch(
            "routers.modules_routes.get_module_by_id", return_value=module_
        )
        mock_delete_module = mocker.patch(
            "routers.modules_routes.delete_module_by_id", return_value=None
        )

        async with AsyncClient(app=app, base_url="http://localhost/modules") as ac:
            res = await ac.delete(
                f"/{module_.id}",
                headers={"Authorization": f"Bearer {token_}"},
            )

        db_call_args: tuple = mock_delete_module.call_args.args

        assert res.status_code == 204
        assert isinstance(db_call_args[0], Session)
        assert isinstance(db_call_args[1], str)
        mock_get_module_by_id.assert_called_once()
        mock_delete_module.assert_called_once()
