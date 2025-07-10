"""
tests.models.test_association_tables

================================================================================
Unit Tests for SQLAlchemy Association Tables
================================================================================

Overview
--------
Verifies the structure and integrity of all many-to-many association tables
defined in `src.models.association_tables` for the SWAPI Voting API. These
association tables implement the join relationships between entities such as
characters, films, starships, vehicles, planets, and species.

Tested Responsibilities
------------------------
- Table naming consistency (e.g., 'character_films', 'film_planets')
- Presence of expected join columns (e.g., 'character_id', 'film_id')
- Each join column is part of the composite primary key
- ForeignKey constraints correctly defined to target primary key of related tables
- Ensures single foreign key per join column
- Structural integrity suitable for SQLAlchemy ORM relationship definitions

Key Characteristics
--------------------
- Uses SQLAlchemy's Table and ForeignKey constructs for validation
- Parametrized tests to cover all association tables
- Enforces schema correctness for many-to-many mappings
- Designed to prevent silent regressions in database migrations

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

import pytest
from sqlalchemy import ForeignKey, Table

import src.models.association_tables as assoc


@pytest.mark.parametrize(
    "table_obj, expected_name, expected_columns",
    [
        (assoc.character_films, "character_films", ["character_id", "film_id"]),
        (
            assoc.character_vehicles,
            "character_vehicles",
            ["character_id", "vehicle_id"],
        ),
        (
            assoc.character_starships,
            "character_starships",
            ["character_id", "starship_id"],
        ),
        (assoc.character_species, "character_species", ["character_id", "species_id"]),
        (assoc.film_planets, "film_planets", ["film_id", "planet_id"]),
        (assoc.film_starships, "film_starships", ["film_id", "starship_id"]),
        (assoc.film_vehicles, "film_vehicles", ["film_id", "vehicle_id"]),
        (assoc.film_species, "film_species", ["film_id", "species_id"]),
    ],
)
def test_association_table_properties(table_obj, expected_name, expected_columns):
    """
    Tests structural properties of SQLAlchemy many-to-many association tables.

    :param table_obj: The SQLAlchemy Table object representing the association table
    :type table_obj: sqlalchemy.Table
    :param expected_name: Expected table name in the database schema
    :type expected_name: str
    :param expected_columns: List of expected column names in the table
    :type expected_columns: list
    :raises AssertionError: If table structure, naming, columns, or foreign keys are incorrect
    :return: None
    :rtype: None
    """
    assert isinstance(table_obj, Table)
    assert table_obj.name == expected_name
    cols = {col.name for col in table_obj.columns}
    assert set(expected_columns) <= cols

    for col_name in expected_columns:
        col = table_obj.c[col_name]
        assert col.primary_key is True

        fks = list(col.foreign_keys)
        assert len(fks) == 1

        fk = fks[0]
        assert isinstance(fk, ForeignKey)
        if "character" in col_name:
            assert fk.target_fullname == "characters.id"
        elif "film" in col_name:
            assert fk.target_fullname == "films.id"
        elif "vehicle" in col_name:
            assert fk.target_fullname == "vehicles.id"
        elif "starship" in col_name:
            assert fk.target_fullname == "starships.id"
        elif "species" in col_name:
            assert fk.target_fullname == "species.id"
        elif "planet" in col_name:
            assert fk.target_fullname == "planets.id"
