"""
src.services.import_service

================================================================================
Data Import Service for SWAPI
================================================================================

Overview
--------
This module defines service-layer functions that orchestrate fetching data
from the SWAPI and storing it in the local database. It handles pagination,
schema transformation, error logging, and calls the CRUD layer to persist
records.

Responsibilities
----------------
- Fetch characters, films, and starships from SWAPI
- Transform SWAPI responses to local schema models
- Store records in the database using CRUD modules
- Log progress and handle errors gracefully

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

from urllib.parse import urlparse

from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.characters import character_exists, create_character
from src.crud.films import create_film, film_exists
from src.crud.starships import create_starship, starship_exists
from src.exceptions.custom_exceptions import DataImportError, ExternalAPIError
from src.models.film import Film
from src.schemas.character import CharacterCreate
from src.schemas.film import FilmCreate
from src.schemas.starship import StarshipCreate
from src.services.swapi_client import fetch_characters, fetch_films, fetch_starships
from src.utils.date_parser_util import parse_iso_date, parse_iso_datetime
from src.utils.logger_util import log_error, log_info


async def import_characters_from_swapi(db: AsyncSession) -> None:
    """
    Fetches all characters from SWAPI (paginated) and stores them in the database.

    Links characters to films by parsing film URLs and appending Film objects.

    :param db: Async database session
    :type db: AsyncSession
    :raises ExternalAPIError: When the external SWAPI request fails.
    :raises DataImportError: When the SWAPI response format is invalid.
    :return: None
    :rtype: None
    """
    page = 1
    total_inserted = 0
    total_skipped = 0

    log_info("Starting import of characters from SWAPI.")

    while True:
        try:
            log_info(f"Fetching SWAPI characters page {page}...")
            response = await fetch_characters(page=page)
        except Exception as e:
            log_error(
                e, function_name="import_characters_from_swapi", context={"page": page}
            )
            raise ExternalAPIError(
                f"Failed to fetch characters from SWAPI page {page}"
            ) from e

        if not isinstance(response, dict):
            raise DataImportError(
                "Invalid SWAPI response format",
                details={"page": page, "response": response},
            )

        results = response.get("results")
        if not results:
            log_info(f"No results on page {page}. Stopping import.")
            break

        for item in results:
            try:
                name = item.get("name", "").strip()
                if not name:
                    log_error(
                        DataImportError("Character with empty name"),
                        function_name="import_characters_from_swapi",
                        context={"item": item},
                    )
                    continue

                if await character_exists(db, name):
                    log_info(f"Skipping existing character: {name}")
                    total_skipped += 1
                    continue

                character_in = CharacterCreate(
                    name=name,
                    gender=item.get("gender"),
                    birth_year=item.get("birth_year"),
                )

                created_character = await create_character(db, character_in)

                if created_character:
                    for film_url in item.get("films", []):
                        try:
                            film_id = int(
                                urlparse(film_url).path.rstrip("/").split("/")[-1]
                            )
                            film = await db.get(Film, film_id)
                            if film:
                                created_character.films.append(film)
                        except Exception as link_exc:
                            log_error(
                                link_exc,
                                function_name="import_characters_from_swapi",
                                context={"film_url": film_url, "character": name},
                            )

                    await db.commit()
                    await db.refresh(created_character)
                    total_inserted += 1
                    log_info(f"Inserted character: {character_in.model_dump()}")

                else:
                    log_info(
                        f"Failed to insert character (IntegrityError?): {character_in.model_dump()}"
                    )

            except Exception as e:
                log_error(
                    e,
                    function_name="import_characters_from_swapi",
                    context={"item": item},
                )

        if not response.get("next"):
            log_info("No 'next' link in SWAPI response. Import complete.")
            break

        page += 1

    log_info(
        f"Completed importing characters from SWAPI. Total inserted: {total_inserted}, Total skipped: {total_skipped}"
    )


async def import_films_from_swapi(db: AsyncSession) -> None:
    """
    Fetches all films from SWAPI and stores them in the database.

    :param db: Async database session
    :type db: AsyncSession
    :raises ExternalAPIError: When the external SWAPI request fails.
    :raises DataImportError: When the SWAPI response contains no results.
    :return: None
    :rtype: None
    """
    log_info("Starting import of films from SWAPI.")
    try:
        response = await fetch_films()
    except Exception as e:
        log_error(e, function_name="import_films_from_swapi")
        raise ExternalAPIError("Failed to fetch films from SWAPI") from e

    if not response or "results" not in response:
        raise DataImportError(
            "No results in SWAPI films response", details={"response": response}
        )

    total_inserted = 0
    total_skipped = 0

    for item in response["results"]:
        try:
            title = item.get("title", "").strip()
            if not title:
                log_error(
                    DataImportError("Film with empty title"),
                    function_name="import_films_from_swapi",
                    context={"item": item},
                )
                continue

            if await film_exists(db, title):
                log_info(f"Skipping existing film: {title}")
                total_skipped += 1
                continue

            film_in = FilmCreate(
                title=title,
                episode_id=item.get("episode_id"),
                opening_crawl=item.get("opening_crawl"),
                director=item.get("director"),
                producer=item.get("producer"),
                release_date=parse_iso_date(item.get("release_date")),
                created=parse_iso_datetime(item.get("created")),
                edited=parse_iso_datetime(item.get("edited")),
                url=item.get("url"),
            )

            await create_film(db, film_in)
            total_inserted += 1
            log_info(f"Inserted film: {title}")

        except Exception as e:
            log_error(
                e, function_name="import_films_from_swapi", context={"item": item}
            )

    log_info(
        f"Completed importing films from SWAPI. Total inserted: {total_inserted}, Total skipped: {total_skipped}"
    )


async def import_starships_from_swapi(db: AsyncSession) -> None:
    """
    Fetches all starships from SWAPI (paginated) and stores them in the database.

    :param db: Async database session
    :type db: AsyncSession
    :raises ExternalAPIError: When the external SWAPI request fails.
    :return: None
    :rtype: None
    """
    page = 1
    total_inserted = 0
    total_skipped = 0

    log_info("Starting import of starships from SWAPI.")

    while True:
        try:
            response = await fetch_starships(page=page)
        except Exception as e:
            log_error(
                e, function_name="import_starships_from_swapi", context={"page": page}
            )
            raise ExternalAPIError(
                f"Failed to fetch starships from SWAPI page {page}"
            ) from e

        if not response or "results" not in response:
            log_info(f"No results on page {page}. Stopping import.")
            break

        for item in response["results"]:
            try:
                starship_in = StarshipCreate(
                    name=item.get("name", "").strip(),
                    model=item.get("model"),
                    manufacturer=item.get("manufacturer"),
                    starship_class=item.get("starship_class"),
                )

                if not starship_in.name:
                    log_error(
                        DataImportError("Starship with empty name"),
                        function_name="import_starships_from_swapi",
                        context={"item": item},
                    )
                    continue

                if await starship_exists(db, starship_in.name):
                    log_info(f"Skipping existing starship: {starship_in.name}")
                    total_skipped += 1
                    continue

                await create_starship(db, starship_in)
                total_inserted += 1
                log_info(f"Inserted starship: {starship_in.model_dump()}")

            except Exception as e:
                log_error(
                    e,
                    function_name="import_starships_from_swapi",
                    context={"item": item},
                )

        if not response.get("next"):
            log_info("No 'next' link in SWAPI response. Import complete.")
            break

        page += 1

    log_info(
        f"Completed importing starships from SWAPI. Total inserted: {total_inserted}, Total skipped: {total_skipped}"
    )
