"""
src.models.association_tables

================================================================================
Association Tables for SQLAlchemy ORM Many-to-Many Relationships
================================================================================

Overview
--------
This module defines the SQLAlchemy `Table` objects used to represent many-to-many
associations between core Star Wars domain models in the application. These
association tables enable rich relational mapping between entities such as
characters, films, vehicles, starships, species, and planets.

Responsibilities
----------------
- Define intermediary SQL tables for many-to-many relationships.
- Support SQLAlchemy ORM relationships via `secondary` joins.
- Provide explicit foreign key constraints for referential integrity.
- Ensure consistent primary key pairings for efficient joins.

Key Characteristics
--------------------
- Declarative `Table` definitions using `Base.metadata`.
- Enforced composite primary keys on join columns.
- Seamless integration with SQLAlchemy ORM `relationship()` mappings.

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

from sqlalchemy import Column, ForeignKey, Integer, Table

from src.database.session import Base

"""
Represents the association table between Character and Film models.

This table enables a many-to-many relationship between characters and films
by acting as a bridge (join) table in the relational schema.

:param name: Table name in the database.
:type name: str
:param metadata: SQLAlchemy Base metadata object.
:type metadata: sqlalchemy.MetaData
:param columns: 
    - character_id (int): Foreign key to characters.id, part of composite primary key.
    - film_id (int): Foreign key to films.id, part of composite primary key.
:type columns: List[sqlalchemy.Column]
"""
character_films = Table(
    "character_films",
    Base.metadata,
    Column("character_id", Integer, ForeignKey("characters.id"), primary_key=True),
    Column("film_id", Integer, ForeignKey("films.id"), primary_key=True),
    extend_existing=True,
)

"""
Represents the association table between Character and Vehicle models.

This table enables a many-to-many relationship between characters and vehicles
by acting as a bridge (join) table in the relational schema.

:param name: Table name in the database.
:type name: str
:param metadata: SQLAlchemy Base metadata object.
:type metadata: sqlalchemy.MetaData
:param columns: 
    - character_id (int): Foreign key to characters.id, part of composite primary key.
    - vehicle_id (int): Foreign key to vehicles.id, part of composite primary key.
:type columns: List[sqlalchemy.Column]
"""
character_vehicles = Table(
    "character_vehicles",
    Base.metadata,
    Column("character_id", Integer, ForeignKey("characters.id"), primary_key=True),
    Column("vehicle_id", Integer, ForeignKey("vehicles.id"), primary_key=True),
    extend_existing=True,
)

"""
Represents the association table between Character and Starship models.

This table enables a many-to-many relationship between characters and starships
by acting as a bridge (join) table in the relational schema.

:param name: Table name in the database.
:type name: str
:param metadata: SQLAlchemy Base metadata object.
:type metadata: sqlalchemy.MetaData
:param columns: 
    - character_id (int): Foreign key to characters.id, part of composite primary key.
    - starship_id (int): Foreign key to starships.id, part of composite primary key.
:type columns: List[sqlalchemy.Column]
"""
character_starships = Table(
    "character_starships",
    Base.metadata,
    Column("character_id", Integer, ForeignKey("characters.id"), primary_key=True),
    Column("starship_id", Integer, ForeignKey("starships.id"), primary_key=True),
    extend_existing=True,
)

"""
Represents the association table between Character and Species models.

This table enables a many-to-many relationship between characters and species
by acting as a bridge (join) table in the relational schema.

:param name: Table name in the database.
:type name: str
:param metadata: SQLAlchemy Base metadata object.
:type metadata: sqlalchemy.MetaData
:param columns: 
    - character_id (int): Foreign key to characters.id, part of composite primary key.
    - species_id (int): Foreign key to species.id, part of composite primary key.
:type columns: List[sqlalchemy.Column]
"""
character_species = Table(
    "character_species",
    Base.metadata,
    Column("character_id", Integer, ForeignKey("characters.id"), primary_key=True),
    Column("species_id", Integer, ForeignKey("species.id"), primary_key=True),
    extend_existing=True,
)

"""
Represents the association table between Film and Planet models.

This table enables a many-to-many relationship between films and planets
by acting as a bridge (join) table in the relational schema.

:param name: Table name in the database.
:type name: str
:param metadata: SQLAlchemy Base metadata object.
:type metadata: sqlalchemy.MetaData
:param columns: 
    - film_id (int): Foreign key to films.id, part of composite primary key.
    - planet_id (int): Foreign key to planets.id, part of composite primary key.
:type columns: List[sqlalchemy.Column]
"""
film_planets = Table(
    "film_planets",
    Base.metadata,
    Column("film_id", Integer, ForeignKey("films.id"), primary_key=True),
    Column("planet_id", Integer, ForeignKey("planets.id"), primary_key=True),
    extend_existing=True,
)

"""
Represents the association table between Film and Starship models.

This table enables a many-to-many relationship between films and starships
by acting as a bridge (join) table in the relational schema.

:param name: Table name in the database.
:type name: str
:param metadata: SQLAlchemy Base metadata object.
:type metadata: sqlalchemy.MetaData
:param columns: 
    - film_id (int): Foreign key to films.id, part of composite primary key.
    - starship_id (int): Foreign key to starships.id, part of composite primary key.
:type columns: List[sqlalchemy.Column]
"""
film_starships = Table(
    "film_starships",
    Base.metadata,
    Column("film_id", Integer, ForeignKey("films.id"), primary_key=True),
    Column("starship_id", Integer, ForeignKey("starships.id"), primary_key=True),
    extend_existing=True,
)

"""
Represents the association table between Film and Vehicle models.

This table enables a many-to-many relationship between films and vehicles
by acting as a bridge (join) table in the relational schema.

:param name: Table name in the database.
:type name: str
:param metadata: SQLAlchemy Base metadata object.
:type metadata: sqlalchemy.MetaData
:param columns: 
    - film_id (int): Foreign key to films.id, part of composite primary key.
    - vehicle_id (int): Foreign key to vehicles.id, part of composite primary key.
:type columns: List[sqlalchemy.Column]
"""
film_vehicles = Table(
    "film_vehicles",
    Base.metadata,
    Column("film_id", Integer, ForeignKey("films.id"), primary_key=True),
    Column("vehicle_id", Integer, ForeignKey("vehicles.id"), primary_key=True),
    extend_existing=True,
)

"""
Represents the association table between Film and Species models.

This table enables a many-to-many relationship between films and species
by acting as a bridge (join) table in the relational schema.

:param name: Table name in the database.
:type name: str
:param metadata: SQLAlchemy Base metadata object.
:type metadata: sqlalchemy.MetaData
:param columns: 
    - film_id (int): Foreign key to films.id, part of composite primary key.
    - species_id (int): Foreign key to species.id, part of composite primary key.
:type columns: List[sqlalchemy.Column]
"""
film_species = Table(
    "film_species",
    Base.metadata,
    Column("film_id", Integer, ForeignKey("films.id"), primary_key=True),
    Column("species_id", Integer, ForeignKey("species.id"), primary_key=True),
    extend_existing=True,
)
