import uuid
from contextlib import contextmanager
from datetime import datetime
from typing import Any, AsyncGenerator, Generator
from uuid import UUID

import pytest
import pytest_asyncio
import redis.asyncio as redis
from redis.asyncio import Redis
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, AsyncTransaction, create_async_engine
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import AsyncRedisContainer

from src.common.infra.entities import table_registry


@pytest_asyncio.fixture(scope="session")
async def engine() -> AsyncGenerator[AsyncEngine, Any]:
    with PostgresContainer('postgres:18', driver='psycopg') as postgres:
        engine = create_async_engine(postgres.get_connection_url())

        async with engine.begin() as connection:
            await connection.run_sync(table_registry.metadata.create_all)

        yield engine

        async with engine.begin() as connection:
            await connection.run_sync(table_registry.metadata.drop_all)


@pytest_asyncio.fixture
async def session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, Any]:
    async with engine.connect() as connection:
        test_transaction = await connection.begin()

        async with AsyncSession(bind=connection, expire_on_commit=False) as session:
            await session.begin_nested()

            @event.listens_for(session.sync_session, 'after_transaction_end')
            def end_savepoint(session: AsyncSession, transaction: AsyncTransaction):
                if not session.in_nested_transaction():
                    session.begin_nested()

            yield session

        await test_transaction.rollback()


@pytest_asyncio.fixture(scope="session")
async def redis_container() -> AsyncGenerator[AsyncRedisContainer, Any]:
    with AsyncRedisContainer(image='redis:8.6-alpine', port_to_expose=6379) as container:
        container.get_container_host_ip()

        yield container


@pytest_asyncio.fixture
async def redis_client(redis_container: AsyncRedisContainer) -> AsyncGenerator[Redis, Any]:
    client = redis.Redis(
        host=redis_container.get_container_host_ip(), port=redis_container.get_exposed_port(6379), decode_responses=True
    )

    yield client

    client.flushall()


@contextmanager
def _mock_db_fields(*, model, id=uuid.uuid7(), time=datetime.now()) -> Generator[tuple[UUID, datetime], Any, None]:
    def fake_time_hook(mapper, connection, target):
        if hasattr(target, 'id'):
            target.id = id

        if hasattr(target, 'created_at'):
            target.created_at = time

        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(model, 'before_insert', fake_time_hook)

    yield id, time

    event.remove(model, 'before_insert', fake_time_hook)


@pytest.fixture
def mock_db_fields():
    return _mock_db_fields
