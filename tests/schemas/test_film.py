"""
tests.schemas.test_film

================================================================================
Unit Tests for Film Pydantic Schemas
================================================================================

Overview
--------
Validates the Pydantic models defined in `src.schemas.film` to ensure they
correctly enforce validation, type safety, and serialization for film-related
data in the SWAPI Voting API. This includes the base film schema, creation
schema, and response schema with nested character, planet, starship, vehicle,
and species relationships.

Tested Responsibilities
------------------------
- Import-level sanity checks for all schema classes
- Field-level validation and type enforcement
- Strict rejection of unknown or extra fields
- Nested serialization of related resources in FilmResponse
- Model configuration (e.g., `strict`, `extra`, `from_attributes`)

Key Characteristics
--------------------
- Ensures consistent API contract for all film-related data
- 100% test coverage of schema paths and validation logic
- Tests both positive (valid) and negative (invalid) scenarios
- Compatible with FastAPI for OpenAPI documentation generation

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

from datetime import UTC, date, datetime

import pytest
from pydantic import ValidationError

from src.schemas import film


def test_importable():
    """
    Tests that all Film-related schema classes can be imported without error.

    :raises AssertionError: If any expected schema class is missing or incorrect
    :return: None
    :rtype: None
    """
    assert isinstance(film.CharacterBase, type)
    assert isinstance(film.PlanetBase, type)
    assert isinstance(film.StarshipBase, type)
    assert isinstance(film.VehicleBase, type)
    assert isinstance(film.SpeciesBase, type)
    assert isinstance(film.FilmBase, type)
    assert isinstance(film.FilmCreate, type)
    assert isinstance(film.FilmResponse, type)


@pytest.mark.parametrize(
    "cls",
    [
        film.CharacterBase,
        film.PlanetBase,
        film.StarshipBase,
        film.VehicleBase,
        film.SpeciesBase,
    ],
)
def test_minimal_nested_base_models(cls):
    """
    Tests minimal instantiation of nested base models with correct config and validation.

    :param cls: The schema class to instantiate
    :type cls: Type[pydantic.BaseModel]
    :raises AssertionError: If field values or config are incorrect
    :raises ValidationError: If extra fields do not raise error
    :return: None
    :rtype: None
    """
    schema = cls(id=1, name="Test Name")
    assert schema.id == 1
    assert schema.name == "Test Name"

    assert schema.model_config["strict"] is True
    assert schema.model_config["extra"] == "forbid"
    assert schema.model_config["from_attributes"] is True

    with pytest.raises(ValidationError):
        cls(id=1, name="Test Name", extra_field="not allowed")


def test_film_base_fields_and_config():
    """
    Tests FilmBase schema fields, type enforcement, strict config, and extra=forbid behavior.

    :raises AssertionError: If field values or config are incorrect
    :raises ValidationError: If extra fields do not raise error
    :return: None
    :rtype: None
    """
    valid_data = {
        "title": "The Empire Strikes Back",
        "episode_id": 5,
        "opening_crawl": "It is a dark time...",
        "director": "Irvin Kershner",
        "producer": "Gary Kurtz",
        "release_date": date(1980, 5, 21),
        "created": datetime.now(UTC),
        "edited": datetime.now(UTC),
        "url": "https://swapi.dev/api/films/2/",
    }

    schema = film.FilmBase(**valid_data)
    for key in valid_data:
        assert getattr(schema, key) == valid_data[key]

    assert schema.model_config["strict"] is True
    assert schema.model_config["extra"] == "forbid"

    with pytest.raises(ValidationError):
        film.FilmBase(**valid_data, extra_field="bad")


def test_film_create_inherits_film_base():
    """
    Tests that FilmCreate schema inherits from FilmBase and enforces strict validation.

    :raises AssertionError: If field inheritance fails or values are incorrect
    :raises ValidationError: If extra fields do not raise error
    :return: None
    :rtype: None
    """
    schema = film.FilmCreate(title="Return of the Jedi")
    assert schema.title == "Return of the Jedi"

    with pytest.raises(ValidationError):
        film.FilmCreate(title="Return of the Jedi", extra_field="not allowed")


def test_film_response_fields_and_nested_relationships():
    """
    Tests FilmResponse schema fields, including nested serialization of related resources,
    with strict config and extra=forbid enforcement.

    :raises AssertionError: If nested data or config values are incorrect
    :raises ValidationError: If extra fields do not raise error
    :return: None
    :rtype: None
    """
    nested_character = {"id": 1, "name": "Luke Skywalker"}
    nested_planet = {"id": 2, "name": "Dagobah"}
    nested_starship = {"id": 3, "name": "X-Wing"}
    nested_vehicle = {"id": 4, "name": "Speeder Bike"}
    nested_species = {"id": 5, "name": "Wookiee"}

    response_data = {
        "id": 99,
        "title": "A New Hope",
        "characters": [nested_character],
        "planets": [nested_planet],
        "starships": [nested_starship],
        "vehicles": [nested_vehicle],
        "species": [nested_species],
    }

    schema = film.FilmResponse(**response_data)
    assert schema.id == 99
    assert schema.title == "A New Hope"
    assert len(schema.characters) == 1
    assert schema.characters[0].id == 1
    assert schema.characters[0].name == "Luke Skywalker"

    assert len(schema.planets) == 1
    assert schema.planets[0].id == 2
    assert schema.planets[0].name == "Dagobah"

    assert len(schema.starships) == 1
    assert schema.starships[0].id == 3
    assert schema.starships[0].name == "X-Wing"

    assert len(schema.vehicles) == 1
    assert schema.vehicles[0].id == 4
    assert schema.vehicles[0].name == "Speeder Bike"

    assert len(schema.species) == 1
    assert schema.species[0].id == 5
    assert schema.species[0].name == "Wookiee"

    assert schema.model_config["strict"] is True
    assert schema.model_config["extra"] == "forbid"
    assert schema.model_config["from_attributes"] is True

    with pytest.raises(ValidationError):
        film.FilmResponse(**response_data, extra_field="bad")
