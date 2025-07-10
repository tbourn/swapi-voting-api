"""
src.crud.films

================================================================================
CRUD Operations for Star Wars Films
================================================================================

Overview
--------
This module provides database CRUD operations for the Film model
using SQLAlchemy AsyncSession. It supports creation, retrieval by ID,
listing with pagination, search by title, and duplicate checks.

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

from typing import List, Optional, Sequence

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.exceptions.custom_exceptions import DatabaseError
from src.models.film import Film
from src.schemas.film import FilmCreate
from src.utils.logger_util import log_error


async def create_film(db: AsyncSession, film_in: FilmCreate) -> Optional[Film]:
    """
    Create a new Film record in the database.

    :param db: Async database session
    :param film_in: Schema with film creation data
    :return: Created Film object or None if failed
    """
    new_film = Film(**film_in.dict())

    try:
        db.add(new_film)
        await db.commit()
        await db.refresh(new_film)
        return new_film
    except IntegrityError as e:
        await db.rollback()
        log_error(
            e,
            function_name="create_film",
            context={"film": film_in.dict()},
        )
        raise DatabaseError(
            "Database integrity error while creating film", details={"error": str(e)}
        )


async def film_exists(db: AsyncSession, title: str) -> bool:
    """
    Check if a Film with the given title already exists.

    :param db: Async database session
    :param title: Film title to check
    :return: True if film exists, False otherwise
    """
    result = await db.execute(select(Film).where(Film.title == title))
    return result.unique().scalar_one_or_none() is not None


async def get_film(db: AsyncSession, film_id: int) -> Optional[Film]:
    """
    Retrieve a Film by its ID.

    :param db: Async database session
    :param film_id: Film ID
    :return: Film object or None
    """
    result = await db.execute(
        select(Film).options(selectinload(Film.characters)).where(Film.id == film_id)
    )
    return result.scalar_one_or_none()


async def list_films(
    db: AsyncSession, skip: int = 0, limit: int = 20
) -> Sequence[Film]:
    """
    Retrieve a paginated list of Films.

    :param db: Async database session
    :param skip: Number of records to skip
    :param limit: Max number of records to return
    :return: List of Film objects
    """
    result = await db.execute(
        select(Film).options(selectinload(Film.characters)).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def search_films_by_title(db: AsyncSession, title: str) -> List[Film]:
    """
    Search for Films by partial title match.

    :param db: Async database session
    :param title: Title search term
    :return: List of matching Film objects
    """

    result = await db.execute(
        select(Film)
        .options(selectinload(Film.characters))
        .where(Film.title.ilike(f"%{title}%"))
    )
    return list(result.unique().scalars().all())
