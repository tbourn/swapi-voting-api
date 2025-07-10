"""
src.models.planet

================================================================================
SQLAlchemy ORM Model for Star Wars Planets
================================================================================

Overview
--------
This module defines the SQLAlchemy model representing a Planet entity in the
Star Wars universe. It includes field definitions mapping to database columns,
as well as the many-to-many relationship to Films through an association table.

Responsibilities
----------------
- Map the "planets" table in the database
- Define column metadata for planet attributes
- Establish the relationship to the Film model

Key Characteristics
--------------------
- SQLAlchemy declarative Base model
- Supports lazy loading with 'selectin' for related films
- Enables autogeneration of migrations via Alembic

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.database.session import Base
from src.models.association_tables import film_planets


class Planet(Base):
    """
    SQLAlchemy ORM model representing a Planet entity.

    This class maps to the 'planets' table in the database and defines
    its columns and relationships. Each Planet instance includes
    identifying details like name, climate, and population, and is
    associated with one or more Films via a many-to-many relationship.

    :param id: Primary key identifier for the planet.
    :type id: int
    :param name: Unique name of the planet (required).
    :type name: str
    :param rotation_period: Duration of a single rotation in standard hours.
    :type rotation_period: str, optional
    :param orbital_period: Duration of a single orbit in standard days.
    :type orbital_period: str, optional
    :param diameter: Diameter of the planet in kilometers.
    :type diameter: str, optional
    :param climate: Climate type(s) found on the planet.
    :type climate: str, optional
    :param gravity: Gravity description of the planet.
    :type gravity: str, optional
    :param terrain: Terrain type(s) on the planet.
    :type terrain: str, optional
    :param surface_water: Percentage of surface water coverage.
    :type surface_water: str, optional
    :param population: Estimated population of the planet.
    :type population: str, optional
    :param url: Source URL for reference.
    :type url: str, optional
    :param films: Related Film instances linked via many-to-many.
    :type films: list[Film]
    """

    __tablename__ = "planets"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True, nullable=False)
    rotation_period = Column(String, nullable=True)
    orbital_period = Column(String, nullable=True)
    diameter = Column(String, nullable=True)
    climate = Column(String, nullable=True)
    gravity = Column(String, nullable=True)
    terrain = Column(String, nullable=True)
    surface_water = Column(String, nullable=True)
    population = Column(String, nullable=True)
    url = Column(String, nullable=True)

    films = relationship(
        "Film",
        secondary=film_planets,
        back_populates="planets",
        lazy="selectin",
    )
