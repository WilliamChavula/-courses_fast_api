from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from core.settings import Settings

POSTGRES_USER = Settings.POSTGRES_USER
POSTGRES_PWD = Settings.POSTGRES_PWD
POSTGRES_DB_NAME = Settings.POSTGRES_DB_NAME
PORT = Settings.PORT
IP_ADDR = Settings.IP_ADDR

__CONNECTION_URI = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PWD}@{IP_ADDR}:{PORT}/{POSTGRES_DB_NAME}"
)

engine = create_engine(__CONNECTION_URI)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
