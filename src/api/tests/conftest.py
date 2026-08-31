from unittest.mock import create_autospec

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.core.api_settings import ApiSettings, get_api_settings
from api.dependencies import get_kafka_producer
from api.routers.telemetry import router


@pytest.fixture
def settings():
    return create_autospec(ApiSettings, instance=True)


@pytest.fixture
def app(producer, settings):
    app = FastAPI()
    app.include_router(router)

    app.dependency_overrides[get_kafka_producer] = lambda: producer
    app.dependency_overrides[get_api_settings] = lambda: settings

    yield app

    app.dependency_overrides.clear()


@pytest.fixture
def client(app):
    with TestClient(app) as client:
        yield client
