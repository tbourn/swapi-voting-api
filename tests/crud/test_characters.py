"""
tests.crud.test_characters

================================================================================
Unit Tests for Character CRUD Operations
================================================================================

Overview
--------
Validates the async CRUD functions in `src.crud.characters`, which handle
SQLAlchemy AsyncSession interactions for the Character model.

Tested Responsibilities
------------------------
- Creating new Character records, including rollback on IntegrityError
- Checking for existing Character records by name
- Fetching a Character by primary key
- Listing Characters with pagination
- Searching Characters by partial name

Key Characteristics
--------------------
- Fully mocks AsyncSession methods such as execute, add, commit, and refresh
- Simulates scalar and list query results, including empty results
- Ensures custom DatabaseError is raised on integrity constraint violations
- Tests transactional rollback behavior on errors
- Confirms correct result shapes for lists and single object fetches

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

from unittest import mock

import pytest
from sqlalchemy.exc import IntegrityError

from src.crud import characters
from src.exceptions.custom_exceptions import DatabaseError
from src.models.character import Character


@pytest.fixture
def fake_character():
    """
    Provides a mock Character model instance for testing CRUD operations.

    :return: Mock Character instance with predefined attributes
    :rtype: Character
    """
    return Character(
        id=1,
        name="Luke Skywalker",
        films=[],
        vehicles=[],
        starships=[],
        species=[],
        homeworld=None,
    )


@pytest.fixture
def fake_character_in():
    """
    Provides a mock Pydantic-like input object for character creation.

    :return: Mock object with .dict() method returning character data
    :rtype: mock.Mock
    """
    mock_in = mock.Mock()
    mock_in.dict.return_value = {
        "name": "Luke Skywalker",
        "films": [],
        "vehicles": [],
        "starships": [],
        "species": [],
        "homeworld": None,
    }
    return mock_in


@pytest.fixture
def fake_result(fake_character):
    """
    Provides a mocked SQLAlchemy execute() result for testing query responses.

    :param fake_character: Mock Character instance to return in query results
    :type fake_character: Character
    :return: Mock result object with scalars().unique().first() and all() methods
    :rtype: mock.Mock
    """
    result_mock = mock.Mock()
    scalars_mock = mock.Mock()
    scalars_mock.unique.return_value.first.return_value = fake_character
    scalars_mock.unique.return_value.all.return_value = [fake_character]
    result_mock.scalars.return_value = scalars_mock
    return result_mock


@pytest.mark.asyncio
async def test_create_character_success(mocker, fake_character, fake_character_in):
    """
    Tests successful creation of a new Character record in the database.

    :param mocker: pytest-mock fixture to patch Character instantiation
    :type mocker: pytest_mock.plugin.MockerFixture
    :param fake_character: Mock Character instance to return
    :type fake_character: Character
    :param fake_character_in: Mock Pydantic input schema
    :type fake_character_in: mock.Mock
    :raises AssertionError: If add, commit, refresh are not called or result is incorrect
    :return: None
    :rtype: None
    """
    mock_session = mock.Mock()
    mock_session.commit = mock.AsyncMock()
    mock_session.refresh = mock.AsyncMock()
    mock_session.rollback = mock.AsyncMock()
    mock_session.execute = mock.AsyncMock()

    mocker.patch("src.crud.characters.Character", return_value=fake_character)

    result = await characters.create_character(mock_session, fake_character_in)

    mock_session.add.assert_called_once_with(fake_character)
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(fake_character)
    assert result == fake_character


@pytest.mark.asyncio
async def test_create_character_integrity_error(mocker, fake_character_in):
    """
    Tests that creating a Character with integrity error rolls back and raises DatabaseError.

    :param mocker: pytest-mock fixture to patch logger
    :type mocker: pytest_mock.plugin.MockerFixture
    :param fake_character_in: Mock Pydantic input schema
    :type fake_character_in: mock.Mock
    :raises DatabaseError: On IntegrityError in commit
    :return: None
    :rtype: None
    """
    mock_session = mock.Mock()
    mock_session.commit = mock.AsyncMock()
    mock_session.refresh = mock.AsyncMock()
    mock_session.rollback = mock.AsyncMock()
    mock_session.execute = mock.AsyncMock()

    mock_session.commit.side_effect = IntegrityError("mock", "mock", "mock")
    mock_session.rollback = mock.AsyncMock()

    mock_log = mocker.patch("src.crud.characters.log_error")

    with pytest.raises(DatabaseError) as exc:
        await characters.create_character(mock_session, fake_character_in)

    assert "Database integrity error" in str(exc.value)
    mock_session.rollback.assert_awaited_once()
    mock_log.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "result_object,expected",
    [
        (object(), True),
        (None, False),
    ],
)
async def test_character_exists(mocker, result_object, expected):
    """
    Tests character_exists returns True or False depending on query result.

    :param mocker: pytest-mock fixture for patching session
    :type mocker: pytest_mock.plugin.MockerFixture
    :param result_object: Object to simulate query result
    :type result_object: Any
    :param expected: Expected boolean result
    :type expected: bool
    :raises AssertionError: If returned value does not match expected
    :return: None
    :rtype: None
    """
    mock_session = mock.Mock()
    mock_session.commit = mock.AsyncMock()
    mock_session.refresh = mock.AsyncMock()
    mock_session.rollback = mock.AsyncMock()
    mock_session.execute = mock.AsyncMock()

    execute_result = mock.Mock()
    scalars_mock = mock.Mock()
    scalars_mock.unique.return_value.first.return_value = result_object
    execute_result.scalars.return_value = scalars_mock
    mock_session.execute.return_value = execute_result

    result = await characters.character_exists(mock_session, "Luke Skywalker")
    assert result is expected


@pytest.mark.asyncio
async def test_get_character_found(mocker, fake_result, fake_character):
    """
    Tests get_character returns a Character when found by ID.

    :param mocker: pytest-mock fixture to patch session
    :type mocker: pytest_mock.plugin.MockerFixture
    :param fake_result: Mock SQLAlchemy result with Character
    :type fake_result: mock.Mock
    :param fake_character: Expected Character object
    :type fake_character: Character
    :raises AssertionError: If result is not the expected Character
    :return: None
    :rtype: None
    """
    mock_session = mock.Mock()
    mock_session.commit = mock.AsyncMock()
    mock_session.refresh = mock.AsyncMock()
    mock_session.rollback = mock.AsyncMock()
    mock_session.execute = mock.AsyncMock()

    mock_session.execute.return_value = fake_result

    result = await characters.get_character(mock_session, 1)
    assert result == fake_character


@pytest.mark.asyncio
async def test_get_character_not_found(mocker):
    """
    Tests get_character returns None when no record is found.

    :param mocker: pytest-mock fixture to patch session
    :type mocker: pytest_mock.plugin.MockerFixture
    :raises AssertionError: If result is not None
    :return: None
    :rtype: None
    """
    mock_session = mock.Mock()
    mock_session.commit = mock.AsyncMock()
    mock_session.refresh = mock.AsyncMock()
    mock_session.rollback = mock.AsyncMock()
    mock_session.execute = mock.AsyncMock()

    execute_result = mock.Mock()
    scalars_mock = mock.Mock()
    scalars_mock.unique.return_value.first.return_value = None
    execute_result.scalars.return_value = scalars_mock
    mock_session.execute.return_value = execute_result

    result = await characters.get_character(mock_session, 999)
    assert result is None


@pytest.mark.asyncio
async def test_list_characters(mocker, fake_result, fake_character):
    """
    Tests list_characters returns list of Character objects with pagination.

    :param mocker: pytest-mock fixture to patch session
    :type mocker: pytest_mock.plugin.MockerFixture
    :param fake_result: Mock SQLAlchemy result with Character list
    :type fake_result: mock.Mock
    :param fake_character: Expected Character object
    :type fake_character: Character
    :raises AssertionError: If result list is incorrect
    :return: None
    :rtype: None
    """
    mock_session = mock.Mock()
    mock_session.commit = mock.AsyncMock()
    mock_session.refresh = mock.AsyncMock()
    mock_session.rollback = mock.AsyncMock()
    mock_session.execute = mock.AsyncMock()

    mock_session.execute.return_value = fake_result

    result = await characters.list_characters(mock_session, skip=0, limit=10)
    assert result == [fake_character]


@pytest.mark.asyncio
async def test_list_characters_empty(mocker):
    """
    Tests list_characters returns empty list when no records found.

    :param mocker: pytest-mock fixture to patch session
    :type mocker: pytest_mock.plugin.MockerFixture
    :raises AssertionError: If result is not empty list
    :return: None
    :rtype: None
    """
    mock_session = mock.Mock()
    mock_session.commit = mock.AsyncMock()
    mock_session.refresh = mock.AsyncMock()
    mock_session.rollback = mock.AsyncMock()
    mock_session.execute = mock.AsyncMock()

    execute_result = mock.Mock()
    scalars_mock = mock.Mock()
    scalars_mock.unique.return_value.all.return_value = []
    execute_result.scalars.return_value = scalars_mock
    mock_session.execute.return_value = execute_result

    result = await characters.list_characters(mock_session, skip=0, limit=10)
    assert result == []


@pytest.mark.asyncio
async def test_search_characters_by_name(mocker, fake_result, fake_character):
    """
    Tests search_characters_by_name returns matching Character list.

    :param mocker: pytest-mock fixture to patch session
    :type mocker: pytest_mock.plugin.MockerFixture
    :param fake_result: Mock SQLAlchemy result with Character list
    :type fake_result: mock.Mock
    :param fake_character: Expected Character object
    :type fake_character: Character
    :raises AssertionError: If result list is incorrect
    :return: None
    :rtype: None
    """
    mock_session = mock.Mock()
    mock_session.commit = mock.AsyncMock()
    mock_session.refresh = mock.AsyncMock()
    mock_session.rollback = mock.AsyncMock()
    mock_session.execute = mock.AsyncMock()

    mock_session.execute.return_value = fake_result

    result = await characters.search_characters_by_name(mock_session, "Luke")
    assert result == [fake_character]


@pytest.mark.asyncio
async def test_search_characters_by_name_empty(mocker):
    """
    Tests search_characters_by_name returns empty list when no matches.

    :param mocker: pytest-mock fixture to patch session
    :type mocker: pytest_mock.plugin.MockerFixture
    :raises AssertionError: If result is not empty list
    :return: None
    :rtype: None
    """
    mock_session = mock.Mock()
    mock_session.commit = mock.AsyncMock()
    mock_session.refresh = mock.AsyncMock()
    mock_session.rollback = mock.AsyncMock()
    mock_session.execute = mock.AsyncMock()

    execute_result = mock.Mock()
    scalars_mock = mock.Mock()
    scalars_mock.unique.return_value.all.return_value = []
    execute_result.scalars.return_value = scalars_mock
    mock_session.execute.return_value = execute_result

    result = await characters.search_characters_by_name(mock_session, "Nobody")
    assert result == []
