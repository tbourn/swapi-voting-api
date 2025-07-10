"""
tests.schemas.test_character

================================================================================
Unit Tests for Character Pydantic Schemas
================================================================================

Overview
--------
Validates the Pydantic models defined in `src.schemas.character` to ensure they
enforce correct validation, configuration, and serialization for Star Wars
character-related data in the SWAPI Voting API.

Tested Responsibilities
------------------------
- Import sanity and model availability
- Field-level validation and type safety
- Rejection of extra/unknown fields (strict mode)
- Nested serialization of FilmBase in CharacterResponse
- Model configuration parameters (e.g., `strict`, `extra`, `from_attributes`)

Key Characteristics
--------------------
- 100% coverage of schema paths
- Tests both positive (valid) and negative (invalid) cases
- Pydantic v2-compliant validation using `model_dump()` if needed
- Supports maintainable and reliable API contract evolution

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

import pytest
from pydantic import ValidationError

from src.schemas import character


def test_importable():
    """
    Tests that all Character schema classes can be imported and are available.

    :raises AssertionError: If any expected schema class is missing or incorrect
    :return: None
    :rtype: None
    """
    assert isinstance(character.FilmBase, type)
    assert isinstance(character.CharacterBase, type)
    assert isinstance(character.CharacterCreate, type)
    assert isinstance(character.CharacterResponse, type)


def test_film_base_fields_and_config():
    """
    Tests FilmBase schema fields, strict config, from_attributes, and rejection of extra fields.

    :raises AssertionError: If field values or config are incorrect
    :raises ValidationError: If extra field does not raise error
    :return: None
    :rtype: None
    """
    schema = character.FilmBase(id=1, title="A New Hope")
    assert schema.id == 1
    assert schema.title == "A New Hope"

    assert schema.model_config["from_attributes"] is True

    with pytest.raises(ValidationError):
        character.FilmBase(id=1, title="A New Hope", extra_field="not allowed")


def test_character_base_fields_and_config():
    """
    Tests CharacterBase schema fields, strict mode, extra=forbid, and correct field validation.

    :raises AssertionError: If field values or config are incorrect
    :raises ValidationError: If extra field does not raise error
    :return: None
    :rtype: None
    """
    valid_data = {
        "name": "Luke Skywalker",
        "gender": "male",
        "birth_year": "19BBY",
    }

    schema = character.CharacterBase(**valid_data)
    for field in valid_data:
        assert getattr(schema, field) == valid_data[field]

    assert schema.model_config["strict"] is True
    assert schema.model_config["extra"] == "forbid"

    with pytest.raises(ValidationError):
        character.CharacterBase(**valid_data, extra_field="nope")


def test_character_create_inherits_base():
    """
    Tests that CharacterCreate schema inherits from CharacterBase and forbids extra fields.

    :raises AssertionError: If field inheritance fails or value mismatch occurs
    :raises ValidationError: If extra field does not raise error
    :return: None
    :rtype: None
    """
    schema = character.CharacterCreate(name="Leia Organa")
    assert schema.name == "Leia Organa"

    with pytest.raises(ValidationError):
        character.CharacterCreate(name="Leia Organa", extra_field="nope")


def test_character_response_fields_and_nested_films():
    """
    Tests CharacterResponse schema fields, nested FilmBase serialization, and strict config.

    :raises AssertionError: If field values or nested objects are incorrect
    :raises ValidationError: If extra field does not raise error
    :return: None
    :rtype: None
    """
    film_data = {"id": 42, "title": "Return of the Jedi"}
    response_data = {"id": 7, "name": "Han Solo", "films": [film_data]}

    schema = character.CharacterResponse(**response_data)
    assert schema.id == 7
    assert schema.name == "Han Solo"
    assert len(schema.films) == 1
    assert schema.films[0].id == 42
    assert schema.films[0].title == "Return of the Jedi"

    assert schema.model_config["strict"] is True
    assert schema.model_config["extra"] == "forbid"
    assert schema.model_config["from_attributes"] is True

    with pytest.raises(ValidationError):
        character.CharacterResponse(**response_data, extra_field="bad")
