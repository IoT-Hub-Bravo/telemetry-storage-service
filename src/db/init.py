import asyncio
import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from db import Base, get_db_settings, create_async_db_engine
from utils.logging import setup_logging

logger = logging.getLogger(__name__)


async def init_db(engine: AsyncEngine) -> None:
    import db.models  # noqa

    async with engine.begin() as conn:
        # check TimescaleDB extension availability & status
        result = await conn.execute(text(
            """
            SELECT 1
            FROM pg_available_extensions
            WHERE name = 'timescaledb'
            """
        ))
        if result.scalar() is None:
            raise RuntimeError(
                'TimescaleDB extension is not available in this PostgreSQL instance.'
            )

        # create TimescaleDB extension
        await conn.execute(text('CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE'))
        logger.info('TimescaleDB available.')

        # create tables
        await conn.run_sync(Base.metadata.create_all)
        logger.info('DB tables created.')

        # create telemetries hypertable
        await conn.execute(text(
            """
            SELECT create_hypertable(
                'telemetries',
                by_range('ts', INTERVAL '7 days'),
                if_not_exists => TRUE,
                migrate_data => TRUE,
                create_default_indexes => TRUE
            )
            """
        ))
        logger.info('telemetries hypertable created.')

        # enable compression
        await conn.execute(text(
            """
            ALTER TABLE telemetries
                SET (
                    timescaledb.compress,
                    timescaledb.compress_segmentby = 'device_metric_id',
                    timescaledb.compress_orderby = 'ts DESC'
                    )
            """
        ))
        logger.info('telemetries compression enabled.')

        # add compression policy
        await conn.execute(text(
            """
            SELECT add_compression_policy(
                'telemetries',
                compress_after => INTERVAL '30 days',
                if_not_exists => TRUE
            )
            """
        ))
        logger.info('telemetries compression policy added.')

        # add retention policy
        await conn.execute(text(
            """
            SELECT add_retention_policy(
                'telemetries',
                drop_after => INTERVAL '1 year',
                if_not_exists => TRUE
            )
            """
        ))
        logger.info('telemetries retention policy added.')


async def main() -> None:
    setup_logging()
    settings = get_db_settings()
    engine = create_async_db_engine(settings)

    try:
        await init_db(engine)
    finally:
        await engine.dispose()


if __name__ == '__main__':
    asyncio.run(main())
