from collections.abc import AsyncGenerator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


def get_session_factory(request: Request) -> async_sessionmaker[AsyncSession]:
    return request.app.state.db_session_factory


async def get_db(request: Request) -> AsyncGenerator[AsyncSession, None]:
    session_factory = get_session_factory(request)

    async with session_factory() as session:
        yield session
