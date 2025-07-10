"""
src.crud.characters

================================================================================
CRUD Operations for Star Wars Characters
================================================================================

Overview
--------
This module provides database CRUD operations for the Character model
using SQLAlchemy AsyncSession. It supports creation, retrieval by ID,
listing with pagination, and search by name.

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.exceptions.custom_exceptions import DatabaseError
from src.models.character import Character
from src.schemas.character import CharacterCreate
from src.utils.logger_util import log_error


async def create_character(
    db: AsyncSession, character_in: CharacterCreate
) -> Optional[Character]:
    """
    Create a new Character record in the database.

    :param db: Async database session
    :type db: AsyncSession
    :param character_in: Schema with character creation data
    :type character_in: CharacterCreate
    :return: Created Character object or None if failed
    :rtype: Optional[Character]
    """
    new_character = Character(**character_in.dict())

    try:
        db.add(new_character)
        await db.commit()
        await db.refresh(new_character)
        return new_character
    except IntegrityError as e:
        await db.rollback()
        log_error(
            e,
            function_name="create_character",
            context={"character": character_in.dict()},
        )
        raise DatabaseError(
            "Database integrity error while creating character",
            details={"error": str(e)},
        )


async def character_exists(db: AsyncSession, name: str) -> bool:
    """
    Check if a character with the given name already exists.

    This handles eager-loading joins that might duplicate rows
    by using scalars().unique().first().

    :param db: Async database session
    :type db: AsyncSession
    :param name: Character name to check
    :type name: str
    :return: True if exists, False otherwise
    :rtype: bool
    """
    result = await db.execute(select(Character).where(Character.name == name))
    return result.scalars().unique().first() is not None


async def get_character(db: AsyncSession, character_id: int) -> Optional[Character]:
    """
    Retrieve a Character by its ID.

    :param db: Async database session
    :type db: AsyncSession
    :param character_id: Character ID
    :type character_id: int
    :return: Character object or None
    :rtype: Optional[Character]
    """
    result = await db.execute(
        select(Character)
        .options(
            selectinload(Character.films),
            selectinload(Character.vehicles),
            selectinload(Character.starships),
            selectinload(Character.species),
            selectinload(Character.homeworld),
        )
        .where(Character.id == character_id)
    )
    return result.scalars().unique().first()


async def list_characters(
    db: AsyncSession, skip: int = 0, limit: int = 20
) -> List[Character]:
    """
    Retrieve a paginated list of Characters.

    :param db: Async database session
    :type db: AsyncSession
    :param skip: Number of records to skip
    :type skip: int, optional
    :param limit: Max number of records to return
    :type limit: int, optional
    :return: List of Character objects
    :rtype: List[Character]
    """
    result = await db.execute(
        select(Character)
        .options(
            selectinload(Character.films),
            selectinload(Character.vehicles),
            selectinload(Character.starships),
            selectinload(Character.species),
            selectinload(Character.homeworld),
        )
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().unique().all())


async def search_characters_by_name(db: AsyncSession, name: str) -> List[Character]:
    """
    Search for Characters by partial name match.

    :param db: Async database session
    :type db: AsyncSession
    :param name: Name search term
    :type name: str
    :return: List of matching Character objects
    :rtype: List[Character]
    """
    result = await db.execute(
        select(Character)
        .options(
            selectinload(Character.films),
            selectinload(Character.vehicles),
            selectinload(Character.starships),
            selectinload(Character.species),
            selectinload(Character.homeworld),
        )
        .where(Character.name.ilike(f"%{name}%"))
    )
    return list(result.scalars().unique().all())
