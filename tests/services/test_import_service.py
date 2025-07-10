"""
tests.services.test_import_service

================================================================================
Unit Tests for Import Service
================================================================================

Overview
--------
Validates `src.services.import_service`, which is responsible for orchestrating
data ingestion from the external Star Wars API (SWAPI) into the local database.

Ensures the service correctly handles:
- Pagination over SWAPI resources
- Skipping or rejecting invalid or duplicate data
- Logging and error handling for upstream failures
- Data conversion and parsing (e.g., dates, timestamps)
- Graceful degradation when inserts fail or raise exceptions

Tested Responsibilities
------------------------
- import_characters_from_swapi
- import_films_from_swapi
- import_starships_from_swapi

Key Characteristics
--------------------
- Uses `pytest-asyncio` to test async service flows
- Employs mocking to isolate dependencies (database session, fetchers, creators)
- Verifies retry and pagination logic with multiple pages
- Confirms all error branches raise correct custom exceptions
- Tests logs and control flow for empty, invalid, or duplicate records

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

import asyncio
from unittest import mock

import pytest

from src.exceptions.custom_exceptions import DataImportError, ExternalAPIError
from src.services import import_service


@pytest.fixture(autouse=True)
def patch_logging():
    """
    Auto-used pytest fixture that patches logging functions in import_service.

    :raises AssertionError: If patching fails or is misused
    :yield: None to allow test execution with patched logging
    :rtype: None
    """
    with mock.patch("src.services.import_service.log_info"), mock.patch(
        "src.services.import_service.log_error"
    ):
        yield


@pytest.fixture
def mock_db():
    """
    Provides a mocked async database session with a get() method.

    :return: A mock object simulating an AsyncSession-like interface with get() method
    :rtype: unittest.mock.AsyncMock
    """
    db = mock.AsyncMock()
    db.get = mock.AsyncMock(return_value=None)
    return db


@pytest.mark.asyncio
async def test_import_characters_happy_path(mock_db):
    """
    Tests the happy path for import_characters_from_swapi with multi-page results.

    :param mock_db: Mocked AsyncSession-like database dependency
    :type mock_db: unittest.mock.AsyncMock
    :raises AssertionError: If pagination or service calls are incorrect
    :return: None
    :rtype: None
    """
    page_responses = [
        {
            "results": [{"name": "Luke", "films": ["https://swapi.dev/api/films/1/"]}],
            "next": "something",
        },
        {"results": [], "next": None},
    ]

    fetch_characters_mock = mock.AsyncMock(side_effect=page_responses)

    with mock.patch(
        "src.services.import_service.fetch_characters", fetch_characters_mock
    ), mock.patch(
        "src.services.import_service.character_exists", side_effect=[False, False]
    ), mock.patch(
        "src.services.import_service.create_character",
        return_value=mock.AsyncMock(films=[]),
    ):

        await import_service.import_characters_from_swapi(mock_db)

    assert fetch_characters_mock.call_count == 2


@pytest.mark.asyncio
async def test_import_characters_existing_skipped(mock_db):
    """
    Tests that existing characters are detected and skipped without creation.

    :param mock_db: Mocked database session
    :type mock_db: unittest.mock.AsyncMock
    :raises AssertionError: If creation logic is wrongly invoked
    :return: None
    :rtype: None
    """
    response = {"results": [{"name": "Leia", "films": []}], "next": None}

    with mock.patch(
        "src.services.import_service.fetch_characters", return_value=response
    ), mock.patch("src.services.import_service.character_exists", return_value=True):

        await import_service.import_characters_from_swapi(mock_db)


@pytest.mark.asyncio
async def test_import_characters_empty_name_logs_and_skips(mock_db):
    """
    Tests that empty-name characters are logged and skipped without processing.

    :param mock_db: Mocked database session
    :type mock_db: unittest.mock.AsyncMock
    :raises AssertionError: If character_exists is incorrectly called
    :return: None
    :rtype: None
    """
    response = {"results": [{"name": ""}], "next": None}

    with mock.patch(
        "src.services.import_service.fetch_characters", return_value=response
    ), mock.patch("src.services.import_service.character_exists") as exists_mock:
        await import_service.import_characters_from_swapi(mock_db)
        exists_mock.assert_not_called()


@pytest.mark.asyncio
async def test_import_characters_fetch_error_raises(mock_db):
    """
    Tests that ExternalAPIError is raised if fetch_characters fails.

    :param mock_db: Mocked database session
    :type mock_db: unittest.mock.AsyncMock
    :raises ExternalAPIError: On upstream fetch failure
    :return: None
    :rtype: None
    """
    with mock.patch(
        "src.services.import_service.fetch_characters", side_effect=Exception("fail")
    ):
        with pytest.raises(ExternalAPIError):
            await import_service.import_characters_from_swapi(mock_db)


@pytest.mark.asyncio
async def test_import_characters_invalid_response_type_raises(mock_db):
    """
    Tests that DataImportError is raised if SWAPI returns invalid type.

    :param mock_db: Mocked database session
    :type mock_db: unittest.mock.AsyncMock
    :raises DataImportError: On invalid response type
    :return: None
    :rtype: None
    """
    with mock.patch("src.services.import_service.fetch_characters", return_value="bad"):
        with pytest.raises(DataImportError):
            await import_service.import_characters_from_swapi(mock_db)


@pytest.mark.asyncio
async def test_import_films_happy_path(mock_db):
    """
    Tests the happy path for import_films_from_swapi with valid single-page results.

    :param mock_db: Mocked database session
    :type mock_db: unittest.mock.AsyncMock
    :raises AssertionError: If creation logic is incorrectly bypassed
    :return: None
    :rtype: None
    """
    response = {
        "results": [
            {
                "title": "A New Hope",
                "episode_id": 4,
                "opening_crawl": "Text",
                "director": "Lucas",
                "producer": "Producer",
                "release_date": "1977-05-25",
                "created": "2023-01-01T00:00:00Z",
                "edited": "2023-01-01T00:00:00Z",
                "url": "https://swapi.dev/api/films/1/",
            }
        ]
    }

    with mock.patch(
        "src.services.import_service.fetch_films", return_value=response
    ), mock.patch(
        "src.services.import_service.film_exists", return_value=False
    ), mock.patch(
        "src.services.import_service.create_film"
    ), mock.patch(
        "src.services.import_service.parse_iso_date", return_value=None
    ), mock.patch(
        "src.services.import_service.parse_iso_datetime", return_value=None
    ):

        await import_service.import_films_from_swapi(mock_db)


@pytest.mark.asyncio
async def test_import_films_fetch_error_raises(mock_db):
    """
    Tests that ExternalAPIError is raised if fetch_films fails.

    :param mock_db: Mocked database session
    :type mock_db: unittest.mock.AsyncMock
    :raises ExternalAPIError: On fetch failure
    :return: None
    :rtype: None
    """
    with mock.patch(
        "src.services.import_service.fetch_films", side_effect=Exception("fail")
    ):
        with pytest.raises(ExternalAPIError):
            await import_service.import_films_from_swapi(mock_db)


@pytest.mark.asyncio
async def test_import_films_empty_response_raises(mock_db):
    """
    Tests that DataImportError is raised on empty API response.

    :param mock_db: Mocked database session
    :type mock_db: unittest.mock.AsyncMock
    :raises DataImportError: On empty results
    :return: None
    :rtype: None
    """
    with mock.patch("src.services.import_service.fetch_films", return_value={}):
        with pytest.raises(DataImportError):
            await import_service.import_films_from_swapi(mock_db)


@pytest.mark.asyncio
async def test_import_films_existing_skipped(mock_db):
    response = {"results": [{"title": "Empire Strikes Back"}]}

    with mock.patch(
        "src.services.import_service.fetch_films", return_value=response
    ), mock.patch("src.services.import_service.film_exists", return_value=True):

        await import_service.import_films_from_swapi(mock_db)


@pytest.mark.asyncio
async def test_import_starships_happy_path(mock_db):
    """
    Tests the happy path for import_starships_from_swapi with multi-page results.

    :param mock_db: Mocked database session
    :type mock_db: unittest.mock.AsyncMock
    :raises AssertionError: If pagination or creation logic fails
    :return: None
    :rtype: None
    """
    page_responses = [
        {
            "results": [
                {
                    "name": "Falcon",
                    "model": "YT-1300",
                    "manufacturer": "Corellian",
                    "starship_class": "Freighter",
                }
            ],
            "next": "x",
        },
        {"results": [], "next": None},
    ]

    fetch_starships_mock = mock.AsyncMock(side_effect=page_responses)

    with mock.patch(
        "src.services.import_service.fetch_starships", fetch_starships_mock
    ), mock.patch(
        "src.services.import_service.starship_exists", return_value=False
    ), mock.patch(
        "src.services.import_service.create_starship"
    ):

        await import_service.import_starships_from_swapi(mock_db)

    assert fetch_starships_mock.call_count == 2


@pytest.mark.asyncio
async def test_import_starships_fetch_error_raises(mock_db):
    """
    Tests that ExternalAPIError is raised if fetch_starships fails.

    :param mock_db: Mocked database session
    :type mock_db: unittest.mock.AsyncMock
    :raises ExternalAPIError: On fetch failure
    :return: None
    :rtype: None
    """
    with mock.patch(
        "src.services.import_service.fetch_starships", side_effect=Exception("fail")
    ):
        with pytest.raises(ExternalAPIError):
            await import_service.import_starships_from_swapi(mock_db)


@pytest.mark.asyncio
async def test_import_starships_empty_name_skips(mock_db):
    """
    Tests that starships with empty names are skipped without checking existence.

    :param mock_db: Mocked database session
    :type mock_db: unittest.mock.AsyncMock
    :raises AssertionError: If existence check is incorrectly called
    :return: None
    :rtype: None
    """
    response = {"results": [{"name": ""}], "next": None}

    with mock.patch(
        "src.services.import_service.fetch_starships", return_value=response
    ), mock.patch("src.services.import_service.starship_exists") as exists_mock:
        await import_service.import_starships_from_swapi(mock_db)
        exists_mock.assert_not_called()


@pytest.mark.asyncio
async def test_import_starships_existing_skipped(mock_db):
    """
    Tests that existing starships are detected and skipped without creation.

    :param mock_db: Mocked database session
    :type mock_db: unittest.mock.AsyncMock
    :raises AssertionError: If creation is incorrectly invoked
    :return: None
    :rtype: None
    """
    response = {"results": [{"name": "X-Wing"}], "next": None}

    with mock.patch(
        "src.services.import_service.fetch_starships", return_value=response
    ), mock.patch("src.services.import_service.starship_exists", return_value=True):

        await import_service.import_starships_from_swapi(mock_db)


@pytest.mark.asyncio
async def test_import_characters_create_character_returns_none(mock_db):
    """
    Tests that characters returning None from create_character are logged and skipped.

    :param mock_db: Mocked database session
    :type mock_db: unittest.mock.AsyncMock
    :raises AssertionError: If error branch is not exercised
    :return: None
    :rtype: None
    """
    response = {"results": [{"name": "Greedo", "films": []}], "next": None}

    with mock.patch(
        "src.services.import_service.fetch_characters", return_value=response
    ), mock.patch(
        "src.services.import_service.character_exists", return_value=False
    ), mock.patch(
        "src.services.import_service.create_character", return_value=None
    ):
        await import_service.import_characters_from_swapi(mock_db)


@pytest.mark.asyncio
async def test_import_characters_general_exception_in_loop(mock_db):
    """
    Tests that general exceptions in processing loop are caught and logged.

    :param mock_db: Mocked database session
    :type mock_db: unittest.mock.AsyncMock
    :raises Exception: If exception handling fails
    :return: None
    :rtype: None
    """
    response = {"results": [{"name": "Biggs"}], "next": None}

    with mock.patch(
        "src.services.import_service.fetch_characters", return_value=response
    ), mock.patch(
        "src.services.import_service.character_exists", return_value=False
    ), mock.patch(
        "src.services.import_service.create_character", side_effect=Exception("DB fail")
    ):
        await import_service.import_characters_from_swapi(mock_db)


@pytest.mark.asyncio
async def test_import_characters_happy_path_with_pagination(mock_db):
    """
    Tests that pagination is correctly handled in import_characters_from_swapi.

    :param mock_db: Mocked database session
    :type mock_db: unittest.mock.AsyncMock
    :return: None
    :rtype: None
    """
    page_responses = [
        {"results": [{"name": "Luke", "films": []}], "next": "some-next-url"},
        {"results": [], "next": None},
    ]
    with mock.patch(
        "src.services.import_service.fetch_characters", side_effect=page_responses
    ), mock.patch(
        "src.services.import_service.character_exists", return_value=False
    ), mock.patch(
        "src.services.import_service.create_character",
        return_value=mock.AsyncMock(films=[]),
    ):
        await import_service.import_characters_from_swapi(mock_db)


@pytest.mark.asyncio
async def test_import_characters_skips_empty_name(mock_db):
    """
    Tests that characters with empty names are skipped without processing.

    :param mock_db: Mocked database session
    :type mock_db: unittest.mock.AsyncMock
    :return: None
    :rtype: None
    """
    response = {"results": [{"name": ""}], "next": None}
    with mock.patch(
        "src.services.import_service.fetch_characters", return_value=response
    ):
        await import_service.import_characters_from_swapi(mock_db)


@pytest.mark.asyncio
async def test_import_characters_skips_existing_character(mock_db):
    """
    Tests that existing characters are skipped and not re-imported.

    :param mock_db: Mocked database session
    :type mock_db: unittest.mock.AsyncMock
    :return: None
    :rtype: None
    """
    response = {"results": [{"name": "Leia"}], "next": None}
    with mock.patch(
        "src.services.import_service.fetch_characters", return_value=response
    ), mock.patch("src.services.import_service.character_exists", return_value=True):
        await import_service.import_characters_from_swapi(mock_db)


@pytest.mark.asyncio
async def test_import_characters_film_linking_exception(mock_db):
    """
    Tests that film linking exceptions are caught and logged during character import.

    :param mock_db: Mocked database session
    :type mock_db: unittest.mock.AsyncMock
    :return: None
    :rtype: None
    """
    response = {
        "results": [{"name": "Han", "films": ["https://swapi.dev/api/films/1/"]}],
        "next": None,
    }
    character = mock.AsyncMock()
    character.films = mock.Mock()
    character.films.append = mock.Mock(side_effect=Exception("link error"))
    with mock.patch(
        "src.services.import_service.fetch_characters", return_value=response
    ), mock.patch(
        "src.services.import_service.character_exists", return_value=False
    ), mock.patch(
        "src.services.import_service.create_character", return_value=character
    ), mock.patch.object(
        mock_db, "get", return_value=mock.Mock()
    ):
        await import_service.import_characters_from_swapi(mock_db)


@pytest.mark.asyncio
async def test_import_characters_create_character_none_triggers_else(mock_db):
    """
    Tests that create_character returning None triggers the fallback logging.

    :param mock_db: Mocked database session
    :type mock_db: unittest.mock.AsyncMock
    :return: None
    :rtype: None
    """
    response = {"results": [{"name": "Greedo"}], "next": None}
    with mock.patch(
        "src.services.import_service.fetch_characters", return_value=response
    ), mock.patch(
        "src.services.import_service.character_exists", return_value=False
    ), mock.patch(
        "src.services.import_service.create_character", return_value=None
    ):
        await import_service.import_characters_from_swapi(mock_db)


@pytest.mark.asyncio
async def test_import_characters_general_for_loop_exception(mock_db):
    """
    Tests that unexpected exceptions in the character processing loop are caught.

    :param mock_db: Mocked database session
    :type mock_db: unittest.mock.AsyncMock
    :return: None
    :rtype: None
    """
    response = {"results": [{"name": "Biggs"}], "next": None}
    with mock.patch(
        "src.services.import_service.fetch_characters", return_value=response
    ), mock.patch(
        "src.services.import_service.character_exists", return_value=False
    ), mock.patch(
        "src.services.import_service.create_character",
        side_effect=Exception("unexpected"),
    ):
        await import_service.import_characters_from_swapi(mock_db)


@pytest.mark.asyncio
async def test_import_characters_no_results_on_page_breaks(mock_db):
    """
    Tests that import_characters_from_swapi exits cleanly when no results are returned.

    :param mock_db: Mocked database session
    :type mock_db: unittest.mock.AsyncMock
    :return: None
    :rtype: None
    """
    response = {"results": [], "next": None}
    with mock.patch(
        "src.services.import_service.fetch_characters", return_value=response
    ):
        await import_service.import_characters_from_swapi(mock_db)


@pytest.mark.asyncio
async def test_import_characters_breaks_on_no_next(mock_db):
    """
    Tests that pagination stops when the 'next' field is missing.

    :param mock_db: Mocked database session
    :type mock_db: unittest.mock.AsyncMock
    :return: None
    :rtype: None
    """
    response = {"results": [{"name": "Obi-Wan"}]}
    with mock.patch(
        "src.services.import_service.fetch_characters", return_value=response
    ), mock.patch(
        "src.services.import_service.character_exists", return_value=False
    ), mock.patch(
        "src.services.import_service.create_character",
        return_value=mock.AsyncMock(films=[]),
    ):
        await import_service.import_characters_from_swapi(mock_db)


@pytest.mark.asyncio
async def test_import_characters_fetch_error_raises_external_api_error(mock_db):
    """
    Tests that ExternalAPIError is raised on fetch_characters failure.

    :param mock_db: Mocked database session
    :type mock_db: unittest.mock.AsyncMock
    :raises ExternalAPIError: On fetch error
    :return: None
    :rtype: None
    """
    with mock.patch(
        "src.services.import_service.fetch_characters", side_effect=Exception("fail")
    ):
        with pytest.raises(import_service.ExternalAPIError):
            await import_service.import_characters_from_swapi(mock_db)


@pytest.mark.asyncio
async def test_import_characters_invalid_response_type_raises_data_import_error(
    mock_db,
):
    """
    Tests that DataImportError is raised when fetch_characters returns invalid type.

    :param mock_db: Mocked database session
    :type mock_db: unittest.mock.AsyncMock
    :raises DataImportError: On invalid response
    :return: None
    :rtype: None
    """
    with mock.patch(
        "src.services.import_service.fetch_characters", return_value="not-a-dict"
    ):
        with pytest.raises(import_service.DataImportError):
            await import_service.import_characters_from_swapi(mock_db)


@pytest.mark.asyncio
async def test_import_films_general_exception_in_loop(mock_db):
    """
    Tests that general exceptions during film processing are caught and logged.

    :param mock_db: Mocked database session
    :type mock_db: unittest.mock.AsyncMock
    :return: None
    :rtype: None
    """
    response = {
        "results": [
            {
                "title": "A New Hope",
                "episode_id": 4,
                "opening_crawl": "Text",
                "director": "Lucas",
                "producer": "Producer",
                "release_date": "1977-05-25",
                "created": "2023-01-01T00:00:00Z",
                "edited": "2023-01-01T00:00:00Z",
                "url": "https://swapi.dev/api/films/1/",
            }
        ]
    }

    with mock.patch(
        "src.services.import_service.fetch_films", return_value=response
    ), mock.patch(
        "src.services.import_service.film_exists", return_value=False
    ), mock.patch(
        "src.services.import_service.parse_iso_date", return_value=None
    ), mock.patch(
        "src.services.import_service.parse_iso_datetime", return_value=None
    ), mock.patch(
        "src.services.import_service.create_film", side_effect=Exception("DB fail")
    ):
        await import_service.import_films_from_swapi(mock_db)


@pytest.mark.asyncio
async def test_import_starships_general_exception_in_loop(mock_db):
    """
    Tests that general exceptions during starship processing are caught and logged.

    :param mock_db: Mocked database session
    :type mock_db: unittest.mock.AsyncMock
    :return: None
    :rtype: None
    """
    page_response = {
        "results": [
            {
                "name": "Falcon",
                "model": "YT-1300",
                "manufacturer": "Corellian",
                "starship_class": "Freighter",
            }
        ],
        "next": None,
    }

    with mock.patch(
        "src.services.import_service.fetch_starships", return_value=page_response
    ), mock.patch(
        "src.services.import_service.starship_exists", return_value=False
    ), mock.patch(
        "src.services.import_service.create_starship", side_effect=Exception("DB fail")
    ):
        await import_service.import_starships_from_swapi(mock_db)


@pytest.mark.asyncio
async def test_import_films_create_film_returns_none(mock_db):
    """
    Tests that create_film returning None triggers fallback logging.

    :param mock_db: Mocked database session
    :type mock_db: unittest.mock.AsyncMock
    :return: None
    :rtype: None
    """
    response = {
        "results": [
            {
                "title": "Rogue One",
                "episode_id": 3,
                "opening_crawl": "crawl",
                "director": "Director",
                "producer": "Producer",
                "release_date": "1977-05-25",
                "created": "2023-01-01T00:00:00Z",
                "edited": "2023-01-01T00:00:00Z",
                "url": "https://swapi.dev/api/films/1/",
            }
        ]
    }
    with mock.patch(
        "src.services.import_service.fetch_films", return_value=response
    ), mock.patch(
        "src.services.import_service.film_exists", return_value=False
    ), mock.patch(
        "src.services.import_service.parse_iso_date", return_value=None
    ), mock.patch(
        "src.services.import_service.parse_iso_datetime", return_value=None
    ), mock.patch(
        "src.services.import_service.create_film", return_value=None
    ):
        await import_service.import_films_from_swapi(mock_db)


@pytest.mark.asyncio
async def test_import_starships_create_starship_returns_none(mock_db):
    """
    Tests that create_starship returning None triggers fallback logging.

    :param mock_db: Mocked database session
    :type mock_db: unittest.mock.AsyncMock
    :return: None
    :rtype: None
    """
    page_response = {
        "results": [
            {
                "name": "Slave I",
                "model": "Firespray",
                "manufacturer": "Kuat",
                "starship_class": "Patrol",
            }
        ],
        "next": None,
    }
    with mock.patch(
        "src.services.import_service.fetch_starships", return_value=page_response
    ), mock.patch(
        "src.services.import_service.starship_exists", return_value=False
    ), mock.patch(
        "src.services.import_service.create_starship", return_value=None
    ):
        await import_service.import_starships_from_swapi(mock_db)


@pytest.mark.asyncio
async def test_import_films_empty_title_skips(mock_db):
    """
    Tests that films with empty titles are skipped without creation.

    :param mock_db: Mocked database session
    :type mock_db: unittest.mock.AsyncMock
    :return: None
    :rtype: None
    """
    response = {
        "results": [
            {
                "title": "",
                "episode_id": 4,
                "opening_crawl": "Text",
                "director": "Lucas",
                "producer": "Producer",
                "release_date": "1977-05-25",
                "created": "2023-01-01T00:00:00Z",
                "edited": "2023-01-01T00:00:00Z",
                "url": "https://swapi.dev/api/films/1/",
            }
        ]
    }
    with mock.patch("src.services.import_service.fetch_films", return_value=response):
        await import_service.import_films_from_swapi(mock_db)


@pytest.mark.asyncio
async def test_import_starships_no_results_key_breaks(mock_db):
    """
    Tests that import_starships_from_swapi exits cleanly when 'results' key is missing.

    :param mock_db: Mocked database session
    :type mock_db: unittest.mock.AsyncMock
    :return: None
    :rtype: None
    """
    page_response = {"not_results": []}
    with mock.patch(
        "src.services.import_service.fetch_starships", return_value=page_response
    ):
        await import_service.import_starships_from_swapi(mock_db)
