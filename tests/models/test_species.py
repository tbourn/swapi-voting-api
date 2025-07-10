"""
tests.models.test_species

================================================================================
Unit Tests for Species SQLAlchemy Model
================================================================================

Overview
--------
Verifies the correctness of the `Species` ORM model defined in `src.models.species`.
These tests ensure the database schema, constraints, and many-to-many relationships
adhere to design expectations in the SWAPI Voting API.

Tested Responsibilities
------------------------
- Correct table name declaration ("species")
- Column definitions and constraints (primary key, unique, indexing, nullability)
- Validation of many-to-many relationships with Films and Characters
- Verification of association (join) tables used in relationships
- Enforcement of lazy loading strategies for efficient querying

Key Characteristics
--------------------
- Uses SQLAlchemy's `class_mapper` to introspect ORM relationships
- Confirms name column is unique, indexed, and non-nullable
- Ensures all other fields are nullable as designed
- Fully automated with `pytest` for reliable, repeatable validation in CI/CD

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

import pytest
from sqlalchemy.orm import class_mapper

from src.models import association_tables
from src.models.species import Species


def test_species_model_importable():
    """
    Tests that the Species model can be imported without error.

    :raises AssertionError: If import fails or object is None
    :return: None
    :rtype: None
    """
    from src.models.species import Species

    assert Species is not None


def test_species_tablename():
    """
    Tests that the Species model has the correct __tablename__ value.

    :raises AssertionError: If __tablename__ does not match expected
    :return: None
    :rtype: None
    """
    assert Species.__tablename__ == "species"


def test_species_columns():
    """
    Tests that Species model has all expected columns with correct constraints.

    :raises AssertionError: If columns are missing, constraints incorrect, or nullability is wrong
    :return: None
    :rtype: None
    """
    cols = {c.name for c in Species.__table__.columns}
    expected = {
        "id",
        "name",
        "classification",
        "designation",
        "average_height",
        "skin_colors",
        "hair_colors",
        "eye_colors",
        "average_lifespan",
        "language",
        "url",
    }
    assert expected <= cols

    assert Species.__table__.c.id.primary_key is True

    assert Species.__table__.c.name.unique is True
    assert Species.__table__.c.name.index is True
    assert Species.__table__.c.name.nullable is False

    nullable_fields = expected - {"id", "name"}
    for field in nullable_fields:
        assert Species.__table__.c[field].nullable is True


def test_species_relationships_exist():
    """
    Tests that Species model defines all expected ORM relationships.

    :raises AssertionError: If any expected relationship key is missing
    :return: None
    :rtype: None
    """
    mapper = class_mapper(Species)
    rels = {rel.key for rel in mapper.relationships}

    assert "films" in rels
    assert "characters" in rels


@pytest.mark.parametrize(
    "rel_name,expected_secondary",
    [
        ("films", association_tables.film_species),
        ("characters", association_tables.character_species),
    ],
)
def test_species_relationship_secondary_and_lazy(rel_name, expected_secondary):
    """
    Tests that Species model relationships use correct secondary tables and lazy loading strategy.

    :param rel_name: Name of the relationship attribute
    :type rel_name: str
    :param expected_secondary: Expected SQLAlchemy association table
    :type expected_secondary: sqlalchemy.Table
    :raises AssertionError: If secondary association table or lazy loading strategy is incorrect
    :return: None
    :rtype: None
    """
    mapper = class_mapper(Species)
    rel = mapper.relationships[rel_name]

    assert rel.secondary == expected_secondary

    assert rel.lazy == "selectin"
