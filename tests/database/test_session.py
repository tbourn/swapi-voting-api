"""
tests.database.test_session

================================================================================
Unit Tests for Database Session Management
================================================================================

Overview
--------
Tests the configuration and utility logic in `src.database.session`, which
handles SQLAlchemy async session creation, URL rewriting for sqlite support,
and dependency-injected session generators for FastAPI.

Tested Responsibilities
------------------------
- `get_db` dependency yields an AsyncSession-compatible object
- ASYNC_DATABASE_URL rewriting from `sqlite://` to `sqlite+aiosqlite://`
- ASYNC_DATABASE_URL preservation for non-sqlite databases
- Ensures SQLAlchemy async engine is initialized with correct parameters

Key Characteristics
--------------------
- Supports dynamic configuration via environment variables
- Enables FastAPI DI for request-scoped async sessions
- Provides database-agnostic connection logic with sqlite compatibility

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

import importlib
from unittest import mock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_get_db_yields_asyncsession(mocker):
    """
    Tests that the get_db dependency yields an AsyncSession-compatible object.

    :param mocker: pytest-mock fixture to patch async_session
    :type mocker: pytest_mock.plugin.MockerFixture
    :raises AssertionError: If yielded object is not the expected AsyncSession
    :return: None
    :rtype: None
    """
    fake_session = mock.AsyncMock(spec=AsyncSession)
    fake_context_manager = mock.AsyncMock()
    fake_context_manager.__aenter__.return_value = fake_session
    fake_context_manager.__aexit__.return_value = None

    mocker.patch(
        "src.database.session.async_session", return_value=fake_context_manager
    )

    from src.database import session

    gen = session.get_db()
    result = await anext(gen)
    assert result == fake_session


def test_sqlite_url_rewriting(monkeypatch, mocker):
    """
    Tests that ASYNC_DATABASE_URL is correctly rewritten for sqlite URLs.

    :param monkeypatch: Pytest fixture to patch environment variable access
    :type monkeypatch: _pytest.monkeypatch.MonkeyPatch
    :param mocker: pytest-mock fixture to patch SQLAlchemy engine creation
    :type mocker: pytest_mock.plugin.MockerFixture
    :raises AssertionError: If URL rewriting or engine call is incorrect
    :return: None
    :rtype: None
    """
    monkeypatch.setattr(
        "src.config.env.get_app_config", lambda: {"DATABASE_URL": "sqlite:///test.db"}
    )
    mock_create_engine = mocker.patch("sqlalchemy.ext.asyncio.create_async_engine")

    import importlib

    session_module = importlib.import_module("src.database.session")
    importlib.reload(session_module)

    assert session_module.ASYNC_DATABASE_URL == "sqlite+aiosqlite:///test.db"
    mock_create_engine.assert_called_once()


def test_non_sqlite_url(monkeypatch, mocker):
    """
    Tests that ASYNC_DATABASE_URL remains unchanged for non-sqlite URLs.

    :param monkeypatch: Pytest fixture to patch environment variable access
    :type monkeypatch: _pytest.monkeypatch.MonkeyPatch
    :param mocker: pytest-mock fixture to patch SQLAlchemy engine creation
    :type mocker: pytest_mock.plugin.MockerFixture
    :raises AssertionError: If URL rewriting or engine call is incorrect
    :return: None
    :rtype: None
    """
    monkeypatch.setattr(
        "src.config.env.get_app_config",
        lambda: {"DATABASE_URL": "postgresql+asyncpg://user:pass@localhost/db"},
    )
    mock_create_engine = mocker.patch("sqlalchemy.ext.asyncio.create_async_engine")

    import importlib

    session_module = importlib.import_module("src.database.session")
    importlib.reload(session_module)

    assert (
        session_module.ASYNC_DATABASE_URL
        == "postgresql+asyncpg://user:pass@localhost/db"
    )
    mock_create_engine.assert_called_once()
