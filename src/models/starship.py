"""
src.models.starship

================================================================================
SQLAlchemy ORM Model for Star Wars Starships
================================================================================

Overview
--------
This module defines the SQLAlchemy ORM model for representing starships
in the Star Wars universe within the SWAPI Voting API. It maps the
'starships' table, specifying fields such as name, model, manufacturer,
and classification, and defines many-to-many relationships with Films
and Characters through association tables.

Responsibilities
----------------
- Map the 'starships' table in the relational database
- Define metadata columns for starship attributes
- Configure many-to-many relationships with Films and Characters

Key Characteristics
--------------------
- SQLAlchemy 2.0 declarative Base model
- Supports eager loading with 'selectin' strategy for relationships
- Async-compatible for Alembic migrations and modern SQLAlchemy usage

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.database.session import Base
from src.models.association_tables import character_starships, film_starships


class Starship(Base):
    """
    SQLAlchemy ORM model representing a Star Wars starship.

    Maps to the 'starships' table in the database, defining columns
    for core metadata such as name, model, manufacturer, and
    classification. Establishes many-to-many relationships with Films
    and Characters via association tables to enable rich querying
    of appearances and crew.

    :param id: Primary key identifier for the starship.
    :type id: int
    :param name: Unique name of the starship (required).
    :type name: str
    :param model: Manufacturer model designation.
    :type model: str, optional
    :param manufacturer: Name of the manufacturing company.
    :type manufacturer: str, optional
    :param starship_class: Classification or type of the starship.
    :type starship_class: str, optional
    :param films: Related Film instances linked via many-to-many.
    :type films: list[Film]
    :param characters: Related Character instances linked via many-to-many.
    :type characters: list[Character]
    """

    __tablename__ = "starships"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    model = Column(String, nullable=True)
    manufacturer = Column(String, nullable=True)
    starship_class = Column(String, nullable=True)

    films = relationship(
        "Film",
        secondary=film_starships,
        back_populates="starships",
        lazy="selectin",
    )

    characters = relationship(
        "Character",
        secondary=character_starships,
        back_populates="starships",
        lazy="selectin",
    )
