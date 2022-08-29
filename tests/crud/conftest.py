# import pytest
# from sqlalchemy import create_engine
# from sqlalchemy.exc import ProgrammingError, OperationalError
#
# from models.session import SessionLocal, Base
# from tests.conf_test_db import SQLALCHEMY_DATABASE_URL
#
# DB_NAME = "tests"
#
#
# # noinspection SqlNoDataSourceInspection
# def db_prep():
#     engine = create_engine(SQLALCHEMY_DATABASE_URL)
#     conn = engine.connect()
#     try:
#         conn = conn.execution_options(autocommit=False)
#         conn.execute("ROLLBACK")
#         conn.execute(f"DROP DATABASE {DB_NAME}")
#     except ProgrammingError:
#         print("Could not drop the database, probably does not exist.")
#         conn.execute("ROLLBACK")
#     except OperationalError:
#         print(
#             "Could not drop database because it’s being accessed by other users (psql prompt open?)"
#         )
#         conn.execute("ROLLBACK")
#     print("test db dropped! about to create test")
#     conn.execute(f"CREATE DATABASE {DB_NAME}")
#     conn.close()
#     print("test db created")
#
#
# @pytest.fixture(scope="session", autouse=True)
# def test_db():
#     # db_prep()
#     print(f"initializing {DB_NAME}…")
#     engine = create_engine(SQLALCHEMY_DATABASE_URL)
#     db = SessionLocal()
#     Base.metadata.create_all(engine)
#     print(f"{DB_NAME} ready to rock!")
#     try:
#         yield db
#     finally:
#         db.close()
