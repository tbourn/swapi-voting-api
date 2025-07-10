"""
src.api.routes

================================================================================
FastAPI Routes for SWAPI Voting API
================================================================================

Overview
--------
This module defines all RESTful API endpoints for the SWAPI Voting API.
It includes endpoints to:

- Import data from the external SWAPI
- Retrieve stored records with pagination
- Search records by name
- Fetch individual records by ID

Responsibilities
----------------
- Trigger asynchronous imports of characters, films, and starships
- Provide paginated list endpoints for all entities
- Support search by name or title with partial matches
- Enforce error handling and meaningful HTTP responses

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.responses import (
    CHARACTER_LIST_RESPONSES,
    CHARACTER_SINGLE_RESPONSES,
    CONTENT_TYPE_JSON,
    DETAIL_FILM_NOT_FOUND,
    DETAIL_NO_CHARACTERS,
    DETAIL_NO_FILMS,
    DETAIL_NO_STARSHIPS,
    DETAIL_STARSHIP_NOT_FOUND,
    FILM_LIST_RESPONSES,
    FILM_SEARCH_RESPONSES,
    FILM_SINGLE_RESPONSES,
    STARSHIP_LIST_RESPONSES,
    STARSHIP_SEARCH_RESPONSES,
    STARSHIP_SINGLE_RESPONSES,
)
from src.config.constants import MAX_PAGE_SIZE
from src.crud.characters import (
    get_character,
    list_characters,
    search_characters_by_name,
)
from src.crud.films import get_film, list_films, search_films_by_title
from src.crud.starships import get_starship, list_starships, search_starships_by_name
from src.database.session import get_db
from src.schemas.character import CharacterResponse
from src.schemas.common import (
    CharacterImportErrorResponse,
    FilmImportErrorResponse,
    MessageResponse,
    StarshipImportErrorResponse,
)
from src.schemas.film import FilmResponse
from src.schemas.starship import StarshipResponse
from src.services.import_service import (
    import_characters_from_swapi,
    import_films_from_swapi,
    import_starships_from_swapi,
)
from src.utils.logger_util import log_error

# ---------------------------------------------------------------------------
# Create the API router
# ---------------------------------------------------------------------------

router = APIRouter()

# ---------------------------------------------------------------------------
# Import Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/import/characters",
    response_model=MessageResponse,
    status_code=202,
    responses={
        202: {
            "description": "Successful import",
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": {"message": "Character import completed."}
                }
            },
        },
        502: {
            "model": CharacterImportErrorResponse,
            "description": "Bad Gateway",
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": {"error": "Failed to import characters from SWAPI."}
                }
            },
        },
    },
)
async def import_characters(db: AsyncSession = Depends(get_db)):
    """
    Trigger fetching and storing characters from SWAPI.

    :param db: Async database session dependency
    :type db: AsyncSession
    :raises HTTPException: If SWAPI fetch or database import fails
    :return: Success message
    :rtype: dict
    """
    try:
        await import_characters_from_swapi(db)
    except Exception as e:
        log_error(e, function_name="import_characters")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to import characters from SWAPI.",
        )
    return {"message": "Character import completed."}


@router.post(
    "/import/films",
    response_model=MessageResponse,
    status_code=202,
    responses={
        202: {
            "description": "Successful import",
            "content": {
                CONTENT_TYPE_JSON: {"example": {"message": "Film import completed."}}
            },
        },
        502: {
            "model": FilmImportErrorResponse,
            "description": "Bad Gateway",
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": {"error": "Failed to import films from SWAPI."}
                }
            },
        },
    },
)
async def import_films(db: AsyncSession = Depends(get_db)):
    """
    Trigger fetching and storing films from SWAPI.

    :param db: Async database session dependency
    :type db: AsyncSession
    :raises HTTPException: If SWAPI fetch or database import fails
    :return: Success message
    :rtype: dict
    """
    try:
        await import_films_from_swapi(db)
    except Exception as e:
        log_error(e, function_name="import_films")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to import films from SWAPI.",
        )
    return {"message": "Film import completed."}


@router.post(
    "/import/starships",
    response_model=MessageResponse,
    status_code=202,
    responses={
        202: {
            "description": "Successful import",
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": {"message": "Starship import completed."}
                }
            },
        },
        502: {
            "model": StarshipImportErrorResponse,
            "description": "Bad Gateway",
            "content": {
                CONTENT_TYPE_JSON: {
                    "example": {"error": "Failed to import starships from SWAPI."}
                }
            },
        },
    },
)
async def import_starships(db: AsyncSession = Depends(get_db)):
    """
    Trigger fetching and storing starships from SWAPI.

    :param db: Async database session dependency
    :type db: AsyncSession
    :raises HTTPException: If SWAPI fetch or database import fails
    :return: Success message
    :rtype: dict
    """
    try:
        await import_starships_from_swapi(db)
    except Exception as e:
        log_error(e, function_name="import_starships")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to import starships from SWAPI.",
        )
    return {"message": "Starship import completed."}


# ---------------------------------------------------------------------------
# Character Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/characters/",
    response_model=List[CharacterResponse],
    responses=CHARACTER_LIST_RESPONSES,
)
async def get_characters(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=MAX_PAGE_SIZE),
    db: AsyncSession = Depends(get_db),
):
    """
    List stored characters with pagination.

    :param skip: Number of records to skip
    :type skip: int
    :param limit: Maximum number of records to return
    :type limit: int
    :param db: Async database session dependency
    :type db: AsyncSession
    :return: List of CharacterResponse
    :rtype: List[CharacterResponse]
    """
    return await list_characters(db, skip=skip, limit=limit)


@router.get(
    "/characters/search",
    response_model=List[CharacterResponse],
    responses=CHARACTER_LIST_RESPONSES,
)
async def search_characters(
    q: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
):
    """
    Search stored characters by partial name match.

    :param q: Query string for character name
    :type q: str
    :param db: Async database session dependency
    :type db: AsyncSession
    :raises HTTPException: If no results are found
    :return: List of CharacterResponse
    :rtype: List[CharacterResponse]
    """
    results = await search_characters_by_name(db, name=q)
    if not results:
        raise HTTPException(status_code=404, detail=DETAIL_NO_CHARACTERS)
    return results


@router.get(
    "/characters/{character_id}",
    response_model=CharacterResponse,
    responses=CHARACTER_SINGLE_RESPONSES,
)
async def get_character_by_id(character_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get a single character by its ID.

    :param character_id: Character's unique ID
    :type character_id: int
    :param db: Async database session dependency
    :type db: AsyncSession
    :raises HTTPException: If the character is not found
    :return: CharacterResponse
    :rtype: CharacterResponse
    """
    character = await get_character(db, character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    return character


# ---------------------------------------------------------------------------
# Film Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/films/",
    response_model=List[FilmResponse],
    responses=FILM_LIST_RESPONSES,
)
async def get_films(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=MAX_PAGE_SIZE),
    db: AsyncSession = Depends(get_db),
):
    """
    List stored films with pagination.

    :param skip: Number of records to skip
    :type skip: int
    :param limit: Maximum number of records to return
    :type limit: int
    :param db: Async database session dependency
    :type db: AsyncSession
    :return: List of FilmResponse
    :rtype: List[FilmResponse]
    """
    return await list_films(db, skip=skip, limit=limit)


@router.get(
    "/films/search",
    response_model=List[FilmResponse],
    responses=FILM_SEARCH_RESPONSES,
)
async def search_films(
    q: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
):
    """
    Search stored films by partial title match.

    :param q: Query string for film title
    :type q: str
    :param db: Async database session dependency
    :type db: AsyncSession
    :raises HTTPException: If no results are found
    :return: List of FilmResponse
    :rtype: List[FilmResponse]
    """
    results = await search_films_by_title(db, title=q)
    if not results:
        raise HTTPException(status_code=404, detail=DETAIL_NO_FILMS)
    return results


@router.get(
    "/films/{film_id}",
    response_model=FilmResponse,
    responses=FILM_SINGLE_RESPONSES,
)
async def get_film_by_id(film_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get a single film by its ID.

    :param film_id: Film's unique ID
    :type film_id: int
    :param db: Async database session dependency
    :type db: AsyncSession
    :raises HTTPException: If the film is not found
    :return: FilmResponse
    :rtype: FilmResponse
    """
    film = await get_film(db, film_id)
    if not film:
        raise HTTPException(status_code=404, detail=DETAIL_FILM_NOT_FOUND)
    return film


# ---------------------------------------------------------------------------
# Starship Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/starships/",
    response_model=List[StarshipResponse],
    responses=STARSHIP_LIST_RESPONSES,
)
async def get_starships(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=MAX_PAGE_SIZE),
    db: AsyncSession = Depends(get_db),
):
    """
    List stored starships with pagination.

    :param skip: Number of records to skip
    :type skip: int
    :param limit: Maximum number of records to return
    :type limit: int
    :param db: Async database session dependency
    :type db: AsyncSession
    :return: List of StarshipResponse
    :rtype: List[StarshipResponse]
    """
    return await list_starships(db, skip=skip, limit=limit)


@router.get(
    "/starships/search",
    response_model=List[StarshipResponse],
    responses=STARSHIP_SEARCH_RESPONSES,
)
async def search_starships(
    q: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
):
    """
    Search stored starships by partial name match.

    :param q: Query string for starship name
    :type q: str
    :param db: Async database session dependency
    :type db: AsyncSession
    :raises HTTPException: If no results are found
    :return: List of StarshipResponse
    :rtype: List[StarshipResponse]
    """
    results = await search_starships_by_name(db, name=q)
    if not results:
        raise HTTPException(status_code=404, detail=DETAIL_NO_STARSHIPS)
    return results


@router.get(
    "/starships/{starship_id}",
    response_model=StarshipResponse,
    responses=STARSHIP_SINGLE_RESPONSES,
)
async def get_starship_by_id(starship_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get a single starship by its ID.

    :param starship_id: Starship's unique ID
    :type starship_id: int
    :param db: Async database session dependency
    :type db: AsyncSession
    :raises HTTPException: If the starship is not found
    :return: StarshipResponse
    :rtype: StarshipResponse
    """
    starship = await get_starship(db, starship_id)
    if not starship:
        raise HTTPException(status_code=404, detail=DETAIL_STARSHIP_NOT_FOUND)
    return starship
