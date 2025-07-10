"""
tests.schemas.test_planet

================================================================================
Unit Tests for Planet Pydantic Schemas
================================================================================

Overview
--------
Validates the Pydantic models defined in `src.schemas.planet` to ensure they
correctly enforce validation, type safety, and serialization for planet-related
data in the SWAPI Voting API. This includes the base planet schema, creation
schema, and response schema with nested film relationships.

Tested Responsibilities
------------------------
- Import-level sanity checks for all schema classes
- Field-level validation and type enforcement
- Strict rejection of unknown or extra fields
- Nested serialization of related films in PlanetResponse
- Model configuration (e.g., `strict`, `extra`, `from_attributes`)

Key Characteristics
--------------------
- Ensures consistent API contract for all planet-related data
- 100% test coverage of schema paths and validation logic
- Tests both positive (valid) and negative (invalid) scenarios
- Fully compatible with FastAPI's OpenAPI documentation generation

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

import pytest
from pydantic import ValidationError

from src.schemas import planet


def test_importable():
    """
    Tests that all Planet-related schema classes can be imported without error.

    :raises AssertionError: If any expected schema class is missing or incorrect
    :return: None
    :rtype: None
    """
    assert isinstance(planet.FilmBase, type)
    assert isinstance(planet.PlanetBase, type)
    assert isinstance(planet.PlanetCreate, type)
    assert isinstance(planet.PlanetResponse, type)


def test_film_base_fields_and_config():
    """
    Tests FilmBase schema fields, strict config, from_attributes setting,
    and rejection of unknown extra fields.

    :raises AssertionError: If field values or config are incorrect
    :raises ValidationError: If extra fields do not raise error
    :return: None
    :rtype: None
    """
    schema = planet.FilmBase(id=1, title="A New Hope")
    assert schema.id == 1
    assert schema.title == "A New Hope"

    assert schema.model_config["strict"] is True
    assert schema.model_config["extra"] == "forbid"
    assert schema.model_config["from_attributes"] is True

    with pytest.raises(ValidationError):
        planet.FilmBase(id=1, title="A New Hope", extra_field="not allowed")


def test_planet_base_fields_and_config():
    """
    Tests PlanetBase schema fields, type enforcement, strict config,
    and extra=forbid behavior.

    :raises AssertionError: If field values or config are incorrect
    :raises ValidationError: If extra fields do not raise error
    :return: None
    :rtype: None
    """
    valid_data = {
        "name": "Tatooine",
        "rotation_period": "23",
        "orbital_period": "304",
        "diameter": "10465",
        "climate": "arid",
        "gravity": "1 standard",
        "terrain": "desert",
        "surface_water": "1",
        "population": "200000",
        "url": "https://swapi.dev/api/planets/1/",
    }

    schema = planet.PlanetBase(**valid_data)
    for field in valid_data:
        assert getattr(schema, field) == valid_data[field]

    assert schema.model_config["strict"] is True
    assert schema.model_config["extra"] == "forbid"

    with pytest.raises(ValidationError):
        planet.PlanetBase(**valid_data, extra_field="bad")


def test_planet_create_inherits_base():
    """
    Tests that PlanetCreate schema inherits from PlanetBase
    and enforces strict validation.

    :raises AssertionError: If field inheritance fails or values are incorrect
    :raises ValidationError: If extra fields do not raise error
    :return: None
    :rtype: None
    """
    data = {"name": "Hoth"}
    schema = planet.PlanetCreate(**data)
    assert schema.name == "Hoth"

    with pytest.raises(ValidationError):
        planet.PlanetCreate(name="Hoth", extra_field="bad")


def test_planet_response_fields_and_nested_films():
    """
    Tests PlanetResponse schema fields, including nested serialization of FilmBase,
    strict config, and extra=forbid enforcement.

    :raises AssertionError: If nested data or config values are incorrect
    :raises ValidationError: If extra fields do not raise error
    :return: None
    :rtype: None
    """
    film_data = {"id": 4, "title": "The Phantom Menace"}
    response_data = {"id": 9, "name": "Naboo", "films": [film_data]}

    schema = planet.PlanetResponse(**response_data)
    assert schema.id == 9
    assert schema.name == "Naboo"
    assert len(schema.films) == 1
    assert schema.films[0].id == 4
    assert schema.films[0].title == "The Phantom Menace"

    assert schema.model_config["strict"] is True
    assert schema.model_config["extra"] == "forbid"
    assert schema.model_config["from_attributes"] is True

    with pytest.raises(ValidationError):
        planet.PlanetResponse(**response_data, extra_field="bad")
