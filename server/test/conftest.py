"""Pytest configuration and fixtures."""
from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from src.app import create_app
from src.config import AppConfig
from src.models import db

if TYPE_CHECKING:
    from collections.abc import Iterator

    from flask import Flask
    from flask.testing import FlaskClient, FlaskCliRunner


@pytest.fixture(scope="session")
def config() -> AppConfig:
    return AppConfig(
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SECRET_KEY="test_secret",
    )


@pytest.fixture
def app(config: AppConfig) -> Iterator[Flask]:
    """Create application for testing."""
    app_ = create_app(config)
    app_.config["TESTING"] = True
    with app_.app_context():
        db.create_all()
        yield app_
        db.drop_all()


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Create test client."""
    return app.test_client()


@pytest.fixture
def runner(app: Flask) -> FlaskCliRunner:
    """Create test CLI runner."""
    return app.test_cli_runner()
