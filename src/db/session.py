from sqlalchemy import URL, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from db import DBSettings


def create_async_db_engine(settings: DBSettings) -> AsyncEngine:
    database_url = URL.create(
        drivername='postgresql+asyncpg',
        username=settings.db_user,
        password=settings.db_password,
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name,
    )

    return create_async_engine(
        database_url,
        connect_args={
            'server_settings': {
                'statement_timeout': str(settings.db_statement_timeout_ms),
            }
        },
    )


def create_sync_db_engine(settings: DBSettings) -> Engine:
    database_url = URL.create(
        drivername='postgresql+psycopg2',
        username=settings.db_user,
        password=settings.db_password,
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name,
    )

    return create_engine(
        database_url,
        connect_args={
            'options': f'-c statement_timeout={settings.db_statement_timeout_ms}'
        },
        pool_pre_ping=True,
    )


def create_async_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )


def create_sync_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(
        bind=engine,
        class_=Session,
        expire_on_commit=False,
        autoflush=False,
    )
