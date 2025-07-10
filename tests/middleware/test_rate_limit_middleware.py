"""
tests.middleware.test_rate_limit_middleware

================================================================================
Unit Tests for RateLimitAndBlocklistMiddleware
================================================================================

Overview
--------
Validates the behavior of the custom FastAPI middleware defined in
`src.middleware.rate_limit_middleware`. This middleware enforces both IP
blocklisting and per-IP rate limiting using Redis-backed counters.

Tested Responsibilities
------------------------
- Returns 403 Forbidden for blocked IPs with an ACCESS_DENIED error payload
- Returns 429 Too Many Requests when rate limit is exceeded with RATE_LIMIT_EXCEEDED
- Allows requests to pass through to the next handler when under limit
- Gracefully handles cases where client IP is missing from the request object

Key Characteristics
--------------------
- Uses FastAPI's middleware dispatch lifecycle for realistic test flow
- Mocks Redis rate limit and blocklist checks to control test scenarios
- Validates JSON error responses for API clients
- Ensures correct bypass behavior when limits are not exceeded

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

import json
from unittest import mock

import pytest
from fastapi import Request
from starlette.responses import Response

from src.middleware.rate_limit_middleware import RateLimitAndBlocklistMiddleware


class FakeClient:
    """
    Simple mock client representation for testing FastAPI Request objects.

    :param host: The simulated client IP address
    :type host: str
    """
    def __init__(self, host):
        self.host = host


@pytest.mark.asyncio
async def test_blocked_ip_returns_403(mocker):
    """
    Tests that requests from blocked IPs return 403 Forbidden with ACCESS_DENIED error.

    :param mocker: pytest-mock fixture to patch blocklist and rate functions
    :type mocker: pytest_mock.plugin.MockerFixture
    :raises AssertionError: If response or calls do not match expectations
    :return: None
    :rtype: None
    """
    mocker.patch(
        "src.middleware.rate_limit_middleware.is_blocked_ip", return_value=True
    )
    mock_increment = mocker.patch("src.middleware.rate_limit_middleware.increment_rate")

    call_next = mock.AsyncMock()
    app = mock.Mock()
    middleware = RateLimitAndBlocklistMiddleware(app)

    request = mock.Mock(spec=Request)
    request.client = FakeClient("1.2.3.4")

    response = await middleware.dispatch(request, call_next)

    assert response.status_code == 403
    parsed = json.loads(response.body)
    assert parsed["error"] == "ACCESS_DENIED"

    mock_increment.assert_not_called()
    call_next.assert_not_called()


@pytest.mark.asyncio
async def test_rate_limit_exceeded_returns_429(mocker):
    """
    Tests that exceeding rate limit returns 429 Too Many Requests with RATE_LIMIT_EXCEEDED error.

    :param mocker: pytest-mock fixture to patch blocklist and rate functions
    :type mocker: pytest_mock.plugin.MockerFixture
    :raises AssertionError: If response or calls do not match expectations
    :return: None
    :rtype: None
    """
    mocker.patch(
        "src.middleware.rate_limit_middleware.is_blocked_ip", return_value=False
    )
    mocker.patch(
        "src.middleware.rate_limit_middleware.increment_rate", return_value=101
    )

    call_next = mock.AsyncMock()
    app = mock.Mock()
    middleware = RateLimitAndBlocklistMiddleware(
        app, max_requests=100, window_seconds=3600
    )

    request = mock.Mock(spec=Request)
    request.client = FakeClient("5.6.7.8")

    response = await middleware.dispatch(request, call_next)

    assert response.status_code == 429
    parsed = json.loads(response.body)
    assert parsed["error"] == "RATE_LIMIT_EXCEEDED"

    call_next.assert_not_called()


@pytest.mark.asyncio
async def test_allows_request_when_under_limit(mocker):
    """
    Tests that requests under the rate limit pass through to the next handler.

    :param mocker: pytest-mock fixture to patch blocklist and rate functions
    :type mocker: pytest_mock.plugin.MockerFixture
    :raises AssertionError: If call_next is not invoked correctly or response mismatches
    :return: None
    :rtype: None
    """
    mocker.patch(
        "src.middleware.rate_limit_middleware.is_blocked_ip", return_value=False
    )
    mocker.patch("src.middleware.rate_limit_middleware.increment_rate", return_value=10)

    expected_response = Response(content=b"ok", status_code=200)
    call_next = mock.AsyncMock(return_value=expected_response)

    app = mock.Mock()
    middleware = RateLimitAndBlocklistMiddleware(
        app, max_requests=100, window_seconds=3600
    )

    request = mock.Mock(spec=Request)
    request.client = FakeClient("9.9.9.9")

    response = await middleware.dispatch(request, call_next)

    assert response == expected_response
    call_next.assert_awaited_once_with(request)


@pytest.mark.asyncio
async def test_unknown_ip_field(mocker):
    """
    Tests that requests with no client IP field still pass through safely.

    :param mocker: pytest-mock fixture to patch blocklist and rate functions
    :type mocker: pytest_mock.plugin.MockerFixture
    :raises AssertionError: If response status is incorrect
    :return: None
    :rtype: None
    """
    mocker.patch(
        "src.middleware.rate_limit_middleware.is_blocked_ip", return_value=False
    )
    mocker.patch("src.middleware.rate_limit_middleware.increment_rate", return_value=5)

    call_next = mock.AsyncMock(return_value=Response(content=b"ok"))

    app = mock.Mock()
    middleware = RateLimitAndBlocklistMiddleware(app)

    request = mock.Mock(spec=Request)
    request.client = None

    response = await middleware.dispatch(request, call_next)
    assert response.status_code == 200
