import contextlib
import os

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

load_dotenv()

DeclarativeBase = declarative_base()

DB_ENGINE = os.getenv("DB_ENGINE")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")

url_object = URL.create(
    DB_ENGINE,
    username=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    host=DB_HOST,
    database=POSTGRES_DB,
    port=POSTGRES_PORT,
    query={"gssencmode": "disable"},
)

engine = create_engine(url_object)
Session = scoped_session(sessionmaker(bind=engine, expire_on_commit=False))


@contextlib.contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
