"""
tests.models.test_character

================================================================================
Unit Tests for Character SQLAlchemy Model
================================================================================

Overview
--------
Validates the `Character` ORM model in `src.models.character`, ensuring the
correct table structure, columns, constraints, foreign key relationships, and
many-to-many associations for the SWAPI Voting API.

Tested Responsibilities
------------------------
- Table naming ("characters")
- All expected columns with proper constraints:
  - Primary key on `id`
  - Unique, non-nullable `name`
  - Nullable `gender`, `birth_year`, `homeworld_id`
  - ForeignKey constraint on `homeworld_id` referencing `planets.id`
- Many-to-many relationships with:
  - Films
  - Vehicles
  - Starships
  - Species
- Many-to-one relationship with:
  - Homeworld (Planet)
- Verification of secondary join tables
- Lazy loading strategy using 'selectin'

Key Characteristics
--------------------
- Uses SQLAlchemy `class_mapper` for ORM mapping introspection
- Asserts database integrity via pytest
- Suitable for CI/CD validation to catch schema regressions

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

import pytest
from sqlalchemy import ForeignKey
from sqlalchemy.orm import class_mapper

from src.models import association_tables
from src.models.character import Character


def test_character_model_importable():
    """
    Tests that the Character model can be imported without error.

    :raises AssertionError: If import fails or object is None
    :return: None
    :rtype: None
    """
    from src.models.character import Character

    assert Character is not None


def test_character_tablename():
    """
    Tests that the Character model has the correct __tablename__ value.

    :raises AssertionError: If __tablename__ does not match expected
    :return: None
    :rtype: None
    """
    assert Character.__tablename__ == "characters"


def test_character_columns():
    """
    Tests that Character model has all expected columns with correct constraints.

    :raises AssertionError: If columns are missing, constraints incorrect, or ForeignKey is wrong
    :return: None
    :rtype: None
    """
    cols = {c.name for c in Character.__table__.columns}
    expected = {
        "id",
        "name",
        "gender",
        "birth_year",
        "homeworld_id",
    }
    assert expected <= cols

    assert Character.__table__.c.id.primary_key is True
    assert Character.__table__.c.id.index is True

    assert Character.__table__.c.name.unique is True
    assert Character.__table__.c.name.nullable is False

    for field in {"gender", "birth_year", "homeworld_id"}:
        assert Character.__table__.c[field].nullable is True

    fk = list(Character.__table__.c.homeworld_id.foreign_keys)[0]
    assert isinstance(fk, ForeignKey)
    assert fk.target_fullname == "planets.id"


def test_character_relationships_exist():
    """
    Tests that Character model defines all expected ORM relationships.

    :raises AssertionError: If any expected relationship key is missing
    :return: None
    :rtype: None
    """
    mapper = class_mapper(Character)
    rels = {rel.key for rel in mapper.relationships}

    assert "films" in rels
    assert "vehicles" in rels
    assert "starships" in rels
    assert "species" in rels
    assert "homeworld" in rels


@pytest.mark.parametrize(
    "rel_name,expected_secondary",
    [
        ("films", association_tables.character_films),
        ("vehicles", association_tables.character_vehicles),
        ("starships", association_tables.character_starships),
        ("species", association_tables.character_species),
    ],
)
def test_character_many_to_many_relationships_secondary_and_lazy(
    rel_name, expected_secondary
):
    """
    Tests that many-to-many relationships have correct secondary tables and lazy loading.

    :param rel_name: Name of the relationship attribute
    :type rel_name: str
    :param expected_secondary: Expected SQLAlchemy association table
    :type expected_secondary: sqlalchemy.Table
    :raises AssertionError: If secondary or lazy strategy is incorrect
    :return: None
    :rtype: None
    """
    mapper = class_mapper(Character)
    rel = mapper.relationships[rel_name]

    assert rel.secondary == expected_secondary
    assert rel.lazy == "selectin"


def test_character_homeworld_relationship_lazy_and_no_secondary():
    """
    Tests that the homeworld relationship is many-to-one with no secondary table and correct lazy strategy.

    :raises AssertionError: If secondary is not None or lazy loading is incorrect
    :return: None
    :rtype: None
    """
    mapper = class_mapper(Character)
    rel = mapper.relationships["homeworld"]

    assert rel.secondary is None
    assert rel.lazy == "selectin"
