"""
tests.api.test_routes

================================================================================
Async Integration Tests for FastAPI API Routes
================================================================================

Overview
--------
Validates the HTTP API endpoints exposed by the SWAPI Voting API FastAPI app.
Uses httpx's ASGITransport and AsyncClient to test the live ASGI app in-memory
without spinning up a real server.

Tested Responsibilities
------------------------
- Import endpoints for characters, films, and starships (happy path and error handling)
- CRUD listing, search, and get-by-ID endpoints for Characters
- CRUD listing, search, and get-by-ID endpoints for Films
- CRUD listing, search, and get-by-ID endpoints for Starships
- Proper status codes and JSON responses for successful and failure scenarios

Key Characteristics
--------------------
- Fully async test suite with pytest-asyncio and pytest-asyncio.fixture
- Mocks backend service calls and database dependencies with pytest-mock
- Tests both success and error paths for complete coverage
- Validates consistent OpenAPI-compatible response structures

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

import httpx
import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from src.main import app

BASE_URL = "http://test"


@pytest_asyncio.fixture
async def async_client():
    """
    Async pytest fixture that provides an httpx.AsyncClient configured with ASGITransport
    for in-memory FastAPI testing without a live server.

    :return: Async test client connected to the FastAPI app
    :rtype: httpx.AsyncClient
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_import_characters_success(mocker, async_client):
    """
    Tests successful POST to /import/characters returning 202 Accepted.

    :param mocker: pytest-mock fixture to patch import logic
    :type mocker: pytest_mock.plugin.MockerFixture
    :param async_client: Async test client for FastAPI app
    :type async_client: httpx.AsyncClient
    :raises AssertionError: If response status or body is incorrect
    :return: None
    :rtype: None
    """
    mocker.patch("src.api.routes.import_characters_from_swapi", return_value=None)
    res = await async_client.post("/import/characters")
    assert res.status_code == 202
    assert res.json() == {"message": "Character import completed."}


@pytest.mark.asyncio
async def test_import_characters_failure(mocker, async_client):
    """
    Tests failed POST to /import/characters returning 502 Bad Gateway.

    :param mocker: pytest-mock fixture to simulate exception
    :type mocker: pytest_mock.plugin.MockerFixture
    :param async_client: Async test client for FastAPI app
    :type async_client: httpx.AsyncClient
    :raises AssertionError: If response does not match expected failure
    :return: None
    :rtype: None
    """
    mocker.patch(
        "src.api.routes.import_characters_from_swapi", side_effect=Exception("fail")
    )
    res = await async_client.post("/import/characters")
    assert res.status_code == 502


@pytest.mark.asyncio
async def test_import_films_success(mocker, async_client):
    """
    Tests successful POST to /import/films returning 202 Accepted.

    :param mocker: pytest-mock fixture to patch import logic
    :type mocker: pytest_mock.plugin.MockerFixture
    :param async_client: Async test client for FastAPI app
    :type async_client: httpx.AsyncClient
    :raises AssertionError: If response status is incorrect
    :return: None
    :rtype: None
    """
    mocker.patch("src.api.routes.import_films_from_swapi", return_value=None)
    res = await async_client.post("/import/films")
    assert res.status_code == 202


@pytest.mark.asyncio
async def test_import_starships_success(mocker, async_client):
    """
    Tests successful POST to /import/starships returning 202 Accepted.

    :param mocker: pytest-mock fixture to patch import logic
    :type mocker: pytest_mock.plugin.MockerFixture
    :param async_client: Async test client for FastAPI app
    :type async_client: httpx.AsyncClient
    :raises AssertionError: If response status is incorrect
    :return: None
    :rtype: None
    """
    mocker.patch("src.api.routes.import_starships_from_swapi", return_value=None)
    res = await async_client.post("/import/starships")
    assert res.status_code == 202


# -----------------------------
# Characters
# -----------------------------


@pytest.mark.asyncio
async def test_list_characters(mocker, async_client):
    """
    Tests GET /characters/ returning 200 with empty list.

    :param mocker: pytest-mock fixture to patch list_characters
    :type mocker: pytest_mock.plugin.MockerFixture
    :param async_client: Async FastAPI test client
    :type async_client: httpx.AsyncClient
    :raises AssertionError: On wrong status code
    :return: None
    :rtype: None
    """
    mocker.patch("src.api.routes.list_characters", return_value=[])
    res = await async_client.get("/characters/")
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_search_characters_found(mocker, async_client):
    """
    Tests GET /characters/search with match returning 200.

    :param mocker: pytest-mock fixture to patch search logic
    :type mocker: pytest_mock.plugin.MockerFixture
    :param async_client: Async FastAPI test client
    :type async_client: httpx.AsyncClient
    :raises AssertionError: On unexpected status
    :return: None
    :rtype: None
    """
    mocker.patch(
        "src.api.routes.search_characters_by_name",
        return_value=[{"id": 1, "name": "Luke"}],
    )
    res = await async_client.get("/characters/search?q=Luke")
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_search_characters_not_found(mocker, async_client):
    """
    Tests GET /characters/search with no match returning 404.

    :param mocker: pytest-mock fixture to patch search logic
    :type mocker: pytest_mock.plugin.MockerFixture
    :param async_client: Async FastAPI test client
    :type async_client: httpx.AsyncClient
    :raises AssertionError: On wrong status
    :return: None
    :rtype: None
    """
    mocker.patch("src.api.routes.search_characters_by_name", return_value=[])
    res = await async_client.get("/characters/search?q=none")
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_get_character_by_id_found(mocker, async_client):
    """
    Tests GET /characters/{id} returning 200 for existing character.

    :param mocker: pytest-mock fixture to patch get_character
    :type mocker: pytest_mock.plugin.MockerFixture
    :param async_client: Async FastAPI test client
    :type async_client: httpx.AsyncClient
    :raises AssertionError: On incorrect status
    :return: None
    :rtype: None
    """
    mocker.patch("src.api.routes.get_character", return_value={"id": 1, "name": "Luke"})
    res = await async_client.get("/characters/1")
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_get_character_by_id_not_found(mocker, async_client):
    """
    Tests GET /characters/{id} with non-existing ID returning 404.

    :param mocker: pytest-mock fixture to patch get_character
    :type mocker: pytest_mock.plugin.MockerFixture
    :param async_client: Async FastAPI test client
    :type async_client: httpx.AsyncClient
    :raises AssertionError: On wrong status
    :return: None
    :rtype: None
    """
    mocker.patch("src.api.routes.get_character", return_value=None)
    res = await async_client.get("/characters/999")
    assert res.status_code == 404


# -----------------------------
# Films
# -----------------------------


@pytest.mark.asyncio
async def test_list_films(mocker, async_client):
    """
    Tests GET /films/ returning 200 with empty list.

    :param mocker: pytest-mock fixture to patch list_films
    :type mocker: pytest_mock.plugin.MockerFixture
    :param async_client: Async test client
    :type async_client: httpx.AsyncClient
    :raises AssertionError: On incorrect status
    :return: None
    :rtype: None
    """
    mocker.patch("src.api.routes.list_films", return_value=[])
    res = await async_client.get("/films/")
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_search_films_found(mocker, async_client):
    """
    Tests GET /films/search with match returning 200.

    :param mocker: pytest-mock fixture to patch search logic
    :type mocker: pytest_mock.plugin.MockerFixture
    :param async_client: Async test client
    :type async_client: httpx.AsyncClient
    :raises AssertionError: On wrong status
    :return: None
    :rtype: None
    """
    mocker.patch(
        "src.api.routes.search_films_by_title",
        return_value=[{"id": 1, "title": "A New Hope"}],
    )
    res = await async_client.get("/films/search?q=Hope")
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_search_films_not_found(mocker, async_client):
    """
    Tests GET /films/search with no match returning 404.

    :param mocker: pytest-mock fixture to patch search logic
    :type mocker: pytest_mock.plugin.MockerFixture
    :param async_client: Async test client
    :type async_client: httpx.AsyncClient
    :raises AssertionError: On wrong status
    :return: None
    :rtype: None
    """
    mocker.patch("src.api.routes.search_films_by_title", return_value=[])
    res = await async_client.get("/films/search?q=none")
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_get_film_by_id_found(mocker, async_client):
    """
    Tests GET /films/{id} returning 200 for existing film.

    :param mocker: pytest-mock fixture to patch get_film
    :type mocker: pytest_mock.plugin.MockerFixture
    :param async_client: Async test client
    :type async_client: httpx.AsyncClient
    :raises AssertionError: On incorrect status
    :return: None
    :rtype: None
    """
    mocker.patch(
        "src.api.routes.get_film", return_value={"id": 1, "title": "A New Hope"}
    )
    res = await async_client.get("/films/1")
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_get_film_by_id_not_found(mocker, async_client):
    """
    Tests GET /films/{id} with non-existing ID returning 404.

    :param mocker: pytest-mock fixture to patch get_film
    :type mocker: pytest_mock.plugin.MockerFixture
    :param async_client: Async test client
    :type async_client: httpx.AsyncClient
    :raises AssertionError: On wrong status
    :return: None
    :rtype: None
    """
    mocker.patch("src.api.routes.get_film", return_value=None)
    res = await async_client.get("/films/999")
    assert res.status_code == 404


# -----------------------------
# Starships
# -----------------------------


@pytest.mark.asyncio
async def test_list_starships(mocker, async_client):
    """
    Tests GET /starships/ returning 200 with empty list.

    :param mocker: pytest-mock fixture to patch list_starships
    :type mocker: pytest_mock.plugin.MockerFixture
    :param async_client: Async test client
    :type async_client: httpx.AsyncClient
    :raises AssertionError: On incorrect status
    :return: None
    :rtype: None
    """
    mocker.patch("src.api.routes.list_starships", return_value=[])
    res = await async_client.get("/starships/")
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_search_starships_found(mocker, async_client):
    """
    Tests GET /starships/search with match returning 200.

    :param mocker: pytest-mock fixture to patch search logic
    :type mocker: pytest_mock.plugin.MockerFixture
    :param async_client: Async test client
    :type async_client: httpx.AsyncClient
    :raises AssertionError: On wrong status
    :return: None
    :rtype: None
    """
    mocker.patch(
        "src.api.routes.search_starships_by_name",
        return_value=[{"id": 1, "name": "Falcon"}],
    )
    res = await async_client.get("/starships/search?q=Falcon")
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_search_starships_not_found(mocker, async_client):
    """
    Tests GET /starships/search with no match returning 404.

    :param mocker: pytest-mock fixture to patch search logic
    :type mocker: pytest_mock.plugin.MockerFixture
    :param async_client: Async test client
    :type async_client: httpx.AsyncClient
    :raises AssertionError: On wrong status
    :return: None
    :rtype: None
    """
    mocker.patch("src.api.routes.search_starships_by_name", return_value=[])
    res = await async_client.get("/starships/search?q=none")
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_get_starship_by_id_found(mocker, async_client):
    """
    Tests GET /starships/{id} returning 200 for existing starship.

    :param mocker: pytest-mock fixture to patch get_starship
    :type mocker: pytest_mock.plugin.MockerFixture
    :param async_client: Async test client
    :type async_client: httpx.AsyncClient
    :raises AssertionError: On incorrect status
    :return: None
    :rtype: None
    """
    mocker.patch(
        "src.api.routes.get_starship", return_value={"id": 1, "name": "Falcon"}
    )
    res = await async_client.get("/starships/1")
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_get_starship_by_id_not_found(mocker, async_client):
    """
    Tests GET /starships/{id} with non-existing ID returning 404.

    :param mocker: pytest-mock fixture to patch get_starship
    :type mocker: pytest_mock.plugin.MockerFixture
    :param async_client: Async test client
    :type async_client: httpx.AsyncClient
    :raises AssertionError: On wrong status
    :return: None
    :rtype: None
    """
    mocker.patch("src.api.routes.get_starship", return_value=None)
    res = await async_client.get("/starships/999")
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_import_films_failure(mocker, async_client):
    """
    Tests failed POST to /import/films returning 502 with error JSON.

    :param mocker: pytest-mock fixture to simulate exception
    :type mocker: pytest_mock.plugin.MockerFixture
    :param async_client: Async test client for FastAPI app
    :type async_client: httpx.AsyncClient
    :raises AssertionError: If response or log behavior is incorrect
    :return: None
    :rtype: None
    """
    mocker.patch(
        "src.api.routes.import_films_from_swapi", side_effect=Exception("SWAPI down")
    )
    mock_log = mocker.patch("src.api.routes.log_error")

    res = await async_client.post("/import/films")

    assert res.status_code == 502
    assert res.json() == {"detail": "Failed to import films from SWAPI."}
    mock_log.assert_called_once()


@pytest.mark.asyncio
async def test_import_starships_failure(mocker, async_client):
    """
    Tests failed POST to /import/starships returning 502 with error JSON.

    :param mocker: pytest-mock fixture to simulate exception
    :type mocker: pytest_mock.plugin.MockerFixture
    :param async_client: Async test client for FastAPI app
    :type async_client: httpx.AsyncClient
    :raises AssertionError: If response or log behavior is incorrect
    :return: None
    :rtype: None
    """
    mocker.patch(
        "src.api.routes.import_starships_from_swapi",
        side_effect=Exception("SWAPI down"),
    )
    mock_log = mocker.patch("src.api.routes.log_error")

    res = await async_client.post("/import/starships")

    assert res.status_code == 502
    assert res.json() == {"detail": "Failed to import starships from SWAPI."}
    mock_log.assert_called_once()
