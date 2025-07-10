"""
src.models.character

================================================================================
SQLAlchemy ORM Model for Star Wars Characters
================================================================================

Overview
--------
Defines the SQLAlchemy ORM model representing the 'characters' table
in the application's relational database schema. The Character entity
captures key properties such as name, gender, and birth year, and
establishes many-to-many and many-to-one relationships with other
domain models, including films, vehicles, starships, species, and planets.

Responsibilities
----------------
- Store canonical data about individual Star Wars characters.
- Support relational queries linking characters to their appearances
  in films, the vehicles and starships they use, their species classification,
  and their homeworld planet.

Key Characteristics
--------------------
- Declarative SQLAlchemy ORM mapping using Base.
- Comprehensive many-to-many associations via association tables.
- Foreign key and relationship mapping to Planets for homeworld linkage.
- Optimized with selectin-loading for performance.

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.database.session import Base
from src.models.association_tables import (
    character_films,
    character_species,
    character_starships,
    character_vehicles,
)


class Character(Base):
    """
    Represents a Star Wars character entity in the database schema.

    This SQLAlchemy ORM model defines the 'characters' table, capturing
    core properties of each character along with their relationships to
    other domain entities such as films, vehicles, starships, species,
    and planets.

    :param id: Primary key identifier for the character.
    :type id: int
    :param name: Unique name of the character (non-nullable).
    :type name: str
    :param gender: Gender of the character (nullable).
    :type gender: str, optional
    :param birth_year: Birth year of the character in in-universe dating
        format (nullable).
    :type birth_year: str, optional
    :param films: Many-to-many relationship linking the character to
        the films in which they appear.
    :type films: List[Film]
    :param vehicles: Many-to-many relationship linking the character to
        the vehicles they have piloted or used.
    :type vehicles: List[Vehicle]
    :param starships: Many-to-many relationship linking the character to
        the starships they have piloted or used.
    :type starships: List[Starship]
    :param species: Many-to-many relationship linking the character to
        their species classification.
    :type species: List[Species]
    :param homeworld_id: Foreign key reference to the associated planet
        serving as the character's homeworld.
    :type homeworld_id: int, optional
    :param homeworld: Many-to-one relationship linking the character to
        their homeworld planet entity.
    :type homeworld: Planet
    """

    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    gender = Column(String, nullable=True)
    birth_year = Column(String, nullable=True)

    # Many-to-many: Films
    films = relationship(
        "Film",
        secondary=character_films,
        back_populates="characters",
        lazy="selectin",
    )

    # Many-to-many: Vehicles
    vehicles = relationship(
        "Vehicle",
        secondary=character_vehicles,
        back_populates="characters",
        lazy="selectin",
    )

    # Many-to-many: Starships
    starships = relationship(
        "Starship",
        secondary=character_starships,
        back_populates="characters",
        lazy="selectin",
    )

    # Many-to-many: Species
    species = relationship(
        "Species",
        secondary=character_species,
        back_populates="characters",
        lazy="selectin",
    )

    # Many-to-one: Homeworld
    homeworld_id = Column(Integer, ForeignKey("planets.id"))
    homeworld = relationship("Planet", lazy="selectin")
