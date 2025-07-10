"""
src.models

================================================================================
SQLAlchemy ORM Model Package for SWAPI Voting API
================================================================================

Overview
--------
This package defines the core SQLAlchemy ORM models used to represent
Star Wars entities in the SWAPI Voting API database schema. Each model
corresponds to a table with well-defined columns, constraints, and
relationships designed for normalized relational storage and efficient querying.

Exported Models
---------------
- Film: Represents Star Wars film records with metadata and many-to-many relationships.
- Character: Represents individual characters with attributes and join tables for relationships.
- Planet: Represents planetary data with many-to-many relationships to films.
- Starship: Represents starships, with relationships to films and characters.
- Vehicle: Represents vehicles, with relationships to films and characters.
- Species: Represents biological species, with join tables linking to films and characters.

Key Characteristics
--------------------
- Declarative SQLAlchemy model definitions.
- Explicit many-to-many join relationships via association tables.
- Designed for FastAPI integration with Pydantic serialization.
- Supports maintainable, testable, and evolvable database schema.

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

from .film import Film
from .character import Character
from .planet import Planet
from .starship import Starship
from .vehicle import Vehicle
from .species import Species

__all__ = [
    "Film",
    "Character",
    "Planet",
    "Starship",
    "Vehicle",
    "Species",
]
