import logging
from typing import Generator
from sqlmodel import Session, SQLModel, create_engine
from app.core.config import settings

logger = logging.getLogger(__name__)
db_url = settings.DB_URL
connect_args = {}

if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(db_url, echo=False, connect_args=connect_args)


def init_db() -> None:
    import app.models  # noqa: F401
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine, expire_on_commit=False) as session:
        yield session
