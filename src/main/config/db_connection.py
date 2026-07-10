from typing import Any, AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from .settings import settings


async def get_engine() -> AsyncEngine:
    engine = create_async_engine(settings.DATABASE_URL)
    return engine


async def get_session() -> AsyncGenerator[AsyncSession, Any]:
    engine = await get_engine()

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session
