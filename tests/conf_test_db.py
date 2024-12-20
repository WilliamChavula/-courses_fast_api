from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from core.settings import Settings
from main import Base, app
from utils import get_db

DB_NAME = "tests"


SQLALCHEMY_DATABASE_URL = f"postgresql://{Settings.POSTGRES_USER}:{Settings.POSTGRES_PWD}@{Settings.IP_ADDR}/{DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# with engine.connect() as conn:
#     conn.execute("commit")
#     # noinspection SqlNoDataSourceInspection
#     conn.execute(f"CREATE DATABASE {DB_NAME}")

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db: Session = TestingSessionLocal()
        yield db
    finally:
        # noinspection PyUnboundLocalVariable
        db.close()


app.dependency_overrides[get_db] = override_get_db
