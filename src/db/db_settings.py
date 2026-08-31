from dataclasses import dataclass
from functools import lru_cache

from decouple import config


@dataclass(slots=True)
class DBSettings:
    db_host: str = config('DB_HOST', default='postgres')
    db_port: int = config('DB_PORT', default=5432, cast=int)
    db_name: str = config('DB_NAME')
    db_user: str = config('DB_USER')
    db_password: str = config('DB_PASSWORD')
    db_statement_timeout_ms: int = config(
        'DB_STATEMENT_TIMEOUT_MS',
        default=5000,
        cast=int,
    )


@lru_cache(maxsize=1)
def get_db_settings() -> DBSettings:
    return DBSettings()
