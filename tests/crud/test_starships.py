"""
tests.crud.test_starships

================================================================================
Unit Tests for Starship CRUD Operations
================================================================================

Overview
--------
Tests the async CRUD functions in `src.crud.starships`, which manage
persistence of Starship records in the database via SQLAlchemy AsyncSession.

Tested Responsibilities
------------------------
- Checking for starship existence by name
- Creating new starships with duplicate-check and integrity error handling
- Fetching single starships by ID
- Listing starships with pagination
- Searching starships by partial name match

Key Characteristics
--------------------
- Verifies correct session methods (add, commit, refresh, rollback)
- Mocks SQLAlchemy query execution and result behavior
- Handles IntegrityError exceptions by raising custom DatabaseError
- Ensures empty result sets return appropriate empty lists

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

from unittest import mock

import pytest
from sqlalchemy.exc import IntegrityError

from src.crud import starships
from src.exceptions.custom_exceptions import DatabaseError
from src.models.starship import Starship


@pytest.fixture
def fake_starship():
    """
    Provides a mock Starship model instance for testing CRUD operations.

    :return: Mock Starship instance with predefined attributes
    :rtype: Starship
    """
    return Starship(id=1, name="Millennium Falcon")


@pytest.fixture
def fake_starship_in():
    """
    Provides a mock Pydantic-like input object for starship creation.

    :return: Mock object with .dict() method returning starship data
    :rtype: mock.Mock
    """
    mock_in = mock.Mock()
    mock_in.name = "Millennium Falcon"
    mock_in.dict.return_value = {"name": "Millennium Falcon"}
    return mock_in


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exists_result,expected",
    [
        (object(), True),
        (None, False),
    ],
)
async def test_starship_exists(mocker, exists_result, expected):
    """
    Tests starship_exists returns True or False depending on query result.

    :param mocker: pytest-mock fixture for patching session
    :type mocker: pytest_mock.plugin.MockerFixture
    :param exists_result: Object to simulate query result
    :type exists_result: Any
    :param expected: Expected boolean result
    :type expected: bool
    :raises AssertionError: If returned value does not match expected
    :return: None
    :rtype: None
    """
    mock_session = mock.Mock()
    mock_session.execute = mock.AsyncMock()

    result_mock = mock.Mock()
    result_mock.unique.return_value.scalar_one_or_none.return_value = exists_result
    mock_session.execute.return_value = result_mock

    result = await starships.starship_exists(mock_session, "Falcon")
    assert result is expected


@pytest.mark.asyncio
async def test_create_starship_success(mocker, fake_starship, fake_starship_in):
    """
    Tests successful creation of a new Starship record in the database.

    :param mocker: pytest-mock fixture to patch Starship instantiation and existence check
    :type mocker: pytest_mock.plugin.MockerFixture
    :param fake_starship: Mock Starship instance to return
    :type fake_starship: Starship
    :param fake_starship_in: Mock Pydantic input schema
    :type fake_starship_in: mock.Mock
    :raises AssertionError: If add, commit, refresh are not called or result is incorrect
    :return: None
    :rtype: None
    """
    mock_session = mock.Mock()
    mock_session.commit = mock.AsyncMock()
    mock_session.refresh = mock.AsyncMock()
    mock_session.execute = mock.AsyncMock()

    mocker.patch("src.crud.starships.starship_exists", return_value=False)
    mocker.patch("src.crud.starships.Starship", return_value=fake_starship)

    result = await starships.create_starship(mock_session, fake_starship_in)

    mock_session.add.assert_called_once_with(fake_starship)
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(fake_starship)
    assert result == fake_starship


@pytest.mark.asyncio
async def test_create_starship_skipped_if_exists(mocker, fake_starship_in):
    """
    Tests that create_starship does nothing if starship already exists.

    :param mocker: pytest-mock fixture to patch starship_exists
    :type mocker: pytest_mock.plugin.MockerFixture
    :param fake_starship_in: Mock Pydantic input schema
    :type fake_starship_in: mock.Mock
    :raises AssertionError: If add or commit are called despite existence
    :return: None
    :rtype: None
    """
    mock_session = mock.Mock()
    mock_session.commit = mock.AsyncMock()
    mock_session.refresh = mock.AsyncMock()
    mock_session.execute = mock.AsyncMock()

    mocker.patch("src.crud.starships.starship_exists", return_value=True)

    result = await starships.create_starship(mock_session, fake_starship_in)
    assert result is None

    mock_session.add.assert_not_called()
    mock_session.commit.assert_not_awaited()
    mock_session.refresh.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_starship_integrity_error(mocker, fake_starship_in):
    """
    Tests that creating a Starship with integrity error rolls back and raises DatabaseError.

    :param mocker: pytest-mock fixture to patch logger and dependencies
    :type mocker: pytest_mock.plugin.MockerFixture
    :param fake_starship_in: Mock Pydantic input schema
    :type fake_starship_in: mock.Mock
    :raises DatabaseError: On IntegrityError in commit
    :return: None
    :rtype: None
    """
    mock_session = mock.Mock()
    mock_session.commit = mock.AsyncMock(
        side_effect=IntegrityError("mock", "mock", "mock")
    )
    mock_session.rollback = mock.AsyncMock()
    mock_session.execute = mock.AsyncMock()

    mocker.patch("src.crud.starships.starship_exists", return_value=False)
    mock_log = mocker.patch("src.crud.starships.log_error")
    mocker.patch("src.crud.starships.Starship", return_value=mock.Mock())

    with pytest.raises(DatabaseError) as exc:
        await starships.create_starship(mock_session, fake_starship_in)

    assert "Database integrity error" in str(exc.value)
    mock_session.rollback.assert_awaited_once()
    mock_log.assert_called_once()


@pytest.mark.asyncio
async def test_get_starship_found(mocker, fake_starship):
    """
    Tests get_starship returns a Starship when found by ID.

    :param mocker: pytest-mock fixture to patch session
    :type mocker: pytest_mock.plugin.MockerFixture
    :param fake_starship: Expected Starship object
    :type fake_starship: Starship
    :raises AssertionError: If result is not the expected Starship
    :return: None
    :rtype: None
    """
    mock_session = mock.Mock()
    mock_session.execute = mock.AsyncMock()

    result_mock = mock.Mock()
    result_mock.unique.return_value.scalar_one_or_none.return_value = fake_starship
    mock_session.execute.return_value = result_mock

    result = await starships.get_starship(mock_session, 1)
    assert result == fake_starship


@pytest.mark.asyncio
async def test_get_starship_not_found(mocker):
    """
    Tests get_starship returns None when no record is found.

    :param mocker: pytest-mock fixture to patch session
    :type mocker: pytest_mock.plugin.MockerFixture
    :raises AssertionError: If result is not None
    :return: None
    :rtype: None
    """
    mock_session = mock.Mock()
    mock_session.execute = mock.AsyncMock()

    result_mock = mock.Mock()
    result_mock.unique.return_value.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = result_mock

    result = await starships.get_starship(mock_session, 999)
    assert result is None


@pytest.mark.asyncio
async def test_list_starships(mocker, fake_starship):
    """
    Tests list_starships returns list of Starship objects with pagination.

    :param mocker: pytest-mock fixture to patch session
    :type mocker: pytest_mock.plugin.MockerFixture
    :param fake_starship: Expected Starship object
    :type fake_starship: Starship
    :raises AssertionError: If result list is incorrect
    :return: None
    :rtype: None
    """
    mock_session = mock.Mock()
    mock_session.execute = mock.AsyncMock()

    result_mock = mock.Mock()
    scalars_mock = mock.Mock()
    scalars_mock.all.return_value = [fake_starship]
    result_mock.unique.return_value.scalars.return_value = scalars_mock
    mock_session.execute.return_value = result_mock

    result = await starships.list_starships(mock_session, skip=0, limit=10)
    assert result == [fake_starship]


@pytest.mark.asyncio
async def test_list_starships_empty(mocker):
    """
    Tests list_starships returns empty list when no records found.

    :param mocker: pytest-mock fixture to patch session
    :type mocker: pytest_mock.plugin.MockerFixture
    :raises AssertionError: If result is not empty list
    :return: None
    :rtype: None
    """
    mock_session = mock.Mock()
    mock_session.execute = mock.AsyncMock()

    result_mock = mock.Mock()
    scalars_mock = mock.Mock()
    scalars_mock.all.return_value = []
    result_mock.unique.return_value.scalars.return_value = scalars_mock
    mock_session.execute.return_value = result_mock

    result = await starships.list_starships(mock_session, skip=0, limit=10)
    assert result == []


@pytest.mark.asyncio
async def test_search_starships_by_name(mocker, fake_starship):
    """
    Tests search_starships_by_name returns matching Starship list.

    :param mocker: pytest-mock fixture to patch session
    :type mocker: pytest_mock.plugin.MockerFixture
    :param fake_starship: Expected Starship object
    :type fake_starship: Starship
    :raises AssertionError: If result list is incorrect
    :return: None
    :rtype: None
    """
    mock_session = mock.Mock()
    mock_session.execute = mock.AsyncMock()

    result_mock = mock.Mock()
    scalars_mock = mock.Mock()
    scalars_mock.all.return_value = [fake_starship]
    result_mock.unique.return_value.scalars.return_value = scalars_mock
    mock_session.execute.return_value = result_mock

    result = await starships.search_starships_by_name(mock_session, "Falcon")
    assert result == [fake_starship]


@pytest.mark.asyncio
async def test_search_starships_by_name_empty(mocker):
    """
    Tests search_starships_by_name returns empty list when no matches.

    :param mocker: pytest-mock fixture to patch session
    :type mocker: pytest_mock.plugin.MockerFixture
    :raises AssertionError: If result is not empty list
    :return: None
    :rtype: None
    """
    mock_session = mock.Mock()
    mock_session.execute = mock.AsyncMock()

    result_mock = mock.Mock()
    scalars_mock = mock.Mock()
    scalars_mock.all.return_value = []
    result_mock.unique.return_value.scalars.return_value = scalars_mock
    mock_session.execute.return_value = result_mock

    result = await starships.search_starships_by_name(mock_session, "Nothing")
    assert result == []
