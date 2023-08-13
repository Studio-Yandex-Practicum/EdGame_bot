import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import URL
from dotenv import load_dotenv

load_dotenv()

DeclarativeBase = declarative_base()

DB_ENGINE = os.getenv('DB_ENGINE')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
POSTGRES_DB = os.getenv('POSTGRES_DB')

url_object = URL.create(
    DB_ENGINE,
    username=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    host=DB_HOST,
    database=POSTGRES_DB,
)


def engine():
    engine = create_engine(url_object)
    return engine
