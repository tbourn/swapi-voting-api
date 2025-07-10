"""
src.exceptions.custom_exceptions

================================================================================
Custom Exceptions for SWAPI Voting API
================================================================================

Overview
--------
This module defines custom exception classes for clearer, consistent error
handling across the service. These can be raised in services and caught
in FastAPI exception handlers to produce clean HTTP responses.

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

from typing import Any, Dict, Optional


class ExternalAPIError(Exception):
    """
    Raised when an error occurs while calling an external API like SWAPI.

    :param message: The error message describing the failure.
    :type message: str
    :param details: Optional dictionary containing additional error details.
    :type details: Optional[Dict[str, Any]]
    """

    def __init__(self, message: str, *, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.details = details or {}


class DataImportError(Exception):
    """
    Raised when importing SWAPI data into the local database fails in a structured way.

    :param message: The error message describing the failure during import.
    :type message: str
    :param details: Optional dictionary containing additional error details.
    :type details: Optional[Dict[str, Any]]
    """

    def __init__(self, message: str, *, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.details = details or {}


class DatabaseError(Exception):
    """
    Raised for errors related to database operations, such as integrity or connection issues.

    :param message: The error message describing the database failure.
    :type message: str
    :param details: Optional dictionary containing additional error details.
    :type details: Optional[Dict[str, Any]]
    """

    def __init__(self, message: str, *, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.details = details or {}
