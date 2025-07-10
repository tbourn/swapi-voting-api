"""
tests.api.test_exception_handlers

================================================================================
Async Unit Tests for FastAPI Exception Handlers
================================================================================

Overview
--------
Tests the custom exception handler functions defined in src.api.exception_handlers
to ensure they return consistent, structured JSON responses with appropriate
HTTP status codes when raised in FastAPI routes.

Tested Responsibilities
------------------------
- Handles ExternalAPIError with 502 Bad Gateway response
- Handles DataImportError with 500 Internal Server Error response
- Handles DatabaseError with 400 Bad Request response
- Includes error message, details, and correct error type in JSON
- Raises when invoked with wrong exception types
- Handles cases where details attribute is missing

Key Characteristics
--------------------
- Fully async pytest-asyncio test suite
- Parameterized tests for multiple handlers and exception classes
- Validates response body structure, status codes, and JSON encoding
- Simulates FastAPI Request objects with SimpleNamespace

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

from types import SimpleNamespace

import pytest
from fastapi import Request
from fastapi.responses import JSONResponse

from src.api import exception_handlers
from src.exceptions import custom_exceptions


@pytest.fixture
def fake_request():
    return SimpleNamespace(url="/test")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "handler, exc_class, expected_status, expected_error",
    [
        (
            exception_handlers.external_api_error_handler,
            custom_exceptions.ExternalAPIError,
            502,
            "External API Error",
        ),
        (
            exception_handlers.data_import_error_handler,
            custom_exceptions.DataImportError,
            500,
            "Data Import Error",
        ),
        (
            exception_handlers.database_error_handler,
            custom_exceptions.DatabaseError,
            400,
            "Database Error",
        ),
    ],
)
async def test_handler_returns_correct_json(
    fake_request, handler, exc_class, expected_status, expected_error
):
    """
    Tests that the custom FastAPI exception handler returns the correct structured JSON response.

    :param fake_request: Simulated FastAPI Request object, defaults to SimpleNamespace with URL
    :type fake_request: Request
    :param handler: The exception handler function to test
    :type handler: Callable
    :param exc_class: The custom exception class to raise
    :type exc_class: Type[Exception]
    :param expected_status: Expected HTTP status code in the response
    :type expected_status: int
    :param expected_error: Expected error type string in the JSON body
    :type expected_error: str
    :raises AssertionError: If the response does not match expected structure, status code, or content
    :return: None
    :rtype: None
    """
    exc = exc_class("Test message", details={"key": "value"})

    response = await handler(fake_request, exc)

    assert isinstance(response, JSONResponse)
    assert response.status_code == expected_status
    assert response.body is not None
    body = response.body.decode()
    assert expected_error in body
    assert "Test message" in body
    assert "key" in body


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "handler, wrong_exc",
    [
        (
            exception_handlers.external_api_error_handler,
            custom_exceptions.DataImportError("oops"),
        ),
        (
            exception_handlers.data_import_error_handler,
            custom_exceptions.DatabaseError("oops"),
        ),
        (
            exception_handlers.database_error_handler,
            custom_exceptions.ExternalAPIError("oops"),
        ),
    ],
)
async def test_handler_wrong_exception_type_raises(fake_request, handler, wrong_exc):
    """
    Tests that the custom exception handler raises when passed the wrong exception type.

    :param fake_request: Simulated FastAPI Request object, defaults to SimpleNamespace with URL
    :type fake_request: Request
    :param handler: The exception handler function to test
    :type handler: Callable
    :param wrong_exc: An exception instance of an unexpected type
    :type wrong_exc: Exception
    :raises Exception: When the handler is invoked with the wrong exception type
    :return: None
    :rtype: None
    """
    with pytest.raises(Exception) as excinfo:
        await handler(fake_request, wrong_exc)
    assert str(wrong_exc) in str(excinfo.value)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "handler, exc_class",
    [
        (
            exception_handlers.external_api_error_handler,
            custom_exceptions.ExternalAPIError,
        ),
        (
            exception_handlers.data_import_error_handler,
            custom_exceptions.DataImportError,
        ),
        (exception_handlers.database_error_handler, custom_exceptions.DatabaseError),
    ],
)
async def test_handler_missing_details_attribute(fake_request, handler, exc_class):
    """
    Tests that the handler works even if the exception is missing the 'details' attribute.

    :param fake_request: Simulated FastAPI Request object, defaults to SimpleNamespace with URL
    :type fake_request: Request
    :param handler: The exception handler function to test
    :type handler: Callable
    :param exc_class: The custom exception class to instantiate without details
    :type exc_class: Type[Exception]
    :raises AssertionError: If the response does not contain expected minimal JSON
    :return: None
    :rtype: None
    """
    class MinimalExc(exc_class):
        """Minimal custom exception subclass with 'details' attribute intentionally removed
        to test handler robustness when optional data is missing.

        :param message: The error message describing the exception
        :type message: str
        :param args: Additional positional arguments passed to the base exception
        :type args: tuple, optional
        :raises AttributeError: If 'details' attribute exists and is removed
        """
        def __init__(self, message):
            super().__init__(message)
            if hasattr(self, "details"):
                del self.details

    exc = MinimalExc("Minimal")

    response = await handler(fake_request, exc)
    assert response.status_code in (400, 500, 502)
    body = response.body.decode()
    assert "Minimal" in body
    assert "{}" in body
