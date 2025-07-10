"""
src.api.exception_handlers

================================================================================
FastAPI Exception Handlers
================================================================================

Overview
--------
This module defines custom exception handlers for FastAPI routes.
It intercepts application-specific exceptions and returns consistent,
structured JSON error responses with appropriate HTTP status codes.

Responsibilities
----------------
- Handle ExternalAPIError for upstream API failures
- Handle DataImportError for internal data transformation/validation failures
- Handle DatabaseError for database integrity or transactional errors
- Return meaningful HTTP status codes and error payloads to clients

Key Characteristics
--------------------
- Structured JSON error responses
- Consistent error schema across the API
- Plug-and-play compatibility with FastAPI router.include_router()

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

from fastapi import Request
from fastapi.responses import JSONResponse

from src.exceptions.custom_exceptions import (
    DatabaseError,
    DataImportError,
    ExternalAPIError,
)


async def external_api_error_handler(request: Request, exc: Exception):
    """
    Handle ExternalAPIError exceptions.

    Returns a 502 Bad Gateway response indicating failure to contact
    an upstream service (e.g., SWAPI).

    :param request: The incoming HTTP request
    :type request: Request
    :param exc: The raised ExternalAPIError
    :type exc: ExternalAPIError
    :return: JSONResponse with error details
    :rtype: JSONResponse
    """
    if not isinstance(exc, ExternalAPIError):
        raise exc
    return JSONResponse(
        status_code=502,
        content={
            "error": "External API Error",
            "message": str(exc),
            "details": getattr(exc, "details", {}),
        },
    )


async def data_import_error_handler(request: Request, exc: Exception):
    """
    Handle DataImportError exceptions.

    Returns a 500 Internal Server Error response indicating a failure
    during data transformation, validation, or business rules.

    :param request: The incoming HTTP request
    :type request: Request
    :param exc: The raised DataImportError
    :type exc: DataImportError
    :return: JSONResponse with error details
    :rtype: JSONResponse
    """
    if not isinstance(exc, DataImportError):
        raise exc
    return JSONResponse(
        status_code=500,
        content={
            "error": "Data Import Error",
            "message": str(exc),
            "details": getattr(exc, "details", {}),
        },
    )


async def database_error_handler(request: Request, exc: Exception):
    """
    Handle DatabaseError exceptions.

    Returns a 400 Bad Request response indicating a failure in
    database integrity constraints or transaction handling.

    :param request: The incoming HTTP request
    :type request: Request
    :param exc: The raised DatabaseError
    :type exc: DatabaseError
    :return: JSONResponse with error details
    :rtype: JSONResponse
    """
    if not isinstance(exc, DatabaseError):
        raise exc
    return JSONResponse(
        status_code=400,
        content={
            "error": "Database Error",
            "message": str(exc),
            "details": getattr(exc, "details", {}),
        },
    )
