"""
tests.models.test_vehicle

================================================================================
Unit Tests for Vehicle SQLAlchemy Model
================================================================================

Overview
--------
Verifies the correctness of the `Vehicle` SQLAlchemy ORM model defined in
`src.models.vehicle`. Ensures that the database schema matches design
expectations and that all relationships and constraints are properly configured.

Tested Responsibilities
------------------------
- Vehicle model importability and tablename declaration
- Column definitions, constraints, and nullability
- Primary key configuration and indexing
- Relationship definitions, including join tables and lazy loading

Key Characteristics
--------------------
- Uses SQLAlchemy class_mapper to inspect ORM mappings
- Validates association tables for many-to-many relationships with Films and Characters
- Ensures naming, indexing, and uniqueness constraints on the `name` column
- Confirms that all other fields allow NULL values by design
- Fully automated with `pytest` for integration in CI/CD

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

import pytest
from sqlalchemy.orm import class_mapper

from src.models import association_tables
from src.models.vehicle import Vehicle


def test_vehicle_model_importable():
    """
    Tests that the Vehicle model can be imported without error.

    :raises AssertionError: If import fails or object is None
    :return: None
    :rtype: None
    """
    from src.models.vehicle import Vehicle

    assert Vehicle is not None


def test_vehicle_tablename():
    """
    Tests that the Vehicle model has the correct __tablename__ value.

    :raises AssertionError: If __tablename__ does not match expected
    :return: None
    :rtype: None
    """
    assert Vehicle.__tablename__ == "vehicles"


def test_vehicle_columns():
    """
    Tests that Vehicle model has all expected columns with correct constraints.

    :raises AssertionError: If columns are missing, constraints incorrect, or nullability is wrong
    :return: None
    :rtype: None
    """
    cols = {c.name for c in Vehicle.__table__.columns}
    expected = {
        "id",
        "name",
        "model",
        "manufacturer",
        "cost_in_credits",
        "length",
        "max_atmosphering_speed",
        "crew",
        "passengers",
        "cargo_capacity",
        "consumables",
        "vehicle_class",
        "url",
    }
    assert expected <= cols

    assert Vehicle.__table__.c.id.primary_key is True

    assert Vehicle.__table__.c.name.unique is True
    assert Vehicle.__table__.c.name.index is True
    assert Vehicle.__table__.c.name.nullable is False

    nullable_fields = expected - {"id", "name"}
    for field in nullable_fields:
        assert Vehicle.__table__.c[field].nullable is True


def test_vehicle_relationships_exist():
    """
    Tests that Vehicle model defines all expected ORM relationships.

    :raises AssertionError: If any expected relationship key is missing
    :return: None
    :rtype: None
    """
    mapper = class_mapper(Vehicle)
    rels = {rel.key for rel in mapper.relationships}

    assert "films" in rels
    assert "characters" in rels


@pytest.mark.parametrize(
    "rel_name,expected_secondary",
    [
        ("films", association_tables.film_vehicles),
        ("characters", association_tables.character_vehicles),
    ],
)
def test_vehicle_relationship_secondary_and_lazy(rel_name, expected_secondary):
    """
    Tests that Vehicle model relationships use correct secondary tables and lazy loading strategy.

    :param rel_name: Name of the relationship attribute
    :type rel_name: str
    :param expected_secondary: Expected SQLAlchemy association table
    :type expected_secondary: sqlalchemy.Table
    :raises AssertionError: If secondary association table or lazy loading strategy is incorrect
    :return: None
    :rtype: None
    """
    mapper = class_mapper(Vehicle)
    rel = mapper.relationships[rel_name]

    assert rel.secondary == expected_secondary
    assert rel.lazy == "selectin"
