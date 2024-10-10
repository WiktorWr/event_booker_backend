import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from httpx import ASGITransport, AsyncClient
import pytest_asyncio

from app.main import app
from app.database.model import Base
from app.database.config import settings
from app.tests.factories import setup_factories

TEST_DB_NAME = f"{settings.DATABASE_NAME}_test"

DATABASE_URL = "postgresql+psycopg2://{user}:{password}@{host}:{port}".format(
    user=settings.DATABASE_USER,
    password=settings.DATABASE_PASSWORD,
    host=settings.DATABASE_HOST,
    port=settings.DATABASE_PORT,
)


@pytest.fixture(scope="session")
def create_test_database():
    engine = create_engine(
        DATABASE_URL,
        isolation_level="AUTOCOMMIT",
    )
    with engine.connect() as connection:
        connection.execute(text(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}"))
        connection.execute(text(f"CREATE DATABASE {TEST_DB_NAME}"))
    engine.dispose()


@pytest.fixture(scope="session")
def database_engine(create_test_database):
    return create_engine(f"{DATABASE_URL}/{TEST_DB_NAME}")


@pytest.fixture(scope="session")
def connection(database_engine):
    with database_engine.connect() as connection:
        with connection.begin():
            Base.metadata.create_all(connection)

        yield connection
    connection.close()


@pytest.fixture
def db_session(connection):
    transaction = connection.begin()
    session_factory = sessionmaker(bind=connection)

    session = session_factory()
    setup_factories(session)
    yield session
    transaction.rollback()


@pytest_asyncio.fixture
async def async_client(db_session):
    from app import main
    from app.database.dependencies import get_db

    main.app.dependency_overrides[get_db] = lambda: db_session

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
