import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PWD = os.getenv("POSTGRES_PWD")
    POSTGRES_DB_NAME = os.getenv("POSTGRES_DB_NAME")
    PORT = os.getenv("PORT")
    IP_ADDR = os.getenv("IP_ADDR")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")
