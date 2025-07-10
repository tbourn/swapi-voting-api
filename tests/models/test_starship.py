"""
tests.models.test_starship

================================================================================
Unit Tests for Starship SQLAlchemy Model
================================================================================

Overview
--------
Validates the `Starship` ORM model defined in `src.models.starship`.
These tests ensure the database schema, constraints, and many-to-many
relationships conform to design expectations in the SWAPI Voting API.

Tested Responsibilities
------------------------
- Correct tablename declaration for the Starship table
- Column definitions and constraints (primary key, unique, nullable)
- Verification of indexing on primary key
- Proper configuration of many-to-many relationships to Films and Characters
  via association tables
- Enforcement of lazy loading strategies for efficient query performance

Key Characteristics
--------------------
- Uses SQLAlchemy's `class_mapper` to introspect ORM relationships
- Confirms that secondary join tables match expected association tables
- Ensures strict schema contract for name uniqueness and required fields
- Fully automated with `pytest` for reliable CI/CD integration

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

import pytest
from sqlalchemy.orm import class_mapper

from src.models import association_tables
from src.models.starship import Starship


def test_starship_model_importable():
    """
    Tests that the Starship model can be imported without error.

    :raises AssertionError: If import fails or object is None
    :return: None
    :rtype: None
    """
    from src.models.starship import Starship

    assert Starship is not None


def test_starship_tablename():
    """
    Tests that the Starship model has the correct __tablename__ value.

    :raises AssertionError: If __tablename__ does not match expected
    :return: None
    :rtype: None
    """
    assert Starship.__tablename__ == "starships"


def test_starship_columns():
    """
    Tests that Starship model has all expected columns with correct constraints.

    :raises AssertionError: If columns are missing, constraints incorrect, or nullability is wrong
    :return: None
    :rtype: None
    """
    cols = {c.name for c in Starship.__table__.columns}
    expected = {
        "id",
        "name",
        "model",
        "manufacturer",
        "starship_class",
    }
    assert expected <= cols

    assert Starship.__table__.c.id.primary_key is True
    assert Starship.__table__.c.id.index is True

    assert Starship.__table__.c.name.unique is True
    assert Starship.__table__.c.name.nullable is False

    assert Starship.__table__.c.model.nullable is True
    assert Starship.__table__.c.manufacturer.nullable is True
    assert Starship.__table__.c.starship_class.nullable is True


def test_starship_relationships_exist():
    """
    Tests that Starship model defines all expected ORM relationships.

    :raises AssertionError: If any expected relationship key is missing
    :return: None
    :rtype: None
    """
    mapper = class_mapper(Starship)
    rels = {rel.key for rel in mapper.relationships}

    assert "films" in rels
    assert "characters" in rels


@pytest.mark.parametrize(
    "rel_name,expected_secondary",
    [
        ("films", association_tables.film_starships),
        ("characters", association_tables.character_starships),
    ],
)
def test_starship_relationship_secondary_and_lazy(rel_name, expected_secondary):
    """
    Tests that Starship model relationships use correct secondary tables and lazy loading strategy.

    :param rel_name: Name of the relationship attribute
    :type rel_name: str
    :param expected_secondary: Expected SQLAlchemy association table
    :type expected_secondary: sqlalchemy.Table
    :raises AssertionError: If secondary association table or lazy loading strategy is incorrect
    :return: None
    :rtype: None
    """
    mapper = class_mapper(Starship)
    rel = mapper.relationships[rel_name]

    assert rel.secondary == expected_secondary

    assert rel.lazy == "selectin"
