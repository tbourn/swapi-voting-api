"""
src.schemas.species

================================================================================
Pydantic Schemas for Star Wars Species
================================================================================

Overview
--------
Defines the Pydantic models used to validate, parse, and serialize
species-related data in the SWAPI Voting API. Supports both request
and response schemas, including nested relationships with films.

Responsibilities
----------------
- Define base schema with shared species fields
- Provide creation schema for incoming requests
- Provide response schema with database ID and nested Film references

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
    Minimal nested Film model for inclusion in Species responses.

    Provides a lightweight reference to a Film entity when serializing
    Species responses, avoiding full Film detail while supporting
    many-to-many relationships.

    :param id: Unique identifier for the film.
    :type id: int
    :param title: Title of the film.
    :type title: str
    """

    id: int
    title: StrictName100

    model_config = {"from_attributes": True, "strict": True, "extra": "forbid"}


class SpeciesBase(BaseModel):
    """
    Base Pydantic schema for a Star Wars species.

    Defines core species fields shared by both creation and response models,
    supporting consistent validation and serialization of species data.

    :param name: Name of the species.
    :type name: str
    :param classification: Biological classification of the species (optional).
    :type classification: str, optional
    :param designation: Designation of the species (optional).
    :type designation: str, optional
    :param average_height: Average height in centimeters (optional).
    :type average_height: str, optional
    :param skin_colors: Comma-separated skin colors (optional).
    :type skin_colors: str, optional
    :param hair_colors: Comma-separated hair colors (optional).
    :type hair_colors: str, optional
    :param eye_colors: Comma-separated eye colors (optional).
    :type eye_colors: str, optional
    :param average_lifespan: Average lifespan in years (optional).
    :type average_lifespan: str, optional
    :param language: Language spoken by the species (optional).
    :type language: str, optional
    :param url: Resource URL (optional).
    :type url: str, optional
    """

    name: StrictName100
    classification: Optional[StrictDesc200] = None
    designation: Optional[StrictDesc200] = None
    average_height: Optional[StrictDesc200] = None
    skin_colors: Optional[StrictDesc200] = None
    hair_colors: Optional[StrictDesc200] = None
    eye_colors: Optional[StrictDesc200] = None
    average_lifespan: Optional[StrictDesc200] = None
    language: Optional[StrictDesc200] = None
    url: Optional[StrictURL] = None

    model_config = {"strict": True, "extra": "forbid"}


class SpeciesCreate(SpeciesBase):
    """
    Schema for creating a new Star Wars species.

    Inherits all fields from SpeciesBase to validate
    incoming species creation requests.
    """

    pass


class SpeciesResponse(SpeciesBase):
    """
    Schema for returning a Star Wars species in API responses.

    Extends SpeciesBase to include the database ID and a nested list
    of associated FilmBase references, enabling rich API responses
    with related film data.

    :param id: Database primary key for the species.
    :type id: int
    :param films: List of associated FilmBase entities.
    :type films: list[FilmBase]
    """

    id: int
    films: List[FilmBase] = []

    model_config = {"from_attributes": True, "strict": True, "extra": "forbid"}
