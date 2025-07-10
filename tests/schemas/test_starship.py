"""
tests.schemas.test_starship

================================================================================
Unit Tests for Starship Pydantic Schemas
================================================================================

Overview
--------
Validates the Pydantic models defined in `src.schemas.starship` to ensure correct
validation, type safety, and serialization of starship-related data in the
SWAPI Voting API. This includes the base schema, creation schema, and response
schema with database ID support.

Tested Responsibilities
------------------------
- Import-level sanity checks for all schema classes
- Field-level validation and strict type enforcement
- Rejection of unknown or extra fields
- Proper configuration (e.g., `strict`, `extra`, `from_attributes`)

Key Characteristics
--------------------
- Guarantees consistent API contract for starship-related endpoints
- Ensures 100% test coverage of all schema paths and validation logic
- Includes both positive (valid) and negative (invalid) test scenarios
- Fully compatible with FastAPI's automatic OpenAPI documentation

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

import pytest
from pydantic import ValidationError

from src.schemas import starship


def test_importable():
    """
    Tests that all Starship-related schema classes can be imported without error.

    :raises AssertionError: If any expected schema class is missing or incorrect
    :return: None
    :rtype: None
    """
    assert isinstance(starship.StarshipBase, type)
    assert isinstance(starship.StarshipCreate, type)
    assert isinstance(starship.StarshipResponse, type)


def test_starship_base_fields_and_config():
    """
    Tests StarshipBase schema fields, type enforcement, strict config,
    and rejection of unknown extra fields.

    :raises AssertionError: If field values or config are incorrect
    :raises ValidationError: If extra fields do not raise error
    :return: None
    :rtype: None
    """
    schema = starship.StarshipBase(
        name="Millennium Falcon",
        model="YT-1300",
        manufacturer="Corellian Engineering Corporation",
        starship_class="Light Freighter",
    )

    assert schema.name == "Millennium Falcon"
    assert schema.model == "YT-1300"
    assert schema.manufacturer == "Corellian Engineering Corporation"
    assert schema.starship_class == "Light Freighter"

    assert schema.model_config["strict"] is True
    assert schema.model_config["extra"] == "forbid"

    with pytest.raises(ValidationError):
        starship.StarshipBase(name="X-Wing", extra_field="not allowed")


def test_starship_create_inherits_base():
    """
    Tests that StarshipCreate schema inherits from StarshipBase
    and enforces strict validation.

    :raises AssertionError: If field inheritance fails or values are incorrect
    :raises ValidationError: If extra fields do not raise error
    :return: None
    :rtype: None
    """
    schema = starship.StarshipCreate(name="Slave I")
    assert schema.name == "Slave I"

    with pytest.raises(ValidationError):
        starship.StarshipCreate(name="Slave I", extra_field="nope")


def test_starship_response_fields_and_config():
    """
    Tests StarshipResponse schema fields with database ID support,
    strict config, and extra=forbid enforcement.

    :raises AssertionError: If field values or config are incorrect
    :raises ValidationError: If extra fields do not raise error
    :return: None
    :rtype: None
    """
    schema = starship.StarshipResponse(
        id=1,
        name="Executor",
        model="Super-class Star Dreadnought",
        manufacturer="Kuat Drive Yards",
        starship_class="Dreadnought",
    )

    assert schema.id == 1
    assert schema.name == "Executor"
    assert schema.model == "Super-class Star Dreadnought"
    assert schema.manufacturer == "Kuat Drive Yards"
    assert schema.starship_class == "Dreadnought"

    assert schema.model_config["strict"] is True
    assert schema.model_config["extra"] == "forbid"
    assert schema.model_config["from_attributes"] is True

    with pytest.raises(ValidationError):
        starship.StarshipResponse(id=1, name="Executor", extra_field="bad")
