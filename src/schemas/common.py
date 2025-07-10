"""
src.schemas.common

================================================================================
Pydantic Schemas for Generic API Responses
================================================================================

Overview
--------
Defines the shared Pydantic models for standardizing generic response payloads
across the SWAPI Voting API. These schemas ensure consistent structure for
success and error messages in the OpenAPI documentation and runtime responses.

Responsibilities
----------------
- Provide a standard schema for success message responses (e.g. imports)
- Provide specific error schemas for character, film, and starship imports
- Ensure type safety and explicit contracts for client-side consumption

Key Characteristics
--------------------
- Fully compatible with FastAPI response_model
- Enables automatic and clear OpenAPI generation
- Strict validation with Pydantic BaseModel

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

from pydantic import BaseModel


class MessageResponse(BaseModel):
    """
    Schema for returning a standard success message in API responses.

    Used to communicate completion or success of operations such as
    SWAPI data imports.

    :param message: Human-readable success message.
    :type message: str
    """

    message: str


class CharacterImportErrorResponse(BaseModel):
    """
    Schema for returning character import errors in API responses.

    Used to provide a standardized error message when character
    data import from SWAPI fails.

    :param error: Error description explaining the failure.
    :type error: str
    """

    error: str


class FilmImportErrorResponse(BaseModel):
    """
    Schema for returning film import errors in API responses.

    Used to provide a standardized error message when film
    data import from SWAPI fails.

    :param error: Error description explaining the failure.
    :type error: str
    """

    error: str


class StarshipImportErrorResponse(BaseModel):
    """
    Schema for returning starship import errors in API responses.

    Used to provide a standardized error message when starship
    data import from SWAPI fails.

    :param error: Error description explaining the failure.
    :type error: str
    """

    error: str
