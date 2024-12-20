from datetime import datetime
from random import randint
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from auth.hashing import get_password_hash
from models.course_models import CourseModel
from models.module_models import ModuleModel
from models.subject_models import SubjectModel
from models.user_models import UserModel
from schemas.course_schemas import CourseBase
from schemas.module_schemas import ModuleBase
from schemas.subject_schemas import SubjectBase
from tests.conf_test_db import app, override_get_db


@pytest.fixture(scope="class")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="module")
def test_client():
    from utils import get_db

    # noinspection PyUnresolvedReferences
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client


@pytest.fixture(autouse=True)
def faker_seed():
    return randint(101, 500)


# noinspection PyUnresolvedReferences
@pytest.fixture
def authenticated_user(create_super_user_instance):
    from auth.authenticate import create_access_token, get_current_user
    from utils.dependencies import verify_super_user

    user_ = create_super_user_instance

    from tests.conf_test_db import override_get_db
    from utils import get_db

    token_ = create_access_token(data={"user": user_.email})
    token_data = get_current_user(token_)

    def override_verify_super_user():
        return user_

    app.dependency_overrides[verify_super_user] = override_verify_super_user
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: token_data

    yield
    del app.dependency_overrides[verify_super_user]
    del app.dependency_overrides[get_db]
    del app.dependency_overrides[get_current_user]


@pytest.fixture
def subject_schema_fixture(faker):
    subject_to_create = SubjectBase(
        title=faker.sentence(nb_words=15), slug=faker.text(max_nb_chars=70)
    )
    return subject_to_create


@pytest.fixture
def module_schema_fixture(faker):
    module_to_create = ModuleBase(
        title=faker.sentence(nb_words=15), description=faker.text(max_nb_chars=100)
    )

    return module_to_create


@pytest.fixture
def course_schema_fixture(faker, module_schema_fixture, subject_schema_fixture):
    course_to_create = CourseBase(
        module=module_schema_fixture,
        subject=subject_schema_fixture,
        overview=faker.sentence(nb_words=35),
        owner=f"{faker.prefix()} {faker.name()}",
        slug=faker.sentence(nb_words=15),
        title=faker.sentence(nb_words=5),
    )
    return course_to_create


@pytest.fixture
def create_subject_fixture(faker):
    subject = SubjectModel(
        id=str(uuid4()), title=faker.sentence(), slug=faker.sentence(nb_words=12)
    )

    return subject


@pytest.fixture
def create_module_fixture(faker):
    module = ModuleModel(
        id=str(uuid4()),
        title=faker.sentence(nb_words=6),
        description=faker.sentence(nb_words=30),
    )

    return module


@pytest.fixture
def create_course_fixture(faker, create_module_fixture, create_subject_fixture):
    database = next(override_get_db())

    new_module = create_module_fixture
    database.add(new_module)
    database.commit()
    database.refresh(new_module)

    new_subject = create_subject_fixture
    database.add(new_subject)
    database.commit()
    database.refresh(new_subject)

    # noinspection PyArgumentList
    new_course = CourseModel(
        id=str(uuid4()),
        module=new_module,
        subject=new_subject,
        owner=f"{faker.prefix()} {faker.name()}",
        title=faker.sentence(nb_words=6),
        slug=faker.sentence(nb_words=10),
        overview=faker.sentence(nb_words=70),
        created=datetime.now(),
    )

    database.add(new_course)
    database.commit()
    database.refresh(new_course)

    yield new_course

    database.execute(delete(CourseModel).where(CourseModel.id == new_course.id))
    database.commit()


@pytest.fixture
def create_course_json_fixture(faker):
    database = next(override_get_db())

    new_course = {
        "id": str(uuid4()),
        "module": {
            "id": str(uuid4()),
            "title": f"{faker.sentence(nb_words=6)}",
            "description": f"{faker.sentence(nb_words=5)}",
        },
        "subject": {
            "id": str(uuid4()),
            "title": f"{faker.sentence(nb_words=6)}",
            "description": f"{faker.sentence(nb_words=10)}",
        },
        "owner": f"{faker.prefix()} {faker.name()}",
        "title": faker.sentence(nb_words=6),
        "slug": faker.slug(),
        "overview": faker.sentence(nb_words=70),
        "created": datetime.now(),
    }

    database.add(new_course)
    database.commit()
    database.refresh(new_course)

    yield new_course

    database.execute(delete(CourseModel).where(CourseModel.id == new_course["id"]))
    database.commit()


@pytest.fixture
def create_user_instance(faker):
    user = UserModel(
        id=str(uuid4()),
        first_name=faker.first_name(),
        last_name=faker.last_name(),
        email=faker.email(),
        job_title=faker.job(),
        password=get_password_hash("kPrzJ20IllmN"),
        is_super_user=False,
        created_at=datetime.now(),
    )

    return user


@pytest.fixture
def create_super_user_instance(faker):
    super_user = UserModel(
        id=str(uuid4()),
        first_name=faker.first_name(),
        last_name=faker.last_name(),
        email=faker.email(),
        job_title=faker.job(),
        password=get_password_hash("kPrzJ20IllmN"),
        is_super_user=True,
        created_at=datetime.now(),
    )

    return super_user
