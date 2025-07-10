"""
src.schemas.planet

================================================================================
Pydantic Schemas for Star Wars Planets
================================================================================

Overview
--------
Defines the Pydantic models used to validate, parse, and serialize
planet-related data in the SWAPI Voting API. Supports both request
and response payloads, including nested relationships with films.

Responsibilities
----------------
- Provide base schema with shared planet fields
- Define creation schema for incoming requests
- Define response schema with database ID and nested Film references

Key Characteristics
--------------------
- Designed for FastAPI with OpenAPI documentation support
- orm_mode enabled for SQLAlchemy integration
- Supports nested FilmBase serialization for related films

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

from typing import List, Optional

from pydantic import BaseModel, constr
from typing_extensions import Annotated

StrictName100 = Annotated[
    str, constr(strip_whitespace=True, min_length=1, max_length=100)
]

StrictDesc200 = Annotated[
    str, constr(strip_whitespace=True, min_length=1, max_length=200)
]

StrictURL = Annotated[str, constr(strip_whitespace=True, min_length=1, max_length=200)]


class FilmBase(BaseModel):
    """
    Minimal nested Film model for inclusion in Planet responses.

    Provides a lightweight reference to a Film entity when serializing
    Planet responses, avoiding full Film detail while supporting
    many-to-many relationships.

    :param id: Unique identifier for the film.
    :type id: int
    :param title: Title of the film.
    :type title: str
    """

    id: int
    title: StrictName100

    model_config = {"from_attributes": True, "strict": True, "extra": "forbid"}


class PlanetBase(BaseModel):
    """
    Base Pydantic schema for a Star Wars planet.

    Defines core fields shared by both creation and response models,
    supporting consistent validation and serialization of planet data.

    :param name: Name of the planet.
    :type name: str
    :param rotation_period: Rotation period of the planet (optional).
    :type rotation_period: str, optional
    :param orbital_period: Orbital period of the planet (optional).
    :type orbital_period: str, optional
    :param diameter: Diameter of the planet (optional).
    :type diameter: str, optional
    :param climate: Climate description (optional).
    :type climate: str, optional
    :param gravity: Gravity description (optional).
    :type gravity: str, optional
    :param terrain: Terrain description (optional).
    :type terrain: str, optional
    :param surface_water: Surface water percentage (optional).
    :type surface_water: str, optional
    :param population: Population estimate (optional).
    :type population: str, optional
    :param url: Resource URL (optional).
    :type url: str, optional
    """

    name: StrictName100
    rotation_period: Optional[StrictDesc200] = None
    orbital_period: Optional[StrictDesc200] = None
    diameter: Optional[StrictDesc200] = None
    climate: Optional[StrictDesc200] = None
    gravity: Optional[StrictDesc200] = None
    terrain: Optional[StrictDesc200] = None
    surface_water: Optional[StrictDesc200] = None
    population: Optional[StrictDesc200] = None
    url: Optional[StrictURL] = None

    model_config = {"strict": True, "extra": "forbid"}


class PlanetCreate(PlanetBase):
    """
    Schema for creating a new Star Wars planet.

    Inherits all fields from PlanetBase to validate
    incoming planet creation requests.
    """

    pass


class PlanetResponse(PlanetBase):
    """
    Schema for returning a Star Wars planet in API responses.

    Extends PlanetBase to include the database ID and a nested list
    of associated FilmBase references, enabling rich API responses
    with related film data.

    :param id: Database primary key for the planet.
    :type id: int
    :param films: List of associated FilmBase entities.
    :type films: list[FilmBase]
    """

    id: int
    films: List[FilmBase] = []

    model_config = {"from_attributes": True, "strict": True, "extra": "forbid"}
