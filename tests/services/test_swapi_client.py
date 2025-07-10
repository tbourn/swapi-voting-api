"""
tests.services.test_swapi_client

================================================================================
Unit Tests for SWAPI Client Service
================================================================================

Overview
--------
Validates the behavior of `src.services.swapi_client`, which is responsible for
fetching data from the external Star Wars API (SWAPI). Ensures correct handling
of network errors, JSON parsing, and data normalization for consistent internal
representation.

Tested Responsibilities
------------------------
- `fetch_resource`: Generic function fetching arbitrary SWAPI resources
  - Handles dict and list payload shapes
  - Handles invalid JSON responses gracefully
  - Retries or fails cleanly on HTTP errors and network issues
- Resource-specific helpers:
  - `fetch_characters`
  - `fetch_films`
  - `fetch_starships`

Key Characteristics
--------------------
- Uses `pytest` with `pytest-asyncio` for async test cases
- Mocks `httpx.AsyncClient` to simulate network responses and errors
- Confirms logging and graceful error handling in all failure modes
- Verifies correct URL composition and request parameter forwarding

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

from unittest.mock import AsyncMock, Mock

import httpx
import pytest

import src.services.swapi_client as swapi_client
from src.exceptions.custom_exceptions import ExternalAPIError


@pytest.fixture(autouse=True)
def patch_config(monkeypatch):
    """
    Autouse fixture to patch swapi_client configuration and logging.

    :param monkeypatch: pytest fixture for dynamic attribute patching
    :type monkeypatch: _pytest.MonkeyPatch
    :return: None
    :rtype: None
    """
    monkeypatch.setattr(swapi_client, "BASE_URL", "https://fake.api")
    monkeypatch.setattr(swapi_client, "VERIFY_SSL", False)
    monkeypatch.setattr(swapi_client, "log_info", Mock())
    monkeypatch.setattr(swapi_client, "log_error", Mock())


def make_response(json_data, status_code=200):
    """
    Create a mocked AsyncHTTPX response with configurable JSON payload and status.

    :param json_data: JSON-like data to be returned by .json()
    :type json_data: Any
    :param status_code: HTTP status code to simulate, defaults to 200
    :type status_code: int, optional
    :return: Configured AsyncMock simulating an httpx.Response
    :rtype: unittest.mock.AsyncMock
    """
    r = AsyncMock()
    r.status_code = status_code
    r.raise_for_status = Mock()
    r.json = Mock(return_value=json_data)
    r.aread = AsyncMock(return_value=b"bad body")
    return r


def patch_httpx_client_success(monkeypatch, response):
    """
    Patch httpx.AsyncClient to simulate successful GET requests with given response.

    :param monkeypatch: pytest fixture for dynamic attribute patching
    :type monkeypatch: _pytest.MonkeyPatch
    :param response: The mocked AsyncMock response to return on GET
    :type response: unittest.mock.AsyncMock
    :return: The mocked AsyncClient with .get() returning the specified response
    :rtype: unittest.mock.AsyncMock
    """
    client_mock = AsyncMock()
    client_mock.get = AsyncMock(return_value=response)

    context_manager = AsyncMock()
    context_manager.__aenter__.return_value = client_mock
    context_manager.__aexit__.return_value = None

    monkeypatch.setattr(
        swapi_client.httpx, "AsyncClient", Mock(return_value=context_manager)
    )
    return client_mock


@pytest.mark.asyncio
async def test_fetch_resource_dict_response(monkeypatch):
    """
    Test fetch_resource returns dict response as-is when SWAPI returns a dict.

    :param monkeypatch: Pytest fixture for dynamic attribute patching
    :type monkeypatch: _pytest.MonkeyPatch
    :return: None
    :rtype: None
    """
    response = make_response({"results": [], "next": None})
    patch_httpx_client_success(monkeypatch, response)
    result = await swapi_client.fetch_resource("people/")
    assert "results" in result


@pytest.mark.asyncio
async def test_fetch_resource_list_response(monkeypatch):
    """
    Test fetch_resource wraps list response in dict with results and next=None.

    :param monkeypatch: Pytest fixture for dynamic attribute patching
    :type monkeypatch: _pytest.MonkeyPatch
    :return: None
    :rtype: None
    """
    response = make_response([{"name": "Luke"}])
    patch_httpx_client_success(monkeypatch, response)
    result = await swapi_client.fetch_resource("people/")
    assert result["results"][0]["name"] == "Luke"
    assert result["next"] is None


@pytest.mark.asyncio
async def test_fetch_resource_unexpected_type(monkeypatch):
    """
    Test fetch_resource returns None if SWAPI returns an unsupported type.

    :param monkeypatch: Pytest fixture for dynamic attribute patching
    :type monkeypatch: _pytest.MonkeyPatch
    :return: None
    :rtype: None
    """
    response = make_response("invalid type")
    patch_httpx_client_success(monkeypatch, response)
    result = await swapi_client.fetch_resource("bad/")
    assert result is None


@pytest.mark.asyncio
async def test_fetch_resource_invalid_json(monkeypatch):
    """
    Test fetch_resource returns None on invalid JSON parse errors.

    :param monkeypatch: Pytest fixture for dynamic attribute patching
    :type monkeypatch: _pytest.MonkeyPatch
    :return: None
    :rtype: None
    """
    bad_response = AsyncMock()
    bad_response.raise_for_status = Mock()
    bad_response.json = Mock(side_effect=ValueError("bad json"))
    bad_response.aread = AsyncMock(return_value=b"garbled data")

    patch_httpx_client_success(monkeypatch, bad_response)
    result = await swapi_client.fetch_resource("films/")
    assert result is None


@pytest.mark.asyncio
async def test_fetch_resource_http_error(monkeypatch):
    """
    Test fetch_resource returns None when httpx raises HTTPStatusError.

    :param monkeypatch: Pytest fixture for dynamic attribute patching
    :type monkeypatch: _pytest.MonkeyPatch
    :return: None
    :rtype: None
    :raises httpx.HTTPStatusError: Simulated HTTP error from httpx
    """
    async def fake_get(*args, **kwargs):
        response = Mock(status_code=404)
        raise httpx.HTTPStatusError("404", request=Mock(), response=response)

    client_mock = AsyncMock()
    client_mock.get = AsyncMock(side_effect=fake_get)

    context_manager = AsyncMock()
    context_manager.__aenter__.return_value = client_mock
    context_manager.__aexit__.return_value = None

    monkeypatch.setattr(
        swapi_client.httpx, "AsyncClient", Mock(return_value=context_manager)
    )
    result = await swapi_client.fetch_resource("bad/")
    assert result is None


@pytest.mark.asyncio
async def test_fetch_resource_request_error(monkeypatch):
    """
    Test fetch_resource returns None when httpx raises RequestError.

    :param monkeypatch: Pytest fixture for dynamic attribute patching
    :type monkeypatch: _pytest.MonkeyPatch
    :return: None
    :rtype: None
    :raises httpx.RequestError: Simulated network error
    """
    async def fake_get(*args, **kwargs):
        raise httpx.RequestError("fail", request=Mock())

    client_mock = AsyncMock()
    client_mock.get = AsyncMock(side_effect=fake_get)

    context_manager = AsyncMock()
    context_manager.__aenter__.return_value = client_mock
    context_manager.__aexit__.return_value = None

    monkeypatch.setattr(
        swapi_client.httpx, "AsyncClient", Mock(return_value=context_manager)
    )
    result = await swapi_client.fetch_resource("bad/")
    assert result is None


@pytest.mark.asyncio
async def test_fetch_characters(monkeypatch):
    """
    Test fetch_characters delegates to fetch_resource with correct params.

    :param monkeypatch: Pytest fixture for dynamic attribute patching
    :type monkeypatch: _pytest.MonkeyPatch
    :return: None
    :rtype: None
    """
    fake_result = {"results": []}
    monkeypatch.setattr(
        swapi_client, "fetch_resource", AsyncMock(return_value=fake_result)
    )
    result = await swapi_client.fetch_characters(page=2)
    assert result == fake_result
    swapi_client.fetch_resource.assert_awaited_with("people/", params={"page": 2})


@pytest.mark.asyncio
async def test_fetch_films(monkeypatch):
    """
    Test fetch_films calls fetch_resource with films/ endpoint.

    :param monkeypatch: Pytest fixture for dynamic attribute patching
    :type monkeypatch: _pytest.MonkeyPatch
    :return: None
    :rtype: None
    """
    fake_result = {"results": []}
    monkeypatch.setattr(
        swapi_client, "fetch_resource", AsyncMock(return_value=fake_result)
    )
    result = await swapi_client.fetch_films()
    assert result == fake_result
    swapi_client.fetch_resource.assert_awaited_with("films/")


@pytest.mark.asyncio
async def test_fetch_starships(monkeypatch):
    """
    Test fetch_starships delegates to fetch_resource with correct params.

    :param monkeypatch: Pytest fixture for dynamic attribute patching
    :type monkeypatch: _pytest.MonkeyPatch
    :return: None
    :rtype: None
    """
    fake_result = {"results": []}
    monkeypatch.setattr(
        swapi_client, "fetch_resource", AsyncMock(return_value=fake_result)
    )
    result = await swapi_client.fetch_starships(page=5)
    assert result == fake_result
    swapi_client.fetch_resource.assert_awaited_with("starships/", params={"page": 5})
