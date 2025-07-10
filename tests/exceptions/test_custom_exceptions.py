"""
tests.exceptions.test_custom_exceptions

================================================================================
Unit Tests for Custom Exception Classes
================================================================================

Overview
--------
Verifies the behavior of custom exception types defined in
`src.exceptions.custom_exceptions`. These exceptions are used across the
application to provide consistent, structured error handling with optional
context details.

Tested Responsibilities
------------------------
- ExternalAPIError carries an error message and optional details dictionary
- DataImportError carries an error message and optional details dictionary
- DatabaseError carries an error message and optional details dictionary
- Ensures that details default to an empty dictionary when not provided
- Confirms string representation matches the message

Key Characteristics
--------------------
- Enforces explicit contract for error objects in FastAPI routes and services
- Supports structured error logging and client-facing JSON payloads
- Maintains type safety and clarity in exception handling across the project

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

import pytest

from src.exceptions import custom_exceptions


def test_external_api_error_with_details():
    """
    Tests ExternalAPIError carries message and provided details dictionary.

    :raises AssertionError: If message or details do not match expected values
    :return: None
    :rtype: None
    """
    exc = custom_exceptions.ExternalAPIError("API failed", details={"code": 500})
    assert str(exc) == "API failed"
    assert exc.details == {"code": 500}


def test_external_api_error_without_details():
    """
    Tests ExternalAPIError defaults details to empty dictionary when omitted.

    :raises AssertionError: If message or details are incorrect
    :return: None
    :rtype: None
    """
    exc = custom_exceptions.ExternalAPIError("API failed")
    assert str(exc) == "API failed"
    assert exc.details == {}


def test_data_import_error_with_details():
    """
    Tests DataImportError carries message and provided details dictionary.

    :raises AssertionError: If message or details do not match expected values
    :return: None
    :rtype: None
    """
    exc = custom_exceptions.DataImportError("Import failed", details={"row": 42})
    assert str(exc) == "Import failed"
    assert exc.details == {"row": 42}


def test_data_import_error_without_details():
    """
    Tests DataImportError defaults details to empty dictionary when omitted.

    :raises AssertionError: If message or details are incorrect
    :return: None
    :rtype: None
    """
    exc = custom_exceptions.DataImportError("Import failed")
    assert str(exc) == "Import failed"
    assert exc.details == {}


def test_database_error_with_details():
    """
    Tests DatabaseError carries message and provided details dictionary.

    :raises AssertionError: If message or details do not match expected values
    :return: None
    :rtype: None
    """
    exc = custom_exceptions.DatabaseError("DB failed", details={"constraint": "unique"})
    assert str(exc) == "DB failed"
    assert exc.details == {"constraint": "unique"}


def test_database_error_without_details():
    """
    Tests DatabaseError defaults details to empty dictionary when omitted.

    :raises AssertionError: If message or details are incorrect
    :return: None
    :rtype: None
    """
    exc = custom_exceptions.DatabaseError("DB failed")
    assert str(exc) == "DB failed"
    assert exc.details == {}
