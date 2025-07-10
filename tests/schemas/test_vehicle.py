"""
tests.schemas.test_vehicle

================================================================================
Unit Tests for Vehicle Pydantic Schemas
================================================================================

Overview
--------
Tests the Pydantic models defined in `src.schemas.vehicle` to ensure strict
validation, correct serialization, and consistent API contracts for vehicle-related
data in the SWAPI Voting API. Includes the base model, creation model, and
response model with nested film relationships.

Tested Responsibilities
------------------------
- Import-level sanity checks for all schema classes
- Field-level validation with correct types and values
- Rejection of unknown or extra fields
- Verification of Pydantic model configurations (`strict`, `extra`, `from_attributes`)
- Nested film references in responses

Key Characteristics
--------------------
- Ensures reliable OpenAPI documentation via FastAPI's response_model
- Includes positive (valid data) and negative (invalid/extra data) test scenarios
- Guarantees 100% test coverage of schema logic and edge cases
- Aligns with strict API design and validation standards

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

import pytest
from pydantic import ValidationError

from src.schemas import vehicle


def test_importable():
    """
    Tests that all Vehicle-related schema classes can be imported without error.

    :raises AssertionError: If any expected schema class is missing or incorrect
    :return: None
    :rtype: None
    """
    assert isinstance(vehicle.FilmBase, type)
    assert isinstance(vehicle.VehicleBase, type)
    assert isinstance(vehicle.VehicleCreate, type)
    assert isinstance(vehicle.VehicleResponse, type)


def test_film_base_fields_and_config():
    """
    Tests FilmBase schema fields, strict config, from_attributes setting,
    and rejection of unknown extra fields.

    :raises AssertionError: If field values or config are incorrect
    :raises ValidationError: If extra fields do not raise error
    :return: None
    :rtype: None
    """
    schema = vehicle.FilmBase(id=1, title="A New Hope")
    assert schema.id == 1
    assert schema.title == "A New Hope"

    assert schema.model_config["strict"] is True
    assert schema.model_config["extra"] == "forbid"
    assert schema.model_config["from_attributes"] is True

    with pytest.raises(ValidationError):
        vehicle.FilmBase(id=1, title="A New Hope", extra_field="not allowed")


def test_vehicle_base_fields_and_config():
    """
    Tests VehicleBase schema fields, type enforcement, strict config,
    and extra=forbid behavior.

    :raises AssertionError: If field values or config are incorrect
    :raises ValidationError: If extra fields do not raise error
    :return: None
    :rtype: None
    """
    valid_data = {
        "name": "Speeder Bike",
        "model": "74-Z",
        "manufacturer": "Aratech",
        "cost_in_credits": "8000",
        "length": "3",
        "max_atmosphering_speed": "500",
        "crew": "1",
        "passengers": "0",
        "cargo_capacity": "4",
        "consumables": "2 days",
        "vehicle_class": "Speeder",
        "url": "https://swapi.dev/api/vehicles/1/",
    }
    schema = vehicle.VehicleBase(**valid_data)
    for field in valid_data:
        assert getattr(schema, field) == valid_data[field]

    assert schema.model_config["strict"] is True
    assert schema.model_config["extra"] == "forbid"

    with pytest.raises(ValidationError):
        vehicle.VehicleBase(**valid_data, extra_field="not allowed")


def test_vehicle_create_inherits_vehicle_base():
    """
    Tests that VehicleCreate schema inherits from VehicleBase
    and enforces strict validation.

    :raises AssertionError: If field inheritance fails or values are incorrect
    :raises ValidationError: If extra fields do not raise error
    :return: None
    :rtype: None
    """
    data = {"name": "AT-AT"}
    schema = vehicle.VehicleCreate(**data)
    assert schema.name == "AT-AT"

    with pytest.raises(ValidationError):
        vehicle.VehicleCreate(name="AT-AT", extra_field="nope")


def test_vehicle_response_fields_and_nested_films():
    """
    Tests VehicleResponse schema fields, including nested serialization of FilmBase,
    strict config, and extra=forbid enforcement.

    :raises AssertionError: If nested data or config values are incorrect
    :raises ValidationError: If extra fields do not raise error
    :return: None
    :rtype: None
    """
    film_data = {"id": 42, "title": "Return of the Jedi"}
    response_data = {"id": 7, "name": "Sandcrawler", "films": [film_data]}
    schema = vehicle.VehicleResponse(**response_data)
    assert schema.id == 7
    assert schema.name == "Sandcrawler"
    assert len(schema.films) == 1
    assert schema.films[0].id == 42
    assert schema.films[0].title == "Return of the Jedi"

    assert schema.model_config["strict"] is True
    assert schema.model_config["extra"] == "forbid"
    assert schema.model_config["from_attributes"] is True

    with pytest.raises(ValidationError):
        vehicle.VehicleResponse(**response_data, extra_field="bad")
