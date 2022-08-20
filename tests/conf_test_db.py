from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app

from core.settings import Settings
from main import Base
from utils import get_db


SQLALCHEMY_DATABASE_URL = f"postgresql://{Settings.POSTGRES_USER}:{Settings.POSTGRES_PWD}@{Settings.IP_ADDR}/tests"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
