"""
src.models.species

================================================================================
SQLAlchemy ORM Model for Star Wars Species
================================================================================

Overview
--------
This module defines the SQLAlchemy model for representing a Species entity
within the Star Wars universe. It includes field mappings to database columns
and many-to-many relationships with Films and Characters via association tables.

Responsibilities
----------------
- Map the 'species' table in the database
- Define metadata for species attributes
- Manage many-to-many links to Films and Characters

Key Characteristics
--------------------
- SQLAlchemy declarative Base model
- Supports eager loading with 'selectin' strategy
- Enables schema migration autogeneration with Alembic

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.database.session import Base
from src.models.association_tables import character_species, film_species


class Species(Base):
    """
    SQLAlchemy ORM model representing a Species entity.

    This class maps to the 'species' table in the database, defining
    the attributes and relationships for a species in the Star Wars
    universe. It includes descriptive biological fields and establishes
    many-to-many relationships with Films and Characters.

    :param id: Primary key identifier for the species.
    :type id: int
    :param name: Unique name of the species (required).
    :type name: str
    :param classification: Taxonomic classification of the species.
    :type classification: str, optional
    :param designation: General designation (e.g., sentient).
    :type designation: str, optional
    :param average_height: Typical height in centimeters.
    :type average_height: str, optional
    :param skin_colors: Comma-separated list of skin colors.
    :type skin_colors: str, optional
    :param hair_colors: Comma-separated list of hair colors.
    :type hair_colors: str, optional
    :param eye_colors: Comma-separated list of eye colors.
    :type eye_colors: str, optional
    :param average_lifespan: Average lifespan in years.
    :type average_lifespan: str, optional
    :param language: Primary language spoken by the species.
    :type language: str, optional
    :param url: Source URL for external reference.
    :type url: str, optional
    :param films: Related Film instances linked via many-to-many.
    :type films: list[Film]
    :param characters: Related Character instances linked via many-to-many.
    :type characters: list[Character]
    """

    __tablename__ = "species"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True, nullable=False)
    classification = Column(String, nullable=True)
    designation = Column(String, nullable=True)
    average_height = Column(String, nullable=True)
    skin_colors = Column(String, nullable=True)
    hair_colors = Column(String, nullable=True)
    eye_colors = Column(String, nullable=True)
    average_lifespan = Column(String, nullable=True)
    language = Column(String, nullable=True)
    url = Column(String, nullable=True)

    films = relationship(
        "Film",
        secondary=film_species,
        back_populates="species",
        lazy="selectin",
    )

    characters = relationship(
        "Character",
        secondary=character_species,
        back_populates="species",
        lazy="selectin",
    )
