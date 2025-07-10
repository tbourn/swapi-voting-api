"""
src.models.vehicle

================================================================================
SQLAlchemy ORM Model for Star Wars Vehicles
================================================================================

Overview
--------
This module defines the SQLAlchemy ORM model for representing vehicles
in the Star Wars universe for the SWAPI Voting API. It maps the
'vehicles' table and specifies fields such as name, model, manufacturer,
and class, while establishing many-to-many relationships with Films
and Characters through association tables.

Responsibilities
----------------
- Map the 'vehicles' table to the relational database
- Define schema columns for vehicle attributes and metadata
- Configure many-to-many relationships with Films and Characters

Key Characteristics
--------------------
- SQLAlchemy 2.0 declarative Base model
- Async-compatible for Alembic migrations
- Uses 'selectin' loading for relationship efficiency

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.database.session import Base
from src.models.association_tables import character_vehicles, film_vehicles


class Vehicle(Base):
    """
    SQLAlchemy ORM model representing a Star Wars vehicle.

    Maps to the 'vehicles' table in the database, defining columns
    for core metadata such as name, model, manufacturer, and class.
    Configures many-to-many relationships with Films and Characters
    via association tables, supporting queries about appearances
    and pilots.

    :param id: Primary key identifier for the vehicle.
    :type id: int
    :param name: Unique name of the vehicle (required).
    :type name: str
    :param model: Manufacturer model designation.
    :type model: str, optional
    :param manufacturer: Name of the manufacturing company.
    :type manufacturer: str, optional
    :param cost_in_credits: Cost of the vehicle in galactic credits.
    :type cost_in_credits: str, optional
    :param length: Length of the vehicle.
    :type length: str, optional
    :param max_atmosphering_speed: Maximum atmospheric speed.
    :type max_atmosphering_speed: str, optional
    :param crew: Number of crew members required.
    :type crew: str, optional
    :param passengers: Passenger capacity.
    :type passengers: str, optional
    :param cargo_capacity: Cargo capacity in kilograms.
    :type cargo_capacity: str, optional
    :param consumables: Duration the vehicle can provide consumables.
    :type consumables: str, optional
    :param vehicle_class: Classification/type of the vehicle.
    :type vehicle_class: str, optional
    :param url: Canonical URL for external SWAPI reference.
    :type url: str, optional
    :param films: Related Film instances linked via many-to-many.
    :type films: list[Film]
    :param characters: Related Character instances linked via many-to-many.
    :type characters: list[Character]
    """

    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True, nullable=False)
    model = Column(String, nullable=True)
    manufacturer = Column(String, nullable=True)
    cost_in_credits = Column(String, nullable=True)
    length = Column(String, nullable=True)
    max_atmosphering_speed = Column(String, nullable=True)
    crew = Column(String, nullable=True)
    passengers = Column(String, nullable=True)
    cargo_capacity = Column(String, nullable=True)
    consumables = Column(String, nullable=True)
    vehicle_class = Column(String, nullable=True)
    url = Column(String, nullable=True)

    # many-to-many with Film
    films = relationship(
        "Film",
        secondary=film_vehicles,
        back_populates="vehicles",
        lazy="selectin",
    )

    # many-to-many with Character
    characters = relationship(
        "Character",
        secondary=character_vehicles,
        back_populates="vehicles",
        lazy="selectin",
    )
