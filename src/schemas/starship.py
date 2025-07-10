"""
src.schemas.starship

================================================================================
Pydantic Schemas for Star Wars Starships
================================================================================

Overview
--------
This module defines the Pydantic models used for validating and serializing
starship-related data in the SWAPI Voting API. It supports both request and
response schemas for starships.

Responsibilities
----------------
- Define base schema with shared starship fields
- Provide request model for starship creation
- Provide response model with ID for database records

Key Characteristics
--------------------
- Compatible with FastAPI for automatic documentation
- orm_mode enabled for SQLAlchemy model integration
- Flat schema without nested relationships

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

from typing import Optional

from pydantic import BaseModel, constr
from typing_extensions import Annotated

StrictName100 = Annotated[
    str, constr(strip_whitespace=True, min_length=1, max_length=100)
]

StrictDesc200 = Annotated[
    str, constr(strip_whitespace=True, min_length=1, max_length=200)
]


class StarshipBase(BaseModel):
    """
    Base Pydantic schema for a Star Wars starship.

    Defines core fields shared by both creation and response models,
    supporting consistent validation and serialization of starship data.

    :param name: Name of the starship (required).
    :type name: str
    :param model: Model of the starship (optional).
    :type model: str, optional
    :param manufacturer: Manufacturer of the starship (optional).
    :type manufacturer: str, optional
    :param starship_class: Classification of the starship (optional).
    :type starship_class: str, optional
    """

    name: StrictName100
    model: Optional[StrictDesc200] = None
    manufacturer: Optional[StrictDesc200] = None
    starship_class: Optional[StrictDesc200] = None

    model_config = {
        "strict": True,
        "extra": "forbid",
    }


class StarshipCreate(StarshipBase):
    """
    Schema for creating a new Star Wars starship.

    Inherits all fields from StarshipBase to validate
    incoming POST requests for starship creation.
    """

    pass


class StarshipResponse(StarshipBase):
    """
    Schema for returning a Star Wars starship in API responses.

    Extends StarshipBase to include the database ID,
    enabling clients to uniquely identify stored starships.

    :param id: Unique database identifier for the starship.
    :type id: int
    """

    id: int

    model_config = {
        "from_attributes": True,
        "strict": True,
        "extra": "forbid",
    }
