"""
tests.schemas.test_common.py

================================================================================
Unit Tests for src.schemas.common
================================================================================

Purpose
-------
Achieve 100% coverage of the generic response schemas:
- MessageResponse
- CharacterImportErrorResponse
- FilmImportErrorResponse
- StarshipImportErrorResponse

Tests
-----
- Successful instantiation with valid data
- Serialization to dict and JSON
- Validation errors on missing required fields

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com>
"""

import pytest
from pydantic import ValidationError

from src.schemas.common import (
    CharacterImportErrorResponse,
    FilmImportErrorResponse,
    MessageResponse,
    StarshipImportErrorResponse,
)


def test_message_response_valid():
    """
    Tests that MessageResponse can be instantiated with valid data
    and serializes correctly to dict and JSON.

    :raises AssertionError: If field value or serialization output is incorrect
    :return: None
    :rtype: None
    """
    model = MessageResponse(message="Import completed")
    assert model.message == "Import completed"
    assert model.model_dump() == {"message": "Import completed"}
    assert "Import completed" in model.model_dump_json()


def test_message_response_missing_field():
    """
    Tests that MessageResponse raises ValidationError when required field is missing.

    :raises ValidationError: If instantiation without 'message' field does not raise error
    :return: None
    :rtype: None
    """
    with pytest.raises(ValidationError):
        MessageResponse()


def test_character_import_error_response_valid():
    """
    Tests that CharacterImportErrorResponse can be instantiated with valid data
    and serializes correctly to dict and JSON.

    :raises AssertionError: If field value or serialization output is incorrect
    :return: None
    :rtype: None
    """
    model = CharacterImportErrorResponse(error="Failed to import characters")
    assert model.error == "Failed to import characters"
    assert model.model_dump() == {"error": "Failed to import characters"}
    assert "Failed to import characters" in model.model_dump_json()


def test_character_import_error_response_missing_field():
    """
    Tests that CharacterImportErrorResponse raises ValidationError when required field is missing.

    :raises ValidationError: If instantiation without 'error' field does not raise error
    :return: None
    :rtype: None
    """
    with pytest.raises(ValidationError):
        CharacterImportErrorResponse()


def test_film_import_error_response_valid():
    """
    Tests that FilmImportErrorResponse can be instantiated with valid data
    and serializes correctly to dict and JSON.

    :raises AssertionError: If field value or serialization output is incorrect
    :return: None
    :rtype: None
    """
    model = FilmImportErrorResponse(error="Failed to import films")
    assert model.error == "Failed to import films"
    assert model.model_dump() == {"error": "Failed to import films"}
    assert "Failed to import films" in model.model_dump_json()


def test_film_import_error_response_missing_field():
    """
    Tests that FilmImportErrorResponse raises ValidationError when required field is missing.

    :raises ValidationError: If instantiation without 'error' field does not raise error
    :return: None
    :rtype: None
    """
    with pytest.raises(ValidationError):
        FilmImportErrorResponse()


def test_starship_import_error_response_valid():
    """
    Tests that StarshipImportErrorResponse can be instantiated with valid data
    and serializes correctly to dict and JSON.

    :raises AssertionError: If field value or serialization output is incorrect
    :return: None
    :rtype: None
    """
    model = StarshipImportErrorResponse(error="Failed to import starships")
    assert model.error == "Failed to import starships"
    assert model.model_dump() == {"error": "Failed to import starships"}
    assert "Failed to import starships" in model.model_dump_json()


def test_starship_import_error_response_missing_field():
    """
    Tests that StarshipImportErrorResponse raises ValidationError when required field is missing.

    :raises ValidationError: If instantiation without 'error' field does not raise error
    :return: None
    :rtype: None
    """
    with pytest.raises(ValidationError):
        StarshipImportErrorResponse()
