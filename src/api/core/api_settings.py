from dataclasses import dataclass
from functools import lru_cache

from decouple import config


@dataclass(frozen=True, slots=True)
class ApiSettings:
    app_name: str = config('APP_NAME', default='telemetry-intake-service')
    app_version: str = config('APP_VERSION', default='0.1.0')
    debug: bool = config('DEBUG', default=False, cast=bool)
    api_prefix: str = config('API_PREFIX', default='/api')


@lru_cache(maxsize=1)
def get_api_settings() -> ApiSettings:
    return ApiSettings()
