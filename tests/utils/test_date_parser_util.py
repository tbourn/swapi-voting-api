"""
tests.utils.test_date_parser_util

================================================================================
Unit Tests for Date Parsing Utilities
================================================================================

Overview
--------
Tests the functions in `src.utils.date_parser_util`, which provide robust parsing
for ISO-8601 date and datetime strings. Ensures correct conversion to Python
`datetime.date` and `datetime.datetime` objects, with graceful handling of invalid
input formats.

Tested Responsibilities
------------------------
- `parse_iso_date`: Parses ISO date strings (e.g., "YYYY-MM-DD")
- `parse_iso_datetime`: Parses ISO datetime strings, including those with "Z" (UTC)

Key Characteristics
--------------------
- Verifies successful parsing for valid ISO formats
- Confirms return of `None` for `None` input
- Asserts fallback to `None` and error logging on invalid input
- Uses pytest fixtures to capture and inspect `log_error` calls

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

import datetime

import pytest

from src.utils import date_parser_util


@pytest.fixture
def mock_log_error(monkeypatch):
    """
    Pytest fixture that patches the log_error function in date_parser_util.

    :param monkeypatch: Pytest's monkeypatch fixture for modifying module attributes
    :type monkeypatch: _pytest.monkeypatch.MonkeyPatch
    :return: A list capturing all calls to the fake_log_error, with tuples of (err, function_name, context)
    :rtype: list
    """
    called = []

    def fake_log_error(err, function_name=None, context=None):
        called.append((err, function_name, context))

    monkeypatch.setattr(date_parser_util, "log_error", fake_log_error)
    return called


def test_parse_iso_date_valid(mock_log_error):
    """
    Tests parsing of a valid ISO-8601 date string.

    :param mock_log_error: Captures calls to the patched log_error function
    :type mock_log_error: list
    :return: None
    :rtype: None
    """
    result = date_parser_util.parse_iso_date("2024-07-15")
    assert isinstance(result, datetime.date)
    assert result == datetime.date(2024, 7, 15)
    assert not mock_log_error


def test_parse_iso_date_none_input(mock_log_error):
    """
    Tests that None input returns None without errors.

    :param mock_log_error: Captures log_error calls
    :type mock_log_error: list
    :return: None
    :rtype: None
    """
    assert date_parser_util.parse_iso_date(None) is None
    assert not mock_log_error


def test_parse_iso_date_invalid_format(mock_log_error):
    """
    Tests that an invalid date format returns None and logs an error.

    :param mock_log_error: Captures log_error calls
    :type mock_log_error: list
    :return: None
    :rtype: None
    """
    result = date_parser_util.parse_iso_date("15/07/2024")
    assert result is None
    assert len(mock_log_error) == 1
    err, func, ctx = mock_log_error[0]
    assert func == "parse_iso_date"
    assert "value" in ctx
    assert ctx["value"] == "15/07/2024"


def test_parse_iso_datetime_valid_iso(mock_log_error):
    """
    Tests parsing of a valid ISO-8601 datetime string without timezone.

    :param mock_log_error: Captures log_error calls
    :type mock_log_error: list
    :return: None
    :rtype: None
    """
    result = date_parser_util.parse_iso_datetime("2024-07-15T12:34:56")
    assert isinstance(result, datetime.datetime)
    assert result.year == 2024
    assert result.month == 7
    assert result.day == 15
    assert result.hour == 12
    assert result.minute == 34
    assert result.second == 56
    assert not mock_log_error


def test_parse_iso_datetime_valid_with_z(mock_log_error):
    """
    Tests parsing of a valid ISO-8601 datetime string with 'Z' UTC suffix.

    :param mock_log_error: Captures log_error calls
    :type mock_log_error: list
    :return: None
    :rtype: None
    """
    result = date_parser_util.parse_iso_datetime("2024-07-15T12:34:56Z")
    assert isinstance(result, datetime.datetime)
    assert result.tzinfo is not None
    assert result.utcoffset().total_seconds() == 0
    assert not mock_log_error


def test_parse_iso_datetime_none_input(mock_log_error):
    """
    Tests that None input returns None without logging errors.

    :param mock_log_error: Captures log_error calls
    :type mock_log_error: list
    :return: None
    :rtype: None
    """
    assert date_parser_util.parse_iso_datetime(None) is None
    assert not mock_log_error


def test_parse_iso_datetime_invalid_format(mock_log_error):
    """
    Tests that an invalid datetime string returns None and logs an error.

    :param mock_log_error: Captures log_error calls
    :type mock_log_error: list
    :return: None
    :rtype: None
    """
    result = date_parser_util.parse_iso_datetime("invalid-timestamp")
    assert result is None
    assert len(mock_log_error) == 1
    err, func, ctx = mock_log_error[0]
    assert func == "parse_iso_datetime"
    assert "value" in ctx
    assert ctx["value"] == "invalid-timestamp"
