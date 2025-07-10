"""
src.schemas.vehicle

================================================================================
Pydantic Schemas for Star Wars Vehicles
================================================================================

Overview
--------
Defines the Pydantic models for validating, parsing, and serializing
vehicle-related data in the SWAPI Voting API. Supports both request
and response schemas with nested film relationships.

Responsibilities
----------------
- Define shared base schema with core vehicle fields
- Provide request model for vehicle creation
- Provide response model with database ID and related films

Key Characteristics
--------------------
- FastAPI-compatible with automatic OpenAPI documentation generation
- orm_mode enabled for SQLAlchemy integration
- Supports nested FilmBase serialization in responses

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

StrictValue50 = Annotated[
    str, constr(strip_whitespace=True, min_length=1, max_length=50)
]


class FilmBase(BaseModel):
    """
    Minimal nested Film model for inclusion in Vehicle responses.

    Defines the structure for embedding associated films in
    vehicle API responses.

    :param id: Unique identifier for the film.
    :type id: int
    :param title: Title of the film.
    :type title: str
    """

    id: int
    title: StrictName100

    model_config = {
        "from_attributes": True,
        "strict": True,
        "extra": "forbid",
    }


class VehicleBase(BaseModel):
    """
    Base Pydantic schema for a Star Wars vehicle.

    Defines core fields shared by both creation and response models,
    supporting consistent validation and serialization of vehicle data.

    :param name: Name of the vehicle (required).
    :type name: str
    :param model: Model of the vehicle (optional).
    :type model: str, optional
    :param manufacturer: Manufacturer of the vehicle (optional).
    :type manufacturer: str, optional
    :param cost_in_credits: Cost of the vehicle in credits (optional).
    :type cost_in_credits: str, optional
    :param length: Length of the vehicle (optional).
    :type length: str, optional
    :param max_atmosphering_speed: Maximum speed in atmosphere (optional).
    :type max_atmosphering_speed: str, optional
    :param crew: Crew capacity (optional).
    :type crew: str, optional
    :param passengers: Passenger capacity (optional).
    :type passengers: str, optional
    :param cargo_capacity: Cargo capacity (optional).
    :type cargo_capacity: str, optional
    :param consumables: Consumables duration (optional).
    :type consumables: str, optional
    :param vehicle_class: Classification of the vehicle (optional).
    :type vehicle_class: str, optional
    :param url: External API URL for the vehicle resource (optional).
    :type url: str, optional
    """

    name: StrictName100
    model: Optional[StrictDesc200] = None
    manufacturer: Optional[StrictDesc200] = None
    cost_in_credits: Optional[StrictValue50] = None
    length: Optional[StrictValue50] = None
    max_atmosphering_speed: Optional[StrictValue50] = None
    crew: Optional[StrictValue50] = None
    passengers: Optional[StrictValue50] = None
    cargo_capacity: Optional[StrictValue50] = None
    consumables: Optional[StrictDesc200] = None
    vehicle_class: Optional[StrictDesc200] = None
    url: Optional[StrictDesc200] = None

    model_config = {
        "strict": True,
        "extra": "forbid",
    }


class VehicleCreate(VehicleBase):
    """
    Schema for creating a new Star Wars vehicle.

    Inherits all fields from VehicleBase to validate
    incoming POST requests for vehicle creation.
    """

    pass


class VehicleResponse(VehicleBase):
    """
    Schema for returning a Star Wars vehicle in API responses.

    Extends VehicleBase to include the database ID and
    nested list of associated films.

    :param id: Unique database identifier for the vehicle.
    :type id: int
    :param films: List of associated films.
    :type films: list[:class:`FilmBase`], optional
    """

    id: int
    films: List[FilmBase] = []

    model_config = {
        "from_attributes": True,
        "strict": True,
        "extra": "forbid",
    }
