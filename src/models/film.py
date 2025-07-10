"""
src.models.film

================================================================================
SQLAlchemy Film Model
================================================================================

Overview
--------
This module defines the SQLAlchemy ORM model for Star Wars films in the
SWAPI Voting API. It includes the films table definition and establishes the
many-to-many relationship with characters via the shared association table.

Responsibilities
----------------
- Define the films table schema
- Implement many-to-many linkage to characters through the association table
- Support bidirectional relationship loading with Character model

Key Characteristics
--------------------
- Uses SQLAlchemy 2.0 declarative base
- Async-compatible metadata for Alembic migrations
- Designed for normalized relational database storage

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import relationship

from src.database.session import Base
from src.models.association_tables import (
    character_films,
    film_planets,
    film_species,
    film_starships,
    film_vehicles,
)
from src.models.character import character_films


class Film(Base):
    __tablename__ = "films"
    id = Column(Integer, primary_key=True)
    episode_id = Column(Integer, nullable=True)
    title = Column(String, unique=True, index=True)
    opening_crawl = Column(Text, nullable=True)
    director = Column(String, nullable=True)
    producer = Column(String, nullable=True)
    release_date = Column(Date, nullable=True)
    created = Column(DateTime, nullable=True)
    edited = Column(DateTime, nullable=True)
    url = Column(String, nullable=True)

    characters = relationship(
        "Character",
        secondary=character_films,
        back_populates="films",
        lazy="selectin",
    )
    planets = relationship(
        "Planet",
        secondary=film_planets,
        back_populates="films",
        lazy="selectin",
    )
    starships = relationship(
        "Starship",
        secondary=film_starships,
        back_populates="films",
        lazy="selectin",
    )
    vehicles = relationship(
        "Vehicle",
        secondary=film_vehicles,
        back_populates="films",
        lazy="selectin",
    )
    species = relationship(
        "Species",
        secondary=film_species,
        back_populates="films",
        lazy="selectin",
    )
