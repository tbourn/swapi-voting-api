"""
tests.models.test_film

================================================================================
Unit Tests for Film SQLAlchemy Model
================================================================================

Overview
--------
Validates the `Film` ORM model in `src.models.film`, ensuring its database
table structure and relationships match the SWAPI Voting API specification.

Tested Responsibilities
------------------------
- Correct table naming ("films")
- Presence of all expected columns with proper constraints
  - Primary key on `id`
  - Unique, indexed `title`
- Definition of many-to-many relationships with:
  - Characters
  - Planets
  - Starships
  - Vehicles
  - Species
- Verification of secondary join tables
- Confirmation of 'selectin' lazy loading strategy for all relationships

Key Characteristics
--------------------
- Uses SQLAlchemy `class_mapper` for deep introspection of ORM mappings
- Enforces schema design integrity in automated tests
- Designed for maintainability and CI/CD integration with pytest

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

import pytest
from sqlalchemy.orm import class_mapper

from src.models import association_tables
from src.models.film import Film


def test_film_tablename():
    """
    Tests that the Film model has the correct __tablename__ value.

    :raises AssertionError: If __tablename__ does not match expected
    :return: None
    :rtype: None
    """
    assert Film.__tablename__ == "films"


def test_film_columns():
    """
    Tests that Film model has all expected columns with correct constraints.

    :raises AssertionError: If columns are missing or constraints are incorrect
    :return: None
    :rtype: None
    """
    cols = {c.name for c in Film.__table__.columns}
    expected = {
        "id",
        "episode_id",
        "title",
        "opening_crawl",
        "director",
        "producer",
        "release_date",
        "created",
        "edited",
        "url",
    }
    assert expected <= cols

    assert Film.__table__.c.id.primary_key is True
    assert Film.__table__.c.title.unique is True
    assert Film.__table__.c.title.index is True


def test_film_relationships():
    """
    Tests that Film model defines all expected many-to-many ORM relationships
    with correct secondary tables and lazy loading strategy.

    :raises AssertionError: If relationships, secondary tables, or lazy loading are incorrect
    :return: None
    :rtype: None
    """
    mapper = class_mapper(Film)
    rels = {rel.key for rel in mapper.relationships}

    assert "characters" in rels
    assert "planets" in rels
    assert "starships" in rels
    assert "vehicles" in rels
    assert "species" in rels

    assert (
        mapper.relationships["characters"].secondary
        == association_tables.character_films
    )
    assert mapper.relationships["characters"].lazy == "selectin"

    assert mapper.relationships["planets"].secondary == association_tables.film_planets
    assert mapper.relationships["planets"].lazy == "selectin"

    assert (
        mapper.relationships["starships"].secondary == association_tables.film_starships
    )
    assert mapper.relationships["starships"].lazy == "selectin"

    assert (
        mapper.relationships["vehicles"].secondary == association_tables.film_vehicles
    )
    assert mapper.relationships["vehicles"].lazy == "selectin"

    assert mapper.relationships["species"].secondary == association_tables.film_species
    assert mapper.relationships["species"].lazy == "selectin"
