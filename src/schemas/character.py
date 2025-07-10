"""
src.schemas.character

================================================================================
Pydantic Schemas for Star Wars Characters
================================================================================

Overview
--------
Defines the Pydantic models for validating, parsing, and serializing
character-related data in the SWAPI Voting API. These schemas ensure
type safety and clarity for both incoming requests and outgoing responses,
including nested Film relationships for richer API output.

Responsibilities
----------------
- Provide a base schema with shared character fields
- Define a creation schema for character input
- Define a response schema with database ID and related films

Key Characteristics
--------------------
- Fully compatible with FastAPI for OpenAPI docs generation
- Enables orm_mode for seamless SQLAlchemy integration
- Supports nested FilmBase serialization for related resources

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

from typing import List, Optional

from pydantic import BaseModel, constr
from typing_extensions import Annotated

StrictStr100 = Annotated[
    str, constr(strip_whitespace=True, min_length=1, max_length=100)
]
StrictStr200 = Annotated[
    str, constr(strip_whitespace=True, min_length=1, max_length=200)
]
StrictStr20 = Annotated[str, constr(strip_whitespace=True, max_length=20)]


class FilmBase(BaseModel):
    """
    Minimal nested Film schema for embedding in Character responses.

    Used to represent film references without full detail, suitable for
    many-to-many relationships in API responses.

    :param id: Unique identifier for the film.
    :type id: int
    :param title: Title of the film.
    :type title: str
    """

    id: int
    title: StrictStr200

    model_config = {
        "from_attributes": True,
        "strict": True,
        "extra": "forbid",
    }


class CharacterBase(BaseModel):
    """
    Base Pydantic schema for a Star Wars character.

    Defines the core fields shared by both request and response models,
    supporting validation and serialization of basic character attributes.

    :param name: Name of the character.
    :type name: str
    :param gender: Gender of the character, if known.
    :type gender: str, optional
    :param birth_year: Birth year of the character in BBY/ABY format.
    :type birth_year: str, optional
    """

    name: StrictStr100
    gender: Optional[StrictStr20] = None
    birth_year: Optional[StrictStr20] = None

    model_config = {"extra": "forbid", "strict": True}


class CharacterCreate(CharacterBase):
    """
    Schema for creating a new Star Wars character.

    Inherits all fields from CharacterBase to validate incoming creation
    requests without additional ID or relational fields.
    """

    pass


class CharacterResponse(CharacterBase):
    """
    Schema for returning a Star Wars character in API responses.

    Extends CharacterBase to include the database ID and nested Film
    references, enabling rich serialization for clients consuming
    the SWAPI Voting API.

    :param id: Database primary key for the character.
    :type id: int
    :param films: List of associated films as nested FilmBase instances.
    :type films: list[FilmBase]
    """

    id: int
    films: List[FilmBase] = []

    model_config = {"from_attributes": True, "extra": "forbid", "strict": True}
