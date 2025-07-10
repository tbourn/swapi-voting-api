"""
src.api.responses

================================================================================
Standardized OpenAPI Response Definitions
================================================================================

Overview
--------
This module defines shared response metadata used for FastAPI route decorators.
It centralizes:

- HTTP content types
- Standard response descriptions
- Detailed error messages
- Example response payloads

Used to ensure consistent and DRY OpenAPI documentation across routes.

Author
------
- Thomas Bournaveas <thomas.bournaveas@gmail.com> — Backend Engineering & Architecture
"""

from typing import Any

# ---------------------------------------------------------------------------
# HTTP Content Types
# ---------------------------------------------------------------------------

CONTENT_TYPE_JSON = "application/json"

# ---------------------------------------------------------------------------
# Standard Response Descriptions
# ---------------------------------------------------------------------------

DESCRIPTION_SUCCESS = "Successful Response"
DESCRIPTION_SEARCH_SUCCESS = "Successful Search"
DESCRIPTION_NOT_FOUND = "Not Found"

# ---------------------------------------------------------------------------
# Detailed Error Messages
# ---------------------------------------------------------------------------

DETAIL_FILM_NOT_FOUND = "Film not found"
DETAIL_STARSHIP_NOT_FOUND = "Starship not found"
DETAIL_NO_FILMS = "No films found matching the query."
DETAIL_NO_STARSHIPS = "No starships found matching the query."
DETAIL_NO_CHARACTERS = "No characters found matching the query."

# ---------------------------------------------------------------------------
# Shared Character Responses
# ---------------------------------------------------------------------------

CHARACTER_EXAMPLE = {
    "id": 1,
    "name": "Luke Skywalker",
    "gender": "male",
    "birth_year": "19BBY",
    "films": [
        {"id": 1, "title": "A New Hope"},
        {"id": 2, "title": "The Empire Strikes Back"},
    ],
}

CHARACTER_LIST_RESPONSES: dict[int | str, dict[str, Any]] = {
    200: {
        "description": DESCRIPTION_SUCCESS,
        "content": {CONTENT_TYPE_JSON: {"example": [CHARACTER_EXAMPLE]}},
    },
    404: {
        "description": DESCRIPTION_NOT_FOUND,
        "content": {CONTENT_TYPE_JSON: {"example": {"detail": DETAIL_NO_CHARACTERS}}},
    },
}

CHARACTER_SINGLE_RESPONSES: dict[int | str, dict[str, Any]] = {
    200: {
        "description": DESCRIPTION_SUCCESS,
        "content": {CONTENT_TYPE_JSON: {"example": CHARACTER_EXAMPLE}},
    },
    404: {
        "description": DESCRIPTION_NOT_FOUND,
        "content": {CONTENT_TYPE_JSON: {"example": {"detail": "Character not found"}}},
    },
}

# ---------------------------------------------------------------------------
# Shared Film Responses
# ---------------------------------------------------------------------------

FILM_EXAMPLE = {
    "id": 1,
    "title": "A New Hope",
    "episode_id": 4,
    "opening_crawl": "It is a period of civil war...",
    "director": "George Lucas",
    "producer": "Gary Kurtz, Rick McCallum",
    "release_date": "1977-05-25",
    "created": "2014-12-10T14:23:31.880000",
    "edited": "2014-12-20T19:49:45.256000",
    "url": "https://swapi.info/api/films/1",
    "characters": [
        {"id": 1, "name": "Luke Skywalker"},
        {"id": 2, "name": "C-3PO"},
    ],
    "planets": [],
    "starships": [],
    "vehicles": [],
    "species": [],
}

FILM_LIST_RESPONSES: dict[int | str, dict[str, Any]] = {
    200: {
        "description": DESCRIPTION_SUCCESS,
        "content": {CONTENT_TYPE_JSON: {"example": [FILM_EXAMPLE]}},
    },
}

FILM_SEARCH_RESPONSES: dict[int | str, dict[str, Any]] = {
    200: {
        "description": DESCRIPTION_SEARCH_SUCCESS,
        "content": {CONTENT_TYPE_JSON: {"example": [FILM_EXAMPLE]}},
    },
    404: {
        "description": "No films found",
        "content": {CONTENT_TYPE_JSON: {"example": {"detail": DETAIL_NO_FILMS}}},
    },
}

FILM_SINGLE_RESPONSES: dict[int | str, dict[str, Any]] = {
    200: {
        "description": DESCRIPTION_SUCCESS,
        "content": {CONTENT_TYPE_JSON: {"example": FILM_EXAMPLE}},
    },
    404: {
        "description": DETAIL_FILM_NOT_FOUND,
        "content": {CONTENT_TYPE_JSON: {"example": {"detail": DETAIL_FILM_NOT_FOUND}}},
    },
}

# ---------------------------------------------------------------------------
# Shared Starship Responses
# ---------------------------------------------------------------------------

STARSHIP_EXAMPLE_1 = {
    "id": 1,
    "name": "CR90 corvette",
    "model": "CR90 corvette",
    "manufacturer": "Corellian Engineering Corporation",
    "starship_class": "corvette",
}

STARSHIP_EXAMPLE_2 = {
    "id": 2,
    "name": "Star Destroyer",
    "model": "Imperial I-class Star Destroyer",
    "manufacturer": "Kuat Drive Yards",
    "starship_class": "Star Destroyer",
}

STARSHIP_SEARCH_EXAMPLE = {
    "id": 5,
    "name": "Millennium Falcon",
    "model": "YT-1300 light freighter",
    "manufacturer": "Corellian Engineering Corporation",
    "starship_class": "Light freighter",
}

STARSHIP_LIST_RESPONSES: dict[int | str, dict[str, Any]] = {
    200: {
        "description": DESCRIPTION_SUCCESS,
        "content": {
            CONTENT_TYPE_JSON: {"example": [STARSHIP_EXAMPLE_1, STARSHIP_EXAMPLE_2]}
        },
    },
}

STARSHIP_SEARCH_RESPONSES: dict[int | str, dict[str, Any]] = {
    200: {
        "description": DESCRIPTION_SEARCH_SUCCESS,
        "content": {CONTENT_TYPE_JSON: {"example": [STARSHIP_SEARCH_EXAMPLE]}},
    },
    404: {
        "description": "No starships found",
        "content": {CONTENT_TYPE_JSON: {"example": {"detail": DETAIL_NO_STARSHIPS}}},
    },
}

STARSHIP_SINGLE_RESPONSES: dict[int | str, dict[str, Any]] = {
    200: {
        "description": DESCRIPTION_SUCCESS,
        "content": {CONTENT_TYPE_JSON: {"example": STARSHIP_SEARCH_EXAMPLE}},
    },
    404: {
        "description": DETAIL_STARSHIP_NOT_FOUND,
        "content": {
            CONTENT_TYPE_JSON: {"example": {"detail": DETAIL_STARSHIP_NOT_FOUND}}
        },
    },
}
