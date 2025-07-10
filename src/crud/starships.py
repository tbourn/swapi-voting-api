"""
src.crud.starships

================================================================================
CRUD Operations for Star Wars Starships
================================================================================

Overview
--------
This module provides database CRUD operations for the Starship model
using SQLAlchemy AsyncSession. It supports creation, retrieval by ID,
listing with pagination, search by name, and duplicate checks.

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.custom_exceptions import DatabaseError
from src.models.starship import Starship
from src.schemas.starship import StarshipCreate
from src.utils.logger_util import log_error


async def starship_exists(db: AsyncSession, name: str) -> bool:
    """
    Check if a Starship with the given name already exists.

    :param db: Async database session
    :param name: Starship name to check
    :return: True if starship exists, False otherwise
    """
    result = await db.execute(select(Starship).where(Starship.name == name))
    return result.unique().scalar_one_or_none() is not None


async def create_starship(
    db: AsyncSession, starship_in: StarshipCreate
) -> Optional[Starship]:
    """
    Create a new Starship record in the database.

    Skips creation if a Starship with the same name already exists.

    :param db: Async database session
    :param starship_in: Schema with starship creation data
    :return: Created Starship object or None if skipped or failed
    """
    try:
        if await starship_exists(db, starship_in.name):
            return None

        new_starship = Starship(**starship_in.dict())
        db.add(new_starship)
        await db.commit()
        await db.refresh(new_starship)
        return new_starship

    except IntegrityError as e:
        await db.rollback()
        log_error(
            e,
            function_name="create_starship",
            context={"starship": starship_in.dict()},
        )
        raise DatabaseError(
            "Database integrity error while creating starship",
            details={"error": str(e)},
        )


async def get_starship(db: AsyncSession, starship_id: int) -> Optional[Starship]:
    """
    Retrieve a Starship by its ID.

    :param db: Async database session
    :param starship_id: Starship ID
    :return: Starship object or None
    """
    result = await db.execute(select(Starship).where(Starship.id == starship_id))
    return result.unique().scalar_one_or_none()


async def list_starships(
    db: AsyncSession, skip: int = 0, limit: int = 20
) -> List[Starship]:
    """
    Retrieve a paginated list of Starships.

    :param db: Async database session
    :param skip: Number of records to skip
    :param limit: Max number of records to return
    :return: List of Starship objects
    """
    result = await db.execute(select(Starship).offset(skip).limit(limit))
    return list(result.unique().scalars().all())


async def search_starships_by_name(db: AsyncSession, name: str) -> List[Starship]:
    """
    Search for Starships by partial name match.

    :param db: Async database session
    :param name: Name search term
    :return: List of matching Starship objects
    """
    result = await db.execute(select(Starship).where(Starship.name.ilike(f"%{name}%")))
    return list(result.unique().scalars().all())
