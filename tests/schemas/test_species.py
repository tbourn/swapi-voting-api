"""
tests.schemas.test_species

================================================================================
Unit Tests for Species Pydantic Schemas
================================================================================

Overview
--------
Validates the Pydantic models defined in `src.schemas.species` to ensure correct
validation, type safety, and serialization of species-related data in the
SWAPI Voting API. This includes the base species schema, creation schema,
and response schema with nested film relationships.

Tested Responsibilities
------------------------
- Import-level sanity checks for all schema classes
- Field-level validation and strict type enforcement
- Rejection of unknown or extra fields
- Serialization of nested films in SpeciesResponse
- Model configuration (e.g., `strict`, `extra`, `from_attributes`)

Key Characteristics
--------------------
- Guarantees consistent API contract for species-related endpoints
- Ensures 100% test coverage of schema paths and validation logic
- Includes both positive (valid) and negative (invalid) test scenarios
- Fully compatible with FastAPI's automatic OpenAPI documentation

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

import pytest
from pydantic import ValidationError

from src.schemas import species


def test_importable():
    """
    Tests that all Species-related schema classes can be imported without error.

    :raises AssertionError: If any expected schema class is missing or incorrect
    :return: None
    :rtype: None
    """
    assert isinstance(species.FilmBase, type)
    assert isinstance(species.SpeciesBase, type)
    assert isinstance(species.SpeciesCreate, type)
    assert isinstance(species.SpeciesResponse, type)


def test_film_base_fields_and_config():
    """
    Tests FilmBase schema fields, strict config, from_attributes setting,
    and rejection of unknown extra fields.

    :raises AssertionError: If field values or config are incorrect
    :raises ValidationError: If extra fields do not raise error
    :return: None
    :rtype: None
    """
    schema = species.FilmBase(id=1, title="A New Hope")
    assert schema.id == 1
    assert schema.title == "A New Hope"

    assert schema.model_config["strict"] is True
    assert schema.model_config["extra"] == "forbid"
    assert schema.model_config["from_attributes"] is True

    with pytest.raises(ValidationError):
        species.FilmBase(id=1, title="A New Hope", extra_field="not allowed")


def test_species_base_fields_and_config():
    """
    Tests SpeciesBase schema fields, type enforcement, strict config,
    and extra=forbid behavior.

    :raises AssertionError: If field values or config are incorrect
    :raises ValidationError: If extra fields do not raise error
    :return: None
    :rtype: None
    """
    valid_data = {
        "name": "Wookiee",
        "classification": "Mammal",
        "designation": "Sentient",
        "average_height": "210",
        "skin_colors": "gray",
        "hair_colors": "brown",
        "eye_colors": "blue",
        "average_lifespan": "400",
        "language": "Shyriiwook",
        "url": "https://swapi.dev/api/species/3/",
    }

    schema = species.SpeciesBase(**valid_data)
    for field in valid_data:
        assert getattr(schema, field) == valid_data[field]

    assert schema.model_config["strict"] is True
    assert schema.model_config["extra"] == "forbid"

    with pytest.raises(ValidationError):
        species.SpeciesBase(**valid_data, extra_field="nope")


def test_species_create_inherits_base():
    """
    Tests that SpeciesCreate schema inherits from SpeciesBase
    and enforces strict validation.

    :raises AssertionError: If field inheritance fails or values are incorrect
    :raises ValidationError: If extra fields do not raise error
    :return: None
    :rtype: None
    """
    data = {"name": "Rodian"}
    schema = species.SpeciesCreate(**data)
    assert schema.name == "Rodian"

    with pytest.raises(ValidationError):
        species.SpeciesCreate(name="Rodian", extra_field="bad")


def test_species_response_fields_and_nested_films():
    """
    Tests SpeciesResponse schema fields, including nested serialization of FilmBase,
    strict config, and extra=forbid enforcement.

    :raises AssertionError: If nested data or config values are incorrect
    :raises ValidationError: If extra fields do not raise error
    :return: None
    :rtype: None
    """
    film_data = {"id": 10, "title": "Attack of the Clones"}
    response_data = {"id": 5, "name": "Twi'lek", "films": [film_data]}

    schema = species.SpeciesResponse(**response_data)
    assert schema.id == 5
    assert schema.name == "Twi'lek"
    assert len(schema.films) == 1
    assert schema.films[0].id == 10
    assert schema.films[0].title == "Attack of the Clones"

    assert schema.model_config["strict"] is True
    assert schema.model_config["extra"] == "forbid"
    assert schema.model_config["from_attributes"] is True

    with pytest.raises(ValidationError):
        species.SpeciesResponse(**response_data, extra_field="not allowed")
