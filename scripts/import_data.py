#!/usr/bin/env python

"""
scripts/import_data.py

===============================================================================
Script to orchestrate full data import from SWAPI into local database.
===============================================================================

Usage:
    poetry run python scripts/import_data.py
    or
    python -m scripts.import_data
-------------------------------------------------------------------------------
"""

import asyncio

from src.database.session import async_session
from src.services.import_service import (
    import_characters_from_swapi,
    import_films_from_swapi,
    import_starships_from_swapi,
)
from src.utils.logger_util import log_info


async def main():
    log_info("Starting full SWAPI import...")

    async with async_session() as session:
        log_info("Importing films first (must come before characters)")
        await import_films_from_swapi(session)

        log_info("Importing characters (links to films now work)")
        await import_characters_from_swapi(session)

        log_info("Importing starships")
        await import_starships_from_swapi(session)

    log_info("SWAPI import complete.")


if __name__ == "__main__":
    asyncio.run(main())
