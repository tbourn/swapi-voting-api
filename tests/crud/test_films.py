"""
tests.crud.test_films

================================================================================
Unit Tests for Film CRUD Operations
================================================================================

Overview
--------
Validates the async CRUD functions in `src.crud.films`, which handle
database interactions for Film entities using SQLAlchemy AsyncSession.

Tested Responsibilities
------------------------
- Creating new Film records, with error handling for IntegrityError
- Checking if a Film exists by title
- Fetching a Film by its ID
- Listing all Films with pagination support
- Searching Films by partial title match

Key Characteristics
--------------------
- Mocks AsyncSession methods including execute, add, commit, and refresh
- Simulates successful, failing, and empty query results
- Ensures database errors are translated to custom DatabaseError
- Enforces correct rollback behavior on IntegrityError

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

from unittest import mock

import pytest
from sqlalchemy.exc import IntegrityError

from src.crud import films
from src.exceptions.custom_exceptions import DatabaseError
from src.models.film import Film


@pytest.fixture
def fake_film():
    """
    Provides a mock Film model instance for testing CRUD operations.

    :return: Mock Film instance with predefined attributes
    :rtype: Film
    """
    return Film(id=1, title="A New Hope", characters=[])


@pytest.fixture
def fake_film_in():
    """
    Provides a mock Pydantic-like input object for film creation.

    :return: Mock object with .dict() method returning film data
    :rtype: mock.Mock
    """
    mock_in = mock.Mock()
    mock_in.dict.return_value = {"title": "A New Hope", "characters": []}
    return mock_in


@pytest.mark.asyncio
async def test_create_film_success(mocker, fake_film, fake_film_in):
    """
    Tests successful creation of a new Film record in the database.

    :param mocker: pytest-mock fixture to patch Film instantiation
    :type mocker: pytest_mock.plugin.MockerFixture
    :param fake_film: Mock Film instance to return
    :type fake_film: Film
    :param fake_film_in: Mock Pydantic input schema
    :type fake_film_in: mock.Mock
    :raises AssertionError: If add, commit, refresh are not called or result is incorrect
    :return: None
    :rtype: None
    """
    mock_session = mock.Mock()
    mock_session.commit = mock.AsyncMock()
    mock_session.refresh = mock.AsyncMock()

    mocker.patch("src.crud.films.Film", return_value=fake_film)

    result = await films.create_film(mock_session, fake_film_in)

    mock_session.add.assert_called_once_with(fake_film)
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(fake_film)
    assert result == fake_film


@pytest.mark.asyncio
async def test_create_film_integrity_error(mocker, fake_film_in):
    """
    Tests that creating a Film with integrity error rolls back and raises DatabaseError.

    :param mocker: pytest-mock fixture to patch logger
    :type mocker: pytest_mock.plugin.MockerFixture
    :param fake_film_in: Mock Pydantic input schema
    :type fake_film_in: mock.Mock
    :raises DatabaseError: On IntegrityError in commit
    :return: None
    :rtype: None
    """
    mock_session = mock.Mock()
    mock_session.commit = mock.AsyncMock(
        side_effect=IntegrityError("mock", "mock", "mock")
    )
    mock_session.rollback = mock.AsyncMock()

    mock_log = mocker.patch("src.crud.films.log_error")

    with pytest.raises(DatabaseError) as exc:
        await films.create_film(mock_session, fake_film_in)

    assert "Database integrity error" in str(exc.value)
    mock_session.rollback.assert_awaited_once()
    mock_log.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "scalar_result,expected",
    [
        (object(), True),
        (None, False),
    ],
)
async def test_film_exists(mocker, scalar_result, expected):
    """
    Tests film_exists returns True or False depending on query result.

    :param mocker: pytest-mock fixture for patching session
    :type mocker: pytest_mock.plugin.MockerFixture
    :param scalar_result: Object to simulate query result
    :type scalar_result: Any
    :param expected: Expected boolean result
    :type expected: bool
    :raises AssertionError: If returned value does not match expected
    :return: None
    :rtype: None
    """
    mock_session = mock.Mock()
    mock_session.execute = mock.AsyncMock()

    result_mock = mock.Mock()
    result_mock.unique.return_value.scalar_one_or_none.return_value = scalar_result
    mock_session.execute.return_value = result_mock

    result = await films.film_exists(mock_session, "A New Hope")
    assert result is expected


@pytest.mark.asyncio
async def test_get_film_found(mocker, fake_film):
    """
    Tests get_film returns a Film when found by ID.

    :param mocker: pytest-mock fixture to patch session
    :type mocker: pytest_mock.plugin.MockerFixture
    :param fake_film: Expected Film object
    :type fake_film: Film
    :raises AssertionError: If result is not the expected Film
    :return: None
    :rtype: None
    """
    mock_session = mock.Mock()
    mock_session.execute = mock.AsyncMock()

    result_mock = mock.Mock()
    result_mock.scalar_one_or_none.return_value = fake_film
    mock_session.execute.return_value = result_mock

    result = await films.get_film(mock_session, 1)
    assert result == fake_film


@pytest.mark.asyncio
async def test_get_film_not_found(mocker):
    """
    Tests get_film returns None when no record is found.

    :param mocker: pytest-mock fixture to patch session
    :type mocker: pytest_mock.plugin.MockerFixture
    :raises AssertionError: If result is not None
    :return: None
    :rtype: None
    """
    mock_session = mock.Mock()
    mock_session.execute = mock.AsyncMock()

    result_mock = mock.Mock()
    result_mock.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = result_mock

    result = await films.get_film(mock_session, 999)
    assert result is None


@pytest.mark.asyncio
async def test_list_films(mocker, fake_film):
    """
    Tests list_films returns list of Film objects with pagination.

    :param mocker: pytest-mock fixture to patch session
    :type mocker: pytest_mock.plugin.MockerFixture
    :param fake_film: Expected Film object
    :type fake_film: Film
    :raises AssertionError: If result list is incorrect
    :return: None
    :rtype: None
    """
    mock_session = mock.Mock()
    mock_session.execute = mock.AsyncMock()

    result_mock = mock.Mock()
    result_mock.scalars.return_value.all.return_value = [fake_film]
    mock_session.execute.return_value = result_mock

    result = await films.list_films(mock_session, skip=0, limit=10)
    assert result == [fake_film]


@pytest.mark.asyncio
async def test_list_films_empty(mocker):
    """
    Tests list_films returns empty list when no records found.

    :param mocker: pytest-mock fixture to patch session
    :type mocker: pytest_mock.plugin.MockerFixture
    :raises AssertionError: If result is not empty list
    :return: None
    :rtype: None
    """
    mock_session = mock.Mock()
    mock_session.execute = mock.AsyncMock()

    result_mock = mock.Mock()
    result_mock.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = result_mock

    result = await films.list_films(mock_session, skip=0, limit=10)
    assert result == []


@pytest.mark.asyncio
async def test_search_films_by_title(mocker, fake_film):
    """
    Tests search_films_by_title returns matching Film list.

    :param mocker: pytest-mock fixture to patch session
    :type mocker: pytest_mock.plugin.MockerFixture
    :param fake_film: Expected Film object
    :type fake_film: Film
    :raises AssertionError: If result list is incorrect
    :return: None
    :rtype: None
    """
    mock_session = mock.Mock()
    mock_session.execute = mock.AsyncMock()

    result_mock = mock.Mock()
    scalars_mock = mock.Mock()
    scalars_mock.all.return_value = [fake_film]
    result_mock.unique.return_value.scalars.return_value = scalars_mock
    mock_session.execute.return_value = result_mock

    result = await films.search_films_by_title(mock_session, "Hope")
    assert result == [fake_film]


@pytest.mark.asyncio
async def test_search_films_by_title_empty(mocker):
    """
    Tests search_films_by_title returns empty list when no matches.

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

    result = await films.search_films_by_title(mock_session, "Nothing")
    assert result == []
