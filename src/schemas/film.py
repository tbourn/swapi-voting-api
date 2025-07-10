"""
src.schemas.film

================================================================================
Pydantic Schemas for Star Wars Films
================================================================================

Overview
--------
Defines the Pydantic models used to validate, parse, and serialize film-related
data for the SWAPI Voting API. Supports both request and response payloads,
including nested relationships with characters, planets, starships, vehicles,
and species.

Responsibilities
----------------
- Provide base schema for shared film fields
- Define creation schema for film input
- Define response schema with database ID and nested related entities

Key Characteristics
--------------------
- Designed for FastAPI with OpenAPI documentation support
- orm_mode enabled for SQLAlchemy integration
- Supports nested serialization of related resources

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, constr
from typing_extensions import Annotated

StrictName100 = Annotated[
    str, constr(strip_whitespace=True, min_length=1, max_length=100)
]
StrictText500 = Annotated[
    str, constr(strip_whitespace=True, min_length=1, max_length=500)
]
StrictURL = Annotated[str, constr(strip_whitespace=True, min_length=1, max_length=200)]


class CharacterBase(BaseModel):
    """
    Minimal nested Character model for inclusion in Film responses.

    Represents a lightweight reference to a Character in the context
    of a Film, avoiding full character detail while supporting
    many-to-many relationships.

    :param id: Unique identifier for the character.
    :type id: int
    :param name: Name of the character.
    :type name: str
    """

    id: int
    name: StrictName100

    model_config = {"from_attributes": True, "strict": True, "extra": "forbid"}


class PlanetBase(BaseModel):
    """
    Minimal nested Planet model for inclusion in Film responses.

    Represents a simplified view of a Planet for nested serialization
    in Film API responses.

    :param id: Unique identifier for the planet.
    :type id: int
    :param name: Name of the planet.
    :type name: str
    """

    id: int
    name: StrictName100

    model_config = {"from_attributes": True, "strict": True, "extra": "forbid"}


class StarshipBase(BaseModel):
    """
    Minimal nested Starship model for inclusion in Film responses.

    Provides a concise reference to a Starship for use in Film-related
    serialization without full Starship details.

    :param id: Unique identifier for the starship.
    :type id: int
    :param name: Name of the starship.
    :type name: str
    """

    id: int
    name: StrictName100

    model_config = {"from_attributes": True, "strict": True, "extra": "forbid"}


class VehicleBase(BaseModel):
    """
    Minimal nested Vehicle model for inclusion in Film responses.

    Defines a lightweight reference to a Vehicle entity for nested
    relationships in Film responses.

    :param id: Unique identifier for the vehicle.
    :type id: int
    :param name: Name of the vehicle.
    :type name: str
    """

    id: int
    name: StrictName100

    model_config = {"from_attributes": True, "strict": True, "extra": "forbid"}


class SpeciesBase(BaseModel):
    """
    Minimal nested Species model for inclusion in Film responses.

    Represents a simplified reference to a Species entity, enabling
    nested serialization without detailed Species attributes.

    :param id: Unique identifier for the species.
    :type id: int
    :param name: Name of the species.
    :type name: str
    """

    id: int
    name: StrictName100

    model_config = {"from_attributes": True, "strict": True, "extra": "forbid"}


class FilmBase(BaseModel):
    """
    Base Pydantic schema for a Star Wars film.

    Defines the core fields shared by both creation and response models,
    enabling consistent validation and serialization of film metadata.

    :param title: Title of the film.
    :type title: str
    :param episode_id: Episode number in the Star Wars saga.
    :type episode_id: int, optional
    :param opening_crawl: Opening crawl text of the film.
    :type opening_crawl: str, optional
    :param director: Director of the film.
    :type director: str, optional
    :param producer: Producer(s) of the film.
    :type producer: str, optional
    :param release_date: Release date of the film.
    :type release_date: datetime.date, optional
    :param created: Timestamp of resource creation.
    :type created: datetime.datetime, optional
    :param edited: Timestamp of last resource edit.
    :type edited: datetime.datetime, optional
    :param url: Resource URL.
    :type url: str, optional
    """

    title: StrictName100
    episode_id: Optional[int] = None
    opening_crawl: Optional[StrictText500] = None
    director: Optional[StrictName100] = None
    producer: Optional[StrictName100] = None
    release_date: Optional[date] = None
    created: Optional[datetime] = None
    edited: Optional[datetime] = None
    url: Optional[StrictURL] = None

    model_config = {"strict": True, "extra": "forbid"}


class FilmCreate(FilmBase):
    """
    Schema for creating a new Star Wars film.

    Inherits all fields from FilmBase to validate incoming
    film creation requests.
    """

    pass


class FilmResponse(FilmBase):
    """
    Schema for returning a Star Wars film in API responses.

    Extends FilmBase to include the database ID and nested lists
    of related entities such as Characters, Planets, Starships,
    Vehicles, and Species, enabling rich API responses.

    :param id: Database primary key for the film.
    :type id: int
    :param characters: List of associated CharacterBase entities.
    :type characters: list[CharacterBase]
    :param planets: List of associated PlanetBase entities.
    :type planets: list[PlanetBase]
    :param starships: List of associated StarshipBase entities.
    :type starships: list[StarshipBase]
    :param vehicles: List of associated VehicleBase entities.
    :type vehicles: list[VehicleBase]
    :param species: List of associated SpeciesBase entities.
    :type species: list[SpeciesBase]
    """

    id: int
    characters: List[CharacterBase] = []
    planets: List[PlanetBase] = []
    starships: List[StarshipBase] = []
    vehicles: List[VehicleBase] = []
    species: List[SpeciesBase] = []

    model_config = {"from_attributes": True, "strict": True, "extra": "forbid"}
