"""
tests.utils.test_retry_util

================================================================================
Unit Tests for retry_with_backoff Utility Decorator
================================================================================

Overview
--------
Tests the `retry_with_backoff` decorator in `src.utils.retry_util`, ensuring that
it correctly implements both synchronous and asynchronous retry logic with
exponential backoff, logging, and error handling. Verifies that network-style
errors trigger retries while other exceptions fail immediately.

Tested Responsibilities
------------------------
- Correct execution without retry when calls succeed
- Retrying on network-like exceptions with backoff and logging
- Immediate failure handling for non-network exceptions
- Proper logging via log_warning and log_error
- Compatibility with both async and sync functions

Key Characteristics
--------------------
- Uses pytest-asyncio for async test cases
- Employs unittest.mock to intercept and verify logging and sleep calls
- Confirms that backoff sleeps are correctly awaited or called
- Ensures predictable retry count and logging behavior

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

import asyncio
from unittest import mock

import pytest

from src.utils.retry_util import retry_with_backoff


@pytest.mark.asyncio
async def test_async_success():
    """
    Test that an async function decorated with retry_with_backoff
    returns normally without retries if no exception is raised.

    :return: Ensures the decorated async function returns expected result
    :rtype: None
    """
    @retry_with_backoff()
    async def ok():
        return "yay"

    assert await ok() == "yay"


@pytest.mark.asyncio
async def test_async_network_retries(monkeypatch):
    """
    Test that async function retries on network-style exceptions with backoff.

    :param monkeypatch: Pytest fixture for dynamic attribute patching
    :type monkeypatch: _pytest.MonkeyPatch
    :return: Asserts correct retry count, backoff sleeps, and logging
    :rtype: None
    """
    warn = mock.Mock()
    err = mock.Mock()
    sleep = mock.AsyncMock()

    monkeypatch.setattr("src.utils.retry_util.log_warning", warn)
    monkeypatch.setattr("src.utils.retry_util.log_error", err)
    monkeypatch.setattr("asyncio.sleep", sleep)

    @retry_with_backoff(retries=3)
    async def flaky():
        raise TimeoutError("fail")

    result = await flaky()
    assert result is None
    assert warn.call_count == 2
    assert err.call_count == 1
    sleep.assert_awaited()


@pytest.mark.asyncio
async def test_async_other_exception(monkeypatch):
    """
    Test that non-network exceptions in async functions fail immediately without retry.

    :param monkeypatch: Pytest fixture for patching
    :type monkeypatch: _pytest.MonkeyPatch
    :return: Asserts immediate failure and logging
    :rtype: None
    """
    err = mock.Mock()
    monkeypatch.setattr("src.utils.retry_util.log_error", err)

    @retry_with_backoff()
    async def bad():
        raise ValueError("bad")

    result = await bad()
    assert result is None
    err.assert_called()


def test_sync_success():
    """
    Test that sync function decorated with retry_with_backoff
    returns normally without retries if no exception is raised.

    :return: Ensures decorated sync function returns expected result
    :rtype: None
    """
    @retry_with_backoff()
    def ok():
        return 42

    assert ok() == 42


def test_sync_network_retries(monkeypatch):
    """
    Test that sync function retries on network-style exceptions with backoff.

    :param monkeypatch: Pytest fixture for dynamic patching
    :type monkeypatch: _pytest.MonkeyPatch
    :return: Asserts retry count, backoff sleeps, and logging calls
    :rtype: None
    """
    warn = mock.Mock()
    err = mock.Mock()
    sleep = mock.Mock()

    monkeypatch.setattr("src.utils.retry_util.log_warning", warn)
    monkeypatch.setattr("src.utils.retry_util.log_error", err)
    monkeypatch.setattr("time.sleep", sleep)

    calls = {"count": 0}

    @retry_with_backoff(retries=3)
    def flaky():
        calls["count"] += 1
        raise ConnectionError("fail")

    result = flaky()
    assert result is None
    assert calls["count"] == 3
    assert warn.call_count == 2
    assert err.call_count == 1
    sleep.assert_called()


def test_sync_other_exception(monkeypatch):
    """
    Test that non-network exceptions in sync functions fail immediately without retry.

    :param monkeypatch: Pytest fixture for dynamic patching
    :type monkeypatch: _pytest.MonkeyPatch
    :return: Asserts immediate failure and error logging
    :rtype: None
    """
    err = mock.Mock()
    monkeypatch.setattr("src.utils.retry_util.log_error", err)

    @retry_with_backoff()
    def bad():
        raise ValueError("boom")

    result = bad()
    assert result is None
    err.assert_called()
