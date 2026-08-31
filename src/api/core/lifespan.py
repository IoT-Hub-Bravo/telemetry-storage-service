from contextlib import asynccontextmanager

from fastapi import FastAPI

from db import (
    get_db_settings,
    create_async_db_engine,
    create_async_session_factory,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_settings = get_db_settings()

    engine = create_async_db_engine(db_settings)
    session_factory = create_async_session_factory(engine)

    app.state.db_engine = engine
    app.state.db_session_factory = session_factory

    try:
        yield
    finally:
        await engine.dispose()
