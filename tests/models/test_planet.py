"""
tests.models.test_planet

================================================================================
Unit Tests for Planet SQLAlchemy Model
================================================================================

Overview
--------
Validates the `Planet` ORM model in `src.models.planet`, ensuring the database
schema and relationships align with the SWAPI Voting API design.

Tested Responsibilities
------------------------
- Verifies correct table name declaration ("planets")
- Checks for expected columns and their constraints (primary key, unique, indexed)
- Ensures non-nullability of the name column
- Confirms all other columns are nullable as expected
- Validates many-to-many relationship with Films, including correct join table
- Confirms use of 'selectin' lazy loading strategy for efficient queries

Key Characteristics
--------------------
- Uses SQLAlchemy's `class_mapper` for introspection of ORM mappings
- Enforces design-time expectations programmatically for maintainability
- Fully integrated with `pytest` for reliable, automated testing in CI/CD

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

import pytest
from sqlalchemy.orm import class_mapper

from src.models import association_tables
from src.models.planet import Planet


def test_planet_model_importable():
    """
    Tests that the Planet model can be imported without error.

    :raises AssertionError: If import fails or object is None
    :return: None
    :rtype: None
    """
    from src.models.planet import Planet

    assert Planet is not None


def test_planet_tablename():
    """
    Tests that the Planet model has the correct __tablename__ value.

    :raises AssertionError: If __tablename__ does not match expected
    :return: None
    :rtype: None
    """
    assert Planet.__tablename__ == "planets"


def test_planet_columns():
    """
    Tests that Planet model has all expected columns with correct constraints.

    :raises AssertionError: If columns are missing, constraints incorrect, or nullability is wrong
    :return: None
    :rtype: None
    """
    cols = {c.name for c in Planet.__table__.columns}
    expected = {
        "id",
        "name",
        "rotation_period",
        "orbital_period",
        "diameter",
        "climate",
        "gravity",
        "terrain",
        "surface_water",
        "population",
        "url",
    }
    assert expected <= cols

    assert Planet.__table__.c.id.primary_key is True

    assert Planet.__table__.c.name.unique is True
    assert Planet.__table__.c.name.index is True
    assert Planet.__table__.c.name.nullable is False

    nullable_fields = expected - {"id", "name"}
    for field in nullable_fields:
        assert Planet.__table__.c[field].nullable is True


def test_planet_relationships_exist():
    """
    Tests that Planet model defines the expected ORM relationship with Films.

    :raises AssertionError: If the 'films' relationship key is missing
    :return: None
    :rtype: None
    """
    mapper = class_mapper(Planet)
    rels = {rel.key for rel in mapper.relationships}

    assert "films" in rels


def test_planet_films_relationship_secondary_and_lazy():
    """
    Tests that the films relationship on Planet uses the correct secondary table and lazy loading strategy.

    :raises AssertionError: If secondary association table or lazy loading strategy is incorrect
    :return: None
    :rtype: None
    """
    mapper = class_mapper(Planet)
    rel = mapper.relationships["films"]

    assert rel.secondary == association_tables.film_planets

    assert rel.lazy == "selectin"
